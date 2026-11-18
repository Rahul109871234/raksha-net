# AICOP-RAKSHA: Unified Autonomous Resilience & Policy Coordination Framework for 5G/6G Terrestrial & Non-Terrestrial Networks

**Authors:** G Rahul Reddy (`24BEC038`), Rajarwar Deependra Sahebrao (`22BCS220`)  
**Faculty Mentor:** Dr. Satish Kumar Tiwari, Department of Electronics & Communication Engineering, PDPM IIITDM Jabalpur  
**Domain:** O-RAN Near-RT RIC | 5G Non-Terrestrial Networks (NTN) | Graph Neural Networks | Post-Quantum Cryptography  

---

## 1. Executive Summary & Vision

As telecommunication architectures evolve toward **3GPP Release-18 and 6G**, terrestrial cellular networks and non-terrestrial satellite constellations (NTN) are converging into a unified, heterogeneous fabric. However, this convergence introduces an unprecedented, multi-surface attack landscape:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              THE DUAL-TIER ATTACK VECTOR IN MODERN 5G/6G NETWORKS              │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. TERRESTRIAL RADIO EDGE (O-RAN gNBs):                                         │
│    Adversaries inject False Data (FDI), spoofing low cell loads or anomalous    │
│    channel states. Conflicting xApps (Traffic Steering vs Energy Saving)        │
│    oscillate wildly, triggering cascaded cell shutdowns and severe QoS drops.  │
│                                                                                 │
│ 2. NON-TERRESTRIAL SPACE UPLINK (LEO Satellite Relays):                        │
│    Adversaries simultaneously deploy high-power Electronic Warfare (RF Jamming) │
│    against satellite feeder links and eavesdrop on ciphertexts to store them    │
│    for future quantum decryption ("Harvest Now, Decrypt Later").               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**AICOP-RAKSHA** is the  unified autonomous cross-layer controller that bridges **O-RAN edge intelligence (AICOP)** with **quantum-safe 5G NTN resilience (RAKSHA-NET)** into a single, closed-loop defense architecture

---

## 2. Integrated System Architecture

```
═════════════════════════════════════════════════════════════════════════════════
                   TIER 3: SPACE / SATELLITE NTN UPLINK (RAKSHA-NET)
═════════════════════════════════════════════════════════════════════════════════
   [LEO Satellite 1 (Primary)]               [LEO Satellite 2 (Strategic Reserve)]
          │                                                    ▲
          │ (RF Jamming: Loss -> 70%)                          │ (190ms Autonomous Failover)
          ▼                                                    │
   ┌───────────────────────────────────────────────────────────┴─────────────────┐
   │ RAKSHA-NET NTN CONTROLLER (Linux TUN `ogstun` + 3GPP Rel-17 Open5GS Core)   │
   │  • Page's CUSUM & Welford EWMA Joint Change-Point Detector                 │
   │  • Calibrated 5% Hysteresis Barrier (0% Route Flapping)                     │
   │  • NIST FIPS 203 ML-KEM-768 Native C PQC Engine (65 µs Encapsulation)       │
   └─────────────────────────────────────▲───────────────────────────────────────┘
                                         │ Cross-Layer Threat Telemetry
                                         │ (RAN Degradation & Cell Corruption Signal)
═════════════════════════════════════════╧═══════════════════════════════════════
               TIER 2: TERRESTRIAL O-RAN Near-RT RIC (AICOP SUBSYSTEM)
═════════════════════════════════════════════════════════════════════════════════
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │ AICOP POLICY COORDINATOR & GRAPHSAGE TRUST ENGINE                           │
   │  • Inductive 2-Layer GraphSAGE (pure NumPy, zero GPU overhead, <8.4ms)       │
   │  • Spatiotemporal Neighborhood Consensus (isolates FDI telemetry corruption)│
   │  • Trust-Weighted Pareto Utility Arbitration (resolves TS vs ES conflicts)   │
   │  • TT-ACTS Canary Hysteresis & Damped Quarantine                            │
   └─────────────────────────────────────▲───────────────────────────────────────┘
                                         │ E2 / E2SM-KPM & E2SM-RC Interfaces
═════════════════════════════════════════╧═══════════════════════════════════════
                 TIER 1: PHYSICAL RADIO ACCESS NETWORK (gNBs & UEs)
═════════════════════════════════════════════════════════════════════════════════
   [gNB-01] [gNB-02] [gNB-03 (FDI Spoofed)] [gNB-04 (Jammed)] ... [gNB-12]
   • Dual-Band: 700 MHz (Macro Coverage) / 3.5 GHz (Capacity Microcells)
```

---

## 3. Mathematical Formulations & Cross-Layer Control Loop

### 3.1 Inductive GraphSAGE Cell Trust Inference
For each radio access node $v \in \mathcal{V}$ with feature vector $x_v = [\text{load}_{\text{rep}}, \text{SINR}_{\text{rep}}, \text{load}_{\text{ref}}, \text{SINR}_{\text{ref}}]^T$:
$$h_{\mathcal{N}(v)}^{(1)} = \frac{1}{|\mathcal{N}(v)|} \sum_{u \in \mathcal{N}(v)} W_1 \cdot x_u$$
$$h_v^{(1)} = \text{ReLU}\left(W_1 \cdot x_v + h_{\mathcal{N}(v)}^{(1)} + b_1\right)$$
$$T(v) = \sigma\left(W_2 \cdot h_v^{(1)} + b_2\right) \cdot \exp\left(-\beta \cdot \|x_v^{\text{rep}} - x_v^{\text{ref}}\|_1\right)$$
Where $T(v) \in [0.05, 1.00]$ is the refined trust score. If $T(v) < 0.40$, cell $v$ is flagged as corrupted.

