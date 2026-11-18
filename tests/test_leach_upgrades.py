from __future__ import annotations
import pytest
from common.interfaces import LinkTelemetry, LinkState, Route
from controller.aggregation_engine import AggregationEngine, AggregatedTelemetry
from controller.route_engine import RouteEngine
from controller.security_engine import SecurityEngine, SecState
from controller.controller import Controller, ROUTES, LINKS


class TestAggregationEngine:
    """Tests for LEACH-style in-flight telemetry aggregation and compression."""

    def test_window_buffering(self):
        engine = AggregationEngine(window=5)
        for i in range(4):
            tel = LinkTelemetry(
                link_id='GW-LEO1',
                t_ms=i * 100,
                latency_ms=25.0,
                jitter_ms=2.0,
                loss=0.01,
                throughput_mbps=100.0,
                queue_depth=0.05,
            )
            result = engine.ingest(tel)
            assert result is None, f"Expected None before window is full, got {result}"

        # 5th sample fills the window and produces aggregate
        tel = LinkTelemetry(
            link_id='GW-LEO1',
            t_ms=400,
            latency_ms=26.0,
            jitter_ms=2.1,
            loss=0.01,
            throughput_mbps=98.0,
            queue_depth=0.06,
        )
        agg = engine.ingest(tel)
        assert agg is not None
        assert isinstance(agg, AggregatedTelemetry)
        assert agg.window_size == 5
        assert agg.link_id == 'GW-LEO1'
        assert agg.raw_bytes > agg.compressed_bytes
        assert agg.compression_ratio > 0.0
        assert engine.bandwidth_saved_theoretical_pct() == 80.0

    def test_anomaly_detection_flag(self):
        engine = AggregationEngine(window=3)
        # 2 normal samples + 1 degraded sample
        engine.ingest(LinkTelemetry('GW-LEO1', 0, 20.0, 1.0, 0.01, 100.0, 0.02))
        engine.ingest(LinkTelemetry('GW-LEO1', 100, 22.0, 1.2, 0.02, 95.0, 0.03))
        agg = engine.ingest(LinkTelemetry('GW-LEO1', 200, 85.0, 15.0, 0.35, 10.0, 0.70))
        assert agg is not None
        assert agg.anomaly_flag is True
        assert agg.mean_loss > 0.10


class TestEnergyAwareRouting:
    """Tests for LEACH-inspired energy-balancing routing."""

    def _mock_telemetry_and_state(self):
        tel = {
            'A-GW': LinkTelemetry('A-GW', 0, 5.0, 0.5, 0.001, 200.0, 0.01),
            'GW-LEO1': LinkTelemetry('GW-LEO1', 0, 20.0, 1.0, 0.01, 100.0, 0.05),
            'LEO1-B': LinkTelemetry('LEO1-B', 0, 22.0, 1.2, 0.01, 100.0, 0.05),
            'GW-LEO2': LinkTelemetry('GW-LEO2', 0, 21.0, 1.1, 0.01, 100.0, 0.05),
            'LEO2-B': LinkTelemetry('LEO2-B', 0, 23.0, 1.3, 0.01, 100.0, 0.05),
        }
        st = {l: LinkState(link_id=l, trust=0.95, anomaly=0.0, isolated=False) for l in tel}
        return tel, st

    def test_battery_drain_triggers_route_switch(self):
        tel, st = self._mock_telemetry_and_state()
        router = RouteEngine(ROUTES, enable_energy=True)
        assert router.active == 'R1'

        # Artificially deplete LEO1 battery (e.g. in eclipse under heavy tx)
        router.set_node_energy('LEO1', 0.10)
        router.set_node_energy('LEO2', 1.00)

        decision = router.decide(100, tel, st)
        # Should switch to R2 (LEO2) due to energy conservation
        assert decision.chosen == 'R2'
        assert router.active == 'R2'

    def test_solar_recharge_model(self):
        router = RouteEngine(ROUTES, enable_energy=True, drain_rate=0.01, recharge_rate=0.005)
        router.set_node_energy('LEO1', 0.50)
        router.set_node_energy('LEO2', 0.50)

        # LEO1 is active: drains; LEO2 is idle: recharges via solar panel
        router.step_energy(active_via='LEO1')
        energy = router.get_node_energy()
        assert energy['LEO1'] < 0.50
        assert energy['LEO2'] > 0.50


class TestLEACHMasterRotation:
    """Tests for Cluster Head / Crypto Session Master election."""

    def test_leach_threshold_formula(self):
        sec = SecurityEngine()
        p = 0.333
        t0 = sec.get_leach_threshold(p=p, round_num=0)
        assert t0 == pytest.approx(0.333, abs=0.01)
        # In later rounds within period, threshold increases
        t1 = sec.get_leach_threshold(p=p, round_num=1)
        assert t1 > t0

    def test_energy_trust_master_handover(self):
        sec = SecurityEngine()
        assert sec.session_master == 'GW'

        # If GW battery or trust is low, elect healthiest satellite
        energy_map = {'GW': 0.20, 'LEO1': 0.40, 'LEO2': 0.95}
        trust_map = {'GW': 0.50, 'LEO1': 0.90, 'LEO2': 0.95}

        new_master, rotated = sec.elect_session_master(
            t_ms=1000,
            round_num=1,
            energy_levels=energy_map,
            trust_levels=trust_map,
            mode='energy_trust'
        )
        assert new_master == 'LEO2'
        assert rotated is True
        assert sec.session_master == 'LEO2'

    def test_isolated_node_barred_from_master(self):
        sec = SecurityEngine()
        sec.isolated.append('LEO2')  # LEO2 is compromised / under EW attack

        energy_map = {'GW': 0.30, 'LEO1': 0.85, 'LEO2': 1.00}
        trust_map = {'GW': 0.70, 'LEO1': 0.90, 'LEO2': 0.10}

        new_master, _ = sec.elect_session_master(
            t_ms=2000,
            round_num=2,
            energy_levels=energy_map,
            trust_levels=trust_map,
            mode='energy_trust'
        )
        # LEO2 must NOT be chosen despite 1.0 energy because it is isolated!
        assert new_master == 'LEO1'


class TestControllerLEACHIntegration:
    """Full system test with all LEACH options active."""

    def test_controller_runs_with_all_leach_upgrades(self):
        c = Controller(
            seed=42,
            enable_energy=True,
            enable_aggregation=True,
            agg_window=4,
            enable_leach_rounds=True,
            round_ticks=20,
        )

        for _ in range(50):
            dec, ok, n = c.step(100)

        # Check telemetry aggregation occurred
        assert len(c.latest_aggregates) > 0
        assert c.aggregator.total_raw_bytes > 0
        assert c.aggregator.overall_compression_ratio > 0.0

        # Check energy tracking
        energy = c.router.get_node_energy()
        assert 'LEO1' in energy
        assert 'LEO2' in energy

        # Check master rotation executed at least once
        assert c._leach_round >= 2
