from __future__ import annotations 
from common .interfaces import LinkTelemetry 
from controller .anomaly_engine import GraphSAGEFallback ,make_detector 
from controller .controller import Controller 

def _window (lat ,jit ,loss ,thr ,q ):
    return [LinkTelemetry ('GW-LEO1',i *100 ,lat ,jit ,loss ,thr ,q )for i in range (5 )]

def test_make_detector_loads_weights_by_default ():
    det =make_detector ('graphsage')
    assert isinstance (det ,GraphSAGEFallback )
    assert det ._loaded ,'graphsage weights were not loaded'

def test_normal_scores_low_and_attack_scores_high ():
    det =make_detector ('graphsage')
    assert det .score (_window (20 ,2 ,0.01 ,50.0 ,0.15 ))<0.3 
    assert det .score (_window (170 ,45 ,0.42 ,8.0 ,0.9 ))>0.5 

def test_no_false_isolation_over_300_normal_cycles ():
    c =Controller (seed =17 ,detector_name ='graphsage',allow_recovery =False )
    for _ in range (300 ):
        c .step ()
    assert not any ((s .isolated for s in c .state .values ()))

def test_graphsage_isolates_and_reroutes_on_severe_degradation ():
    c =Controller (seed =1 ,detector_name ='graphsage',allow_recovery =False )
    for _ in range (25 ):
        c .step ()
    c .net .set_profile ('GW-LEO1','severe')
    c .net .set_profile ('LEO1-B','severe')
    for _ in range (40 ):
        c .step ()
    assert c .router .active =='R2'
    assert any ((c .state [l ].isolated for l in ('GW-LEO1','LEO1-B')))