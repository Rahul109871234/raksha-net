"""
emulator/gnuradio_backend.py
============================
GNU Radio <-> RAKSHA-NET ZeroMQ (ZMQ) Telemetry & Control Bridge.

This module connects RAKSHA-NET to physical Software-Defined Radios (SDRs)
like HackRF One, USRP B210, and ADALM-PLUTO running GNU Radio flowgraphs.

Architecture:
  [SDR Antenna / RF Front-End]
              │
              ▼
    GNU Radio Flowgraph (.grc)
      ├─ Demodulator / Decimator (measure RSSI, SNR, Packet Error Rate)
      ├─ ZMQ PUB Sink (tcp://127.0.0.1:5555) ───► Telemetry stream (JSON)
      └─ ZMQ SUB Source (tcp://127.0.0.1:5556) ◄── Control commands (Freq Hop / Failover)
              │
              ▼
      GnuRadioBackend (Python)
              │ (feeds sample() -> LinkTelemetry)
              ▼
   RAKSHA-NET Controller
      ├─ Anomaly Detection (EWMA > 0.60 when RF jamming strikes)
      ├─ Zero-Trust Failover (190ms migration to healthy backup link)
      └─ NIST ML-KEM-768 Native C Post-Quantum Rekeying & Quarantine
"""
from __future__ import annotations

import json
import logging
import threading
import time
from typing import Dict, List, Optional

from common.interfaces import LinkTelemetry

log = logging.getLogger("raksha.gnuradio")

# Standard ports for GNU Radio ZMQ blocks
DEFAULT_TELEMETRY_PORT = 5555  # GNU Radio ZMQ PUB Sink
DEFAULT_CONTROL_PORT   = 5556  # GNU Radio ZMQ SUB Source

class GnuRadioBackend:
    """
    SDR Telemetry backend connecting RAKSHA-NET to live GNU Radio flowgraphs.
    Drop-in replacement for NetworkEmulator and Open5GSBackend.
    """

    def __init__(
        self,
        link_ids: Optional[List[str]] = None,
        telemetry_addr: str = f"tcp://127.0.0.1:{DEFAULT_TELEMETRY_PORT}",
        control_addr: str = f"tcp://127.0.0.1:{DEFAULT_CONTROL_PORT}",
        fallback_baseline: bool = True,
    ):
        self.link_ids = link_ids or ["A-GW", "GW-LEO1", "GW-LEO2", "LEO1-B", "LEO2-B"]
        self.telemetry_addr = telemetry_addr
        self.control_addr = control_addr
        self.fallback_baseline = fallback_baseline

        self._lock = threading.Lock()
        self._cache: Dict[str, Dict] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

        self._zmq_sub = None
        self._zmq_pub = None

        # Nominal RF link baseline (fallback if GNU Radio stream is not yet active)
        for lid in self.link_ids:
            self._cache[lid] = {
                "latency_ms": 20.0,
                "jitter_ms": 1.5,
                "loss": 0.01,
                "throughput_mbps": 45.0,
                "queue_depth": 0.1,
                "snr_db": 22.0,
                "rssi_dbm": -45.0,
            }

        self._init_zmq()

    def _init_zmq(self):
        """Initialize ZeroMQ subscriber and publisher sockets if pyzmq is available."""
        try:
            import zmq
            self._zmq_ctx = zmq.Context()
            
            # Telemetry Subscriber (Reads from GNU Radio)
            self._zmq_sub = self._zmq_ctx.socket(zmq.SUB)
            self._zmq_sub.connect(self.telemetry_addr)
            self._zmq_sub.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all topics
            self._zmq_sub.RCVTIMEO = 200  # 200ms non-blocking timeout

            # Command Publisher (Sends control back to GNU Radio)
            self._zmq_pub = self._zmq_ctx.socket(zmq.PUB)
            self._zmq_pub.bind(self.control_addr)

            self._running = True
            self._thread = threading.Thread(target=self._telemetry_listener, daemon=True)
            self._thread.start()
            log.info("[GnuRadioBackend] Connected to ZMQ telemetry at %s", self.telemetry_addr)
        except ImportError:
            log.warning("[GnuRadioBackend] pyzmq not installed; running in simulated SDR fallback mode.")
        except Exception as e:
            log.warning("[GnuRadioBackend] Could not connect to ZMQ: %s. Using cached RF telemetry.", e)

    def _telemetry_listener(self):
        """Background thread listening for live RF telemetry messages from GNU Radio."""
        while self._running:
            try:
                raw_msg = self._zmq_sub.recv_string()
                data = json.loads(raw_msg)
                link_id = data.get("link_id")
                if link_id in self.link_ids:
                    with self._lock:
                        self._cache[link_id].update(data)
            except Exception:
                # Timeout or empty buffer, continue loop
                pass

    def sample(self, link_id: str) -> LinkTelemetry:
        """Sample current physical RF telemetry for link_id (consumed by RAKSHA-NET Controller)."""
        with self._lock:
            stats = self._cache.get(link_id, {
                "latency_ms": 20.0,
                "jitter_ms": 1.5,
                "loss": 0.01,
                "throughput_mbps": 40.0,
                "queue_depth": 0.1,
            })
        return LinkTelemetry(
            link_id=link_id,
            t_ms=int(time.time() * 1000),
            latency_ms=float(stats.get("latency_ms", 20.0)),
            jitter_ms=float(stats.get("jitter_ms", 1.5)),
            loss=float(stats.get("loss", 0.01)),
            throughput_mbps=float(stats.get("throughput_mbps", 40.0)),
            queue_depth=float(stats.get("queue_depth", 0.1)),
        )

    def send_sdr_command(self, action: str, params: Optional[dict] = None):
        """
        Send a real-time control command back to the GNU Radio flowgraph.
        Actions include:
          - 'frequency_hop': Hop carrier frequency to evade active RF jamming
          - 'route_switch': Switch active TX/RX frequency or antenna port to backup satellite
          - 'gain_adjust': Increase LNA/VGA receiver gain
        """
        if self._zmq_pub is not None:
            cmd = json.dumps({"action": action, "params": params or {}, "timestamp": time.time()})
            try:
                self._zmq_pub.send_string(cmd)
                log.info("[GnuRadioBackend] Sent SDR control command: %s", action)
            except Exception as e:
                log.warning("[GnuRadioBackend] Failed to send SDR command: %s", e)

    def set_profile(self, link_id: str, profile: str):
        """Simulate or inject RF impairments for testing."""
        if profile == "severe":
            with self._lock:
                self._cache[link_id] = {
                    "latency_ms": 170.0,
                    "jitter_ms": 45.0,
                    "loss": 0.42,
                    "throughput_mbps": 8.0,
                    "queue_depth": 0.9,
                    "snr_db": 2.1,  # Jammer submerged SNR
                }
            self.send_sdr_command("jamming_alert", {"link_id": link_id})
        elif profile == "normal":
            with self._lock:
                self._cache[link_id] = {
                    "latency_ms": 20.0,
                    "jitter_ms": 1.5,
                    "loss": 0.01,
                    "throughput_mbps": 48.0,
                    "queue_depth": 0.1,
                    "snr_db": 24.5,
                }
            self.send_sdr_command("channel_restored", {"link_id": link_id})

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
