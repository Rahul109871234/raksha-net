# RAKSHA-NET: Defensible Competition Submission & Jury Evaluation Handbook

> **Challenge:** TechGig / Times of India *Ideas for India 2026*  
> **Theme:** Sovereign Technology (Defence & Strategic Technologies / AI & Deep Tech / Space Technology)  
> **Project:** RAKSHA-NET (Software-Based Security & Resilience Controller for 5G/NTN Testbeds)

---

## 1. Revised Defensible Novelty Statement

### RAKSHA-NET — Novelty and Technical Contribution

> **"RAKSHA-NET is a software-based security and resilience controller for 5G and non-terrestrial network testbeds. It coordinates telemetry-driven anomaly detection, trust-aware route selection and hybrid X25519–ML-KEM-768 key-establishment or rekey operations within a containerized environment connected to Open5GS.**  
>
> **Unlike evaluations that examine route resilience and cryptographic performance separately, our prototype investigates their coordinated operation during controlled network-impairment scenarios. We measure packet delivery ratio, route recovery time and cryptographic execution latency to evaluate the effects of adaptive recovery.**  
>
> **Our current contribution is the integrated controller, its implementation in the testbed and the evaluation of its response under the conditions tested. Physical-RF validation, indigenous embedded-hardware portability and operational deployment remain future validation objectives."**

---

## 2. Reconciled Experimental Performance Data (Single Source of Truth)

All metrics below are drawn directly from the underlying 10-trial experimental benchmark log ([results/benchmark_heuristic.csv](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/results/benchmark_heuristic.csv)) and match the generated comparison chart ([results/benchmark_heuristic_metrics.png](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/results/benchmark_heuristic_metrics.png)).

### The 4-Phase PDR Timeline

```text
Normal Baseline (96.8%) 
       │
       ▼ [Jamming Injected]
Initial Reaction Dip (~190 ms mean)
  ├─ Static: 33.8% (Catastrophic collapse)
  └─ AI:     83.5% (Transient drop during anomaly detection & switch)
       │
       ▼ [Failover to LEO-2 Completed]
Sustained Attack Window (Steady-State)
  ├─ Static: 32.3% (Remains unmitigated)
  └─ AI:     96.8% (Recovered on backup satellite route)
       │
       ▼ [Jamming Ceases]
Post-Attack Restoration
  ├─ Static: 86.9% (Gradually recovers without rerouting)
  └─ AI:     96.8% (Stable nominal transmission)
```

### Complete Reconciled Performance Table

| Experimental Phase | RAKSHA-NET (AI Controller) | Static Routing (No Controller) | Empirical Difference | Physical Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Phase 1: Normal Pre-Attack** | **$96.8\%$ PDR** ($3.2\%$ loss) | **$96.8\%$ PDR** ($3.2\%$ loss) | $0.0\%$ | Baseline nominal traffic across 3-hop satellite path. |
| **Phase 2: Transient Reaction Dip** | **$83.5\%$ PDR** ($16.5\%$ loss) | **$33.8\%$ PDR** ($66.2\%$ loss) | **$+49.7\%$ PDR** | Transient impact during detection and route selection before failover. |
| **Phase 3: Sustained Attack (Steady-State)** | **$96.8\%$ PDR** ($3.2\%$ loss) | **$32.3\%$ PDR** ($67.7\%$ loss) | **$+64.5\%$ PDR** | Traffic rerouted to backup LEO-2; static routing remains jammed. |
| **Phase 4: Post-Attack Restoration** | **$96.8\%$ PDR** | **$86.9\%$ PDR** | **$+9.9\%$ PDR** | Network profiles returned to normal; static routing recovers slowly. |
| **Full 6-Second Attack Window Average** | **$96.8\%$ PDR** ($\pm 0.4\%$) | **$32.3\%$ PDR** ($\pm 2.0\%$) | **$+64.5\%$ PDR** | Paired Student's $t$-test: $t = 98.8,\ p = 5.6 \times 10^{-15}$ ($n = 10$). |

### Route Recovery & Cryptographic Timing (Empirically Measured)
- **Route Failover Latency:** **Mean = $190\text{ ms}$** ($\text{SD} = 30\text{ ms}$, $\min = 100\text{ ms}$, $\max = 200\text{ ms}$ across 10 trials).  
  *Reporting note:* We report the $190\text{ ms}$ result as a sample mean across ten trials with bounded variance, rather than a universal guarantee.
- **Switch Success Rate:** **$100\%$ ($10/10$ trials)** transitioned to healthy LEO-2 within two 100ms controller cycles.
- **PQC Rekey Latency:** **Mean = $0.48\text{ ms}$** ($\text{SD} = 0.17\text{ ms}$) wall-clock execution on CPU using native C `liboqs-python` for hybrid X25519 + ML-KEM-768.

---

## 3. Q3. Contribution to Selected Challenge Theme (Sovereign Technology)

**Positioning: Strategic Communications Cybersecurity & Deep Tech for India:**

1. **Software-Centric Architecture for Reduced Foreign Hardware Dependency:**  
   Traditional defense communication security often relies on dedicated proprietary cryptographic appliances from foreign vendors. RAKSHA-NET uses a software-based architecture intended to reduce reliance on foreign black-box appliances, with portability to indigenous hardware platforms (e.g., standard COTS ARM processors, Indian Shakti/Vega RISC-V platforms, and CubeSat On-Board Computers) as a primary development goal.
2. **Standardized Post-Quantum Cryptographic Preparedness:**  
   Adversaries engage in *"Harvest Now, Decrypt Later"* espionage, archiving encrypted military telemetry today. RAKSHA-NET implements standardized post-quantum cryptography (**NIST FIPS 203 ML-KEM-768**) designed to resist attacks from adversaries with quantum-computing capabilities, subject to the security assumptions of the algorithm and implementation.
