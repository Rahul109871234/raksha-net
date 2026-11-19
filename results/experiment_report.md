# RAKSHA-NET — Experiment Summary

> **Emulated Testbed** — PDPM IIITDM Jabalpur — Sovereign Technology for India  
> All results from statistical simulation (100ms emulated control cycle).  
> Not real satellites, RF jamming, QKD, or defense deployment.

**Trials:** 20 | **Backend:** MOCK | **Detector:** HeuristicDetector  
**Source:** `experiment.csv`

---

## Table: Multi-Phase Attack Dynamics (Before, Initial Dip, and Rerouted)

| Operational Phase | RAKSHA-NET (AI Routing) | Static Routing (No AI) | Impact / Note |
|:---|:---:|:---:|:---|
| **Normal (Pre-Attack)** | 0.972 (3.2% loss) | 0.972 (3.2% loss) | Baseline nominal traffic |
| **Initial Reaction Dip (Onset $\rightarrow$ Switch, ~190ms)** | **0.785** (21.5% loss) | **0.311** (68.9% loss) | Transient impact before failover |
| **Rerouted Steady-State (LEO-2 Backup)** | **0.970** (3.2% loss) | **0.325** (67.5% loss) | AI rescues link; Static stays jammed |
| **Post-Attack Recovery (Normal restored)** | **0.970** | **0.872** | Network profile restored to normal |
| **Route Recovery Latency** | **mean=185ms** (SD=36ms, min=100, max=200) | No failover | Switched in 1-2 control cycles (100%) |
| **NIST ML-KEM-768 Rekey Latency** | **N/A (MOCK backend — do not report)** | No rekey | Native C `liboqs` execution |

> **Key takeaway:** The initial EW attack causes a measurable transient dip in packet delivery (78.5% PDR, 21.5% loss). In contrast to static routing which collapses completely (31.1% PDR, 68.9% loss), RAKSHA-NET detects the anomaly in <200ms and autonomously migrates traffic to LEO-2, restoring mission delivery to 97.0%.

---

## AI vs Static Routing — Window-Wide PDR Comparison

| Window / Metric | AI Routing (RAKSHA) | Static (No AI) | AI Advantage |
|:---|:---:|:---:|:---:|
| **Initial 190ms Reaction Dip** | 0.785 | 0.311 | **+0.474** |
| **Full 6-Second Attack Window** | 0.970 | 0.325 | **+0.644** |
| **Post-Attack Restoration** | 0.970 | 0.872 | **+0.098** |

---

## Route Recovery Statistics (emulated-clock ms)

| Stat | Value |
|---|---|
| Trials | 20 |
| Switch Success Rate | 20/20 (100%) |
| Mean Failover Latency | 185 ms |
| Standard Deviation | 36 ms |
| Range (Min - Max) | 100 ms - 200 ms |
