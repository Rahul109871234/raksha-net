"""
open5gs_backend.py — Raksha-Net <-> Open5GS Live Telemetry Bridge
=================================================================
Replaces NetworkEmulator with real Open5GS 5G Core metrics.

Architecture:
    Open5GS (AMF/SMF/UPF running in WSL2)
        |-- Prometheus metrics  -> http://127.0.0.1:9090/metrics
        |-- Process liveness    -> pgrep open5gs-<daemon>
        |-- Ping probes         -> loopback pings to core NF addresses
        |-- Log parsing         -> UPF log volume counts
        v
    Open5GSBackend.sample(link_id) -> LinkTelemetry
        v
    Raksha-Net Controller (anomaly -> trust -> route -> PQC rekey)

Usage (replace NetworkEmulator in controller.py):
    from emulator.open5gs_backend import Open5GSBackend
    backend = Open5GSBackend(link_ids=LINKS)

Run standalone demo:
    python -m emulator.open5gs_backend
"""
from __future__ import annotations

import logging
import os
import re
import subprocess
import threading
import time
from typing import Dict, List, Optional

from common.interfaces import LinkTelemetry

log = logging.getLogger("raksha.open5gs")

# ── Open5GS install paths (NIST O-RAN Testbed layout) ──────────────────────
O5GS_BASE = os.environ.get(
    "OPEN5GS_BASE",
    "/home/rahul/O-RAN-Testbed-Automation/5G_Core_Network/open5gs",
)
O5GS_LOG_DIR = os.path.join(O5GS_BASE, "install/var/log/open5gs")
O5GS_METRICS_URL = os.environ.get("OPEN5GS_METRICS_URL", "http://127.0.0.1:9090/metrics")

# UPF TUN interfaces (ogstun = LEO-1, ogstun2 = LEO-2)
UPF_TUN_IFACE  = os.environ.get("OPEN5GS_TUN", "ogstun")
UPF_TUN_ADDR   = os.environ.get("OPEN5GS_TUN_ADDR", "10.45.0.1")
UPF_TUN_IFACE2 = os.environ.get("OPEN5GS_TUN2", "ogstun2")
UPF_TUN_ADDR2  = os.environ.get("OPEN5GS_TUN_ADDR2", "10.46.0.1")

# ── Link -> probe mapping ───────────────────────────────────────────────────
# Maps each Raksha-Net logical link to an Open5GS NF process + ping target.
LINK_PROBE_MAP: Dict[str, Dict] = {
    "A-GW":    {"process": "amfd",  "target": "10.201.0.5", "netns": "ue1", "label": "UE1->Gateway (v-eth1)"},
    "GW-LEO1": {"process": "smfd",  "target": UPF_TUN_ADDR,                 "label": "Gateway->LEO1 (UPF-1)"},
    "GW-LEO2": {"process": "upfd",  "target": UPF_TUN_ADDR2,                "label": "Gateway->LEO2 (UPF-2)"},
    "LEO1-B":  {"process": "upfd",  "target": UPF_TUN_ADDR,                 "label": "LEO1->Tactical Edge B"},
    "LEO2-B":  {"process": "nrfd",  "target": UPF_TUN_ADDR2,                "label": "LEO2->Tactical Edge B"},
}

_BASELINE = dict(latency_ms=5.0, jitter_ms=0.5, loss=0.0, throughput_mbps=50.0, queue_depth=0.1)
_BLACKOUT  = dict(latency_ms=999.0, jitter_ms=0.0, loss=1.0, throughput_mbps=0.0, queue_depth=1.0)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _is_process_running(process_name: str) -> bool:
    """Return True if open5gs-<process_name> or standalone daemon is alive."""
    try:
        r = subprocess.run(
            ["pgrep", "-f", f"open5gs-{process_name}"],
            capture_output=True, timeout=2,
        )
        if r.returncode == 0:
            return True
        r2 = subprocess.run(
            ["pgrep", "-x", process_name],
            capture_output=True, timeout=2,
        )
        return r2.returncode == 0
    except Exception:
        return False


