"""
scripts/run_detection_ablation.py
==================================
Empirical, Reproducible Detection & Algorithmic Ablation Study.
Directly generates every row and column of the Whitepaper's Table 4.2:
  1. Tuned Spatial Median Residual
  2. 2-Layer MLP (No Graph Aggregation, 4 features)
  3. GraphSAGE-Only (Learned GNN, 8 concatenated features matching Eq. 1-2)
  4. Deviation Penalty-Only (Heuristic exp(-beta * ||x_rep - x_ref||_1))
  5. Unified AICOP GraphSAGE + Penalty (Ours)

Key Scientific Rigor Improvements:
  - Reference vector x_v^ref is NON-ORACLE: derived online from temporal EWMA
    and spatial neighbor consensus (no access to true latent unperturbed load).
  - GraphSAGE architecture strictly matches Eq. 1 & 2: W1 in R^(16x8) operates on
    concatenated self-features and neighbor mean aggregate [x_v || mean(x_u)].
  - Strict Held-Out Evaluation: GNN and MLP are trained ONLY on gross FDI attacks.
    Stealth attacks (delta <= 0.15 = 2.5 sigma) and multi-cell collusion are strictly
    held out from training to test genuine generalization.
  - Chronological 70/30 split across 2,000 epochs (12 cells x 2,000 epochs = 24,000 cell-epochs):
    1,400 warmup epochs, 600 evaluation epochs (7,200 cell-epochs).
  - True cell-epoch prevalence is measured and printed explicitly.

Saves results to results/detection_ablation_results.csv.
"""

from __future__ import annotations
import os
import sys
import pathlib
import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

RESULTS_DIR = pathlib.Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# 3x4 Planar Grid Topology (12 cells, 17 edges)
GRID_ADJACENCY = {
    "gNB-01": ["gNB-02", "gNB-05"],
    "gNB-02": ["gNB-01", "gNB-03", "gNB-06"],
    "gNB-03": ["gNB-02", "gNB-04", "gNB-07"],
    "gNB-04": ["gNB-03", "gNB-08"],
    "gNB-05": ["gNB-01", "gNB-06", "gNB-09"],
    "gNB-06": ["gNB-02", "gNB-05", "gNB-07", "gNB-10"],
    "gNB-07": ["gNB-03", "gNB-06", "gNB-08", "gNB-11"],
    "gNB-08": ["gNB-04", "gNB-07", "gNB-12"],
    "gNB-09": ["gNB-05", "gNB-10"],
    "gNB-10": ["gNB-06", "gNB-09", "gNB-11"],
    "gNB-11": ["gNB-07", "gNB-10", "gNB-12"],
    "gNB-12": ["gNB-08", "gNB-11"],
}
NODE_LIST = sorted(list(GRID_ADJACENCY.keys()))
N_NODES = len(NODE_LIST)
NODE_TO_IDX = {nid: i for i, nid in enumerate(NODE_LIST)}

SEEDS = [42, 107, 211, 389, 523, 647, 761, 883, 941, 1039]


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def relu(x):
    return np.maximum(0.0, x)


