from __future__ import annotations 
import os 
import pytest 
from cryptography .exceptions import InvalidTag 
from controller import crypto_agility as ca 
from controller .security_engine import SecurityEngine 
from controller .controller import Controller 

class TestPolicy :

    def test_high_bw_no_threat_is_pqc_aes (self ):
        assert ca .select_suite (50.0 ,threat =False )is ca .PQC_AES 

    def test_low_bw_no_threat_is_pqc_chacha (self ):
        assert ca .select_suite (8.0 ,threat =False )is ca .PQC_CHACHA 

    def test_threat_is_hybrid (self ):
        assert ca .select_suite (50.0 ,threat =True )is ca .HYBRID_AES 
        assert ca .select_suite (8.0 ,threat =True )is ca .HYBRID_CHACHA 

    def test_classical_only_when_opted_in (self ):
        assert ca .select_suite (5.0 ,False )is ca .PQC_CHACHA 
        assert ca .select_suite (5.0 ,False ,allow_classical =True )is ca .CLASSICAL_CHACHA 
        assert ca .select_suite (5.0 ,True ,allow_classical =True ).hybrid 

    def test_unknown_bw_treated_as_high (self ):
        assert ca .select_suite (None ,False )is ca .PQC_AES 

    def test_transmit_time_scales_with_bandwidth (self ):
        slow =ca .transmit_ms (ca .HYBRID_AES ,1.0 )
        fast =ca .transmit_ms (ca .HYBRID_AES ,100.0 )
        assert slow ==pytest .approx (fast *100 )
        assert ca .HYBRID_AES .handshake_bytes >ca .PQC_AES .handshake_bytes >ca .CLASSICAL_CHACHA .handshake_bytes 

class TestHandshakeAndAead :

    @pytest .mark .parametrize ('suite',list (ca .SUITES .values ()))
    def test_handshake_yields_32_byte_key (self ,suite ):
        key ,ms ,real =ca .handshake (suite ,b't')
        assert len (key )==32 and ms >=0 

    def test_hybrid_keys_differ_per_handshake (self ):
        k1 ,_ ,_ =ca .handshake (ca .HYBRID_AES ,b't')
        k2 ,_ ,_ =ca .handshake (ca .HYBRID_AES ,b't')
        assert k1 !=k2 

    @pytest .mark .parametrize ('aead',['AES-256-GCM','ChaCha20-Poly1305'])
    def test_aead_round_trip_and_tamper (self ,aead ):
        key =os .urandom (32 )
        ct =ca .aead_encrypt (aead ,key ,b'payload',b'aad')
        assert ca .aead_decrypt (aead ,key ,ct ,b'aad')==b'payload'
        bad =bytearray (ct )
        bad [-1 ]^=255 
        with pytest .raises (InvalidTag ):
            ca .aead_decrypt (aead ,key ,bytes (bad ),b'aad')

class TestEngineIntegration :

    def test_threat_on_low_bw_switches_to_hybrid_chacha_and_messages_work (self ):
        sec =SecurityEngine ()
        assert sec .suite is ca .PQC_AES 
        sec .on_threat (100 ,'GW-LEO1',0.9 ,via ='LEO1',bw_mbps =8.0 )
        assert sec .suite is ca .HYBRID_CHACHA 
        msg =sec .send_message (b'hello')
        assert msg ['suite']=='HYBRID_CHACHA'
        assert sec .receive_message (msg )==b'hello'

    def test_recovery_on_high_bw_drops_back_to_pqc_aes (self ):
        sec =SecurityEngine ()
        sec .on_threat (100 ,'GW-LEO1',0.9 ,via ='LEO1',bw_mbps =8.0 )
        sec .on_recovery (200 ,'GW-LEO1',via ='LEO1',bw_mbps =50.0 )
        assert sec .suite is ca .PQC_AES 
        assert sec .receive_message (sec .send_message (b'ok'))==b'ok'

    def test_events_record_suite (self ):
        sec =SecurityEngine ()
        sec .on_threat (100 ,'GW-LEO1',0.9 ,via ='LEO1',bw_mbps =8.0 )
        assert any ((e .suite =='HYBRID_CHACHA'and e .bw_mbps ==8.0 for e in sec .events ))

    def test_controller_threat_picks_hybrid_suite (self ):
        c =Controller (seed =2 ,allow_recovery =False )
        for _ in range (20 ):
            c .step ()
        c .net .set_profile ('GW-LEO1','severe')
        c .net .set_profile ('LEO1-B','severe')
        for _ in range (40 ):
            c .step ()
        assert c .sec .suite .hybrid ,f'expected hybrid suite, got {c .sec .suite .name }'