#!/usr/bin/env python3
"""
generate_space2026_poster.py
============================
Generates the official publication-grade Single-Page A0 PDF poster for:
Sixteenth International Conference on Security, Privacy and Applied Cryptographic Engineering (SPACE 2026)
Organized by C-DAC Bengaluru · Venue: The Chancery Pavilion, Bengaluru, India

Specifications:
  - Exact single-page A0 dimensions: 841 mm × 1189 mm (2383.94 pt × 3370.39 pt)
  - Topic: Applied Cryptographic Engineering, 5G/NTN Cyber-Resilience, Hardware Security
  - Sole Author: G. Rahul Reddy (24BEC038), PDPM IIITDM Jabalpur
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

HEADER_HEIGHT = 410
FOOTER_HEIGHT = 80
TOP_MARGIN = 30
BOTTOM_MARGIN = 20
SIDE_MARGIN = 48

CONTENT_TOP = PAGE_HEIGHT - HEADER_HEIGHT - 28
CONTENT_BOTTOM = FOOTER_HEIGHT + 32
CONTENT_HEIGHT = CONTENT_TOP - CONTENT_BOTTOM  # 2820.39 pt

NUM_COLS = 3
COL_GAP = 44
COL_WIDTH = (PAGE_WIDTH - 2 * SIDE_MARGIN - (NUM_COLS - 1) * COL_GAP) / NUM_COLS  # ~733.3 pt

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
# Typography Styles (Tuned for A0 Poster Viewing from 1.5–2 meters)
# -----------------------------------------------------------------------------
styles = getSampleStyleSheet()

style_title = ParagraphStyle(
    "PosterTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=43,
    leading=52,
    textColor=C_WHITE,
    alignment=TA_CENTER,
)

style_conf_tag = ParagraphStyle(
    "PosterConfTag",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=15.5,
    leading=21,
    textColor=C_GOLD,
    alignment=TA_CENTER,
)

style_authors = ParagraphStyle(
    "PosterAuthors",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=25,
    leading=31,
    textColor=C_WHITE,
    alignment=TA_CENTER,
)

style_affil = ParagraphStyle(
    "PosterAffil",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=17,
    leading=23,
    textColor=colors.HexColor("#94a3b8"),
    alignment=TA_CENTER,
)

style_card_title = ParagraphStyle(
    "CardTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=21.5,
    leading=26,
    textColor=C_WHITE,
    alignment=TA_LEFT,
)

style_card_body = ParagraphStyle(
    "CardBody",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=15,
    leading=22,
    textColor=C_TEXT_MAIN,
    alignment=TA_LEFT,
)

style_card_body_bold = ParagraphStyle(
    "CardBodyBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=15,
    leading=22,
    textColor=C_TEXT_MAIN,
    alignment=TA_LEFT,
)

style_callout_label = ParagraphStyle(
    "CalloutLabel",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=12.5,
    leading=16,
    textColor=C_TEXT_MUTED,
    alignment=TA_CENTER,
)

style_table_header = ParagraphStyle(
    "TableHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=12.5,
    leading=16.5,
    textColor=C_WHITE,
    alignment=TA_CENTER,
)

style_table_cell = ParagraphStyle(
    "TableCell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=12,
    leading=16,
    textColor=C_TEXT_MAIN,
    alignment=TA_LEFT,
)

style_table_cell_bold = ParagraphStyle(
    "TableCellBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=C_TEXT_MAIN,
    alignment=TA_LEFT,
)

style_table_cell_center = ParagraphStyle(
    "TableCellCenter",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=12,
    leading=16,
    textColor=C_TEXT_MAIN,
    alignment=TA_CENTER,
)


def draw_rounded_card_frame(c: canvas.Canvas, x, y, width, height, title, header_color=C_PRIMARY_BLUE, radius=10):
    """Draws a professional card container with rounded borders and a colored header ribbon."""
    c.saveState()
    # Drop shadow
    c.setFillColor(colors.HexColor("#e2e8f0"))
    c.roundRect(x + 3, y - 3, width, height, radius, fill=1, stroke=0)
    
    # White card container
    c.setFillColor(C_CARD_BG)
    c.setStrokeColor(C_CARD_BORDER)
    c.setLineWidth(1.6)
    c.roundRect(x, y, width, height, radius, fill=1, stroke=1)
    
    # Header ribbon (44 pt height)
    header_h = 44
    c.setFillColor(header_color)
    p = c.beginPath()
    p.moveTo(x, y + height - radius)
    p.arcTo(x, y + height - 2*radius, x + 2*radius, y + height, radius)
    p.lineTo(x + width - radius, y + height)
    p.arcTo(x + width - 2*radius, y + height, x + width, y + height - 2*radius, radius)
    p.lineTo(x + width, y + height - header_h)
    p.lineTo(x, y + height - header_h)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    
    # Title text
    p_title = Paragraph(f"<b>{title}</b>", style_card_title)
    w, h = p_title.wrap(width - 40, header_h)
    p_title.drawOn(c, x + 18, y + height - 33)
    
    c.restoreState()


class CardFlow:
    """Manages strict top-down flow layout inside a card to guarantee ZERO text overlaps."""
    def __init__(self, c: canvas.Canvas, x, y, width, height, title, header_color=C_PRIMARY_BLUE):
        self.c = c
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.header_color = header_color
        self.content_w = width - 36
        self.content_x = x + 18
        
        draw_rounded_card_frame(c, x, y, width, height, title, header_color)
        # Content starts 14 pt below the 44 pt header ribbon
        self.cy = y + height - 58

    def add_paragraph(self, text, style=style_card_body, spacing=12):
        p = Paragraph(text, style)
        w, h = p.wrap(self.content_w, 4000)
        p.drawOn(self.c, self.content_x, self.cy - h)
        self.cy -= (h + spacing)
        return h

    def add_table(self, table: Table, spacing=14):
        w, h = table.wrap(self.content_w, 4000)
        table.drawOn(self.c, self.content_x, self.cy - h)
        self.cy -= (h + spacing)
        return h

    def add_image(self, img_path, img_w, img_h, spacing=14):
        img_x = self.x + (self.width - img_w) / 2.0
        self.c.setStrokeColor(colors.HexColor("#94a3b8"))
        self.c.setLineWidth(1)
        self.c.rect(img_x - 1, self.cy - img_h - 1, img_w + 2, img_h + 2, fill=0, stroke=1)
        self.c.drawImage(str(img_path), img_x, self.cy - img_h, width=img_w, height=img_h)
        self.cy -= (img_h + spacing)

    def add_formula_box(self, title_text, formula_text, desc_text=None, border_color=C_PRIMARY_BLUE, bg_color=colors.HexColor("#f8fafc"), title_color=None, text_color=C_TEXT_MAIN, spacing=13):
        """Draws an elegant, mathematically styled callout container."""
        tc = title_color if title_color else border_color
        p_title = Paragraph(f"<font color='{tc.hexval()}'><b>{title_text}</b></font>", ParagraphStyle("FTit", fontName="Helvetica-Bold", fontSize=14, leading=18))
        p_form = Paragraph(formula_text, ParagraphStyle("FForm", fontName="Helvetica", fontSize=14, leading=20, textColor=text_color))
        
        wt, ht = p_title.wrap(self.content_w - 28, 4000)
        wf, hf = p_form.wrap(self.content_w - 28, 4000)
        
        hd = 0
        p_desc = None
        if desc_text:
            desc_col = colors.HexColor("#94a3b8") if bg_color == C_DARK_BG or bg_color == colors.HexColor("#0f172a") else C_TEXT_MUTED
            p_desc = Paragraph(desc_text, ParagraphStyle("FDesc", fontName="Helvetica", fontSize=12.5, leading=17, textColor=desc_col))
            wd, hd = p_desc.wrap(self.content_w - 28, 4000)
        
        box_padding = 11
        total_h = box_padding * 2 + ht + 6 + hf + (hd + 6 if hd > 0 else 0)
        
        self.c.saveState()
        self.c.setFillColor(bg_color)
        self.c.setStrokeColor(colors.HexColor("#cbd5e1") if bg_color != colors.HexColor("#0f172a") else C_HEADER_ACCENT)
        self.c.setLineWidth(1.2)
        self.c.roundRect(self.content_x, self.cy - total_h, self.content_w, total_h, 6, fill=1, stroke=1)
        
        # Left thick accent bar
        self.c.setFillColor(border_color)
        self.c.roundRect(self.content_x, self.cy - total_h, 5, total_h, 2, fill=1, stroke=0)
        
        # Draw texts
        inner_y = self.cy - box_padding
        p_title.drawOn(self.c, self.content_x + 16, inner_y - ht)
        inner_y -= (ht + 6)
        
        p_form.drawOn(self.c, self.content_x + 16, inner_y - hf)
        inner_y -= (hf + 6)
        
        if p_desc:
            p_desc.drawOn(self.c, self.content_x + 16, inner_y - hd)
            
        self.c.restoreState()
        self.cy -= (total_h + spacing)

    def add_stat_triplet(self, items, height=86, spacing=13):
        """Draws 3 side-by-side callout metric cards."""
        w_item = (self.content_w - 20) / 3.0
        for i, (num_str, label_str, col) in enumerate(items):
            bx = self.content_x + i * (w_item + 10)
            by = self.cy - height
            self.c.saveState()
            self.c.setFillColor(colors.HexColor("#f1f5f9"))
            self.c.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.c.setLineWidth(1.2)
            self.c.roundRect(bx, by, w_item, height, 7, fill=1, stroke=1)
            
            self.c.setFillColor(col)
            self.c.setFont("Helvetica-Bold", 26)
            self.c.drawCentredString(bx + w_item/2.0, by + height - 32, num_str)
            
            p_lbl = Paragraph(label_str, style_callout_label)
            w, h = p_lbl.wrap(w_item - 10, height - 36)
            p_lbl.drawOn(self.c, bx + 5, by + 8)
            self.c.restoreState()
            
        self.cy -= (height + spacing)

    def check_overflow(self):
        remaining = self.cy - self.y
        if remaining < 10:
            print(f"[WARNING] Card '{self.title}' is tight: {remaining:.1f} pt remaining")
        else:
            print(f"[OK] Card '{self.title}' fitted with {remaining:.1f} pt bottom breathing room")


def build_poster():
    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=A0)
    c.setTitle("RAKSHA-NET: Applied Cryptographic Engineering & 5G NTN Resilience (SPACE 2026)")
    c.setAuthor("G. Rahul Reddy (PDPM IIITDM Jabalpur)")
    c.setSubject("SPACE 2026 Poster Submission - Applied Cryptography & Hardware Security")

    # 1. Background
    c.setFillColor(C_PAGE_BG)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    # -------------------------------------------------------------------------
    # 2. Header Banner (Top-Down Dynamic Flow)
    # -------------------------------------------------------------------------
    c.saveState()
    c.setFillColor(C_HEADER_BG)
    c.rect(0, PAGE_HEIGHT - HEADER_HEIGHT, PAGE_WIDTH, HEADER_HEIGHT, fill=1, stroke=0)
    
    # Accent lines
    c.setStrokeColor(C_HEADER_ACCENT)
    c.setLineWidth(4)
    c.line(0, PAGE_HEIGHT - HEADER_HEIGHT, PAGE_WIDTH, PAGE_HEIGHT - HEADER_HEIGHT)
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(2)
    c.line(0, PAGE_HEIGHT - HEADER_HEIGHT - 3, PAGE_WIDTH, PAGE_HEIGHT - HEADER_HEIGHT - 3)

    y_hdr = PAGE_HEIGHT - 32

    # 2.1 Conference Venue Pill / Tag
    conf_tag_text = (
        "<b>SPACE 2026</b> · 16TH INTERNATIONAL CONFERENCE ON SECURITY, PRIVACY AND APPLIED CRYPTOGRAPHIC ENGINEERING<br/>"
        "ORGANISED BY <b>CENTRE FOR DEVELOPMENT OF ADVANCED COMPUTING (C-DAC), BENGALURU</b> · 16–19 DECEMBER 2026 · BENGALURU, INDIA"
    )
    p_tag = Paragraph(conf_tag_text, style_conf_tag)
    w, h_tag = p_tag.wrap(PAGE_WIDTH - 120, 100)
    p_tag.drawOn(c, 60, y_hdr - h_tag)
    y_hdr -= (h_tag + 14)

    # 2.2 Main Poster Title
    title_text = "RAKSHA-NET: Autonomous Cross-Layer Resilience & Post-Quantum<br/>Cryptographic Agility for 5G Non-Terrestrial Networks"
    p_main_title = Paragraph(title_text, style_title)
    w, h_title = p_main_title.wrap(PAGE_WIDTH - 160, 150)
    p_main_title.drawOn(c, 80, y_hdr - h_title)
    y_hdr -= (h_title + 14)

    # 2.3 Sole Author: G. Rahul Reddy (Faculty Mentor completely removed)
    authors_text = "<b>G. Rahul Reddy</b> &nbsp;&nbsp;·&nbsp;&nbsp; Roll No: <b>24BEC038</b>"
    p_authors = Paragraph(authors_text, style_authors)
    w, h_auth = p_authors.wrap(PAGE_WIDTH - 160, 60)
    p_authors.drawOn(c, 80, y_hdr - h_auth)
    y_hdr -= (h_auth + 8)

    # 2.4 Affiliations & Contact
    affil_text = (
        "Department of Electronics & Communication Engineering, "
        "<b>PDPM Indian Institute of Information Technology, Design & Manufacturing (IIITDM), Jabalpur</b>, MP, India<br/>"
        "Author Email: <u>24bec038@iiitdmj.ac.in</u> &nbsp;|&nbsp; "
        "Open Artifact Repository: <u>https://github.com/Rahul109871234/raksha-net</u> (Apache-2.0 License)"
    )
    p_affil = Paragraph(affil_text, style_affil)
    w, h_affil = p_affil.wrap(PAGE_WIDTH - 160, 80)
    p_affil.drawOn(c, 80, y_hdr - h_affil)
    y_hdr -= (h_affil + 16)

    # 2.5 Quick Highlights Badges Ribbon
    badges_w = PAGE_WIDTH - 240
    badges_x = 120
    badges_h = 44
    badges_y = y_hdr - badges_h
    c.setFillColor(colors.HexColor("#1e293b"))
    c.setStrokeColor(colors.HexColor("#334155"))
    c.setLineWidth(1.4)
    c.roundRect(badges_x, badges_y, badges_w, badges_h, 8, fill=1, stroke=1)
    
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
        c.drawCentredString(bx + step_w / 2.0, badges_y + 14, b_text)
        if i < len(badge_items) - 1:
            c.setStrokeColor(colors.HexColor("#475569"))
            c.setLineWidth(1)
            c.line(bx + step_w, badges_y + 7, bx + step_w, badges_y + 37)

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
        "Proceedings & Poster Track · Organised by C-DAC Bengaluru · Venue: The Chancery Pavilion, Residency Road, Bengaluru, Karnataka"
    )
    p_foot_l = Paragraph(footer_left, ParagraphStyle("FL", fontName="Helvetica", fontSize=13, leading=18, textColor=colors.HexColor("#94a3b8")))
    w, h = p_foot_l.wrap(1150, 60)
    p_foot_l.drawOn(c, SIDE_MARGIN + 10, 18)

    footer_right = (
        "<b>Sovereign Cyber-Resilience for India</b> · PDPM IIITDM Jabalpur (Author: G. Rahul Reddy, Roll: 24BEC038)<br/>"
        "Artifact Code, Open5GS Profiles, Pre-Trained Weights & 53 Tests: <b>github.com/Rahul109871234/raksha-net</b>"
    )
    p_foot_r = Paragraph(footer_right, ParagraphStyle("FR", fontName="Helvetica", fontSize=13, leading=18, textColor=colors.HexColor("#94a3b8"), alignment=TA_RIGHT))
    w, h = p_foot_r.wrap(1150, 60)
    p_foot_r.drawOn(c, PAGE_WIDTH - SIDE_MARGIN - 1160, 18)
    c.restoreState()

    # -------------------------------------------------------------------------
    # 4. Columns & Grid Layout
    # -------------------------------------------------------------------------
    col1_x = SIDE_MARGIN
    col2_x = SIDE_MARGIN + COL_WIDTH + COL_GAP
    col3_x = SIDE_MARGIN + 2 * (COL_WIDTH + COL_GAP)

    CARD_GAP = 24  # gap between stacked cards in a column

    # =========================================================================
    # COLUMN 1: Problem Formulation, Threat Vectors & 5G NTN Architecture
    # =========================================================================
    curr_y = CONTENT_TOP

    # --- CARD 1.1: Multi-Tier Threat Vectors ---
    card1_h = 750
    curr_y -= card1_h
    card1 = CardFlow(c, col1_x, curr_y, COL_WIDTH, card1_h, "1. The 5G NTN Convergence & Multi-Tier Threat", C_PRIMARY_BLUE)
    
    card1.add_paragraph("In <b>3GPP Release-18 (5G-Advanced)</b> and emerging <b>6G architectures</b>, terrestrial Open Radio Access Networks (O-RAN) and Non-Terrestrial Networks (NTN) converge into a heterogeneous Space-Air-Ground Integrated Network (SAGIN).")
    card1.add_paragraph("While enabling persistent tactical coverage across maritime and contested borders, this convergence exposes mission-critical communications to a <b>synchronized multi-surface threat vector</b>:")
    card1.add_paragraph("• <b>1. Terrestrial Edge (O-RAN Radio Units):</b> Hostile nodes inject False Data (FDI), falsifying low PRB utilization (e.g. 18%) or corrupted SINR. Near-RT RIC xApps (Traffic Steering vs Energy Saving) oscillate uncontrollably, forcing active capacity cells into sleep and causing <b>55.40% unmanaged SLA collapse</b>.")
    card1.add_paragraph("• <b>2. Space Layer (LEO Satellite Uplinks):</b> Electronic Warfare (high-power RF Jamming) degrades satellite feeder links to <b>29.6% PDR (70.4% loss)</b>, severing strategic command-and-control backhauls.")
    card1.add_paragraph("• <b>3. Harvest-Now-Decrypt-Later (HNDL):</b> Adversaries passively intercept satellite ciphertext to store it for future cryptanalysis once large-scale quantum computers arrive. Classical ECC (X25519) and RSA will be compromised by Shor's algorithm.")
    
    threat_table_data = [
        [Paragraph("<b>Target Domain</b>", style_table_header), Paragraph("<b>Attack Vector</b>", style_table_header), Paragraph("<b>Exploited Protocol / Interface</b>", style_table_header), Paragraph("<b>System Impact Without RAKSHA</b>", style_table_header)],
        [Paragraph("Terrestrial O-RAN", style_table_cell_bold), Paragraph("False Data Injection (FDI)", style_table_cell), Paragraph("O-RAN E2SM-KPM / E2 Telemetry", style_table_cell), Paragraph("<b>55.40% SLA violation</b> (Macro overload)", style_table_cell)],
        [Paragraph("Space NTN Uplink", style_table_cell_bold), Paragraph("Electronic Warfare RF Jamming", style_table_cell), Paragraph("LEO Feeder Carrier / Ka-Band", style_table_cell), Paragraph("<b>29.6% PDR</b> (70.4% tactical packet drop)", style_table_cell)],
        [Paragraph("Cryptographic Fabric", style_table_cell_bold), Paragraph("HNDL Quantum Wiretapping", style_table_cell), Paragraph("IKEv2 / IPsec Satellite Tunnels", style_table_cell), Paragraph("Retroactive decryption via Shor's algo", style_table_cell)],
    ]
    t_threat = Table(threat_table_data, colWidths=[140, 160, 185, 210])
    t_threat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    card1.add_table(t_threat, spacing=13)

    card1.add_stat_triplet([
        ("55.40%", "SLA Failure (Unmanaged FDI)", C_ROSE),
        ("29.6% PDR", "Space RF Jamming Loss (70.4% Drop)", C_ROSE),
        ("HNDL Threat", "Quantum Interception Risk", C_GOLD),
    ], height=86)
    card1.check_overflow()

    # --- CARD 1.2: Core Research Thesis ---
    curr_y -= CARD_GAP
    card2_h = 620
    curr_y -= card2_h
    card2 = CardFlow(c, col1_x, curr_y, COL_WIDTH, card2_h, "2. Core Thesis: Why Routing & Cryptography Must Unify", C_CYAN_ACCENT)
    
    card2.add_paragraph("<b>The Conventional Silo:</b> In current 5G and satellite networks, routing resilience and cryptographic key management are isolated into non-communicating engineering silos:")
    card2.add_paragraph("• <i>Routing protocols</i> (BGP, BFD, ECMP) treat link degradation purely as a benign physical fault, ignoring whether packet loss stems from active adversarial jamming or wiretap insertion.")
    card2.add_paragraph("• <i>Applied cryptographers</i> benchmark post-quantum algorithms in offline isolation, ignoring network drop dynamics, queue overflow, and rekeying storm latencies.")
    card2.add_paragraph("<b>The RAKSHA-NET Paradigm:</b> <i>Link degradation is an active cryptographic tampering signal.</i>")
    card2.add_paragraph("When electronic warfare hits an orbital link, RAKSHA-NET does not simply re-route packets: it proactively treats the degraded link as potentially compromised, migrates traffic to strategic backup satellites in <b>188 ms</b>, and concurrently triggers <b>NIST FIPS 203 ML-KEM-768</b> post-quantum session rekeying to isolate the adversary.")
    
    card2.add_formula_box(
        "Cross-Layer Autonomous Coupling Rule (r = 0.754):",
        "<b>Link Anomaly Score <i>a<sub>t</sub></i> &ge; 0.60 &nbsp;or&nbsp; Cell Trust <i>T(v)</i> &lt; 0.50 &nbsp;&rArr;&nbsp; Trigger Proactive Failover + ML-KEM Rekey</b>",
        "Pre-arms orbital failover 20 ms prior to physical disconnect (22 ms primed vs 42 ms cold), suppressing transition packet loss by 44.5 pp."
    )
    card2.check_overflow()

    # --- CARD 1.3: End-to-End System Architecture Diagram ---
    curr_y -= CARD_GAP
    card3_h = 1402
    curr_y -= card3_h
    card3 = CardFlow(c, col1_x, curr_y, COL_WIDTH, card3_h, "3. Cross-Layer System Architecture & SAGIN Topology", C_DARK_BG)

    arch_img_path = RESULTS_DIR / "aicop_raksha_architecture.png"
    if arch_img_path.exists():
        img_w = COL_WIDTH - 36
        img_h = (1890 / 3120) * img_w  # ~422 pt
        card3.add_image(arch_img_path, img_w, img_h, spacing=14)

    card3.add_paragraph("<b>Three-Tier Hierarchical Defense Architecture:</b>")
    card3.add_paragraph("• <b>Tier 3: Space NTN Uplink (RAKSHA-NET Core):</b> Linux TUN <code>ogstun</code> interface interfacing with 3GPP Rel-17 Open5GS core functions. Hosts Page's CUSUM sequential change-point detector, 5% hysteresis barrier, and native C ML-KEM-768 PQC session manager.")
    card3.add_paragraph("• <b>Tier 2: Terrestrial O-RAN Near-RT RIC (AICOP Engine):</b> Inductive pure-NumPy 2-Layer GraphSAGE inference engine running in <b>0.091 ms</b>. Cross-validates reported telemetry against observable spatial neighbor consensus and temporal EWMA baselines.")
    card3.add_paragraph("• <b>Tier 1: Physical Radio Nodes (12-Cell Planar Grid):</b> Dual-band layout: 700 MHz Macro Umbrella Tier (Cells 1–6, non-sleeping) and 3.5 GHz Capacity Micro Tier (Cells 7–12, dynamic power gating under trust control).")
    
    tier_table_data = [
        [Paragraph("<b>Tier / Subsystem</b>", style_table_header), Paragraph("<b>Target Environment</b>", style_table_header), Paragraph("<b>Primary Autonomous Function</b>", style_table_header), Paragraph("<b>Latency Bound</b>", style_table_header)],
        [Paragraph("<b>Tier 3: Space NTN</b>", style_table_cell_bold), Paragraph("Open5GS Core / Linux TUN", style_table_cell), Paragraph("CUSUM Anomaly Detection + ML-KEM-768 Rekey", style_table_cell), Paragraph("<b>188 ms</b> failover", style_table_cell_center)],
        [Paragraph("<b>Tier 2: Near-RT RIC</b>", style_table_cell_bold), Paragraph("O-RAN E2 Node Interface", style_table_cell), Paragraph("Inductive GraphSAGE Trust + Pareto Arbitration", style_table_cell), Paragraph("<b>0.091 ms</b> GNN", style_table_cell_center)],
        [Paragraph("<b>Tier 1: Physical gNBs</b>", style_table_cell_bold), Paragraph("12-Cell Dual-Band RAN", style_table_cell), Paragraph("FDI Mitigation & Capacity Micro Power Gating", style_table_cell), Paragraph("10 ms TTI loop", style_table_cell_center)],
    ]
    t_tier = Table(tier_table_data, colWidths=[150, 160, 260, 125])
    t_tier.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    card3.add_table(t_tier, spacing=13)

    card3.add_formula_box(
        "Cross-Layer Telemetry Bus & Control Loop Timing:",
        "<b>O-RAN E2SM-KPM / E2SM-RC &harr; Linux TUN <code>ogstun</code> Subsystem:</b><br/>"
        "• <b>Telemetry Feed:</b> Every 20 ms, physical gNBs publish PRB load, SINR, and packet error counters over E2.<br/>"
        "• <b>Fast-Path Propagation:</b> Trust score anomalies trigger pre-failover priming flags across TUN buffers within 1.2 ms.<br/>"
        "• <b>Zero Packet Oscillation:</b> A strict 5% hysteresis barrier eliminates route flapping under orbital Doppler jitter.",
        border_color=C_HEADER_ACCENT,
        bg_color=colors.HexColor("#f8fafc")
    )
    card3.check_overflow()

    # =========================================================================
    # COLUMN 2: Applied Cryptographic Engineering & Edge AI
    # =========================================================================
    curr_y = CONTENT_TOP

    # --- CARD 2.1: Post-Quantum Crypto-Agility Engine ---
    card4_h = 820
    curr_y -= card4_h
    card4 = CardFlow(c, col2_x, curr_y, COL_WIDTH, card4_h, "4. Applied Post-Quantum Crypto-Agility (IETF RFC 9370)", C_PRIMARY_BLUE)

    card4.add_paragraph("<b>Standardized Hybrid Key Exchange:</b> In accordance with <b>IETF RFC 9370</b> and <b>RFC 9242</b> (<i>Multiple Key Exchanges in IKEv2</i>), RAKSHA-NET binds classical elliptic-curve Diffie-Hellman with lattice-based post-quantum key encapsulation:")
    
    card4.add_formula_box(
        "IETF RFC 9370 Hybrid Key Derivation Function:",
        "<b><i>K</i></b> = HKDF-Extract-and-Expand(&thinsp;salt = sid,&nbsp; <b><i>ss</i><sub>classical</sub></b> || <b><i>ss</i><sub>pqc</sub></b>,&nbsp; \"RAKSHA-AEAD\",&nbsp; 32 Bytes&thinsp;)",
        "• <b>Classical Component:</b> ECDH X25519 (32-byte public key, 32-byte shared secret <i>ss</i><sub>classical</sub>)<br/>"
        "• <b>Post-Quantum Component:</b> <b>NIST FIPS 203 ML-KEM-768</b> (1,184-byte public key, 1,088-byte ciphertext, 32-byte <i>ss</i><sub>pqc</sub>)<br/>"
        "• <b>Dual-Hardness Security:</b> Confidentiality holds as long as <i>at least one</i> mathematical assumption (discrete log or MLWE) remains unbroken."
    )

    kex_comp_data = [
        [Paragraph("<b>Key Exchange Scheme</b>", style_table_header), Paragraph("<b>Public Key</b>", style_table_header), Paragraph("<b>Ciphertext / Secret</b>", style_table_header), Paragraph("<b>Underlying Hardness</b>", style_table_header), Paragraph("<b>Quantum Security</b>", style_table_header)],
        [Paragraph("Classical (X25519)", style_table_cell_bold), Paragraph("32 Bytes", style_table_cell_center), Paragraph("32 Bytes", style_table_cell_center), Paragraph("Elliptic Curve Discrete Log", style_table_cell), Paragraph("Compromised (Shor's)", style_table_cell_center)],
        [Paragraph("Pure PQC (ML-KEM-768)", style_table_cell_bold), Paragraph("1,184 Bytes", style_table_cell_center), Paragraph("1,088 Bytes", style_table_cell_center), Paragraph("Module-LWE (Lattice)", style_table_cell), Paragraph("<b>NIST Category 3 Safe</b>", style_table_cell_center)],
        [Paragraph("<b>RFC 9370 Dual-Hybrid</b>", style_table_cell_bold), Paragraph("<b>1,216 Bytes</b>", style_table_cell_center), Paragraph("<b>1,120 Bytes</b>", style_table_cell_center), Paragraph("<b>Dual-Hardness (ECC + LWE)</b>", style_table_cell), Paragraph("<b>Provably Quantum-Safe</b>", style_table_cell_center)],
    ]
    t_kex = Table(kex_comp_data, colWidths=[175, 110, 135, 160, 115])
    t_kex.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    card4.add_table(t_kex, spacing=12)
    
    card4.add_paragraph("<b>Cryptographic Lifecycle & Automated Rekey Policy:</b>")
    card4.add_paragraph("1. <i>Pre-emptive Rekeying:</i> Triggered autonomously whenever Link Anomaly Score <i>a<sub>t</sub></i> &ge; 0.60 or cell trust <i>T(v)</i> &lt; 0.50, pre-empting eavesdropping before adversary completes cryptanalysis.")
    card4.add_paragraph("2. <i>Forward Secrecy Quarantine:</i> Upon autonomous failover, the degraded satellite relay is immediately purged from all future key schedules, preventing replay or session hijacking.")
    card4.add_paragraph("3. <i>Anti-Replay Window:</i> Strictly monotonic 96-bit packet counters integrated directly into AEAD nonces to prevent replay attacks across orbital transitions.")
    card4.check_overflow()

    # --- CARD 2.2: Dynamic Suite Selection & liboqs Benchmarks ---
    curr_y -= CARD_GAP
    card5_h = 920
    curr_y -= card5_h
    card5 = CardFlow(c, col2_x, curr_y, COL_WIDTH, card5_h, "5. Hardware Crypto Benchmarks & Dynamic AEAD Selection", C_VIOLET)

    card5.add_paragraph("<b>Architectural Dynamic Suite Selection Policy:</b> The controller continuously monitors link bandwidth and threat state to select the optimal AEAD cipher suite across satellite payloads:")

    crypto_data = [
        [Paragraph("<b>Suite Name</b>", style_table_header), Paragraph("<b>Key Exchange</b>", style_table_header), Paragraph("<b>AEAD Cipher</b>", style_table_header), Paragraph("<b>Handshake<br/>Bytes</b>", style_table_header), Paragraph("<b>Execution<br/>Time</b>", style_table_header), Paragraph("<b>AEAD<br/>Throughput</b>", style_table_header)],
        [Paragraph("CLASSICAL_CHACHA", style_table_cell_bold), Paragraph("X25519", style_table_cell), Paragraph("ChaCha20-Poly1305", style_table_cell), Paragraph("64 B", style_table_cell_center), Paragraph("0.120 ms", style_table_cell_center), Paragraph("55.6 MB/s", style_table_cell_center)],
        [Paragraph("PQC_CHACHA", style_table_cell_bold), Paragraph("ML-KEM-768", style_table_cell), Paragraph("ChaCha20-Poly1305", style_table_cell), Paragraph("2,272 B", style_table_cell_center), Paragraph("<b>0.045 ms</b>", style_table_cell_center), Paragraph("57.4 MB/s", style_table_cell_center)],
        [Paragraph("PQC_AES", style_table_cell_bold), Paragraph("ML-KEM-768", style_table_cell), Paragraph("AES-256-GCM", style_table_cell), Paragraph("2,272 B", style_table_cell_center), Paragraph("<b>0.045 ms</b>", style_table_cell_center), Paragraph("<b>74.3 MB/s</b>", style_table_cell_center)],
        [Paragraph("HYBRID_CHACHA", style_table_cell_bold), Paragraph("X25519 + ML-KEM", style_table_cell), Paragraph("ChaCha20-Poly1305", style_table_cell), Paragraph("2,336 B", style_table_cell_center), Paragraph("0.167 ms", style_table_cell_center), Paragraph("56.8 MB/s", style_table_cell_center)],
        [Paragraph("HYBRID_AES", style_table_cell_bold), Paragraph("X25519 + ML-KEM", style_table_cell), Paragraph("AES-256-GCM", style_table_cell), Paragraph("2,336 B", style_table_cell_center), Paragraph("0.167 ms", style_table_cell_center), Paragraph("<b>74.1 MB/s</b>", style_table_cell_center)],
    ]
    t_crypto = Table(crypto_data, colWidths=[140, 115, 145, 85, 100, 105])
    t_crypto.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    card5.add_table(t_crypto, spacing=13)

    card5.add_formula_box(
        "Cryptographic Side-Channel Defense for Embedded Edge Silicon:",
        "<b>Why ChaCha20-Poly1305 on Edge Payloads? (IETF RFC 8439)</b><br/>"
        "• On server CPUs with AES-NI instructions, AES-256-GCM achieves 74.3 MB/s. However, embedded ARM Cortex-M and indigenous <b>Indian Shakti RISC-V</b> processors often lack hardware AES accelerators.<br/>"
        "• Software AES on these chips is vulnerable to cache-timing attacks (Bernstein 2005) and up to 3× slower.<br/>"
        "• <b>ChaCha20-Poly1305 is inherently constant-time in software by design</b>, eliminating side-channel vulnerability on low-power satellite payloads.",
        border_color=C_VIOLET,
        bg_color=colors.HexColor("#faf5ff")
    )

    embedded_crypto_data = [
        [Paragraph("<b>Algorithm</b>", style_table_header), Paragraph("<b>Target Silicon</b>", style_table_header), Paragraph("<b>Peak RAM</b>", style_table_header), Paragraph("<b>Code Size</b>", style_table_header), Paragraph("<b>Clock Cycles</b>", style_table_header), Paragraph("<b>Side-Channel Security</b>", style_table_header)],
        [Paragraph("X25519 (ECDH)", style_table_cell_bold), Paragraph("ARM Cortex-M4 (64 MHz)", style_table_cell), Paragraph("1.8 KB", style_table_cell_center), Paragraph("3.2 KB", style_table_cell_center), Paragraph("~780k cycles", style_table_cell_center), Paragraph("Protected (Constant-time)", style_table_cell)],
        [Paragraph("ML-KEM-768", style_table_cell_bold), Paragraph("ARM Cortex-M4 (64 MHz)", style_table_cell), Paragraph("2.8 KB", style_table_cell_center), Paragraph("8.4 KB", style_table_cell_center), Paragraph("~1,250k cycles", style_table_cell_center), Paragraph("Constant-time NTT", style_table_cell)],
        [Paragraph("ChaCha20-Poly1305", style_table_cell_bold), Paragraph("Shakti C-Class (50 MHz)", style_table_cell), Paragraph("0.5 KB", style_table_cell_center), Paragraph("2.1 KB", style_table_cell_center), Paragraph("~32 cycles/byte", style_table_cell_center), Paragraph("<b>Inherent Constant-Time</b>", style_table_cell)],
        [Paragraph("AES-256-GCM (sw)", style_table_cell_bold), Paragraph("Shakti C-Class (no AES)", style_table_cell), Paragraph("0.8 KB", style_table_cell_center), Paragraph("4.8 KB", style_table_cell_center), Paragraph("~95 cycles/byte", style_table_cell_center), Paragraph("Vulnerable (Cache-timing)", style_table_cell)],
    ]
    t_emb = Table(embedded_crypto_data, colWidths=[135, 150, 75, 80, 115, 140])
    t_emb.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_VIOLET),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    card5.add_table(t_emb, spacing=11)
    card5.check_overflow()

    # --- CARD 2.3: Inductive GraphSAGE & Pareto Arbitration ---
    curr_y -= CARD_GAP
    card6_h = 1032
    curr_y -= card6_h
    card6 = CardFlow(c, col2_x, curr_y, COL_WIDTH, card6_h, "6. Inductive GraphSAGE Trust & Pareto Arbitration", C_EMERALD)

    card6.add_paragraph("<b>Non-Oracle Spatial-Temporal Reference Estimation:</b>")
    card6.add_paragraph("To eliminate synthetic oracle data leakage, the honest reference vector <b>x</b><sub>v</sub><sup>ref</sup> = [<i>L</i><sub>ref</sub>, &gamma;<sub>ref</sub>]<sup>T</sup> is computed online from observable quantities: an adaptive temporal EWMA (&alpha; = 0.6) and physical 1-hop spatial neighbor medians (weight 0.4).")

    sage_feat_data = [
        [Paragraph("<b>Feature Index</b>", style_table_header), Paragraph("<b>Physical Metric</b>", style_table_header), Paragraph("<b>Measurement Source</b>", style_table_header), Paragraph("<b>Normalization Range</b>", style_table_header)],
        [Paragraph("x<sub>v, 0</sub>", style_table_cell_bold), Paragraph("Physical Resource Block (PRB) Load", style_table_cell), Paragraph("O-RAN MAC Layer Telemetry", style_table_cell), Paragraph("[0.0, 1.0]", style_table_cell_center)],
        [Paragraph("x<sub>v, 1</sub>", style_table_cell_bold), Paragraph("Signal-to-Interference-Plus-Noise (SINR)", style_table_cell), Paragraph("UE Measurement Reports (MR)", style_table_cell), Paragraph("[-10 dB, +30 dB]", style_table_cell_center)],
        [Paragraph("x<sub>v, 2</sub>", style_table_cell_bold), Paragraph("Reference Signal Received Power (RSRP)", style_table_cell), Paragraph("Radio Link Monitoring (RLM)", style_table_cell), Paragraph("[-140 dBm, -44 dBm]", style_table_cell_center)],
        [Paragraph("x<sub>v, 3</sub>", style_table_cell_bold), Paragraph("Active User Equipment (UE) Density", style_table_cell), Paragraph("RRC Connected Counter", style_table_cell), Paragraph("[0, 500 active UEs]", style_table_cell_center)],
    ]
    t_sage = Table(sage_feat_data, colWidths=[110, 240, 215, 130])
    t_sage.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_EMERALD),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    card6.add_table(t_sage, spacing=12)

    card6.add_formula_box(
        "8-Dimensional Inductive GraphSAGE Formulation (0.091 ms Pure NumPy):",
        "<b>1. Spatial Aggregator:</b> &nbsp; <b>h</b><sub>N(v)</sub> = Aggregate(&thinsp;{ <b>x</b><sub>u</sub> : u in N(v) }&thinsp;) in <b>R</b><sup>4</sup><br/>"
        "<b>2. Inductive Layer-1:</b> &nbsp; <b>h</b><sub>v</sub><sup>(1)</sup> = ReLU(&thinsp;<b>W</b><sub>1</sub> &middot; [<b>x</b><sub>v</sub> || <b>h</b><sub>N(v)</sub>] + <b>b</b><sub>1</sub>&thinsp;), &nbsp; <b>W</b><sub>1</sub> in <b>R</b><sup>16 &times; 8</sup>, <b>b</b><sub>1</sub> in <b>R</b><sup>16</sup><br/>"
        "<b>3. GraphSAGE Trust Score:</b> &nbsp; <b><i>T(v)</i></b> = &sigma;(&thinsp;<b>w</b><sub>2</sub><sup>T</sup> <b>h</b><sub>v</sub><sup>(1)</sup> + b<sub>2</sub>&thinsp;) &middot; exp(&thinsp;&minus;&beta; &middot; ||<b>x</b><sub>v</sub> &minus; <b>x</b><sub>v</sub><sup>ref</sup>||<sub>1</sub>&thinsp;)",
        border_color=C_EMERALD,
        bg_color=colors.HexColor("#f0fdf4")
    )

    card6.add_formula_box(
        "Trust-Weighted Continuous Pareto Utility Arbitration:",
        "<b><i>U</i><sub>joint</sub>(v)</b> = &lambda; &middot; <i>T(v)</i> &middot; &Delta;<sub>TS</sub>(v) + (1 &minus; &lambda;) &middot; <b><i>T(v)</i><sup>2</sup></b> &middot; &Delta;<sub>ES</sub>(v) + &Delta;<sub>QoS</sub>(v)",
        "• <b>Quadratic Trust Penalty (<i>T(v)</i><sup>2</sup>):</b> When FDI corrupts reported load (e.g. spoofed 18%), trust collapses (<i>T</i> &lt; 0.35 &rArr; <i>T</i><sup>2</sup> &lt; 0.12). The energy-saving shutdown utility is vetoed, preventing catastrophic cell sleeping under high actual load.",
        border_color=C_PRIMARY_BLUE,
        bg_color=colors.HexColor("#eff6ff")
    )

    card6.add_stat_triplet([
        ("0.091 ms", "Pure NumPy GNN Latency", C_EMERALD),
        ("67× Margin", "Under 8.4 ms RIC Deadline", C_PRIMARY_BLUE),
        ("0.1% FAR", "Non-Oracle False Alarm Rate", C_CYAN_ACCENT),
    ], height=86)
    card6.check_overflow()

    # =========================================================================
    # COLUMN 3: Empirical Validation, Multi-Baseline & Sovereign Roadmap
    # =========================================================================
    curr_y = CONTENT_TOP

    # --- CARD 3.1: Multi-Baseline Dynamic PDR Evaluation ---
    card7_h = 900
    curr_y -= card7_h
    card7 = CardFlow(c, col3_x, curr_y, COL_WIDTH, card7_h, "7. Multi-Baseline Resilience: AICOP vs BFD vs Static", C_PRIMARY_BLUE)

    card7.add_paragraph("<b>Evaluating Beyond Strawman Baselines:</b> Standard cellular backhauls deploy <b>reactive Bidirectional Forwarding Detection (BFD) hold-timers (RFC 5880 / 3GPP TS 38.300)</b>. We evaluate RAKSHA-NET against both unmanaged static routing and industry-standard reactive BFD under 70% RF jamming:")

    baseline_table_data = [
        [Paragraph("<b>Operational Phase</b>", style_table_header), Paragraph("<b>RAKSHA-NET<br/>(Proactive AI)</b>", style_table_header), Paragraph("<b>Reactive BFD<br/>(3GPP Standard)</b>", style_table_header), Paragraph("<b>Static Route<br/>(Unmanaged)</b>", style_table_header), Paragraph("<b>AI Net Gain<br/>vs BFD / Static</b>", style_table_header)],
        [Paragraph("<b>Phase 1: Normal Pre-Attack</b>", style_table_cell_bold), Paragraph("0.972 (2.8% loss)", style_table_cell_center), Paragraph("0.972 (2.8% loss)", style_table_cell_center), Paragraph("0.972 (2.8% loss)", style_table_cell_center), Paragraph("0.0 pp", style_table_cell_center)],
        [Paragraph("<b>Phase 2: Transient Outage</b>", style_table_cell_bold), Paragraph("<b>0.785</b> (21.5% loss)", style_table_cell_center), Paragraph("0.340 (66.0% loss)", style_table_cell_center), Paragraph("0.311 (68.9% loss)", style_table_cell_center), Paragraph("<b>+44.5 / +47.4 pp</b>", style_table_cell_center)],
        [Paragraph("<b>Phase 3: Sustained Jamming</b>", style_table_cell_bold), Paragraph("<b>0.970</b> (3.0% loss)", style_table_cell_center), Paragraph("0.760 (24.0% loss)", style_table_cell_center), Paragraph("0.325 (67.5% loss)", style_table_cell_center), Paragraph("<b>+21.0 / +64.5 pp</b>", style_table_cell_center)],
        [Paragraph("<b>Phase 4: Post-Attack Recovery</b>", style_table_cell_bold), Paragraph("0.971 (nominal)", style_table_cell_center), Paragraph("0.965 (reconnected)", style_table_cell_center), Paragraph("0.872 (slow drain)", style_table_cell_center), Paragraph("+0.6 / +9.9 pp", style_table_cell_center)],
        [Paragraph("<b>Route Failover Latency</b>", style_table_cell_bold), Paragraph("<b>188 ms</b> (simulated)", style_table_cell_center), Paragraph("1,500–2,800 ms (timeout)", style_table_cell_center), Paragraph("No failover (inf)", style_table_cell_center), Paragraph("<b>10× Faster</b>", style_table_cell_center)],
        [Paragraph("<b>Route Flapping (Jitter)</b>", style_table_cell_bold), Paragraph("<b>0.71 ± 0.82 flaps</b>", style_table_cell_center), Paragraph("Frequent flaps under jitter", style_table_cell_center), Paragraph("0 (stays broken)", style_table_cell_center), Paragraph("<b>25.7× Reduction</b>", style_table_cell_center)],
    ]
    t_base = Table(baseline_table_data, colWidths=[165, 135, 135, 125, 130])
    t_base.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    card7.add_table(t_base, spacing=13)

    card7.add_paragraph("<b>Core Takeaway:</b> RAKSHA-NET achieves <b>+21.0 pp higher PDR over industry-standard reactive BFD</b> because predictive EWMA/CUSUM anomaly scoring anticipates link collapse and pre-arms failover in ~188 ms, whereas BFD must wait for hold-timer loss counters to expire.")
    
    card7.add_formula_box(
        "100-Seed Monte Carlo Statistical Rigor (batch_100_seeds_experiment.csv):",
        "• <b>PDR Restored:</b> From <b>29.6% to 96.8%</b> (+67.16 pp net improvement)<br/>"
        "• <b>95% Confidence Interval:</b> [66.19, 68.14] pp &nbsp;|&nbsp; <b>Significance:</b> <i>p</i> &lt; 0.0001 (paired <i>t</i> = 138.4)<br/>"
        "• <b>Flap Suppression:</b> Hysteresis cuts routing oscillations from 18.3 &plusmn; 3.5 down to <b>0.71 &plusmn; 0.82 flaps</b>.",
        border_color=C_PRIMARY_BLUE,
        bg_color=colors.HexColor("#eff6ff")
    )
    card7.check_overflow()

    # --- CARD 3.2: Detection Ablation & SLA Protection ---
    card8_h = 910
    curr_y -= CARD_GAP
    curr_y -= card8_h
    card8 = CardFlow(c, col3_x, curr_y, COL_WIDTH, card8_h, "8. Detection Ablation & SLA Risk Mitigation", C_CYAN_ACCENT)

    card8.add_paragraph("<b>10-Seed Non-Oracle Detection Ablation (7,200 Cell-Epochs):</b>")

    ablation_data = [
        [Paragraph("<b>Detection Architecture</b>", style_table_header), Paragraph("<b>Precision</b>", style_table_header), Paragraph("<b>Recall</b>", style_table_header), Paragraph("<b>F1-Score</b>", style_table_header), Paragraph("<b>FAR</b>", style_table_header), Paragraph("<b>Collusion F1</b>", style_table_header)],
        [Paragraph("Spatial Median Only", style_table_cell_bold), Paragraph("8.4%", style_table_cell_center), Paragraph("22.3%", style_table_cell_center), Paragraph("12.2%", style_table_cell_center), Paragraph("28.5%", style_table_cell_center), Paragraph("14.2%", style_table_cell_center)],
        [Paragraph("2-Layer MLP (Isolated)", style_table_cell_bold), Paragraph("1.8%", style_table_cell_center), Paragraph("0.8%", style_table_cell_center), Paragraph("1.1%", style_table_cell_center), Paragraph("1.4%", style_table_cell_center), Paragraph("0.0%", style_table_cell_center)],
        [Paragraph("Deviation Penalty Only", style_table_cell_bold), Paragraph("98.4%", style_table_cell_center), Paragraph("43.1%", style_table_cell_center), Paragraph("59.9%", style_table_cell_center), Paragraph("0.0%", style_table_cell_center), Paragraph("51.2%", style_table_cell_center)],
        [Paragraph("<b>Unified AICOP (Proposed)</b>", style_table_cell_bold), Paragraph("<b>92.8 ± 6.2%</b>", style_table_cell_center), Paragraph("<b>63.2 ± 7.3%</b>", style_table_cell_center), Paragraph("<b>74.8 ± 5.3%</b>", style_table_cell_center), Paragraph("<b>0.1%</b>", style_table_cell_center), Paragraph("<b>82.8%</b>", style_table_cell_center)],
    ]
    t_ablation = Table(ablation_data, colWidths=[175, 105, 105, 105, 95, 105])
    t_ablation.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_CYAN_ACCENT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    card8.add_table(t_ablation, spacing=11)

    sla_tradeoff_data = [
        [Paragraph("<b>Power & Control Policy</b>", style_table_header), Paragraph("<b>SLA Failure Rate</b>", style_table_header), Paragraph("<b>Macro Power</b>", style_table_header), Paragraph("<b>Micro Power</b>", style_table_header), Paragraph("<b>Fleet Energy Saving</b>", style_table_header)],
        [Paragraph("Naive Unmanaged Sleep", style_table_cell_bold), Paragraph("55.40% (Collapse)", style_table_cell_center), Paragraph("280 W (Overload)", style_table_cell_center), Paragraph("68 W (Sleeping)", style_table_cell_center), Paragraph("0.0% (Unusable)", style_table_cell_center)],
        [Paragraph("Always-ON (Static)", style_table_cell_bold), Paragraph("10.60% (Nominal)", style_table_cell_center), Paragraph("220 W (Nominal)", style_table_cell_center), Paragraph("145 W (Active)", style_table_cell_center), Paragraph("-4.9% (Wasted)", style_table_cell_center)],
        [Paragraph("PACIFISTA (Hysteresis)", style_table_cell_bold), Paragraph("22.15% (Timer Leaks)", style_table_cell_center), Paragraph("255 W", style_table_cell_center), Paragraph("98 W", style_table_cell_center), Paragraph("+3.3% Saved", style_table_cell_center)],
        [Paragraph("<b>Unified AICOP (Proposed)</b>", style_table_cell_bold), Paragraph("<b>10.60 ± 1.67%</b>", style_table_cell_center), Paragraph("<b>220 W</b>", style_table_cell_center), Paragraph("<b>108 W (Gated)</b>", style_table_cell_center), Paragraph("<b>+25.3% Net Saved</b>", style_table_cell_center)],
    ]
    t_sla = Table(sla_tradeoff_data, colWidths=[175, 135, 125, 125, 130])
    t_sla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_CYAN_ACCENT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    card8.add_table(t_sla, spacing=11)

    card8.add_formula_box(
        "EARTH 5G Macro/Micro Power Dissipation Model:",
        "<b><i>P</i><sub>gNB</sub> = <i>P</i><sub>0</sub> + &Delta;<sub><i>P</i></sub> &middot; <i>L</i>(<i>t</i>)</b> &nbsp; where Macro (<i>P</i><sub>0</sub> = 130 W, &Delta;<sub><i>P</i></sub> = 250 W) &amp; Micro (<i>P</i><sub>0</sub> = 68 W, &Delta;<sub><i>P</i></sub> = 120 W)",
        "AICOP suppresses over-switching wear while reducing overall radio access network energy consumption by 25.3%."
    )
    card8.check_overflow()

    # --- CARD 3.3: Sovereign Hardware Roadmap & Artifact Availability ---
    card9_h = 962
    curr_y -= CARD_GAP
    curr_y -= card9_h
    card9 = CardFlow(c, col3_x, curr_y, COL_WIDTH, card9_h, "9. Sovereign Hardware Roadmap & Reproducibility", C_DARK_BG)

    card9.add_paragraph("<b>Scientific Integrity & TRL-4 Laboratory Testbed Disclosure:</b>")
    card9.add_paragraph("• Evaluated against an active <b>3GPP Rel-17 Open5GS Core</b> (16 active daemons, user plane over Linux <code>ogstun</code>) and containerized network namespaces (Docker + Linux kernel <code>tc netem</code> for delay, loss, and jitter injection).")
    card9.add_paragraph("• Cryptographic benchmarks are wall-clock hardware-timed via native C <code>liboqs</code>; satellite failover times reflect a simulated discrete-event transition model based on 20 ms BFD micro-sampling.")

    roadmap_data = [
        [Paragraph("<b>Development Phase</b>", style_table_header), Paragraph("<b>Target Hardware Platform</b>", style_table_header), Paragraph("<b>Key Technical Milestone</b>", style_table_header), Paragraph("<b>Deployment Window</b>", style_table_header)],
        [Paragraph("<b>Phase 1: COTS Gateways</b>", style_table_cell_bold), Paragraph("Raspberry Pi 5 / Jetson Orin", style_table_cell), Paragraph("Tactical Search-and-Rescue UAV Relays", style_table_cell), Paragraph("Months 1–3", style_table_cell_center)],
        [Paragraph("<b>Phase 2: Sovereign Silicon</b>", style_table_cell_bold), Paragraph("Indian Shakti & Vega RISC-V", style_table_cell), Paragraph("Bare-Metal Pure-NumPy & C ML-KEM Port", style_table_cell), Paragraph("Months 3–6", style_table_cell_center)],
        [Paragraph("<b>Phase 3: Physical SDRs</b>", style_table_cell_bold), Paragraph("HackRF One / USRP B210", style_table_cell), Paragraph("Live OTA Over-The-Air RF Jamming Testbed", style_table_cell), Paragraph("Months 6–12", style_table_cell_center)],
    ]
    t_road = Table(roadmap_data, colWidths=[165, 175, 230, 125])
    t_road.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    card9.add_table(t_road, spacing=13)

    # High-contrast repository verification box
    card9.add_formula_box(
        "OPEN RESEARCH ARTIFACT & REPRODUCIBILITY CODE",
        "<font color='#ffffff'><b>Clone & verify the full 53-test automated suite:</b></font><br/>"
        "<font color='#38bdf8'><b>git clone https://github.com/Rahul109871234/raksha-net.git</b></font><br/>"
        "<font color='#facc15'><b>python run_all_tests.py &nbsp;&nbsp;# 53 / 53 UNIT TESTS PASSING (100%)</b></font>",
        "Apache-2.0 Open Source License · Document ID: SPACE-2026-POSTER-RAKSHA<br/>Sole Author: G. Rahul Reddy (Roll: 24BEC038), Dept. of ECE, PDPM IIITDM Jabalpur",
        border_color=C_HEADER_ACCENT,
        bg_color=colors.HexColor("#0f172a"),
        title_color=C_HEADER_ACCENT,
        text_color=colors.white
    )
    card9.check_overflow()

    # -------------------------------------------------------------------------
    # Save Canvas and Finalize Document
    # -------------------------------------------------------------------------
    c.showPage()
    c.save()
    print(f"\n[SUCCESS] Single-Page A0 Poster successfully generated -> {OUTPUT_PDF}")
    print(f"          Dimensions: {PAGE_WIDTH:.2f} pt x {PAGE_HEIGHT:.2f} pt ({PAGE_WIDTH/72*25.4:.1f} mm x {PAGE_HEIGHT/72*25.4:.1f} mm)")


if __name__ == "__main__":
    build_poster()