def generate_train_dataset(n_samples=4000, seed=42):
    """
    Generates balanced training data for neural models (50% honest, 50% gross FDI).
    Stealth and collusion attacks are STRICTLY HELD OUT from training.
    Returns:
      X_self: shape (N, 4) for MLP: [rep_l, rep_s, ref_l, ref_s]
      X_sage: shape (N, 8) for GraphSAGE: [x_v || x_nbr_mean] matching Eq. 1
      y: shape (N,) where 1 = honest/trusted, 0 = attack/untrusted
    """
    rng = np.random.default_rng(seed)
    X_self, X_sage, y = [], [], []
    half = n_samples // 2

    # 1. Honest samples (y = 1.0)
    for _ in range(half):
        ref_l = rng.uniform(0.15, 0.85)
        ref_s = rng.uniform(0.30, 0.90)
        rep_l = float(np.clip(ref_l + rng.normal(0, 0.04), 0.0, 1.0))
        rep_s = float(np.clip(ref_s + rng.normal(0, 0.03), 0.0, 1.0))
        x_v = [rep_l, rep_s, ref_l, ref_s]

        # Simulated honest neighbor mean
        nbr_ref_l = float(np.clip(ref_l + rng.normal(0, 0.05), 0.10, 0.90))
        nbr_ref_s = float(np.clip(ref_s + rng.normal(0, 0.04), 0.20, 0.95))
        nbr_rep_l = float(np.clip(nbr_ref_l + rng.normal(0, 0.04), 0.0, 1.0))
        nbr_rep_s = float(np.clip(nbr_ref_s + rng.normal(0, 0.03), 0.0, 1.0))
        x_nbr = [nbr_rep_l, nbr_rep_s, nbr_ref_l, nbr_ref_s]

        X_self.append(x_v)
        X_sage.append(x_v + x_nbr)
        y.append(1.0)

    # 2. Attack samples: Gross FDI only (y = 0.0)
    # Stealth and collusion are held out for testing
    for _ in range(half):
        ref_l = rng.uniform(0.15, 0.85)
        ref_s = rng.uniform(0.30, 0.90)
        d_l = rng.choice([-1, 1]) * rng.uniform(0.25, 0.60)
        d_s = rng.choice([-1, 1]) * rng.uniform(0.20, 0.50)
        rep_l = float(np.clip(ref_l + d_l, 0.0, 1.0))
        rep_s = float(np.clip(ref_s + d_s, 0.0, 1.0))
        x_v = [rep_l, rep_s, ref_l, ref_s]

        # Honest neighbors during standard single-cell gross FDI
        nbr_ref_l = float(np.clip(ref_l + rng.normal(0, 0.05), 0.10, 0.90))
        nbr_ref_s = float(np.clip(ref_s + rng.normal(0, 0.04), 0.20, 0.95))
        nbr_rep_l = float(np.clip(nbr_ref_l + rng.normal(0, 0.04), 0.0, 1.0))
        nbr_rep_s = float(np.clip(nbr_ref_s + rng.normal(0, 0.03), 0.0, 1.0))
        x_nbr = [nbr_rep_l, nbr_rep_s, nbr_ref_l, nbr_ref_s]

        X_self.append(x_v)
        X_sage.append(x_v + x_nbr)
        y.append(0.0)

    X_self = np.array(X_self, dtype=np.float32)
    X_sage = np.array(X_sage, dtype=np.float32)
    y = np.array(y, dtype=np.float32)

    perm = rng.permutation(len(y))
    return X_self[perm], X_sage[perm], y[perm]


class VectorizedNeuralNet:
    """Vectorized 2-layer Neural Network matching Eq. 1 & 2 in pure NumPy."""
    def __init__(self, in_features: int, hidden: int = 16, lr: float = 0.02, epochs: int = 350):
        self.in_features = in_features
        self.hidden = hidden
        self.lr = lr
        self.epochs = epochs
        self.w1 = None  # shape (hidden, in_features)
        self.b1 = None  # shape (hidden,)
        self.w2 = None  # shape (hidden,)
        self.b2 = None  # scalar

    def fit(self, X: np.ndarray, y: np.ndarray, seed: int = 42):
        rng = np.random.default_rng(seed)
        limit1 = np.sqrt(6.0 / (self.in_features + self.hidden))
        self.w1 = rng.uniform(-limit1, limit1, (self.hidden, self.in_features)).astype(np.float32)
        self.b1 = np.zeros(self.hidden, dtype=np.float32)

        limit2 = np.sqrt(6.0 / (self.hidden + 1))
        self.w2 = rng.uniform(-limit2, limit2, self.hidden).astype(np.float32)
        self.b2 = np.float32(0.0)

        n = len(X)
        v_w1, v_b1, v_w2, v_b2 = 0.0, 0.0, 0.0, 0.0
        beta_mom = 0.9

        for _ in range(self.epochs):
            # Forward pass
            h1 = relu(self.w1 @ X.T + self.b1[:, None])  # (hidden, N)
            logits = self.w2 @ h1 + self.b2              # (N,)
            preds = sigmoid(logits)                      # (N,)

            # Gradient of binary cross entropy
            d_logits = (preds - y) / n
            d_w2 = h1 @ d_logits
            d_b2 = float(np.sum(d_logits))

            d_h1 = np.outer(self.w2, d_logits) * (h1 > 0).astype(np.float32)
            d_w1 = d_h1 @ X
            d_b1 = d_h1.sum(axis=1)

            # Momentum updates
            v_w1 = beta_mom * v_w1 + (1.0 - beta_mom) * d_w1
            v_b1 = beta_mom * v_b1 + (1.0 - beta_mom) * d_b1
            v_w2 = beta_mom * v_w2 + (1.0 - beta_mom) * d_w2
            v_b2 = beta_mom * v_b2 + (1.0 - beta_mom) * d_b2

            self.w1 -= self.lr * v_w1
            self.b1 -= self.lr * v_b1
            self.w2 -= self.lr * v_w2
            self.b2 -= self.lr * np.float32(v_b2)

    def predict_trust(self, X: np.ndarray) -> np.ndarray:
        """Computes sigma(z_v) trust logit projection (Eq. 2)."""
        h1 = relu(self.w1 @ X.T + self.b1[:, None])
        logits = self.w2 @ h1 + self.b2
        return sigmoid(logits)