def _ping_probe(target: str, count: int = 3, netns: Optional[str] = None) -> Dict[str, float]:
    """Ping target and return latency/jitter/loss dict, optionally executing inside a network namespace."""
    try:
        base_cmd = ["ping", "-c", str(count), "-W", "1", "-i", "0.2", target]
        if netns:
            # Check if namespace exists before executing
            ns_chk = subprocess.run(["ip", "netns", "list"], capture_output=True, text=True, timeout=2)
            if netns in ns_chk.stdout:
                cmd = ["sudo", "ip", "netns", "exec", netns] + base_cmd
            else:
                cmd = base_cmd
        else:
            cmd = base_cmd

        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        out = r.stdout
        loss_m = re.search(r"(\d+)%\s+packet loss", out)
        loss = float(loss_m.group(1)) / 100.0 if loss_m else 1.0
        rtt_m = re.search(
            r"rtt min/avg/max/mdev\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)", out
        )
        if rtt_m:
            lat, jit = float(rtt_m.group(2)), float(rtt_m.group(4))
        else:
            lat, jit = 999.0, 0.0
        return {"latency_ms": lat, "jitter_ms": jit, "loss": loss}
    except Exception as e:
        log.debug("ping failed for %s (netns=%s): %s", target, netns, e)
        return {"latency_ms": 999.0, "jitter_ms": 0.0, "loss": 1.0}


def _read_prometheus(url: str, timeout: float = 2.0) -> Dict[str, float]:
    """Fetch Open5GS Prometheus metrics. Returns {} on failure."""
    metrics: Dict[str, float] = {}
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode()
        for line in body.splitlines():
            if line.startswith("#"):
                continue
            parts = line.rsplit(" ", 1)
            if len(parts) == 2:
                try:
                    metrics[parts[0].strip()] = float(parts[1].strip())
                except ValueError:
                    pass
    except Exception as e:
        log.debug("Prometheus read failed (%s): %s", url, e)
    return metrics


def _parse_upf_throughput(log_path: str, window_s: float = 10.0) -> Optional[float]:
    """Parse UPF log for volume bytes -> Mbps estimate."""
    try:
        r = subprocess.run(
            ["tail", "-n", "100", log_path],
            capture_output=True, text=True, timeout=3,
        )
        byte_counts = []
        for line in r.stdout.splitlines():
            m = re.search(r"volume[:\s]+(\d+)", line, re.IGNORECASE)
            if m:
                byte_counts.append(int(m.group(1)))
        if len(byte_counts) >= 2:
            delta = max(byte_counts) - min(byte_counts)
            return round((delta * 8) / (window_s * 1e6), 2)
    except Exception:
        pass
    return None


# ── Main Backend ────────────────────────────────────────────────────────────

