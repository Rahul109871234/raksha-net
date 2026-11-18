from __future__ import annotations
import json
import logging
import pathlib
import time
from collections import defaultdict
from typing import Optional, Dict, List, Tuple
from common.interfaces import LinkState, Route, RouteDecision
from emulator.network_emulator import NetworkEmulator
from controller.anomaly_engine import HeuristicDetector, make_detector
from controller.trust_engine import TrustEngine
from controller.route_engine import RouteEngine
from controller.security_engine import SecurityEngine, BACKEND
from controller.aggregation_engine import AggregationEngine, AggregatedTelemetry

ROUTES = [
    Route('R1', ['A-GW', 'GW-LEO1', 'LEO1-B'], 'LEO1'),
    Route('R2', ['A-GW', 'GW-LEO2', 'LEO2-B'], 'LEO2'),
]
LINKS = sorted({h for r in ROUTES for h in r.hops})
LINK_TO_VIA: dict[str, str] = {
    'A-GW': 'GW',
    'GW-LEO1': 'LEO1',
    'GW-LEO2': 'LEO2',
    'LEO1-B': 'LEO1',
    'LEO2-B': 'LEO2',
}
THREAT_ANOMALY = 0.6
RECOVERY_WINDOW = 8
RECOVERY_ANOMALY_THRESH = 0.25
log = logging.getLogger('raksha.controller')


