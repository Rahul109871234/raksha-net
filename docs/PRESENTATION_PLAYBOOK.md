# RAKSHA-NET: Complete Presentation Playbook & Jury Defense Guide

> **Venue:** Ideas for India 2026 (TechGig / Times of India) | PDPM IIITDM Jabalpur  
> **Track:** Sovereign Defence & Strategic Technologies / AI & Deep Tech  
> **Classification & Readiness:** TRL-4 Laboratory Testbed Emulation (No Physical Satellite Deployments Claimed)  
> **License:** Apache License 2.0 (Open Source)  
> **Security Architecture & Threat Model:** [`docs/THREAT_MODEL.md`](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/docs/THREAT_MODEL.md) (STRIDE Methodology)  
> **Generated Deck:** [`raksha-net/results/raksha_net_defense_presentation.pptx`](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/results/raksha_net_defense_presentation.pptx)  
> **Team:** G Rahul Reddy & Rajarwar Deependra Sahebrao  

---

## 1. Presentation Structure & Slide Breakdown (12 Slides)

The deck is engineered in a 16:9 widescreen format using a high-contrast dark tactical defense aesthetic. Every slide includes speaker notes embedded directly into PowerPoint presenter view.

| Slide # | Title & Theme | Core Takeaway | Time (10-12m) | Presenter |
| :---: | :--- | :--- | :---: | :---: |
| **1** | **Title & Strategic Positioning** | Quantum-resilient cyber defense controller for 5G/NTN; TRL-4 testbed validation, Apache 2.0 | 0:00 – 1:00 | Rahul |
| **2** | **Tactical Problem & Threat Landscape** | EW jamming collapse (Static 32% PDR, Reactive BFD 76% PDR) + HNDL quantum threat (`docs/THREAT_MODEL.md`) | 1:00 – 2:00 | Rahul |
| **3** | **Unified 4-Pillar Architecture** | Closed-loop sensing, zero trust, PQC, and Docker CNF namespace sandboxing (STRIDE boundaries) | 2:00 – 3:15 | Deependra |
| **4** | **Algorithmic Engines & Mathematics** | $a_t$ CUSUM/EWMA scoring, Bayesian trust decay, 5% hysteresis, ML-KEM-768 | 3:15 – 4:30 | Deependra |
| **5** | **Container-Native CNF & Blast Radius** | Docker namespace isolation vs. proprietary foreign hardware; Apache 2.0 open source | 4:30 – 5:45 | Deependra |
| **6** | **Empirical Results: Multi-Baseline PDR** | +64.5 pp vs Static, +21.0 pp vs Reactive BFD under jamming ($p = 5.6 \times 10^{-15}$); TRL-4 testbed | 5:45 – 7:00 | Rahul |
| **7** | **Failover Latency & Native C PQC** | 190ms proactive failover (vs 1.5–2.8s BFD), 0.065ms KEM, debunking PQC overhead myth | 7:00 – 8:15 | Rahul |
| **8** | **Active 3GPP 5G Core Integration** | 17 Open5GS daemons, `ogstun`, 53/53 pytest suite, Apache 2.0, `docs/THREAT_MODEL.md` | 8:15 – 9:15 | Rahul |
| **9** | **Tactical LEACH: Space Energy & BW** | TRL-4 solar/battery aware routing simulation + 75% telemetry compression | 9:15 – 10:15 | Deependra |
| **10** | **Defensibility & Honest Implementation** | TRL-4 Honesty Matrix: 100% Real software vs standard RF/orbital emulation (No physical spacecraft) | 10:15 – 11:15 | Deependra |
| **11** | **National Impact & 12-Month Roadmap** | Atmanirbhar sovereignty, Apache 2.0, roadmap from TRL-4 to TRL-5/6 (SDR/OTA) & TRL-7 (CubeSat) | 11:15 – 12:15 | Rahul |
| **12** | **Conclusion & Live Demo Invocation** | Summary (+64.5 pp vs Static, +21.0 pp vs BFD), live terminal demo, and opening for Jury Q&A | 12:15 – 13:00 | Both |