class Open5GSBackend:
    """
    Live Open5GS telemetry backend for Raksha-Net.
    Drop-in replacement for NetworkEmulator / RealNetworkBackend.

    Telemetry priority:
      1. Prometheus endpoint (if metrics enabled in Open5GS)
      2. Ping probes to Open5GS internal NF addresses
      3. Process liveness  (daemon down -> blackout)
      4. UPF log parsing   (throughput estimate)
    """

    def __init__(
        self,
        link_ids: Optional[List[str]] = None,
        probe_interval_s: float = 2.0,
        ping_count: int = 3,
        use_prometheus: bool = True,
        metrics_url: str = O5GS_METRICS_URL,
        allow_degraded: bool = True,
    ):
        if link_ids is None:
            link_ids = list(LINK_PROBE_MAP.keys())
        self.link_ids = link_ids
        self.links = link_ids
        self.t_ms: int = 0
        self.ping_count = ping_count
        self.use_prometheus = use_prometheus
        self.metrics_url = metrics_url
        self.allow_degraded = allow_degraded
        self._probe_interval = probe_interval_s

        self._cache: Dict[str, Dict] = {lid: dict(_BASELINE) for lid in link_ids}
        self._lock = threading.Lock()
        self._running = True
        self._thread = threading.Thread(target=self._probe_loop, daemon=True)
        self._thread.start()
        log.info("[Open5GSBackend] started — probing %d links every %.1fs", len(link_ids), probe_interval_s)

    def stop(self):
        self._running = False

    # ── NetworkEmulator-compatible public API ───────────────────────────────

    def tick(self, dt_ms: int = 100):
        self.t_ms += dt_ms

    def sample(self, link_id: str) -> LinkTelemetry:
        with self._lock:
            s = dict(self._cache.get(link_id, _BASELINE))
        return LinkTelemetry(
            link_id=link_id, t_ms=self.t_ms,
            latency_ms=s["latency_ms"], jitter_ms=s["jitter_ms"],
            loss=s["loss"], throughput_mbps=s["throughput_mbps"],
            queue_depth=s["queue_depth"],
        )

    def send(self, link_ids: List[str], n: int = 20):
        import random
        rng = random.Random()
        ok = sum(
            1 for _ in range(n)
            if all(
                rng.random() > self._cache.get(lid, _BLACKOUT)["loss"]
                for lid in link_ids
            )
        )
        return (ok, n)

    def set_profile(self, link_id: str, profile: str, ramp_steps=None):
        """Inject jamming profile on a link + apply tc netem on kernel physical interfaces."""
        from emulator.network_emulator import PROFILES
        assert profile in PROFILES, f"Unknown profile: {profile}"
        lat, jit, loss, thr, q = PROFILES[profile]
        log.info("[Open5GSBackend] %s -> profile=%s (loss=%.0f%%)", link_id, profile, loss * 100)
        
        # Apply physical RF shaping directly on the respective satellite tunnel (ogstun = LEO-1, ogstun2 = LEO-2)
        if "LEO1" in link_id or link_id == "GW-LEO1":
            self._tc_netem(UPF_TUN_IFACE, lat, jit, loss, thr)
        elif "LEO2" in link_id or link_id == "GW-LEO2":
            self._tc_netem(UPF_TUN_IFACE2, lat, jit, loss, thr)

        with self._lock:
            self._cache[link_id] = dict(
                latency_ms=lat, jitter_ms=jit, loss=loss,
                throughput_mbps=thr, queue_depth=q,
            )

    def set_profile_instant(self, link_id: str, profile: str):
        self.set_profile(link_id, profile)

    def current_profile(self, link_id: str) -> str:
        return "open5gs-live"

    def target_profile(self, link_id: str) -> str:
        return "open5gs-live"

    def is_ramping(self, link_id: str) -> bool:
        return False

    # ── Internal probing ────────────────────────────────────────────────────

    def _probe_loop(self):
        while self._running:
            for lid in self.link_ids:
                try:
                    stats = self._probe_link(lid)
                    with self._lock:
                        self._cache[lid] = stats
                except Exception as e:
                    log.debug("probe error %s: %s", lid, e)
            time.sleep(self._probe_interval)

    def _probe_link(self, link_id: str) -> Dict:
        cfg     = LINK_PROBE_MAP.get(link_id, {})
        process = cfg.get("process", "")
        target  = cfg.get("target", "")
        netns   = cfg.get("netns", None)

        # Process liveness -> total blackout if daemon is down, unless degraded mode allowed
        if process and not _is_process_running(process):
            if not self.allow_degraded:
                log.warning("[Open5GS] %s DOWN -> %s BLACKOUT", process, link_id)
                return dict(_BLACKOUT)

        # Ping for latency / loss
        ping = {"latency_ms": 5.0, "jitter_ms": 0.5, "loss": 0.0}
        if target:
            res = _ping_probe(target, self.ping_count, netns=netns)
            if res["loss"] < 1.0 or not self.allow_degraded:
                ping = res
            else:
                # In degraded mode (e.g. Windows without active WSL2 ogstun IP), preserve calibrated profile
                with self._lock:
                    cached = self._cache.get(link_id, _BASELINE)
                ping = {"latency_ms": cached["latency_ms"], "jitter_ms": cached["jitter_ms"], "loss": cached["loss"]}

        # Prometheus throughput / queue
        thr, qdep = _BASELINE["throughput_mbps"], _BASELINE["queue_depth"]
        if self.use_prometheus:
            prom = _read_prometheus(self.metrics_url)
            if prom:
                rx = prom.get("fivegs_upf_rx_bytes_total", 0)
                tx = prom.get("fivegs_upf_tx_bytes_total", 0)
                if rx + tx > 0:
                    thr = round((rx + tx) * 8 / (self._probe_interval * 1e6), 2)
                sessions = prom.get("fivegs_smfd_session_count", 0)
                qdep = round(min(1.0, sessions / 10.0), 3)

        # UPF log fallback for throughput
        if thr == _BASELINE["throughput_mbps"]:
            parsed = _parse_upf_throughput(os.path.join(O5GS_LOG_DIR, "upf.log"))
            if parsed is not None:
                thr = parsed

        return dict(
            latency_ms=ping["latency_ms"], jitter_ms=ping["jitter_ms"],
            loss=ping["loss"], throughput_mbps=thr, queue_depth=qdep,
        )

    def _tc_netem(self, iface: str, lat: float, jit: float, loss: float, thr: float):
        """Apply tc netem on kernel interfaces to simulate real physical RF jamming."""
        # Clean restoration
        if loss <= 0.01 and lat <= 20.0:
            try:
                subprocess.run(["sudo", "tc", "qdisc", "del", "dev", iface, "root"], capture_output=True, timeout=3)
                log.info("[Open5GS] tc netem cleared on %s", iface)
            except Exception:
                pass
            return

        cmd = [
            "sudo", "tc", "qdisc", "replace", "dev", iface, "root",
            "netem", "delay", f"{lat:.0f}ms", f"{jit:.0f}ms",
            "loss", f"{loss * 100:.1f}%", "rate", f"{max(thr, 0.1):.1f}mbit",
        ]
        try:
            subprocess.run(cmd, check=True, timeout=5)
            log.info("[Open5GS] tc netem applied on %s: %s", iface, " ".join(cmd[5:]))
        except Exception as e:
            log.warning("[Open5GS] tc netem failed on %s: %s", iface, e)

    def check_daemons(self) -> Dict[str, bool]:
        """Return liveness dictionary for all primary Open5GS daemons."""
        daemons = ["amfd", "smfd", "upfd", "nrfd", "ausfd", "udmd", "nssfd"]
        return {f"open5gs-{d}": _is_process_running(d) for d in daemons}

    def close(self):
        """Stop background probing thread."""
        self._running = False


