# Contributing to RAKSHA-NET

Thank you for your interest in contributing to RAKSHA-NET! This project is an open research prototype for sovereign 5G/NTN cyber-resilience.

---

## 1. Development Environment Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Rahul109871234/raksha-net.git
   cd raksha-net
   ```

2. **Create Virtual Environment & Install Dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Run the Test Suite:**
   ```bash
   python run_all_tests.py
   ```
   All 53 tests must pass before opening a Pull Request.

---

## 2. Code Standards & Architecture Guidelines

- **Reproducibility First:** All experimental claims must be backed by runnable scripts in `scripts/` that output reproducible CSVs into `results/`.
- **Zero Hallucinated Numbers:** Never hardcode experimental outputs or replace measured performance with synthetic random variables. Use `time.perf_counter()` for hardware timing and clearly label discrete-event simulation models.
- **Crypto-Agility:** Cryptographic primitives must cleanly degrade to `MOCK` when native C libraries (`liboqs`) are absent, while supporting hardware execution in production Linux environments.
- **Minimal Dependencies:** Core algorithms (GraphSAGE, trust scoring, routing) should rely on standard scientific libraries (`numpy`, `scipy`) without requiring proprietary cloud endpoints or heavy GPU frameworks for inference.

---

## 3. Pull Request Process

1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Write unit tests for new logic in `tests/`.
3. Verify that `python run_all_tests.py` passes 100%.
4. Commit your changes with clear, semantic commit messages:
   ```bash
   git commit -m "feat(routing): add reactive BFD hold-timer baseline"
   ```
5. Open a Pull Request targeting `main`. Describe the exact problem solved and link any relevant experimental logs.
