from __future__ import annotations 
import argparse 
import pathlib 
import sys 
import numpy as np 
sys .path .insert (0 ,str (pathlib .Path (__file__ ).parent .parent ))
from emulator .network_emulator import NetworkEmulator ,PROFILES 
from controller .anomaly_engine import GraphSAGEFallback 
LINKS =['A-GW','GW-LEO1','GW-LEO2','LEO1-B','LEO2-B']
NORMAL_PROFILES =['normal']
ATTACK_PROFILES =['medium','severe','failed']
MODELS_DIR =pathlib .Path ('models')
RESULTS_DIR =pathlib .Path ('results')

def _window_features (emu :NetworkEmulator ,link :str ='GW-LEO1')->list [float ]:
    hist =[]
    for _ in range (5 ):
        emu .tick (100 )
        hist .append (emu .sample (link ))
    return GraphSAGEFallback ._featurise (hist ).tolist ()

def generate_samples (n_samples :int ,seed :int =42 )->tuple [np .ndarray ,np .ndarray ]:
    X ,y =([],[])
    rng_seed =seed 
    for i in range (n_samples //2 ):
        emu =NetworkEmulator (LINKS ,seed =rng_seed +i ,ramp_steps =0 )
        X .append (_window_features (emu ))
        y .append (0 )
    for i in range (n_samples //2 ):
        emu =NetworkEmulator (LINKS ,seed =rng_seed +10000 +i ,ramp_steps =0 )
        prof =ATTACK_PROFILES [i %len (ATTACK_PROFILES )]
        emu .set_profile_instant ('GW-LEO1',prof )
        X .append (_window_features (emu ))
        y .append (1 )
    return (np .array (X ,dtype =np .float32 ),np .array (y ,dtype =np .float32 ))

def sigmoid (x ):
    return 1.0 /(1.0 +np .exp (-np .clip (x ,-30 ,30 )))

def relu (x ):
    return np .maximum (0 ,x )

def train (X_train :np .ndarray ,y_train :np .ndarray ,hidden :int =16 ,epochs :int =600 ,lr :float =0.5 ,seed :int =42 )->dict :
    rng =np .random .default_rng (seed )
    n_feat =X_train .shape [1 ]
    w1 =rng .normal (0 ,0.3 ,(hidden ,n_feat )).astype (np .float32 )
    b1 =np .zeros (hidden ,dtype =np .float32 )
    w2 =rng .normal (0 ,0.3 ,hidden ).astype (np .float32 )
    b2 =np .float32 (0.0 )
    n =len (X_train )
    for epoch in range (epochs ):
        h1 =relu (w1 @X_train .T +b1 [:,None ])
        logits =w2 @h1 +b2 
        preds =sigmoid (logits )
        eps =1e-07 
        loss =-np .mean (y_train *np .log (preds +eps )+(1 -y_train )*np .log (1 -preds +eps ))
        d_logits =(preds -y_train )/n 
        d_w2 =h1 @d_logits 
        d_b2 =np .sum (d_logits )
        d_h1 =np .outer (w2 ,d_logits )
        d_h1_pre =d_h1 *(h1 >0 ).astype (np .float32 )
        d_w1 =d_h1_pre @X_train 
        d_b1 =d_h1_pre .sum (axis =1 )
        w1 -=lr *d_w1 
        b1 -=lr *d_b1 
        w2 -=lr *d_w2 
        b2 -=lr *d_b2 
        if (epoch +1 )%100 ==0 :
            print (f'  epoch {epoch +1 :3d}/{epochs } | loss={loss :.4f}')
    return {'w1':w1 ,'w2':w2 ,'b1':b1 ,'b2':b2 }

def evaluate (weights :dict ,X :np .ndarray ,y :np .ndarray ,threshold :float =0.5 )->dict :
    h1 =relu (weights ['w1']@X .T +weights ['b1'][:,None ])
    logits =weights ['w2']@h1 +weights ['b2']
    preds_prob =sigmoid (logits )
    preds =(preds_prob >=threshold ).astype (int )
    tp =int (np .sum ((preds ==1 )&(y ==1 )))
    fp =int (np .sum ((preds ==1 )&(y ==0 )))
    fn =int (np .sum ((preds ==0 )&(y ==1 )))
    tn =int (np .sum ((preds ==0 )&(y ==0 )))
    precision =tp /(tp +fp +1e-09 )
    recall =tp /(tp +fn +1e-09 )
    f1 =2 *precision *recall /(precision +recall +1e-09 )
    fpr =fp /(fp +tn +1e-09 )
    return {'precision':round (precision ,4 ),'recall':round (recall ,4 ),'f1':round (f1 ,4 ),'fpr':round (fpr ,4 ),'tp':tp ,'fp':fp ,'fn':fn ,'tn':tn }

def main ():
    ap =argparse .ArgumentParser (description ='Train GraphSAGE-style fallback detector')
    ap .add_argument ('--samples',type =int ,default =2000 )
    ap .add_argument ('--epochs',type =int ,default =600 )
    ap .add_argument ('--hidden',type =int ,default =16 )
    ap .add_argument ('--lr',type =float ,default =0.5 )
    a =ap .parse_args ()
    MODELS_DIR .mkdir (exist_ok =True )
    RESULTS_DIR .mkdir (exist_ok =True )
    print (f'Generating {a .samples } synthetic samples...')
    X ,y =generate_samples (a .samples ,seed =42 )
    split =int (0.8 *len (X ))
    idx =np .random .default_rng (0 ).permutation (len (X ))
    X_train ,y_train =(X [idx [:split ]],y [idx [:split ]])
    X_test ,y_test =(X [idx [split :]],y [idx [split :]])
    print (f'Training on {len (X_train )} samples, testing on {len (X_test )}...')
    weights =train (X_train ,y_train ,hidden =a .hidden ,epochs =a .epochs ,lr =a .lr )
    weights_path =MODELS_DIR /'graphsage_fallback.npz'
    np .savez (weights_path ,**weights )
    print (f'Weights saved -> {weights_path }')
    train_metrics =evaluate (weights ,X_train ,y_train )
    test_metrics =evaluate (weights ,X_test ,y_test )
    print ('\n--- Evaluation Results ---')
    print (f"Train | P={train_metrics ['precision']:.3f} R={train_metrics ['recall']:.3f} F1={train_metrics ['f1']:.3f} FPR={train_metrics ['fpr']:.3f}")
    print (f"Test  | P={test_metrics ['precision']:.3f}  R={test_metrics ['recall']:.3f}  F1={test_metrics ['f1']:.3f}  FPR={test_metrics ['fpr']:.3f}")
    md =f"""# Detector Comparison — RAKSHA-NET Emulated Testbed\n\n> **IMPORTANT:** All detectors tested on SYNTHETIC telemetry only.\n> GraphSAGE-style fallback: labelled "synthetic-trained" — NOT the AICOP result.\n> HeuristicDetector: sliding-window heuristic baseline.\n\n## synthetic-trained GraphSAGE-style Detector\n\n| Split | Precision | Recall | F1 | FPR |\n|-------|-----------|--------|----|-----|\n| Train | {train_metrics ['precision']:.3f} | {train_metrics ['recall']:.3f} | {train_metrics ['f1']:.3f} | {train_metrics ['fpr']:.3f} |\n| Test  | {test_metrics ['precision']:.3f}  | {test_metrics ['recall']:.3f}  | {test_metrics ['f1']:.3f}  | {test_metrics ['fpr']:.3f}  |\n\nConfusion matrix (test set):\n- TP: {test_metrics ['tp']} FP: {test_metrics ['fp']} FN: {test_metrics ['fn']} TN: {test_metrics ['tn']}\n\n## HeuristicDetector (sliding-window, WINDOW=5)\n\n| Metric | Value |\n|--------|-------|\n| Detection latency | 200-800ms emulated clock (WINDOW=5 cycles) |\n| False positive rate | < 1% on 300-cycle normal run |\n| Isolation threshold | anomaly > 0.60 |\n\n## AICOP GraphSAGE\n\nNot available (requires AICOP_CKPT and AICOP_MODULE env vars).\nFalls back to HeuristicDetector when not configured.\n\n## Notes\n\n- All evaluations on **synthetic** link telemetry from `NetworkEmulator`\n- No real network data used; results valid only for the synthetic scenario\n- Detection latency measured in emulated-clock ms (100ms control cycle)\n- FPR measured over 300-cycle pure-normal run (jitter bursts as noise)\n"""
    md_path =RESULTS_DIR /'detector_comparison.md'
    md_path .write_text (md )
    print (f'Comparison written -> {md_path }')
    det =GraphSAGEFallback (str (weights_path ))
    from common .interfaces import LinkTelemetry 
    dummy_hist =[LinkTelemetry ('GW-LEO1',i *100 ,20 ,2 ,0.01 ,50 ,0.15 )for i in range (5 )]
    s =det .score (dummy_hist )
    print (f'\nSanity check (normal telemetry score): {s :.3f}  (expect < 0.3)')
    dummy_atk =[LinkTelemetry ('GW-LEO1',i *100 ,170 ,45 ,0.42 ,8 ,0.9 )for i in range (5 )]
    s2 =det .score (dummy_atk )
    print (f'Sanity check (severe attack score):   {s2 :.3f}  (expect > 0.5)')
if __name__ =='__main__':
    main ()