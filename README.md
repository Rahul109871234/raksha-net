# RAKSHA-NET: Autonomous Cross-Layer Resilience & Post-Quantum Cryptography for 5G/NTN

**PDPM Indian Institute of Information Technology, Design & Manufacturing (IIITDM), Jabalpur**  
*Department of Electronics & Communication Engineering*  
*Authors:* G. Rahul Reddy (`24BEC038`) & Dr. Satish Kumar Tiwari (`stiwari@iiitdmj.ac.in`)  

[![CI Test Suite](https://github.com/Rahul109871234/raksha-net/actions/workflows/ci.yml/badge.svg)](https://github.com/Rahul109871234/raksha-net/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Threat Model](https://img.shields.io/badge/Security-Threat%20Model-red.svg)](docs/THREAT_MODEL.md)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](requirements.txt)
[![Backend: liboqs / MOCK](https://img.shields.io/badge/crypto-liboqs%20%7C%20MOCK-orange)](controller/security_engine.py)
[![TRL: 4 (Testbed Validation)](https://img.shields.io/badge/TRL-4%20(Testbed%20Validation)-green.svg)](docs/WHITEPAPER_AICOP_RAKSHA.md)

---

## 1. Research Scope & Emulation Notice

> **Scientific Disclosure (TRL-4 Lab Prototype):**  
> RAKSHA-NET is an open-source software-defined resilience controller for 5G and Non-Terrestrial Network (NTN) testbeds.
> - **Network Model:** Evaluated via discrete-event state machine transitions (`emulator/network_emulator.py`) and containerized Linux kernel network emulation (`docker/` with `tc netem` delay, loss, and jitter shaping).
> - **Cryptographic Execution:** Implements native C **NIST FIPS 203 ML-KEM-768** (`liboqs`) and hybrid IKEv2 (RFC 9370) key establishment on supported Linux platforms, with a graceful `MOCK` fallback for non-compiled / Windows environments.
> - **Physical Limitations:** These benchmarks represent software-in-the-loop and network-emulated evaluations, not physical satellite orbital payloads, over-the-air RF defense deployments, or commercial base station silicon.

---

## 2. Core Architecture: The Multi-Baseline Comparison

Traditional networks either lack automated failover (naive static) or rely on reactive **Bidirectional Forwarding Detection (BFD) / Hold-Timer Timeouts** (RFC 5880 / 3GPP TS 38.300), which suffer severe transient packet loss while waiting for loss counters to expire.

RAKSHA-NET combines O-RAN Near-RT RIC edge intelligence (AICOP inductive GraphSAGE) with proactive change-point detection (Page's CUSUM), achieving sub-second path healing and zero route flapping:

```
Normal Link → Jamming Injected (70% Loss) → Cross-Layer Telemetry Drift
  ├─ Naive Static:       Never reroutes → Collapses to 0.325 PDR (67.5% packet loss)
  ├─ Reactive BFD:       Wait-to-expire timeout (1.5s–2.8s) → Recovers late (0.740–0.760 PDR)
  └─ Proactive AICOP:    Joint Anomaly Score >= 0.60 → Reroutes in ~188ms → Restores to 0.970 PDR
```

### Empirical Baseline Comparison (n=20 Paired Trials)

| Routing Approach | Detection Mechanism | Outage Window Before Failover | Sustained Attack Window PDR | Net Availability Gain vs Static |
| :--- | :--- | :---: | :---: | :---: |
| **Static Routing** | None (Manual Intervention) | $\infty$ (No failover) | **0.325** ($67.5\%$ loss) | Baseline ($0.0\text{ pp}$) |
| **Reactive BFD (3GPP standard)** | Loss hold-timer timeout ($15\text{ ticks}$) | $1,500\text{--}2,800\text{ ms}$ | **0.760** ($24.0\%$ loss) | **$+43.5\text{ pp}$** |
| **RAKSHA-NET (AICOP Proactive)** | Multi-parameter drift + CUSUM | **$188\text{--}200\text{ ms}$** | **0.970** ($3.0\%$ loss) | **$+64.5\text{ pp}$** ($+21.0\text{ pp}$ over BFD) |

*Large-Scale 100-Seed Batch (`results/batch_100_seeds_experiment.csv`):* PDR restored from $29.6 \pm 4.8\%$ to $96.8 \pm 0.4\%$ ($+67.16\text{ pp}$ net gain; $95\%\text{ CI: } [+66.19, +68.14]\text{ pp}$).

---

## 3. Cryptographic Agility & Post-Quantum Security

Conforming to **IETF RFC 9370** (*Multiple Key Exchanges in IKEv2*), the controller dynamically selects cryptographic suites based on link threat levels and available bandwidth:

- **Threat Level Elevated:** Deploys Hybrid Key Exchange (**X25519 + NIST ML-KEM-768** via HKDF-SHA256). Even if classical discrete logs are retroactively broken by quantum adversaries (*Harvest Now, Decrypt Later*), lattice-based ML-KEM guarantees forward secrecy.
- **AEAD Selection Policy:**
  - High Bandwidth ($\ge 30\text{ Mbps}$): **AES-256-GCM** (~$74.1\text{--}74.3\text{ MB/s}$ on x86_64 with AES-NI instructions).
  - Low Bandwidth / Constrained Link ($< 30\text{ Mbps}$): **ChaCha20-Poly1305** (~$55.6\text{--}57.4\text{ MB/s}$).  
    *Hardware Note:* ChaCha20-Poly1305 is architecturally designated for embedded ARM/RISC-V cores lacking dedicated AES hardware acceleration (RFC 8439), where software AES suffers severe cache-timing vulnerabilities.
- **Cryptographic Backend:**
  - **Linux / Docker:** Native C compiled `liboqs` (v0.10.0+) for hardware-timed key encapsulation ($0.045\text{ ms}$) and hybrid rekeying ($0.48\text{ ms}$).
  - **Windows / Bare Pip:** Self-contained `MOCK` backend for functional and state-machine verification without C compilation barriers.

---

## 4. Fully Reproducible Open-Source AICOP Integration

Unlike implementations requiring external proprietary checkpoints, RAKSHA-NET includes the complete, self-contained **2-Layer Inductive GraphSAGE Trust Engine and Pareto Arbitrator**:
- **Code:** [`controller/aicop_bridge.py`](controller/aicop_bridge.py)
- **Pre-trained Weights:** [`models/aicop_trust_engine.npz`](models/aicop_trust_engine.npz) and [`models/graphsage_fallback.npz`](models/graphsage_fallback.npz)
- **Training Harness:** [`scripts/train_detector.py`](scripts/train_detector.py) and [`scripts/run_detection_ablation.py`](scripts/run_detection_ablation.py)

Running `--detector aicop` or `--detector graphsage` operates 100% out-of-the-box using the verified NumPy model.

---

## 5. Quickstart & Step-by-Step Reproduction

### 5.1 Local Simulation Mode (Zero External Dependencies)

```bash
# 1. Clone repository
git clone https://github.com/Rahul109871234/raksha-net.git
cd raksha-net

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run full automated test suite (53 tests parameterized)
python run_all_tests.py

# 4. Run single verbose 5-scene scenario
python -m scripts.run_scenario --verbose

# 5. Run 20-trial multi-baseline comparison (AI vs BFD vs Static)
python -m scripts.run_scenario --trials 20 --csv results/experiment.csv --compare-static

# 6. Generate experiment report and charts
python scripts/make_report.py --csv results/experiment.csv
```

### 5.2 Live Dashboard

```bash
# Terminal 1: Launch controller daemon
python -m controller.controller_daemon --backend sim

# Terminal 2: Start Streamlit GUI
streamlit run dashboard/app.py
```

### 5.3 Docker Mode (Real Linux Kernel `tc netem`)

Requires Docker & Linux / WSL2:
```bash
make docker-up
python -m scripts.run_scenario --backend real --verbose
make docker-down
```

---

## 6. Repository Layout & Documentation

```
├── .github/workflows/ci.yml       # Automated GitHub Actions CI test suite
├── LICENSE                        # Apache 2.0 open-source license
├── CONTRIBUTING.md                # Development guidelines & PR checklist
├── CITATION.cff                   # Academic citation metadata
├── SECURITY.md                    # Coordinated vulnerability disclosure policy
├── common/interfaces.py           # Data contracts (LinkTelemetry, RouteDecision, SecurityEvent)
├── controller/
│   ├── aicop_bridge.py            # Inductive GraphSAGE trust engine & Pareto coordinator
│   ├── anomaly_engine.py          # Sliding EWMA, Page's CUSUM, and GNN detectors
│   ├── crypto_agility.py          # Dynamic 5-suite AEAD & PQC selector
│   ├── route_engine.py            # AI multi-criteria optimizer & Reactive BFD baseline
│   ├── security_engine.py         # NIST ML-KEM-768 (liboqs / MOCK) & hybrid AEAD
│   └── unified_controller.py      # Master cross-layer closed loop
├── emulator/
│   ├── network_emulator.py        # Statistical link model + ramp transitions
│   └── real_backend.py            # Docker tc netem interface
├── models/                        # Pre-trained open-source weights (NumPy .npz)
├── docs/
│   ├── THREAT_MODEL.md            # Comprehensive STRIDE security & crypto review
│   ├── WHITEPAPER_AICOP_RAKSHA.md # 3GPP/O-RAN reference technical specification
│   ├── ARCHITECTURE.md            # Detailed 5-tier SAGIN topology diagram
│   └── DOCKER_SETUP.md            # Linux kernel emulation setup guide
├── results/                       # Master CSV datasets, benchmark charts, and whitepaper PDF
├── run_all_tests.py               # Self-contained 53-test test runner
└── scripts/                       # Reproducible Monte Carlo batches & ablation scripts
```

---

## 7. License & Academic Attribution

This project is licensed under the **Apache License 2.0** — see [`LICENSE`](LICENSE) for details.

If you cite or build upon this architecture in your academic work, please use:
```bibtex
@misc{reddy2026rakshanet,
  author = {G. Rahul Reddy and Dr. Satish Kumar Tiwari},
  title = {RAKSHA-NET: A Unified Cross-Layer Architecture for Autonomous Telemetry Trust, Near-RT O-RAN Policy Coordination, and Post-Quantum 5G Non-Terrestrial Network Resilience},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/Rahul109871234/raksha-net}}
}
```