---

## 2. Word-for-Word Spoken Script by Slide

### Slide 1: Title & Strategic Positioning (0:00 – 1:00)
> **[Rahul]:**  
> *"Respected members of the jury, good morning. We are Rahul Reddy and Deependra Rajarwar from PDPM IIITDM Jabalpur. Today, we present **RAKSHA-NET**: an indigenous, open-source (Apache License 2.0) quantum-resilient autonomous cybersecurity and availability controller for 5G Non-Terrestrial Networks, evaluated at **Technology Readiness Level 4 (TRL-4)** in our laboratory testbed.  
> In modern multi-domain defense, tactical superiority depends on resilient satellite communications. However, strategic orbital links face a dual crisis: aggressive Electronic Warfare jamming that severs mission connectivity, and quantum-capable adversaries passively harvesting military signals for future decryption ('Harvest Now, Decrypt Later').  
> RAKSHA-NET addresses this with a unified software controller: restoring packet delivery from 32% back to 97% in 190 milliseconds—delivering a **+64.5 pp advantage over static routing** and **+21.0 pp over standard 3GPP Reactive BFD hold-timers**—while rekeying sessions using NIST ML-KEM-768 post-quantum cryptography in under half a millisecond. We operate strictly as an open-source software-in-the-loop laboratory testbed without claiming physical satellite orbital launches. Let us examine the threat landscape in today's military networks."*

---

### Slide 2: The Tactical Problem & The Threat Landscape (1:00 – 2:00)
> **[Rahul]:**  
> *"When hostile forces deploy Electronic Warfare against satellite communications, conventional routing mechanisms fail catastrophically:  
> First, **static routing** lacks automated failover entirely; in our live testbed, packet delivery ratio collapses to 32.3%—a 67.7% loss that isolates frontline soldiers, UAVs, and tactical commands.  
> Second, the industry-standard **Reactive BFD (RFC 5880 / 3GPP TS 38.300)** relies on consecutive packet loss hold-timers. It waits 15 ticks—1.5 to 2.8 seconds—before triggering failover, causing severe blackout and sustaining only 76.0% PDR.  
> Simultaneously, adversaries are executing 'Harvest Now, Decrypt Later' espionage. Even if satellite traffic is encrypted with RSA or ECC today, adversaries archive the ciphertext to decrypt it once quantum computers mature. As formalized in our STRIDE threat model in `docs/THREAT_MODEL.md`, tactical networks require quantum-safe forward secrecy right now.  
> The root failure is an academic silo: routing engineers only look at path availability, while cryptographers benchmark post-quantum algorithms in isolation. In reality, jamming often signals an active link tampering or Indicator of Compromise. Zero-trust demands that path recovery and cryptographic rekeying execute in sub-second unison. That is what RAKSHA-NET delivers."*

---

### Slide 3: Unified Solution Architecture & The 4 Pillars (2:00 – 3:15)
> **[Deependra]:**  
> *"As shown in our system architecture, RAKSHA-NET operates through a closed-loop feedback controller across four core pillars in our TRL-4 testbed:  
> 1. **Telemetry Ingestion:** Continuously streams round-trip latency, jitter, packet loss, and queue depth directly from the live Open5GS tunnel interface `ogstun`.  
> 2. **Anomaly Detection Engine:** Evaluates deviations against rolling EWMA baselines and Page's CUSUM change-point scores, pushing the anomaly score past 0.60 when jamming hits.  
> 3. **Zero-Trust Route Engine:** Updates Bayesian link trust; when trust drops below 0.50, our multi-criteria optimizer evicts the attacked satellite LEO-1 and proactively migrates traffic to LEO-2 in 190 milliseconds with zero flapping—avoiding the multi-second blackout of reactive BFD.  
> 4. **Post-Quantum Security Engine:** Simultaneously invokes NIST ML-KEM-768 via native C `liboqs`, establishing a clean, forward-secret dual-hybrid session (RFC 9370) in 0.48 milliseconds while isolating the compromised node.  
> Because each relay runs as a Docker Container Network Function (CNF) in an isolated Linux network namespace, lateral privilege escalation is eliminated strictly following `docs/THREAT_MODEL.md`."*

