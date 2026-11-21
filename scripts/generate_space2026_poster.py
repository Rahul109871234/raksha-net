#!/usr/bin/env python3
"""
generate_space2026_poster.py
============================
Generates the official publication-grade Single-Page A0 PDF poster for:
Sixteenth International Conference on Security, Privacy and Applied Cryptographic Engineering (SPACE 2026)
Organized by C-DAC Bengaluru · Venue: The Chancery Pavilion, Bengaluru, India

Requirements:
  - Exact single-page A0 dimensions: 841 mm × 1189 mm (2383.94 pt × 3370.39 pt)
  - Topic: Applied Cryptographic Engineering, 5G/NTN Cyber-Resilience, Hardware Security
  - Output: results/SPACE2026_RAKSHA_NET_Poster_A0.pdf
"""

import os
import sys
import math
import pathlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A0
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PDF = RESULTS_DIR / "SPACE2026_RAKSHA_NET_Poster_A0.pdf"

# -----------------------------------------------------------------------------
# Dimensions & Grid
# -----------------------------------------------------------------------------
PAGE_WIDTH, PAGE_HEIGHT = A0  # (2383.937 pt, 3370.394 pt)

HEADER_HEIGHT = 440
FOOTER_HEIGHT = 85
TOP_MARGIN = 40
BOTTOM_MARGIN = 25
SIDE_MARGIN = 50

CONTENT_TOP = PAGE_HEIGHT - HEADER_HEIGHT - 35
CONTENT_BOTTOM = FOOTER_HEIGHT + 35
CONTENT_HEIGHT = CONTENT_TOP - CONTENT_BOTTOM  # ~2775 pt

NUM_COLS = 3
COL_GAP = 48
COL_WIDTH = (PAGE_WIDTH - 2 * SIDE_MARGIN - (NUM_COLS - 1) * COL_GAP) / NUM_COLS  # ~729.3 pt

# Colors
C_DARK_BG = colors.HexColor("#090d16")
C_HEADER_BG = colors.HexColor("#0b1329")
C_HEADER_ACCENT = colors.HexColor("#38bdf8")
C_GOLD = colors.HexColor("#f59e0b")
C_WHITE = colors.HexColor("#ffffff")
C_PAGE_BG = colors.HexColor("#f8fafc")
C_CARD_BG = colors.HexColor("#ffffff")
C_CARD_BORDER = colors.HexColor("#cbd5e1")
C_TEXT_MAIN = colors.HexColor("#0f172a")
C_TEXT_MUTED = colors.HexColor("#475569")
C_TEXT_LIGHT = colors.HexColor("#e2e8f0")
C_PRIMARY_BLUE = colors.HexColor("#1d4ed8")
C_CYAN_ACCENT = colors.HexColor("#0284c7")
C_EMERALD = colors.HexColor("#047857")
C_VIOLET = colors.HexColor("#6d28d9")
C_ROSE = colors.HexColor("#be123c")

# -----------------------------------------------------------------------------
# Typography Styles
# -----------------------------------------------------------------------------
styles = getSampleStyleSheet()

style_title = ParagraphStyle(
    "PosterTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=44,
    leading=54,
    textColor=C_WHITE,
    alignment=TA_CENTER,
)

style_subtitle = ParagraphStyle(
    "PosterSubtitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=26,
    leading=34,
    textColor=C_HEADER_ACCENT,
    alignment=TA_CENTER,
)

style_authors = ParagraphStyle(
    "PosterAuthors",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=30,
    textColor=C_WHITE,
    alignment=TA_CENTER,
)

style_affil = ParagraphStyle(
    "PosterAffil",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=18,
    leading=25,
    textColor=colors.HexColor("#94a3b8"),
    alignment=TA_CENTER,
)

style_conf_tag = ParagraphStyle(
    "PosterConfTag",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=16,
    leading=22,
    textColor=C_GOLD,
    alignment=TA_CENTER,
)

style_card_title = ParagraphStyle(
    "CardTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=28,
    textColor=C_WHITE,
    alignment=TA_LEFT,
)

style_card_body = ParagraphStyle(
    "CardBody",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=14.5,
    leading=21.5,
    textColor=C_TEXT_MAIN,
    alignment=TA_LEFT,
)

style_card_body_bold = ParagraphStyle(
    "CardBodyBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=14.5,
    leading=21.5,
    textColor=C_TEXT_MAIN,
    alignment=TA_LEFT,
)

style_card_body_muted = ParagraphStyle(
    "CardBodyMuted",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=13,
    leading=18,
    textColor=C_TEXT_MUTED,
    alignment=TA_LEFT,
)

style_callout_title = ParagraphStyle(
    "CalloutTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=26,
    textColor=C_PRIMARY_BLUE,
    alignment=TA_CENTER,
)

style_callout_label = ParagraphStyle(
    "CalloutLabel",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=11.5,
    leading=15,
    textColor=C_TEXT_MUTED,
    alignment=TA_CENTER,
)

style_table_header = ParagraphStyle(
    "TableHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=12.5,
    leading=16,
    textColor=C_WHITE,
    alignment=TA_CENTER,
)

style_table_cell = ParagraphStyle(
    "TableCell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=11.5,
    leading=15,
    textColor=C_TEXT_MAIN,
    alignment=TA_LEFT,
)

style_table_cell_bold = ParagraphStyle(
    "TableCellBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11.5,
    leading=15,
    textColor=C_TEXT_MAIN,
    alignment=TA_LEFT,
)