3. **Resilience in Contested 5G NTN Environments:**  
   Addresses a critical operational requirement for India’s emerging satellite and tactical communication infrastructure: maintaining communication availability and cryptographic security when orbital or aerial relay links suffer electronic warfare degradation.

---

## 4. Q4. Development Stage and Validation

**Status: Integrated Laboratory / Testbed Prototype**

Our prototype is evaluated in an integrated emulation and core-network testbed environment:
- **3GPP 5G Core Integration:** Connected to an active **Open5GS 5G Core** instance with 16 active network functions (`amfd`, `smfd`, `upfd`, `nrfd`, `ausfd`, `udmd`, etc.) and user-plane tunneling over active Linux interface `ogstun` (`10.45.0.1/16`).
- **Post-Quantum Implementation:** Native C execution via `liboqs-python` for NIST **ML-KEM-768** key encapsulation ($0.065\text{ ms}$) and hybrid session rekeying ($0.48\text{ ms}$ mean).
- **Containerized Multi-Node Emulation:** Multi-hop satellite topology (`node_a`, `gateway`, `leo1`, `leo2`, `node_b`) running in Docker with per-hop Linux kernel `tc netem` impairment injection.
- **Automated Verification:** **53 out of 53 pytest unit tests passing (100%)**, covering routing hysteresis, anomaly scoring, crypto-agility state transitions, and telemetry aggregation.

---

## 5. Most Significant Impact & "Why Do You Want to Win This"

### Significant Impact:
**"Mitigating Communication Disruption and Preserving Post-Quantum Session Security Under Electronic Warfare Impairments."**  
In tactical and satellite operations, link degradation can lead to mission failure. RAKSHA-NET aims to reduce the duration and severity of communication disruption under evaluated network-impairment scenarios, restoring packet delivery to $96.8\%$ within a mean of $190\text{ ms}$ while rotating cryptographic sessions with quantum-resistant key establishment.

### Why We Want to Win:
> *"Winning the Ideas for India 2026 Challenge provides the institutional support and technical visibility needed to transition RAKSHA-NET from an emulated testbed prototype into physical over-the-air evaluations. It will enable direct engagement with defence and space research organizations (such as DRDO and IN-SPACe) to test our coordinated control algorithms on physical Software-Defined Radios (SDRs) and embedded satellite payloads."*

---

## 6. Sustainability, Scalability, and Inclusion

### A. Sustainability (Energy-Aware Modeling & Computational Efficiency):
- **Energy-Aware Routing Model:** Includes a simulated battery drain and solar replenishment model (inspired by LEACH principles) to evaluate how residual energy can inform route selection.
- **In-Flight Telemetry Compression:** Integrates lossless `zlib` moment compression, achieving approximately $75\%$ bandwidth reduction in telemetry transmission to reduce channel occupancy and modeled RF transmit energy.
- **Lightweight Compute Footprint:** The entire Python controller and C cryptographic library operate within $<60\text{ MB}$ of memory and sub-millisecond execution times, making it suitable for low-power embedded computing environments.

### B. Scalability (Modular Container-Based Architecture):
- **Containerized Microservices:** Designed to run in standard Linux containers (Docker CNF) with isolated network namespaces, allowing the control layer to scale across multi-hop relay configurations.
- **Low Computational Complexity:** Anomaly scoring and Bayesian trust updates are $O(1)$ operations per tick; multi-criteria path selection evaluates candidate routes in microseconds, scaling linearly with network topology size.

### C. Inclusion (Remote Connectivity & Emergency Disaster Response):
- **Civilian & Remote Area Application:** The same resilience mechanism developed for satellite defense can preserve connectivity in remote civilian areas (Himalayan border villages, island territories) where terrestrial fiber is unavailable.
- **Disaster Response Utility:** During natural disasters when terrestrial telecom infrastructure is damaged, the controller can be deployed on temporary aerial relays (UAVs) or portable satellite fly-away kits to establish fault-tolerant emergency communication channels.

---

## 7. Q7. Collaborations, Partnerships & Future Roadmap

### Planned Institutional Engagements:
1. **Defence & Strategic R&D Organizations:** Seeking research partnerships with **DRDO (CAIR / DEAL)** and applying to **iDEX (Innovations for Defence Excellence)** to validate the controller against tactical military communication standards.
2. **Space & Satellite Ecosystem:** Engaging with **IN-SPACe / ISRO** and Indian commercial space entities to explore software-in-the-loop validation on CubeSat on-board computers (OBCs).
3. **National Telecom Testbeds:** Engaging with the **IIT Madras 5G Testbed** and **C-DOT** to test compatibility with indigenous 5G RAN and core deployments over physical RF channels.

### 12-Month Technical Roadmap:
- **Phase 2 (Months 1–3 — Physical RF Validation):** Connect physical Software-Defined Radios (HackRF / USRP) via GNU Radio and ZMQ to validate the controller against actual RF interference and channel fading.
- **Phase 3 (Months 4–6 — Over-the-Air 5G & Embedded ARM Testing):** Test with open-source 5G RAN (`srsRAN`) transmitting to commercial user equipment (UEs) and benchmark controller execution on embedded ARM edge hardware (e.g., Raspberry Pi CM4 / Jetson).
- **Phase 4 (Months 7–12 — Security Hardening & Formal Evaluation):** Conduct formal security audits of session-key handling, implement peer authentication mechanisms (such as ML-DSA), and propose a demonstration payload for a CubeSat orbital platform.
