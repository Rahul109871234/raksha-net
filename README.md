# RAKSHA-NET — AI-Driven Quantum-Safe SAGIN Defense Communication Prototype

PDPM IIITDM Jabalpur — Sovereign Technology for India
Results from statistical simulation.

[![Tests](https://img.shields.io/badge/tests-53%20passed-22c55e)](tests/)
[![Backend](https://img.shields.io/badge/crypto-MOCK%20(liboqs%20optional)-f59e0b)](controller/security_engine.py)
[![Python](https://img.shields.io/badge/python-3.10%2B-3b82f6)](requirements.txt)

## Demo Story

```
Normal → link degradation/jamming → anomaly detected → trust drops
       → route switches LEO-1 → LEO-2 → degraded link isolated
       → ML-KEM re-key / PQC session → communication restored
```

Impaired LEO-profile links are rate-limited to 8-50 Mbit/s;
results for those are in results/summary.md.

- **Crypto-Agility Engine:** Dynamically chooses between ChaCha20 and AES-GCM (ChaCha20 is for CPUs without AES acceleration like ARM edge nodes). Benchmarks in `results/crypto_benchmark.md` show per-suite AEAD throughput of ~55.6–57.4 MB/s for ChaCha20-Poly1305 and ~74.1–74.3 MB/s for AES-256-GCM.
- **AI vs Static Routing:** The AI routing maintains a PDR of 0.970 during link degradation, while static routing drops to 0.325 in 20-trial emulated runs (see `results/summary.md`). In large-scale 100-seed Monte Carlo evaluation (`results/batch_100_seeds_experiment.csv`), AICOP restores PDR from 29.6% to 96.8% (+67.16 pp).

## Quickstart — Simulated Mode (No Docker, No Hardware)

```bash
# Install dependencies
pip install -r requirements.txt

# Run single verbose scenario (5 scenes)
python -m scripts.run_scenario --verbose

# Run 20-trial experiment with AI vs static comparison
python -m scripts.run_scenario --trials 20 --csv results/experiment.csv --compare-static

# Generate report + charts
python scripts/make_report.py --csv results/experiment.csv

# Run all tests (53 tests parameterized)
python run_all_tests.py
```

## Quickstart — Live Dashboard

```bash
# Terminal 1: start controller daemon
python -m controller.controller_daemon --backend sim

# Terminal 2: start dashboard (opens in browser)
streamlit run dashboard/app.py
```

Then use the sidebar to:
- **SIMULATE LINK ATTACK** → watch route switch + security adaptation
- **RESTORE LINK** → watch recovery + re-authentication
- **RUN 20-TRIAL EXPERIMENT** → see results in the Results tab

## Docker Mode (Real tc netem)

See [`docs/DOCKER_SETUP.md`](docs/DOCKER_SETUP.md) for full setup.

```bash
# Requires Docker + WSL2 on Windows, or Linux
make docker-up
python -m scripts.run_scenario --backend real --verbose
make docker-down
```

## AICOP Proprietary Integration (Optional)

To run the controller using the AICOP checkpoint instead of the default GraphSAGE fallback, simply point the engine to your checkpoint via environment variables:

```bash
AICOP_CKPT=/path/to/your/model.pt \
AICOP_MODULE=/path/to/your/infer.py \
python -m scripts.run_scenario --backend real --detector aicop
```

## Layout

```
common/interfaces.py          Data contracts (LinkTelemetry, Route, RouteDecision, SecurityEvent)
emulator/network_emulator.py  Statistical link model + ramp transitions + jitter bursts
emulator/real_backend.py      Docker/tc-netem real backend
controller/anomaly_engine.py  HeuristicDetector (sliding window) | GraphSAGEFallback | AICOP hook
controller/trust_engine.py    EWMA weighted trust
controller/route_engine.py    Route score + hysteresis
controller/security_engine.py ML-KEM-768 (liboqs) or MOCK; AEAD; HKDF; REKEY; isolation
controller/crypto_agility.py  Bandwidth/threat-based suite selection: ML-KEM-768, X25519+ML-KEM hybrid, AES-256-GCM, ChaCha20-Poly1305
scripts/benchmark_crypto.py   Per-suite handshake time/size + AEAD throughput -> results/crypto_benchmark.md
controller/controller.py      Full control cycle (anomaly->trust->route->security->send)
controller/controller_daemon.py Background daemon writing live_state.json
security/qkd_mock.py          QKD interface (Simulated interface)
dashboard/app.py              Streamlit live dashboard
scripts/run_scenario.py       5-scene demo + 20-trial experiment + static baseline
scripts/train_detector.py     Train GraphSAGE-style fallback on synthetic data
scripts/make_report.py        Generate summary.md + PNG charts from CSV
scripts/install_liboqs.sh     Install real liboqs (Ubuntu/WSL2)
scripts/smoke.sh              Smoke test: run scenario, assert route switch + recovery
docker/docker-compose.yml     Topology A--GW--{LEO1,LEO2}--B
docs/ARCHITECTURE.md          Mermaid 5-layer SAGIN diagram + module interfaces
docs/DOCKER_SETUP.md          Docker + WSL2 + tc netem setup guide
docs/OPEN5GS_ATTACH.md        Open5GS/srsRAN integration hook
docs/DEMO_SCRIPT.md           4-minute spoken script + Q&A cheat sheet
docs/LIMITATIONS.md           System Limitations
docs/PROGRESS.md              Running log: done, blocked, measured numbers
```

## Make Targets

```bash
make test              # pytest -q tests/
make scenario          # verbose single run
make experiment        # 20 trials + CSV + report
make dashboard         # start daemon + Streamlit
make demo-sim          # one-command demo (sim mode)
make docker-up         # docker compose up --build -d
make docker-down       # docker compose down
make train-detector    # train GraphSAGE fallback
make smoke             # smoke test
```