style_table_cell_center = ParagraphStyle(
    "TableCellCenter",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=11.5,
    leading=15,
    textColor=C_TEXT_MAIN,
    alignment=TA_CENTER,
)

# -----------------------------------------------------------------------------
# Drawing Helpers
# -----------------------------------------------------------------------------
def draw_rounded_card(c: canvas.Canvas, x, y, width, height, title, header_color=C_PRIMARY_BLUE, radius=10):
    """Draws a professional card with rounded borders, a colored header banner, and drop shadow."""
    c.saveState()
    # Subtle drop shadow
    c.setFillColor(colors.HexColor("#e2e8f0"))
    c.roundRect(x + 3, y - 3, width, height, radius, fill=1, stroke=0)
    
    # White card container
    c.setFillColor(C_CARD_BG)
    c.setStrokeColor(C_CARD_BORDER)
    c.setLineWidth(1.8)
    c.roundRect(x, y, width, height, radius, fill=1, stroke=1)
    
    # Colored header ribbon
    header_h = 44
    c.setFillColor(header_color)
    # Clip path for rounded top corners
    p = c.beginPath()
    p.moveTo(x, y + height - radius)
    p.arcTo(x, y + height - 2*radius, x + 2*radius, y + height, radius)
    p.lineTo(x + width - radius, y + height)
    p.arcTo(x + width - 2*radius, y + height, x + width, y + height - 2*radius, radius)
    p.lineTo(x + width, y + height - header_h)
    p.lineTo(x, y + height - header_h)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    
    # Render header title
    p_title = Paragraph(f"<b>{title}</b>", style_card_title)
    w, h = p_title.wrap(width - 40, header_h)
    p_title.drawOn(c, x + 20, y + height - 34)
    
    c.restoreState()


def draw_stat_box(c: canvas.Canvas, x, y, width, height, num_str, label_str, num_color=C_PRIMARY_BLUE, bg_color=colors.HexColor("#f1f5f9")):
    """Draws a compact stat metric callout box."""
    c.saveState()
    c.setFillColor(bg_color)
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setLineWidth(1.2)
    c.roundRect(x, y, width, height, 8, fill=1, stroke=1)
    
    c.setFillColor(num_color)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(x + width/2.0, y + height - 30, num_str)
    
    p_label = Paragraph(label_str, style_callout_label)
    w, h = p_label.wrap(width - 12, height - 32)
    p_label.drawOn(c, x + 6, y + 8)
    c.restoreState()