class Controller:
    """
    RAKSHA-NET autonomous controller.
    Coordinates anomaly detection, trust scoring, multi-criteria routing,
    PQC crypto state machine, and LEACH-inspired enhancements:
      - Energy-aware routing and satellite battery tracking
      - In-flight telemetry aggregation and compression
      - LEACH session master (cluster head) dynamic rotation
    """

    def __init__(
        self,
        seed: int = 0,
        net = None,
        detector = None,
        detector_name: str = 'heuristic',
        allow_recovery: bool = True,
        ramp_steps: int = 15,
        verbose: bool = False,
        enable_energy: bool = False,
        enable_aggregation: bool = False,
        agg_window: int = 5,
        enable_leach_rounds: bool = False,
        round_ticks: int = 50,
    ):
        if net is not None:
            self.net = net
        else:
            self.net = NetworkEmulator(LINKS, seed=seed, ramp_steps=ramp_steps)
        if detector is not None:
            self.det = detector
            self._detector_name = getattr(detector, 'LABEL', detector_name)
        else:
            self.det = make_detector(detector_name)
            self._detector_name = getattr(self.det, 'LABEL', detector_name)

        self.trust = TrustEngine()
        self.enable_energy = enable_energy
        self.router = RouteEngine(ROUTES, enable_energy=enable_energy)
        self.sec = SecurityEngine()

        self.enable_aggregation = enable_aggregation
        self.aggregator = AggregationEngine(window=agg_window) if enable_aggregation else None
        self.latest_aggregates: Dict[str, AggregatedTelemetry] = {}

        self.enable_leach_rounds = enable_leach_rounds
        self.round_ticks = round_ticks
        self._step_count = 0
        self._leach_round = 0

        self.hist = defaultdict(list)
        self.state: dict[str, LinkState] = {l: LinkState(l) for l in LINKS}
        self.decisions: list[RouteDecision] = []
        self.allow_recovery = allow_recovery
        self.verbose = verbose
        self._recovery_count: dict[str, int] = defaultdict(int)
        self._live_state_path = pathlib.Path('runs/live_state.json')
        self._live_state_path.parent.mkdir(exist_ok=True)

    @property
    def detector_name(self) -> str:
        return self._detector_name

    @property
    def backend(self) -> str:
        return BACKEND

    def step(self, dt_ms: int = 100) -> tuple[RouteDecision, int, int]:
        self._step_count += 1
        self.net.tick(dt_ms)
        tel: dict = {}

        for link in LINKS:
            t = self.net.sample(link)
            tel[link] = t
            self.hist[link].append(t)

            # In-flight LEACH-style aggregation
            if self.aggregator is not None:
                agg = self.aggregator.ingest(t)
                if agg is not None:
                    self.latest_aggregates[link] = agg

            a = self.det.score(self.hist[link])
            st = self.state[link]
            st.anomaly = a
            st.trust = self.trust.update(t, a)
            via = LINK_TO_VIA.get(link, link)

            if a > THREAT_ANOMALY and (not st.isolated):
                st.isolated = True
                self._recovery_count[link] = 0
                if self.verbose:
                    log.info('[t=%dms] THREAT %s anomaly=%.3f', self.net.t_ms, link, a)
                self.sec.on_threat(self.net.t_ms, link, a, via=via, bw_mbps=t.throughput_mbps)
            elif st.isolated and self.allow_recovery:
                if a < RECOVERY_ANOMALY_THRESH and st.trust > 0.6:
                    self._recovery_count[link] += 1
                else:
                    self._recovery_count[link] = 0
                if self._recovery_count[link] >= RECOVERY_WINDOW:
                    st.isolated = False
                    self._recovery_count[link] = 0
                    if self.verbose:
                        log.info('[t=%dms] RECOVERY %s trust=%.3f', self.net.t_ms, link, st.trust)
                    self.sec.on_recovery(self.net.t_ms, link, via=via, bw_mbps=t.throughput_mbps)

        # Route decision
        decision = self.router.decide(self.net.t_ms, tel, self.state)
        self.decisions.append(decision)

        # LEACH-style round boundary check: periodic session master rotation
        if self.enable_leach_rounds and (self._step_count % self.round_ticks == 0):
            self._leach_round += 1
            trust_map = {
                'GW': 1.0,
                'LEO1': min(self.state['GW-LEO1'].trust, self.state['LEO1-B'].trust),
                'LEO2': min(self.state['GW-LEO2'].trust, self.state['LEO2-B'].trust),
            }
            energy_map = self.router.get_node_energy()
            new_master, rotated = self.sec.elect_session_master(
                t_ms=self.net.t_ms,
                round_num=self._leach_round,
                energy_levels=energy_map,
                trust_levels=trust_map,
                mode='energy_trust'
            )
            if rotated and self.verbose:
                log.info('[LEACH Round %d] Master rotated to %s', self._leach_round, new_master)

        self.sec.periodic_rekey_if_due(self.net.t_ms)
        hops = self.router.routes[self.router.active].hops
        ok, n = self.net.send(hops)
        if self.verbose and decision.reason != 'keep':
            log.info('[t=%dms] ROUTE %s->%s | %s', decision.t_ms, decision.previous, decision.chosen, decision.reason)

        self._write_live(decision, tel, ok, n)
        return (decision, ok, n)

    def _write_live(self, decision: RouteDecision, tel: dict, ok: int, n: int):
        try:
            state_data = {
                't_ms': self.net.t_ms,
                'active_route': self.router.active,
                'scores': decision.scores,
                'reason': decision.reason,
                'backend': BACKEND,
                'detector': self._detector_name,
                'sec_state': self.sec.state.value,
                'session_master': self.sec.session_master,
                'suite': self.sec.suite.name,
                'kex': self.sec.suite.kex,
                'aead': self.sec.suite.aead,
                'isolated': list(self.sec.isolated),
                'session_id': self.sec._session_id,
                'pdr': round(ok / n, 3) if n else 0,
                'energy': self.router.get_node_energy() if self.enable_energy else {},
                'aggregation_saved_pct': self.aggregator.bandwidth_saved_theoretical_pct() if self.aggregator else 0.0,
                'links': {
                    link: {
                        'latency_ms': round(tel[link].latency_ms, 2),
                        'loss': round(tel[link].loss, 3),
                        'jitter_ms': round(tel[link].jitter_ms, 2),
                        'throughput_mbps': round(tel[link].throughput_mbps, 2),
                        'queue_depth': round(tel[link].queue_depth, 3),
                        'trust': round(self.state[link].trust, 3),
                        'anomaly': round(self.state[link].anomaly, 3),
                        'isolated': self.state[link].isolated,
                    }
                    for link in LINKS
                },
            }
            self._live_state_path.write_text(json.dumps(state_data))
        except OSError:
            pass