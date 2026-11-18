from __future__ import annotations 
import json 
import pathlib 
import subprocess 
import sys 
import time 
import threading 
from datetime import datetime 
from typing import Optional 
import pandas as pd 
import plotly .graph_objects as go 
import streamlit as st 
RUNS_DIR =pathlib .Path ('runs')
RESULTS_DIR =pathlib .Path ('results')
LIVE_STATE =RUNS_DIR /'live_state.json'
EVENTS_FILE =RUNS_DIR /'events.jsonl'
COMMANDS_FILE =RUNS_DIR /'commands.json'
POLL_MS =500 
RUNS_DIR .mkdir (exist_ok =True )
RESULTS_DIR .mkdir (exist_ok =True )
st .set_page_config (page_title ='RAKSHA-NET | Emulated Testbed',page_icon ='🛡️',layout ='wide',initial_sidebar_state ='expanded')
st .markdown ('\n<style>\n@import url(\'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap\');\n\nhtml, body, [class*="css"] {\n    font-family: \'Inter\', sans-serif;\n    background-color: #0a0e1a;\n    color: #e2e8f0;\n}\n\n.main .block-container {\n    padding-top: 1rem;\n    max-width: 100%;\n}\n\n/* Header */\n.raksha-header {\n    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);\n    border: 1px solid #1e40af;\n    border-radius: 12px;\n    padding: 1.2rem 2rem;\n    margin-bottom: 1rem;\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n}\n\n.raksha-title {\n    font-size: 2rem;\n    font-weight: 800;\n    background: linear-gradient(90deg, #3b82f6, #06b6d4, #8b5cf6);\n    -webkit-background-clip: text;\n    -webkit-text-fill-color: transparent;\n    margin: 0;\n}\n\n.raksha-subtitle {\n    font-size: 0.75rem;\n    color: #64748b;\n    margin-top: 0.2rem;\n    text-transform: uppercase;\n    letter-spacing: 0.1em;\n}\n\n/* Badges */\n.badge {\n    display: inline-block;\n    padding: 0.25rem 0.7rem;\n    border-radius: 20px;\n    font-size: 0.7rem;\n    font-weight: 700;\n    letter-spacing: 0.05em;\n    text-transform: uppercase;\n    margin: 0.15rem;\n}\n\n.badge-blue   { background: #1d4ed8; color: #bfdbfe; }\n.badge-green  { background: #14532d; color: #86efac; }\n.badge-yellow { background: #713f12; color: #fde68a; }\n.badge-red    { background: #7f1d1d; color: #fca5a5; animation: pulse 1s infinite; }\n.badge-purple { background: #4c1d95; color: #c4b5fd; }\n.badge-gray   { background: #374151; color: #9ca3af; }\n\n@keyframes pulse {\n    0%, 100% { opacity: 1; }\n    50% { opacity: 0.6; }\n}\n\n/* Metric cards */\n.metric-card {\n    background: linear-gradient(135deg, #1e293b, #0f172a);\n    border: 1px solid #334155;\n    border-radius: 10px;\n    padding: 1rem;\n    text-align: center;\n    transition: border-color 0.3s;\n}\n.metric-card:hover { border-color: #3b82f6; }\n.metric-value {\n    font-size: 2rem;\n    font-weight: 800;\n    color: #38bdf8;\n}\n.metric-label {\n    font-size: 0.7rem;\n    color: #64748b;\n    text-transform: uppercase;\n    letter-spacing: 0.08em;\n}\n\n/* Security state */\n.sec-state {\n    background: linear-gradient(135deg, #1e293b, #0f172a);\n    border: 1px solid #334155;\n    border-radius: 10px;\n    padding: 1rem;\n    margin: 0.5rem 0;\n}\n\n.sec-normal   { border-left: 4px solid #22c55e; }\n.sec-threat   { border-left: 4px solid #f59e0b; animation: pulse 0.8s infinite; }\n.sec-rekey    { border-left: 4px solid #3b82f6; animation: pulse 0.6s infinite; }\n.sec-pqc      { border-left: 4px solid #8b5cf6; }\n\n/* Event log */\n.event-item {\n    font-family: \'JetBrains Mono\', monospace;\n    font-size: 0.72rem;\n    padding: 0.3rem 0.5rem;\n    border-left: 3px solid #334155;\n    margin: 0.1rem 0;\n    color: #94a3b8;\n}\n.event-route  { border-left-color: #3b82f6; color: #93c5fd; }\n.event-threat { border-left-color: #ef4444; color: #fca5a5; }\n.event-pqc    { border-left-color: #8b5cf6; color: #c4b5fd; }\n.event-normal { border-left-color: #22c55e; color: #86efac; }\n\n/* Demo scene captions */\n.scene-caption {\n    background: linear-gradient(90deg, rgba(59,130,246,0.15), rgba(139,92,246,0.15));\n    border: 1px solid rgba(139,92,246,0.4);\n    border-radius: 8px;\n    padding: 0.8rem 1.5rem;\n    text-align: center;\n    font-size: 1.1rem;\n    font-weight: 600;\n    color: #c4b5fd;\n    margin: 0.5rem 0;\n    animation: fadeIn 0.5s ease;\n}\n\n@keyframes fadeIn {\n    from { opacity: 0; transform: translateY(-5px); }\n    to   { opacity: 1; transform: translateY(0); }\n}\n\n/* Stframe tweaks */\n[data-testid="stSidebar"] {\n    background: #0d1117;\n    border-right: 1px solid #1e293b;\n}\n\n/* Section headers */\n.section-header {\n    font-size: 0.8rem;\n    font-weight: 700;\n    color: #3b82f6;\n    text-transform: uppercase;\n    letter-spacing: 0.1em;\n    border-bottom: 1px solid #1e293b;\n    padding-bottom: 0.3rem;\n    margin-bottom: 0.8rem;\n}\n\ndiv[data-testid="stDataFrame"] {\n    background: #1e293b;\n}\n</style>\n',unsafe_allow_html =True )
if 'events_shown'not in st .session_state :
    st .session_state .events_shown =0 
