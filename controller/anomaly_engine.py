from __future__ import annotations 
import os 
import importlib .util 
from collections import deque 
from typing import List 
try:
    import numpy as np
except ImportError:
    np = None 
from common .interfaces import LinkTelemetry 
NORMAL_LAT =20.0 
NORMAL_LOSS =0.01 
NORMAL_Q =0.15 
W_LAT =0.35 
W_LOSS =0.45 
W_Q =0.2 
WINDOW =5 

def _raw_score (lat :float ,loss :float ,q :float )->float :
    s_lat =min (1.0 ,max (0.0 ,(lat -NORMAL_LAT )/150.0 ))
    s_loss =min (1.0 ,loss /0.4 )
    s_q =min (1.0 ,max (0.0 ,(q -NORMAL_Q )/0.75 ))
    return min (1.0 ,W_LAT *s_lat +W_LOSS *s_loss +W_Q *s_q )

class HeuristicDetector :
    LABEL ='HeuristicDetector'

    def __init__ (self ,window :int =WINDOW ,ewma_alpha :float =0.4 ):
        self ._window =window 
        self ._alpha =ewma_alpha 
        self ._raw_buf :dict [str ,deque ]={}
        self ._smoothed :dict [str ,float ]={}

    def score (self ,hist :List [LinkTelemetry ])->float :
        if not hist :
            return 0.0 
        link_id =hist [-1 ].link_id 
        if link_id not in self ._raw_buf :
            self ._raw_buf [link_id ]=deque (maxlen =self ._window )
            self ._smoothed [link_id ]=0.0 
        t =hist [-1 ]
        raw =_raw_score (t .latency_ms ,t .loss ,t .queue_depth )
        self ._raw_buf [link_id ].append (raw )
        buf =self ._raw_buf [link_id ]
        if len (buf )<self ._window :
            windowed =sum (buf )/self ._window 
        else :
            windowed =sum (buf )/self ._window 
        prev =self ._smoothed [link_id ]
        smoothed =self ._alpha *windowed +(1 -self ._alpha )*prev 
        self ._smoothed [link_id ]=smoothed 
        return round (min (1.0 ,smoothed ),3 )

class CUSUMDetector:
    """
    Page's Cumulative Sum (CUSUM) sequential change-point detector (Moustakides 1986).
    Computes: S_t = max(0, S_{t-1} + (z_t - k)), with drift k=0.50, threshold h=2.0.
    Supports proactive cross-layer pre-arming (priming S_0 = 1.0 on terrestrial FDI intent).
    """
    LABEL = 'CUSUMDetector'

    def __init__(self, drift_k: float = 0.50, threshold_h: float = 2.0):
        self.k = drift_k
        self.h = threshold_h
        self.S: Dict[str, float] = {}
        self.is_pre_armed: Dict[str, bool] = {}

    def pre_arm(self, link_id: str, primed_s0: float = 1.0):
        """Prime CUSUM state S_0 = 1.0 upon terrestrial cross-layer alert."""
        self.S[link_id] = max(self.S.get(link_id, 0.0), primed_s0)
        self.is_pre_armed[link_id] = True

    def reset_pre_arm(self, link_id: str):
        self.is_pre_armed[link_id] = False

    def score(self, hist: List[LinkTelemetry]) -> float:
        if not hist:
            return 0.0
        t = hist[-1]
        lid = t.link_id
        raw = _raw_score(t.latency_ms, t.loss, t.queue_depth)
        
        # Sequential CUSUM accumulation
        prev_s = self.S.get(lid, 0.0)
        curr_s = max(0.0, prev_s + (raw * 2.5 - self.k))
        self.S[lid] = curr_s
        
        # Normalized anomaly score [0.0, 1.0]
        return round(min(1.0, curr_s / self.h), 3)

