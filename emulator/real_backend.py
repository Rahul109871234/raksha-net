from __future__ import annotations 
import re 
import subprocess 
import time 
from typing import Optional 
from common .interfaces import LinkTelemetry 
from emulator .network_emulator import PROFILES ,apply_netem 
CONTAINER_IFACES :dict [str ,tuple [str ,str ]]={'A-GW':('gateway','eth0'),'GW-LEO1':('leo1','eth0'),'GW-LEO2':('leo2','eth0'),'LEO1-B':('node_b','eth0'),'LEO2-B':('node_b','eth1')}
PING_TARGETS :dict [str ,tuple [str ,str ]]={'A-GW':('node_a','10.10.1.3'),'GW-LEO1':('gateway','10.10.2.3'),'GW-LEO2':('gateway','10.10.3.3'),'LEO1-B':('leo1','10.10.4.3'),'LEO2-B':('leo2','10.10.5.3')}
GATEWAY_ROUTES :dict [str ,dict ]={'R1':{'dest':'10.10.4.0/24','via':'10.10.2.3'},'R2':{'dest':'10.10.5.0/24','via':'10.10.3.3'}}

def _ping_stats (container :str ,target_ip :str ,count :int =5 )->dict [str ,float ]:
    cmd =['docker','exec',container ,'ping','-c',str (count ),'-W','1',target_ip ]
    try :
        result =subprocess .run (cmd ,capture_output =True ,text =True ,timeout =15 )
        out =result .stdout 
        loss_match =re .search ('(\\d+)%\\s+packet loss',out )
        loss =float (loss_match .group (1 ))/100.0 if loss_match else 1.0 
        rtt_match =re .search ('rtt min/avg/max/mdev\\s*=\\s*([\\d.]+)/([\\d.]+)/([\\d.]+)/([\\d.]+)',out )
        if rtt_match :
            lat =float (rtt_match .group (2 ))
            jit =float (rtt_match .group (4 ))
        else :
            lat ,jit =(999.0 ,0.0 )
        return {'latency_ms':lat ,'jitter_ms':jit ,'loss':loss }
    except Exception as e :
        return {'latency_ms':999.0 ,'jitter_ms':0.0 ,'loss':1.0 ,'_error':str (e )}

class RealNetworkBackend :

    def __init__ (self ,link_ids :list [str ]):
        self .t_ms :int =0 
        self ._profiles :dict [str ,str ]={l :'normal'for l in link_ids }
        self ._last_thr :dict [str ,float ]={l :50.0 for l in link_ids }

    def set_profile (self ,link_id :str ,profile :str ,ramp_steps :Optional [int ]=None ):
        assert profile in PROFILES 
        self ._profiles [link_id ]=profile 
        if link_id in CONTAINER_IFACES :
            container ,iface =CONTAINER_IFACES [link_id ]
            try :
                apply_netem (container ,iface ,profile )
            except Exception as e :
                print (f'[RealBackend] apply_netem failed for {link_id }: {e }')

    def set_profile_instant (self ,link_id :str ,profile :str ):
        self .set_profile (link_id ,profile )

    def tick (self ,dt_ms :int =100 ):
        self .t_ms +=dt_ms 

    def sample (self ,link_id :str )->LinkTelemetry :
        if link_id in PING_TARGETS :
            container ,target =PING_TARGETS [link_id ]
            stats =_ping_stats (container ,target ,count =3 )
        else :
            lat ,jit ,loss ,thr ,q =PROFILES [self ._profiles .get (link_id ,'normal')]
            stats ={'latency_ms':lat ,'jitter_ms':jit ,'loss':loss }
        thr =PROFILES [self ._profiles .get (link_id ,'normal')][3 ]
        q =PROFILES [self ._profiles .get (link_id ,'normal')][4 ]
        return LinkTelemetry (link_id =link_id ,t_ms =self .t_ms ,latency_ms =stats ['latency_ms'],jitter_ms =stats ['jitter_ms'],loss =stats ['loss'],throughput_mbps =thr ,queue_depth =q )

    def send (self ,link_ids :list [str ],n :int =20 )->tuple [int ,int ]:
        import random 
        ok =0 
        rng =random .Random ()
        for _ in range (n ):
            delivered =all ((rng .random ()>PROFILES [self ._profiles .get (l ,'normal')][2 ]for l in link_ids ))
            if delivered :
                ok +=1 
        return (ok ,n )

    def set_gateway_route (self ,route_name :str ):
        route =GATEWAY_ROUTES .get (route_name )
        if not route :
            print (f'[RealBackend] Unknown route: {route_name }')
            return 
        cmd =['docker','exec','gateway','ip','route','replace',route ['dest'],'via',route ['via']]
        try :
            subprocess .run (cmd ,check =True ,timeout =5 )
            print (f'[RealBackend] Gateway route set to {route_name }: {route }')
        except Exception as e :
            print (f'[RealBackend] Route switch failed: {e }')