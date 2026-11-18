from __future__ import annotations 
import os 
import time 
import hashlib 
QKD_LABEL ='SIMULATED / not available'
QKD_AVAILABLE =False 

class QKDInterface :

    def __init__ (self ):
        self .label =QKD_LABEL 
        self .available =QKD_AVAILABLE 
        self ._sim_keys :list [bytes ]=[]
        self ._key_count =0 

    def request_key (self ,key_id :str ='',length :int =32 )->dict :
        _start =time .perf_counter ()
        seed =os .urandom (16 )
        key =hashlib .sha256 (seed +key_id .encode ()).digest ()[:length ]
        sim_latency_ms =(time .perf_counter ()-_start )*1000 
        self ._key_count +=1 
        return {'key_bytes':key ,'key_id':key_id or f'qkd-sim-{self ._key_count :04d}','length':length ,'simulated':True ,'available':False ,'label':QKD_LABEL ,'latency_ms':round (sim_latency_ms ,3 )}

    def status (self )->dict :
        return {'available':False ,'label':QKD_LABEL ,'keys_issued':self ._key_count ,'note':'Real QKD: future upgrade path. Requires quantum channel hardware.'}