---

### Slide 4: Algorithmic Engines & Mathematical Design (3:15 – 4:30)
> **[Deependra]:**  
> *"Let us look under the hood at the mathematics guaranteeing stability:  
> - In **Algorithm 1**, our anomaly score $a_t$ tracks normalized deviations in latency, queue depth, and packet delivery ratio, augmented by Page's CUSUM change-point detection ($k=0.5, h=2.0$). Our calibrated threshold of $a_t \ge 0.60$ cleanly detects jamming onset within milliseconds, whereas standard BFD waits for 15 consecutive dropped-packet ticks.  
> - In **Algorithm 2**, Bayesian trust updates via $T_{t+1} = \alpha T_t + (1 - \alpha)(1 - a_t)$ with $\alpha = 0.85$, ensuring that jamming triggers a steep trust collapse. Routes are scored across Trust, Latency, PDR, and Battery reserves. To eliminate route flapping, we enforce a strict 5% hysteresis margin ($\epsilon = 0.05$). In our empirical testing across all trials, route flapping was exactly zero.  
> - In **Algorithm 3**, the security engine combines NIST ML-KEM-768 with X25519 via HKDF-SHA256, instantaneously isolating the compromised satellite from future key schedules and enforcing the cryptographic mitigations in `docs/THREAT_MODEL.md`."*

---

### Slide 5: Container-Native Architecture & Zero-Trust Blast Radius (4:30 – 5:45)
> **[Deependra]:**  
> *"Juries frequently ask: 'Why implement this in software containers rather than proprietary foreign hardware?'  
> The answer lies in four decisive operational and sovereignty advantages:  
> 1. **Blast-Radius Containment:** In proprietary chassis, a link breach can laterally infect the host. In RAKSHA-NET, every satellite node runs in an isolated Linux network namespace via Docker CNFs. An attacker who breaches LEO-1 cannot escape the container, mitigating STRIDE Elevation of Privilege per `docs/THREAT_MODEL.md`.  
> 2. **Hardware Sovereignty:** We eliminate foreign cryptographic ASIC black-boxes. Our 100% software-defined stack runs on standard COTS ARM processors or India's indigenous Shakti and Vega RISC-V platforms.  
> 3. **Sub-Second Programmatic Quarantine:** The controller evicts or rate-limits compromised container interfaces in under 200 milliseconds using kernel routing.  
> 4. **Apache 2.0 Open-Source Footprint:** The entire controller requires under 60 MB of memory, licensed under Apache 2.0 to eliminate commercial vendor lock-in."*

---

### Slide 6: Empirical Results: Multi-Baseline PDR Restoration Under Jamming (5:45 – 7:00)
> **[Rahul]:**  
> *"Here are our empirical results across 10 independent trials using our active TRL-4 testbed:  
> Notice the operational performance comparing three routing strategies:  
> - In **Phase 1**, pre-attack baseline PDR is 96.8% across all systems.  
> - At $t = 2\text{s}$, active RF jamming strikes LEO-1. Under static routing, PDR plunges to 33.8% and stays broken at 32.3% during steady-state.  
> - Under standard 3GPP **Reactive BFD (RFC 5880)**, the system waits 15 ticks (1.5 to 2.8 seconds) for loss hold-timers to expire before triggering failover, resulting in an average sustained PDR of only 76.0% (24% packet loss).  
> - **RAKSHA-NET (Proactive AICOP)** experiences only a brief 190ms reaction dip to 83.5% during detection and switchover. It immediately fails over to LEO-2, fully restoring packet delivery to 96.8%—delivering a **+64.5 pp net gain over static routing** and a **+21.0 pp advantage over Reactive BFD**.  
> - A paired Student's t-test yields $t = 98.8$ and $p = 5.6 \times 10^{-15}$, confirming that our proactive recovery is statistically definitive under our emulated laboratory testbed conditions."*

