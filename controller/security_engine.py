from __future__ import annotations 
import json 
import os 
import pathlib 
import time 
import uuid 
from typing import List 
from common .interfaces import SecState ,SecurityEvent 
from controller import crypto_agility as ca 
try :
    import oqs 
    _KEM_ALG ='ML-KEM-768'
    _SIG_ALG :str |None =None 
    for _sig_candidate in ('ML-DSA-65','Dilithium3'):
        try :
            with oqs .Signature (_sig_candidate )as _ :
                _SIG_ALG =_sig_candidate 
            break 
        except Exception :
            pass 
    BACKEND =f'liboqs-{_KEM_ALG }'
except Exception :
    oqs =None 
    _KEM_ALG =None 
    _SIG_ALG =None 
    BACKEND ='MOCK'
from cryptography .hazmat .primitives .ciphers .aead import AESGCM 
from cryptography .hazmat .primitives .hashes import SHA256 
from cryptography .hazmat .primitives .kdf .hkdf import HKDF 
_RUNS_DIR =pathlib .Path ('runs')

def _hkdf (ikm :bytes ,info :bytes =b'raksha-net-session')->bytes :
    kdf =HKDF (algorithm =SHA256 (),length =32 ,salt =None ,info =info )
    return kdf .derive (ikm )

def _kem_handshake ()->tuple [bytes ,float ]:
    t0 =time .perf_counter ()
    if oqs is not None :
        with oqs .KeyEncapsulation (_KEM_ALG )as client :
            pk =client .generate_keypair ()
            with oqs .KeyEncapsulation (_KEM_ALG )as server :
                ct ,ss_srv =server .encap_secret (pk )
            ss_cli =client .decap_secret (ct )
        assert ss_cli ==ss_srv ,'KEM shared secret mismatch!'
        ss =ss_cli 
    else :
        ss =os .urandom (32 )
    wall_ms =(time .perf_counter ()-t0 )*1000.0 
    return (ss ,wall_ms )

def _sign (payload :bytes )->bytes |None :
    if oqs is None or _SIG_ALG is None :
        return None 
    with oqs .Signature (_SIG_ALG )as signer :
        pk =signer .generate_keypair ()
        sig =signer .sign (payload )
        with oqs .Signature (_SIG_ALG )as verifier :
            verifier .verify (payload ,sig ,pk )
    return sig 

def encrypt_message (key :bytes ,plaintext :bytes ,aad :bytes =b'')->bytes :
    nonce =os .urandom (12 )
    ct =AESGCM (key ).encrypt (nonce ,plaintext ,aad )
    return nonce +ct 

def decrypt_message (key :bytes ,payload :bytes ,aad :bytes =b'')->bytes :
    nonce ,ct =(payload [:12 ],payload [12 :])
    return AESGCM (key ).decrypt (nonce ,ct ,aad )

