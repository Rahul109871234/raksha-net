"""
aicop_bridge.py
===============
AICOP-to-RAKSHA Cross-Layer Intelligence Bridge.
Integrates AICOP's O-RAN Near-RT RIC intelligence (GraphSAGE trust scoring,
TT-ACTS canary damping, and Pareto xApp conflict arbitration) directly into
RAKSHA-NET's 5G NTN satellite resilience controller.

Features:
  - 2-Layer Inductive GraphSAGE Trust Engine (pure NumPy / vector math).
  - Pareto Utility Arbitration between Traffic Steering (TS), Energy Saving (ES),
    and QoS xApps under corrupted telemetry / False Data Injection (FDI).
  - Cross-layer Threat Signal: Feeds terrestrial cell trust degradation directly
    into RAKSHA-NET's CUSUM anomaly engine for proactive satellite offloading.
"""

import math
import random
from typing import Dict, List, Tuple, Optional

class GraphSAGETrustEngine:
    """
    2-Layer GraphSAGE Trust Model for Radio Access Nodes (gNBs / Cells).
    Evaluates reported metrics against spatial neighborhood reference to detect
    False Data Injection (FDI) and telemetry flapping without GPU overhead.
    """
    def __init__(self, in_features: int = 4, hidden_dim: int = 8):
        self.in_features = in_features
        self.hidden_dim = hidden_dim
        # Deterministic weights for inference stability
        random.seed(42)
        self.W1 = [[random.gauss(0, 0.2) for _ in range(hidden_dim)] for _ in range(in_features)]
        self.W2 = [[random.gauss(0, 0.2) for _ in range(1)] for _ in range(hidden_dim)]
        self.b1 = [0.01] * hidden_dim
        self.b2 = 0.5

    def _matmul(self, vec: List[float], mat: List[List[float]]) -> List[float]:
        cols = len(mat[0])
        res = [0.0] * cols
        for j in range(cols):
            res[j] = sum(vec[i] * mat[i][j] for i in range(len(vec)))
        return res

    def _relu(self, vec: List[float]) -> List[float]:
        return [max(0.0, v) for v in vec]

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(min(x, 15.0), -15.0)))

    def infer_cell_trust(self, node_features: Dict[str, List[float]], adjacency: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Runs 2-layer GraphSAGE mean aggregation over the cell graph.
        Features per node: [reported_load, reported_sinr, ref_load, ref_sinr]
        Returns: {cell_id: trust_score} where trust_score in [0.0, 1.0].
        """
        trust_scores = {}
        # Layer 1: Aggregate 1-hop neighbor features
        h1 = {}
        for node, feats in node_features.items():
            neighbors = adjacency.get(node, [])
            if neighbors:
                agg_feats = [
                    sum(node_features[nbr][f] for nbr in neighbors) / len(neighbors)
                    for f in range(self.in_features)
                ]
            else:
                agg_feats = feats[:]
            
            # Combine self + neighborhood
            combined = [(feats[k] + agg_feats[k]) * 0.5 for k in range(self.in_features)]
            z1 = self._matmul(combined, self.W1)
            h1[node] = self._relu([z1[k] + self.b1[k] for k in range(self.hidden_dim)])

        # Layer 2: Final regression to trust score
        for node, h_vec in h1.items():
            z2 = sum(h_vec[k] * self.W2[k][0] for k in range(self.hidden_dim)) + self.b2
            # Reference deviation penalty
            rf = node_features[node]
            dev = abs(rf[0] - rf[2]) + abs(rf[1] - rf[3])  # |load - ref_load| + |sinr - ref_sinr|
            trust_raw = self._sigmoid(z2) * math.exp(-2.5 * dev)
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
        
        # Build 12-cell dual-band hexagonal topology adjacency
        self.adjacency = {}
        for i in range(num_cells):
            cid = f"gNB-{i+1:02d}"
            # Adjacent to nearest 2 neighbors in ring/cluster
            self.adjacency[cid] = [
                f"gNB-{(i-1)%num_cells + 1:02d}",
                f"gNB-{(i+1)%num_cells + 1:02d}"
            ]

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