---

### Slide 7: Failover Latency & Native C Post-Quantum Cryptography (7:00 – 8:15)
> **[Rahul]:**  
> *"Next, let us address the primary critique of Post-Quantum Cryptography: the myth that PQC is too computationally heavy for tactical 5G.  
> Measured over 200 iterations using native C `liboqs`:  
> - Pure NIST ML-KEM-768 key encapsulation takes just **0.065 milliseconds**—that is 65 microseconds! It is actually three times faster to compute than classical X25519 (0.198 ms).  
> - Our dual-hybrid suite (X25519 + ML-KEM-768 per RFC 9370) executes in **0.233 milliseconds**.  
> - Even during an active attack inside Open5GS, complete session re-negotiation, HKDF derivation, and node isolation take only **0.48 to 0.71 milliseconds**—well within the 1-millisecond real-time 5G deadline.  
> - Compare our 190ms proactive failover to Reactive BFD's 1,500–2,800ms hold-timer outage: RAKSHA-NET is an order of magnitude faster, with zero route flaps.  
> Furthermore, at 2.3 kilobytes, the handshake payload fits inside standard MTU frames without IP fragmentation."*

---

### Slide 8: Real 3GPP 5G Core Integration (Open5GS Live Testbed) (8:15 – 9:15)
> **[Rahul]:**  
> *"To ensure RAKSHA-NET is not just a simulation, we integrated it with a live 3GPP Release-17 5G Core: Open5GS.  
> All 17 Open5GS core daemons are verified and running under our WSL2 Ubuntu 24.04 TRL-4 testbed—including the AMF, SMF, UPF, and AUSF. User traffic traverses a real Linux TUN interface `ogstun` at `10.45.0.1/16`.  
> In our live demo script (`scripts/run_open5gs_demo.py`), we inject electronic warfare impairments using Linux kernel traffic control (`tc netem`) directly onto `ogstun`. The controller detects the degradation, executes the PQC rekey in C, and updates routing in real time.  
> Our architecture adheres strictly to the STRIDE threat model formalized in `docs/THREAT_MODEL.md`, is released under Apache 2.0, and passes **53 out of 53 pytest unit tests (100%)**, ensuring complete code reliability."*

---

### Slide 9: Tactical LEACH: Satellite Energy & Telemetry Compression (9:15 – 10:15)
> **[Deependra]:**  
> *"In low-Earth-orbit constellations, electrical power and RF uplink bandwidth are critical constraints. Within our TRL-4 orbital simulation environment, we enhanced the classical LEACH protocol with tactical awareness:  
> - **Orbital Energy & Solar Awareness:** Satellites pass between eclipse and sunlight. RAKSHA-NET incorporates residual battery level and solar exposure into route scoring, preventing premature battery exhaustion on shadowed relays.  
> - **In-Flight Telemetry Compression:** Streaming high-frequency telemetry can congest satellite uplinks. By implementing lossless zlib moment compression, we achieve approximately **75% bandwidth reduction**.  
> In comparative benchmarks, RAKSHA-NET maintains 96.4% PDR under jamming while preserving constellation lifetime, avoiding the cluster collapses seen in classical LEACH and static baselines."*

---

### Slide 10: Defensible Novelty & Honest Implementation Matrix (10:15 – 11:15)
> **[Deependra]:**  
> *"We believe absolute scientific honesty is the cornerstone of jury trust. Here is our transparent TRL-4 implementation matrix:  
> - **What is 100% Real Software:** Our NIST ML-KEM-768 cryptography is compiled native C via `liboqs`. Our 5G Core is live Open5GS with 17 daemons. Our anomaly scoring, Bayesian trust, and routing algorithms are live production code verified by 53 unit tests. Our security architecture is documented in `docs/THREAT_MODEL.md` and open source under Apache 2.0.  
> - **What is Emulated (TRL-4 Lab Prototype):** We make ZERO claims of having launched physical satellites or deployed spaceflight payloads. The physical RF channel is emulated using Linux kernel `tc netem` packet shaping, and orbital passes are modeled computationally. This is standard aerospace engineering methodology for control-plane validation prior to hardware integration.  
> - **Our Defensible Novelty:** We do not claim to invent a new mathematical cipher or put a physical satellite into orbit today. Our contribution is the container-native, coordinated execution of proactive zero-trust route recovery and post-quantum session rekeying under electronic warfare, validated at TRL-4."*

