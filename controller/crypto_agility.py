from __future__ import annotations 
import os 
import time 
from dataclasses import dataclass 
from typing import Optional 
from cryptography .hazmat .primitives .asymmetric .x25519 import X25519PrivateKey 
from cryptography .hazmat .primitives .ciphers .aead import AESGCM ,ChaCha20Poly1305 
from cryptography .hazmat .primitives .hashes import SHA256 
from cryptography .hazmat .primitives .kdf .hkdf import HKDF 
try :
    import oqs 
    _KEM_ALG :Optional [str ]='ML-KEM-768'
    with oqs .KeyEncapsulation (_KEM_ALG ):
        pass 
except Exception :
    oqs =None 
    _KEM_ALG =None 
HAS_MLKEM =oqs is not None 
AEAD_AES_MIN_MBPS =30.0 
CLASSICAL_MAX_MBPS =10.0 
_X25519_BYTES =32 +32 
_MLKEM768_BYTES =1184 +1088 

@dataclass (frozen =True )
class Suite :
    name :str 
    kex :str 
    aead :str 
    handshake_bytes :int 

    @property 
    def uses_mlkem (self )->bool :
        return 'ML-KEM'in self .kex 

    @property 
    def hybrid (self )->bool :
        return '+'in self .kex 
CLASSICAL_CHACHA =Suite ('CLASSICAL_CHACHA','X25519','ChaCha20-Poly1305',_X25519_BYTES )
PQC_CHACHA =Suite ('PQC_CHACHA','ML-KEM-768','ChaCha20-Poly1305',_MLKEM768_BYTES )
PQC_AES =Suite ('PQC_AES','ML-KEM-768','AES-256-GCM',_MLKEM768_BYTES )
HYBRID_CHACHA =Suite ('HYBRID_CHACHA','X25519+ML-KEM-768','ChaCha20-Poly1305',_X25519_BYTES +_MLKEM768_BYTES )
HYBRID_AES =Suite ('HYBRID_AES','X25519+ML-KEM-768','AES-256-GCM',_X25519_BYTES +_MLKEM768_BYTES )
SUITES ={s .name :s for s in (CLASSICAL_CHACHA ,PQC_CHACHA ,PQC_AES ,HYBRID_CHACHA ,HYBRID_AES )}

def select_suite (bw_mbps :Optional [float ],threat :bool ,allow_classical :bool =False )->Suite :
    bw =float ('inf')if bw_mbps is None else bw_mbps 
    low_bw =bw <AEAD_AES_MIN_MBPS 
    if threat :
        return HYBRID_CHACHA if low_bw else HYBRID_AES 
    if allow_classical and bw <CLASSICAL_MAX_MBPS :
        return CLASSICAL_CHACHA 
    return PQC_CHACHA if low_bw else PQC_AES 

def transmit_ms (suite :Suite ,bw_mbps :Optional [float ])->Optional [float ]:
    if not bw_mbps or bw_mbps <=0 :
        return None 
    return suite .handshake_bytes *8 /(bw_mbps *1000.0 )

def _mlkem_exchange ()->bytes :
    if oqs is None :
        return os .urandom (32 )
    with oqs .KeyEncapsulation (_KEM_ALG )as client :
        pk =client .generate_keypair ()
        with oqs .KeyEncapsulation (_KEM_ALG )as server :
            ct ,ss_srv =server .encap_secret (pk )
        ss_cli =client .decap_secret (ct )
    assert ss_cli ==ss_srv ,'ML-KEM shared secret mismatch!'
    return ss_cli 

def _x25519_exchange ()->bytes :
    a ,b =(X25519PrivateKey .generate (),X25519PrivateKey .generate ())
    ss_a =a .exchange (b .public_key ())
    ss_b =b .exchange (a .public_key ())
    assert ss_a ==ss_b ,'X25519 shared secret mismatch!'
    return ss_a 

def handshake (suite :Suite ,info :bytes =b'')->tuple [bytes ,float ,bool ]:
    t0 =time .perf_counter ()
    parts =[]
    if 'X25519'in suite .kex :
        parts .append (_x25519_exchange ())
    if suite .uses_mlkem :
        parts .append (_mlkem_exchange ())
    wall_ms =(time .perf_counter ()-t0 )*1000.0 
    ikm =b''.join (parts )
    key =HKDF (algorithm =SHA256 (),length =32 ,salt =None ,info =(suite .name .encode ()+b'|'+info )[:64 ]).derive (ikm )
    real =HAS_MLKEM or not suite .uses_mlkem 
    return (key ,wall_ms ,real )

def _aead (name :str ,key :bytes ):
    if name =='ChaCha20-Poly1305':
        return ChaCha20Poly1305 (key )
    if name =='AES-256-GCM':
        return AESGCM (key )
    raise ValueError (f'unknown AEAD {name !r }')

def aead_encrypt (name :str ,key :bytes ,plaintext :bytes ,aad :bytes =b'')->bytes :
    nonce =os .urandom (12 )
    return nonce +_aead (name ,key ).encrypt (nonce ,plaintext ,aad )

def aead_decrypt (name :str ,key :bytes ,payload :bytes ,aad :bytes =b'')->bytes :
    return _aead (name ,key ).decrypt (payload [:12 ],payload [12 :],aad )