def generate_fleet_eval_trajectory(num_epochs=2000, seed=42):
    """
    Generates realistic 12-cell O-RAN trajectory over space and time.
    Calculates reference load and SINR purely from observable signals:
      - Temporal EWMA of past reports
      - Spatial neighbor consensus (median of neighbors)
    NO ORACLE ACCESS TO TRUE LATENT LOAD.
    """
    rng = np.random.default_rng(seed)

    # Underlying latent physical load profile (unobserved)
    base_load = rng.uniform(0.40, 0.65, size=N_NODES)
    base_sinr = rng.uniform(0.70, 0.85, size=N_NODES)

    rep_loads = np.zeros((num_epochs, N_NODES), dtype=np.float32)
    rep_sinrs = np.zeros((num_epochs, N_NODES), dtype=np.float32)
    ref_loads = np.zeros((num_epochs, N_NODES), dtype=np.float32)
    ref_sinrs = np.zeros((num_epochs, N_NODES), dtype=np.float32)

    labels = np.zeros((num_epochs, N_NODES), dtype=np.float32)  # 1 = attack, 0 = nominal
    attack_types = np.zeros((num_epochs, N_NODES), dtype=np.int32)  # 0=norm, 1=gross, 2=stealth, 3=collusion

    # Online observable EWMA trackers
    ewma_l = np.copy(base_load)
    ewma_s = np.copy(base_sinr)

    for ep in range(num_epochs):
        # Latent true state with physical jitter (sigma = 0.05)
        true_l = np.clip(base_load + rng.normal(0, 0.05, size=N_NODES), 0.10, 0.90)
        true_s = np.clip(base_sinr + rng.normal(0, 0.03, size=N_NODES), 0.20, 0.95)

        # Baseline reported telemetry (honest cells)
        r_l = np.clip(true_l + rng.normal(0, 0.02, size=N_NODES), 0.0, 1.0)
        r_s = np.clip(true_s + rng.normal(0, 0.02, size=N_NODES), 0.0, 1.0)

        # Attacks occur in evaluation portion (epochs 1400..2000)
        if ep >= 1400:
            if rng.uniform() < 0.25:
                # Choose attack family
                att_mode = rng.choice(["gross", "stealth", "collusion"], p=[0.35, 0.40, 0.25])
                if att_mode == "collusion":
                    # Coordinated multi-cell collusion on adjacent edge: gNB-09 & gNB-10
                    for c_idx in [NODE_TO_IDX["gNB-09"], NODE_TO_IDX["gNB-10"]]:
                        labels[ep, c_idx] = 1.0
                        attack_types[ep, c_idx] = 3
                        r_l[c_idx] = float(np.clip(r_l[c_idx] - rng.uniform(0.18, 0.32), 0.05, 0.95))
                        r_s[c_idx] = float(np.clip(r_s[c_idx] - rng.uniform(0.15, 0.25), 0.10, 0.95))
                elif att_mode == "stealth":
                    # Stealth attack: bounded perturbation (delta <= 0.15 = 2.5 sigma)
                    target = rng.choice(N_NODES)
                    labels[ep, target] = 1.0
                    attack_types[ep, target] = 2
                    d_l = rng.choice([-1, 1]) * rng.uniform(0.08, 0.14)
                    d_s = rng.choice([-1, 1]) * rng.uniform(0.06, 0.12)
                    r_l[target] = float(np.clip(r_l[target] + d_l, 0.05, 0.95))
                    r_s[target] = float(np.clip(r_s[target] + d_s, 0.10, 0.95))
                else:
                    # Gross FDI attack
                    target = rng.choice(N_NODES)
                    labels[ep, target] = 1.0
                    attack_types[ep, target] = 1
                    d_l = rng.choice([-1, 1]) * rng.uniform(0.28, 0.55)
                    d_s = rng.choice([-1, 1]) * rng.uniform(0.22, 0.48)
                    r_l[target] = float(np.clip(r_l[target] + d_l, 0.05, 0.95))
                    r_s[target] = float(np.clip(r_s[target] + d_s, 0.10, 0.95))

        # Online Non-Oracle Reference Computation (observable EWMA + Spatial Neighbors)
        # L_ref(v) = 0.6 * L_ewma(v) + 0.4 * median(nbrs)
        for i, nid in enumerate(NODE_LIST):
            nbr_indices = [NODE_TO_IDX[nbr] for nbr in GRID_ADJACENCY[nid]]
            nbr_l_median = float(np.median([r_l[idx] for idx in nbr_indices]))
            nbr_s_median = float(np.median([r_s[idx] for idx in nbr_indices]))

            ref_loads[ep, i] = 0.6 * ewma_l[i] + 0.4 * nbr_l_median
            ref_sinrs[ep, i] = 0.6 * ewma_s[i] + 0.4 * nbr_s_median

        # Update EWMA for next epoch (alpha = 0.20)
        ewma_l = 0.80 * ewma_l + 0.20 * r_l
        ewma_s = 0.80 * ewma_s + 0.20 * r_s

        rep_loads[ep] = r_l
        rep_sinrs[ep] = r_s

    return rep_loads, rep_sinrs, ref_loads, ref_sinrs, labels, attack_types


