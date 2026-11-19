"""
RAKSHA-NET: Automated Professional PowerPoint Presentation Generator
Creates a 12-slide, 16:9 widescreen, dark-themed defense pitch deck for Ideas for India 2026.
Reflects TRL-4 laboratory emulation (no claims of physical satellite deployment),
cites the Reactive BFD baseline alongside static routing,
and references the Apache 2.0 license and docs/THREAT_MODEL.md.
Includes complete speaker notes, tables, metrics, and embedded benchmark charts.
"""
from __future__ import annotations
import pathlib
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_FILE = REPO_ROOT / "results" / "raksha_net_defense_presentation.pptx"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Theme Palette (Tactical Dark Cyber Defense)
BG_COLOR = RGBColor(10, 14, 26)         # #0A0E1A
CARD_BG = RGBColor(19, 27, 46)          # #131B2E
CARD_BORDER = RGBColor(51, 65, 85)      # #334155
TEXT_WHITE = RGBColor(248, 250, 252)    # #F8FAFC
TEXT_MUTED = RGBColor(148, 163, 184)    # #94A3B8
TEXT_BODY = RGBColor(203, 213, 225)     # #CBD5E1
CYAN = RGBColor(0, 240, 255)            # #00F0FF (Telemetry / AI)
GREEN = RGBColor(16, 185, 129)          # #10B981 (Success / Resilience)
AMBER = RGBColor(245, 158, 11)          # #F59E0B (Jamming / Threat)
RED = RGBColor(239, 68, 68)             # #EF4444 (Failure / Collapse)
PURPLE = RGBColor(168, 85, 247)         # #A855F7 (Post-Quantum Crypto)

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"