class SecurityEngine :

    def __init__ (self ,rekey_interval_s :float =0.0 ,allow_classical :bool =False ):
        self .state =SecState .NORMAL 
        self .events :List [SecurityEvent ]=[]
        self .isolated :List [str ]=[]
        self ._rekeyed_vias :set [str ]=set ()
        self .rekey_interval_s =rekey_interval_s 
        self .allow_classical =allow_classical 
        self ._last_rekey_wall :float =time .time ()
        self ._session_id :str =str (uuid .uuid4 ())[:8 ]
        self ._last_bw :float =0.0 
        self .suite :ca .Suite =ca .PQC_AES 
        self .session_key ,_ ,_ =ca .handshake (self .suite ,b'initial')
        self .session_counter :int =0 
        self .session_master :str ='GW'
        self ._leach_round :int =0 
        self .candidate_masters :List [str ]=['GW','LEO1','LEO2']
        _RUNS_DIR .mkdir (exist_ok =True )
        self ._events_path =_RUNS_DIR /'events.jsonl'

    def _log (self ,t_ms :int ,state :SecState ,detail :str ,rekey_ms :float =0.0 )->SecurityEvent :
        self .state =state 
        e =SecurityEvent (t_ms =t_ms ,state =state ,detail =detail ,backend =BACKEND ,rekey_ms =rekey_ms ,isolated_nodes =list (self .isolated ),suite =self .suite .name ,bw_mbps =round (self ._last_bw ,2 ))
        self .events .append (e )
        try :
            with self ._events_path .open ('a')as f :
                f .write (json .dumps ({'t_ms':t_ms ,'state':state .value ,'detail':detail ,'backend':BACKEND ,'rekey_ms':rekey_ms ,'session_id':self ._session_id ,'isolated':list (self .isolated ),'suite':self .suite .name ,'kex':self .suite .kex ,'aead':self .suite .aead ,'bw_mbps':round (self ._last_bw ,2 )})+'\n')
        except OSError :
            pass 
        return e 

    def _do_rekey (self ,t_ms :int ,reason :str ,bw_mbps :float |None =None ,threat :bool =False )->float :
        self ._last_bw =bw_mbps if bw_mbps is not None else 0.0 
        self .suite =ca .select_suite (bw_mbps ,threat ,self .allow_classical )
        tx =ca .transmit_ms (self .suite ,bw_mbps )
        tx_note =f', est. tx {tx :.2f} ms'if tx is not None else ''
        self ._log (t_ms ,SecState .REKEY ,f'Rekey required: {reason } | suite={self .suite .name } ({self .suite .kex }+{self .suite .aead }, {self .suite .handshake_bytes } B{tx_note })')
        key ,wall_ms ,real =ca .handshake (self .suite ,reason .encode ())
        self .session_key =key 
        self ._session_id =str (uuid .uuid4 ())[:8 ]
        self .session_counter =0 
        self ._last_rekey_wall =time .time ()
        return wall_ms if real else 0.0 

    def on_threat (self ,t_ms :int ,link_id :str ,anomaly :float ,via :str ='',bw_mbps :float |None =None )->SecurityEvent :
        self ._log (t_ms ,SecState .THREAT_DETECTED ,f'{link_id } anomaly={anomaly :.3f}')
        if link_id not in self .isolated :
            self .isolated .append (link_id )
        key =via if via else link_id 
        if key in self ._rekeyed_vias :
            return self ._log (t_ms ,SecState .THREAT_DETECTED ,f'{link_id } isolated (re-key already done for {key })')
        self ._rekeyed_vias .add (key )
        wall_ms =self ._do_rekey (t_ms ,f'{link_id } isolation',bw_mbps =bw_mbps ,threat =True )
        return self ._log (t_ms ,SecState .PQC_SESSION ,f'new session, {link_id } isolated | backend={BACKEND } | suite={self .suite .name }',rekey_ms =wall_ms )

    def on_recovery (self ,t_ms :int ,link_id :str ,via :str ='',bw_mbps :float |None =None )->SecurityEvent :
        if link_id not in self .isolated :
            return self ._log (t_ms ,SecState .NORMAL ,f'{link_id } recovery (was not isolated)')
        self .isolated .remove (link_id )
        key =via if via else link_id 
        self ._rekeyed_vias .discard (key )
        wall_ms =self ._do_rekey (t_ms ,f'{link_id } re-authentication',bw_mbps =bw_mbps ,threat =False )
        return self ._log (t_ms ,SecState .PQC_SESSION ,f'{link_id } un-isolated; re-auth done | suite={self .suite .name }',rekey_ms =wall_ms )

    def periodic_rekey_if_due (self ,t_ms :int ,bw_mbps :float |None =None )->SecurityEvent |None :
        if self .rekey_interval_s <=0 :
            return None 
        if time .time ()-self ._last_rekey_wall >=self .rekey_interval_s :
            wall_ms =self ._do_rekey (t_ms ,'periodic',bw_mbps =bw_mbps ,threat =bool (self .isolated ))
            return self ._log (t_ms ,SecState .PQC_SESSION ,f'periodic re-key | suite={self .suite .name }',rekey_ms =wall_ms )
        return None 

    def reset_incident (self ):
        self ._rekeyed_vias .clear ()

    def send_message (self ,plaintext :bytes )->dict :
        if not plaintext :
            return {}
        self .session_counter +=1 
        aad =f'raksha:{self ._session_id }:{self .session_counter }'.encode ()
        ct =ca .aead_encrypt (self .suite .aead ,self .session_key ,plaintext ,aad )
        return {'session_id':self ._session_id ,'counter':self .session_counter ,'suite':self .suite .name ,'ciphertext_hex':ct .hex (),'aad':aad .decode ()}

    def receive_message (self ,payload :dict )->bytes :
        sid =payload .get ('session_id','')
        if sid !=self ._session_id :
            raise ValueError (f'Message from stale/isolated session {sid !r }')
        aad =payload .get ('aad','').encode ()
        ct =bytes .fromhex (payload ['ciphertext_hex'])
        return ca .aead_decrypt (self .suite .aead ,self .session_key ,ct ,aad )

    def get_leach_threshold (self ,p :float =0.333 ,round_num :int |None =None )->float :
        """
        Classic LEACH cluster-head election threshold formula:
        T(n) = p / (1 - p * (r mod (1/p)))
        """
        r =self ._leach_round if round_num is None else int (round_num )
        period =int (round (1.0 /p ))if p >0 else 1 
        denom =1.0 -p *(r %period )
        return round (p /denom ,4 )if denom >0 else 1.0 

    def elect_session_master (
        self ,
        t_ms :int ,
        round_num :int |None =None ,
        energy_levels :dict [str ,float ]|None =None ,
        trust_levels :dict [str ,float ]|None =None ,
        mode :str ='energy_trust'
    )->tuple [str ,bool ]:
        """
        LEACH-inspired Cluster Head / Crypto Session Master election.
        Rotates key custody to prevent Gateway from being a single point of failure (SPOF).
        Excludes isolated/compromised nodes.

        Modes:
          - 'energy_trust': Elect candidate with highest residual energy * trust score.
          - 'stochastic': Round-robin rotation among eligible non-isolated nodes.

        Returns (elected_master, rotated_bool).
        """
        if round_num is not None :
            self ._leach_round =round_num 
        else :
            self ._leach_round +=1 

        eligible =[c for c in self .candidate_masters if c not in self .isolated ]
        if not eligible :
            eligible =['GW']

        old_master =self .session_master 

        if mode =='energy_trust'and (energy_levels or trust_levels ):
            e_map =energy_levels or {}
            t_map =trust_levels or {}
            scores ={}
            for c in eligible :
                e_val =e_map .get (c ,1.0 )
                t_val =t_map .get (c ,0.95 )
                scores [c ]=e_val *t_val 
            new_master =max (scores ,key =scores .get )
        else :
            idx =self ._leach_round %len (eligible )
            new_master =eligible [idx ]

        rotated =False 
        if new_master !=old_master :
            self .session_master =new_master 
            wall_ms =self ._do_rekey (t_ms ,f'LEACH CH rotation {old_master }->{new_master }',threat =False )
            self ._log (
                t_ms ,
                SecState .PQC_SESSION ,
                f'LEACH master handover: {old_master }->{new_master } | rekey={wall_ms :.2f}ms',
                rekey_ms =wall_ms 
            )
            rotated =True 

        return (new_master ,rotated )