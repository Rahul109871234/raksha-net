from __future__ import annotations 
import argparse 
import csv 
import logging 
import pathlib 
import random 
import statistics as _st 
import sys 
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import Optional 
from controller .controller import Controller 
from controller .security_engine import BACKEND 
logging .basicConfig (level =logging .INFO ,format ='%(asctime)s %(levelname)s %(name)s | %(message)s',datefmt ='%H:%M:%S')
log =logging .getLogger ('raksha.scenario')
DT_MS =100 
NORMAL_CYCLES =20 
ATTACK_CYCLES =60 
RECOVERY_CYCLES =30 
RAMP_STEPS =15 
PDR_AFTER_K =20 
ONSET_MIN =5 
ONSET_MAX =20 

def _pdr (c :Controller ,k :int =PDR_AFTER_K )->float :
    ok =n =0 
    for _ in range (k ):
        _ ,o ,m =c .step (DT_MS )
        ok +=o 
        n +=m 
    return ok /n if n else 0.0 

def _window_pdr (pdr_log :list ,start_t :int ,end_t :int )->float :
    window =[e [2 ]for e in pdr_log if start_t <=e [0 ]<end_t ]
    return sum (window )/len (window )if window else 0.0 

def trial (seed :int ,verbose :bool =False ,detector_name :str ='heuristic',compare_static :bool =False )->dict :
    rng =random .Random (seed )
    onset_extra =rng .randint (ONSET_MIN ,ONSET_MAX )
    c =Controller (seed =seed ,detector_name =detector_name ,verbose =verbose ,ramp_steps =RAMP_STEPS )
    for _ in range (NORMAL_CYCLES +onset_extra ):
        c .step (DT_MS )
    pdr_before =_pdr (c ,PDR_AFTER_K )
    t_onset_ms =c .net .t_ms 
    if verbose :
        log .info ('[Scene 1] Normal warm-up done. t=%dms pdr_before=%.3f',t_onset_ms ,pdr_before )
    c .net .set_profile ('GW-LEO1','severe')
    c .net .set_profile ('LEO1-B','severe')
    switch_t :Optional [int ]=None 
    t_detect_ms :Optional [int ]=None 
    pdr_log :list =[]
    for i in range (ATTACK_CYCLES ):
        d ,ok ,n =c .step (DT_MS )
        pdr =ok /n if n else 0.0 
        pdr_log .append ((c .net .t_ms ,d .chosen ,pdr ))
        if t_detect_ms is None :
            if max ((c .state [lk ].anomaly for lk in c .state ))>0.6 :
                t_detect_ms =c .net .t_ms 
        if switch_t is None and d .chosen =='R2':
            switch_t =c .net .t_ms 
            if verbose :
                log .info ('[Scene 3] ROUTE SWITCH R1->R2 at t=%dms | %s',switch_t ,d .reason )
    attack_end_t =t_onset_ms +ATTACK_CYCLES *DT_MS 
    pdr_degraded_window =round (_window_pdr (pdr_log ,t_onset_ms ,attack_end_t ),3 )
    dip_pdr =round (_window_pdr (pdr_log ,t_onset_ms ,switch_t ),3 )if switch_t else pdr_degraded_window 
    if verbose :
        for e in c .sec .events :
            log .info ('[SEC] t=%dms %s | %s | rekey_ms=%.2f',e .t_ms ,e .state .value ,e .detail ,e .rekey_ms )
    t_pdr_recovered :Optional [int ]=None 
    for i in range (2 ,len (pdr_log )):
        rolling =sum ((e [2 ]for e in pdr_log [i -2 :i +1 ]))/3 
        if rolling >=0.9 and pdr_log [i ][1 ]=='R2':
            t_pdr_recovered =pdr_log [i ][0 ]
            break 
    c .net .set_profile ('GW-LEO1','normal')
    c .net .set_profile ('LEO1-B','normal')
    for _ in range (RECOVERY_CYCLES ):
        c .step (DT_MS )
    if verbose :
        log .info ('[Scene 5] Recovery. Active route: %s | isolated: %s',c .router .active ,c .sec .isolated )
    pdr_after =round (_window_pdr (pdr_log +[(c .net .t_ms ,'',_pdr (c ,50 ))],c .net .t_ms -50 *DT_MS ,c .net .t_ms +DT_MS ),3 )
    ev =[e for e in c .sec .events if e .rekey_ms >0 and e .backend !='MOCK']
    rekey_ms =ev [0 ].rekey_ms if ev else None 
    result ={'seed':seed ,'t_onset_ms':t_onset_ms ,'t_detect_ms':t_detect_ms ,'t_decision_ms':switch_t ,'t_new_route_ms':switch_t ,'t_pdr_recovered_ms':t_pdr_recovered ,'route_recovery_ms':switch_t -t_onset_ms if switch_t else None ,'pdr_before':round (pdr_before ,3 ),'pdr_degraded_window':pdr_degraded_window ,'pdr_after':round (pdr_after ,3 ),'dip_pdr':dip_pdr ,'pdr_during':pdr_degraded_window ,'rekey_ms':round (rekey_ms ,3 )if rekey_ms else None ,'backend':BACKEND ,'detector':c .detector_name }
    if compare_static :
        stat =_static_trial (seed =seed ,onset_extra =onset_extra ,t_onset_ms =t_onset_ms ,switch_t =switch_t ,attack_end_t =attack_end_t )
        result .update (stat )
    if verbose :
        log .info ('RESULT: %s',result )
    return result 

