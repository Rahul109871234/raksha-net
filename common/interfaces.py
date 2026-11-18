from dataclasses import dataclass ,field 
from enum import Enum 
from typing import List 

@dataclass 
class LinkTelemetry :
    link_id :str 
    t_ms :int 
    latency_ms :float 
    jitter_ms :float 
    loss :float 
    throughput_mbps :float 
    queue_depth :float 

@dataclass 
class LinkState :
    link_id :str 
    trust :float =0.95 
    anomaly :float =0.0 
    isolated :bool =False 

@dataclass 
class Route :
    name :str 
    hops :List [str ]
    via :str 

@dataclass 
class RouteDecision :
    t_ms :int 
    chosen :str 
    previous :str 
    scores :dict 
    reason :str 

class SecState (str ,Enum ):
    NORMAL ='NORMAL'
    THREAT_DETECTED ='THREAT_DETECTED'
    REKEY ='REKEY_REQUIRED'
    PQC_SESSION ='PQC_SESSION_ESTABLISHED'

@dataclass 
class SecurityEvent :
    t_ms :int 
    state :SecState 
    detail :str 
    backend :str =''
    rekey_ms :float =0.0 
    isolated_nodes :List [str ]=field (default_factory =list )
    suite :str =''
    bw_mbps :float =0.0 