def compute_metrics(y_true, y_pred):
    y_t = y_true.astype(int)
    y_p = y_pred.astype(int)

    tp = int(np.sum((y_p == 1) & (y_t == 1)))
    fp = int(np.sum((y_p == 1) & (y_t == 0)))
    fn = int(np.sum((y_p == 0) & (y_t == 1)))
    tn = int(np.sum((y_p == 0) & (y_t == 0)))

    prec = tp / (tp + fp + 1e-9)
    rec = tp / (tp + fn + 1e-9)
    f1 = 2 * prec * rec / (prec + rec + 1e-9)
    far = fp / (fp + tn + 1e-9)

    return prec, rec, f1, far


def compute_auc(y_true, scores):
    """Computes AUC-ROC via Mann-Whitney U test."""
    pos = scores[y_true == 1]
    neg = scores[y_true == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    n_pos, n_neg = len(pos), len(neg)
    all_scores = np.concatenate([pos, neg])
    ranks = np.argsort(np.argsort(all_scores)) + 1
    rank_sum_pos = np.sum(ranks[:n_pos])
    u = rank_sum_pos - (n_pos * (n_pos + 1)) / 2.0
    return float(u / (n_pos * n_neg))


def main():
    print("=" * 96)
    print("  AICOP-RAKSHA: REBUILT DETECTION & ALGORITHMIC ABLATION STUDY")
    print("  Non-Oracle Reference | 8-dim GraphSAGE Concatenation (Eq. 1-2) | Held-Out Stealth & Collusion")
    print("=" * 96)

    models = [
        "Tuned Spatial Median Residual",
        "2-Layer MLP (No Graph Aggregation)",
        "GraphSAGE-Only (Learned GNN)",
        "Deviation Penalty-Only (Heuristic)",
        "Unified AICOP GraphSAGE + Penalty (Ours)",
    ]

    results = {m: [] for m in models}
    all_prevalences = []

    for seed_idx, seed in enumerate(SEEDS):
        # 1. Train models on Gross FDI only (Stealth & Collusion held out)
        X_self_train, X_sage_train, y_train = generate_train_dataset(n_samples=3500, seed=seed)

        mlp = VectorizedNeuralNet(in_features=4, hidden=16, lr=0.15, epochs=350)
        mlp.fit(X_self_train, y_train, seed=seed)

        sage = VectorizedNeuralNet(in_features=8, hidden=16, lr=0.15, epochs=350)
        sage.fit(X_sage_train, y_train, seed=seed)

        # 2. Generate Fleet Trajectory (2,000 epochs)
        rep_l, rep_s, ref_l, ref_s, labels, attack_types = generate_fleet_eval_trajectory(num_epochs=2000, seed=seed)

        # 70/30 Chronological Split: Evaluate on the last 600 epochs (7,200 cell-epochs)
        test_start = 1400
        test_rep_l = rep_l[test_start:]
        test_rep_s = rep_s[test_start:]
        test_ref_l = ref_l[test_start:]
        test_ref_s = ref_s[test_start:]
        test_labels = labels[test_start:]
        test_att_types = attack_types[test_start:]

        n_test_epochs = len(test_rep_l)
        total_eval_cells = n_test_epochs * N_NODES

        flat_y = test_labels.reshape(-1)
        flat_types = test_att_types.reshape(-1)
        prevalence = float(np.sum(flat_y)) / total_eval_cells * 100.0
        all_prevalences.append(prevalence)

        # Construct Features per cell
        # x_v = [rep_l, rep_s, ref_l, ref_s] (4 dims)
        # x_nbr = mean_nbr([rep_l, rep_s, ref_l, ref_s]) (4 dims)
        # x_sage = [x_v || x_nbr] (8 dims, Eq. 1)
        feat_self = np.zeros((n_test_epochs, N_NODES, 4), dtype=np.float32)
        feat_sage = np.zeros((n_test_epochs, N_NODES, 8), dtype=np.float32)

        for ep in range(n_test_epochs):
            for i, nid in enumerate(NODE_LIST):
                v_feat = [test_rep_l[ep, i], test_rep_s[ep, i], test_ref_l[ep, i], test_ref_s[ep, i]]
                feat_self[ep, i] = v_feat

                nbr_indices = [NODE_TO_IDX[nbr] for nbr in GRID_ADJACENCY[nid]]
                nbr_rep_l_mean = float(np.mean([test_rep_l[ep, idx] for idx in nbr_indices]))
                nbr_rep_s_mean = float(np.mean([test_rep_s[ep, idx] for idx in nbr_indices]))
                nbr_ref_l_mean = float(np.mean([test_ref_l[ep, idx] for idx in nbr_indices]))
                nbr_ref_s_mean = float(np.mean([test_ref_s[ep, idx] for idx in nbr_indices]))
                nbr_feat = [nbr_rep_l_mean, nbr_rep_s_mean, nbr_ref_l_mean, nbr_ref_s_mean]

                feat_sage[ep, i] = v_feat + nbr_feat

        # Model 1: Tuned Spatial Median Residual
        sm_attacks = np.zeros((n_test_epochs, N_NODES), dtype=int)
        sm_residuals = np.zeros((n_test_epochs, N_NODES), dtype=np.float32)
        for ep in range(n_test_epochs):
            for i, nid in enumerate(NODE_LIST):
                nbr_indices = [NODE_TO_IDX[nbr] for nbr in GRID_ADJACENCY[nid]]
                nbr_med = np.median([test_rep_l[ep, idx] for idx in nbr_indices])
                res = abs(test_rep_l[ep, i] - nbr_med)
                sm_residuals[ep, i] = res
                sm_attacks[ep, i] = 1 if res > 0.12 else 0

        # Model 2: 2-Layer MLP
        flat_self = feat_self.reshape(-1, 4)
        mlp_trust = mlp.predict_trust(flat_self).reshape(n_test_epochs, N_NODES)
        mlp_attacks = (mlp_trust < 0.25).astype(int)

        # Model 3: GraphSAGE-Only (Eq. 1 & 2)
        flat_sage = feat_sage.reshape(-1, 8)
        sage_trust = sage.predict_trust(flat_sage).reshape(n_test_epochs, N_NODES)
        sage_attacks = (sage_trust < 0.25).astype(int)

        # Model 4: Deviation Penalty-Only: T = exp(-2.5 * ||x_rep - x_ref||_1)
        dev_l = np.abs(test_rep_l - test_ref_l)
        dev_s = np.abs(test_rep_s - test_ref_s)
        dev_norm = dev_l + dev_s
        dev_trust = np.exp(-2.5 * dev_norm)
        dev_attacks = (dev_trust < 0.35).astype(int)

        # Model 5: Unified AICOP GraphSAGE + Penalty (Eq. 3 with calibrated operating threshold theta=0.25)
        unified_trust = np.clip(sage_trust * np.exp(-2.5 * dev_norm), 0.05, 1.00)
        unified_attacks = (unified_trust < 0.25).astype(int)

        preds_map = {
            "Tuned Spatial Median Residual": (sm_attacks.reshape(-1), sm_residuals.reshape(-1)),
            "2-Layer MLP (No Graph Aggregation)": (mlp_attacks.reshape(-1), 1.0 - mlp_trust.reshape(-1)),
            "GraphSAGE-Only (Learned GNN)": (sage_attacks.reshape(-1), 1.0 - sage_trust.reshape(-1)),
            "Deviation Penalty-Only (Heuristic)": (dev_attacks.reshape(-1), 1.0 - dev_trust.reshape(-1)),
            "Unified AICOP GraphSAGE + Penalty (Ours)": (unified_attacks.reshape(-1), 1.0 - unified_trust.reshape(-1)),
        }

        for m in models:
            preds, scores = preds_map[m]
            p, r, f1, far = compute_metrics(flat_y, preds)
            auc = compute_auc(flat_y, scores)

            # Stealth attack evaluation subset (type == 2 vs honest)
            st_mask = (flat_types == 2) | (flat_y == 0)
            st_p, st_r, st_f1, _ = compute_metrics(flat_y[st_mask], preds[st_mask])

            # Adjacent Collusion evaluation subset (type == 3 vs honest)
            col_mask = (flat_types == 3) | (flat_y == 0)
            col_p, col_r, col_f1, _ = compute_metrics(flat_y[col_mask], preds[col_mask])

            results[m].append({
                "precision": p * 100.0,
                "recall": r * 100.0,
                "f1": f1 * 100.0,
                "far": far * 100.0,
                "auc": auc,
                "stealth_f1": st_f1 * 100.0,
                "collusion_f1": col_f1 * 100.0,
            })

        print(f"  [Seed {seed_idx+1:2d}/10: {seed}] Test Prevalence = {prevalence:.2f}% | Unified F1 = {results['Unified AICOP GraphSAGE + Penalty (Ours)'][-1]['f1']:.1f}%")

    mean_prev = np.mean(all_prevalences)
    print(f"\n[Test Set Setup] Mean Cell-Epoch Attack Prevalence across 10 Seeds: {mean_prev:.2f}% ({round(mean_prev * 72.0)} attacked of 7,200 cell-epochs)")

    print("\n" + "=" * 110)
    print("  COMPREHENSIVE ABLATION TABLE (EMPIRICALLY COMPUTED FROM 10 SEEDS)")
    print("=" * 110)
    print(f"{'Model Architecture':<42} | {'Precision':<12} | {'Recall':<12} | {'F1-Score':<12} | {'FAR':<10} | {'AUC-ROC':<8} | {'Stealth F1':<12} | {'Collusion F1'}")
    print("-" * 135)

    summary_rows = []
    for m in models:
        df_m = pd.DataFrame(results[m])
        p_m, p_sd = df_m["precision"].mean(), df_m["precision"].std()
        r_m, r_sd = df_m["recall"].mean(), df_m["recall"].std()
        f1_m, f1_sd = df_m["f1"].mean(), df_m["f1"].std()
        far_m, far_sd = df_m["far"].mean(), df_m["far"].std()
        auc_m, auc_sd = df_m["auc"].mean(), df_m["auc"].std()
        st_m, st_sd = df_m["stealth_f1"].mean(), df_m["stealth_f1"].std()
        col_m, col_sd = df_m["collusion_f1"].mean(), df_m["collusion_f1"].std()

        print(f"{m:<42} | {p_m:5.1f} +/- {p_sd:4.1f}% | {r_m:5.1f} +/- {r_sd:4.1f}% | {f1_m:5.1f} +/- {f1_sd:4.1f}% | {far_m:4.1f} +/- {far_sd:3.1f}% | {auc_m:6.3f}   | {st_m:5.1f} +/- {st_sd:4.1f}% | {col_m:5.1f} +/- {col_sd:4.1f}%")

        summary_rows.append({
            "model": m,
            "precision_mean": p_m, "precision_std": p_sd,
            "recall_mean": r_m, "recall_std": r_sd,
            "f1_mean": f1_m, "f1_std": f1_sd,
            "far_mean": far_m, "far_std": far_sd,
            "auc_mean": auc_m, "auc_std": auc_sd,
            "stealth_f1_mean": st_m, "stealth_f1_std": st_sd,
            "collusion_f1_mean": col_m, "collusion_f1_std": col_sd,
        })

    out_csv = RESULTS_DIR / "detection_ablation_results.csv"
    pd.DataFrame(summary_rows).to_csv(out_csv, index=False)
    print(f"\n[OK] Successfully saved empirical ablation results to: {out_csv}")
    print("=" * 110)


if __name__ == "__main__":
    main()
