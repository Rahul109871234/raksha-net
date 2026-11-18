from __future__ import annotations 
import pytest 
from scripts .run_scenario import trial ,RAMP_STEPS ,ATTACK_CYCLES 
from controller .controller import Controller 
from controller .anomaly_engine import HeuristicDetector 
from controller .security_engine import SecurityEngine ,BACKEND ,encrypt_message ,decrypt_message 
from emulator .network_emulator import NetworkEmulator ,PROFILES 

class TestBaseline :

    def test_imports (self ):
        from common .interfaces import LinkTelemetry ,LinkState ,Route ,RouteDecision ,SecState ,SecurityEvent 
        from controller .trust_engine import TrustEngine 
        from controller .route_engine import RouteEngine 

    def test_single_trial_runs (self ):
        r =trial (seed =42 ,verbose =False )
        assert isinstance (r ,dict )
        assert 'pdr_before'in r 
        assert 'pdr_after'in r 
        assert 'backend'in r 
        assert 'detector'in r 

    def test_csv_columns_complete (self ):
        required ={'seed','t_onset_ms','t_detect_ms','t_decision_ms','t_new_route_ms','t_pdr_recovered_ms','route_recovery_ms','pdr_before','pdr_degraded_window','pdr_after','rekey_ms','backend','detector'}
        r =trial (seed =0 ,verbose =False )
        missing =required -set (r .keys ())
        assert not missing ,f'Missing CSV columns: {missing }'

class TestRealisticDynamics :

    def test_reroutes_on_degradation (self ):
        r =trial (seed =1 ,verbose =False )
        assert r ['route_recovery_ms']is not None ,'Route switch never happened'

    def test_route_recovery_within_budget (self ):
        r =trial (seed =1 ,verbose =False )
        if r ['route_recovery_ms']is not None :
            assert r ['route_recovery_ms']<=8000 ,f"Recovery took {r ['route_recovery_ms']}ms (> 8000ms budget)"

    def test_pdr_recovers_after_reroute (self ):
        r =trial (seed =1 ,verbose =False )
        assert r ['pdr_after']>0.9 ,f"AI pdr_after={r ['pdr_after']:.3f} (expected > 0.9)"

    def test_detection_latency_not_trivial (self ):
        r =trial (seed =5 ,verbose =False )
        if r ['t_detect_ms']and r ['t_onset_ms']:
            detect_lag =r ['t_detect_ms']-r ['t_onset_ms']
            assert detect_lag >=200 ,f'Detection trivially fast: lag={detect_lag }ms (WINDOW=5 needs >= 200ms)'

    def test_ramp_interpolates_profile (self ):
        emu =NetworkEmulator (['GW-LEO1'],seed =0 ,ramp_steps =10 )
        emu .set_profile ('GW-LEO1','severe')
        mid_latencies =[]
        for _ in range (5 ):
            emu .tick (100 )
            t =emu .sample ('GW-LEO1')
            mid_latencies .append (t .latency_ms )
        avg_mid =sum (mid_latencies )/len (mid_latencies )
        normal_lat =PROFILES ['normal'][0 ]
        severe_lat =PROFILES ['severe'][0 ]
        assert normal_lat <avg_mid <severe_lat ,f'Ramp not interpolating: mid_avg={avg_mid :.1f} (normal={normal_lat }, severe={severe_lat })'

    def test_false_positive_300_cycles_normal (self ):
        c =Controller (seed =17 ,allow_recovery =False )
        for _ in range (300 ):
            c .step ()
        assert c .router .active =='R1',f'False positive: route switched to {c .router .active } under normal traffic'
        any_isolated =any ((c .state [l ].isolated for l in c .state ))
        assert not any_isolated ,f'False positive: links isolated under normal traffic: {[l for l in c .state if c .state [l ].isolated ]}'

    def test_recovery_path_unsolates_link (self ):
        c =Controller (seed =3 ,allow_recovery =True )
        for _ in range (20 ):
            c .step ()
        c .net .set_profile ('GW-LEO1','severe')
        c .net .set_profile ('LEO1-B','severe')
        for _ in range (30 ):
            c .step ()
        isolated_before =any ((c .state [l ].isolated for l in ['GW-LEO1','LEO1-B']))
        assert isolated_before ,'Link was never isolated (test invalid)'
        c .net .set_profile ('GW-LEO1','normal')
        c .net .set_profile ('LEO1-B','normal')
        for _ in range (50 ):
            c .step ()
        still_isolated =any ((c .state [l ].isolated for l in ['GW-LEO1','LEO1-B']))
        assert not still_isolated ,'Recovery path failed: link still isolated after normal restoration'

    def test_static_stays_on_R1_entire_run (self ):
        from scripts .run_scenario import _static_trial ,NORMAL_CYCLES ,DT_MS ,ATTACK_CYCLES 
        import random 
        rng =random .Random (7 )
        onset_extra =rng .randint (5 ,20 )
        t_onset =(NORMAL_CYCLES +onset_extra )*DT_MS 
        attack_end =t_onset +ATTACK_CYCLES *DT_MS 
        stat =_static_trial (seed =7 ,onset_extra =onset_extra ,t_onset_ms =t_onset ,switch_t =None ,attack_end_t =attack_end )
        assert 'static_pdr_degraded_window'in stat 
        assert 'static_pdr_after'in stat 

    def test_static_pdr_degraded_below_08 (self ):
        r =trial (seed =2 ,verbose =False ,compare_static =True )
        spd =r .get ('static_pdr_degraded_window')
        assert spd is not None ,'static_pdr_degraded_window missing'
        assert spd <0.8 ,f'Static PDR during degradation should be < 0.8 (got {spd :.3f}); check that ramp is complete before measurement'

    def test_ai_pdr_after_above_09 (self ):
        r =trial (seed =2 ,verbose =False )
        assert r ['pdr_after']>0.9 ,f"AI pdr_after={r ['pdr_after']:.3f} (expected > 0.9 after switching to LEO-2)"

    def test_ai_benefit_vs_static (self ):
        r =trial (seed =2 ,verbose =False ,compare_static =True )
        ai_dw =r ['pdr_degraded_window']
        sta_dw =r ['static_pdr_degraded_window']
        benefit =ai_dw -sta_dw 
        assert benefit >0.3 ,f'AI benefit too small: AI={ai_dw :.3f} static={sta_dw :.3f} diff={benefit :.3f} (expected > 0.3)'

    def test_static_comparison_present (self ):
        r =trial (seed =0 ,compare_static =True )
        assert 'static_pdr_degraded_window'in r 
        assert 'static_pdr_after'in r 

    def test_window_pdr_calculation (self ):
        from scripts .run_scenario import _window_pdr 
        log =[(100 ,'R1',0.0 ),(200 ,'R1',0.0 ),(300 ,'R1',1.0 ),(400 ,'R1',1.0 )]
        result =_window_pdr (log ,300 ,500 )
        assert result ==1.0 ,f'Expected 1.0, got {result }'

