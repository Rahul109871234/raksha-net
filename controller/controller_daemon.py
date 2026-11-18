from __future__ import annotations 
import argparse 
import json 
import logging 
import pathlib 
import signal 
import sys 
import threading 
import time 
from controller .controller import Controller 
from controller .security_engine import BACKEND 
logging .basicConfig (level =logging .INFO ,format ='%(asctime)s %(levelname)s %(name)s | %(message)s',datefmt ='%H:%M:%S')
log =logging .getLogger ('raksha.daemon')
RUNS_DIR =pathlib .Path ('runs')
COMMANDS_FILE =RUNS_DIR /'commands.json'
LIVE_STATE_FILE =RUNS_DIR /'live_state.json'
_STOP =threading .Event ()

def _handle_commands (controller :Controller ):
    if not COMMANDS_FILE .exists ():
        return 
    try :
        cmds =json .loads (COMMANDS_FILE .read_text ())
        if not cmds :
            return 
        for cmd in cmds :
            action =cmd .get ('action','')
            if action =='simulate_attack':
                link =cmd .get ('link','GW-LEO1')
                severity =cmd .get ('severity','severe')
                other ={'GW-LEO1':'LEO1-B','GW-LEO2':'LEO2-B'}.get (link ,link )
                controller .net .set_profile (link ,severity )
                controller .net .set_profile (other ,severity )
                log .info ('[CMD] simulate_attack link=%s severity=%s',link ,severity )
            elif action =='restore_link':
                link =cmd .get ('link','GW-LEO1')
                other ={'GW-LEO1':'LEO1-B','GW-LEO2':'LEO2-B'}.get (link ,link )
                controller .net .set_profile (link ,'normal')
                controller .net .set_profile (other ,'normal')
                log .info ('[CMD] restore_link link=%s',link )
            elif action =='node_failure':
                link =cmd .get ('link','GW-LEO1')
                controller .net .set_profile (link ,'failed')
                log .info ('[CMD] node_failure link=%s',link )
            elif action =='reset':
                for lnk in controller .net .links :
                    controller .net .set_profile_instant (lnk ,'normal')
                    controller .state [lnk ].isolated =False 
                controller .sec .isolated .clear ()
                controller .sec .reset_incident ()
                log .info ('[CMD] reset')
        COMMANDS_FILE .write_text ('[]')
    except Exception as e :
        log .warning ('[CMD] Error processing commands: %s',e )

def _run_daemon (controller :Controller ,cycle_ms :int =100 ):
    log .info ('Daemon started | backend=%s | detector=%s',controller .backend ,controller .detector_name )
    while not _STOP .is_set ():
        _handle_commands (controller )
        try :
            controller .step (cycle_ms )
        except Exception as e :
            log .error ('Controller step error: %s',e )
        time .sleep (cycle_ms /1000.0 )
    log .info ('Daemon stopped.')

def main ():
    ap = argparse.ArgumentParser(description='RAKSHA-NET controller daemon')
    ap.add_argument('--backend', default='sim', choices=['sim', 'real', 'open5gs'])
    ap.add_argument('--detector', default='heuristic', choices=['heuristic', 'graphsage', 'aicop'])
    ap.add_argument('--cycle-ms', type=int, default=100)
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()
    RUNS_DIR.mkdir(exist_ok=True)
    COMMANDS_FILE.write_text('[]')
    net_backend = None
    if a.backend == 'open5gs':
        from emulator.open5gs_backend import Open5GSBackend
        log.info('Connecting to live Open5GS 5G Core backend...')
        net_backend = Open5GSBackend()
    elif a.backend == 'real':
        try:
            from emulator.real_backend import RealNetworkBackend
            log.info('Using real backend (Docker + tc netem)')
            log.warning('Real backend not fully wired to daemon — using sim')
        except ImportError:
            log.warning('real_backend not available; falling back to sim')
    controller = Controller(net=net_backend, seed=0, detector_name=a.detector, allow_recovery=True, verbose=a.verbose)

    def _sig (sig ,frame ):
        log .info ('Signal %s received, stopping...',sig )
        _STOP .set ()
    signal .signal (signal .SIGINT ,_sig )
    signal .signal (signal .SIGTERM ,_sig )
    _run_daemon (controller ,a .cycle_ms )
if __name__ =='__main__':
    main ()