---

### Slide 11: National Impact, Technology Sovereignty & Roadmap (11:15 – 12:15)
> **[Rahul]:**  
> *"Looking at national strategic value, RAKSHA-NET directly supports Atmanirbhar Bharat in strategic communications. By transitioning from foreign proprietary crypto appliances to an Apache 2.0 licensed software controller, India avoids foreign hardware lock-in and supply-chain backdoors.  
> Beyond defense, it provides civilian inclusion: maintaining emergency telecom in isolated Himalayan border outposts and island territories, or as UAV fly-away kits during natural disasters.  
> Our 12-month roadmap defines a clear progression from laboratory emulation to spaceflight:  
> - **Phase 1 (Completed):** TRL-4 Laboratory Prototype with Open5GS, liboqs, Docker CNFs, and multi-baseline validation.  
> - **Phase 2 (Months 1–3) [TRL-5 Target]:** Connect physical Software-Defined Radios (HackRF/USRP B210) via GNU Radio.  
> - **Phase 3 (Months 4–6) [TRL-6 Target]:** Deploy over-the-air srsRAN gNodeBs on embedded ARM hardware (Jetson / Pi CM4).  
> - **Phase 4 (Months 7–12) [TRL-7 Target]:** Propose a flight payload for an Indian CubeSat orbital mission via IN-SPACe / ISRO."*

---

### Slide 12: Conclusion, Live Demo & Q&A (12:15 – 13:00)
> **[Both]:**  
> *"To conclude, RAKSHA-NET proves that communication resilience and quantum-safe security can operate in sub-second unison:  
> - Restoring 96.8% packet delivery in 190 milliseconds (**+64.5 pp over static routing, +21.0 pp over Reactive BFD**).  
> - Establishing post-quantum forward secrecy in under half a millisecond via NIST ML-KEM-768.  
> - 100% software-defined, Apache 2.0 licensed, STRIDE threat-modeled (`docs/THREAT_MODEL.md`), and verified against an active 5G Core at TRL-4.  
> Our prototype is running live right now. We invite the jury to inspect our live terminal demo, review our telemetry dashboard, and we look forward to your questions. Thank you!"*

---

## 3. Fast 5-Minute Flash Pitch Adaptation

If the jury interrupts or shortens your pitch to **5 minutes**, deliver this condensed version:

- **Minute 1 (Slides 1 & 2):** Introduce yourselves, define the crisis (EW jamming drops static PDR to 32% and BFD to 76%, HNDL quantum threat), cite Apache 2.0 and `docs/THREAT_MODEL.md`, and state the thesis: proactive availability and post-quantum security must be coordinated.
- **Minute 2 (Slides 3 & 4):** Walk through the 4-pillar diagram: Open5GS telemetry $\rightarrow$ Page's CUSUM / EWMA anomaly trigger ($a \ge 0.60$) $\rightarrow$ Bayesian trust decay $\rightarrow$ 190ms proactive failover to LEO-2 (vs 1.5–2.8s BFD timeout) + 0.48ms ML-KEM-768 rekey.
- **Minute 3 (Slides 6 & 7):** Show the empirical results: +64.5 pp gain over static routing, +21.0 pp gain over Reactive BFD ($p < 0.001$), 190ms failover with 0 flaps, and debunk the PQC overhead myth with 65-microsecond ML-KEM-768 native C execution.
- **Minute 4 (Slides 8 & 10):** Give the TRL-4 honesty matrix: Real Open5GS core (17 daemons) + real native C `liboqs` + 53 unit tests; RF channel shaped via `tc netem`. Explicitly disclose TRL-4 laboratory testbed status (no physical satellites claimed). Emphasize container sandboxing (Docker CNF).
- **Minute 5 (Slide 12):** Conclude on strategic sovereignty, invoke the live demo, and invite jury questions.

