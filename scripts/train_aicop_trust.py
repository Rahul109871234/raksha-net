"""
train_aicop_trust.py
====================
Trains the GraphSAGE-style cell trust engine used in aicop_bridge.py.

Generates synthetic labeled O-RAN telemetry:
  - Normal cells : reported ≈ reference  (small Gaussian deviation)
  - FDI cells    : reported far from reference (large injected deviation)

Saves weights to models/aicop_trust_engine.npz.

Usage:
    python scripts/train_aicop_trust.py [--samples 2000] [--epochs 800] [--hidden 16]
"""
from __future__ import annotations
import argparse
import pathlib
import sys
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

MODELS_DIR  = pathlib.Path("models")
RESULTS_DIR = pathlib.Path("results")


def generate_samples(n: int = 2000, seed: int = 42):
    rng = np.random.default_rng(seed)
    X, y = [], []
    half = n // 2

    # Trusted cells: reported ≈ reference ± small noise (σ=0.04)
    for _ in range(half):
        ref_l = rng.uniform(0.1, 0.9)
        ref_s = rng.uniform(0.2, 1.0)
        X.append([
            float(np.clip(ref_l + rng.normal(0, 0.04), 0, 1)),
            float(np.clip(ref_s + rng.normal(0, 0.04), 0, 1)),
            ref_l, ref_s
        ])
        y.append(1.0)

    # FDI / compromised: large deviation (0.25–0.65) in random direction
    for _ in range(half):
        ref_l = rng.uniform(0.1, 0.9)
        ref_s = rng.uniform(0.2, 1.0)
        d_l = rng.choice([-1, 1]) * rng.uniform(0.25, 0.65)
        d_s = rng.choice([-1, 1]) * rng.uniform(0.25, 0.65)
        X.append([
            float(np.clip(ref_l + d_l, 0, 1)),
            float(np.clip(ref_s + d_s, 0, 1)),
            ref_l, ref_s
        ])
        y.append(0.0)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)
    idx = rng.permutation(len(X))
    return X[idx], y[idx]


def train(X, y, hidden=16, epochs=800, lr=0.3, seed=42):
    rng = np.random.default_rng(seed)
    n_feat = X.shape[1]
    w1 = rng.normal(0, 0.3, (hidden, n_feat)).astype(np.float32)
    b1 = np.zeros(hidden, dtype=np.float32)
    w2 = rng.normal(0, 0.3, hidden).astype(np.float32)
    b2 = np.float32(0.0)

    def relu(x):    return np.maximum(0.0, x)
    def sigmoid(x): return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

    n = len(X)
    for epoch in range(epochs):
        h1     = relu(w1 @ X.T + b1[:, None])
        logits = w2 @ h1 + b2
        preds  = sigmoid(logits)
        eps = 1e-7
        loss = -np.mean(y * np.log(preds + eps) + (1 - y) * np.log(1 - preds + eps))

        d_logits = (preds - y) / n
        d_w2     = h1 @ d_logits
        d_b2     = float(np.sum(d_logits))
        d_h1     = np.outer(w2, d_logits)
        d_h1_pre = d_h1 * (h1 > 0).astype(np.float32)
        d_w1     = d_h1_pre @ X
        d_b1     = d_h1_pre.sum(axis=1)

        w1 -= lr * d_w1
        b1 -= lr * d_b1
        w2 -= lr * d_w2
        b2 -= lr * np.float32(d_b2)

        if (epoch + 1) % 100 == 0:
            print(f"  epoch {epoch+1:3d}/{epochs} | loss={loss:.4f}")

    return {"w1": w1, "w2": w2, "b1": b1, "b2": b2}


def evaluate(weights, X, y, threshold=0.5):
    def relu(x):    return np.maximum(0.0, x)
    def sigmoid(x): return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))
    h1    = relu(weights["w1"] @ X.T + weights["b1"][:, None])
    preds = (sigmoid(weights["w2"] @ h1 + weights["b2"]) >= threshold).astype(int)
    tp = int(np.sum((preds == 1) & (y == 1)))
    fp = int(np.sum((preds == 1) & (y == 0)))
    fn = int(np.sum((preds == 0) & (y == 1)))
    tn = int(np.sum((preds == 0) & (y == 0)))
    p  = tp / (tp + fp + 1e-9)
    r  = tp / (tp + fn + 1e-9)
    f1 = 2 * p * r / (p + r + 1e-9)
    return {"precision": round(p,4), "recall": round(r,4), "f1": round(f1,4),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn}


def main():
    ap = argparse.ArgumentParser(description="Train AICOP cell trust engine")
    ap.add_argument("--samples", type=int, default=2000)
    ap.add_argument("--epochs",  type=int, default=800)
    ap.add_argument("--hidden",  type=int, default=16)
    ap.add_argument("--lr",      type=float, default=0.3)
    a = ap.parse_args()

    MODELS_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)

    print(f"Generating {a.samples} synthetic cell-trust samples...")
    X, y = generate_samples(a.samples, seed=42)
    split = int(0.8 * len(X))
    idx   = np.random.default_rng(0).permutation(len(X))
    X_tr, y_tr = X[idx[:split]], y[idx[:split]]
    X_te, y_te = X[idx[split:]], y[idx[split:]]

    print(f"Training on {len(X_tr)} | Testing on {len(X_te)} | "
          f"hidden={a.hidden} epochs={a.epochs} lr={a.lr}")
    weights = train(X_tr, y_tr, hidden=a.hidden, epochs=a.epochs, lr=a.lr)

    out = MODELS_DIR / "aicop_trust_engine.npz"
    np.savez(str(out), **weights)
    print(f"\nWeights saved → {out}")

    tr_m = evaluate(weights, X_tr, y_tr)
    te_m = evaluate(weights, X_te, y_te)
    print("\n--- Cell Trust Engine Results ---")
    print(f"Train | P={tr_m['precision']:.3f} R={tr_m['recall']:.3f} F1={tr_m['f1']:.3f}")
    print(f"Test  | P={te_m['precision']:.3f} R={te_m['recall']:.3f} F1={te_m['f1']:.3f}")
    print(f"Confusion (test): TP={te_m['tp']} FP={te_m['fp']} FN={te_m['fn']} TN={te_m['tn']}")

    # Sanity checks
    print("\n--- Sanity checks ---")
    from controller.aicop_bridge import GraphSAGETrustEngine
    eng = GraphSAGETrustEngine()
    adjacency = {"gNB-01": ["gNB-02"], "gNB-02": ["gNB-01"]}
    # Normal cell
    normal = {"gNB-01": [0.5, 0.7, 0.5, 0.7], "gNB-02": [0.4, 0.6, 0.4, 0.6]}
    scores_n = eng.infer_cell_trust(normal, adjacency)
    # FDI cell
    fdi    = {"gNB-01": [0.9, 0.1, 0.5, 0.7], "gNB-02": [0.4, 0.6, 0.4, 0.6]}
    scores_f = eng.infer_cell_trust(fdi, adjacency)
    print(f"Normal cell trust : {scores_n['gNB-01']:.4f}  (expect > 0.60)")
    print(f"FDI cell trust    : {scores_f['gNB-01']:.4f}  (expect < 0.40)")


if __name__ == "__main__":
    main()