def build_poster():
    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=A0)
    c.setTitle("RAKSHA-NET: Applied Cryptographic Engineering & 5G NTN Resilience (SPACE 2026)")
    c.setAuthor("G. Rahul Reddy & Dr. Satish Kumar Tiwari (PDPM IIITDM Jabalpur)")
    c.setSubject("SPACE 2026 Poster Submission - Applied Cryptography & Hardware Security")

    # 1. Fill Page Canvas Background
    c.setFillColor(C_PAGE_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    # -------------------------------------------------------------------------
    # 2. Header Banner (Top)
    # -------------------------------------------------------------------------
    c.saveState()
    # Gradient/Dark Navy Header Background
    c.setFillColor(C_HEADER_BG)
    c.rect(0, PAGE_HEIGHT - HEADER_HEIGHT, PAGE_WIDTH, HEADER_HEIGHT, fill=1, stroke=0)
    
    # Subtle bottom accent lines
    c.setStrokeColor(C_HEADER_ACCENT)
    c.setLineWidth(4)
    c.line(0, PAGE_HEIGHT - HEADER_HEIGHT, PAGE_WIDTH, PAGE_HEIGHT - HEADER_HEIGHT)
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(2)
    c.line(0, PAGE_HEIGHT - HEADER_HEIGHT - 3, PAGE_WIDTH, PAGE_HEIGHT - HEADER_HEIGHT - 3)

    # Top Conference Venue Pill / Tag
    conf_tag_text = (
        "<b>SPACE 2026</b> · 16TH INTERNATIONAL CONFERENCE ON SECURITY, PRIVACY AND APPLIED CRYPTOGRAPHIC ENGINEERING<br/>"
        "ORGANISED BY <b>CENTRE FOR DEVELOPMENT OF ADVANCED COMPUTING (C-DAC), BENGALURU</b> · 16–19 DECEMBER 2026 · BENGALURU, INDIA"
    )
    p_tag = Paragraph(conf_tag_text, style_conf_tag)
    p_tag.wrapOn(c, PAGE_WIDTH - 120, 50)
    p_tag.drawOn(c, 60, PAGE_HEIGHT - 65)

    # Main Poster Title
    title_text = "RAKSHA-NET: Autonomous Cross-Layer Resilience & Post-Quantum<br/>Cryptographic Agility for 5G Non-Terrestrial Networks"
    p_main_title = Paragraph(title_text, style_title)
    p_main_title.wrapOn(c, PAGE_WIDTH - 160, 120)
    p_main_title.drawOn(c, 80, PAGE_HEIGHT - 195)

    # Author Names & Mentorship
    authors_text = (
        "<b>G. Rahul Reddy</b><sup>1</sup> &nbsp;&nbsp;·&nbsp;&nbsp; "
        "<b>Dr. Satish Kumar Tiwari</b><sup>1</sup>"
    )
    p_authors = Paragraph(authors_text, style_authors)
    p_authors.wrapOn(c, PAGE_WIDTH - 160, 40)
    p_authors.drawOn(c, 80, PAGE_HEIGHT - 245)

    # Affiliations & Contact
    affil_text = (
        "<sup>1</sup> Department of Electronics & Communication Engineering, "
        "<b>PDPM Indian Institute of Information Technology, Design & Manufacturing (IIITDM), Jabalpur</b>, India<br/>"
        "Lead Researcher Email: <u>24bec038@iiitdmj.ac.in</u> &nbsp;|&nbsp; Faculty Mentor: <u>stiwari@iiitdmj.ac.in</u> &nbsp;|&nbsp; "
        "Artifact Repository: <u>https://github.com/Rahul109871234/raksha-net</u> (Apache-2.0)"
    )
    p_affil = Paragraph(affil_text, style_affil)
    p_affil.wrapOn(c, PAGE_WIDTH - 160, 60)
    p_affil.drawOn(c, 80, PAGE_HEIGHT - 325)

    # Header Quick Highlights Ribbon
    badges_w = PAGE_WIDTH - 240
    badges_x = 120
    badges_y = PAGE_HEIGHT - 405
    c.setFillColor(colors.HexColor("#1e293b"))
    c.setStrokeColor(colors.HexColor("#334155"))
    c.setLineWidth(1.5)
    c.roundRect(badges_x, badges_y, badges_w, 48, 8, fill=1, stroke=1)
    
    badge_items = [
        ("NIST FIPS 203 ML-KEM-768", C_HEADER_ACCENT),
        ("IETF RFC 9370 Dual Hybrid", C_GOLD),
        ("0.091 ms Zero-GPU GNN", colors.HexColor("#34d399")),
        ("188 ms Failover (Zero Flap)", colors.HexColor("#f472b6")),
        ("3GPP Rel-17 Open5GS Core", colors.HexColor("#a78bfa")),
        ("Apache 2.0 Open Source", C_WHITE),
    ]
    step_w = badges_w / len(badge_items)
    for i, (b_text, b_col) in enumerate(badge_items):
        bx = badges_x + i * step_w
        c.setFillColor(b_col)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(bx + step_w / 2.0, badges_y + 16, b_text)
        if i < len(badge_items) - 1:
            c.setStrokeColor(colors.HexColor("#475569"))
            c.setLineWidth(1)
            c.line(bx + step_w, badges_y + 8, bx + step_w, badges_y + 40)

    c.restoreState()

    # -------------------------------------------------------------------------
    # 3. Footer Banner (Bottom)
    # -------------------------------------------------------------------------
    c.saveState()
    c.setFillColor(C_HEADER_BG)
    c.rect(0, 0, PAGE_WIDTH, FOOTER_HEIGHT, fill=1, stroke=0)
    c.setStrokeColor(C_HEADER_ACCENT)
    c.setLineWidth(2.5)
    c.line(0, FOOTER_HEIGHT, PAGE_WIDTH, FOOTER_HEIGHT)

    footer_left = (
        "<b>SPACE 2026: 16th International Conference on Security, Privacy and Applied Cryptographic Engineering</b><br/>"
        "Proceedings & Poster Track · C-DAC Bengaluru · Venue: The Chancery Pavilion, Residency Road, Bengaluru, Karnataka"
    )
    p_foot_l = Paragraph(footer_left, ParagraphStyle("FL", fontName="Helvetica", fontSize=13, leading=18, textColor=colors.HexColor("#94a3b8")))
    p_foot_l.wrapOn(c, 1100, 50)
    p_foot_l.drawOn(c, SIDE_MARGIN + 10, 20)

    footer_right = (
        "<b>Sovereign Cyber-Resilience for India</b> · PDPM IIITDM Jabalpur<br/>"
        "Code, Pre-Trained GNN Weights, Open5GS Profiles & Test Suite: <b>github.com/Rahul109871234/raksha-net</b>"
    )
    p_foot_r = Paragraph(footer_right, ParagraphStyle("FR", fontName="Helvetica", fontSize=13, leading=18, textColor=colors.HexColor("#94a3b8"), alignment=TA_RIGHT))
    p_foot_r.wrapOn(c, 1100, 50)
    p_foot_r.drawOn(c, PAGE_WIDTH - SIDE_MARGIN - 1110, 20)
    c.restoreState()

    # -------------------------------------------------------------------------
    # Column Setup Calculations
    # -------------------------------------------------------------------------
    col1_x = SIDE_MARGIN
    col2_x = SIDE_MARGIN + COL_WIDTH + COL_GAP
    col3_x = SIDE_MARGIN + 2 * (COL_WIDTH + COL_GAP)

    # =========================================================================
    # COLUMN 1: Problem Formulation, Threat Vectors & 5G NTN Architecture
    # =========================================================================
    curr_y = CONTENT_TOP

    # --- CARD 1.1: 5G NTN Threat Landscape ---
    card1_h = 740
    curr_y -= card1_h
    draw_rounded_card(c, col1_x, curr_y, COL_WIDTH, card1_h, "1. The 5G NTN Convergence & Multi-Tier Threat", C_PRIMARY_BLUE)
    
    c1_content = [
        "In <b>3GPP Release-18 (5G-Advanced)</b> and emerging <b>6G systems</b>, terrestrial Open Radio Access Networks (O-RAN) and Non-Terrestrial Networks (NTN) converge into a heterogeneous Space-Air-Ground Integrated Network (SAGIN).",
        "While offering global connectivity, this convergence exposes strategic communication to a <b>synchronized multi-surface threat vector</b>:",
        "<b>1. Terrestrial Edge (O-RAN Radio Units):</b> Hostile adversaries inject False Data (FDI), spoofing low PRB load (e.g. 18%) or corrupted SINR. Near-RT RIC xApps (Traffic Steering vs Energy Saving) oscillate uncontrollably, forcing active capacity cells into sleep and causing <b>55.4% unmanaged SLA collapse</b>.",
        "<b>2. Space Layer (LEO Satellite Uplinks):</b> Electronic Warfare (high-power RF Jamming) drops satellite feeder packet delivery to <b>29.6% PDR (70.4% loss)</b>, severing tactical command loops.",
        "<b>3. Harvest-Now-Decrypt-Later (HNDL):</b> Adversaries passively intercept satellite ciphertext to store it for future cryptanalysis once large-scale quantum computers emerge. Classical ECC (X25519) and RSA will be completely compromised by Shor's algorithm.",
    ]
    cy = curr_y + card1_h - 75
    for text in c1_content:
        p = Paragraph(text, style_card_body)
        w, h = p.wrap(COL_WIDTH - 40, 200)
        p.drawOn(c, col1_x + 20, cy - h)
        cy -= (h + 14)

    # Threat stat boxes inside Card 1.1
    draw_stat_box(c, col1_x + 20, cy - 85, (COL_WIDTH - 60)/3, 78, "55.40%", "SLA Failure (Unmanaged FDI)", C_ROSE)
    draw_stat_box(c, col1_x + 30 + (COL_WIDTH - 60)/3, cy - 85, (COL_WIDTH - 60)/3, 78, "29.6% PDR", "Space RF Jamming Loss", C_ROSE)
    draw_stat_box(c, col1_x + 40 + 2*(COL_WIDTH - 60)/3, cy - 85, (COL_WIDTH - 60)/3, 78, "HNDL Threat", "Quantum Interception", C_GOLD)

    # --- CARD 1.2: Core Research Thesis ---
    curr_y -= 25
    card2_h = 580
    curr_y -= card2_h
    draw_rounded_card(c, col1_x, curr_y, COL_WIDTH, card2_h, "2. Core Thesis: Why Routing & Cryptography Must Unify", C_CYAN_ACCENT)

    c2_content = [
        "<b>The Conventional Silo:</b> In existing 5G and satellite architectures, routing availability and cryptographic key management are isolated into independent subsystems:",
        "• <i>Routing protocols</i> (BGP, BFD, ECMP) treat link degradation purely as an availability fault, ignoring whether the degradation was caused by active adversarial jamming or wiretap insertion.",
        "• <i>Applied cryptographers</i> benchmark post-quantum algorithms in isolation, ignoring network dynamics, queue drop rates, and rekeying storm latencies.",
        "<b>The RAKSHA-NET Paradigm:</b> <i>Link degradation is an active cryptographic tampering signal.</i>",
        "When electronic warfare hits an orbital link, RAKSHA-NET does not simply switch paths: it proactively treats the degraded link as potentially compromised, migrates traffic to strategic backup satellites in <b>188 ms</b>, and concurrently triggers <b>NIST FIPS 203 ML-KEM-768</b> post-quantum session rekeying to isolate the adversary.",
    ]
    cy = curr_y + card2_h - 75
    for text in c2_content:
        p = Paragraph(text, style_card_body)
        w, h = p.wrap(COL_WIDTH - 40, 200)
        p.drawOn(c, col1_x + 20, cy - h)
        cy -= (h + 14)

    # --- CARD 1.3: End-to-End System Architecture Diagram ---
    curr_y -= 25
    card3_h = 1380
    curr_y -= card3_h
    draw_rounded_card(c, col1_x, curr_y, COL_WIDTH, card3_h, "3. Cross-Layer System Architecture & SAGIN Topology", C_DARK_BG)

    arch_img_path = RESULTS_DIR / "aicop_raksha_architecture.png"
    if arch_img_path.exists():
        img_w = COL_WIDTH - 40
        img_h = (1890 / 3120) * img_w  # preserve aspect ratio (~420 pt)
        img_y = curr_y + card3_h - 65 - img_h
        c.drawImage(str(arch_img_path), col1_x + 20, img_y, width=img_w, height=img_h)
        cy = img_y - 20
    else:
        cy = curr_y + card3_h - 80

    arch_desc = [
        "<b>Three-Tier Hierarchical Defense Architecture:</b>",
        "• <b>Tier 3: Space NTN Uplink (RAKSHA-NET Core):</b> Linux TUN <code>ogstun</code> interface interfacing with 3GPP Rel-17 Open5GS core functions. Hosts Page's CUSUM sequential change-point detector, 5% hysteresis barrier, and native C ML-KEM-768 PQC session manager.",
        "• <b>Tier 2: Terrestrial O-RAN Near-RT RIC (AICOP Engine):</b> Inductive pure-NumPy 2-Layer GraphSAGE inference engine running at $0.091\\text{ ms}$. Cross-validates reported telemetry against observable spatial neighbor consensus and temporal EWMA baselines.",
        "• <b>Tier 1: Physical Radio Nodes (12-Cell Planar Grid):</b> Dual-band layout: 700 MHz Macro Umbrella Tier (Cells 1–6, non-sleeping) and 3.5 GHz Capacity Micro Tier (Cells 7–12, dynamic power gating under trust control).",
        "<b>Cross-Layer Control Bus:</b> Terrestrial edge trust deficits proactively pre-arm satellite failover prior to physical service interruption ($r = 0.754$ coupling rule).",
    ]
    for text in arch_desc:
        p = Paragraph(text, style_card_body)
        w, h = p.wrap(COL_WIDTH - 40, 200)
        p.drawOn(c, col1_x + 20, cy - h)
        cy -= (h + 12)

    # =========================================================================
    # COLUMN 2: Applied Cryptographic Engineering & Edge AI
    # =========================================================================
    curr_y = CONTENT_TOP

    # --- CARD 2.1: Post-Quantum Crypto-Agility Engine ---
    card4_h = 870
    curr_y -= card4_h
    draw_rounded_card(c, col2_x, curr_y, COL_WIDTH, card4_h, "4. Applied Post-Quantum Crypto-Agility (IETF RFC 9370)", C_PRIMARY_BLUE)

    c4_content = [
        "<b>Standardized Hybrid Key Exchange:</b> In accordance with <b>IETF RFC 9370</b> and <b>RFC 9242</b> (*Multiple Key Exchanges in IKEv2*), RAKSHA-NET binds classical elliptic-curve Diffie-Hellman with lattice-based post-quantum key encapsulation:",
        "$$\\text{Session Key } K = \\text{HKDF-Extract-and-Expand}\\Big(\\text{salt}=\\text{sid},\\; ss_{\\text{classical}} \\;\\parallel\\; ss_{\\text{pqc}},\\; \\text{\"RAKSHA-AEAD\"},\\; 32\\Big)$$",
        "• <b>Classical Component:</b> ECDH X25519 (32-byte public key, 32-byte shared secret).",
        "• <b>Post-Quantum Component:</b> <b>NIST FIPS 203 ML-KEM-768</b> (Kyber) (1,184-byte public key, 1,088-byte ciphertext).",
        "• <b>Dual-Hardness Security:</b> Confidentiality is preserved as long as <i>at least one</i> mathematical assumption (discrete logarithm or Module-LWE) remains uncompromised.",
        "<b>Cryptographic Lifecycle & Automated Rekey Policy:</b>",
        "1. <i>Pre-emptive Rekey:</i> Triggered whenever Link Anomaly Score $a_t \\ge 0.60$ or trust drops below 0.50.",
        "2. <i>Forward Secrecy Quarantine:</i> Upon autonomous failover, the degraded satellite relay is immediately purged from future key schedules, preventing replay or session hijacking.",
        "3. <i>Anti-Replay Window:</i> Strictly monotonic 96-bit packet counters integrated with AEAD nonces.",
    ]
    cy = curr_y + card4_h - 75
    for text in c4_content:
        p = Paragraph(text, style_card_body)
        w, h = p.wrap(COL_WIDTH - 40, 200)
        p.drawOn(c, col2_x + 20, cy - h)
        cy -= (h + 13)

    # --- CARD 2.2: Dynamic Suite Selection & liboqs Benchmarks ---
    curr_y -= 25
    card5_h = 850
    curr_y -= card5_h
    draw_rounded_card(c, col2_x, curr_y, COL_WIDTH, card5_h, "5. Hardware Crypto Benchmarks & Dynamic AEAD Selection", C_VIOLET)

    c5_intro = (
        "<b>Architectural Suite Selection Policy:</b> The controller continuously monitors link bandwidth and threat state to select the optimal AEAD cipher suite:"
    )
    p = Paragraph(c5_intro, style_card_body)
    w, h = p.wrap(COL_WIDTH - 40, 100)
    p.drawOn(c, col2_x + 20, curr_y + card5_h - 75)

    # Crypto Benchmark Table
    crypto_data = [
        [
            Paragraph("<b>Suite Name</b>", style_table_header),
            Paragraph("<b>Key Exchange</b>", style_table_header),
            Paragraph("<b>AEAD Cipher</b>", style_table_header),
            Paragraph("<b>Handshake<br/>Bytes</b>", style_table_header),
            Paragraph("<b>Execution<br/>Time</b>", style_table_header),
            Paragraph("<b>AEAD<br/>Throughput</b>", style_table_header),
        ],
        [
            Paragraph("CLASSICAL_CHACHA", style_table_cell_bold),
            Paragraph("X25519", style_table_cell),
            Paragraph("ChaCha20-Poly1305", style_table_cell),
            Paragraph("64 B", style_table_cell_center),
            Paragraph("0.120 ms", style_table_cell_center),
            Paragraph("55.6 MB/s", style_table_cell_center),
        ],
        [
            Paragraph("PQC_CHACHA", style_table_cell_bold),
            Paragraph("ML-KEM-768", style_table_cell),
            Paragraph("ChaCha20-Poly1305", style_table_cell),
            Paragraph("2,272 B", style_table_cell_center),
            Paragraph("<b>0.045 ms</b>", style_table_cell_center),
            Paragraph("57.4 MB/s", style_table_cell_center),
        ],
        [
            Paragraph("PQC_AES", style_table_cell_bold),
            Paragraph("ML-KEM-768", style_table_cell),
            Paragraph("AES-256-GCM", style_table_cell),
            Paragraph("2,272 B", style_table_cell_center),
            Paragraph("<b>0.045 ms</b>", style_table_cell_center),
            Paragraph("<b>74.3 MB/s</b>", style_table_cell_center),
        ],
        [
            Paragraph("HYBRID_CHACHA", style_table_cell_bold),
            Paragraph("X25519 + ML-KEM", style_table_cell),
            Paragraph("ChaCha20-Poly1305", style_table_cell),
            Paragraph("2,336 B", style_table_cell_center),
            Paragraph("0.167 ms", style_table_cell_center),
            Paragraph("56.8 MB/s", style_table_cell_center),
        ],
        [
            Paragraph("HYBRID_AES", style_table_cell_bold),
            Paragraph("X25519 + ML-KEM", style_table_cell),
            Paragraph("AES-256-GCM", style_table_cell),
            Paragraph("2,336 B", style_table_cell_center),
            Paragraph("0.167 ms", style_table_cell_center),
            Paragraph("<b>74.1 MB/s</b>", style_table_cell_center),
        ],
    ]
    t_crypto = Table(crypto_data, colWidths=[140, 115, 150, 85, 95, 95])
    t_crypto.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    tw, th = t_crypto.wrap(COL_WIDTH - 40, 300)
    t_crypto.drawOn(c, col2_x + 20, curr_y + card5_h - 110 - th)

    c5_notes = [
        "<b>Engineering Rationale for ChaCha20-Poly1305 on Edge Nodes:</b>",
        "• On host CPUs with AES-NI instructions, AES-256-GCM achieves 74.3 MB/s. However, embedded ARM Cortex-M and Indian Shakti RISC-V nodes often lack hardware AES engines.",
        "• On such nodes, software AES is up to 3× slower and vulnerable to cache-timing attacks (Bernstein 2005). <b>ChaCha20-Poly1305 is constant-time in software by design (RFC 8439)</b>, making it the mathematically defensible choice for low-power edge satellite payloads.",
    ]
    cy = curr_y + card5_h - 130 - th
    for text in c5_notes:
        p = Paragraph(text, style_card_body)
        w, h = p.wrap(COL_WIDTH - 40, 150)
        p.drawOn(c, col2_x + 20, cy - h)
        cy -= (h + 10)

    # --- CARD 2.3: Inductive GraphSAGE & Pareto Arbitration ---
    curr_y -= 25
    card6_h = 1000
    curr_y -= card6_h
    draw_rounded_card(c, col2_x, curr_y, COL_WIDTH, card6_h, "6. Inductive GraphSAGE Trust & Pareto Arbitration", C_EMERALD)

    c6_content = [
        "<b>Non-Oracle Spatial-Temporal Reference Estimation:</b>",
        "To prevent synthetic oracle data leakage, the uncompromised baseline vector $x_v^{\\text{ref}} = [L_{\\text{ref}}, \\gamma_{\\text{ref}}]^T$ is computed online from observable quantities: an adaptive temporal EWMA (weight 0.6) and physical 1-hop spatial neighbor medians (weight 0.4).",
        "<b>8-Dimensional Inductive GraphSAGE Formulation:</b>",
        "$$h_{\\mathcal{N}(v)}^{(1)} = \\frac{1}{|\\mathcal{N}(v)|} \\sum_{u \\in \\mathcal{N}(v)} x_u \\in \\mathbb{R}^4, \\quad h_v^{(1)} = \\text{ReLU}\\Big(W_1 \\cdot \\big[x_v \\parallel h_{\\mathcal{N}(v)}^{(1)}\\big] + b_1\\Big)$$",
        "$$T(v) = \\sigma\\Big(w_2^T h_v^{(1)} + b_2\\Big) \\cdot \\exp\\Big(-\\beta \\|x_v - x_v^{\\text{ref}}\\|_1\\Big)$$",
        "Where $W_1 \\in \\mathbb{R}^{16 \\times 8}, b_1 \\in \\mathbb{R}^{16}$ and $w_2 \\in \\mathbb{R}^{16}, b_2 \\in \\mathbb{R}$. The pure NumPy implementation requires <b>0.091 ms</b> inference, with stealth attacks ($\\delta \\le 0.15$) and adjacent collusion (gNB-09 & 10) held out during training.",
        "<b>Trust-Weighted Continuous Pareto Utility Arbitration:</b>",
        "$$U_{\\text{joint}}(v) = \\lambda \\cdot T(v) \\cdot \\Delta_{\\text{TS}}(v) + (1 - \\lambda) \\cdot T(v)^2 \\cdot \\Delta_{\\text{ES}}(v) + \\Delta_{\\text{QoS}}(v)$$",
        "• <b>Quadratic Trust Penalty ($T(v)^2$):</b> When FDI corrupts telemetry, trust collapses ($T(v) < 0.35 \\implies T^2 < 0.12$). Energy-saving shutdown utility is completely vetoed, eliminating dangerous sleep actions under falsified low loads.",
    ]
    cy = curr_y + card6_h - 75
    for text in c6_content:
        p = Paragraph(text, style_card_body)
        w, h = p.wrap(COL_WIDTH - 40, 200)
        p.drawOn(c, col2_x + 20, cy - h)
        cy -= (h + 12)

    draw_stat_box(c, col2_x + 20, curr_y + 25, (COL_WIDTH - 60)/3, 75, "0.091 ms", "Pure NumPy GNN Latency", C_EMERALD)
    draw_stat_box(c, col2_x + 30 + (COL_WIDTH - 60)/3, curr_y + 25, (COL_WIDTH - 60)/3, 75, "67× Margin", "Under 8.4ms RIC Deadline", C_PRIMARY_BLUE)
    draw_stat_box(c, col2_x + 40 + 2*(COL_WIDTH - 60)/3, curr_y + 25, (COL_WIDTH - 60)/3, 75, "0.1% FAR", "Non-Oracle False Alarm Rate", C_CYAN_ACCENT)

    # =========================================================================
    # COLUMN 3: Empirical Validation, Multi-Baseline & Sovereign Roadmap
    # =========================================================================
    curr_y = CONTENT_TOP

    # --- CARD 3.1: Multi-Baseline Dynamic PDR Evaluation ---
    card7_h = 920
    curr_y -= card7_h
    draw_rounded_card(c, col3_x, curr_y, COL_WIDTH, card7_h, "7. Multi-Baseline Resilience: AICOP vs BFD vs Static", C_PRIMARY_BLUE)

    c7_intro = (
        "<b>Evaluating Beyond Strawman Baselines:</b> Standard cellular/NTN backhauls deploy <b>reactive Bidirectional Forwarding Detection (BFD) hold-timers (RFC 5880 / 3GPP TS 38.300)</b>. We evaluate RAKSHA-NET against both unmanaged static routing and industry-standard reactive BFD under 70% RF jamming:"
    )
    p = Paragraph(c7_intro, style_card_body)
    w, h = p.wrap(COL_WIDTH - 40, 100)
    p.drawOn(c, col3_x + 20, curr_y + card7_h - 75)

    baseline_table_data = [
        [
            Paragraph("<b>Operational Phase</b>", style_table_header),
            Paragraph("<b>RAKSHA-NET<br/>(Proactive AI)</b>", style_table_header),
            Paragraph("<b>Reactive BFD<br/>(3GPP Standard)</b>", style_table_header),
            Paragraph("<b>Static Route<br/>(Unmanaged)</b>", style_table_header),
            Paragraph("<b>AI Net Gain<br/>vs BFD / Static</b>", style_table_header),
        ],
        [
            Paragraph("<b>Phase 1: Normal Pre-Attack</b>", style_table_cell_bold),
            Paragraph("0.972 (2.8% loss)", style_table_cell_center),
            Paragraph("0.972 (2.8% loss)", style_table_cell_center),
            Paragraph("0.972 (2.8% loss)", style_table_cell_center),
            Paragraph("0.0 pp", style_table_cell_center),
        ],
        [
            Paragraph("<b>Phase 2: Transient Outage Window</b>", style_table_cell_bold),
            Paragraph("<b>0.785</b> (21.5% loss)", style_table_cell_center),
            Paragraph("0.340 (66.0% loss)", style_table_cell_center),
            Paragraph("0.311 (68.9% loss)", style_table_cell_center),
            Paragraph("<b>+44.5 / +47.4 pp</b>", style_table_cell_center),
        ],
        [
            Paragraph("<b>Phase 3: Sustained Jamming</b>", style_table_cell_bold),
            Paragraph("<b>0.970</b> (3.0% loss)", style_table_cell_center),
            Paragraph("0.760 (24.0% loss)", style_table_cell_center),
            Paragraph("0.325 (67.5% loss)", style_table_cell_center),
            Paragraph("<b>+21.0 / +64.5 pp</b>", style_table_cell_center),
        ],
        [
            Paragraph("<b>Phase 4: Post-Attack Recovery</b>", style_table_cell_bold),
            Paragraph("0.971 (nominal)", style_table_cell_center),
            Paragraph("0.965 (reconnected)", style_table_cell_center),
            Paragraph("0.872 (slow drain)", style_table_cell_center),
            Paragraph("+0.6 / +9.9 pp", style_table_cell_center),
        ],
        [
            Paragraph("<b>Route Failover Latency</b>", style_table_cell_bold),
            Paragraph("<b>188 ms</b> (simulated)", style_table_cell_center),
            Paragraph("1,500–2,800 ms (timeout)", style_table_cell_center),
            Paragraph("No failover (inf)", style_table_cell_center),
            Paragraph("<b>10× Faster</b>", style_table_cell_center),
        ],
        [
            Paragraph("<b>Route Flapping Oscillations</b>", style_table_cell_bold),
            Paragraph("<b>0.71 ± 0.82 flaps</b>", style_table_cell_center),
            Paragraph("Frequent flaps under jitter", style_table_cell_center),
            Paragraph("0 (stays broken)", style_table_cell_center),
            Paragraph("<b>25.7× Reduction</b>", style_table_cell_center),
        ],
    ]
    t_base = Table(baseline_table_data, colWidths=[170, 135, 135, 120, 120])
    t_base.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    tw, th = t_base.wrap(COL_WIDTH - 40, 350)
    t_base.drawOn(c, col3_x + 20, curr_y + card7_h - 130 - th)

    c7_findings = [
        "<b>Core Takeaway:</b> RAKSHA-NET achieves <b>+21.0 pp higher PDR over industry-standard reactive BFD</b> because predictive EWMA/CUSUM anomaly scoring anticipates link collapse and pre-arms failover in ~188 ms, whereas BFD must wait for hold-timer loss counters to expire.",
        "Across 100 Monte Carlo seeds (<code>batch_100_seeds_experiment.csv</code>), PDR is restored from <b>29.6% to 96.8% (+67.16 pp, 95% CI: [66.19, 68.14] pp, p < 0.0001)</b>.",
    ]
    cy = curr_y + card7_h - 150 - th
    for text in c7_findings:
        p = Paragraph(text, style_card_body)
        w, h = p.wrap(COL_WIDTH - 40, 150)
        p.drawOn(c, col3_x + 20, cy - h)
        cy -= (h + 10)

    # --- CARD 3.2: Detection Ablation & SLA Protection ---
    curr_y -= 25
    card8_h = 830
    curr_y -= card8_h
    draw_rounded_card(c, col3_x, curr_y, COL_WIDTH, card8_h, "8. Detection Ablation & SLA Risk Mitigation", C_CYAN_ACCENT)

    c8_content = [
        "<b>10-Seed Non-Oracle Detection Ablation (7,200 Cell-Epochs):</b>",
        "• <i>Spatial Median Only:</i> F1 12.2%, High FAR (28.5%), Stealth F1 3.0%.",
        "• <i>2-Layer MLP (Isolated Node Features):</i> F1 1.1%, Collusion F1 0.0%.",
        "• <i>Deviation Penalty Only:</i> F1 59.9%, FAR 0.0%, Stealth F1 1.1%.",
        "• <b>Unified AICOP (Proposed):</b> <b>Precision 92.8 ± 6.2%, Recall 63.2 ± 7.3%, F1 74.8 ± 5.3%, FAR 0.1%, Stealth F1 17.0%, Collusion F1 82.8%</b>.",
        "<b>Service Level Agreement (SLA) Protection (EARTH Model):</b>",
        "• <b>Unmanaged Baseline:</b> Naively sleeps capacity cells on spoofed low load → <b>55.40% SLA violations</b>.",
        "• <b>PACIFISTA Baseline:</b> Timer hysteresis expires during sustained FDI → <b>22.15% SLA violations</b>.",
        "• <b>Always-ON Baseline:</b> <b>10.60% SLA violations</b> (purely from stochastic traffic peaks > 0.85).",
        "• <b>Unified AICOP:</b> <b>10.60 ± 1.67% SLA violations</b> (matches Always-ON on attacked cells by vetoing sleep, while saving <b>25.3% off-peak power</b> on honest capacity cells).",
    ]
    cy = curr_y + card8_h - 75
    for text in c8_content:
        p = Paragraph(text, style_card_body)
        w, h = p.wrap(COL_WIDTH - 40, 200)
        p.drawOn(c, col3_x + 20, cy - h)
        cy -= (h + 10)

    # --- CARD 3.3: Sovereign Hardware Roadmap & Artifact Availability ---
    curr_y -= 25
    card9_h = 990
    curr_y -= card9_h
    draw_rounded_card(c, col3_x, curr_y, COL_WIDTH, card9_h, "9. Sovereign Hardware Roadmap & Reproducibility", C_DARK_BG)

    c9_content = [
        "<b>Scientific Integrity & TRL-4 Laboratory Testbed Disclosure:</b>",
        "• Evaluated against an active <b>3GPP Rel-17 Open5GS Core</b> (16 active daemons, user plane over Linux <code>ogstun</code>) and containerized network namespaces (Docker + Linux kernel <code>tc netem</code> for delay, loss, and jitter injection).",
        "• Cryptographic benchmarks are wall-clock hardware-timed via native C <code>liboqs</code>; satellite failover times reflect a simulated discrete-event transition model based on 20 ms BFD micro-sampling.",
        "<b>Portability Roadmap for Indigenous Indian Hardware:</b>",
        "1. <i>COTS Edge Gateways (Months 1–3):</i> Raspberry Pi 5 / NVIDIA Jetson Orin Nano for field search-and-rescue UAV gateways.",
        "2. <i>Sovereign Silicon (Months 3–6):</i> Porting pure-NumPy GraphSAGE and C ML-KEM-768 to <b>Indian Shakti and Vega RISC-V platforms</b>.",
        "3. <i>Physical RF Validation (Months 6–12):</i> Transitioning from <code>tc netem</code> to physical Software-Defined Radios (HackRF One / USRP B210) over GNU Radio.",
        "<b>Artifact Availability & Open Source:</b>",
        "• Complete Python/C controllers, Open5GS profiles, and 100-seed batch logs are publicly available under <b>Apache License 2.0</b>.",
        "• <b>Repository:</b> <u>https://github.com/Rahul109871234/raksha-net</u>",
        "• <b>Automated Test Suite:</b> <b>53 / 53 unit tests passing (100%)</b>.",
    ]
    cy = curr_y + card9_h - 75
    for text in c9_content:
        p = Paragraph(text, style_card_body)
        w, h = p.wrap(COL_WIDTH - 40, 200)
        p.drawOn(c, col3_x + 20, cy - h)
        cy -= (h + 12)

    # QR Code placeholder / GitHub Box
    qr_w = COL_WIDTH - 40
    qr_h = 90
    qr_y = curr_y + 25
    c.setFillColor(colors.HexColor("#1e293b"))
    c.setStrokeColor(C_HEADER_ACCENT)
    c.setLineWidth(1.5)
    c.roundRect(col3_x + 20, qr_y, qr_w, qr_h, 8, fill=1, stroke=1)
    
    p_repo_box = Paragraph(
        "<font size=16 color='#38bdf8'><b>OPEN RESEARCH ARTIFACT & REPRODUCIBILITY CODE</b></font><br/>"
        "<font size=13 color='#ffffff'>Clone & verify the full 53-test suite: <b>git clone https://github.com/Rahul109871234/raksha-net.git</b></font><br/>"
        "<font size=11 color='#94a3b8'>Apache-2.0 License · Document ID: SPACE-2026-POSTER-RAKSHA · PDPM IIITDM Jabalpur</font>",
        ParagraphStyle("RepoBox", fontName="Helvetica", alignment=TA_CENTER, leading=20)
    )
    p_repo_box.wrapOn(c, qr_w - 20, qr_h - 10)
    p_repo_box.drawOn(c, col3_x + 30, qr_y + 12)

    # -------------------------------------------------------------------------
    # Save Canvas and Finalize Document
    # -------------------------------------------------------------------------
    c.showPage()
    c.save()
    print(f"[OK] Single-Page A0 Poster successfully generated -> {OUTPUT_PDF}")
    print(f"     Page dimensions: {PAGE_WIDTH:.2f} pt x {PAGE_HEIGHT:.2f} pt ({PAGE_WIDTH/72*25.4:.1f} mm x {PAGE_HEIGHT/72*25.4:.1f} mm)")


if __name__ == "__main__":
    build_poster()
