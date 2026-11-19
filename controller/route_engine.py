from __future__ import annotations
from typing import Dict, List, Optional
from common.interfaces import Route, RouteDecision, LinkTelemetry, LinkState

# Standard weights (sum = 1.00)
RW = dict(latency=0.2, pdr=0.3, congestion=0.15, trust=0.25, jam=0.1)

# LEACH-inspired Energy-Aware weights (sum = 1.00)
# Energy gets 16% weight to balance satellite battery depletion
RW_ENERGY = dict(latency=0.15, pdr=0.25, congestion=0.12, trust=0.22, jam=0.10, energy=0.16)


class RouteEngine:
    """
    Route selection engine with multi-criteria AI scoring.
    Supports both baseline QoS scoring and LEACH-inspired Energy-Aware Routing.
    """

    def __init__(
        self,
        routes: List[Route],
        margin: float = 0.05,
        min_trust: float = 0.5,
        enable_energy: bool = False,
        initial_energy: Optional[Dict[str, float]] = None,
        drain_rate: float = 0.002,
        recharge_rate: float = 0.001,
    ):
        self.routes = {r.name: r for r in routes}
        self.active = routes[0].name
        self.margin = margin
        self.min_trust = min_trust
        self.enable_energy = enable_energy
        self.drain_rate = drain_rate
        self.recharge_rate = recharge_rate

        # Initialize residual energy per node/satellite (0.0 to 1.0)
        self.node_energy: Dict[str, float] = {}
        for r in routes:
            self.node_energy[r.via] = 1.0
        if initial_energy:
            self.node_energy.update(initial_energy)

    def set_node_energy(self, via: str, level: float) -> None:
        """Set residual energy for a specific satellite/node (clamped [0.0, 1.0])."""
        self.node_energy[via] = max(0.0, min(1.0, float(level)))

    def get_node_energy(self) -> Dict[str, float]:
        """Return a copy of the current residual energy for all nodes."""
        return dict(self.node_energy)

    def drain_energy(self, via: str, amount: Optional[float] = None) -> float:
        """Drain energy from a node due to transmission/processing."""
        rate = self.drain_rate if amount is None else amount
        current = self.node_energy.get(via, 1.0)
        updated = max(0.0, current - rate)
        self.node_energy[via] = updated
        return updated

    def recharge_energy(self, via: str, amount: Optional[float] = None) -> float:
        """Recharge energy from solar harvesting during sunlight orbit."""
        rate = self.recharge_rate if amount is None else amount
        current = self.node_energy.get(via, 1.0)
        updated = min(1.0, current + rate)
        self.node_energy[via] = updated
        return updated

    def step_energy(self, active_via: str) -> None:
        """
        LEACH-style energy cycle:
        The active satellite drains battery, while idle satellites recharge via solar panels.
        """
        for via in list(self.node_energy.keys()):
            if via == active_via:
                self.drain_energy(via)
            else:
                self.recharge_energy(via)

    def score(self, route: Route, tel: Dict[str, LinkTelemetry], st: Dict[str, LinkState]) -> float:
        hops = route.hops
        if any(st[h].isolated for h in hops):
            return 0.0

        lat = sum(tel[h].latency_ms for h in hops)
        pdr = 1.0
        for h in hops:
            pdr *= (1.0 - tel[h].loss)
        cong = max(tel[h].queue_depth for h in hops)
        trust = min(st[h].trust for h in hops)
        jam = max(st[h].anomaly for h in hops)

        if not self.enable_energy:
            # Baseline QoS formula
            return round(
                RW['latency'] * max(0.0, 1.0 - lat / 400.0)
                + RW['pdr'] * pdr
                + RW['congestion'] * (1.0 - cong)
                + RW['trust'] * trust
                + RW['jam'] * (1.0 - jam),
                3
            )

        # LEACH-inspired Energy-Aware formula
        energy = self.node_energy.get(route.via, 1.0)
        return round(
            RW_ENERGY['latency'] * max(0.0, 1.0 - lat / 400.0)
            + RW_ENERGY['pdr'] * pdr
            + RW_ENERGY['congestion'] * (1.0 - cong)
            + RW_ENERGY['trust'] * trust
            + RW_ENERGY['jam'] * (1.0 - jam)
            + RW_ENERGY['energy'] * energy,
            3
        )

    def decide(self, t_ms: int, tel: Dict[str, LinkTelemetry], st: Dict[str, LinkState]) -> RouteDecision:
        scores = {n: self.score(r, tel, st) for n, r in self.routes.items()}
        best = max(scores, key=scores.get)
        prev = self.active
        cur_trust = min(st[h].trust for h in self.routes[prev].hops)

        # Reroute condition: either score difference exceeds margin, or trust is degraded
        if best != prev and (scores[best] - scores[prev] > self.margin or cur_trust < self.min_trust):
            self.active = best
            reason = f'{prev} score {scores[prev]} (trust {cur_trust:.2f}) < {best} score {scores[best]}'
        else:
            reason = 'keep'

        # If energy tracking is enabled, update node battery levels
        if self.enable_energy:
            active_via = self.routes[self.active].via
            self.step_energy(active_via)

        return RouteDecision(t_ms, self.active, prev, scores, reason)


class ReactiveBFDRouteEngine:
    """
    Standard industry reactive baseline: Bidirectional Forwarding Detection (BFD)
    with loss hold-timer timeout (RFC 5880 / 3GPP TS 38.300).
    Unlike proactive AICOP-RAKSHA (which predicts cross-layer degradation in ~188ms),
    reactive BFD waits for consecutive loss samples exceeding the threshold (e.g. loss > 0.40
    for 1.5 seconds / 15 control cycles) before triggering failover.
    """
    def __init__(self, routes: List[Route], loss_threshold: float = 0.40, hold_ticks: int = 15):
        self.routes = {r.name: r for r in routes}
        self.route_list = list(routes)
        self.active = routes[0].name
        self.loss_threshold = loss_threshold
        self.hold_ticks = hold_ticks
        self._consecutive_loss_ticks = 0

    def decide(self, t_ms: int, tel: Dict[str, LinkTelemetry], st: Dict[str, LinkState]) -> RouteDecision:
        curr_route = self.routes[self.active]
        curr_loss = max((tel[h].loss for h in curr_route.hops), default=0.0)
        prev = self.active

        if curr_loss >= self.loss_threshold:
            self._consecutive_loss_ticks += 1
        else:
            self._consecutive_loss_ticks = max(0, self._consecutive_loss_ticks - 1)

        scores = {r.name: 1.0 if r.name == self.active else 0.5 for r in self.route_list}
        reason = 'keep (monitoring loss)'

        if self._consecutive_loss_ticks >= self.hold_ticks:
            alternatives = [r for r in self.route_list if r.name != self.active]
            if alternatives:
                best_alt = min(alternatives, key=lambda r: max((tel[h].loss for h in r.hops), default=0.0))
                self.active = best_alt.name
                reason = f'BFD timeout expired ({self._consecutive_loss_ticks} ticks); failover to {self.active}'
                self._consecutive_loss_ticks = 0

        return RouteDecision(t_ms, self.active, prev, scores, reason)
