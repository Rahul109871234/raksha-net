# RAKSHA-NET — Experiment Summary

> **Emulated Testbed** — PDPM IIITDM Jabalpur — Sovereign Technology for India  
> All results from statistical simulation (100ms emulated control cycle).  
> Not real satellites, RF jamming, QKD, or defense deployment.

**Trials:** 10 | **Backend:** liboqs-ML-KEM-768 | **Detector:** synthetic-trained GraphSAGE-style detector  
**Source:** `benchmark_graphsage.csv`

---

## Table: Before / During / After Degradation

| Metric | Before degradation | During (no AI / static) | After AI reroute |
|--------|-------------------|------------------------|-----------------|
| PDR | 0.968 | 0.323 | 0.968 |
| Latency | (emulated normal) | (emulated degraded) | (emulated LEO-2) |
| Packet loss | ~3.2% | ~67.7% (static) | ~3.2% |
| Trust | ~0.95 | drops < 0.5 | recovers > 0.85 |
| Anomaly score | < 0.3 | > 0.6 | < 0.3 (LEO-2) |
| Throughput | ~50 Mbps | ~8 Mbps | ~50 Mbps (LEO-2) |
| Route recovery time | — | — | mean=180ms SD=40ms min=100 max=200 |
| Rekey time (wall-clock) | — | — | 0.47 ms (wall-clock, SD=0.14) |

> **Note:** Latency and throughput values above are from PROFILES table (emulated).
> Packet loss rows computed from PDR: loss% = (1-PDR)*100.

---

## AI vs Static Routing — PDR Comparison

| Routing | PDR During Attack | PDR After Attack |
|---------|------------------|-----------------|
| **AI routing (RAKSHA)** | 0.968 | 0.968 |
| Static (no AI) | 0.323 | 0.869 |
| **AI benefit** | **+0.645** | **+0.099** |

---

## Route Recovery Statistics (emulated-clock ms)

| Stat | Value |
|------|-------|
| Trials | 10 |
| Switched | 10/10 (100%) |
| Mean | 180 ms |
| SD | 40 ms |
| Min | 100 ms |
| Max | 200 ms |
