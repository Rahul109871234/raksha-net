"""
generate_ihack_pitch.py
=======================
Generates the 6-Slide Pitch Deck for IIT Bombay E-Summit '26 — <i_hack>
Track: TIH Foundation for IoT & IoE
Project: RESCUE-NET (Autonomous Quantum-Safe IoT-to-Satellite Mesh)
Authors: G Rahul Reddy (24BEC038) & Rajarwar Deependra Sahebrao (22BCS220)
Mentor: Dr. Satish Kumar Tiwari, PDPM IIITDM Jabalpur
"""
import pathlib
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = pathlib.Path("raksha-net/results/rescue_net_ihack_presentation.pptx")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# High-contrast deep-tech palette
BG_COLOR    = RGBColor(11, 15, 25)       # #0B0F19
CARD_BG     = RGBColor(20, 27, 45)       # #141B2D
CARD_BORDER = RGBColor(51, 65, 85)       # #334155
TEXT_WHITE  = RGBColor(248, 250, 252)   # #F8FAFC
TEXT_MUTED  = RGBColor(148, 163, 184)   # #94A3B8
TEXT_BODY   = RGBColor(203, 213, 225)    # #CBD5E1
CYAN        = RGBColor(0, 225, 255)      # #00E1FF
GREEN       = RGBColor(16, 185, 129)     # #10B981
AMBER       = RGBColor(245, 158, 11)     # #F59E0B
PURPLE      = RGBColor(168, 85, 247)     # #A855F7
RED         = RGBColor(239, 68, 68)      # #EF4444

FONT_HEADING = "Segoe UI"
FONT_BODY    = "Segoe UI"

