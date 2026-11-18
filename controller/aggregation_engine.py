from __future__ import annotations
import json, zlib
from collections import deque
from dataclasses import dataclass
from typing import Dict, Optional
from common.interfaces import LinkTelemetry

@dataclass
class AggregatedTelemetry:
    link_id: str
    window_size: int
    t_ms_start: int
    t_ms_end: int
    mean_latency: float
    mean_loss: float
    mean_throughput: float
    max_queue: float
    min_throughput: float
    anomaly_flag: bool
    compressed_bytes: int
    raw_bytes: int
    compression_ratio: float
    def bandwidth_saved_pct(self) -> float:
        return round(self.compression_ratio * 100, 1)

class AggregationEngine:
    def __init__(self, window: int = 5):
        assert window >= 2
        self._window = window
        self._buffers: Dict[str, deque] = {}
        self.total_raw_bytes = 0
        self.total_compressed_bytes = 0

    def ingest(self, tel: LinkTelemetry) -> Optional[AggregatedTelemetry]:
        lid = tel.link_id
        if lid not in self._buffers:
            self._buffers[lid] = deque(maxlen=self._window)
        self._buffers[lid].append(tel)
        if len(self._buffers[lid]) >= self._window:
            agg = self._aggregate(lid)
            self.total_raw_bytes += agg.raw_bytes
            self.total_compressed_bytes += agg.compressed_bytes
            return agg
        return None

    def _aggregate(self, link_id: str) -> AggregatedTelemetry:
        buf = list(self._buffers[link_id])
        n = len(buf)
        mean_lat  = sum(t.latency_ms for t in buf) / n
        mean_loss = sum(t.loss for t in buf) / n
        mean_thr  = sum(t.throughput_mbps for t in buf) / n
        min_thr   = min(t.throughput_mbps for t in buf)
        max_q     = max(t.queue_depth for t in buf)
        flag = any(t.loss > 0.20 or t.latency_ms > 70 or t.queue_depth > 0.5 for t in buf)
        rows = [dict(l=round(t.latency_ms,1), p=round(t.loss,4), b=round(t.throughput_mbps,1), q=round(t.queue_depth,3)) for t in buf]
        raw_payload = json.dumps(rows).encode()
        compressed = zlib.compress(raw_payload, level=6)
        ratio = 1.0 - len(compressed) / len(raw_payload)
        self._buffers[link_id].clear()
        return AggregatedTelemetry(
            link_id=link_id, window_size=n,
            t_ms_start=buf[0].t_ms, t_ms_end=buf[-1].t_ms,
            mean_latency=round(mean_lat,2), mean_loss=round(mean_loss,4),
            mean_throughput=round(mean_thr,2), min_throughput=round(min_thr,2),
            max_queue=round(max_q,3), anomaly_flag=flag,
            compressed_bytes=len(compressed), raw_bytes=len(raw_payload),
            compression_ratio=round(max(0.0,ratio),3),
        )

    @property
    def overall_compression_ratio(self) -> float:
        if self.total_raw_bytes == 0:
            return 0.0
        return round(1 - self.total_compressed_bytes / self.total_raw_bytes, 3)

    def bandwidth_saved_theoretical_pct(self) -> float:
        return round((self._window - 1) / self._window * 100, 1)
