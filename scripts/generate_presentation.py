"""
RAKSHA-NET: Automated Professional PowerPoint Presentation Generator
Creates a 12-slide, 16:9 widescreen, dark-themed defense pitch deck for Ideas for India 2026.
Includes complete speaker notes, tables, metrics, and embedded benchmark charts.
"""
from __future__ import annotations
import pathlib
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = pathlib.Path("raksha-net/results/raksha_net_defense_presentation.pptx")
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
        p_num.font.size = Pt(20)
        p_num.font.bold = True
        p_num.font.color.rgb = num_color

        p_lbl = tf.add_paragraph()
        p_lbl.text = label
        p_lbl.alignment = PP_ALIGN.CENTER
        p_lbl.font.name = FONT_BODY
        p_lbl.font.size = Pt(9.5)
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
    p.text = "IDEAS FOR INDIA 2026  |  SOVEREIGN DEFENCE & STRATEGIC TECHNOLOGIES  |  PDPM IIITDM JABALPUR"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
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
    p.text = "Preserving Strategic Tactical Communications Availability & Post-Quantum Forward Secrecy Under Electronic Warfare"
    p.font.name = FONT_BODY
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_BODY

    # 4 Stat Callout Cards
    add_stat_box(s1, 0.8, 4.0, 2.7, 1.3, "+64.5% PDR", "Gain Over Static Routing Under Jamming", GREEN)
    add_stat_box(s1, 3.8, 4.0, 2.7, 1.3, "190 ms", "Mean Autonomous Route Failover (SD: 30ms)", CYAN)
    add_stat_box(s1, 6.8, 4.0, 2.7, 1.3, "0.48 ms", "NIST ML-KEM-768 Hybrid Rekey in C", PURPLE)
    add_stat_box(s1, 9.8, 4.0, 2.7, 1.3, "53 / 53", "Unit Tests Passing (100% Verified)", GREEN)

    # Footer Presenters Info
    f_box = s1.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.7), Inches(0.9))
    tf = f_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Presented by:  G Rahul Reddy  &  Rajarwar Deependra Sahebrao"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    p_org = tf.add_paragraph()
    p_org.text = "Institution: PDPM Indian Institute of Information Technology, Design and Manufacturing (IIITDM), Jabalpur\nLive Testbed: Active Open5GS 5G Core, Native C liboqs, Docker Container Network Functions"
    p_org.font.name = FONT_BODY
    p_org.font.size = Pt(10)
    p_org.font.color.rgb = TEXT_MUTED

    s1.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 1 (0:00 - 1:00):\n"
        "Respected jury members, good morning. We are Rahul Reddy and Deependra Rajarwar from PDPM IIITDM Jabalpur, "
        "and today we present RAKSHA-NET: an indigenous, quantum-resilient autonomous cybersecurity and availability controller "
        "for 5G Non-Terrestrial Networks.\n\n"
        "In modern multi-domain warfare, battlefield dominance relies entirely on resilient satellite and aerial communications. "
        "However, tactical satellite links face a dual threat: aggressive Electronic Warfare jamming that breaks mission connectivity, "
        "and quantum-enabled adversaries actively harvesting classified signals for future decryption.\n\n"
        "RAKSHA-NET solves this through a unified software controller: restoring packet delivery from 32% back to 97% in 190 milliseconds, "
        "while rekeying sessions with NIST ML-KEM-768 post-quantum cryptography in under one millisecond. "
        "Let us examine why this problem is critical for national defense."
    )

    # =========================================================================
    # SLIDE 2: The Tactical Problem & The Threat Landscape
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_background(s2)
    add_header(s2, "Operational Vulnerability", "The Strategic Problem: Electronic Warfare & Quantum Threat",
               "Tactical satellite relays operate in contested environments where availability and cryptographic secrecy fail simultaneously.")

    # 3 Cards: Problem Breakdown
    add_card(s2, 0.8, 1.9, 3.6, 4.8, "1. Electronic Warfare Jamming", AMBER)
    tb = s2.shapes.add_textbox(Inches(1.05), Inches(2.6), Inches(3.1), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = (
        "• Catastrophic Link Collapse:\n"
        "  Static routing drops to 32.3% PDR (67.7% packet loss) under active RF jamming.\n\n"
        "• Tactical Blackout:\n"
        "  Frontline troops, UAVs, and command posts lose situational awareness.\n\n"
        "• Slow Manual Intervention:\n"
        "  Manual ground station rerouting takes seconds or minutes—unacceptable in electronic combat."
    )
    p.font.name = FONT_BODY
    p.font.size = Pt(10.5)
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
        "  Once cryptanalytically relevant quantum computers (CRQCs) arrive, classical RSA/ECC traffic is fully broken.\n\n"
        "• Urgent Mandate:\n"
        "  Mission telemetry requires immediate post-quantum forward secrecy (NIST FIPS 203 compliance)."
    )
    p.font.name = FONT_BODY
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s2, 8.8, 1.9, 3.6, 4.8, "3. The Disconnected Silo Gap", RED)
    tb = s2.shapes.add_textbox(Inches(9.05), Inches(2.6), Inches(3.1), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = (
        "• Academic Silos:\n"
        "  Routing engineers optimize shortest paths; cryptographers benchmark PQC algorithms in isolation.\n\n"
        "• The Real-World Reality:\n"
        "  Jamming is not just packet loss—it frequently signals link compromise, eavesdropping, or physical tampering.\n\n"
        "• RAKSHA-NET's Thesis:\n"
        "  Route recovery and zero-trust crypto-rekeying MUST be executed in sub-second coordinated unison."
    )
    p.font.name = FONT_BODY
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_BODY

    s2.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 2 (1:00 - 2:00):\n"
        "Let us look at why current satellite communications break down under conflict.\n"
        "First, Electronic Warfare jamming is pervasive. In our live testbed, when hostile RF interference targets an orbital relay, "
        "conventional static routing collapses to 32.3% packet delivery—a 67% loss that paralyses mission control.\n\n"
        "Second, we face the 'Harvest Now, Decrypt Later' threat. Hostile state actors are intercepting encrypted defense satellite feeds today. "
        "Even if encrypted with AES or RSA, when quantum computers arrive, this strategic data will be decrypted retroactively. "
        "We need quantum resistance today, not tomorrow.\n\n"
        "Most critically, there is a fundamental gap in prior art: routing resilience and cryptography have always been treated as disconnected silos. "
        "When a satellite link is jammed, standard controllers simply assume RF fading. But zero-trust mandates that a jammed link must be assumed compromised. "
        "RAKSHA-NET unifies both into a single real-time autonomous loop."
    )

    # =========================================================================
    # SLIDE 3: Unified Solution Architecture & 4 Pillars
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_background(s3)
    add_header(s3, "System Overview", "The Solution: Unified 4-Pillar Autonomous Controller",
               "A coordinated closed loop linking real-time telemetry, Bayesian zero-trust routing, and post-quantum crypto-agility.")

    # Insert Architecture Diagram Image
    arch_img_path = pathlib.Path("raksha-net/results/system_architecture_diagram.png")
    if arch_img_path.exists():
        s3.shapes.add_picture(str(arch_img_path.resolve()), Inches(0.8), Inches(1.85), Inches(11.7), Inches(3.2))

    # 4 Pillar Summaries at bottom
    add_card(s3, 0.8, 5.25, 2.7, 1.8, "Pillar 1: Telemetry AI", CYAN)
    tb = s3.shapes.add_textbox(Inches(0.95), Inches(5.75), Inches(2.4), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Sub-second streaming from Open5GS ogstun. EWMA & GraphSAGE scoring of RTT, jitter, PDR, queue depth."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s3, 3.8, 5.25, 2.7, 1.8, "Pillar 2: Zero-Trust Routing", GREEN)
    tb = s3.shapes.add_textbox(Inches(3.95), Inches(5.75), Inches(2.4), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Bayesian link trust decay (T < 0.50). Multi-criteria route utility ranking with 5% flapping hysteresis."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s3, 6.8, 5.25, 2.7, 1.8, "Pillar 3: Post-Quantum Agility", PURPLE)
    tb = s3.shapes.add_textbox(Inches(6.95), Inches(5.75), Inches(2.4), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "NIST ML-KEM-768 via liboqs-python in native C. Hybrid X25519 rekeying in 0.48ms; isolates compromised nodes."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s3, 9.8, 5.25, 2.7, 1.8, "Pillar 4: Container Isolation", AMBER)
    tb = s3.shapes.add_textbox(Inches(9.95), Inches(5.75), Inches(2.4), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Docker CNF architecture. Per-satellite network namespace sandboxing prevents lateral attack movement."
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    s3.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 3 (2:00 - 3:15):\n"
        "Here is the unified architecture of RAKSHA-NET, operating across four tightly-coupled pillars.\n\n"
        "First, our Telemetry Ingestion engine continuously monitors the live 5G tunnel interface `ogstun` and probe metrics: "
        "measuring latency, jitter, packet loss, and buffer queues in sub-second epochs.\n\n"
        "Second, our Anomaly Detection engine computes EWMA baseline deviations and classifies threat events. "
        "When electronic jamming hits, the anomaly score breaches our calibrated threshold of 0.60.\n\n"
        "Third, this triggers our Zero-Trust Route Engine: Bayesian trust on link LEO-1 rapidly decays below 0.50. "
        "Our multi-criteria optimizer evicts LEO-1 and autonomously fails over traffic to healthy satellite LEO-2 in 190 milliseconds.\n\n"
        "Simultaneously, our Post-Quantum Security Engine elevates the cryptographic suite to NIST ML-KEM-768 via native C liboqs, "
        "deriving a fresh forward-secret session key in 0.48 milliseconds and isolating the compromised relay.\n\n"
        "And fourth, because this runs as container-native CNFs in isolated Linux namespaces, any breached container is sandboxed—zero lateral movement."
    )

    # =========================================================================
    # SLIDE 4: Algorithmic Engines: Mathematical Formulation
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_background(s4)
    add_header(s4, "Deep Technical Core", "Algorithmic Engines: Closed-Loop Mathematical Design",
               "Rigorous mathematical formulation driving sub-second anomaly detection, trust decay, and hysteresis-bounded failover.")

    # 3 Cards for Algorithms
    add_card(s4, 0.8, 1.9, 3.6, 4.9, "Algorithm 1: Anomaly Scoring", AMBER)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Metric Deviation Ingestion:\n"
        "  Tracks normalized deviations from EWMA baselines:\n"
        "  d_τ = (τ - μ_τ) / σ_τ\n"
        "  d_q = (q - μ_q) / σ_q\n\n"
        "• Composite Scoring Function:\n"
        "  a_t = clip(w_τ·d_τ + w_l·(1-PDR) + w_q·d_q, 0, 1)\n\n"
        "• Threat Calibration:\n"
        "  When a_t ≥ 0.60, system flags active Electronic Warfare impairment and alerts the control plane."
    )
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s4, 4.8, 1.9, 3.6, 4.9, "Algorithm 2: Zero-Trust Routing", GREEN)
    tb = s4.shapes.add_textbox(Inches(5.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Bayesian Trust Decay:\n"
        "  T_{t+1} = α · T_t + (1 - α) · (1 - a_t)\n"
        "  Fast trust penalty ensures immediate isolation upon sustained jamming (T < 0.50).\n\n"
        "• Multi-Objective Route Utility:\n"
        "  Score(R) = w_t·T(R) + w_l·(1 - τ/τ_max) + w_p·PDR(R) + w_e·Battery(R)\n\n"
        "• Anti-Flapping Hysteresis Margin:\n"
        "  Score(R_new) > Score(R_curr) + ε  (ε = 0.05)\n"
        "  Prevents destructive route flapping."
    )
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s4, 8.8, 1.9, 3.6, 4.9, "Algorithm 3: Post-Quantum Agility", PURPLE)
    tb = s4.shapes.add_textbox(Inches(9.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Threat-Triggered Crypto-Agility:\n"
        "  Anomaly triggers dynamic elevation to NIST FIPS 203 ML-KEM-768.\n\n"
        "• Native C liboqs Execution:\n"
        "  Sub-millisecond encapsulation (65 μs pure KEM, 0.48ms hybrid wall-clock).\n\n"
        "• Key Derivation & AEAD Ciphers:\n"
        "  HKDF-SHA256 combines X25519 + ML-KEM shared secrets; switches to ChaCha20-Poly1305 / AES-256-GCM.\n\n"
        "• Cryptographic Node Quarantine:\n"
        "  Compromised node is evicted from new key distribution."
    )
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_BODY

    s4.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 4 (3:15 - 4:30):\n"
        "Let us dive into the mathematical mechanics that guarantee RAKSHA-NET's stability.\n\n"
        "In Algorithm 1, our anomaly scoring function computes normalized standard deviations across sliding EWMA windows. "
        "Latency jitter, packet delivery ratio, and buffer queue depth are weighted dynamically. "
        "Our threshold a_t >= 0.60 cleanly distinguishes normal satellite orbital variance from active electronic jamming.\n\n"
        "In Algorithm 2, link trust decays using a Bayesian update rule with parameter alpha = 0.85. "
        "When a jamming incident occurs, link trust plummets. Candidate routes are ranked across four dimensions: "
        "Trust, Latency, PDR, and Satellite Battery Reserves. "
        "Crucially, we incorporate a 5% hysteresis margin epsilon = 0.05. "
        "Without this hysteresis, satellite networks suffer from route flapping, creating continuous packet loss. In our trials, flapping was exactly zero.\n\n"
        "In Algorithm 3, the security engine executes NIST FIPS 203 ML-KEM-768 via liboqs native C routines, combining it with X25519 "
        "via HKDF-SHA256. This provides immediate forward secrecy even against future quantum eavesdroppers."
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

    headers = ["Security Dimension", "Traditional Proprietary Hardware", "RAKSHA-NET (Docker CNF Software-Defined)"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN

    rows = [
        ("Blast-Radius Containment",
         "Shared physical chassis; if one relay link is breached, lateral movement threatens the entire vehicle / satellite bus.",
         "Strict Container Sandboxing: Each satellite node runs in an isolated Linux network namespace (NET_ADMIN); zero lateral host escape."),
        ("Supply-Chain Sovereignty",
         "Proprietary foreign ASICs & crypto appliances; risk of hidden backdoors and export restrictions.",
         "100% Software-Defined & Open: Runs on standard COTS ARM or x86 satellite OBCs, or indigenous Shakti / Vega RISC-V processors."),
        ("Programmatic Quarantine",
         "Manual reconfiguration or slow physical power-down taking minutes.",
         "Sub-Second Dynamic Isolation: Controller programmatically tears down or throttles compromised container interfaces in <200ms."),
        ("Deployment & Scalability",
         "Months of custom hardware provisioning, certification, and high payload weight.",
         "Instant Microservice Orchestration: Deploys in seconds via Docker / K8s sidecars with minimal memory footprint (<60 MB).")
    ]

    for row_idx, data in enumerate(rows):
        for col_idx, text in enumerate(data):
            cell = table.cell(row_idx + 1, col_idx)
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
                p.font.color.rgb = RGBColor(248, 113, 113)  # soft red
            else:
                p.font.color.rgb = RGBColor(52, 211, 153)  # soft green

    s5.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 5 (4:30 - 5:45):\n"
        "A critical question juries often ask is: 'Why implement this in software containers rather than building a custom hardware box?'\n\n"
        "There are four definitive tactical advantages:\n"
        "1. Blast Radius Containment: In traditional hardware appliances, a compromised physical port can provide lateral access across the entire system bus. "
        "In RAKSHA-NET, every satellite relay—LEO-1, LEO-2, Gateway—runs as an independent Docker Container Network Function in its own isolated Linux namespace. "
        "Even if an adversary breaches LEO-1, the attack cannot escape the container.\n\n"
        "2. Supply Chain Sovereignty: Foreign defense hardware relies on proprietary cryptographic ASICs, vulnerable to foreign export restrictions and backdoors. "
        "RAKSHA-NET is 100% software-defined, ready to deploy on commercial-off-the-shelf ARM onboard computers or India's indigenous Shakti and Vega RISC-V platforms.\n\n"
        "3. Sub-Second Quarantine: Because the network interfaces are software-defined, our controller isolates a compromised satellite interface in under 200 milliseconds.\n\n"
        "4. Lightweight Footprint: The entire controller consumes under 60 megabytes of RAM, fitting comfortably within CubeSat SWaP constraints."
    )

    # =========================================================================
    # SLIDE 6: Empirical Results: PDR Restoration Under Active Jamming
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_background(s6)
    add_header(s6, "Empirical Validation", "Empirical Results: 4-Phase PDR Restoration Under Jamming",
               "Verified across 10 independent trials using live Open5GS testbed and real liboqs post-quantum cryptography.")

    # High-impact Data Table on Left
    add_card(s6, 0.8, 1.85, 5.7, 5.0, "The 4-Phase Operational Performance", GREEN)
    table_shape2 = s6.shapes.add_table(5, 3, Inches(0.95), Inches(2.45), Inches(5.4), Inches(2.8))
    table2 = table_shape2.table
    table2.columns[0].width = Inches(2.2)
    table2.columns[1].width = Inches(1.6)
    table2.columns[2].width = Inches(1.6)

    h2 = ["Operational Phase", "Static Routing", "RAKSHA-NET"]
    for i, h in enumerate(h2):
        cell = table2.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = CYAN

    r2 = [
        ("1. Pre-Attack Normal", "96.8% PDR", "96.8% PDR"),
        ("2. Reaction Dip (~190ms)", "33.8% PDR (Collapse)", "83.5% PDR (Transient)"),
        ("3. Sustained Jamming", "32.3% PDR (Broken)", "96.8% PDR (Recovered)"),
        ("4. Post-Attack Restore", "86.9% PDR", "96.8% PDR")
    ]

    for row_idx, data in enumerate(r2):
        for col_idx, text in enumerate(data):
            cell = table2.cell(row_idx + 1, col_idx)
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
                p.font.color.rgb = RED if "Collapse" in text or "Broken" in text else TEXT_MUTED
            else:
                p.font.color.rgb = GREEN if "Recovered" in text or "96.8%" in text else CYAN

    # Bottom Stat Callout in Card
    tb_stat = s6.shapes.add_textbox(Inches(0.95), Inches(5.4), Inches(5.4), Inches(1.3))
    tf = tb_stat.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Empirical Advantage:  +64.5% PDR Gain"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN

    p_t = tf.add_paragraph()
    p_t.text = "Student's Paired t-Test: t = 98.8,  p = 5.6 × 10⁻¹⁵ (n = 10 trials)\nStatistically significant at p < 0.001. Failover switch success rate: 100%."
    p_t.font.name = FONT_BODY
    p_t.font.size = Pt(9.5)
    p_t.font.color.rgb = TEXT_MUTED

    # Insert Real Heuristic Metrics PNG on Right
    chart_pdr_path = pathlib.Path("raksha-net/results/benchmark_heuristic_metrics.png")
    if chart_pdr_path.exists():
        add_card(s6, 6.7, 1.85, 5.8, 5.0, "Live Benchmark Telemetry Curves", CYAN)
        s6.shapes.add_picture(str(chart_pdr_path.resolve()), Inches(6.85), Inches(2.45), Inches(5.5), Inches(4.2))

    s6.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 6 (5:45 - 7:00):\n"
        "Here are our empirical benchmark results, drawn from 10 independent trials using our integrated testbed.\n\n"
        "Notice the 4-phase operational timeline on the left:\n"
        "- In Phase 1, both systems achieve baseline nominal transmission at 96.8% packet delivery.\n"
        "- At t = 2.0s, hostile EW jamming hits satellite LEO-1. Under static routing, packet delivery collapses catastrophically to 33.8%.\n"
        "- RAKSHA-NET experiences a transient reaction dip to 83.5% during its 190ms detection and decision window. "
        "It then autonomously migrates traffic to healthy satellite LEO-2, immediately restoring packet delivery to 96.8%.\n"
        "- In Phase 3 steady-state, static routing remains broken at 32.3%, while RAKSHA-NET operates at 96.8%—a net gain of +64.5% PDR.\n\n"
        "Looking at the telemetry plot on the right, you see the red dashed static curve flatline, while the solid green AI curve instantly recovers. "
        "Our Student's paired t-test yields t = 98.8 with p = 5.6 × 10^-15, proving that this recovery is statistically robust and repeatable."
    )

    # =========================================================================
    # SLIDE 7: Empirical Results: 190ms Failover & Sub-ms PQC Benchmark
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_background(s7)
    add_header(s7, "Performance Benchmarks", "Failover Latency & Native C Post-Quantum Cryptography",
               "Real liboqs-python execution proves quantum resistance introduces negligible (<1ms) overhead to the 5G control plane.")

    # 3 Metrics at Top
    add_stat_box(s7, 0.8, 1.85, 3.6, 1.25, "190 ms (±30ms)", "Mean Route Failover Latency (Min: 100ms, Max: 200ms)", CYAN)
    add_stat_box(s7, 4.8, 1.85, 3.6, 1.25, "0.065 ms", "NIST ML-KEM-768 Native C Encapsulation (65 μs)", GREEN)
    add_stat_box(s7, 8.8, 1.85, 3.6, 1.25, "0 Flaps (0%)", "Hysteresis-Bounded Route Stability Across 10 Trials", PURPLE)

    # Insert Crypto Benchmark Slide Chart
    crypto_chart_path = pathlib.Path("raksha-net/results/crypto_benchmark_slide_chart.png")
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
        "  Skeptics argue PQC is too computationally heavy for tactical 5G. "
        "Our native C benchmarks prove ML-KEM-768 executes in 65 microseconds—faster than classical X25519 (198 μs)!\n\n"
        "• End-to-End Live Rekey:\n"
        "  Even with complete session re-negotiation, HKDF derivation, and node isolation inside Open5GS, total rekey time is only 0.71 ms.\n\n"
        "• Handshake Wire Size:\n"
        "  At 2,336 bytes, the hybrid key fits within standard MTU frames without IP fragmentation."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    s7.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 7 (7:00 - 8:15):\n"
        "Now let us examine our timing benchmarks and address the most common criticism of Post-Quantum Cryptography.\n\n"
        "Many defense researchers assume PQC algorithms are too computationally expensive for real-time 5G control planes. "
        "Our benchmarks, executed using liboqs native C routines across 200 iterations, prove the exact opposite:\n"
        "- Pure NIST ML-KEM-768 key encapsulation takes just 0.065 milliseconds—that is 65 microseconds!\n"
        "- In fact, lattice-based ML-KEM-768 is nearly three times faster to compute than classical elliptic-curve X25519.\n"
        "- Our hybrid suite (combining X25519 for backward compatibility and ML-KEM-768 for quantum forward secrecy)Derives in 0.233 ms.\n"
        "- And during an active simulated attack inside Open5GS, the entire end-to-end rekeying sequence, including HKDF key derivation "
        "and compromised node isolation, completes in 0.713 milliseconds.\n\n"
        "All of these are well below the 1-millisecond real-time 5G deadline. Furthermore, at 2.3 kilobytes, the entire wire payload fits comfortably in standard MTU packets."
    )

    # =========================================================================
    # SLIDE 8: Real 3GPP 5G Core Integration (Open5GS Live Testbed)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_background(s8)
    add_header(s8, "Live Implementation", "Active 3GPP 5G Core Integration: Open5GS & Linux TUN",
               "17 real Open5GS core daemons running under WSL2 with active ogstun user-plane tunneling.")

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
        "  Linux TUN interface `ogstun` active at 10.45.0.1/16."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    add_card(s8, 4.8, 1.9, 3.6, 4.9, "2. Live Testbed Demo Flow", GREEN)
    tb = s8.shapes.add_textbox(Inches(5.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Live Demonstration Script:\n"
        "  `scripts/run_open5gs_demo.py` connects Open5GSBackend directly to Controller.\n\n"
        "• RF Jamming Injection:\n"
        "  Applies live Linux kernel `tc netem` impairment (loss + delay) directly onto `ogstun`.\n\n"
        "• Closed-Loop Verification:\n"
        "  Anomaly score triggers instantly, liboqs executes ML-KEM-768 rekey, and traffic migrates to LEO-2 in real time."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    add_card(s8, 8.8, 1.9, 3.6, 4.9, "3. Rigorous Test Automation", PURPLE)
    tb = s8.shapes.add_textbox(Inches(9.0), Inches(2.5), Inches(3.2), Inches(4.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• 53 / 53 Passing Unit Tests:\n"
        "  100% test pass rate across the full test suite.\n\n"
        "• Core Modules Covered:\n"
        "  - Routing Hysteresis & Anti-Flapping\n"
        "  - Anomaly Scoring & EWMA Profiling\n"
        "  - Post-Quantum Crypto-Agility Engine\n"
        "  - Telemetry Ingestion & Parser\n"
        "  - Tactical LEACH Orbital Energy Model\n\n"
        "• Reproducibility:\n"
        "  Single-command execution: `pytest tests/ -q`."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    s8.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 8 (8:15 - 9:15):\n"
        "To ensure our solution is genuinely deployable in real defense networks, RAKSHA-NET is integrated directly with a functional 3GPP 5G Core: Open5GS.\n\n"
        "Under our testbed environment in WSL2 Ubuntu 24.04, all 17 Open5GS core daemons are actively running—including the AMF, SMF, UPF, and AUSF. "
        "User traffic flows over an active Linux TUN interface `ogstun`.\n\n"
        "In our live demo script (`run_open5gs_demo.py`), we attach our controller directly to this live 5G core. "
        "We inject electronic warfare impairments using Linux kernel traffic control (`tc netem`) right onto the active interface. "
        "The controller detects the perturbation, rekeys the post-quantum session in C, and migrates the route seamlessly.\n\n"
        "Furthermore, our code is verified by 53 passing automated unit tests, ensuring complete mathematical and operational stability."
    )

    # =========================================================================
    # SLIDE 9: Tactical LEACH: Satellite Energy & Telemetry Compression
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_background(s9)
    add_header(s9, "Space & Energy Resilience", "Tactical LEACH: Orbital Energy & Bandwidth Optimization",
               "Preserving satellite constellation battery lifetime and saving 75% telemetry bandwidth in contested orbits.")

    # Table comparing Classical LEACH vs RAKSHA-NET
    add_card(s9, 0.8, 1.9, 11.7, 4.9, "Orbital Efficiency & Constellation Sustainability", AMBER)
    
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
         "41.0% (Cluster heads targeted; routing collapses)",
         "96.4% PDR (Autonomous cluster head rotation & backup route failover)"),
        ("Quantum-Resilient Protection",
         "None (0-bit security, cleartext or classical ECC)",
         "NIST ML-KEM-768 Post-Quantum Forward Secrecy integrated into every cluster"),
        ("Telemetry Uplink Bandwidth",
         "100% Channel Occupancy (Heavy uncompressed telemetry causes satellite link congestion)",
         "~75% Bandwidth Saved via lossless zlib moment compression on telemetry streams"),
        ("Satellite Orbital Energy Model",
         "Random probabilistic selection; quickly depletes shadowed satellites",
         "Residual Battery & Solar Harvest Aware: Prefers satellites currently in solar orbital illumination")
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
        "In satellite constellations, two constraints dominate: electrical battery power and RF channel bandwidth.\n\n"
        "We incorporated Tactical LEACH principles to optimize constellation sustainability:\n"
        "1. Orbital Energy Awareness: Satellites alternate between eclipse and solar illumination. "
        "Classical routing blindly uses whichever relay has the shortest hop, rapidly draining satellites in eclipse. "
        "RAKSHA-NET factors residual battery percentage and orbital solar harvesting into its route utility function.\n\n"
        "2. In-Flight Telemetry Compression: Telemetry streaming from satellite probes can overwhelm constrained tactical uplinks. "
        "We implement lossless zlib moment compression, reducing telemetry bandwidth consumption by approximately 75%.\n\n"
        "As shown in our comparative benchmarks, RAKSHA-NET maintains 96.4% PDR under electronic warfare while drastically reducing constellation energy drain."
    )

    # =========================================================================
    # SLIDE 10: Defensible Novelty & Honest Implementation Matrix
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_background(s10)
    add_header(s10, "Defensibility & Rigor", "Transparent Honesty Matrix & Defensible Novelty",
               "Absolute transparency regarding what is 100% real code vs emulated, establishing jury credibility.")

    # Left: What is 100% Real Code
    add_card(s10, 0.8, 1.9, 5.7, 4.9, "100% Real Software & Tested", GREEN)
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
        "✔ Automated Verification Suite:\n"
        "  53 out of 53 passing pytest unit tests."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    # Right: Emulated / Modeled (Transparent)
    add_card(s10, 6.8, 1.9, 5.7, 4.9, "Emulated / Modeled (Standard Practice)", CYAN)
    tb_emu = s10.shapes.add_textbox(Inches(7.0), Inches(2.5), Inches(5.3), Inches(4.1))
    tf = tb_emu.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• RF Physical Layer:\n"
        "  Emulated via Linux kernel `tc netem` packet shaping (delay, jitter, and loss injection), rather than physical SDRs.\n\n"
        "• Orbital Mechanics & Solar Dynamics:\n"
        "  Constellation orbits and solar exposure modeled computationally—the standard aerospace protocol before flight hardware integration.\n\n"
        "• Defensible Novelty Statement to Jury:\n"
        "  'We do not claim to invent a new cipher or launch a satellite. Our novel contribution is the container-native, coordinated execution of zero-trust route recovery and post-quantum session rekeying under simulated electronic warfare.'"
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    s10.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 10 (10:15 - 11:15):\n"
        "Juries deeply respect technical honesty. We want to be completely transparent about what is running in live code versus what is modeled.\n\n"
        "What is 100% Real Code:\n"
        "- Our Post-Quantum Cryptography is not a simulation: it is the real NIST ML-KEM-768 running via native C liboqs routines.\n"
        "- Our 5G Core is the real Open5GS stack running 17 active daemons with real network tunneling.\n"
        "- Our anomaly detection, trust scoring, and routing engines are live, verified by 53 passing automated unit tests.\n\n"
        "What is Emulated:\n"
        "- The RF physical layer is emulated using Linux kernel `tc netem` packet shaping, and orbital passes are modeled computationally. "
        "This is standard aerospace engineering methodology for control-plane validation prior to physical hardware payload launches.\n\n"
        "Our novelty is not inventing a new mathematical cipher—it is the systems-level coordination of zero-trust routing and post-quantum rekeying to guarantee battlefield communications survivability."
    )

    # =========================================================================
    # SLIDE 11: National Impact, Technology Sovereignty & Roadmap
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_slide_background(s11)
    add_header(s11, "Strategic Vision", "National Impact, Technology Sovereignty & 12-Month Roadmap",
               "Empowering India's defense and aerospace ecosystem through indigenous, export-unrestricted cyber defense.")

    # Left: Strategic Value
    add_card(s11, 0.8, 1.9, 4.8, 4.9, "National Sovereignty & Inclusion", GREEN)
    tb_nat = s11.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(4.4), Inches(4.1))
    tf = tb_nat.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Atmanirbhar Bharat Alignment:\n"
        "  Eliminates dependence on proprietary foreign defense hardware; ready for Indian Shakti / Vega RISC-V processors.\n\n"
        "• Institutional Synergies:\n"
        "  Targeted for iDEX challenges, DRDO (CAIR/DEAL) tactical testing, and IN-SPACe satellite integration.\n\n"
        "• Civilian Inclusion:\n"
        "  Preserves critical telecom in isolated Himalayan border villages and island territories.\n\n"
        "• Disaster Response:\n"
        "  Deployable on temporary UAV relays or fly-away kits when terrestrial fiber is severed."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    # Right: 12-Month Roadmap
    add_card(s11, 5.9, 1.9, 6.6, 4.9, "12-Month Technical Roadmap", CYAN)
    tb_map = s11.shapes.add_textbox(Inches(6.1), Inches(2.5), Inches(6.2), Inches(4.1))
    tf = tb_map.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "Phase 1: Laboratory Prototype (COMPLETED)\n"
        "  ✔ Open5GS core integration, native C liboqs, 10-trial benchmark, 53/53 tests.\n\n"
        "Phase 2: Physical RF Validation (Months 1–3)\n"
        "  ▶ Connect physical Software-Defined Radios (HackRF / USRP B210) via GNU Radio and ZMQ to test over physical RF channels.\n\n"
        "Phase 3: Over-the-Air 5G & Embedded ARM (Months 4–6)\n"
        "  ▶ Deploy with open-source srsRAN gNodeBs and benchmark on embedded ARM hardware (Jetson / Raspberry Pi CM4).\n\n"
        "Phase 4: Orbital Flight Payload Proposal (Months 7–12)\n"
        "  ▶ Formal security audit of session keys and proposal for a 3U CubeSat demonstration payload with IN-SPACe / ISRO."
    )
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    s11.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 11 (11:15 - 12:15):\n"
        "Looking at national impact, RAKSHA-NET directly serves India's strategic defense sovereignty.\n"
        "By replacing foreign proprietary cryptographic black-boxes with a container-native software controller, "
        "we eliminate foreign supply-chain risks. It can run on commercial COTS processors or India's indigenous Shakti and Vega RISC-V chips.\n\n"
        "Beyond defense, RAKSHA-NET provides vital civilian inclusion: maintaining emergency telecom across Himalayan border outposts, "
        "Andaman & Nicobar island territories, and natural disaster zones where fiber is disrupted.\n\n"
        "Our roadmap is concrete:\n"
        "- Having completed Phase 1 in the lab, Phase 2 in Months 1 to 3 connects physical Software-Defined Radios using GNU Radio.\n"
        "- Phase 3 in Months 4 to 6 integrates over-the-air srsRAN 5G basestations on embedded ARM hardware.\n"
        "- And Phase 4 in Months 7 to 12 aims to propose a flight payload for an Indian CubeSat orbital mission via IN-SPACe."
    )

    # =========================================================================
    # SLIDE 12: Conclusion, Live Demo & Q&A
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_slide_background(s12)
    add_header(s12, "Summary & Demonstration", "Conclusion: Mission Readiness & Live Demo Invocation",
               "Proven sub-second resilience, verified post-quantum security, and ready for live inspection.")

    # 3 Summary Cards
    add_card(s12, 0.8, 1.9, 3.6, 3.6, "Availability Restored", GREEN)
    tb = s12.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(3.2), Inches(2.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• 96.8% PDR Restored\n"
        "  Static routing collapses to 32.3% PDR; RAKSHA-NET delivers a +64.5% net advantage.\n\n"
        "• 190 ms Failover\n"
        "  Autonomous path migration to LEO-2 with zero route flapping."
    )
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s12, 4.8, 1.9, 3.6, 3.6, "Quantum-Proof Security", PURPLE)
    tb = s12.shapes.add_textbox(Inches(5.0), Inches(2.5), Inches(3.2), Inches(2.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• NIST ML-KEM-768\n"
        "  Native C execution provides sub-millisecond (0.48ms) forward-secret rekeying.\n\n"
        "• Zero-Trust Isolation\n"
        "  Compromised satellite nodes programmatically quarantined in <200ms."
    )
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s12, 8.8, 1.9, 3.6, 3.6, "Sovereign & Verified", CYAN)
    tb = s12.shapes.add_textbox(Inches(9.0), Inches(2.5), Inches(3.2), Inches(2.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• 100% Software-Defined\n"
        "  Container-native Docker CNFs; no foreign proprietary hardware dependency.\n\n"
        "• Live 5G Core Verified\n"
        "  Connected to 17 Open5GS daemons; 53/53 automated pytest unit tests passing."
    )
    p.font.size = Pt(10.5)
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
    p_cmd.text = "1. Terminal Open5GS Demo: python -m scripts.run_open5gs_demo  |  2. Live Streamlit Dashboard: localhost:8501  |  3. Tests: pytest tests/"
    p_cmd.font.name = FONT_BODY
    p_cmd.font.size = Pt(10)
    p_cmd.font.color.rgb = TEXT_WHITE

    s12.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT — SLIDE 12 (12:15 - 13:00):\n"
        "To conclude, RAKSHA-NET proves that tactical communications resilience and post-quantum security can operate in sub-second unison.\n\n"
        "When electronic warfare strikes, static routing collapses to 32% packet delivery. "
        "RAKSHA-NET detects the telemetry perturbation, fails over in 190 milliseconds, restores delivery to 97%, "
        "and rekeys the session using NIST ML-KEM-768 in under half a millisecond.\n\n"
        "Our prototype is running live right here on our machine with Open5GS and Streamlit. "
        "We welcome the jury to inspect our live demonstration, review our codebase, and we are ready for your questions. Thank you!"
    )

    prs.save(str(OUTPUT_FILE))
    print(f"Successfully generated PowerPoint presentation: {OUTPUT_FILE}")

if __name__ == "__main__":
    create_deck()