if 'demo_mode'not in st .session_state :
    st .session_state .demo_mode =False 
if 'demo_scene'not in st .session_state :
    st .session_state .demo_scene =0 
if 'demo_start_t'not in st .session_state :
    st .session_state .demo_start_t =None 
if 'pdr_history'not in st .session_state :
    st .session_state .pdr_history =[]
if 'daemon_proc'not in st .session_state :
    st .session_state .daemon_proc =None 
DEMO_SCENES =[('Scene 1: Normal Operations','All links nominal. PDR > 98%. Trust high.',6 ),('Scene 2: LEO-1 Link Attack','Simulating jamming on LEO-1. Latency spiking...',5 ),('Scene 3: AI Routing Decision','Anomaly detected. Trust dropping. Switching to LEO-2!',5 ),('Scene 4: Security Adaptation','ML-KEM re-key in progress. LEO-1 isolated.',5 ),('Scene 5: Communication Restored','LEO-2 active. PDR recovering. System resilient.',6 )]

def load_live_state ()->Optional [dict ]:
    try :
        if LIVE_STATE .exists ():
            return json .loads (LIVE_STATE .read_text ())
    except Exception :
        pass 
    return None 

def load_events (max_lines :int =100 )->list [dict ]:
    events =[]
    try :
        if EVENTS_FILE .exists ():
            lines =EVENTS_FILE .read_text ().strip ().split ('\n')
            for line in lines [-max_lines :]:
                if line .strip ():
                    events .append (json .loads (line ))
    except Exception :
        pass 
    return events 

def send_command (action :str ,**kwargs ):
    cmds =[]
    try :
        if COMMANDS_FILE .exists ():
            cmds =json .loads (COMMANDS_FILE .read_text ())
    except Exception :
        pass 
    cmds .append ({'action':action ,**kwargs })
    COMMANDS_FILE .write_text (json .dumps (cmds ))
NODE_POS ={'A':(0.0 ,0.5 ),'GW':(0.25 ,0.5 ),'LEO1':(0.6 ,0.8 ),'LEO2':(0.6 ,0.2 ),'B':(0.95 ,0.5 )}
NODE_LABELS ={'A':'Node A\n(Soldier)','GW':'Gateway\n(AI+Security)','LEO1':'LEO-1\n(Primary)','LEO2':'LEO-2\n(Backup)','B':'Node B\n(UAV/Air)'}
LINK_NODES ={'A-GW':('A','GW'),'GW-LEO1':('GW','LEO1'),'GW-LEO2':('GW','LEO2'),'LEO1-B':('LEO1','B'),'LEO2-B':('LEO2','B')}
R1_LINKS ={'A-GW','GW-LEO1','LEO1-B'}
R2_LINKS ={'A-GW','GW-LEO2','LEO2-B'}

