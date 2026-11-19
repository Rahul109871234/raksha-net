# RAKSHA-NET Security Architecture & Threat Model

**Document ID:** `TM-RAKSHA-NET-2026-V1`  
**Classification:** Open Research Specification (TRL-4)  
**Authors:** G. Rahul Reddy & Dr. Satish Kumar Tiwari, PDPM IIITDM Jabalpur  

---

## 1. System Scope & Trust Boundaries

RAKSHA-NET operates as a software-defined controller coordinating O-RAN Near-RT RIC edge analytics and Non-Terrestrial Network (NTN) satellite backhaul resilience.

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │ UNTRUSTED ENVIRONMENT: RF & Terrestrial Edge                            │
 │  • Adversarial UEs / compromised gNBs (False Data Injection)           │
 │  • Electronic Warfare (High-power RF Jamming on Satellite Uplink)       │
 │  • Eavesdroppers recording ciphertext for quantum cryptanalysis (HNDL) │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Telemetry / Encrypted Traffic
 ┌───────────────────────────────────▼────────────────────────────────────┐
 │ TRUST BOUNDARY: Containerized Edge / Gateway Controller                │
 │  • Linux Network Namespaces (`ogstun`, Docker virtual switches)        │
 │  • Near-RT RIC Anomaly & Policy Arbitration (AICOP Engine)             │
 │  • Cryptographic Agility & Key Management Engine (security_engine.py)  │
 └────────────────────────────────────────────────────────────────────────┘
```

### 1.1 Assumptions
1. **Host Integrity:** The host executing the controller daemon (Docker host or Linux kernel) is trusted. Attacks targeting host kernel privilege escalation or hypervisor escape are out of scope.
2. **Standard Cryptographic Primitives:** NIST FIPS 203 (ML-KEM-768), RFC 7748 (X25519), and RFC 8439 (ChaCha20-Poly1305) / FIPS 197 (AES-256-GCM) are assumed computationally secure against classical and quantum adversaries within their specified security levels.
3. **Synchronized Clocks:** Controller nodes maintain relative temporal ordering via monotonic clocks (`time.perf_counter`) to prevent replay of expired telemetry.

---

## 2. Threat Analysis (STRIDE Taxonomy)

| Threat Category | Specific Attack Vector | System Impact | Mitigation in RAKSHA-NET |
| :--- | :--- | :--- | :--- |
| **Spoofing (S)** | False Data Injection (FDI) at terrestrial gNB reporting falsified low load ($18\%$) to force capacity cells to sleep. | Service Level Agreement (SLA) violation on active subscribers ($55.4\%$ unmanaged collapse). | **Inductive GraphSAGE + Spatial Neighbor Consensus:** Cross-validates reported metrics against physical 1-hop spatial neighbor medians. Compares with temporal EWMA. |
| **Tampering (T)** | In-flight telemetry alteration or intentional bit flips on satellite backhaul. | Unwarranted rerouting or silent packet corruption. | **Authenticated Encryption (AEAD):** Every payload carries Poly1305 or GCM authentication tag. Any tampering triggers immediate `InvalidTag` drop and link isolation. |
| **Repudiation (R)** | Malicious cell claims legitimate state transitions or denies causing flapping. | Hard to audit cascading cell shutdowns. | **Immutable State Machine Logging:** Controller logs every route score transition, hysteresis barrier activation, and trust decay event to structured `events.jsonl`. |
| **Information Disclosure (I)** | Passive interception of satellite feeder links under *"Harvest Now, Decrypt Later"* (HNDL). | Future exposure of classified/tactical telemetry once quantum computers mature. | **Post-Quantum Hybrid IKEv2 (RFC 9370):** Combines classical X25519 with NIST FIPS 203 ML-KEM-768. Even if classical discrete logs are broken retroactively, ML-KEM ensures confidentiality. |
| **Denial of Service (D)** | **1. High-Power RF Jamming:** Slashes packet delivery to $<30\%$.<br>**2. Threshold Dithering:** Oscillating link quality around the threshold to cause continuous route flapping. | Communication blackout or route table thrashing. | **1. Page's CUSUM Detector:** Rapidly detects persistent distribution shift ($k=0.5, h=2.0$).<br>**2. 5% Hysteresis Barrier:** Suppresses flap oscillations ($0.71 \pm 0.82$ flaps vs naive $18.3 \pm 3.5$). |
| **Elevation of Privilege (E)** | Compromise of an individual satellite relay interface. | Lateral movement across multi-hop network. | **Container-Native Sandboxing:** Relays operate in distinct Linux network namespaces. Controller programmatically quarantines compromised interfaces. |

---

## 3. Cryptographic Lifecycle & Key Management

### 3.1 Key Exchange Architecture
- **Protocol:** Dual-hybrid encapsulation conforming to **IETF RFC 9370** (*Multiple Key Exchanges in IKEv2*).
- **Primitives:**
  - Classical: ECDH X25519 (32-byte public key, 32-byte shared secret).
  - Post-Quantum: ML-KEM-768 (1,184-byte public key, 1,088-byte ciphertext, 32-byte shared secret).
- **Key Derivation:**
  $$K_{\text{session}} = \text{HKDF-Extract-and-Expand}\left(\text{salt}=\text{sid}, \text{IKM} = ss_{\text{classical}} \parallel ss_{\text{pqc}}, \text{info}=\text{"RAKSHA-NET-AEAD-KEY"}, L=32\right)$$
  Both key exchanges must be simultaneously compromised to recover the session key.

### 3.2 Rekeying & Forward Secrecy Policy
- **Trigger Conditions:**
  1. Link Anomaly Score $a_t \ge 0.60$ (immediate pre-emptive rekey).
  2. Route Failover event (isolation of compromised path and migration to backup route).
  3. Traffic volume threshold ($2^{32}$ packets) or time-based expiry (standard 3,600s).
- **Anti-Replay Mechanism:** AEAD nonces are strictly monotonic 96-bit counters incremented per packet. Duplicate or out-of-window nonces are discarded.

---

## 4. Known Implementation Boundaries & Side-Channel Disclosure

1. **Python vs. Hardware Execution:**
   - In the reference software prototype, cryptographic wrappers run within the Python runtime. While underlying C libraries (`liboqs` and `cryptography`/OpenSSL) implement constant-time algorithms, Python-level orchestration is subject to timing variations.
   - For mission-critical production deployment, controller modules should be embedded in native Rust/C micro-services or dedicated Hardware Security Modules (HSMs).
2. **Crypto Backend Fallback:**
   - On systems without compiled C `liboqs` binaries (e.g., bare Windows environments), the controller falls back to a verified `MOCK` implementation.
   - *Operational Rule:* Production deployments require verified Linux environments with native `liboqs` enabled (`scripts/install_liboqs.sh`).
3. **Out-of-Scope Adversary Capabilities:**
   - Physical satellite kinetic anti-satellite (ASAT) attacks.
   - Direct physical compromise of host memory (e.g. cold-boot attacks).
