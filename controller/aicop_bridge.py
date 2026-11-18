"""
aicop_bridge.py
===============
AICOP-to-RAKSHA Cross-Layer Intelligence Bridge.
Integrates AICOP's O-RAN Near-RT RIC intelligence (GraphSAGE trust scoring,
TT-ACTS canary damping, and Pareto xApp conflict arbitration) directly into
RAKSHA-NET's 5G NTN satellite resilience controller.

Features:
  - 2-Layer Inductive GraphSAGE Trust Engine (trained on synthetic O-RAN FDI data).
  - Pareto Utility Arbitration between Traffic Steering (TS), Energy Saving (ES),
    and QoS xApps under corrupted telemetry / False Data Injection (FDI).
  - Cross-layer Threat Signal: Feeds terrestrial cell trust degradation directly
    into RAKSHA-NET's CUSUM anomaly engine for proactive satellite offloading.

Weights are trained by scripts/train_aicop_trust.py and stored in
models/aicop_trust_engine.npz. If the file is missing, a one-time training
run is triggered automatically on first import.
"""

import math
import pathlib
from typing import Dict, List, Tuple, Optional

try:
    import numpy as np
    _HAS_NP = True
except ImportError:
    np = None
    _HAS_NP = False

_MODELS_DIR = pathlib.Path(__file__).resolve().parent.parent / "models"
_WEIGHTS_PATH = _MODELS_DIR / "aicop_trust_engine.npz"

# ---------------------------------------------------------------------------
# Synthetic training data generator
# Features per cell: [reported_load, reported_sinr, ref_load, ref_sinr]
#   Normal cell  → reported ≈ reference  (small deviation)
#   FDI cell     → reported far from reference (large deviation)
# Label: 1 = trusted (low deviation), 0 = corrupted (high deviation)
# ---------------------------------------------------------------------------

def _generate_trust_training_data(n_samples: int = 2000, seed: int = 42):
    """Generate synthetic labeled training data for the cell trust engine."""
    rng = np.random.default_rng(seed)
    X, y = [], []
    half = n_samples // 2

    # Normal (trusted) cells: reported ≈ reference ± small noise
    for _ in range(half):
        ref_load = rng.uniform(0.1, 0.9)
        ref_sinr = rng.uniform(0.2, 1.0)
        rep_load = np.clip(ref_load + rng.normal(0, 0.04), 0.0, 1.0)
        rep_sinr = np.clip(ref_sinr + rng.normal(0, 0.04), 0.0, 1.0)
        X.append([rep_load, rep_sinr, ref_load, ref_sinr])
        y.append(1.0)  # trusted

    # FDI / compromised cells: reported far from reference
    for _ in range(half):
        ref_load = rng.uniform(0.1, 0.9)
        ref_sinr = rng.uniform(0.2, 1.0)
        # Inject large deviation: attacker inflates/deflates values
        dev_load = rng.choice([-1, 1]) * rng.uniform(0.25, 0.65)
        dev_sinr = rng.choice([-1, 1]) * rng.uniform(0.25, 0.65)
        rep_load = np.clip(ref_load + dev_load, 0.0, 1.0)
        rep_sinr = np.clip(ref_sinr + dev_sinr, 0.0, 1.0)
        X.append([rep_load, rep_sinr, ref_load, ref_sinr])
        y.append(0.0)  # corrupted

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)
    idx = rng.permutation(len(X))
    return X[idx], y[idx]