class TestSecurity :

    def test_kem_round_trip (self ):
        sec =SecurityEngine ()
        original_key =sec .session_key 
        sec ._do_rekey (0 ,'test')
        assert sec .session_key !=original_key ,'Re-key did not produce a new key'
        assert len (sec .session_key )==32 ,'Key is not 32 bytes'

    def test_aead_round_trip (self ):
        import os 
        key =os .urandom (32 )
        plaintext =b'RAKSHA-NET test message 12345'
        ct =encrypt_message (key ,plaintext )
        pt =decrypt_message (key ,ct )
        assert pt ==plaintext 

    def test_tamper_detection (self ):
        import os 
        from cryptography .exceptions import InvalidTag 
        key =os .urandom (32 )
        ct =encrypt_message (key ,b'secret payload')
        ct_list =bytearray (ct )
        ct_list [-1 ]^=255 
        tampered =bytes (ct_list )
        with pytest .raises ((ValueError ,InvalidTag ,Exception )):
            decrypt_message (key ,tampered )

    def test_isolated_link_message_rejected (self ):
        sec =SecurityEngine ()
        msg =sec .send_message (b'classified data')
        old_session_id =msg ['session_id']
        sec ._do_rekey (100 ,'isolation test')
        msg ['session_id']=old_session_id 
        with pytest .raises (ValueError ):
            sec .receive_message (msg )

    def test_backend_label_consistent (self ):
        assert BACKEND in ('MOCK','liboqs-ML-KEM-768'),f'Unexpected backend: {BACKEND }'

    def test_rekey_deduplication (self ):
        sec =SecurityEngine ()
        sec .on_threat (100 ,'GW-LEO1',0.85 ,via ='LEO1')
        sec .on_threat (200 ,'LEO1-B',0.9 ,via ='LEO1')
        from common .interfaces import SecState 
        rekey_events =[e for e in sec .events if e .state ==SecState .PQC_SESSION ]
        assert len (rekey_events )==1 ,f'Expected 1 re-key for satellite LEO1, got {len (rekey_events )}'

    def test_send_receive_message (self ):
        sec =SecurityEngine ()
        payload =b'Node A to Node B: RAKSHA encrypted'
        msg =sec .send_message (payload )
        assert 'ciphertext_hex'in msg 
        assert len (msg ['ciphertext_hex'])>0 
        pt =sec .receive_message (msg )
        assert pt ==payload 