def build_topology (state :Optional [dict ])->go .Figure :
    active =state .get ('active_route','R1')if state else 'R1'
    active_links =R1_LINKS if active =='R1'else R2_LINKS 
    isolated =set (state .get ('isolated',[]))if state else set ()
    link_states =state .get ('links',{})if state else {}
    fig =go .Figure ()
    for link_id ,(u ,v )in LINK_NODES .items ():
        x0 ,y0 =NODE_POS [u ]
        x1 ,y1 =NODE_POS [v ]
        ldata =link_states .get (link_id ,{})
        is_iso =link_id in isolated 
        is_active =link_id in active_links 
        anomaly =ldata .get ('anomaly',0 )
        if is_iso :
            color ,width ,dash =('#ef4444',2 ,'dot')
        elif is_active :
            if anomaly >0.5 :
                color ,width ,dash =('#f59e0b',3 ,'dash')
            else :
                color ,width ,dash =('#22c55e',4 ,'solid')
        else :
            color ,width ,dash =('#334155',1.5 ,'dash')
        fig .add_trace (go .Scatter (x =[x0 ,x1 ,None ],y =[y0 ,y1 ,None ],mode ='lines',line =dict (color =color ,width =width ,dash =dash ),hoverinfo ='skip',showlegend =False ))
        if is_iso :
            mx ,my =((x0 +x1 )/2 ,(y0 +y1 )/2 )
            fig .add_annotation (x =mx ,y =my ,text ='✗',font =dict (size =20 ,color ='#ef4444'),showarrow =False )
        lat =ldata .get ('latency_ms','-')
        loss_pct =round (ldata .get ('loss',0 )*100 ,1 )
        mx ,my =((x0 +x1 )/2 +0.01 ,(y0 +y1 )/2 +0.04 )
        fig .add_annotation (x =mx ,y =my ,text =f'<b>{link_id }</b><br>{lat }ms | {loss_pct }% loss',font =dict (size =9 ,color ='#94a3b8'),showarrow =False ,bgcolor ='rgba(15,23,42,0.8)')
    for node ,(x ,y )in NODE_POS .items ():
        is_gw =node =='GW'
        node_color ='#3b82f6'if is_gw else '#1e40af'
        border_color ='#60a5fa'
        fig .add_trace (go .Scatter (x =[x ],y =[y ],mode ='markers+text',marker =dict (size =40 if is_gw else 28 ,color =node_color ,line =dict (color =border_color ,width =2 ),symbol ='square'if is_gw else 'circle'),text =[NODE_LABELS [node ]],textposition ='bottom center',textfont =dict (size =10 ,color ='#e2e8f0'),hoverinfo ='text',hovertext =NODE_LABELS [node ],showlegend =False ))
    if state :
        t =state .get ('t_ms',0 )
        anim_t =t //100 %10 /10.0 
        route_nodes =['A','GW','LEO1','B']if active =='R1'else ['A','GW','LEO2','B']
        n_seg =len (route_nodes )-1 
        seg_idx =int (anim_t *n_seg )
        seg_alpha =anim_t *n_seg -seg_idx 
        seg_idx =min (seg_idx ,n_seg -1 )
        u_n ,v_n =(route_nodes [seg_idx ],route_nodes [seg_idx +1 ])
        px =NODE_POS [u_n ][0 ]+seg_alpha *(NODE_POS [v_n ][0 ]-NODE_POS [u_n ][0 ])
        py =NODE_POS [u_n ][1 ]+seg_alpha *(NODE_POS [v_n ][1 ]-NODE_POS [u_n ][1 ])
        fig .add_trace (go .Scatter (x =[px ],y =[py ],mode ='markers',marker =dict (size =12 ,color ='#06b6d4',symbol ='circle',line =dict (color ='white',width =1 )),hoverinfo ='skip',showlegend =False ))
    fig .update_layout (paper_bgcolor ='#0a0e1a',plot_bgcolor ='#0d1117',margin =dict (l =10 ,r =10 ,t =10 ,b =10 ),xaxis =dict (range =[-0.05 ,1.05 ],showgrid =False ,zeroline =False ,showticklabels =False ),yaxis =dict (range =[-0.05 ,1.1 ],showgrid =False ,zeroline =False ,showticklabels =False ),height =320 )
    return fig 

