from __future__ import annotations 
import argparse 
import csv 
import os 
import sys
import platform
import pathlib 
import statistics as st 
import time 

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from controller import crypto_agility as ca 
from controller .security_engine import BACKEND 
RESULTS = pathlib.Path("results")
BANDWIDTHS =(1.0 ,8.0 ,50.0 )

def bench_handshake (suite :ca .Suite ,n :int )->list [float ]:
    ca .handshake (suite ,b'warmup')
    return [ca .handshake (suite ,b'bench')[1 ]for _ in range (n )]

def bench_aead (aead :str ,n :int ,size :int =1024 )->float :
    key ,data =(os .urandom (32 ),os .urandom (size ))
    t0 =time .perf_counter ()
    for _ in range (n ):
        ca .aead_decrypt (aead ,key ,ca .aead_encrypt (aead ,key ,data ,b'a'),b'a')
    dt =time .perf_counter ()-t0 
    return size *n /dt /1000000.0 

def main (n :int ):
    RESULTS .mkdir (exist_ok =True )
    rows =[]
    for s in ca .SUITES .values ():
        t =bench_handshake (s ,n )
        row ={'suite':s .name ,'kex':s .kex ,'aead':s .aead ,'handshake_bytes':s .handshake_bytes ,'hs_mean_ms':round (st .mean (t ),3 ),'hs_sd_ms':round (st .pstdev (t ),3 ),'hs_p95_ms':round (sorted (t )[int (0.95 *len (t ))-1 ],3 ),'real':ca .HAS_MLKEM or not s .uses_mlkem ,'aead_MBps':round (bench_aead (s .aead ,n *5 ),1 )}
        for bw in BANDWIDTHS :
            row [f'tx_ms_{bw :g}mbps']=round (ca .transmit_ms (s ,bw ),3 )
        rows .append (row )
    with (RESULTS /'crypto_benchmark.csv').open ('w',newline ='')as f :
        w =csv .DictWriter (f ,fieldnames =list (rows [0 ]))
        w .writeheader ()
        w .writerows (rows )
    bw_cols =[f'tx_ms_{b :g}mbps'for b in BANDWIDTHS ]
    lines = [
        '# Crypto-Agility Benchmark',
        '',
        '> **Measurement Environment:**',
        f'> - **Platform:** {platform.platform()} ({platform.machine()})',
        f'> - **Python:** {platform.python_version()}',
        f'> - **Crypto Backend:** {BACKEND}',
        f'> - **liboqs Active:** {ca.HAS_MLKEM}',
        f'> - **Repetitions:** {n}',
        '',
        '> **Note:** Handshake / AEAD timings are wall-clock on the machine that ran the script (Python/OpenSSL).',
        '> Transmit times are bandwidth-only estimates (bytes*8/bw), not measured network RTT.',
        '',
        '| Suite | Key exchange | AEAD | Handshake bytes | Handshake mean (ms) | SD | p95 | AEAD MB/s (1 KiB) | ' + ' | '.join((f'tx @{b:g} Mbps (ms)' for b in BANDWIDTHS)) + ' | Real? |',
        '|' + '---|' * (8 + len(BANDWIDTHS) + 1)
    ]
    for r in rows :
        lines .append (f"| {r ['suite']} | {r ['kex']} | {r ['aead']} | {r ['handshake_bytes']} | {r ['hs_mean_ms']} | {r ['hs_sd_ms']} | {r ['hs_p95_ms']} | {r ['aead_MBps']} | "+' | '.join ((str (r [c ])for c in bw_cols ))+f" | {('yes'if r ['real']else 'MOCK ML-KEM')} |")
    lines +=['','## Policy','','- Threat -> hybrid (X25519 + ML-KEM-768).',f'- No threat -> ML-KEM-768 alone.',f'- AEAD: ChaCha20-Poly1305 below {ca .AEAD_AES_MIN_MBPS :g} Mbps, AES-256-GCM at or above.',f'- X25519-only below {ca .CLASSICAL_MAX_MBPS :g} Mbps only if `allow_classical=True` (not PQ-safe).','']
    if not ca .HAS_MLKEM :
        lines .append ('> **MOCK CRYPTO:** liboqs not installed - ML-KEM timings above are NOT real. Re-run under WSL2 after `scripts/install_liboqs.sh`.')
    (RESULTS /'crypto_benchmark.md').write_text ('\n'.join (lines )+'\n',encoding ='utf-8')
    print ('\n'.join (lines ))
if __name__ =='__main__':
    ap =argparse .ArgumentParser ()
    ap .add_argument ('--n',type =int ,default =200 )
    main (ap .parse_args ().n )