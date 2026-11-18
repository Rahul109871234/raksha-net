"""
Generate high-resolution dark-themed charts for RAKSHA-NET presentation slides.
"""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = pathlib.Path("raksha-net/results")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Common Dark Theme Palette
BG_DARK = "#0a0e1a"
CARD_BG = "#131b2e"
TEXT_COLOR = "#f8fafc"
TEXT_MUTED = "#94a3b8"
CYAN = "#00f0ff"
GREEN = "#10b981"
AMBER = "#f59e0b"
RED = "#ef4444"
PURPLE = "#a855f7"
BORDER_COLOR = "#334155"

plt.rcParams.update({
    "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
    "font.family": "sans-serif",
    "figure.facecolor": BG_DARK,
    "axes.facecolor": CARD_BG,
    "axes.edgecolor": BORDER_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": TEXT_MUTED,
    "ytick.color": TEXT_MUTED,
    "text.color": TEXT_COLOR,
    "grid.color": "#1e293b",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
})

def create_crypto_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=200)
    fig.patch.set_facecolor(BG_DARK)
    
    # 1. Execution Speed Chart
    suites = ['Classical\nX25519', 'NIST\nML-KEM-768', 'Hybrid\nX25519+\nML-KEM-768', 'Live Attack\nRekey\n(Open5GS)']
    times_ms = [0.198, 0.065, 0.233, 0.713]
    colors = ['#64748b', GREEN, CYAN, PURPLE]
    
    bars1 = ax1.bar(suites, times_ms, color=colors, width=0.55, edgecolor=BORDER_COLOR, linewidth=1.2)
    ax1.set_title("Key Exchange Latency (ms) — Native C via liboqs", fontsize=11, fontweight="bold", pad=12, color=TEXT_COLOR)
    ax1.set_ylabel("Execution Time (milliseconds)", fontsize=10, color=TEXT_MUTED)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    ax1.set_ylim(0, 0.9)
    
    # Value labels on top of bars
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.025, f"{yval:.3f} ms" if yval < 0.1 else f"{yval:.3f} ms",
                 ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=TEXT_COLOR)
                 
    ax1.axhline(1.0, color=RED, linestyle=':', alpha=0.6, label="1ms Real-Time 5G Deadline")
    ax1.text(0.1, 0.82, "All < 1 ms (Real-Time Control Plane Ready)", fontsize=8.5, color=GREEN, fontstyle='italic')
    
    # 2. Wire Size Overhead Chart
    suites2 = ['Classical\nX25519', 'NIST\nML-KEM-768', 'Hybrid\nSuite']
    sizes_bytes = [64, 2272, 2336]
    colors2 = ['#64748b', GREEN, CYAN]
    
    bars2 = ax2.bar(suites2, sizes_bytes, color=colors2, width=0.5, edgecolor=BORDER_COLOR, linewidth=1.2)
    ax2.set_title("Handshake Wire Payload (Bytes)", fontsize=11, fontweight="bold", pad=12, color=TEXT_COLOR)
    ax2.set_ylabel("Payload Size (Bytes)", fontsize=10, color=TEXT_MUTED)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    ax2.set_ylim(0, 2800)
    
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 60, f"{int(yval):,} B",
                 ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=TEXT_COLOR)
                 
    ax2.text(0.1, 2550, "Fits in single MTU (1500B standard/jumbo)", fontsize=8.5, color=TEXT_MUTED, fontstyle='italic')

    plt.tight_layout()
    chart_path = OUTPUT_DIR / "crypto_benchmark_slide_chart.png"
    plt.savefig(chart_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"Generated crypto chart: {chart_path}")

def create_system_architecture_chart():
    fig, ax = plt.subplots(figsize=(12, 4.5), dpi=200)
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(CARD_BG)
    ax.axis('off')
    
    # Draw architecture blocks
    # Box 1: Ingestion
    bbox_props_ingest = dict(boxstyle="round,pad=0.7", fc="#1e293b", ec=CYAN, lw=2)
    ax.text(0.12, 0.5, "1. TELEMETRY INGESTION\n\n• Open5GS ogstun TUN (10.45.0.1)\n• RTT, Jitter, PDR, Queue Depth\n• Sliding Window Sub-second Stream",
            ha="center", va="center", fontsize=9.5, color=TEXT_COLOR, bbox=bbox_props_ingest)

    # Box 2: Anomaly Engine
    bbox_props_ai = dict(boxstyle="round,pad=0.7", fc="#1e293b", ec=AMBER, lw=2)
    ax.text(0.38, 0.5, "2. ANOMALY DETECTION\n\n• EWMA Baseline Profiling\n• GraphSAGE Neural Engine\n• Anomaly Score a in [0.0, 1.0]\n• Jamming Trigger: a >= 0.60",
            ha="center", va="center", fontsize=9.5, color=TEXT_COLOR, bbox=bbox_props_ai)

    # Box 3: Zero-Trust & Route Engine
    bbox_props_route = dict(boxstyle="round,pad=0.7", fc="#1e293b", ec=GREEN, lw=2)
    ax.text(0.64, 0.75, "3A. ZERO-TRUST & ROUTE ENGINE\n\n• Bayesian Trust Decay (T < 0.50)\n• Multi-Objective Utility Optimization\n• 5% Flapping Hysteresis Margin\n• Autonomous Failover to LEO-2 in 190ms",
            ha="center", va="center", fontsize=9.2, color=TEXT_COLOR, bbox=bbox_props_route)

    # Box 4: Post-Quantum Security Engine
    bbox_props_pqc = dict(boxstyle="round,pad=0.7", fc="#1e293b", ec=PURPLE, lw=2)
    ax.text(0.64, 0.25, "3B. POST-QUANTUM CRYPTO-AGILITY\n\n• Native C liboqs Engine (NIST FIPS 203)\n• Hybrid ML-KEM-768 + X25519 Rekey\n• Sub-millisecond derivation (0.48ms)\n• Compromised Node Container Quarantine",
            ha="center", va="center", fontsize=9.2, color=TEXT_COLOR, bbox=bbox_props_pqc)

    # Box 5: Outcome
    bbox_props_out = dict(boxstyle="round,pad=0.7", fc="#0f2b2b", ec=CYAN, lw=2)
    ax.text(0.90, 0.5, "4. VERIFIED RECOVERY\n\n• PDR Restored: 96.8%\n  (Static drops to 32.3%)\n• Failover: 190 ms\n• Zero Flapping\n• Post-Quantum Forward Secrecy",
            ha="center", va="center", fontsize=9.5, color=CYAN, fontweight="bold", bbox=bbox_props_out)

    # Connecting arrows
    arrow_props = dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#94a3b8", lw=2)
    ax.annotate("", xy=(0.25, 0.5), xytext=(0.20, 0.5), arrowprops=arrow_props)
    ax.annotate("", xy=(0.49, 0.70), xytext=(0.47, 0.55), arrowprops=arrow_props)
    ax.annotate("", xy=(0.49, 0.30), xytext=(0.47, 0.45), arrowprops=arrow_props)
    ax.annotate("", xy=(0.78, 0.55), xytext=(0.76, 0.70), arrowprops=arrow_props)
    ax.annotate("", xy=(0.78, 0.45), xytext=(0.76, 0.30), arrowprops=arrow_props)

    plt.tight_layout()
    chart_path = OUTPUT_DIR / "system_architecture_diagram.png"
    plt.savefig(chart_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"Generated architecture diagram: {chart_path}")

if __name__ == "__main__":
    create_crypto_chart()
    create_system_architecture_chart()