def backend_badge (backend :str )->str :
    if backend =='MOCK':
        return '<span class="badge badge-red">MOCK CRYPTO</span>'
    return f'<span class="badge badge-green">{backend }</span>'

def detector_badge (det :str )->str :
    if 'AICOP'in det .upper ():
        return f'<span class="badge badge-purple">{det }</span>'
    if 'synthetic'in det .lower ()or 'graphsage'in det .lower ():
        return f'<span class="badge badge-blue">{det }</span>'
    return f'<span class="badge badge-yellow">{det }</span>'

def sec_state_badge (state :str )->str :
    colors ={'NORMAL':'badge-green','THREAT_DETECTED':'badge-red','REKEY_REQUIRED':'badge-blue','PQC_SESSION_ESTABLISHED':'badge-purple'}
    cls =colors .get (state ,'badge-gray')
    return f'<span class="badge {cls }">{state }</span>'

def render_sidebar ():
    with st .sidebar :
        st .markdown ('## 🎮 Controls')
        st .markdown ('---')
        st .markdown ('### Simulate Link Attack')
        attack_link =st .selectbox ('Target link',['GW-LEO1','GW-LEO2'],key ='attack_link')
        severity =st .select_slider ('Severity',options =['low','medium','severe','failed'],value ='severe',key ='severity')
        col1 ,col2 =st .columns (2 )
        with col1 :
            if st .button ('🔴 ATTACK',use_container_width =True ,key ='btn_attack'):
                send_command ('simulate_attack',link =attack_link ,severity =severity )
                st .success (f'Attack sent: {attack_link } -> {severity }')
        with col2 :
            if st .button ('🟢 RESTORE',use_container_width =True ,key ='btn_restore'):
                send_command ('restore_link',link =attack_link )
                st .success ('Restore sent')
        st .markdown ('---')
        if st .button ('❌ NODE FAILURE',use_container_width =True ,key ='btn_fail'):
            send_command ('node_failure',link =attack_link )
            st .warning ('Node failure sent')
        if st .button ('🔄 RESET ALL',use_container_width =True ,key ='btn_reset'):
            send_command ('reset')
            st .info ('Reset sent')
        st .markdown ('---')
        st .markdown ('### Experiment')
        if st .button ('📊 RUN 20-TRIAL EXPERIMENT',use_container_width =True ,key ='btn_exp'):
            st .info ('Starting experiment... check results/ folder.')
            threading .Thread (target =lambda :subprocess .run ([sys .executable ,'-m','scripts.run_scenario','--trials','20','--csv','results/experiment.csv','--compare-static'],cwd =pathlib .Path .cwd ()),daemon =True ).start ()
        if st .button ('🧪 RUN LEACH BENCHMARK',use_container_width =True ,key ='btn_leach'):
            st .info ('Running LEACH vs RAKSHA-NET benchmark... check runs/leach_comparison.json')
            threading .Thread (target =lambda :subprocess .run ([sys .executable ,'-m','scripts.run_leach_comparison'],cwd =pathlib .Path .cwd ()),daemon =True ).start ()
        st .markdown ('---')
        st .markdown ('### Demo Mode')
        if not st .session_state .demo_mode :
            if st .button ('▶ START DEMO',use_container_width =True ,key ='btn_demo'):
                st .session_state .demo_mode =True 
                st .session_state .demo_scene =0 
                st .session_state .demo_start_t =time .time ()
                send_command ('reset')
        else :
            st .success (f'Demo scene {st .session_state .demo_scene +1 }/5')
            if st .button ('⏹ STOP DEMO',use_container_width =True ,key ='btn_demo_stop'):
                st .session_state .demo_mode =False 
                st .session_state .demo_scene =0 
        st .markdown ('---')
        st .markdown ('### System Info')
        st .markdown ('\n<small>\n**RAKSHA-NET Emulated Testbed**<br>\nPDPM IIITDM Jabalpur<br>\nSovereign Technology for India<br>\nAll results: simulated/emulated.<br>\nNo real satellites, RF jamming,<br>\nor QKD hardware used.\n</small>\n',unsafe_allow_html =True )