def build_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, tag: str, title: str, subtitle: str):
        p_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_p = p_box.text_frame
        tf_p.word_wrap = True
        tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = 0
        p = tf_p.paragraphs[0]
        p.text = f"●  {tag.upper()}"
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = CYAN

        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.65))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
        p = tf_t.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(21)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        s_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.35))
        tf_s = s_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
        p = tf_s.paragraphs[0]
        p.text = subtitle
        p.font.name = FONT_BODY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, title="", border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        if title:
            tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.18), Inches(width - 0.5), Inches(0.38))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = FONT_HEADING
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = border_color if border_color != CARD_BORDER else CYAN
        return card

    def add_stat_box(slide, left, top, width, height, number: str, label: str, num_color=CYAN):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(15, 23, 42)
        box.line.color.rgb = num_color
        box.line.width = Pt(1.5)
        tb = slide.shapes.add_textbox(Inches(left + 0.1), Inches(top + 0.1), Inches(width - 0.2), Inches(height - 0.2))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p_num = tf.paragraphs[0]
        p_num.text = number
        p_num.alignment = PP_ALIGN.CENTER
        p_num.font.name = FONT_HEADING
        p_num.font.size = Pt(18)
        p_num.font.bold = True
        p_num.font.color.rgb = num_color
        p_lbl = tf.add_paragraph()
        p_lbl.text = label
        p_lbl.alignment = PP_ALIGN.CENTER
        p_lbl.font.name = FONT_BODY
        p_lbl.font.size = Pt(9)
        p_lbl.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 1: Title, Event & Identity
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1)

    tb = s1.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.4))
    p = tb.text_frame.paragraphs[0]
    p.text = "IIT BOMBAY E-SUMMIT '26  |  <i_hack>  |  TIH FOUNDATION FOR IoT & IoE"
    p.font.name = FONT_HEADING
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = CYAN

    tb = s1.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(11.7), Inches(1.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "RESCUE-NET"
    p.font.name = FONT_HEADING
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p2 = tf.add_paragraph()
    p2.text = "Autonomous, Quantum-Safe IoT-to-Satellite Mesh Architecture for Disaster UAVs & Sensor Swarms"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = GREEN

    tb = s1.shapes.add_textbox(Inches(0.8), Inches(2.75), Inches(11.7), Inches(0.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "A self-healing Internet of Everything (IoE) network combining ground LoRa sensors, autonomous search-and-rescue UAVs, "
        "and sub-200ms satellite failover with NIST FIPS 203 Post-Quantum Cryptography for zero-infrastructure disaster zones."
    )
    p.font.name = FONT_BODY
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_BODY

    add_stat_box(s1, 0.8, 3.8, 2.7, 1.25, "+64.5% PDR", "Recovery Under RF Interference", GREEN)
    add_stat_box(s1, 3.8, 3.8, 2.7, 1.25, "190 ms", "Sub-Second Satellite Failover", CYAN)
    add_stat_box(s1, 6.8, 3.8, 2.7, 1.25, "65 µs", "Native C NIST ML-KEM-768 Rekey", PURPLE)
    add_stat_box(s1, 9.8, 3.8, 2.7, 1.25, "~₹51,000", "Total Prototype Hardware BOM", GREEN)

    add_card(s1, 0.8, 5.3, 11.7, 1.6, "Team, Affiliation & Mentor", CYAN)
    tb = s1.shapes.add_textbox(Inches(1.05), Inches(5.75), Inches(11.2), Inches(1.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Student Innovators: G Rahul Reddy (Roll: 24BEC038, 2nd Year ECE) & Rajarwar Deependra Sahebrao (Roll: 22BCS220, 3rd Year CSE)\n"
        "• Institution: PDPM Indian Institute of Information Technology, Design and Manufacturing (IIITDM), Jabalpur\n"
        "• Faculty Mentor: Dr. Satish Kumar Tiwari, Assistant Professor, Department of ECE, PDPM IIITDM Jabalpur\n"
        "• Track Focus: IoT Sensors + Autonomous Robotics + Edge AI + Satellite Communication Deployment"
    )
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 2: Real-World Problem (Disaster & Tactical Blackout)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)
    add_header(s2, "The Real-World Crisis", "The Ground Zero Dilemma: Total Communications & Power Blackout",
               "When natural disasters or tactical conflicts wipe out terrestrial infrastructure, emergency operations are paralyzed.")

    add_card(s2, 0.8, 1.85, 3.6, 5.1, "1. Terrestrial Infrastructure Wipeout", RED)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• What Happens:\n"
        "  Landslides, floods, or earthquakes topple cellular base stations, sever optical fiber, and cut off grid power.\n\n"
        "• The Impact:\n"
        "  First responders and search-and-rescue UAVs enter complete communication blackouts.\n\n"
        "• Ground Truth:\n"
        "  In events like the Wayanad landslides and Uttarakhand floods, rescue teams operated without real-time telemetry for 48+ hours."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s2, 4.8, 1.85, 3.6, 5.1, "2. Limitations of Existing Satcom", AMBER)
    tb = s2.shapes.add_textbox(Inches(5.0), Inches(2.5), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Prohibitive Hardware Cost:\n"
        "  Current military-grade emergency terminals cost ₹40 Lakhs to ₹1+ Crore each and are heavy (>25 kg).\n\n"
        "• Static Link Vulnerability:\n"
        "  Terrain blockage, tree canopy, or RF interference drops packet delivery down to 32.3%, taking minutes to recover.\n\n"
        "• Drone Incompatibility:\n"
        "  Lightweight UAVs cannot carry bulky satellite dishes due to severe payload and battery limits."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s2, 8.8, 1.85, 3.6, 5.1, "3. Interception & Quantum Threat", PURPLE)
    tb = s2.shapes.add_textbox(Inches(9.0), Inches(2.5), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Open Air Interception:\n"
        "  Satellite broadcasts are actively archived by adversaries ('Harvest Now, Decrypt Later').\n\n"
        "• Cryptographic Vulnerability:\n"
        "  Legacy RSA and ECC encryption will be cracked once quantum computing scales.\n\n"
        "• National Mandate:\n"
        "  Critical defense and disaster sensor streams require NIST FIPS 203 quantum-safe forward secrecy today."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 3: 3-Tier IoE Architecture
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)
    add_header(s3, "System Innovation", "The RESCUE-NET Solution: 3-Tier Self-Healing IoE Mesh",
               "Uniting ground IoT sensors, autonomous aerial drone relays, and LEO satellite uplinks into one cohesive loop.")

    add_card(s3, 0.8, 1.85, 3.6, 5.1, "Tier 1: Ground IoT Sensors", CYAN)
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Hardware:\n"
        "  ESP32-S3 + Semtech SX1276 LoRa transceivers (868/433 MHz) + BLE mesh.\n\n"
        "• Function:\n"
        "  Deployed across debris or worn by responders; gathers real-time biometric vitals (heart-rate, SpO2), GPS, gas leaks, and seismic shifts.\n\n"
        "• Self-Healing Mesh:\n"
        "  Multi-hop ad-hoc routing; packets hop across neighboring sensor nodes if direct line-of-sight is lost."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s3, 4.8, 1.85, 3.6, 5.1, "Tier 2: Edge AI UAV Gateway", GREEN)
    tb = s3.shapes.add_textbox(Inches(5.0), Inches(2.5), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Hardware:\n"
        "  Raspberry Pi 5 / Jetson Nano mounted on autonomous search-and-rescue UAV.\n\n"
        "• On-Device Intelligence:\n"
        "  Pure-NumPy GraphSAGE kernel & EWMA anomaly detection (<10ms inference, zero GPU required) prioritizes emergency SOS telemetry.\n\n"
        "• Telemetry Compression:\n"
        "  Lossless zlib moment compression saves ~75% uplink bandwidth on constrained channels."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s3, 8.8, 1.85, 3.6, 5.1, "Tier 3: Quantum-Safe Satcom", PURPLE)
    tb = s3.shapes.add_textbox(Inches(9.0), Inches(2.5), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Hardware:\n"
        "  Software-Defined Radio (HackRF One / ADALM-PLUTO) interfacing with LEO satellites.\n\n"
        "• Sub-Second Failover:\n"
        "  When interference strikes, RAKSHA-NET reroutes traffic to a backup satellite in 190ms with 0% route flapping (5% hysteresis).\n\n"
        "• Post-Quantum Rekey:\n"
        "  Invokes NIST FIPS 203 ML-KEM-768 in native C, re-encrypting sessions in 65 µs."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 4: Empirical Validation & Verified Benchmarks
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)
    add_header(s4, "Experimental Proof", "Empirical Validation: Measured on Active 3GPP 5G Core Testbed",
               "Real code execution across 17 Open5GS core daemons with native C cryptography and kernel network shaping.")

    add_card(s4, 0.8, 1.85, 5.7, 5.1, "Measured Multi-Phase Performance", GREEN)
    table_shape = s4.shapes.add_table(5, 3, Inches(0.95), Inches(2.45), Inches(5.4), Inches(2.8))
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(1.6)
    table.columns[2].width = Inches(1.6)

    h_row = ["Operational Phase", "Static Unmanaged", "RESCUE-NET AI"]
    for i, h in enumerate(h_row):
        c = table.cell(0, i)
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = c.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = CYAN

    data_rows = [
        ("1. Pre-Attack Normal", "96.8% PDR", "96.8% PDR"),
        ("2. Reaction Dip (~190ms)", "33.8% PDR (Collapse)", "83.5% PDR (Transient)"),
        ("3. Sustained Interference", "32.3% PDR (Broken)", "96.8% PDR (Recovered)"),
        ("4. Post-Attack Return", "86.9% PDR", "96.8% PDR")
    ]
    for r_idx, d in enumerate(data_rows):
        for c_idx, txt in enumerate(d):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(19, 27, 46) if r_idx % 2 == 0 else RGBColor(15, 23, 42)
            p = cell.text_frame.paragraphs[0]
            p.text = txt
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_WHITE
            elif c_idx == 1:
                p.font.color.rgb = RED if "Collapse" in txt or "Broken" in txt else TEXT_MUTED
            else:
                p.font.color.rgb = GREEN if "Recovered" in txt or "96.8%" in txt else CYAN

    tb = s4.shapes.add_textbox(Inches(0.95), Inches(5.4), Inches(5.4), Inches(1.35))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Key Verified Results (10 Independent Trials):"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p2 = tf.add_paragraph()
    p2.text = (
        "• +64.5% PDR Gain: Restores 96.8% transmission under jamming (t = 98.8, p = 5.6 × 10⁻¹⁵).\n"
        "• 190 ms Failover: Autonomous path migration to LEO-2 with 0% route flapping.\n"
        "• Sub-Millisecond PQC: NIST ML-KEM-768 runs in 65 µs in native C (3x faster than ECC).\n"
        "• Full Reliability: 53 / 53 automated unit tests passing across all control engines."
    )
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    metric_img = pathlib.Path("raksha-net/results/benchmark_heuristic_metrics.png")
    if metric_img.exists():
        add_card(s4, 6.7, 1.85, 5.8, 5.1, "Measured Telemetry Graph (AI vs Static)", CYAN)
        s4.shapes.add_picture(str(metric_img.resolve()), Inches(6.85), Inches(2.45), Inches(5.5), Inches(4.3))

    # =========================================================================
    # SLIDE 5: Hardware Prototype & Lab BOM (Under ₹51,000)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5)
    add_header(s5, "Physical Deployment", "Hardware Bill of Materials (BOM) & Prototype Setup",
               "A student-feasible hardware implementation mapping simulation directly onto COTS edge devices.")

    add_card(s5, 0.8, 1.85, 11.7, 5.1, "Prototype Hardware Architecture & Cost Breakdown (~₹51,000 Total)", CYAN)

    t_bom = s5.shapes.add_table(6, 4, Inches(1.1), Inches(2.55), Inches(11.1), Inches(4.1))
    table_b = t_bom.table
    table_b.columns[0].width = Inches(2.6)
    table_b.columns[1].width = Inches(4.2)
    table_b.columns[2].width = Inches(1.8)
    table_b.columns[3].width = Inches(2.5)

    headers_b = ["Component", "Specification / Model", "Est. Cost (INR)", "Role in Prototype"]
    for i, h in enumerate(headers_b):
        c = table_b.cell(0, i)
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = c.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = CYAN

    rows_b = [
        ("IoT Ground Sensor Nodes", "3x ESP32-S3 + Semtech SX1276 LoRa (868 MHz) + Vitals/Gas sensors", "₹9,500", "Wearable victim biometrics & debris monitoring"),
        ("Edge AI Gateway", "Raspberry Pi 5 (8GB) + Active Cooler + 64GB MicroSD", "₹11,500", "Runs GraphSAGE, zlib compression, and controller"),
        ("Software-Defined Radio", "HackRF One (1 MHz – 6 GHz) + TCXO + Antennas", "₹18,500", "Transmits/receives satellite telemetry via GNU Radio"),
        ("Conducted RF Test Kit", "SMA Coaxial Cables, 30 dB Attenuators, 2-Way Combiner", "₹6,500", "Enables safe, legal lab jamming without air radiation"),
        ("Portable Field Power", "20,000 mAh PD Power Bank + 18650 Li-ion batteries", "₹5,000", "Self-contained field power for drone/gateway demonstration")
    ]
    for r_idx, d in enumerate(rows_b):
        for c_idx, txt in enumerate(d):
            cell = table_b.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(19, 27, 46) if r_idx % 2 == 0 else RGBColor(15, 23, 42)
            p = cell.text_frame.paragraphs[0]
            p.text = txt
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_WHITE
            elif c_idx == 2:
                p.font.color.rgb = GREEN
                p.font.bold = True
            else:
                p.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 6: Impact, TIH Internship & Future Roadmap
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6)
    add_header(s6, "Impact & Vision", "Real-World Deployment, TIH Partnership & 12-Month Plan",
               "Transitioning a verified disaster-relief testbed into a production-grade IoT-to-Satellite standard.")

    add_card(s6, 0.8, 1.85, 3.6, 5.1, "1. Real-World Applications", GREEN)
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Disaster Management:\n"
        "  Rapid deployment with NDRF / SDRF teams during Himalayan landslides and coastal cyclones.\n\n"
        "• Tactical Defense & UAV Swarms:\n"
        "  Guarantees anti-jamming C2 telemetry for autonomous military drone fleets in contested border zones.\n\n"
        "• Remote Civilian Connectivity:\n"
        "  Bridges isolated tribal villages and island outposts lacking terrestrial fiber."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s6, 4.8, 1.85, 3.6, 5.1, "2. TIH Foundation Partnership Ask", CYAN)
    tb = s6.shapes.add_textbox(Inches(5.0), Inches(2.5), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• TIH Foundation Internship:\n"
        "  Seeking research internship with IIT Bombay's TIH for IoT & IoE to test our algorithms on real physical hardware testbeds.\n\n"
        "• Hardware Prototyping Support:\n"
        "  Access to IIT Bombay IoT/Robotics testing facilities and mentoring from wireless systems faculty.\n\n"
        "• Open-Source Contribution:\n"
        "  Releasing the core ZMQ bridge and C PQC wrapper for the Indian IoT & drone ecosystem."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    add_card(s6, 8.8, 1.85, 3.6, 5.1, "3. 12-Month Technical Roadmap", PURPLE)
    tb = s6.shapes.add_textbox(Inches(9.0), Inches(2.5), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = (
        "• Phase 1: Core Testbed (COMPLETED)\n"
        "  Open5GS 5G Core, native C liboqs, 190ms failover, 53/53 pytest tests.\n\n"
        "• Phase 2: Hardware Assembly (Months 1–3)\n"
        "  Deploy LoRa ESP32 sensor fleet + Raspberry Pi 5 gateway.\n\n"
        "• Phase 3: SDR Over-the-Air (Months 4–6)\n"
        "  Connect HackRF to open-source srsRAN 5G NTN stack.\n\n"
        "• Phase 4: Field Disaster Drill (Months 7–12)\n"
        "  Live demonstration with university UAV club and local disaster agencies."
    )
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_BODY

    prs.save(str(OUTPUT_FILE))
    print(f"[OK] Successfully built 6-slide i_hack presentation: {OUTPUT_FILE.resolve()} ({OUTPUT_FILE.stat().st_size} bytes)")

if __name__ == "__main__":
    build_deck()
