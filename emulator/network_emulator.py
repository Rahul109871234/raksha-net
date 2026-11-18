import random 
import subprocess 
from dataclasses import dataclass 
from typing import Optional 
from common .interfaces import LinkTelemetry 
PROFILES :dict [str ,tuple ]={'normal':(20 ,2 ,0.01 ,50.0 ,0.15 ),'low':(40 ,8 ,0.08 ,35.0 ,0.35 ),'medium':(90 ,20 ,0.22 ,20.0 ,0.6 ),'severe':(170 ,45 ,0.42 ,8.0 ,0.9 ),'failed':(999 ,0 ,1.0 ,0.0 ,1.0 )}
PROFILE_ORDER =['normal','low','medium','severe','failed']

def _interp (a :tuple ,b :tuple ,alpha :float )->tuple :
    return tuple ((x +alpha *(y -x )for x ,y in zip (a ,b )))

@dataclass 
class Link :
    link_id :str 
    profile :str ='normal'
    _target_profile :str ='normal'
    _ramp_step :int =0 
    _ramp_total :int =0 

class NetworkEmulator :

    def __init__ (self ,link_ids ,seed :int =0 ,ramp_steps :int =15 ):
        self .links :dict [str ,Link ]={l :Link (l )for l in link_ids }
        self .rng =random .Random (seed )
        self .t_ms :int =0 
        self .ramp_steps =ramp_steps 
        self ._burst_rng =random .Random (seed +99999 )
        self ._burst_active :dict [str ,int ]={}

    def set_profile (self ,link_id :str ,profile :str ,ramp_steps :Optional [int ]=None ):
        assert profile in PROFILES ,f'Unknown profile: {profile }'
        lnk =self .links [link_id ]
        lnk ._target_profile =profile 
        steps =ramp_steps if ramp_steps is not None else self .ramp_steps 
        lnk ._ramp_total =steps 
        lnk ._ramp_step =0 

    def set_profile_instant (self ,link_id :str ,profile :str ):
        assert profile in PROFILES 
        lnk =self .links [link_id ]
        lnk .profile =profile 
        lnk ._target_profile =profile 
        lnk ._ramp_step =0 
        lnk ._ramp_total =0 

    def tick (self ,dt_ms :int =100 ):
        self .t_ms +=dt_ms 
        for lnk in self .links .values ():
            if lnk ._ramp_total >0 and lnk ._ramp_step <lnk ._ramp_total :
                lnk ._ramp_step +=1 
                if lnk ._ramp_step >=lnk ._ramp_total :
                    lnk .profile =lnk ._target_profile 
                    lnk ._ramp_total =0 
                    lnk ._ramp_step =0 

    def _effective_params (self ,lnk :Link )->tuple :
        if lnk ._ramp_total >0 and lnk ._ramp_step <lnk ._ramp_total :
            alpha =lnk ._ramp_step /lnk ._ramp_total 
            src =PROFILES [lnk .profile ]
            dst =PROFILES [lnk ._target_profile ]
            return _interp (src ,dst ,alpha )
        return PROFILES [lnk .profile ]

    def sample (self ,link_id :str )->LinkTelemetry :
        lnk =self .links [link_id ]
        lat ,jit ,loss ,thr ,q =self ._effective_params (lnk )
        r =self .rng 
        if link_id not in self ._burst_active :
            if self ._burst_rng .random ()<0.05 :
                self ._burst_active [link_id ]=self ._burst_rng .randint (2 ,4 )
        if link_id in self ._burst_active :
            jit =jit *self ._burst_rng .uniform (2.5 ,4.0 )
            lat =lat *self ._burst_rng .uniform (1.2 ,1.8 )
            self ._burst_active [link_id ]-=1 
            if self ._burst_active [link_id ]<=0 :
                del self ._burst_active [link_id ]
        sampled_lat =max (1.0 ,r .gauss (lat ,max (jit ,0.1 )))
        sampled_loss =min (1.0 ,max (0.0 ,r .gauss (loss ,0.01 +loss *0.1 )))
        sampled_thr =max (0.0 ,r .gauss (thr ,thr *0.05 +0.1 ))
        sampled_q =min (1.0 ,max (0.0 ,r .gauss (q ,0.03 )))
        return LinkTelemetry (link_id =link_id ,t_ms =self .t_ms ,latency_ms =sampled_lat ,jitter_ms =jit ,loss =sampled_loss ,throughput_mbps =sampled_thr ,queue_depth =sampled_q )

    def send (self ,link_ids ,n :int =20 )->tuple [int ,int ]:
        ok =0 
        for _ in range (n ):
            delivered =True 
            for l in link_ids :
                _ ,_ ,loss ,_ ,_ =self ._effective_params (self .links [l ])
                if self .rng .random ()<=loss :
                    delivered =False 
                    break 
            if delivered :
                ok +=1 
        return (ok ,n )

    def current_profile (self ,link_id :str )->str :
        return self .links [link_id ].profile 

    def target_profile (self ,link_id :str )->str :
        return self .links [link_id ]._target_profile 

    def is_ramping (self ,link_id :str )->bool :
        lnk =self .links [link_id ]
        return lnk ._ramp_total >0 and lnk ._ramp_step <lnk ._ramp_total 

def apply_netem (container :str ,iface :str ,profile :str ):
    lat ,jit ,loss ,thr ,_ =PROFILES [profile ]
    cmd =['docker','exec',container ,'tc','qdisc','replace','dev',iface ,'root','netem','delay',f'{lat }ms',f'{jit }ms','loss',f'{loss *100 :.1f}%','rate',f'{max (thr ,0.1 )}mbit']
    subprocess .run (cmd ,check =True ,timeout =10 )