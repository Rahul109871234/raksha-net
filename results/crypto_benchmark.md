# Crypto-Agility Benchmark

> **Emulated testbed.** Handshake / AEAD timings are wall-clock on the
> machine that ran the script (Python). Transmit times are bandwidth-only
> estimates (bytes*8/bw), not measured network RTT.

**Backend:** liboqs-ML-KEM-768 | **Repetitions:** 200

| Suite | Key exchange | AEAD | Handshake bytes | Handshake mean (ms) | SD | p95 | AEAD MB/s (1 KiB) | tx @1 Mbps (ms) | tx @8 Mbps (ms) | tx @50 Mbps (ms) | Real? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CLASSICAL_CHACHA | X25519 | ChaCha20-Poly1305 | 64 | 0.12 | 0.009 | 0.135 | 55.6 | 0.512 | 0.064 | 0.01 | yes |
| PQC_CHACHA | ML-KEM-768 | ChaCha20-Poly1305 | 2272 | 0.045 | 0.004 | 0.053 | 57.4 | 18.176 | 2.272 | 0.364 | yes |
| PQC_AES | ML-KEM-768 | AES-256-GCM | 2272 | 0.045 | 0.004 | 0.055 | 74.3 | 18.176 | 2.272 | 0.364 | yes |
| HYBRID_CHACHA | X25519+ML-KEM-768 | ChaCha20-Poly1305 | 2336 | 0.167 | 0.008 | 0.182 | 56.8 | 18.688 | 2.336 | 0.374 | yes |
| HYBRID_AES | X25519+ML-KEM-768 | AES-256-GCM | 2336 | 0.167 | 0.009 | 0.186 | 74.1 | 18.688 | 2.336 | 0.374 | yes |

## Policy

- Threat -> hybrid (X25519 + ML-KEM-768).
- No threat -> ML-KEM-768 alone.
- AEAD: ChaCha20-Poly1305 below 30 Mbps, AES-256-GCM at or above.
- X25519-only below 10 Mbps only if `allow_classical=True` (not PQ-safe).

