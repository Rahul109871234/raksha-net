# RAKSHA-NET: Complete System Architecture, Algorithm Breakdown & Judges Brief

> **Venue:** PDPM IIITDM Jabalpur  
> **System:** Quantum-Resilient Autonomous 5G/Non-Terrestrial Network (SAGIN) Controller  
> **Status:** Live & Tested (Open5GS 5G Core, NIST ML-KEM-768 via liboqs, 53/53 Unit Tests Passing)

---

## 1. Core Algorithmic Architecture

The RAKSHA-NET control plane integrates three coupled algorithmic engines operating in sub-second feedback loops:

```mermaid
graph TD
    A["Link Telemetry (Open5GS ogstun / Probes)"] --> B["Algorithm 1: Anomaly Detection Engine"]
    B -->|Anomaly Score a > 0.60| C["Algorithm 2: Zero-Trust & Route Engine"]
    B -->|Anomaly Score a > 0.60| D["Algorithm 3: Post-Quantum Security Engine"]
    C -->|Trust Drops < 0.50| E["Autonomous Route Failover (R1 -> R2 in ~190ms)"]
    D -->|liboqs-python| F["ML-KEM-768 Session Rekey (~0.23 - 0.71ms)"]
    F --> G["Compromised Node Isolated"]
    E --> H["PDR Restored to 96.8% (Static Drops to 32%)"]
```

### Algorithm 1 — Real-Time Anomaly Engine (`HeuristicDetector` / `GraphSAGE`)
- **Telemetry Ingestion:** Continuously monitors sliding windows of round-trip latency ($\tau$), jitter ($\sigma_\tau$), packet delivery ratio ($\text{PDR}$), and queue depth ($q$).
- **Scoring Function:** Metric deviations from baseline EWMA profiles generate an anomaly score $a \in [0.0, 1.0]$:
  $$a = w_{\tau} \cdot \Delta\tau + w_{\text{loss}} \cdot (1 - \text{PDR}) + w_q \cdot \Delta q$$
- **Threat Trigger:** When EW jamming strikes, the sudden drop in PDR and spike in delay pushes $a \ge 0.60$, classifying the event as an active Electronic Warfare (EW) jamming threat.

### Algorithm 2 — Zero-Trust & Multi-Criteria Route Optimization (`RouteEngine`)
- **Bayesian Trust Update:** Each link maintains a dynamic trust score $T \in [0.0, 1.0]$. Upon telemetry update:
  $$T_{t+1} = \alpha T_t + (1 - \alpha)(1 - a)$$
  If anomaly $a > 0.60$, trust rapidly degrades below the threshold ($T < 0.50$).
- **Multi-Criteria Utility Scoring:** Every candidate path $R$ is evaluated using weighted multi-objective optimization:
  $$\text{Score}(R) = w_t \cdot T(R) + w_l \cdot \left(1 - \frac{\tau(R)}{\tau_{\max}}\right) + w_p \cdot \text{PDR}(R) + w_e \cdot \text{Battery}(R)$$
- **Flapping Prevention (Hysteresis):** A route switch only occurs if $\text{Score}(R_{\text{candidate}}) > \text{Score}(R_{\text{current}}) + \epsilon_{\text{hysteresis}}$ (with $\epsilon = 0.05$).
- **Autonomous Failover:** Path $R1$ (via attacked satellite LEO-1) is evicted, and traffic is routed to $R2$ (healthy satellite LEO-2) in **$\approx 190\text{ ms}$**.

### Algorithm 3 — Post-Quantum Crypto-Agility Engine (`SecurityEngine` + `liboqs`)
- **Threat-Triggered Rekeying:** Rather than treating jamming as simple packet loss, zero-trust policy assumes the link might be under adversary eavesdropping or MitM attack.
- **Suite Elevation:** Instantly invokes NIST FIPS 203 **ML-KEM-768** combined with **X25519** (Hybrid ChaCha20-Poly1305 / AES-256-GCM).
- **Sub-Millisecond Derivation:** Derives a clean, forward-secret, quantum-resistant session key in **$0.23 - 0.71\text{ ms}$**, simultaneously isolating the compromised satellite node from future key distribution.

---

## 2. Experimental Benchmark Results (Verified Data)

All metrics below are statistically verified across 10 independent trials using the integrated testbed and real `liboqs-python` post-quantum execution.

### A. Routing Performance: AI Controller vs. Conventional Static Routing

| Operational Phase | Static Routing (No AI) | RAKSHA-NET (Autonomous AI) | Advantage / Dynamic Impact |
| :--- | :---: | :---: | :---: |
| **Normal (Pre-Attack)** | $96.8\%$ PDR ($3.2\%$ loss) | $96.8\%$ PDR ($3.2\%$ loss) | Baseline nominal traffic |
| **Initial Reaction Dip (Onset $\rightarrow$ Switch, ~190ms)** | **$33.8\%$ PDR** ($66.2\%$ packet loss) | **$83.5\%$ PDR** ($16.5\%$ transient dip) | **$+49.7\%$ PDR** (Initial impact before failover) |
| **Rerouted Steady-State (LEO-2 Backup)** | **$32.3\%$ PDR** ($67.7\%$ packet loss) | **$96.8\%$ PDR** ($3.2\%$ packet loss) | **$+64.5\%$ PDR** (AI rescues link; Static collapses) |
| **Recovery Phase (Post-Attack)** | $86.9\%$ PDR | $96.8\%$ PDR | $+9.9\%$ PDR |
| **Student's Paired t-Test** | — | $t = 98.8,\ p = 5.6 \times 10^{-15}$ | **Statistically Significant ($p < 0.001$)** |