def handle_demo_mode ():
    if not st .session_state .demo_mode :
        return (None ,None )
    scene_idx =st .session_state .demo_scene 
    elapsed =time .time ()-(st .session_state .demo_start_t or time .time ())
    scene_elapsed =elapsed -sum ((s [2 ]for s in DEMO_SCENES [:scene_idx ]))
    name ,desc ,duration =DEMO_SCENES [scene_idx ]
    if scene_idx ==0 and scene_elapsed <1 :
        send_command ('reset')
    elif scene_idx ==1 and scene_elapsed <1 :
        send_command ('simulate_attack',link ='GW-LEO1',severity ='severe')
    elif scene_idx ==4 and scene_elapsed <1 :
        send_command ('restore_link',link ='GW-LEO1')
    if scene_elapsed >=duration :
        st .session_state .demo_scene =(scene_idx +1 )%len (DEMO_SCENES )
        if st .session_state .demo_scene ==0 :
            st .session_state .demo_mode =False 
    return (name ,desc )

def main ():
    render_sidebar ()
    state =load_live_state ()
    events =load_events (50 )
    backend =state .get ('backend','MOCK')if state else 'MOCK'
    detector =state .get ('detector','HeuristicDetector')if state else 'Unknown'
    sec_st =state .get ('sec_state','NORMAL')if state else 'NORMAL'
    suite =state .get ('suite','PQC_AES')if state else 'PQC_AES'
    kex =state .get ('kex','ML-KEM-768')if state else 'ML-KEM-768'
    aead =state .get ('aead','AES-256-GCM')if state else 'AES-256-GCM'
    t_ms =state .get ('t_ms',0 )if state else 0 
    active =state .get ('active_route','R1')if state else 'R1'
    pdr =state .get ('pdr',0 )if state else 0 
    st .session_state .pdr_history .append (pdr )
    if len (st .session_state .pdr_history )>60 :
        st .session_state .pdr_history .pop (0 )
    scene_name ,scene_desc =handle_demo_mode ()
    st .markdown (f'\n<div class="raksha-header">\n  <div>\n    <div class="raksha-title">🛡️ RAKSHA-NET</div>\n    <div class="raksha-subtitle">Emulated Testbed &nbsp;|&nbsp; Space-Air-Ground Integrated Network</div>\n  </div>\n  <div>\n    <span class="badge badge-blue">SIM</span>\n    {backend_badge (backend )}\n    {detector_badge (detector )}\n    {sec_state_badge (sec_st )}\n    <span class="badge badge-blue">{suite }</span>\n    <span class="badge badge-gray">t={t_ms }ms</span>\n    <span class="badge badge-gray">QKD: SIMULATED</span>\n  </div>\n</div>\n',unsafe_allow_html =True )
    if scene_name :
        st .markdown (f'\n<div class="scene-caption">\n  🎬 <b>{scene_name }</b> &nbsp;—&nbsp; {scene_desc }\n</div>\n',unsafe_allow_html =True )
    tab_live ,tab_security ,tab_results =st .tabs (['📡 Live Network','🔐 Security','📊 Results'])
    with tab_live :
        st .markdown ('<div class="section-header">Network Topology</div>',unsafe_allow_html =True )
        topology_placeholder =st .empty ()
        topology_placeholder .plotly_chart (build_topology (state ),use_container_width =True )
        st .markdown ('<div class="section-header">Live Metrics — Active Route</div>',unsafe_allow_html =True )
        link_data =state .get ('links',{})if state else {}
        active_links =['A-GW','GW-LEO1','LEO1-B']if active =='R1'else ['A-GW','GW-LEO2','LEO2-B']
        avg_lat =0.0 
        avg_loss =0.0 
        min_trust =1.0 
        max_anom =0.0 
        if link_data :
            lats =[link_data .get (l ,{}).get ('latency_ms',0 )for l in active_links if l in link_data ]
            losses =[link_data .get (l ,{}).get ('loss',0 )for l in active_links if l in link_data ]
            trusts =[link_data .get (l ,{}).get ('trust',1 )for l in active_links if l in link_data ]
            anoms =[link_data .get (l ,{}).get ('anomaly',0 )for l in active_links if l in link_data ]
            avg_lat =sum (lats )/len (lats )if lats else 0 
            avg_loss =sum (losses )/len (losses )if losses else 0 
            min_trust =min (trusts )if trusts else 1 
            max_anom =max (anoms )if anoms else 0 
        c1 ,c2 ,c3 ,c4 ,c5 ,c6 =st .columns (6 )
        metrics =[(c1 ,f'{pdr *100 :.1f}%','PDR','#22c55e'if pdr >0.9 else '#ef4444'),(c2 ,f'{avg_lat :.0f}ms','Latency','#38bdf8'),(c3 ,f'{avg_loss *100 :.1f}%','Packet Loss','#f59e0b'if avg_loss >0.1 else '#64748b'),(c4 ,f'{min_trust :.2f}','Min Trust','#22c55e'if min_trust >0.7 else '#ef4444'),(c5 ,f'{max_anom :.2f}','Max Anomaly','#ef4444'if max_anom >0.5 else '#64748b'),(c6 ,active ,'Active Route','#8b5cf6')]
        for col ,val ,label ,color in metrics :
            with col :
                st .markdown (f'\n<div class="metric-card">\n  <div class="metric-value" style="color:{color }">{val }</div>\n  <div class="metric-label">{label }</div>\n</div>\n',unsafe_allow_html =True )
        if st .session_state .pdr_history :
            st .markdown ('<div class="section-header">PDR History (last 60 cycles)</div>',unsafe_allow_html =True )
            pdr_fig =go .Figure ()
            pdr_fig .add_trace (go .Scatter (y =st .session_state .pdr_history ,mode ='lines',fill ='tozeroy',line =dict (color ='#22c55e'if pdr >0.9 else '#ef4444',width =2 ),fillcolor ='rgba(34,197,94,0.1)'))
            pdr_fig .update_layout (paper_bgcolor ='#0a0e1a',plot_bgcolor ='#0d1117',margin =dict (l =0 ,r =0 ,t =0 ,b =0 ),height =80 ,xaxis =dict (showgrid =False ,showticklabels =False ),yaxis =dict (showgrid =False ,range =[0 ,1.05 ],showticklabels =False ))
            st .plotly_chart (pdr_fig ,use_container_width =True )
        st .markdown ('<div class="section-header">Per-Link Telemetry</div>',unsafe_allow_html =True )
        if link_data :
            rows =[]
            for lid ,d in link_data .items ():
                rows .append ({'Link':lid ,'Latency (ms)':f"{d .get ('latency_ms',0 ):.1f}",'Loss (%)':f"{d .get ('loss',0 )*100 :.1f}",'Jitter (ms)':f"{d .get ('jitter_ms',0 ):.1f}",'Throughput':f"{d .get ('throughput_mbps',0 ):.1f} Mbps",'Queue':f"{d .get ('queue_depth',0 ):.2f}",'Anomaly':f"{d .get ('anomaly',0 ):.3f}",'Trust':f"{d .get ('trust',1 ):.3f}",'Isolated':'YES ⛔'if d .get ('isolated')else 'no'})
            df =pd .DataFrame (rows ).set_index ('Link')
            st .dataframe (df ,use_container_width =True )
        st .markdown ('<div class="section-header">AI Routing Decision</div>',unsafe_allow_html =True )
        if state :
            scores =state .get ('scores',{})
            reason =state .get ('reason','keep')
            cols =st .columns (len (scores )+1 )
            for i ,(rname ,rscore )in enumerate (scores .items ()):
                with cols [i ]:
                    color ='#22c55e'if rname ==active else '#475569'
                    label ='ACTIVE ✓'if rname ==active else 'STANDBY'
                    st .markdown (f'\n<div class="metric-card" style="border-color:{color }">\n  <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase">{label }</div>\n  <div class="metric-value" style="color:{color };font-size:1.5rem">{rname }</div>\n  <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0">Score: {rscore :.3f}</div>\n</div>\n',unsafe_allow_html =True )
            with cols [-1 ]:
                st .markdown (f"""\n<div class="metric-card">\n  <div class="metric-label">Decision Reason</div>\n  <div style="font-size:0.85rem;color:#e2e8f0;margin-top:0.5rem;font-family:'JetBrains Mono',monospace">\n    {reason [:120 ]}\n  </div>\n</div>\n""",unsafe_allow_html =True )
        if state and state .get ('energy'):
            st .markdown ('<div class="section-header">Satellite Energy & Tactical LEACH Upgrades</div>',unsafe_allow_html =True )
            ec1 ,ec2 ,ec3 ,ec4 =st .columns (4 )
            with ec1 :
                st .markdown (f'<div class="metric-card"><div class="metric-value" style="color:#38bdf8">{state .get ("session_master","GW")}</div><div class="metric-label">Crypto Session Master</div></div>',unsafe_allow_html =True )
            with ec2 :
                l1_e =state ['energy'].get ('LEO1',1.0 )*100 
                st .markdown (f'<div class="metric-card"><div class="metric-value" style="color:#22c55e">{l1_e :.0f}%</div><div class="metric-label">LEO1 Battery</div></div>',unsafe_allow_html =True )
            with ec3 :
                l2_e =state ['energy'].get ('LEO2',1.0 )*100 
                st .markdown (f'<div class="metric-card"><div class="metric-value" style="color:#22c55e">{l2_e :.0f}%</div><div class="metric-label">LEO2 Battery</div></div>',unsafe_allow_html =True )
            with ec4 :
                saved =state .get ('aggregation_saved_pct',0.0 )
                st .markdown (f'<div class="metric-card"><div class="metric-value" style="color:#a855f7">{saved :.0f}%</div><div class="metric-label">Telemetry BW Saved</div></div>',unsafe_allow_html =True )
        st .markdown ('<div class="section-header">Event Log</div>',unsafe_allow_html =True )
        if events :
            html ='<div style="height:220px;overflow-y:auto;background:#0d1117;border-radius:8px;padding:0.5rem">'
            for ev in reversed (events [-30 :]):
                state_val =ev .get ('state','')
                css ='event-item'
                if 'ROUTE'in ev .get ('detail','').upper ():
                    css ='event-item event-route'
                elif 'THREAT'in state_val :
                    css ='event-item event-threat'
                elif 'PQC'in state_val :
                    css ='event-item event-pqc'
                elif 'NORMAL'in state_val :
                    css ='event-item event-normal'
                dt =datetime .now ().strftime ('%H:%M:%S')
                html +=f'''<div class="{css }">[t={ev .get ('t_ms','?')}ms] {state_val }: {ev .get ('detail','')}</div>'''
            html +='</div>'
            st .markdown (html ,unsafe_allow_html =True )
        else :
            st .info ('No events yet. Start the controller daemon to see live events.')
    with tab_security :
        st .markdown ('<div class="section-header">Security State Machine</div>',unsafe_allow_html =True )
        states =['NORMAL','THREAT_DETECTED','REKEY_REQUIRED','PQC_SESSION_ESTABLISHED']
        state_labels ={'NORMAL':('✅','NORMAL','System nominal. Trust high.'),'THREAT_DETECTED':('⚠️','THREAT DETECTED','Anomaly detected on link.'),'REKEY_REQUIRED':('🔄','RE-KEY REQUIRED','ML-KEM handshake in progress...'),'PQC_SESSION_ESTABLISHED':('🔐','PQC SESSION','New quantum-safe session established.')}
        cols =st .columns (len (states ))
        for i ,s in enumerate (states ):
            ico ,label ,desc =state_labels [s ]
            is_active =s ==sec_st 
            border_color ='#3b82f6'if is_active else '#1e293b'
            bg_color ='rgba(59,130,246,0.1)'if is_active else 'transparent'
            with cols [i ]:
                st .markdown (f'\n<div style="border:2px solid {border_color };border-radius:10px;padding:1rem;\n            text-align:center;background:{bg_color };transition:all 0.3s">\n  <div style="font-size:2rem">{ico }</div>\n  <div style="font-size:0.75rem;font-weight:700;color:#e2e8f0;margin:0.3rem 0">{label }</div>\n  <div style="font-size:0.65rem;color:#64748b">{desc }</div>\n</div>\n',unsafe_allow_html =True )
        st .markdown ('---')
        if state :
            sid =state .get ('session_id','N/A')
            isolated =state .get ('isolated',[])
            col1 ,col2 ,col3 ,col4 =st .columns (4 )
            with col1 :
                st .metric ('Session ID',sid )
            with col2 :
                st .metric ('Isolated Links',len (isolated ))
            with col3 :
                st .metric ('Crypto Backend',backend )
            with col4 :
                st .metric ('Active Suite',suite )
            st .caption (f'Key exchange: {kex } | AEAD: {aead } (chosen from link bandwidth + threat state)')
            if isolated :
                st .error (f"**Isolated links:** {', '.join (isolated )}")
        st .markdown ('<div class="section-header">Encrypted Message Feed</div>',unsafe_allow_html =True )
        st .markdown ('\n<div style="background:#0d1117;border:1px solid #334155;border-radius:8px;\n            padding:1rem;font-family:\'JetBrains Mono\',monospace;font-size:0.75rem">\n  <div style="color:#64748b">// Demo: Node A sends encrypted payload to Node B</div>\n  <div style="color:#f59e0b;margin-top:0.5rem">🔒 Ciphertext (hex): <span id="ct">a1b2c3d4...</span></div>\n  <div style="color:#22c55e;margin-top:0.3rem">✅ Decrypted at B: <b>RAKSHA-NET status OK | t={t_ms}ms</b></div>\n  <div style="color:#64748b;margin-top:0.3rem">Backend: {backend} | Suite: {suite} | KEX: {kex} | AEAD: {aead} | KDF: HKDF-SHA256</div>\n  <div style="color:#8b5cf6;margin-top:0.3rem">QKD: SIMULATED / not available (future upgrade path)</div>\n</div>\n'.format (backend =backend ,t_ms =t_ms ,suite =suite ,kex =kex ,aead =aead ),unsafe_allow_html =True )
        st .markdown ('<div class="section-header">Security Events</div>',unsafe_allow_html =True )
        if events :
            sec_events =[e for e in events if e .get ('state')in ['THREAT_DETECTED','REKEY_REQUIRED','PQC_SESSION_ESTABLISHED']]
            if sec_events :
                df_sec =pd .DataFrame ([{'t (ms)':e .get ('t_ms'),'State':e .get ('state'),'Detail':e .get ('detail'),'Backend':e .get ('backend'),'Suite':e .get ('suite',''),'BW (Mbps)':e .get ('bw_mbps',0 ),'Rekey ms (wall)':e .get ('rekey_ms',0 )}for e in sec_events [-20 :]])
                st .dataframe (df_sec ,use_container_width =True )
    with tab_results :
        st .markdown ('<div class="section-header">Experiment Results</div>',unsafe_allow_html =True )
        csv_files =list (RESULTS_DIR .glob ('*.csv'))
        if not csv_files :
            st .info ('No CSV results yet. Run the experiment from the sidebar or use `make experiment`.')
        else :
            csv_path =st .selectbox ('Select results file',csv_files ,format_func =lambda p :p .name )
            try :
                df =pd .read_csv (csv_path )
                st .dataframe (df ,use_container_width =True )
                if 'route_recovery_ms'in df .columns :
                    rr =df ['route_recovery_ms'].dropna ()
                    if not rr .empty :
                        fig_hist =go .Figure ()
                        fig_hist .add_trace (go .Histogram (x =rr ,nbinsx =15 ,marker_color ='#3b82f6',name ='Route Recovery Time'))
                        fig_hist .update_layout (title ='Route Recovery Time Distribution (emulated-clock ms)',paper_bgcolor ='#0a0e1a',plot_bgcolor ='#0d1117',font =dict (color ='#e2e8f0'),height =300 )
                        st .plotly_chart (fig_hist ,use_container_width =True )
                if 'static_pdr_during'in df .columns :
                    ai_pd =df ['pdr_during'].mean ()
                    sta_pd =df ['static_pdr_during'].mean ()
                    ai_pa =df ['pdr_after'].mean ()
                    sta_pa =df ['static_pdr_after'].mean ()
                    fig_cmp =go .Figure (data =[go .Bar (name ='AI Routing',x =['PDR During','PDR After'],y =[ai_pd ,ai_pa ],marker_color ='#22c55e'),go .Bar (name ='Static Routing',x =['PDR During','PDR After'],y =[sta_pd ,sta_pa ],marker_color ='#ef4444')])
                    fig_cmp .update_layout (title ='AI vs Static Routing — PDR Comparison',barmode ='group',paper_bgcolor ='#0a0e1a',plot_bgcolor ='#0d1117',font =dict (color ='#e2e8f0'),height =300 )
                    st .plotly_chart (fig_cmp ,use_container_width =True )
                st .markdown ('### Summary Statistics')
                numeric_cols =df .select_dtypes (include ='number').columns 
                st .dataframe (df [numeric_cols ].describe ().round (3 ),use_container_width =True )
            except Exception as e :
                st .error (f'Error loading {csv_path .name }: {e }')
    time .sleep (POLL_MS /1000 )
    st .rerun ()
if __name__ =='__main__':
    main ()