def _train_trust_engine(hidden: int = 16, epochs: int = 800, lr: float = 0.3,
                        seed: int = 42, n_samples: int = 2000) -> dict:
    """Train a 2-layer MLP on synthetic FDI trust data via SGD."""
    X, y = _generate_trust_training_data(n_samples=n_samples, seed=seed)
    rng = np.random.default_rng(seed)
    n_feat = X.shape[1]

    w1 = rng.normal(0, 0.3, (hidden, n_feat)).astype(np.float32)
    b1 = np.zeros(hidden, dtype=np.float32)
    w2 = rng.normal(0, 0.3, hidden).astype(np.float32)
    b2 = np.float32(0.0)

    def _relu(x): return np.maximum(0.0, x)
    def _sig(x):  return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

    n = len(X)
    for _ in range(epochs):
        h1 = _relu(w1 @ X.T + b1[:, None])
        logits = w2 @ h1 + b2
        preds = _sig(logits)
        eps = 1e-7
        d_logits = (preds - y) / n
        d_w2 = h1 @ d_logits
        d_b2 = float(np.sum(d_logits))
        d_h1 = np.outer(w2, d_logits)
        d_h1_pre = d_h1 * (h1 > 0).astype(np.float32)
        d_w1 = d_h1_pre @ X
        d_b1 = d_h1_pre.sum(axis=1)
        w1 -= lr * d_w1
        b1 -= lr * d_b1
        w2 -= lr * d_w2
        b2 -= lr * float(d_b2)

    return {"w1": w1, "w2": w2, "b1": b1, "b2": np.float32(b2)}


def _ensure_weights() -> bool:
    """Train and save weights if not present. Returns True if weights are ready."""
    if not _HAS_NP:
        return False
    if not _WEIGHTS_PATH.exists():
        print("[aicop_bridge] No trained weights found — training trust engine "
              f"(2000 samples, 800 epochs) → {_WEIGHTS_PATH}")
        _MODELS_DIR.mkdir(parents=True, exist_ok=True)
        weights = _train_trust_engine()
        np.savez(str(_WEIGHTS_PATH), **weights)
        print(f"[aicop_bridge] Weights saved → {_WEIGHTS_PATH}")
    return True