---

## 4. Live Demonstration Walkthrough Guide

When the jury asks to see the system running live, execute these four steps:

### Demo Step 1: Automated Unit Test Suite (10 seconds)
Show that the mathematics and logic are 100% verified:
```bash
wsl -d Ubuntu-24.04 python3 -m pytest tests/ -q
```
*Expected Output:* `53 passed in ~1.2s`. Point out: *"53/53 tests passing across routing hysteresis, anomaly scoring, crypto transitions, and telemetry aggregation."*

### Demo Step 2: Multi-Baseline Scenario Benchmark (20 seconds)
Run the automated scenario comparing Proactive AICOP vs Reactive BFD vs Static Routing:
```bash
python scripts/run_scenario.py --trials 5 --compare-static
```
*Expected Output:* Shows paired trials comparing Proactive AICOP (190ms failover, ~97% PDR) vs Reactive BFD (15-tick hold timer timeout, ~76% PDR) vs Static Routing (0% failover, ~32% PDR).

### Demo Step 3: Live Open5GS Terminal Attack & Recovery (30 seconds)
Run the live integration script connecting directly to the Open5GS core:
```bash
wsl -d Ubuntu-24.04 python3 -m scripts.run_open5gs_demo
```
*What happens on screen:*
1. Controller attaches to `ogstun` (`10.45.0.1`).
2. Live traffic flows nominally (Anomaly score = 0.00, PDR = 96.8%).
3. Active `tc netem` impairment injected onto `ogstun`.
4. Anomaly score spikes ($a \ge 0.60$), trust decays ($T < 0.50$).
5. Live `liboqs` ML-KEM-768 rekey fires in C ($<1\text{ ms}$).
6. Route failover to LEO-2 executes in ~190ms; PDR recovers to 96.8%.

### Demo Step 4: Interactive Telemetry Dashboard (Streamlit)
Open the browser at `http://localhost:8501`:
```bash
python -m streamlit run dashboard/app.py
```
*Show the jury:* The real-time gauges for Anomaly Score, Link Trust, PDR curves comparing AI vs BFD vs Static, and cryptographic suite status.

---

## 5. Master Jury Defense & Cross-Examination Cheatsheet

### Category A: Novelty & Academic Literature
- **Q: "Isn't combining PQC and 5G already done in literature (e.g. arXiv 2026 or Scientific Reports 2026)?"**  
  *Answer:* "Yes, academic literature has begun exploring PQC in 5G cores via sidecar proxies, and theoretical models for NTN zero-trust have been published. However, existing works treat routing resilience and cryptography in isolation. RAKSHA-NET's concrete contribution is the **coordinated execution**: we demonstrate that when an orbital link is jammed, zero-trust trust decay directly triggers autonomous sub-200ms route failover coupled with sub-millisecond NIST ML-KEM-768 session rekeying and node quarantine in an active testbed."

- **Q: "Did you design a new post-quantum cryptographic algorithm?"**  
  *Answer:* "No, and doing so would be a security anti-pattern in military engineering. We implement the standardized NIST FIPS 203 ML-KEM-768 via the industry-standard native C `liboqs` library. Our innovation is at the systems control plane: dynamic crypto-agility triggered by real-time telemetry anomalies."

### Category B: Cryptography & Performance Overhead
- **Q: "Why do we need Post-Quantum Cryptography now if quantum computers don't exist yet?"**  
  *Answer:* "Because of 'Harvest Now, Decrypt Later' espionage. Adversaries are recording encrypted military communications today. When a quantum computer arrives in 5 to 10 years, all classically encrypted telemetry will be compromised. NIST ML-KEM-768 guarantees forward secrecy starting immediately, mitigating Information Disclosure as documented in `docs/THREAT_MODEL.md`."