### 3.2 Trust-Weighted Pareto xApp Arbitration
The coordinated action for each cell balances Traffic Steering ($\Delta_{\text{TS}}$), Energy Saving ($\Delta_{\text{ES}}$), and QoS Latency ($\Delta_{\text{QoS}}$):
$$U_{\text{joint}}(v) = \lambda \cdot T(v) \cdot \Delta_{\text{TS}}(v) + (1 - \lambda) \cdot T(v)^2 \cdot \Delta_{\text{ES}}(v) + \Delta_{\text{QoS}}(v)$$
* **Pacifista Veto:** If $\Delta_{\text{TS}} > 0.05 \land \Delta_{\text{ES}} < 0$, $\Delta_{\text{ES}}$ is forced to $0.0$, preventing power shutdowns on cells absorbing steered load.
* **Quadratic Trust Penalty ($T(v)^2$):** Ensures that compromised or flapping nodes are barred from entering sleep mode under false low-load claims.

### 3.3 Cross-Layer Threat Propagation & Page's CUSUM Detector
The terrestrial degradation score feeds directly into RAKSHA-NET's joint anomaly metric:
$$A_{\text{joint}}(t) = w_{\text{RAN}} \cdot \left(\frac{1}{N} \sum_{v=1}^N \mathbb{I}_{T(v) < 0.40} + \text{SLA\_Risk}\right) + w_{\text{NTN}} \cdot A_{\text{CUSUM}}(t)$$
Where $A_{\text{CUSUM}}(t)$ is derived from Page's test tracking satellite packet loss $\ell_t$:
$$S_t = \max\left(0, S_{t-1} + \frac{\ell_t - \mu_t}{\sigma_t} - k\right)$$

When $A_{\text{joint}}(t) \ge 0.60$:
1. **Autonomous Route Handover:** Reroutes traffic to healthy LEO-2 in **190 ms ($\pm 30\text{ ms}$)**.
2. **Hysteresis Enforcement:** Switching is locked under barrier $\epsilon = 0.05$, guaranteeing **0% route flapping**.
3. **Quantum Forward Secrecy:** Concurrently triggers native C **NIST FIPS 203 ML-KEM-768** key encapsulation in **$65\text{ }\mu\text{s}$**, securing user data against eavesdropping.

---

## 4. Empirical Benchmark Data & System Outcomes

Validated across 240 simulated O-RAN runs and 10 live Open5GS / `liboqs` hardware-in-the-loop trials:

| Metric / Parameter | Baseline (Uncoordinated) | Unified AICOP-RAKSHA System | Net Measurable Advantage |
| :--- | :---: | :---: | :---: |
| **QoS-SLA Violation Under 50% Telemetry Flapping** | **35.31%** | **5.88%** | **-29.43% SLA Violations** (Superior to PACIFISTA baseline of 8.24%) |
| **Daily Modeled Base Station Power Savings** | 0.0% (Always On) | **20.4% Daily (71.2% Off-Peak)** | Significant operational energy conservation |
| **Packet Delivery Under Space Electronic Jamming** | **32.3% PDR** | **96.8% PDR** | **+64.5% Net PDR Gain** ($p = 5.6 \times 10^{-15}$) |
| **Autonomous Route Failover Latency** | $>30\text{ seconds}$ (Manual) | **190 milliseconds** | **150× Faster Response**, sub-second path healing |
| **Route Flapping Oscillations** | Frequent flapping | **0 Flaps (0%)** | Stable state enforced by $5\%$ hysteresis barrier |
| **Post-Quantum Cryptographic Handshake** | None / Classical ECC | **NIST FIPS 203 ML-KEM-768** | **65 µs Encapsulation** in native C (`liboqs`) |
| **Edge AI Inference Execution Overhead** | 400–1,200 ms (Cloud GPU) | **8.4 milliseconds** (pure NumPy) | Runs on embedded edge gNB without GPU dependency |

---

## 5. Summary of Unified Codebase Architecture

* [`controller/aicop_bridge.py`](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/controller/aicop_bridge.py): Inductive 2-layer GraphSAGE engine and Pareto xApp policy arbiter.
* [`controller/unified_controller.py`](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/controller/unified_controller.py): Master cross-layer controller integrating AICOP and RAKSHA-NET state machines.
* [`scripts/run_unified_aicop_raksha.py`](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/scripts/run_unified_aicop_raksha.py): Runnable 12-tick dual-attack simulation harness.
* [`controller/security_engine.py`](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/controller/security_engine.py): Native C `liboqs` wrapper for NIST ML-KEM-768 and hybrid AEAD.
* [`controller/anomaly_engine.py`](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/controller/anomaly_engine.py): Welford EWMA and Page's CUSUM change-point detectors.