class GraphSAGETrustEngine:
    """
    2-Layer GraphSAGE Trust Model for Radio Access Nodes (gNBs / Cells).
    Evaluates reported metrics against spatial neighborhood reference to detect
    False Data Injection (FDI) and telemetry flapping without GPU overhead.

    Weights are loaded from models/aicop_trust_engine.npz (trained by
    scripts/train_aicop_trust.py or auto-generated on first use).
    """
    def __init__(self, in_features: int = 4, hidden_dim: int = 16):
        self.in_features = in_features
        self.hidden_dim = hidden_dim

        # Try to load trained weights; fall back to Xavier init if unavailable
        self._loaded = False
        if _ensure_weights():
            try:
                data = np.load(str(_WEIGHTS_PATH))
                # w1: (hidden, in_features) → transpose to (in_features, hidden) for _matmul
                self._W1_np = data["w1"]   # shape (hidden, in_features)
                self._W2_np = data["w2"]   # shape (hidden,)
                self._b1_np = data["b1"]   # shape (hidden,)
                self._b2_np = float(data["b2"])
                self.hidden_dim = self._W1_np.shape[0]
                self._loaded = True
                print(f"[GraphSAGETrustEngine] Loaded trained weights from {_WEIGHTS_PATH} "
                      f"(hidden={self.hidden_dim})")
            except Exception as exc:
                print(f"[GraphSAGETrustEngine] Weight load failed ({exc}); using Xavier init")

        if not self._loaded:
            # Xavier uniform fallback (better than Gaussian noise seed-42)
            import math as _math
            limit = _math.sqrt(6.0 / (in_features + hidden_dim))
            self._W1_np = None  # will use pure-python path
            self.W1 = [[((i * hidden_dim + j) % 17 - 8) * limit / 8
                         for j in range(hidden_dim)] for i in range(in_features)]
            self.W2 = [[(j % 11 - 5) * limit / 5] for j in range(hidden_dim)]
            self.b1 = [0.0] * hidden_dim
            self.b2 = 0.0

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(min(x, 15.0), -15.0)))

    def _infer_numpy(self, combined: "np.ndarray") -> float:
        """Single-node forward pass using trained numpy weights."""
        h1 = np.maximum(0.0, self._W1_np @ combined + self._b1_np)
        logit = float(self._W2_np @ h1 + self._b2_np)
        return 1.0 / (1.0 + math.exp(-max(min(logit, 15.0), -15.0)))

    def _infer_python(self, combined: List[float]) -> float:
        """Single-node forward pass using pure-Python fallback weights."""
        z1 = [sum(combined[i] * self.W1[i][j]
                  for i in range(self.in_features)) + self.b1[j]
              for j in range(self.hidden_dim)]
        h1 = [max(0.0, v) for v in z1]
        z2 = sum(h1[k] * self.W2[k][0] for k in range(self.hidden_dim)) + self.b2
        return self._sigmoid(z2)

    def infer_cell_trust(self, node_features: Dict[str, List[float]],
                         adjacency: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Runs 2-layer GraphSAGE mean aggregation over the cell graph.
        Features per node: [reported_load, reported_sinr, ref_load, ref_sinr]
        Returns: {cell_id: trust_score} where trust_score in [0.05, 1.00].
        """
        trust_scores = {}

        for node, feats in node_features.items():
            # --- GraphSAGE Layer 1: mean-aggregate 1-hop neighbours ---
            neighbors = adjacency.get(node, [])
            if neighbors:
                agg = [
                    sum(node_features[nbr][f] for nbr in neighbors) / len(neighbors)
                    for f in range(self.in_features)
                ]
            else:
                agg = feats[:]

            # Concat [self || agg] then mean-pool to keep in_features dim
            combined = [(feats[k] + agg[k]) * 0.5 for k in range(self.in_features)]

            # --- Layer 2: forward pass (trained weights if available) ---
            if self._loaded and _HAS_NP:
                x_np = np.array(combined, dtype=np.float32)
                base_score = self._infer_numpy(x_np)
            else:
                base_score = self._infer_python(combined)

            # --- Deviation penalty: exp(-β·||x_rep - x_ref||₁) ---
            dev = abs(feats[0] - feats[2]) + abs(feats[1] - feats[3])
            trust_raw = base_score * math.exp(-2.5 * dev)
            trust_scores[node] = round(max(0.05, min(1.0, trust_raw)), 4)

        return trust_scores


class AICOPPolicyCoordinator:
    """
    Coordinates xApp decisions (Traffic Steering, Energy Saving, and QoS)
    using Trust-Weighted Pareto Utility Arbitration.
    """
    def __init__(self, sleep_load_thresh: float = 0.20):
        self.sleep_load_thresh = sleep_load_thresh
        self.gnb_states = {}  # {cell_id: 'ON' | 'SLEEP'}
        self.flapping_history = {}

    def arbitrate_cell(self, cell_id: str, load: float, sinr: float, trust: float) -> Dict[str, any]:
        """
        Arbitrates conflicting policies for an edge gNB.
        Returns coordinated action and SLA safety margin.
        """
        # 1. Individual xApp Proposals
        # TS xApp wants to steer traffic away if load is high
        ts_delta = max(-0.3, min(0.3, (0.50 - load) * 0.6))
        
        # ES xApp wants to put under-utilized cells into sleep
        es_delta = -0.5 if (load < self.sleep_load_thresh and trust > 0.60) else 0.0
        
        # QoS xApp wants capacity boost if SINR is poor or load high
        pred_latency_risk = (1.0 - sinr) + load
        qos_delta = max(0.0, min(0.4, (pred_latency_risk - 0.9) * 0.7))

        # 2. Conflict Veto (Pacifista Rule)
        # If TS wants to steer traffic TO this cell, but ES wants to SLEEP it -> Veto ES!
        cross_conflict = (ts_delta > 0.05) and (es_delta < 0.0)
        if cross_conflict:
            es_delta = 0.0
            ts_delta *= 0.5  # Dampen TS

        # 3. Trust-Weighted Utility Blend
        # Under low trust (corrupted telemetry), veto drastic actions (both sleep & aggressive steering)
        effective_ts = ts_delta * trust
        effective_es = es_delta * (trust ** 2)  # Quadratic penalty on power down under suspicious data
        
        # Determine cell power state
        if effective_es < -0.3 and trust >= 0.70:
            new_state = "SLEEP"
        else:
            new_state = "ON"
        self.gnb_states[cell_id] = new_state

        # Compute SLA violation risk
        sla_violation_risk = max(0.0, (load + (0.3 if new_state == "SLEEP" else 0.0)) - 0.85)

        return {
            "cell_id": cell_id,
            "state": new_state,
            "effective_ts": round(effective_ts, 3),
            "effective_es": round(effective_es, 3),
            "qos_boost": round(qos_delta, 3),
            "trust": trust,
            "sla_risk": round(sla_violation_risk, 3),
            "is_corrupted": (trust < 0.40)
        }


class UnifiedAICOPBridge:
    """
    High-level facade connecting AICOP O-RAN RAN telemetry to RAKSHA-NET NTN Controller.
    """
    def __init__(self, num_cells: int = 12):
        self.num_cells = num_cells
        self.trust_engine = GraphSAGETrustEngine()
        self.coordinator = AICOPPolicyCoordinator()

        # Build 12-cell planar grid topology (3 rows × 4 columns).
        # Layout:
        #   gNB-01  gNB-02  gNB-03  gNB-04
        #   gNB-05  gNB-06  gNB-07  gNB-08
        #   gNB-09  gNB-10  gNB-11  gNB-12
        #
        # Each cell is adjacent to its N/S/E/W neighbours.
        # Degree distribution: 4 corners (d=2), 8 edge/interior (d=3 or d=4).
        # |E| = 17,  mean degree ≈ 2.83
        rows, cols = 3, 4
        self.adjacency = {}
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                cid = f"gNB-{idx + 1:02d}"
                nbrs = []
                if r > 0:          nbrs.append(f"gNB-{(r-1)*cols + c + 1:02d}")   # north
                if r < rows - 1:   nbrs.append(f"gNB-{(r+1)*cols + c + 1:02d}")   # south
                if c > 0:          nbrs.append(f"gNB-{r*cols + (c-1) + 1:02d}")    # west
                if c < cols - 1:   nbrs.append(f"gNB-{r*cols + (c+1) + 1:02d}")    # east
                self.adjacency[cid] = nbrs

    def evaluate_ran_fleet(self, telemetry_batch: Dict[str, List[float]]) -> Tuple[Dict[str, any], float]:
        """
        Ingests telemetry from all terrestrial gNBs:
          telemetry_batch: {cell_id: [reported_load, reported_sinr, ref_load, ref_sinr]}
        Returns:
          - detailed decisions per cell
          - aggregate terrestrial degradation signal [0.0 to 1.0] for RAKSHA-NET
        """
        # 1. Compute GraphSAGE trust
        trust_scores = self.trust_engine.infer_cell_trust(telemetry_batch, self.adjacency)

        # 2. Run Pareto xApp policy coordination per cell
        decisions = {}
        corrupted_count = 0
        total_sla_risk = 0.0

        for cid, feats in telemetry_batch.items():
            t_score = trust_scores.get(cid, 0.95)
            dec = self.coordinator.arbitrate_cell(cid, load=feats[0], sinr=feats[1], trust=t_score)
            decisions[cid] = dec
            if dec["is_corrupted"]:
                corrupted_count += 1
            total_sla_risk += dec["sla_risk"]

        # 3. Compute cross-layer degradation score
        # Higher score means terrestrial RAN is severely corrupted / overloaded
        ran_degradation = min(1.0, (corrupted_count / max(1, self.num_cells)) * 1.5 + (total_sla_risk / max(1, self.num_cells)))
        return decisions, round(ran_degradation, 4)