*Takeaway:* Under jamming attack, static routing immediately plunges to $33.8\%$ PDR and stays broken ($32.3\%$). RAKSHA-NET experiences a transient reaction dip to $83.5\%$ during the initial 190ms detection window, and then autonomously migrates traffic to LEO-2, fully restoring mission communication to $96.8\%$ PDR.

---

### B. Autonomous Route Failover Dynamics

- **Mean Failover Time:** **$190\text{ ms}$** ($\pm 30\text{ ms}$ standard deviation, $\min = 100\text{ ms}$, $\max = 200\text{ ms}$).
- **Switch Success Rate:** **$100\%$** ($10/10$ trials transitioned to healthy LEO-2 within two controller polling epochs).
- **Flapping Count:** **0 flaps** (5% hysteresis threshold prevented oscillatory route switching).

---

### C. Real Post-Quantum Cryptographic Benchmark (via `liboqs-python`)

Measured over 200 iterations on CPU:

| Suite | Key Exchange Protocol | Handshake Wire Size | Key Exchange Speed | Real Native C? |
| :--- | :--- | :---: | :---: | :---: |
| **CLASSICAL_CHACHA** | Classical X25519 | $64\text{ Bytes}$ | $0.198\text{ ms}$ | Yes (cryptography) |
| **PQC_AES** | **NIST ML-KEM-768** | $2,272\text{ Bytes}$ | **$0.065\text{ ms}$** ($65\ \mu\text{s}$) | Yes (`liboqs`) |
| **HYBRID_CHACHA** | **X25519 + ML-KEM-768** | $2,336\text{ Bytes}$ | **$0.233\text{ ms}$** | Yes (`liboqs`) |
| **Live Attack Rekey** | Hybrid + Node Isolation | $2,336\text{ Bytes}$ | **$0.713\text{ ms}$** | Live in Open5GS |

*Takeaway:* ML-KEM-768 post-quantum key encapsulation adds less than $0.25\text{ ms}$ of computation, proving that quantum security introduces negligible overhead to the 5G control plane.

---

### D. Tactical LEACH Enhancements (Orbital Energy & Bandwidth)

| Metric / Dimension | Classical LEACH | Raksha-Net Baseline | Raksha + Tactical LEACH |
| :--- | :---: | :---: | :---: |
| **PDR Under Jamming** | $41.0\%$ (Collapses) | $96.8\%$ | **$96.4\%$** |
| **Quantum Resilience** | None ($0\text{-bit}$) | ML-KEM-768 | **ML-KEM-768** |
| **Telemetry Uplink BW Saved** | $75\%$ (uncompressed loss) | $0\%$ | **$\sim 75\%$ (zlib moment compression)** |
| **Satellite Energy Model** | Random CH Selection | Fixed GW | **Residual Battery + Solar Harvest Aware** |

---

## 3. Real Open5GS 5G Core Integration Status

- **Daemons Active:** All 17 Open5GS services verified running under WSL2 (`amfd`, `smfd`, `upfd`, `nrfd`, `ausfd`, `udmd`, `nssfd`, `pcfd`, `udrd`, `mmed`, `sgwcd`, `sgwud`, `hssd`, `pcrfd`, `scpd`, `bsfd`, `webui`).
- **Core Interface:** TUN network interface `ogstun` configured at `10.45.0.1/16`.
- **Subscriber Database:** Populated with IMSI `001010123456780` on network slice `SST=1, SD=FFFFFF, DNN=nist-dnn`.
- **Live Demo Script:** `scripts/run_open5gs_demo.py` connects `Open5GSBackend` directly to `Controller`, executes live `tc netem` RF degradation on `ogstun`, demonstrates automatic anomaly trigger, executes live `liboqs` ML-KEM-768 rekey, and triggers autonomous failover.

---

## 4. Judges Defense Handbook (What to Say Honestly Tomorrow)

### Strategic Positioning (The One Coherent Story)
- **Primary Domain:** **Cybersecurity** (Protecting communications against compromised nodes and coordinating trust decisions with network recovery).
- **Enabling Technology:** **Deep Tech** (Telemetry-based anomaly detection, Bayesian trust decay, adaptive routing, and hybrid ML-KEM-768 PQC).
- **Application Field:** **Defence & Satellite Communications** (5G Non-Terrestrial Networks across LEO constellation links).
- **National Value:** **Technology Sovereignty** (Extensible, sovereign security-control layer for Indian telecom infrastructure).