def _static_trial (seed :int ,onset_extra :int ,t_onset_ms :int ,switch_t :Optional [int ],attack_end_t :int )->dict :
    cs =Controller (seed =seed ,detector_name ='heuristic',allow_recovery =False ,ramp_steps =RAMP_STEPS )
    from common .interfaces import RouteDecision 
    cs .router .active ='R1'
    cs .router .decide =lambda t_ms ,tel ,st :RouteDecision (t_ms ,'R1','R1',{},'static')
    for _ in range (NORMAL_CYCLES +onset_extra ):
        cs .step (DT_MS )
    cs .net .set_profile ('GW-LEO1','severe')
    cs .net .set_profile ('LEO1-B','severe')
    static_log :list =[]
    for _ in range (ATTACK_CYCLES ):
        _ ,ok ,n =cs .step (DT_MS )
        static_log .append ((cs .net .t_ms ,'R1',ok /n if n else 0 ))
    static_pdr_degraded =round (_window_pdr (static_log ,t_onset_ms ,attack_end_t ),3 )
    static_dip_pdr =round (_window_pdr (static_log ,t_onset_ms ,switch_t ),3 )if switch_t else static_pdr_degraded 
    cs .net .set_profile ('GW-LEO1','normal')
    cs .net .set_profile ('LEO1-B','normal')
    for _ in range (RECOVERY_CYCLES -50 ):
        cs .step (DT_MS )
    static_pdr_after =round (_window_pdr ([(cs .net .t_ms ,'',_pdr (cs ,50 ))],cs .net .t_ms -50 *DT_MS ,cs .net .t_ms +DT_MS ),3 )
    return {'static_pdr_degraded_window':static_pdr_degraded ,'static_pdr_after':static_pdr_after ,'static_dip_pdr':static_dip_pdr ,'static_pdr_during':static_pdr_degraded }

