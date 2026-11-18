# RAKSHA-NET Makefile
# Usage: make <target>
# Windows (PowerShell): use `nmake` or run commands directly.
# Prefer running in Git Bash / WSL for best compatibility.

PYTHON  ?= python
PYTEST  ?= pytest
STREAMLIT ?= streamlit
RESULTS_DIR = results
RUNS_DIR = runs

.PHONY: all test scenario experiment dashboard docker-up docker-down demo-sim clean bench-crypto

all: test

## ── Development ──────────────────────────────────────────────────────────────

test:
	$(PYTEST) -q tests/

scenario:
	$(PYTHON) -m scripts.run_scenario --verbose

experiment:
	@mkdir -p $(RESULTS_DIR)
	$(PYTHON) -m scripts.run_scenario \
		--trials 20 \
		--csv $(RESULTS_DIR)/experiment.csv \
		--detector $(or $(DETECTOR),heuristic) \
		--compare-static
	$(PYTHON) scripts/make_report.py --csv $(RESULTS_DIR)/experiment.csv

dashboard:
	@mkdir -p $(RUNS_DIR)
	$(PYTHON) -m controller.controller_daemon &
	$(STREAMLIT) run dashboard/app.py --server.headless true

demo-sim:
	@mkdir -p $(RUNS_DIR)
	@echo "Starting RAKSHA-NET demo (sim mode)..."
	$(PYTHON) -m controller.controller_daemon --backend sim &
	sleep 2
	$(STREAMLIT) run dashboard/app.py

## ── Docker ───────────────────────────────────────────────────────────────────

docker-up:
	docker compose -f docker/docker-compose.yml up --build -d

docker-down:
	docker compose -f docker/docker-compose.yml down

docker-scenario:
	docker compose -f docker/docker-compose.yml exec controller \
		python -m scripts.run_scenario --backend real --trials 1 --verbose

## ── Utilities ────────────────────────────────────────────────────────────────

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; \
	find . -name "*.pyc" -delete 2>/dev/null; \
	rm -rf $(RESULTS_DIR)/*.csv $(RUNS_DIR)/*.json $(RUNS_DIR)/*.jsonl; \
	echo "Cleaned."

train-detector:
	$(PYTHON) scripts/train_detector.py

bench-crypto:
	$(PYTHON) -m scripts.benchmark_crypto --n 200

smoke:
	bash scripts/smoke.sh
