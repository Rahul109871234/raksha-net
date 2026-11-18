# RAKSHA-NET — Experiment Summary

> **Emulated Testbed** — PDPM IIITDM Jabalpur — Sovereign Technology for India  
> All results from statistical simulation (100ms emulated control cycle).  
> Not real satellites, RF jamming, QKD, or defense deployment.

**Trials:** 10 | **Backend:** liboqs-ML-KEM-768 | **Detector:** HeuristicDetector  
**Source:** `benchmark_heuristic.csv`

---

## Table: Multi-Phase Attack Dynamics (Before, Initial Dip, and Rerouted)

| Operational Phase | RAKSHA-NET (AI Routing) | Static Routing (No AI) | Impact / Note |
|:---|:---:|:---:|:---|
| **Normal (Pre-Attack)** | 0.968 (3.2% loss) | 0.968 (3.2% loss) | Baseline nominal traffic |
| **Initial Reaction Dip (Onset $\rightarrow$ Switch, ~190ms)** | **0.835** (16.5% loss) | **0.338** (66.2% loss) | Transient impact before failover |
| **Rerouted Steady-State (LEO-2 Backup)** | **0.968** (3.2% loss) | **0.323** (67.7% loss) | AI rescues link; Static stays jammed |
| **Post-Attack Recovery (Normal restored)** | **0.968** | **0.869** | Network profile restored to normal |
| **Route Recovery Latency** | **mean=190ms** (SD=30ms, min=100, max=200) | No failover | Switched in 1-2 control cycles (100%) |
| **NIST ML-KEM-768 Rekey Latency** | **0.48 ms (wall-clock, SD=0.17)** | No rekey | Native C `liboqs` execution |

> **Key takeaway:** The initial EW attack causes a measurable transient dip in packet delivery (83.5% PDR, 16.5% loss). In contrast to static routing which collapses completely (33.8% PDR, 66.2% loss), RAKSHA-NET detects the anomaly in <200ms and autonomously migrates traffic to LEO-2, restoring mission delivery to 96.8%.

---

## AI vs Static Routing — Window-Wide PDR Comparison

| Window / Metric | AI Routing (RAKSHA) | Static (No AI) | AI Advantage |
|:---|:---:|:---:|:---:|
| **Initial 190ms Reaction Dip** | 0.835 | 0.338 | **+0.497** |
| **Full 6-Second Attack Window** | 0.968 | 0.323 | **+0.645** |
| **Post-Attack Restoration** | 0.968 | 0.869 | **+0.099** |

---

## Route Recovery Statistics (emulated-clock ms)

| Stat | Value |
|---|---|
| Trials | 10 |
| Switch Success Rate | 10/10 (100%) |
| Mean Failover Latency | 190 ms |
| Standard Deviation | 30 ms |
| Range (Min - Max) | 100 ms - 200 ms |