def _summarise (rows :list [dict ]):
    switched =[r for r in rows if r .get ('route_recovery_ms')is not None ]
    rr =[r ['route_recovery_ms']for r in switched ]
    pb =[r ['pdr_before']for r in rows ]
    pdw =[r ['pdr_degraded_window']for r in rows ]
    pa =[r ['pdr_after']for r in rows ]
    print ('\n'+'='*62 )
    print ('RAKSHA-NET — Experiment Summary (Emulated Testbed)')
    print ('='*62 )
    print (f'Trials: {len (rows )}  |  Switched: {len (switched )}/{len (rows )}')
    print (f"Backend: {rows [0 ]['backend']}  |  Detector: {rows [0 ]['detector']}")
    print (f'\nPDR windows (post-ramp steady-state, emulated-clock):')
    print (f'  before (normal):        {_st .mean (pb ):.3f}  SD={_st .pstdev (pb ):.4f}')
    print (f'  degraded_window (AI):   {_st .mean (pdw ):.3f}  SD={_st .pstdev (pdw ):.4f}')
    print (f'  after (AI, restored):   {_st .mean (pa ):.3f}  SD={_st .pstdev (pa ):.4f}')
    if rr :
        print (f'\nRoute-recovery time (emulated-clock ms):')
        print (f'  mean={_st .mean (rr ):.0f}  SD={_st .pstdev (rr ):.0f}  min={min (rr ):.0f}  max={max (rr ):.0f}')
    if rows [0 ].get ('static_pdr_degraded_window')is not None :
        spd =[r ['static_pdr_degraded_window']for r in rows ]
        spa =[r ['static_pdr_after']for r in rows ]
        print (f'\nAI vs Static routing — paired comparison:')
        print (f"  {'Metric':<30} {'AI':>8} {'Static':>8}  {'Diff':>8}")
        print (f"  {'-'*58 }")

        def _fmt (label ,ai_v ,st_v ):
            ai_m =_st .mean (ai_v )
            st_m =_st .mean (st_v )
            ai_sd =_st .pstdev (ai_v )
            st_sd =_st .pstdev (st_v )
            print (f'  {label :<30} {ai_m :.3f}({ai_sd :.3f}) {st_m :.3f}({st_sd :.3f})    {ai_m -st_m :+.3f}')
        _fmt ('pdr_degraded_window',pdw ,spd )
        _fmt ('pdr_after',pa ,spa )
        try :
            from scipy import stats 
            t_stat ,p_val =stats .ttest_rel (pdw ,spd )
            print (f'\n  Paired t-test (pdr_degraded_window, AI vs static):')
            print (f'    t={t_stat :.3f}  p={p_val :.4g}  n={len (rows )}')
            if p_val <0.05 :
                print (f'    *** statistically significant (p<0.05)')
            else :
                print (f'    (not significant at p=0.05)')
            print (f'  Exact window used: onset -> end of attack ({ATTACK_CYCLES } cycles)')
            if rows [0 ].get ('dip_pdr')is not None :
                ai_dip =[r ['dip_pdr']for r in rows ]
                st_dip =[r ['static_dip_pdr']for r in rows ]
                ai_dip_loss =[1.0 -x for x in ai_dip ]
                print (f'\n  Packet-loss dip (onset -> route switch):')
                print (f'    AI loss:     {_st .mean (ai_dip_loss )*100 :.1f}%')
                print (f'    Static loss: {(1.0 -_st .mean (st_dip ))*100 :.1f}%')
        except ImportError :
            print ('  (scipy not available for t-test)')
    rk =[r ['rekey_ms']for r in rows if r .get ('rekey_ms')]
    if rk :
        print (f'\nRekey time (wall-clock, liboqs only):')
        print (f'  mean={_st .mean (rk ):.2f}ms  SD={_st .pstdev (rk ):.2f}ms')
    print ('='*62 +'\n')
if __name__ =='__main__':
    ap =argparse .ArgumentParser (description ='RAKSHA-NET scenario runner')
    ap .add_argument ('--trials',type =int ,default =1 )
    ap .add_argument ('--csv',type =str ,default =None )
    ap .add_argument ('--detector',type =str ,default ='heuristic',choices =['heuristic','graphsage','aicop'])
    ap .add_argument ('--compare-static',action ='store_true')
    ap .add_argument ('--verbose',action ='store_true')
    a =ap .parse_args ()
    if a .trials ==1 :
        rows =[trial (0 ,verbose =True ,detector_name =a .detector ,compare_static =a .compare_static )]
    else :
        rows =[]
        for s in range (a .trials ):
            r =trial (s ,verbose =False ,detector_name =a .detector ,compare_static =a .compare_static )
            rows .append (r )
            pdw =r ['pdr_degraded_window']
            spd =r .get ('static_pdr_degraded_window',float ('nan'))
            print (f"  seed={s :3d}  rr={r ['route_recovery_ms']}ms  pdr_before={r ['pdr_before']:.2f}  pdr_dw(AI)={pdw :.2f}  pdr_dw(static)={spd :.2f}  pdr_after={r ['pdr_after']:.2f}")
    _summarise (rows )
    if a .csv :
        p =pathlib .Path (a .csv )
        p .parent .mkdir (parents =True ,exist_ok =True )
        with open (p ,'w',newline ='')as f :
            w =csv .DictWriter (f ,fieldnames =rows [0 ].keys ())
            w .writeheader ()
            w .writerows (rows )
        print (f'CSV written -> {p }')