class AICOPDetector:
    LABEL = 'AICOP-GraphSAGE'

    def __init__(self):
        self._fallback = None
        self._infer = None
        self._bridge = None
        self._graph_sage = None
        self._ckpt_path = os.environ.get('AICOP_CKPT', '')
        self._module_path = os.environ.get('AICOP_MODULE', '')
        
        # 1. Custom external checkpoint if supplied via environment
        if self._ckpt_path and self._module_path:
            try:
                spec = importlib.util.spec_from_file_location('aicop_inference', self._module_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self._infer = mod.infer
                if hasattr(mod, 'load_checkpoint'):
                    mod.load_checkpoint(self._ckpt_path)
                print(f'[AICOPDetector] Loaded custom module from {self._module_path} | ckpt={self._ckpt_path}')
                return
            except Exception as exc:
                print(f'[AICOPDetector] Custom load failed ({exc}) — falling back to internal bridge')

        # 2. Built-in Open-Source GraphSAGE Bridge (Included directly in repository)
        try:
            from controller.aicop_bridge import UnifiedAICOPBridge
            self._bridge = UnifiedAICOPBridge()
            self._graph_sage = GraphSAGEFallback()
            self.LABEL = 'AICOP-GraphSAGE (Built-in weights)'
            print('[AICOPDetector] Initialized built-in UnifiedAICOPBridge & GraphSAGE (models/aicop_trust_engine.npz)')
        except Exception as e:
            print(f'[AICOPDetector] Bridge load error ({e}) — falling back to HeuristicDetector')
            self._fallback = HeuristicDetector()
            self.LABEL = 'HeuristicDetector (AICOP fallback)'

    def score(self, hist: List[LinkTelemetry]) -> float:
        if self._infer is not None:
            if not hist:
                return 0.0
            graph = build_graph(hist)
            try:
                result = self._infer(graph)
                return round(float(result), 3)
            except Exception:
                pass
        if self._graph_sage is not None and self._graph_sage._loaded:
            return self._graph_sage.score(hist)
        if self._fallback is not None:
            return self._fallback.score(hist)
        return 0.0

class GraphSAGEFallback:
    LABEL = 'synthetic-trained GraphSAGE-style detector'

    def __init__(self, weights_path: str | None = None):
        self._w1: np.ndarray | None = None
        self._w2: np.ndarray | None = None
        self._b1: np.ndarray | None = None
        self._b2: np.ndarray | None = None
        self._loaded = False
        self._fallback = HeuristicDetector()
        
        if weights_path is None:
            import pathlib
            default_path = pathlib.Path(__file__).resolve().parent.parent / 'models' / 'graphsage_fallback.npz'
            if default_path.exists():
                weights_path = str(default_path)
                
        if weights_path:
            self.load(weights_path)

    def load (self ,path :str ):
        try :
            data =np .load (path )
            self ._w1 =data ['w1']
            self ._w2 =data ['w2']
            self ._b1 =data ['b1']
            self ._b2 =data ['b2']
            self ._loaded =True 
        except Exception as e :
            print (f'[GraphSAGEFallback] Cannot load weights {path }: {e }')

    @staticmethod 
    def _featurise (hist :List [LinkTelemetry ])->np .ndarray :
        window =hist [-5 :]if len (hist )>=5 else hist 
        n =len (window )
        lat =sum ((h .latency_ms for h in window ))/n 
        jit =sum ((h .jitter_ms for h in window ))/n 
        loss =sum ((h .loss for h in window ))/n 
        q =sum ((h .queue_depth for h in window ))/n 
        thr =sum ((h .throughput_mbps for h in window ))/n 
        return np .array ([lat /200.0 ,jit /50.0 ,loss ,q ,max (0 ,1 -thr /50.0 )],dtype =np .float32 )

    @staticmethod 
    def _relu (x :np .ndarray )->np .ndarray :
        return np .maximum (0 ,x )

    @staticmethod 
    def _sigmoid (x :float )->float :
        return 1.0 /(1.0 +np .exp (-x ))

    def _forward (self ,x :np .ndarray )->float :
        h1 =self ._relu (self ._w1 @x +self ._b1 )
        logit =float (self ._w2 @h1 +self ._b2 )
        return self ._sigmoid (logit )

    def score (self ,hist :List [LinkTelemetry ])->float :
        if not self ._loaded or self ._w1 is None :
            return self ._fallback .score (hist )
        if not hist :
            return 0.0 
        x =self ._featurise (hist )
        return round (float (self ._forward (x )),3 )

def build_graph (telemetry_hist :List [LinkTelemetry ]):
    import networkx as nx 
    G =nx .Graph ()
    NODES =['A','GW','LEO1','LEO2','B']
    for n in NODES :
        G .add_node (n )
    LINK_MAP ={'A-GW':('A','GW'),'GW-LEO1':('GW','LEO1'),'GW-LEO2':('GW','LEO2'),'LEO1-B':('LEO1','B'),'LEO2-B':('LEO2','B')}
    latest :dict [str ,LinkTelemetry ]={}
    for t in telemetry_hist :
        latest [t .link_id ]=t 
    for link_id ,(u ,v )in LINK_MAP .items ():
        if link_id in latest :
            t =latest [link_id ]
            G .add_edge (u ,v ,link_id =link_id ,latency_ms =t .latency_ms ,jitter_ms =t .jitter_ms ,loss =t .loss ,throughput_mbps =t .throughput_mbps ,queue_depth =t .queue_depth )
    return G 

def make_detector (name :str ,weights_path :str |None =None ):
    if name =='heuristic':
        return HeuristicDetector ()
    elif name =='graphsage':
        if weights_path is None :
            import pathlib 
            weights_path =str (pathlib .Path (__file__ ).resolve ().parent .parent /'models'/'graphsage_fallback.npz')
        det =GraphSAGEFallback (weights_path )
        if not det ._loaded :
            print ('[make_detector] WARNING: graphsage weights not loaded; falling back to HeuristicDetector. Run scripts/train_detector.py')
        return det 
    elif name =='aicop':
        return AICOPDetector ()
    else :
        raise ValueError (f'Unknown detector: {name !r }. Choose heuristic|graphsage|aicop')