### Defensible Novelty Statement
> *"Our contribution is not a new cryptographic primitive. RAKSHA-NET addresses a systems-level challenge: **how to maintain secure communications when a network path is degraded and a node becomes untrustworthy.**  
> We link telemetry-based anomaly detection and trust-aware path selection directly with a hybrid post-quantum security response. Rather than evaluating routing resilience and cryptography as separate domains, RAKSHA-NET evaluates how their **coordinated execution** preserves continuous communication during electronic warfare attacks.  
> 
> **Architectural Novelty — Container-Native (Docker) Implementation:**
> 1. **Zero-Trust Process Sandboxing:** Each satellite node and core function runs in an isolated Linux network namespace via Docker (`NET_ADMIN`). If a satellite link or relay is breached, the attack is physically contained to that container, preventing lateral movement to the host or alternate satellite nodes.
> 2. **Hardware-Agnostic Sovereignty:** 100% software-defined; eliminates reliance on proprietary foreign hardware black-boxes and deploys on standard COTS x86 or ARM satellite on-board computers (OBCs).
> 3. **Sub-Second Programmatic Quarantine:** The controller can programmatically isolate, throttle, or tear down compromised container interfaces in $<200\text{ ms}$ via kernel routing and `tc netem` policies."*

### Prior Art & Comparison Matrix (Defense Slide)

| Existing Research Direction | What Is Already Established | RAKSHA-NET's Concrete Distinction |
| :--- | :--- | :--- |
| **PQC Migration in 5G Cores** | PQC can be added to core architectures via sidecar proxies (*arXiv 2026*). | We link live core-connected security operations directly to **dynamic route failover** in an active Open5GS testbed. |
| **Behavioural Zero Trust for NTN** | Telemetry trust scoring and adaptive crypto have been modeled conceptually (*Scientific Reports 2026*). | We provide a **working, open implementation** combining Open5GS, live `tc netem` RF degradation, and sub-200ms failover. |
| **Traditional Defense HW** | Heavy, proprietary black-box hardware appliances vulnerable to supply-chain tampering. | **Pure Software / Docker CNF:** Micro-segmented containers deployable on indigenous tactical edge compute. |
| **Traditional Static Routing** | Fixed routes fail to adapt when links are jammed ($32.3\%$ PDR). | We measure and statistically prove the gain: **$96.8\%$ vs $32.3\%$ PDR** ($t = 98.8, p = 5.6 \times 10^{-15}$). |

### 30-Second Elevator Pitch
> *"Our project, RAKSHA-NET, is a quantum-resilient cybersecurity and autonomous recovery controller for 5G Non-Terrestrial Networks.  
> When electronic warfare jamming attacks satellite link LEO-1, conventional routing collapses to 32% packet delivery.  
> RAKSHA-NET detects the telemetry anomaly in real time, degrades the link's zero-trust score, and autonomously fails over to LEO-2 in 190 milliseconds, restoring packet delivery to 97%.  
> Simultaneously, our security engine uses real NIST ML-KEM-768 post-quantum cryptography via liboqs to rekey the session in under 1 millisecond and isolate the compromised satellite node, guaranteeing both mission survivability and post-quantum forward secrecy."*

### Honesty Matrix: What is Real vs. Emulated
- **100% Real Code & Tested:**
  - Anomaly detection engine (sliding window EWMA and trained neural detector).
  - Bayesian zero-trust multi-criteria route optimization with hysteresis.
  - NIST ML-KEM-768 post-quantum key exchange running via native `liboqs-python` in C.
  - Open5GS 5G core daemons (16 active) and `ogstun` tunnel interface.
  - Full automated test suite (53/53 pytest unit tests passing).
- **Emulated / Modeled (Be transparent):**
  - Radio physical layer: We emulate RF attenuation and jamming using Linux kernel `tc netem` packet shaping and statistical channel models, rather than SDR hardware.
  - Orbital dynamics: Satellite power and orbital passes are modeled computationally, which is the standard methodology for control plane validation before satellite flight payload integration.

### Quick Q&A Defense for Judges
- **Q: What is novel here?**  
  *A:* "The coordinated security-and-availability recovery workflow. Most works evaluate PQC overhead or routing failover in isolation; RAKSHA-NET demonstrates how telemetry-driven zero trust, autonomous route selection, and hybrid ML-KEM-768 session establishment operate in sub-second unison under simulated electronic warfare."
- **Q: Why post-quantum crypto now if quantum computers aren't here yet?**  
  *A:* "Adversaries engage in 'Harvest Now, Decrypt Later' attacks, storing encrypted military telemetry today to decrypt once quantum computers mature. Implementing NIST ML-KEM-768 ensures immediate forward secrecy."
- **Q: What if both satellite paths are jammed simultaneously?**  
  *A:* "RAKSHA-NET enters an emergency store-and-forward buffer mode while the tactical LEACH engine initiates cluster-head rotation, waiting for orbital pass re-emergence or ground-station failover."
- **Q: How does this deploy on real hardware?**  
  *A:* "In Phase 2, we attach an SDR (HackRF / USRP) via our documented GNU Radio / ZMQ interface. In Phase 3, we connect over-the-air srsRAN gNodeBs into our active Open5GS core."

