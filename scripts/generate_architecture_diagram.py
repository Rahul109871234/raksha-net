#!/usr/bin/env python3
"""
generate_architecture_diagram.py
================================
Generates an ultra-crisp, publication-grade system architecture diagram for
AICOP-RAKSHA.
Renders to a 300-DPI high-contrast PNG image ready to be embedded into the PDF whitepaper.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_architecture(output_path):
    fig, ax = plt.subplots(figsize=(10.5, 6.4), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    # Colors
    c_tier3_bg = "#0F172A"      # Deep Navy/Slate
    c_tier2_bg = "#1E293B"      # Mid Slate
    c_tier1_bg = "#334155"      # Light Slate
    c_blue = "#0284C7"          # Primary Tech Blue
    c_cyan = "#06B6D4"          # Accent Cyan
    c_red = "#EF4444"           # Threat/Jamming Red
    c_green = "#10B981"         # Recovery/Safe Green
    c_purple = "#8B5CF6"        # Quantum/Crypto Purple
    c_yellow = "#F59E0B"        # Attention Amber
    c_text_bright = "#F8FAFC"
    c_text_dim = "#94A3B8"

    # =========================================================================
    # TIER 3: SPACE / SATELLITE NTN (RAKSHA-NET) [Y: 66 to 98]
    # =========================================================================
    box_t3 = patches.FancyBboxPatch(
        (2, 66), 96, 32,
        boxstyle="round,pad=0.8,rounding_size=2.0",
        facecolor=c_tier3_bg, edgecolor=c_blue, linewidth=2.0
    )
    ax.add_patch(box_t3)
    ax.text(4, 95, "TIER 3: SPACE / 5G NON-TERRESTRIAL NETWORK (NTN) & POST-QUANTUM SHIELD",
            fontsize=10.5, fontweight="bold", color=c_cyan, fontfamily="sans-serif")
    ax.text(4, 91.5, "Sub-second Autonomous Resilience Controller | Linux TUN interface (ogstun) | 3GPP Rel-17 Open5GS Core",
            fontsize=7.5, color=c_text_dim, fontfamily="sans-serif")

    # Satellite 1 (Jammed)
    sat1 = patches.FancyBboxPatch((5, 70), 26, 18, boxstyle="round,pad=0.5,rounding_size=1.2",
                                 facecolor="#1E1B4B", edgecolor=c_red, linewidth=1.8, linestyle="--")
    ax.add_patch(sat1)
    ax.text(18, 84, "LEO Satellite 1 (Primary)", fontsize=8.5, fontweight="bold", color=c_red, ha="center")
    ax.text(18, 79.5, "• RF Jamming Attack Injected", fontsize=7.2, color="#FCA5A5", ha="center")
    ax.text(18, 75.5, "• Packet Loss: 3.2% -> 67.7%", fontsize=7.2, color="#FCA5A5", ha="center")
    ax.text(18, 71.5, "• PDR Collapses to 32.3%", fontsize=7.2, fontweight="bold", color=c_red, ha="center")

    # Satellite 2 (Reserve / Restored)
    sat2 = patches.FancyBboxPatch((69, 70), 26, 18, boxstyle="round,pad=0.5,rounding_size=1.2",
                                 facecolor="#064E3B", edgecolor=c_green, linewidth=1.8)
    ax.add_patch(sat2)
    ax.text(82, 84, "LEO Satellite 2 (Strategic Reserve)", fontsize=8.5, fontweight="bold", color="#A7F3D0", ha="center")
    ax.text(82, 79.5, "• 190ms Autonomous Failover", fontsize=7.2, fontweight="bold", color="#34D399", ha="center")
    ax.text(82, 75.5, "• 5% Hysteresis (0% Flapping)", fontsize=7.2, color="#6EE7B7", ha="center")
    ax.text(82, 71.5, "• PDR Restored to 96.8%", fontsize=7.2, fontweight="bold", color=c_green, ha="center")

    # Core Security Engine (Middle of Tier 3)
    sec_box = patches.FancyBboxPatch((34, 69.5), 32, 19, boxstyle="round,pad=0.5,rounding_size=1.2",
                                    facecolor="#2E1065", edgecolor=c_purple, linewidth=1.8)
    ax.add_patch(sec_box)
    ax.text(50, 85, "RAKSHA-NET ENGINE", fontsize=9, fontweight="bold", color="#E9D5FF", ha="center")
    ax.text(50, 80.5, "• Page's CUSUM (22ms Primed / 42ms Cold)", fontsize=7.0, color="#DDD6FE", ha="center")
    ax.text(50, 76.5, "• NIST FIPS 203 ML-KEM-768", fontsize=7.5, fontweight="bold", color="#C084FC", ha="center")
    ax.text(50, 72.5, "• 45 us ML-KEM Encap / 167 us Hybrid", fontsize=7.0, color="#DDD6FE", ha="center")

    # Arrows between Satellites and Engine
    ax.annotate("", xy=(34, 78), xytext=(31, 78), arrowprops=dict(arrowstyle="->", color=c_red, lw=1.5))
    ax.annotate("", xy=(69, 78), xytext=(66, 78), arrowprops=dict(arrowstyle="->", color=c_green, lw=2.0))

    # =========================================================================
    # CROSS-LAYER BUS [Y: 57 to 64]
    # =========================================================================
    bus_box = patches.FancyBboxPatch(
        (10, 56.5), 80, 7.5,
        boxstyle="round,pad=0.4,rounding_size=1.0",
        facecolor="#0284C7", edgecolor="#38BDF8", linewidth=1.5
    )
    ax.add_patch(bus_box)
    ax.text(50, 61, "CROSS-LAYER TELEMETRY & THREAT PROPAGATION BUS",
            fontsize=8.5, fontweight="bold", color=c_text_bright, ha="center")
    ax.text(50, 58, "E2SM-KPM / E2SM-RC Interfaces | Real-time Terrestrial Cell Trust & Anomaly Feed",
            fontsize=7, color="#E0F2FE", ha="center")

    # Vertical Connecting Arrows
    ax.annotate("", xy=(50, 66), xytext=(50, 64), arrowprops=dict(arrowstyle="<->", color=c_cyan, lw=2))

    # =========================================================================
    # TIER 2: TERRESTRIAL O-RAN Near-RT RIC (AICOP) [Y: 26 to 54]
    # =========================================================================
    box_t2 = patches.FancyBboxPatch(
        (2, 26), 96, 28,
        boxstyle="round,pad=0.8,rounding_size=2.0",
        facecolor=c_tier2_bg, edgecolor=c_blue, linewidth=2.0
    )
    ax.add_patch(box_t2)
    ax.text(4, 51.5, "TIER 2: TERRESTRIAL O-RAN Near-RT RIC (AICOP SUBSYSTEM)",
            fontsize=10.5, fontweight="bold", color=c_cyan, fontfamily="sans-serif")
    ax.text(4, 48, "Inductive Spatial-Consensus Trust Inference & Multi-Objective xApp Conflict Arbitration",
            fontsize=7.5, color=c_text_dim, fontfamily="sans-serif")

    # Left: 2-Layer GraphSAGE Engine
    gs_box = patches.FancyBboxPatch((5, 29), 43, 16.5, boxstyle="round,pad=0.5,rounding_size=1.2",
                                   facecolor="#0F172A", edgecolor=c_blue, linewidth=1.5)
    ax.add_patch(gs_box)
    ax.text(26.5, 42, "Inductive 2-Layer GraphSAGE Engine", fontsize=8.5, fontweight="bold", color="#7DD3FC", ha="center")
    ax.text(26.5, 38, "• Pure NumPy Vector Formulation (<8.4ms, 0 GPU)", fontsize=7.2, color=c_text_bright, ha="center")
    ax.text(26.5, 34, "• Spatial Neighbor Consensus [W1, W2 Matrices]", fontsize=7.2, color=c_text_bright, ha="center")
    ax.text(26.5, 30.5, "• Detects False Data Injection (FDI) & Flapping", fontsize=7.2, fontweight="bold", color=c_yellow, ha="center")

    # Right: Pareto Conflict Arbiter
    pa_box = patches.FancyBboxPatch((52, 29), 43, 16.5, boxstyle="round,pad=0.5,rounding_size=1.2",
                                   facecolor="#0F172A", edgecolor=c_blue, linewidth=1.5)
    ax.add_patch(pa_box)
    ax.text(73.5, 42, "Trust-Weighted Pareto Policy Arbiter", fontsize=8.5, fontweight="bold", color="#7DD3FC", ha="center")
    ax.text(73.5, 38, "• Pacifista Conflict Veto: (TS > 0.05 & ES < 0)", fontsize=7.2, color=c_text_bright, ha="center")
    ax.text(73.5, 34, "• Quadratic Trust Penalty T(v)² Suppresses Sleep", fontsize=7.2, color=c_text_bright, ha="center")
    ax.text(73.5, 30.5, "• SLA Violations Cut to 5.88% (Beats PACIFISTA)", fontsize=7.2, fontweight="bold", color=c_green, ha="center")

    # Connection arrow between GraphSAGE and Arbiter
    ax.annotate("", xy=(52, 37), xytext=(48, 37), arrowprops=dict(arrowstyle="->", color=c_cyan, lw=1.8))
    # Vertical Connecting Arrows to Bus
    ax.annotate("", xy=(50, 56.5), xytext=(50, 54), arrowprops=dict(arrowstyle="<->", color=c_cyan, lw=2))

    # =========================================================================
    # TIER 1: PHYSICAL RADIO ACCESS NETWORK (gNBs) [Y: 2 to 23]
    # =========================================================================
    box_t1 = patches.FancyBboxPatch(
        (2, 2), 96, 21.5,
        boxstyle="round,pad=0.8,rounding_size=2.0",
        facecolor=c_tier1_bg, edgecolor="#64748B", linewidth=1.5
    )
    ax.add_patch(box_t1)
    ax.text(4, 20.5, "TIER 1: PHYSICAL HETEROGENEOUS RADIO ACCESS NETWORK (12-CELL DUAL-BAND)",
            fontsize=9.5, fontweight="bold", color="#F1F5F9", fontfamily="sans-serif")
    ax.text(4, 17.5, "Dual-Band gNB Infrastructure | 700 MHz Macro Coverage + 3.5 GHz Urban Capacity Cells",
            fontsize=7.2, color="#CBD5E1", fontfamily="sans-serif")

    # Render representative cells showing Macro Umbrella + Micro Capacity split
    cell_names = ["gNB-01 (Macro)\n[Always Active]", "gNB-02 (Macro)\n[Always Active]", "gNB-07 (Micro)\n[Nominal Load]", "gNB-09 (Micro)\n[FDI SPOOFED]", "gNB-10 (Micro)\n[FDI SPOOFED]", "gNB-11 (Micro)\n[Sleep Valid]"]
    cell_colors = [c_tier2_bg, c_tier2_bg, c_tier2_bg, "#7F1D1D", "#7F1D1D", "#064E3B"]
    cell_borders = [c_cyan, c_cyan, c_cyan, c_red, c_red, c_green]

    for idx, (name, bg, bd) in enumerate(zip(cell_names, cell_colors, cell_borders)):
        cx = 5 + idx * 15.2
        c_box = patches.FancyBboxPatch((cx, 4), 14, 11.5, boxstyle="round,pad=0.3,rounding_size=0.8",
                                      facecolor=bg, edgecolor=bd, linewidth=1.2)
        ax.add_patch(c_box)
        txt_col = "#FCA5A5" if "FDI" in name else ("#A7F3D0" if "Sleep" in name else c_text_bright)
        ax.text(cx + 7, 9.5, name, fontsize=6.8, fontweight="bold", color=txt_col, ha="center", va="center")

    # Vertical Connecting Arrows from Tier 1 to Tier 2
    ax.annotate("", xy=(50, 26), xytext=(50, 23.5), arrowprops=dict(arrowstyle="<->", color=c_cyan, lw=2))

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] High-resolution architecture diagram saved: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
    out_file = os.path.join(out_dir, "aicop_raksha_architecture.png")
    draw_architecture(out_file)