def create_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, category: str, title: str, subtitle: str):
        # Category pill text
        pill_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_pill = pill_box.text_frame
        tf_pill.word_wrap = True
        tf_pill.margin_left = tf_pill.margin_top = tf_pill.margin_right = tf_pill.margin_bottom = 0
        p_pill = tf_pill.paragraphs[0]
        p_pill.text = f"●  {category.upper()}"
        p_pill.font.name = FONT_HEADING
        p_pill.font.size = Pt(10)
        p_pill.font.bold = True
        p_pill.font.color.rgb = CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, title: str = "", border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        
        if title:
            tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = FONT_HEADING
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = CYAN
        return card

    def add_stat_box(slide, left, top, width, height, number: str, label: str, num_color=CYAN):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(15, 23, 42)
        box.line.color.rgb = num_color
        box.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(Inches(left + 0.1), Inches(top + 0.12), Inches(width - 0.2), Inches(height - 0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_num = tf.paragraphs[0]
        p_num.text = number
        p_num.alignment = PP_ALIGN.CENTER
        p_num.font.name = FONT_HEADING
        p_num.font.size = Pt(19)
        p_num.font.bold = True
        p_num.font.color.rgb = num_color

        p_lbl = tf.add_paragraph()
        p_lbl.text = label
        p_lbl.alignment = PP_ALIGN.CENTER
        p_lbl.font.name = FONT_BODY
        p_lbl.font.size = Pt(9.0)
        p_lbl.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 1: Title & Strategic Positioning
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_slide_background(s1)

    # Top Tag
    tag_box = s1.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.4))
    tf = tag_box.text_frame
    p = tf.paragraphs[0]
    p.text = "IDEAS FOR INDIA 2026  |  SOVEREIGN DEFENCE & STRATEGIC TECHNOLOGIES  |  TRL-4 TESTBED VALIDATION  |  APACHE 2.0"
    p.font.name = FONT_HEADING
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = CYAN

    # Main Title
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(1.6))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "RAKSHA-NET  (रक्षा-नेट)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    p2 = tf.add_paragraph()
    p2.text = "Quantum-Resilient Autonomous 5G / NTN Cyber-Defense Controller"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(18)
    p2.font.bold = True
    p2.font.color.rgb = GREEN

    # Subtitle Pitch
    pitch_box = s1.shapes.add_textbox(Inches(0.8), Inches(3.0), Inches(11.7), Inches(0.9))
    tf = pitch_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Preserving Tactical Comms Availability & Post-Quantum Forward Secrecy Under EW Jamming (TRL-4 Laboratory Emulation)"
    p.font.name = FONT_BODY
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_BODY

    # 4 Stat Callout Cards
    add_stat_box(s1, 0.8, 4.0, 2.7, 1.3, "+64.5% PDR", "+64.5% vs Static | +21.0% vs Reactive BFD", GREEN)
    add_stat_box(s1, 3.8, 4.0, 2.7, 1.3, "190 ms", "Autonomous Failover (vs 1.5–2.8s BFD)", CYAN)
    add_stat_box(s1, 6.8, 4.0, 2.7, 1.3, "0.48 ms", "NIST ML-KEM-768 Hybrid Rekey in C", PURPLE)
    add_stat_box(s1, 9.8, 4.0, 2.7, 1.3, "TRL-4 / 53", "53/53 Unit Tests | Apache 2.0 Open Source", GREEN)

    # Footer Presenters Info
    f_box = s1.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.7), Inches(1.1))
    tf = f_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Presented by:  G Rahul Reddy  &  Rajarwar Deependra Sahebrao  |  PDPM IIITDM Jabalpur"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    p_org = tf.add_paragraph()
    p_org.text = (
        "License: Apache License 2.0 (Open Source)  |  Security Architecture: docs/THREAT_MODEL.md (STRIDE)\n"
        "Scientific Disclosure: TRL-4 Laboratory Testbed Validation (Active Open5GS, Native C liboqs, Docker CNFs; No Physical Satellites Deployed)"
    )
    p_org.font.name = FONT_BODY
    p_org.font.size = Pt(9.5)
    p_org.font.color.rgb = TEXT_MUTED

    s1.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 1 (0:00 - 1:00):\n"
        "Respected jury members, good morning. We are Rahul Reddy and Deependra Rajarwar from PDPM IIITDM Jabalpur. "
        "Today we present RAKSHA-NET: an indigenous, open-source (Apache 2.0 licensed) quantum-resilient autonomous cyber-defense "
        "and availability controller for 5G Non-Terrestrial Networks, rigorously evaluated at Technology Readiness Level 4 (TRL-4) in a laboratory testbed.\n\n"
        "In modern multi-domain warfare, battlefield dominance relies on resilient satellite communications. "
        "However, tactical satellite links face a dual threat: aggressive Electronic Warfare jamming that breaks mission connectivity, "
        "and quantum-enabled adversaries executing 'Harvest Now, Decrypt Later' espionage.\n\n"
        "RAKSHA-NET addresses both through a unified software controller: restoring packet delivery from 32% to 97% in 190 milliseconds—outperforming "
        "both static routing (+64.5 pp) and standard 3GPP Reactive BFD hold-timers (+21.0 pp)—while rekeying sessions with NIST ML-KEM-768 post-quantum "
        "cryptography in under half a millisecond. We operate strictly as an open-source software-in-the-loop laboratory testbed without claiming physical satellite orbital launches. "
        "Let us examine the threat landscape."
    )

    # =========================================================================
    # SLIDE 2: The Tactical Problem & The Threat Landscape
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_background(s2)
    add_header(s2, "Operational Vulnerability", "The Strategic Problem: Electronic Warfare & Quantum Threat",
               "Tactical satellite relays operate in contested environments where availability and cryptographic secrecy fail simultaneously.")

    # 3 Cards: Problem Breakdown
    add_card(s2, 0.8, 1.9, 3.6, 4.8, "1. Multi-Baseline Jamming Failure", AMBER)
    tb = s2.shapes.add_textbox(Inches(1.05), Inches(2.6), Inches(3.1), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = (
        "• Static Routing Collapse:\n"
        "  Zero automated failover; drops to 32.3% PDR (67.7% packet loss) under active RF jamming.\n\n"
        "• Reactive BFD Delay (RFC 5880):\n"
        "  Standard 3GPP loss hold-timer (15 ticks) takes 1.5s–2.8s to trigger, causing severe transient blackout (76.0% PDR).\n\n"
        "• Tactical Blackout:\n"
        "  Frontline soldiers, UAVs, and command posts lose situational awareness during crucial combat seconds."
    )
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    add_card(s2, 4.8, 1.9, 3.6, 4.8, "2. 'Harvest Now, Decrypt Later'", PURPLE)
    tb = s2.shapes.add_textbox(Inches(5.05), Inches(2.6), Inches(3.1), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = (
        "• Quantum Espionage:\n"
        "  Adversaries passively intercept and store encrypted satellite telemetry today.\n\n"
        "• Retroactive Exposure:\n"
        "  Once cryptanalytically relevant quantum computers (CRQCs) arrive, classical RSA/ECC traffic is fully compromised.\n\n"
        "• STRIDE Threat Governance:\n"
        "  Formalized in docs/THREAT_MODEL.md; requires immediate NIST FIPS 203 ML-KEM-768 forward secrecy."
    )
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    add_card(s2, 8.8, 1.9, 3.6, 4.8, "3. The Disconnected Silo Gap", RED)
    tb = s2.shapes.add_textbox(Inches(9.05), Inches(2.6), Inches(3.1), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = (
        "• Academic Silos:\n"
        "  Routing engineers optimize link paths; cryptographers benchmark PQC algorithms in isolation.\n\n"
        "• Indicator of Compromise (IoC):\n"
        "  Jamming is not just RF fading—it frequently signals link tampering, interception, or physical node compromise.\n\n"
        "• RAKSHA-NET's Thesis:\n"
        "  Proactive route recovery and zero-trust crypto-rekeying MUST be executed in sub-second coordinated unison."
    )
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    s2.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 2 (1:00 - 2:00):\n"
        "Let us examine why existing tactical satellite communications fail under modern electronic warfare.\n\n"
        "First, current routing architectures are either unmanaged or reactive. In our live testbed, static routing collapses to 32.3% PDR. "
        "Meanwhile, the industry standard 3GPP Reactive BFD baseline (RFC 5880) relies on consecutive loss hold-timers that take 1.5 to 2.8 seconds to expire. "
        "During those seconds, tactical telemetry is lost, paralyzing C2 operations.\n\n"
        "Second, we face the 'Harvest Now, Decrypt Later' threat. Hostile state actors are archiving military satellite feeds today. "
        "When quantum computers mature, all classically encrypted traffic will be decrypted retroactively. As detailed in our formal STRIDE Threat Model "
        "in docs/THREAT_MODEL.md, quantum-safe forward secrecy must be integrated directly into the communication fabric now.\n\n"
        "Finally, routing resilience and cryptography have always existed as disconnected academic silos. "
        "RAKSHA-NET treats jamming as an active Indicator of Compromise, unifying proactive route migration and post-quantum rekeying into a sub-second autonomous loop."
    )

    # =========================================================================
    # SLIDE 3: Unified Solution Architecture & 4 Pillars
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_background(s3)
    add_header(s3, "System Overview", "The Solution: Unified 4-Pillar Autonomous Controller",
               "TRL-4 closed loop linking real-time telemetry, Bayesian zero-trust routing, and post-quantum crypto-agility.")

    # Insert Architecture Diagram Image
    arch_img_path = REPO_ROOT / "results" / "system_architecture_diagram.png"
    if arch_img_path.exists():
        s3.shapes.add_picture(str(arch_img_path.resolve()), Inches(0.8), Inches(1.85), Inches(11.7), Inches(3.2))

    # 4 Pillar Summaries at bottom
    add_card(s3, 0.8, 5.25, 2.7, 1.8, "Pillar 1: Telemetry AI", CYAN)
    tb = s3.shapes.add_textbox(Inches(0.95), Inches(5.75), Inches(2.4), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Sub-second streaming from Open5GS ogstun. EWMA & Page's CUSUM scoring of RTT, jitter, PDR, queue depth."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s3, 3.8, 5.25, 2.7, 1.8, "Pillar 2: Zero-Trust Routing", GREEN)
    tb = s3.shapes.add_textbox(Inches(3.95), Inches(5.75), Inches(2.4), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Bayesian link trust decay (T < 0.50). Multi-criteria route utility ranking with 5% hysteresis; beats 15-tick BFD timeout."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s3, 6.8, 5.25, 2.7, 1.8, "Pillar 3: Post-Quantum Agility", PURPLE)
    tb = s3.shapes.add_textbox(Inches(6.95), Inches(5.75), Inches(2.4), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "NIST ML-KEM-768 via native C liboqs. Dual-hybrid RFC 9370 rekeying in 0.48ms; programmatically isolates compromised relays."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s3, 9.8, 5.25, 2.7, 1.8, "Pillar 4: Container Isolation", AMBER)
    tb = s3.shapes.add_textbox(Inches(9.95), Inches(5.75), Inches(2.4), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Docker CNF architecture. Network namespace sandboxing stops lateral movement per docs/THREAT_MODEL.md."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    s3.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 3 (2:00 - 3:15):\n"
        "Here is the unified architecture of RAKSHA-NET, operating across four tightly-coupled pillars in our TRL-4 testbed.\n\n"
        "First, Telemetry Ingestion continuously monitors the live 5G tunnel interface `ogstun`, measuring latency, jitter, packet loss, "
        "and buffer queues in sub-second epochs.\n\n"
        "Second, our Anomaly Detection engine computes EWMA baseline deviations and Page's CUSUM change-point scores. "
        "When electronic jamming hits, the anomaly score breaches our calibrated threshold of 0.60.\n\n"
        "Third, this triggers our Zero-Trust Route Engine: Bayesian trust on link LEO-1 collapses below 0.50. "
        "Rather than waiting seconds for reactive BFD loss timers, our multi-criteria optimizer evicts LEO-1 and proactively migrates "
        "traffic to healthy satellite LEO-2 in 190 milliseconds with zero flapping.\n\n"
        "Simultaneously, our Post-Quantum Security Engine initiates dual-hybrid RFC 9370 rekeying via NIST ML-KEM-768 in native C, "
        "establishing a quantum-secure forward secret session in 0.48 milliseconds while isolating the compromised node.\n\n"
        "And fourth, because satellite relays run as Docker Container Network Functions in isolated Linux namespaces, lateral privilege escalation is eliminated, "
        "strictly implementing the mitigations specified in docs/THREAT_MODEL.md."
    )

    # =========================================================================
    # SLIDE 4: Algorithmic Engines: Mathematical Formulation
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_background(s4)
    add_header(s4, "Deep Technical Core", "Algorithmic Engines: Closed-Loop Mathematical Design",
               "Rigorous mathematical formulation driving proactive anomaly detection, trust decay, and hysteresis-bounded failover.")

    # 3 Cards for Algorithms
    add_card(s4, 0.8, 1.9, 3.6, 4.9, "Algorithm 1: Anomaly Scoring", AMBER)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Metric Deviation Ingestion:\n"
        "  Tracks normalized deviations from EWMA baselines:\n"
        "  d_τ = (τ - μ_τ) / σ_τ,  d_q = (q - μ_q) / σ_q\n\n"
        "• Composite Scoring Function:\n"
        "  a_t = clip(w_τ·d_τ + w_l·(1-PDR) + w_q·d_q, 0, 1)\n\n"
        "• Page's CUSUM Detector:\n"
        "  Detects persistent distribution shifts (k=0.5, h=2.0) before loss counters expire, outperforming reactive BFD."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    add_card(s4, 4.8, 1.9, 3.6, 4.9, "Algorithm 2: Zero-Trust Routing", GREEN)
    tb = s4.shapes.add_textbox(Inches(5.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Bayesian Trust Decay:\n"
        "  T_{t+1} = α · T_t + (1 - α) · (1 - a_t)  (α = 0.85)\n"
        "  Rapid trust collapse evicts jammed links (T < 0.50).\n\n"
        "• Multi-Objective Route Utility:\n"
        "  Score(R) = w_t·T(R) + w_l·(1 - τ/τ_max) + w_p·PDR(R) + w_e·Battery(R)\n\n"
        "• Anti-Flapping Hysteresis Margin:\n"
        "  Score(R_new) > Score(R_curr) + ε  (ε = 0.05)\n"
        "  Guarantees 0 route flaps (vs severe BFD flapping)."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    add_card(s4, 8.8, 1.9, 3.6, 4.9, "Algorithm 3: Post-Quantum Agility", PURPLE)
    tb = s4.shapes.add_textbox(Inches(9.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Dual-Hybrid Key Exchange (RFC 9370):\n"
        "  Combines classical X25519 with NIST FIPS 203 ML-KEM-768 via HKDF-SHA256.\n\n"
        "• Native C liboqs Speed:\n"
        "  0.065ms pure KEM encapsulation, 0.48ms hybrid wall-clock rekey.\n\n"
        "• Adaptive AEAD Cipher Selection:\n"
        "  AES-256-GCM (high BW) or ChaCha20-Poly1305 (constrained embedded links per RFC 8439).\n\n"
        "• Threat Governance:\n"
        "  Quarantines compromised nodes per docs/THREAT_MODEL.md."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    s4.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 4 (3:15 - 4:30):\n"
        "Let us examine the mathematical mechanics guaranteeing stability and high availability.\n\n"
        "In Algorithm 1, our anomaly scoring function tracks normalized deviations from rolling EWMA baselines and integrates Page's CUSUM. "
        "While standard 3GPP BFD waits passively for 15 consecutive dropped packet ticks, our CUSUM detector detects persistent distribution shifts "
        "in latency, jitter, and queue depth, triggering failover within milliseconds.\n\n"
        "In Algorithm 2, link trust decays using a Bayesian update rule with alpha = 0.85. When jamming strikes, link trust plummets. "
        "Candidate routes are ranked across Trust, Latency, PDR, and Battery Reserves. "
        "Crucially, we enforce a strict 5% hysteresis barrier (epsilon = 0.05). In all our trials, route flapping was exactly zero.\n\n"
        "In Algorithm 3, the security engine executes NIST FIPS 203 ML-KEM-768 via native C liboqs routines, establishing dual-hybrid RFC 9370 "
        "shared secrets via HKDF-SHA256 in 0.48 milliseconds. Compromised nodes are evicted from future key schedules, fulfilling the mitigations "
        "formalized in our STRIDE threat model (docs/THREAT_MODEL.md)."
    )

    # =========================================================================
    # SLIDE 5: Container-Native Architecture & Zero-Trust Blast Radius
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_background(s5)
    add_header(s5, "System Engineering & Sovereignty", "Container-Native Architecture & Blast-Radius Containment",
               "Docker CNF micro-segmentation eliminates proprietary hardware lock-in and contains breaches to isolated Linux namespaces.")

    # Comparison Table
    table_card = add_card(s5, 0.8, 1.9, 11.7, 4.9, "Architectural Comparison: Traditional Hardware vs RAKSHA-NET CNF", CYAN)
    
    table_shape = s5.shapes.add_table(5, 3, Inches(1.1), Inches(2.6), Inches(11.1), Inches(3.8))
    table = table_shape.table
    table.columns[0].width = Inches(2.4)
    table.columns[1].width = Inches(4.3)
    table.columns[2].width = Inches(4.4)

    headers = ["Security & Architecture Dimension", "Traditional Proprietary Hardware", "RAKSHA-NET (Docker CNF Software-Defined)"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = CYAN

    rows = [
        ("Blast-Radius Containment",
         "Shared physical chassis; if one relay link is breached, lateral movement threatens the entire vehicle / satellite bus.",
         "Strict Container Sandboxing: Relays run in isolated Linux namespaces (NET_ADMIN); zero lateral host escape (docs/THREAT_MODEL.md)."),
        ("Supply-Chain Sovereignty",
         "Proprietary foreign ASICs & crypto appliances; risk of hidden backdoors and export restrictions.",
         "100% Software-Defined & Open: Runs on standard COTS ARM or x86 satellite OBCs, or indigenous Shakti / Vega RISC-V processors."),
        ("Programmatic Quarantine",
         "Manual reconfiguration or slow physical power-down taking minutes.",
         "Sub-Second Dynamic Isolation: Controller programmatically tears down or throttles compromised container interfaces in <200ms."),
        ("Deployment & Licensing",
         "Proprietary vendor licensing, months of custom hardware provisioning, heavy payload mass.",
         "Apache License 2.0: Permissive open-source deployment via Docker / K8s sidecars with lightweight memory footprint (<60 MB).")
    ]

    for row_idx, data in enumerate(rows):
        for col_idx, text in enumerate(data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(19, 27, 46) if row_idx % 2 == 0 else RGBColor(15, 23, 42)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_WHITE
            elif col_idx == 1:
                p.font.color.rgb = RGBColor(248, 113, 113)  # soft red
            else:
                p.font.color.rgb = RGBColor(52, 211, 153)  # soft green

    s5.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 5 (4:30 - 5:45):\n"
        "A critical question juries often ask is: 'Why implement this in software containers rather than building a custom defense hardware appliance?'\n\n"
        "There are four decisive operational advantages:\n"
        "1. Blast Radius Containment: In traditional hardware appliances, a compromised interface allows lateral movement across the internal bus. "
        "In RAKSHA-NET, every satellite relay runs in an isolated Linux network namespace via Docker CNFs. Even if an adversary compromises LEO-1, "
        "the attack cannot escape the container, directly addressing the Elevation of Privilege threat detailed in docs/THREAT_MODEL.md.\n\n"
        "2. Supply Chain Sovereignty: Proprietary defense appliances rely on foreign cryptographic ASICs vulnerable to export controls and backdoors. "
        "RAKSHA-NET is 100% software-defined, ready to deploy on standard COTS ARM processors or India's indigenous Shakti and Vega RISC-V platforms.\n\n"
        "3. Sub-Second Quarantine: Network interfaces are software-defined, allowing programmatic quarantine in under 200 milliseconds.\n\n"
        "4. Permissive Open-Source Licensing: Released under Apache License 2.0, RAKSHA-NET avoids commercial vendor lock-in and consumes under 60 MB of RAM, "
        "enabling rapid deployment on tactical edge compute."
    )

    # =========================================================================
    # SLIDE 6: Empirical Results: Multi-Baseline PDR Restoration Under Jamming
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_background(s6)
    add_header(s6, "Empirical Validation", "Empirical Results: Multi-Baseline PDR Restoration Under Jamming",
               "TRL-4 testbed validation across 10 trials comparing Proactive AICOP vs Reactive BFD and Static Routing.")

    # High-impact Data Table on Left
    add_card(s6, 0.8, 1.85, 5.7, 5.0, "Multi-Baseline Operational Performance", GREEN)
    table_shape2 = s6.shapes.add_table(5, 4, Inches(0.92), Inches(2.45), Inches(5.46), Inches(2.75))
    table2 = table_shape2.table
    table2.columns[0].width = Inches(1.56)
    table2.columns[1].width = Inches(1.15)
    table2.columns[2].width = Inches(1.35)
    table2.columns[3].width = Inches(1.40)

    h2 = ["Operational Phase", "Static Routing", "Reactive BFD (RFC 5880)", "RAKSHA-NET (AICOP)"]
    for i, h in enumerate(h2):
        cell = table2.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = CYAN

    r2 = [
        ("1. Pre-Attack Normal", "96.8% PDR", "96.8% PDR", "96.8% PDR"),
        ("2. Reaction Dip", "33.8% (Collapse)", "33.8% (Hold-Timer Wait)", "83.5% (190ms Dip)"),
        ("3. Sustained Jamming", "32.3% (Broken)", "76.0% (Late Failover)", "96.8% (Restored)"),
        ("4. Post-Attack Restore", "86.9% PDR", "96.8% PDR", "96.8% PDR")
    ]

    for row_idx, data in enumerate(r2):
        for col_idx, text in enumerate(data):
            cell = table2.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(19, 27, 46) if row_idx % 2 == 0 else RGBColor(15, 23, 42)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = FONT_BODY
            p.font.size = Pt(8.0)
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_WHITE
            elif col_idx == 1:
                p.font.color.rgb = RED if "Collapse" in text or "Broken" in text else TEXT_MUTED
            elif col_idx == 2:
                p.font.color.rgb = AMBER if "Hold-Timer" in text or "76.0%" in text else TEXT_MUTED
            else:
                p.font.color.rgb = GREEN if "Restored" in text or "96.8%" in text else CYAN

    # Bottom Stat Callout in Card
    tb_stat = s6.shapes.add_textbox(Inches(0.92), Inches(5.35), Inches(5.46), Inches(1.35))
    tf = tb_stat.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Empirical Gain: +64.5% vs Static | +21.0% vs Reactive BFD"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = GREEN

    p_t = tf.add_paragraph()
    p_t.text = (
        "Paired t-Test vs Static: t = 98.8, p = 5.6 × 10⁻¹⁵ (n = 10 trials, statistically significant).\n"
        "Outage Window: 190ms (Proactive CUSUM) vs 1,500–2,800ms (Reactive BFD 15-tick hold timer).\n"
        "TRL-4 laboratory validation under simulated Linux tc netem jamming (0 physical satellites claimed)."
    )
    p_t.font.name = FONT_BODY
    p_t.font.size = Pt(8.5)
    p_t.font.color.rgb = TEXT_MUTED

    # Insert Real Heuristic Metrics PNG on Right
    chart_pdr_path = REPO_ROOT / "results" / "benchmark_heuristic_metrics.png"
    if chart_pdr_path.exists():
        add_card(s6, 6.7, 1.85, 5.8, 5.0, "Live Benchmark Telemetry Curves (TRL-4)", CYAN)
        s6.shapes.add_picture(str(chart_pdr_path.resolve()), Inches(6.85), Inches(2.45), Inches(5.5), Inches(4.2))

    s6.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 6 (5:45 - 7:00):\n"
        "Here are our empirical benchmark results across 10 independent trials conducted in our TRL-4 laboratory testbed.\n\n"
        "We evaluate three routing paradigms under active RF jamming:\n"
        "1. Static Routing: When jamming strikes at t = 2.0s, it never reroutes, flatlining at 32.3% PDR (67.7% loss).\n"
        "2. Reactive BFD (3GPP standard RFC 5880): Relies on a 15-tick loss counter. It takes 1.5 to 2.8 seconds to trigger, "
        "recovering late and suffering an average PDR of only 76.0% (24% packet loss).\n"
        "3. RAKSHA-NET (Proactive AICOP): Experiences only a transient 190ms reaction dip to 83.5% during detection, then recovers "
        "to 96.8% PDR. This delivers a +64.5 pp gain over static routing and a decisive +21.0 pp gain over 3GPP Reactive BFD.\n\n"
        "Our paired Student's t-test yields t = 98.8 with p = 5.6 × 10^-15, proving our proactive advantage is statistically definitive. "
        "Looking at the telemetry plot on the right, you see the red dashed static curve collapse, while RAKSHA-NET instantly restores connectivity."
    )

    # =========================================================================
    # SLIDE 7: Empirical Results: 190ms Failover & Sub-ms PQC Benchmark
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_background(s7)
    add_header(s7, "Performance Benchmarks", "Failover Latency & Native C Post-Quantum Cryptography",
               "Real liboqs-python execution proves quantum resistance introduces negligible (<1ms) overhead to the 5G control plane.")

    # 3 Metrics at Top
    add_stat_box(s7, 0.8, 1.85, 3.6, 1.25, "190 ms (±30ms)", "Proactive Failover (vs 1.5–2.8s BFD Timeout)", CYAN)
    add_stat_box(s7, 4.8, 1.85, 3.6, 1.25, "0.065 ms", "NIST ML-KEM-768 Native C Encapsulation (65 μs)", GREEN)
    add_stat_box(s7, 8.8, 1.85, 3.6, 1.25, "0 Flaps (0%)", "5% Hysteresis Stability (0 flaps across all trials)", PURPLE)

    # Insert Crypto Benchmark Slide Chart
    crypto_chart_path = REPO_ROOT / "results" / "crypto_benchmark_slide_chart.png"
    if crypto_chart_path.exists():
        s7.shapes.add_picture(str(crypto_chart_path.resolve()), Inches(0.8), Inches(3.25), Inches(7.6), Inches(3.6))

    # Right Card: Cryptographic Key Insights
    add_card(s7, 8.6, 3.25, 3.9, 3.6, "Post-Quantum Insights", PURPLE)
    tb_crypto = s7.shapes.add_textbox(Inches(8.8), Inches(3.85), Inches(3.5), Inches(2.8))
    tf = tb_crypto.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Debunking the PQC Overhead Myth:\n"
        "  Skeptics claim PQC is too heavy for tactical 5G. Native C benchmarks prove ML-KEM-768 executes in 65 microseconds—faster than classical X25519 (198 μs)!\n\n"
        "• End-to-End Live Rekey:\n"
        "  Even with complete session re-negotiation, HKDF derivation, and node isolation inside Open5GS, total rekey time is only 0.48 ms–0.71 ms.\n\n"
        "• Dual-Hybrid RFC 9370:\n"
        "  2,336-byte wire payload fits standard MTU without fragmentation; eliminates HNDL risk per docs/THREAT_MODEL.md."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    s7.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 7 (7:00 - 8:15):\n"
        "Now let us examine our timing benchmarks and address the primary skepticism regarding Post-Quantum Cryptography.\n\n"
        "Many defense researchers assume PQC algorithms are too computationally expensive for real-time 5G control planes. "
        "Our benchmarks, executed using liboqs native C routines across 200 iterations, directly disprove this myth:\n"
        "- Pure NIST ML-KEM-768 key encapsulation takes just 0.065 milliseconds—that is 65 microseconds!\n"
        "- Lattice-based ML-KEM-768 is actually three times faster to compute than classical elliptic-curve X25519 (0.198 ms).\n"
        "- Our dual-hybrid suite (combining X25519 and ML-KEM-768 per RFC 9370) executes in 0.233 ms.\n"
        "- Even during an active attack inside Open5GS, complete session re-negotiation, HKDF derivation, and compromised node isolation "
        "complete in 0.48 to 0.71 milliseconds—comfortably within the 1-millisecond real-time 5G deadline.\n\n"
        "Furthermore, at 2.3 kilobytes, the entire wire payload fits into standard MTU frames without IP fragmentation."
    )

    # =========================================================================
    # SLIDE 8: Real 3GPP 5G Core Integration (Open5GS Live Testbed)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_background(s8)
    add_header(s8, "Live Implementation", "Active 3GPP 5G Core Integration: Open5GS & Linux TUN",
               "TRL-4 laboratory testbed: 17 Open5GS core daemons running under WSL2 with active ogstun user-plane tunneling.")

    # 3 Cards: Core Architecture
    add_card(s8, 0.8, 1.9, 3.6, 4.9, "1. 17 Active Open5GS Daemons", CYAN)
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Verified Active Services:\n"
        "  amfd, smfd, upfd, nrfd, ausfd, udmd, nssfd, pcfd, udrd, mmed, sgwcd, sgwud, hssd, pcrfd, scpd, bsfd, webui.\n\n"
        "• 3GPP Rel-17 Compliant:\n"
        "  True service-based architecture (SBA) handling live 5G registration and session management.\n\n"
        "• Real User-Plane Tunnel:\n"
        "  Linux TUN interface `ogstun` active at 10.45.0.1/16 in TRL-4 testbed."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    add_card(s8, 4.8, 1.9, 3.6, 4.9, "2. Live Testbed Demo Flow", GREEN)
    tb = s8.shapes.add_textbox(Inches(5.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Demonstration Script:\n"
        "  `scripts/run_open5gs_demo.py` connects Open5GSBackend directly to Controller.\n\n"
        "• RF Jamming Injection:\n"
        "  Applies live Linux kernel `tc netem` impairment (loss + delay) directly onto `ogstun`.\n\n"
        "• Closed-Loop Verification:\n"
        "  Anomaly score triggers instantly, liboqs executes ML-KEM-768 rekey, and traffic migrates to LEO-2 in 190ms."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    add_card(s8, 8.8, 1.9, 3.6, 4.9, "3. Verification & Governance", PURPLE)
    tb = s8.shapes.add_textbox(Inches(9.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• 53 / 53 Passing Unit Tests:\n"
        "  100% test pass rate across routing, anomaly, crypto, and telemetry modules.\n\n"
        "• Apache License 2.0:\n"
        "  Permissive open-source license enabling unhindered defense & academic collaboration.\n\n"
        "• STRIDE Threat Model:\n"
        "  Formal security architecture and threat boundaries documented in docs/THREAT_MODEL.md.\n\n"
        "• Single-Command Test:\n"
        "  `pytest tests/ -q` executes in ~1.2 seconds."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    s8.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 8 (8:15 - 9:15):\n"
        "To ensure our solution is genuinely deployable in real defense networks, RAKSHA-NET is integrated directly with a functional 3GPP 5G Core: Open5GS.\n\n"
        "Under our TRL-4 testbed environment in WSL2 Ubuntu 24.04, all 17 Open5GS core daemons are actively running—including the AMF, SMF, UPF, and AUSF. "
        "User traffic flows over an active Linux TUN interface `ogstun`.\n\n"
        "In our live demo script (`run_open5gs_demo.py`), we attach our controller directly to this live 5G core. "
        "We inject electronic warfare impairments using Linux kernel traffic control (`tc netem`) right onto the active interface. "
        "The controller detects the perturbation, rekeys the post-quantum session in C, and migrates the route seamlessly.\n\n"
        "Furthermore, our codebase is released under the permissive Apache License 2.0, adheres strictly to the STRIDE threat model in docs/THREAT_MODEL.md, "
        "and is verified by 53 passing automated unit tests."
    )

    # =========================================================================
    # SLIDE 9: Tactical LEACH: Satellite Energy & Telemetry Compression
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_background(s9)
    add_header(s9, "Space & Energy Resilience", "Tactical LEACH: Orbital Energy & Bandwidth Optimization",
               "TRL-4 orbital simulation: Preserving constellation battery lifetime and saving 75% telemetry bandwidth in contested orbits.")

    # Table comparing Classical LEACH vs RAKSHA-NET
    add_card(s9, 0.8, 1.9, 11.7, 4.9, "Orbital Efficiency & Constellation Sustainability (TRL-4 Simulation)", AMBER)
    
    t_shape3 = s9.shapes.add_table(5, 3, Inches(1.1), Inches(2.6), Inches(11.1), Inches(3.8))
    table3 = t_shape3.table
    table3.columns[0].width = Inches(2.8)
    table3.columns[1].width = Inches(4.1)
    table3.columns[2].width = Inches(4.2)

    h3 = ["Dimension / Capability", "Classical LEACH (Baseline)", "RAKSHA-NET + Tactical LEACH"]
    for i, h in enumerate(h3):
        cell = table3.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN

    r3 = [
        ("PDR Under Electronic Jamming",
         "41.0% (Cluster heads targeted; routing collapses without proactive recovery)",
         "96.4% PDR (Autonomous cluster head rotation & backup route failover in 190ms)"),
        ("Quantum-Resilient Protection",
         "None (0-bit security, cleartext or classical ECC vulnerable to HNDL)",
         "NIST ML-KEM-768 Post-Quantum Forward Secrecy integrated into every cluster"),
        ("Telemetry Uplink Bandwidth",
         "100% Channel Occupancy (Heavy uncompressed telemetry causes uplink congestion)",
         "~75% Bandwidth Saved via lossless zlib moment compression on telemetry streams"),
        ("Satellite Orbital Energy Model",
         "Random probabilistic selection; quickly depletes shadowed satellites",
         "Residual Battery & Solar Harvest Aware: Prefers relays currently in solar orbital illumination")
    ]

    for row_idx, data in enumerate(r3):
        for col_idx, text in enumerate(data):
            cell = table3.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(19, 27, 46) if row_idx % 2 == 0 else RGBColor(15, 23, 42)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = FONT_BODY
            p.font.size = Pt(10)
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_WHITE
            elif col_idx == 1:
                p.font.color.rgb = RGBColor(248, 113, 113)
            else:
                p.font.color.rgb = RGBColor(52, 211, 153)

    s9.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 9 (9:15 - 10:15):\n"
        "In satellite constellations, electrical power and RF channel bandwidth are severely constrained.\n\n"
        "In our TRL-4 simulation environment, we incorporated Tactical LEACH principles to optimize constellation sustainability:\n"
        "1. Orbital Energy Awareness: Satellites alternate between eclipse and solar illumination. "
        "Classical routing blindly uses whichever relay has the shortest hop, rapidly draining satellites in eclipse. "
        "RAKSHA-NET factors residual battery percentage and orbital solar harvesting into its route utility function.\n\n"
        "2. In-Flight Telemetry Compression: High-rate telemetry streaming from satellite probes can overwhelm constrained tactical uplinks. "
        "We implement lossless zlib moment compression, reducing telemetry bandwidth consumption by approximately 75%.\n\n"
        "As shown in our comparative benchmarks, RAKSHA-NET maintains 96.4% PDR under electronic warfare while drastically reducing constellation energy drain."
    )

    # =========================================================================
    # SLIDE 10: Defensible Novelty & Honest Implementation Matrix
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_background(s10)
    add_header(s10, "Defensibility & Rigor", "TRL-4 Honesty Matrix: Real Code vs Emulation",
               "Absolute transparency regarding TRL-4 laboratory emulation vs real software stack, ensuring jury credibility.")

    # Left: What is 100% Real Code
    add_card(s10, 0.8, 1.9, 5.7, 4.9, "100% Real Software & Tested (TRL-4)", GREEN)
    tb_real = s10.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(5.3), Inches(4.1))
    tf = tb_real.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "✔ NIST ML-KEM-768 Cryptography:\n"
        "  Native C compiled execution via liboqs-python (0.065ms KEM, 0.48ms hybrid rekey).\n\n"
        "✔ Active 3GPP 5G Core:\n"
        "  17 Open5GS microservices actively running with real Linux ogstun tunnel interface.\n\n"
        "✔ Autonomous Control Engines:\n"
        "  EWMA anomaly scoring, Bayesian trust decay, multi-criteria route optimization, 5% hysteresis.\n\n"
        "✔ Multi-Baseline Verification:\n"
        "  Superiority verified against Static Routing and Reactive BFD (RFC 5880).\n\n"
        "✔ Governance & Test Suite:\n"
        "  Apache 2.0 license, STRIDE Threat Model (docs/THREAT_MODEL.md), 53/53 pytest tests."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    # Right: Emulated / Modeled (Transparent)
    add_card(s10, 6.8, 1.9, 5.7, 4.9, "Emulated / Modeled (TRL-4 Lab Prototype — No Physical Spacecraft)", CYAN)
    tb_emu = s10.shapes.add_textbox(Inches(7.0), Inches(2.5), Inches(5.3), Inches(4.1))
    tf = tb_emu.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Explicit TRL-4 Lab Prototype Disclosure:\n"
        "  Laboratory breadboard & component validation; strictly software-in-the-loop.\n\n"
        "• Zero Physical Satellite Deployments:\n"
        "  NO physical satellites in orbit, NO space-qualified payloads, NO commercial silicon claimed.\n\n"
        "• RF Physical Layer Emulation:\n"
        "  Linux kernel `tc netem` packet shaping (loss, delay, jitter injection), rather than physical SDRs.\n\n"
        "• Orbital Dynamics Modeling:\n"
        "  Keplerian orbital passes and solar eclipse modeled computationally (standard aerospace protocol).\n\n"
        "• Defensible Novelty Statement to Jury:\n"
        "  'We do not claim to invent a new cipher or launch a physical satellite. Our defensible novelty is the container-native, coordinated execution of proactive zero-trust route recovery and post-quantum session rekeying under electronic warfare, fully validated at TRL-4.'"
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    s10.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 10 (10:15 - 11:15):\n"
        "Juries deeply value scientific honesty. We want to state unequivocally our exact Technology Readiness Level:\n"
        "RAKSHA-NET is a TRL-4 laboratory prototype. We make zero claim of having launched physical satellites or deployed spaceflight hardware.\n\n"
        "What is 100% Real Software:\n"
        "- Our Post-Quantum Cryptography is the real NIST ML-KEM-768 running via native C liboqs routines.\n"
        "- Our 5G Core is the real Open5GS stack running 17 active daemons with real network tunneling.\n"
        "- Our anomaly detection, trust scoring, and routing engines are live, verified by 53 passing automated unit tests.\n"
        "- The software is open source under Apache 2.0 and governed by our STRIDE Threat Model in docs/THREAT_MODEL.md.\n\n"
        "What is Emulated:\n"
        "- The RF physical layer is emulated using Linux kernel `tc netem` packet shaping, and orbital passes are modeled computationally. "
        "This is standard aerospace engineering methodology for control-plane validation prior to hardware integration.\n\n"
        "Our contribution is not inventing a new mathematical cipher or launching a satellite—it is the systems-level coordination of zero-trust routing and post-quantum rekeying to guarantee communications survivability."
    )

    # =========================================================================
    # SLIDE 11: National Impact, Technology Sovereignty & Roadmap
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_slide_background(s11)
    add_header(s11, "Strategic Vision", "National Impact, Technology Sovereignty & 12-Month Roadmap",
               "Empowering India's defense ecosystem through Apache-2.0 open-source innovation, advancing from TRL-4 to TRL-7.")

    # Left: Strategic Value
    add_card(s11, 0.8, 1.9, 4.8, 4.9, "National Sovereignty & Inclusion", GREEN)
    tb_nat = s11.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(4.4), Inches(4.1))
    tf = tb_nat.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Atmanirbhar Bharat Alignment:\n"
        "  Eliminates dependence on proprietary foreign defense hardware; ready for Indian Shakti / Vega RISC-V processors.\n\n"
        "• Open Source Defense Commons:\n"
        "  Permissive Apache 2.0 license enables seamless integration by DRDO (CAIR/DEAL), iDEX partners, and universities.\n\n"
        "• Security Assurance:\n"
        "  STRIDE threat model in docs/THREAT_MODEL.md provides clear operational security specifications.\n\n"
        "• Civilian & Tactical Inclusion:\n"
        "  Maintains communications in isolated Himalayan outposts, island territories, or disaster fly-away kits."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    # Right: 12-Month Roadmap
    add_card(s11, 5.9, 1.9, 6.6, 4.9, "12-Month Technical Roadmap (TRL-4 to TRL-7)", CYAN)
    tb_map = s11.shapes.add_textbox(Inches(6.1), Inches(2.5), Inches(6.2), Inches(4.1))
    tf = tb_map.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "Phase 1: TRL-4 Laboratory Prototype (COMPLETED)\n"
        "  ✔ Open5GS core integration, native C liboqs, BFD comparison, Apache 2.0, 53/53 tests.\n\n"
        "Phase 2: Physical RF SDR Validation (Months 1–3) [TRL-5 Target]\n"
        "  ▶ Connect physical Software-Defined Radios (HackRF / USRP B210) via GNU Radio and ZMQ to test over physical RF channels.\n\n"
        "Phase 3: Over-the-Air 5G & Embedded ARM (Months 4–6) [TRL-6 Target]\n"
        "  ▶ Deploy with open-source srsRAN gNodeBs and benchmark on embedded ARM hardware (Jetson / Raspberry Pi CM4).\n\n"
        "Phase 4: Orbital Flight Payload Proposal (Months 7–12) [TRL-7 Target]\n"
        "  ▶ Formal security audit of session keys and proposal for a 3U CubeSat demonstration payload with IN-SPACe / ISRO."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    s11.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 11 (11:15 - 12:15):\n"
        "Looking at national impact, RAKSHA-NET directly serves India's strategic defense sovereignty.\n"
        "By replacing foreign proprietary cryptographic black-boxes with an Apache 2.0 licensed software controller, "
        "we eliminate foreign supply-chain risks. It can run on commercial COTS processors or India's indigenous Shakti and Vega RISC-V chips.\n\n"
        "Our formal threat model in docs/THREAT_MODEL.md ensures verified security posture, while enabling civilian disaster resilience in remote territories.\n\n"
        "Our roadmap defines a clear maturation path from laboratory emulation to space flight:\n"
        "- Having completed Phase 1 at TRL-4 in the lab, Phase 2 in Months 1 to 3 targets TRL-5 by connecting physical Software-Defined Radios using GNU Radio.\n"
        "- Phase 3 in Months 4 to 6 targets TRL-6 by integrating over-the-air srsRAN 5G basestations on embedded ARM hardware.\n"
        "- And Phase 4 in Months 7 to 12 targets TRL-7 by proposing a flight payload for an Indian CubeSat orbital demonstration via IN-SPACe."
    )

    # =========================================================================
    # SLIDE 12: Conclusion, Live Demo & Q&A
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_slide_background(s12)
    add_header(s12, "Summary & Demonstration", "Conclusion: Mission Readiness & Live Demo Invocation",
               "Proven sub-second resilience, verified post-quantum security, TRL-4 validated, and ready for live inspection.")

    # 3 Summary Cards
    add_card(s12, 0.8, 1.9, 3.6, 3.6, "Availability Restored", GREEN)
    tb = s12.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(3.2), Inches(2.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• 96.8% PDR Restored\n"
        "  +64.5 pp gain over static routing (32.3% PDR) and +21.0 pp gain over Reactive BFD (76.0% PDR).\n\n"
        "• 190 ms Proactive Failover\n"
        "  Sub-second path migration to LEO-2 with zero route flapping (vs 1.5–2.8s BFD timeout)."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    add_card(s12, 4.8, 1.9, 3.6, 3.6, "Quantum-Proof Security", PURPLE)
    tb = s12.shapes.add_textbox(Inches(5.0), Inches(2.5), Inches(3.2), Inches(2.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• NIST ML-KEM-768\n"
        "  Native C execution provides sub-millisecond (0.48ms) dual-hybrid forward-secret rekeying.\n\n"
        "• Zero-Trust STRIDE Model\n"
        "  Quarantines compromised relays in <200ms following docs/THREAT_MODEL.md specifications."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    add_card(s12, 8.8, 1.9, 3.6, 3.6, "TRL-4 Open Source", CYAN)
    tb = s12.shapes.add_textbox(Inches(9.0), Inches(2.5), Inches(3.2), Inches(2.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Apache License 2.0\n"
        "  100% open-source software-defined controller; container-native Docker CNFs (<60 MB RAM).\n\n"
        "• Live 5G Core Verified\n"
        "  17 Open5GS daemons running; 53/53 pytest tests passing (TRL-4 laboratory emulation disclosure)."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    # Live Demo Banner at Bottom
    demo_box = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.75), Inches(11.7), Inches(1.2))
    demo_box.fill.solid()
    demo_box.fill.fore_color.rgb = RGBColor(15, 23, 42)
    demo_box.line.color.rgb = CYAN
    demo_box.line.width = Pt(1.5)

    tb_d = s12.shapes.add_textbox(Inches(1.0), Inches(5.85), Inches(11.3), Inches(1.0))
    tf = tb_d.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "READY FOR LIVE DEMONSTRATION & JURY QUESTIONS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN

    p_cmd = tf.add_paragraph()
    p_cmd.text = (
        "1. Open5GS Live Demo: python -m scripts.run_open5gs_demo  |  "
        "2. Multi-Baseline Scenario: python scripts/run_scenario.py --trials 5 --compare-static  |  "
        "3. Tests: pytest tests/"
    )
    p_cmd.font.name = FONT_BODY
    p_cmd.font.size = Pt(9.5)
    p_cmd.font.color.rgb = TEXT_WHITE

    s12.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 12 (12:15 - 13:00):\n"
        "To conclude, RAKSHA-NET proves that tactical communications resilience and post-quantum security can operate in sub-second unison.\n\n"
        "When electronic warfare strikes, static routing collapses to 32% PDR, and standard 3GPP Reactive BFD delays recovery by up to 2.8 seconds. "
        "RAKSHA-NET detects the telemetry perturbation proactively, fails over in 190 milliseconds, restores delivery to 97% (+64.5 pp vs static, +21.0 pp vs BFD), "
        "and rekeys the session using NIST ML-KEM-768 in under half a millisecond.\n\n"
        "Our prototype is 100% open source under Apache 2.0, evaluated at TRL-4 in our laboratory testbed, and governed by our STRIDE Threat Model in docs/THREAT_MODEL.md. "
        "We welcome the jury to inspect our live demonstration, review our codebase, and we look forward to your questions. Thank you!"
    )

    prs.save(str(OUTPUT_FILE))
    print(f"Successfully generated PowerPoint presentation: {OUTPUT_FILE}")

if __name__ == "__main__":
    create_deck()