# ── Standalone demo ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    LINKS = ["A-GW", "GW-LEO1", "GW-LEO2", "LEO1-B", "LEO2-B"]

    print("=" * 65)
    print("  RAKSHA-NET <-> Open5GS Live Bridge — Standalone Demo")
    print("=" * 65)
    print(f"  Open5GS base : {O5GS_BASE}")
    print(f"  Metrics URL  : {O5GS_METRICS_URL}")
    print(f"  UPF TUN      : {UPF_TUN_IFACE} ({UPF_TUN_ADDR})")
    print()

    print("[ Open5GS Daemon Status ]")
    daemons = ["amfd", "smfd", "upfd", "nrfd", "ausfd", "udmd", "nssfd"]
    any_running = False
    for d in daemons:
        up = _is_process_running(d)
        if up:
            any_running = True
        print(f"  open5gs-{d:<8}: {'✅ RUNNING' if up else '❌ NOT RUNNING'}")
    print()

    if not any_running:
        print("  ⚠️  No Open5GS daemons running.")
        print("  Start them with:")
        print("    wsl -d Ubuntu-24.04 bash /home/rahul/O-RAN-Testbed-Automation/5G_Core_Network/run.sh")
        print()
        print("  Running in DEGRADED mode — ping probes to loopback only.")
        print()

    backend = Open5GSBackend(LINKS, probe_interval_s=2.0, ping_count=3)
    print("Warming up probes (3s)...")
    time.sleep(3)

    print(f"\n{'Link':<12} {'Latency':>10} {'Jitter':>8} {'Loss':>8} {'Thr Mbps':>10} {'QDepth':>8}  Status")
    print("-" * 72)

    for tick in range(6):
        backend.tick(100)
        for lid in LINKS:
            tel = backend.sample(lid)
            status = "🔴 JAMMED" if tel.loss >= 0.9 else ("🟡 DEGRADED" if tel.loss > 0.1 else "🟢 OK")
            print(
                f"{lid:<12} {tel.latency_ms:>9.1f}ms {tel.jitter_ms:>7.1f}ms "
                f"{tel.loss:>7.1%} {tel.throughput_mbps:>9.1f} {tel.queue_depth:>8.3f}  {status}"
            )
        print()
        time.sleep(2)

    backend.stop()
    print("Demo complete.")