- **Q: "Isn't ML-KEM-768 too slow and heavy for 5G low-latency control planes?"**  
  *Answer:* "That is a common misconception that our benchmarks directly disprove. In our native C `liboqs` tests, ML-KEM-768 key encapsulation takes just 0.065 ms (65 microseconds)—faster than classical X25519 (0.198 ms). Even with complete session re-negotiation inside Open5GS, live rekeying takes only 0.48 to 0.71 ms, well below the 1-millisecond 5G threshold."

### Category C: Multi-Baseline Comparison (Reactive BFD vs Proactive AICOP)
- **Q: "Why not simply use standard 3GPP Reactive BFD (Bidirectional Forwarding Detection) instead of AI?"**  
  *Answer:* "Standard Reactive BFD (RFC 5880 / 3GPP TS 38.300) relies on consecutive packet loss count or hold-timer timeouts (typically 15 ticks, equivalent to 1,500–2,800 ms). During this detection window, tactical telemetry suffers complete blackout, yielding a sustained PDR of only 76.0% (24% packet loss). Furthermore, BFD is blind to multi-parameter degradation (jitter, queue delay, and cryptographic compromise). RAKSHA-NET uses Page's CUSUM and Bayesian trust decay to detect drift proactively, failing over in 190 ms to achieve 96.8% PDR (+21.0 pp advantage over BFD) with zero route flapping."

### Category D: Emulation vs. Real Hardware (TRL-4 Status)
- **Q: "Is this running on real satellites and real radios?"**  
  *Answer:* "To be completely transparent: RAKSHA-NET is a **TRL-4 laboratory prototype**. We make **no claim of physical satellite deployments or spaceflight hardware**. Our 5G Core (17 Open5GS daemons) and post-quantum cryptography (native C `liboqs`) are 100% real production code. The RF physical channel is emulated using Linux kernel `tc netem` packet shaping, and orbital passes are modeled computationally. This is standard aerospace engineering methodology: control plane algorithms are validated in software-in-the-loop emulation before committing to physical satellite launches."

- **Q: "What is your next step to validate on physical hardware?"**  
  *Answer:* "In Phase 2 of our roadmap (Months 1–3, targeting TRL-5), we connect physical Software-Defined Radios (HackRF / USRP B210) via GNU Radio and ZMQ. In Phase 3 (Months 4–6, targeting TRL-6), we will test over-the-air 5G RAN using `srsRAN` on embedded ARM boards like Jetson and Raspberry Pi CM4. In Phase 4, we propose a CubeSat demonstration payload with IN-SPACe / ISRO."

### Category E: Architecture, Threat Modeling & Licensing
- **Q: "Why use Docker containers instead of dedicated hardware boxes?"**  
  *Answer:* "Two crucial defense reasons: First, **blast-radius containment**. In Docker CNFs, each satellite relay operates in an isolated Linux network namespace (`NET_ADMIN`). A compromised link cannot laterally escape to adjacent nodes, mitigating STRIDE Elevation of Privilege per `docs/THREAT_MODEL.md`. Second, **technology sovereignty**. Hardware boxes create reliance on foreign proprietary ASICs. Our software stack is 100% open under Apache 2.0 and portable to standard COTS ARM processors or India's indigenous Shakti/Vega RISC-V chips."

- **Q: "What license is this released under, and what threat model does it follow?"**  
  *Answer:* "RAKSHA-NET is open source under the permissive **Apache License 2.0**, enabling sovereign military, governmental, and academic adoption without commercial vendor lock-in. Our security architecture is strictly governed by [`docs/THREAT_MODEL.md`](file:///c:/Users/Rahul/Downloads/raksha-net-scaffold/raksha-net/docs/THREAT_MODEL.md), which implements the Microsoft STRIDE taxonomy covering Spoofing (GraphSAGE consensus), Tampering (AEAD tags), Repudiation (immutable event logging), Information Disclosure (ML-KEM-768), Denial of Service (CUSUM + 5% hysteresis), and Elevation of Privilege (network namespace isolation)."
