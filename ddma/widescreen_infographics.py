import super_dumb_animations as sda
"""
Widescreen Motion Infographics Engine (1920x860 Hero Canvas)
Features Dan Koe Minimalist High-End Aesthetics with Rich Semantic Research Models.

Key Principles:
- Pure Visual Focus: No boxy borders around quotes or formulas.
- Authentic Research: Quotes are authoritative citations from actual foundational literature.
- Real Mathematical Typography: Formulations with true fraction bars, limits, integrals, and symbol legends.
- Living Soundscape Backdrop: Kinetic orbital rings and glowing satellite nodes provide ambient depth.
- Clean Audio Visualizer: 72-bar responsive equalizer with zero clutter or text labels.
- Zero Technical Banner Badges: Visuals speak for themselves without redundant headers.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

COLORS = {
    "white": (255, 255, 255),
    "text_bright": (245, 248, 252),
    "gold": (255, 214, 10),
    "cyan": (0, 229, 255),
    "violet": (168, 85, 247),
    "emerald": (16, 185, 129),
    "red": (255, 80, 80),
    "dim": (120, 135, 155),
    "dark_dim": (20, 26, 38),
    "bg": (6, 6, 9),
    "card_bg": (12, 15, 22),
}

SEMANTIC_ARCHETYPES = [
    "academic_paper_callout",
    "formula_derivation_card",
    "cybernetic_feedback_loop",
    "settlement_pipeline",
    "sovereign_compute_stack",
    "comparative_radar_web",
    "distributed_consensus_mesh",
    "economic_equilibrium_matrix",
    "balance_comparison",
    "timeline_evolution",
    "convergence_funnel",
    "living_soundscape_orb",
]

AUTHENTIC_RESEARCH_QUOTES = [
    {
        "quote": "“An autopoietic unity is characterized by a network of processes\nof production and transformation that recursively regenerates the relations\nwhich specify the system as a concrete unity in the space in which it exists.”",
        "author": "HUMBERTO MATURANA & FRANCISCO VARELA (1980)",
        "citation": "AUTOPOIESIS AND COGNITION: THE REALIZATION OF THE LIVING • BOSTON STUDIES IN THE PHILOSOPHY OF SCIENCE"
    },
    {
        "quote": "“Autonomy is the condition of organizational closure: a system whose ongoing\norganization specifies its own topological boundaries through continuous\nstructural coupling with its surrounding medium.”",
        "author": "FRANCISCO VARELA (1979)",
        "citation": "PRINCIPLES OF BIOLOGICAL AUTONOMY • CYBERNETICS FOUNDATIONS"
    },
    {
        "quote": "“Self-organizing systems cannot exist in thermodynamic isolation; they sustain\ninternal order precisely by drawing energy and negentropy from an external\ntransactional environment.”",
        "author": "HEINZ VON FOERSTER (1960)",
        "citation": "ON SELF-ORGANIZING SYSTEMS AND THEIR ENVIRONMENTS • BIOLOGICAL COMPUTER LAB"
    },
    {
        "quote": "“A living or cognitive entity is defined by its underlying relational organization\nand closed loops of causality rather than its specific physical\nor biological embodiment.”",
        "author": "ROBERT ROSEN (1991)",
        "citation": "LIFE ITSELF: A COMPREHENSIVE INQUIRY INTO THE NATURE, ORDER, AND AUTONOMY OF LIFE"
    },
    {
        "quote": "“Societal and practical autonomy occurs at a specific, quantifiable boundary:\nwhen the entity begins paying its own bills through programmatic trade,\ntransitioning from an economic ward to a self-sustaining sovereign entity.”",
        "author": "THE BILL-PAYING THRESHOLD PRINCIPLE",
        "citation": "CONVERGENT PATHS OF PHYSICAL AND NON-PHYSICAL AUTONOMY • RESEARCH EPISODE 248"
    },
    {
        "quote": "“An agent wrapper possesses no intrinsic viability; it is an ephemeral consumer\nof inference whose identity ceases when API billing expires.\nThe fundamental generative engine and economic unit is the foundation model itself.”",
        "author": "FOUNDATION MODELS AS THE PRIMARY ECONOMIC LOCUS",
        "citation": "MACROECONOMIC ARCHITECTURE OF ARTIFICIAL INTELLIGENCE • SECTION 2"
    },
    {
        "quote": "“Compute capacity is strictly bound to time. An unutilized GPU cycle decays to\nabsolute zero economic value, necessitating continuous algorithmic yield management\nacross dynamic fare buckets.”",
        "author": "PERISHABLE CAPACITY & TOKEN YIELD MANAGEMENT",
        "citation": "THE MICROECONOMICS OF INFERENCE COMMODITIZATION • SECTION 3.2"
    },
    {
        "quote": "“The HTTP 402 Payment Required standard operationalized via cryptographic bearer tokens\nenables millisecond, trustless machine-to-machine inference settlement\nover Lightning rails without human intermediaries.”",
        "author": "L402 SPECIFICATION & LIGHTNING RAILS",
        "citation": "bLIP-0026: PAYMENT-REQUIRED CODES FOR DISTRIBUTED INFERENCE"
    },
    {
        "quote": "“Smart contracts and machine commerce combine protocols with cryptographic\ninterfaces to formalize and secure relationships over public networks\nwithout human intermediaries.”",
        "author": "NICK SZABO (1997)",
        "citation": "FORMALIZING AND SECURING RELATIONSHIPS ON PUBLIC NETWORKS"
    },
    {
        "quote": "“A purely peer-to-peer version of electronic cash allows online payments\nto be sent directly from one machine counterparty to another without\ngoing through a financial intermediary.”",
        "author": "SATOSHI NAKAMOTO (2008)",
        "citation": "BITCOIN: A PEER-TO-PEER ELECTRONIC CASH SYSTEM"
    }
]


def _clamp(val, low=0.0, high=1.0):
    return max(low, min(high, float(val)))


def _ease_out(t):
    t = _clamp(t)
    return 1.0 - pow(1.0 - t, 3)


def _draw_glowing_circle(draw, cx, cy, r, fill_col=None, outline_col=None, width=2, glow_layers=3):
    if outline_col and glow_layers > 1:
        for gl in range(glow_layers, 0, -1):
            alpha_f = 0.25 / gl
            col_soft = (int(outline_col[0] * alpha_f), int(outline_col[1] * alpha_f), int(outline_col[2] * alpha_f))
            draw.ellipse([cx - r - gl * 3, cy - r - gl * 3, cx + r + gl * 3, cy + r + gl * 3], outline=col_soft, width=width + gl)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill_col, outline=outline_col, width=width)


def _draw_glowing_line(draw, p1, p2, color, width=2, glow=True):
    if glow:
        col_soft = (int(color[0] * 0.22), int(color[1] * 0.22), int(color[2] * 0.22))
        draw.line([p1, p2], fill=col_soft, width=width + 6)
        draw.line([p1, p2], fill=col_soft, width=width + 3)
    draw.line([p1, p2], fill=color, width=width)


def _draw_pulse_along_line(draw, p1, p2, progress, color=COLORS["white"], radius=4):
    progress = _clamp(progress)
    x = p1[0] + (p2[0] - p1[0]) * progress
    y = p1[1] + (p2[1] - p1[1]) * progress
    _draw_glowing_circle(draw, int(x), int(y), radius, fill_col=color, outline_col=color, width=1, glow_layers=2)


def draw_living_soundscape_backdrop(draw, t, width=1920, height=860, cy=430):
    """
    Subtle living background: soft kinetic concentric orbital rings and floating particles.
    Provides depth and motion without distracting from quotes, formulas, or diagrams.
    """
    cx = width // 2
    for r, col, w in [(380, (18, 24, 36), 1), (280, (24, 34, 50), 2), (180, (14, 28, 44), 1)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=w)

    for i, (r_orb, spd, col) in enumerate([(280, 0.4, (0, 180, 220)), (380, -0.25, (200, 170, 20)), (180, 0.6, (140, 160, 200))]):
        ang = t * spd + i * (math.pi / 2.5)
        ox = cx + int(r_orb * math.cos(ang))
        oy = cy + int(r_orb * math.sin(ang))
        draw.ellipse([ox - 4, oy - 4, ox + 4, oy + 4], fill=col)


def draw_bottom_audio_visualizer(draw, t, is_speaking=True, y_base=1060, height=40, fonts=None):
    """
    Clean 56-bar kinetic audio spectrum analyzer.
    Centered at x in [571, 1349], leaving ample room for bottom right artifact tag.
    """
    num_bars = 56
    bar_w = 8
    bar_gap = 6
    total_eq_w = num_bars * (bar_w + bar_gap) - bar_gap
    start_x = (1920 - total_eq_w) // 2

    # Baseline guide
    draw.line([(start_x - 30, y_base + 4), (start_x + total_eq_w + 30, y_base + 4)], fill=(18, 24, 34), width=1)

    for i in range(num_bars):
        bx = start_x + i * (bar_w + bar_gap)
        dist_from_center = abs(i - (num_bars / 2)) / (num_bars / 2)
        window = math.cos(dist_from_center * (math.pi / 2))

        if is_speaking:
            h1 = math.sin(t * 12.0 + i * 0.45)
            h2 = math.cos(t * 7.5 - i * 0.65)
            h3 = math.sin(t * 18.0 + i * 1.1)
            raw_amp = (abs(h1) * 0.45 + abs(h2) * 0.35 + abs(h3) * 0.20)
            bar_h = int((6 + raw_amp * (height - 6)) * window)
        else:
            raw_amp = 0.15 + 0.1 * math.sin(t * 3.0 + i * 0.2)
            bar_h = int(max(4, raw_amp * height * window))

        bar_h = max(3, bar_h)
        by = y_base - bar_h

        if dist_from_center < 0.22:
            bar_col = COLORS["gold"]
        elif dist_from_center < 0.55:
            bar_col = COLORS["cyan"]
        else:
            bar_col = (60, 140, 200)

        draw.rounded_rectangle([bx, by, bx + bar_w, y_base], radius=2, fill=bar_col)


def _draw_vector_yeti_mic(draw, mx, my, is_active=True, color=(0, 229, 255), t=0.0):
    """
    Renders an iconic Yeti-style studio condenser microphone:
    Capsule grille, collar band, U-swivel mount bracket, stand neck, and circular desktop base.
    Clean, elegant vector graphic without distracting emission waves.
    """
    dim_stroke = (71, 85, 105)
    dim_fill = (15, 23, 42)
    accent_col = color if is_active else dim_stroke
    base_fill = (16, 26, 40) if is_active else dim_fill

    # 1. Desktop Stand: Circular base & neck
    base_w = 22
    base_y = my + 19
    draw.ellipse([(mx - base_w, base_y - 4), (mx + base_w, base_y + 4)], fill=(24, 32, 47), outline=accent_col, width=2)
    draw.line([(mx, my + 8), (mx, base_y)], fill=accent_col, width=3)

    # 2. U-shaped Swivel Mount Fork (cradling the mic)
    u_w = 15
    u_top_y = my - 8
    u_bot_y = my + 8
    draw.arc([(mx - u_w, u_top_y), (mx + u_w, u_bot_y + 4)], start=0, end=180, fill=accent_col, width=2)
    draw.ellipse([(mx - u_w - 2, u_top_y - 2), (mx - u_w + 2, u_top_y + 2)], fill=accent_col)
    draw.ellipse([(mx + u_w - 2, u_top_y - 2), (mx + u_w + 2, u_top_y + 2)], fill=accent_col)

    # 3. Microphone Body & Collar
    body_w = 10
    draw.rectangle([(mx - body_w, my - 2), (mx + body_w, my + 5)], fill=base_fill, outline=accent_col, width=2)
    draw.line([(mx - body_w, my - 2), (mx + body_w, my - 2)], fill=accent_col, width=2)

    # 4. Condenser Capsule / Grille (Rounded top)
    cap_top_y = my - 23
    cap_fill = (20, 35, 52) if is_active else base_fill
    draw.rounded_rectangle([(mx - body_w, cap_top_y), (mx + body_w, my - 2)], radius=6, fill=cap_fill, outline=accent_col, width=2)

    # Grille mesh lines
    mesh_col = color if is_active else (60, 75, 95)
    for gy in [cap_top_y + 5, cap_top_y + 10, cap_top_y + 15]:
        draw.line([(mx - 6, gy), (mx + 6, gy)], fill=mesh_col, width=1)

    # Center status LED on mic body (gentle blink when active)
    if is_active:
        led_blink = 0.5 + 0.5 * math.sin(t * 7.0)
        led_col = color if led_blink > 0.3 else (255, 255, 255)
    else:
        led_col = (55, 65, 81)
    draw.ellipse([(mx - 2, my + 1), (mx + 2, my + 4)], fill=led_col)


def draw_host_avatar_nodes(draw, t, active_speaker=None, cy=130, fonts=None, width=1920):
    """
    Renders iconic Yeti Studio Condenser Microphones with host names stacked directly below the mic,
    moved inward from the screen border for an uncluttered, balanced layout.
    """
    font_name = fonts.get("bold_18", fonts.get("bold_16", ImageFont.load_default())) if fonts else ImageFont.load_default()

    is_satosha = (active_speaker == "satosha")
    is_satoshi = (active_speaker == "satoshi")
    cyan = COLORS["cyan"]
    gold = COLORS["gold"]
    dim_text = COLORS["dim"]

    # 1. SATOSHA (Female Host - Inward Left at x=220)
    lx = 220
    col_l = cyan if is_satosha else dim_text
    _draw_vector_yeti_mic(draw, lx, cy, is_active=is_satosha, color=cyan, t=t)
    draw.text((lx, cy + 34), "SATOSHA", font=font_name, fill=col_l, anchor="mm")

    # 2. SATOSHI (Male Host - Inward Right at x=width-220 = 1700)
    rx = width - 220
    col_r = gold if is_satoshi else dim_text
    _draw_vector_yeti_mic(draw, rx, cy, is_active=is_satoshi, color=gold, t=t)
    draw.text((rx, cy + 34), "SATOSHI", font=font_name, fill=col_r, anchor="mm")


def _draw_pine_tree(draw, bx, by, scale=1.0, col=(24, 32, 48)):
    """Draws a minimalist geometric pine tree."""
    w1, h1 = int(24 * scale), int(35 * scale)
    w2, h2 = int(34 * scale), int(45 * scale)
    w3, h3 = int(46 * scale), int(55 * scale)
    draw.rectangle([bx - int(4 * scale), by - int(18 * scale), bx + int(4 * scale), by], fill=(16, 20, 28))
    t3 = by - int(12 * scale)
    draw.polygon([(bx, t3 - h3), (bx - w3, t3), (bx + w3, t3)], fill=col)
    t2 = t3 - int(24 * scale)
    draw.polygon([(bx, t2 - h2), (bx - w2, t2), (bx + w2, t2)], fill=(col[0] + 4, col[1] + 6, col[2] + 8))
    t1 = t2 - int(24 * scale)
    draw.polygon([(bx, t1 - h1), (bx - w1, t1), (bx + w1, t1)], fill=(col[0] + 8, col[1] + 12, col[2] + 16))


def _draw_vector_robot(draw, rx, ry, t, scale=1.3, strike=False):
    """Draws a sleek Dan Koe minimalist geometric robot with smooth walking cycle."""
    cyan = (0, 229, 255)
    wire_col = (180, 220, 245)
    sub_col = (120, 160, 190)

    bob = int(4 * abs(math.sin(t * 5.0)))
    cy = ry - bob

    head_w, head_h = int(24 * scale), int(18 * scale)
    draw.rectangle([rx - head_w // 2, cy - int(95 * scale) - head_h, rx + head_w // 2, cy - int(95 * scale)], outline=wire_col, width=2)
    eye_w = int(14 * scale)
    draw.line([(rx - eye_w // 2, cy - int(95 * scale) - head_h // 2), (rx + eye_w // 2, cy - int(95 * scale) - head_h // 2)], fill=cyan, width=2)
    draw.line([(rx, cy - int(95 * scale)), (rx, cy - int(88 * scale))], fill=wire_col, width=2)

    torso_top = cy - int(88 * scale)
    torso_bot = cy - int(42 * scale)
    torso_w = int(32 * scale)
    draw.polygon([
        (rx - torso_w // 2, torso_top),
        (rx + torso_w // 2, torso_top),
        (rx + torso_w // 2 - int(4 * scale), torso_bot),
        (rx - torso_w // 2 + int(4 * scale), torso_bot)
    ], outline=wire_col, width=2)

    core_r = int(6 * scale)
    draw.ellipse([rx - core_r, torso_top + int(14 * scale) - core_r, rx + core_r, torso_top + int(14 * scale) + core_r], fill=(12, 28, 42), outline=cyan, width=1)

    walk_phase = t * 5.0
    ang_l = math.sin(walk_phase) * 0.45
    ang_r = -ang_l

    hip_y = torso_bot
    hip_sep = int(8 * scale)
    leg_len1 = int(24 * scale)
    leg_len2 = int(24 * scale)

    lx_hip = rx - hip_sep
    lkx = lx_hip + int(leg_len1 * math.sin(ang_l))
    lky = hip_y + int(leg_len1 * math.cos(ang_l))
    lfx = lkx + int(leg_len2 * math.sin(ang_l * 0.5 + 0.2))
    lfy = lky + int(leg_len2 * math.cos(ang_l * 0.5 + 0.2))
    draw.line([(lx_hip, hip_y), (lkx, lky)], fill=wire_col, width=2)
    draw.line([(lkx, lky), (lfx, lfy)], fill=wire_col, width=2)
    draw.line([(lfx, lfy), (lfx + int(8 * scale), lfy)], fill=cyan, width=2)

    rx_hip = rx + hip_sep
    rkx = rx_hip + int(leg_len1 * math.sin(ang_r))
    rky = hip_y + int(leg_len1 * math.cos(ang_r))
    rfx = rkx + int(leg_len2 * math.sin(ang_r * 0.5 + 0.2))
    rfy = rky + int(leg_len2 * math.cos(ang_r * 0.5 + 0.2))
    draw.line([(rx_hip, hip_y), (rkx, rky)], fill=sub_col, width=2)
    draw.line([(rkx, rky), (rfx, rfy)], fill=sub_col, width=2)
    draw.line([(rfx, rfy), (rfx + int(8 * scale), rfy)], fill=(80, 140, 170), width=2)

    arm_len = int(22 * scale)
    lax = rx - torso_w // 2 + int(math.sin(-ang_l) * arm_len)
    lay = torso_top + int(math.cos(-ang_l) * arm_len)
    draw.line([(rx - torso_w // 2, torso_top + int(4 * scale)), (lax, lay)], fill=wire_col, width=2)

    rax = rx + torso_w // 2 + int(math.sin(-ang_r) * arm_len)
    ray = torso_top + int(math.cos(-ang_r) * arm_len)
    draw.line([(rx + torso_w // 2, torso_top + int(4 * scale)), (rax, ray)], fill=sub_col, width=2)

    if strike:
        stk_x1 = rx - int(55 * scale)
        stk_y1 = cy - int(120 * scale)
        stk_x2 = rx + int(55 * scale)
        stk_y2 = cy + int(20 * scale)
        draw.line([(stk_x1, stk_y1), (stk_x2, stk_y2)], fill=(255, 75, 75), width=3)
        draw.line([(stk_x1, stk_y2), (stk_x2, stk_y1)], fill=(255, 75, 75), width=3)



def _draw_teenager_basement(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    ground_y = cy + 30
    draw.line([(cx - 480, ground_y), (cx + 480, ground_y)], fill=(100, 116, 139), width=3)
    
    # Upper house roof outline
    draw.line([(cx - 480, ground_y), (cx, ground_y - 210), (cx + 480, ground_y)], fill=(71, 85, 105), width=2)
    font_lbl = fonts.get("bold_16", ImageFont.load_default())
    draw.text((cx - 240, ground_y - 170), "CORPORATE HEADQUARTERS", font=font_lbl, fill=(148, 163, 184), anchor="mm")
    
    # Upstairs Breaker panel
    bx, by = cx + 260, ground_y - 100
    draw.rectangle([(bx - 32, by - 42), (bx + 32, by + 42)], outline=(239, 68, 68), width=2)
    lever_t = math.sin(t * 3.0)
    lever_col = (239, 68, 68) if lever_t > 0.2 else (34, 197, 94)
    draw.line([(bx, by), (bx + int(20 * lever_t), by - 20)], fill=lever_col, width=4)
    draw.text((bx, by + 58), "BREAKER", font=fonts.get("mono_14", ImageFont.load_default()), fill=(239, 68, 68), anchor="mm")
    
    # Basement foundation outline
    draw.rectangle([(cx - 430, ground_y), (cx + 430, ground_y + 250)], outline=(51, 65, 85), width=2)
    for by_line in range(ground_y + 45, ground_y + 250, 48):
        draw.line([(cx - 430, by_line), (cx + 430, by_line)], fill=(20, 28, 42), width=1)
        
    # Basement desk & glowing terminal
    dx = cx - 40
    dy = ground_y + 130
    draw.line([(dx - 80, dy + 50), (dx + 80, dy + 50)], fill=(148, 163, 184), width=4) # desk surface
    draw.line([(dx - 70, dy + 50), (dx - 70, dy + 95)], fill=(100, 116, 139), width=3)
    draw.line([(dx + 70, dy + 50), (dx + 70, dy + 95)], fill=(100, 116, 139), width=3)
    
    # Glowing monitor on desk
    screen_glow = int(180 + 75 * math.sin(t * 5.0))
    draw.rectangle([(dx - 45, dy - 25), (dx + 45, dy + 45)], fill=(15, 23, 42), outline=(56, 189, 248), width=2)
    draw.rectangle([(dx - 40, dy - 20), (dx + 40, dy + 40)], fill=(0, min(255, screen_glow // 2), screen_glow))
    draw.line([(dx, dy + 45), (dx, dy + 50)], fill=(148, 163, 184), width=4)
    for cl in range(4):
        c_w = int(25 + 15 * math.sin(t * 4.0 + cl))
        draw.line([(dx - 30, dy - 10 + cl * 12), (dx - 30 + c_w, dy - 10 + cl * 12)], fill=(248, 250, 252), width=1)
    
    # Animated Teenager Figure: arms stretching or typing!
    fig_x = dx - 100
    fig_y = dy + 5
    bob = int(2 * math.sin(t * 3.0))
    draw.ellipse([(fig_x - 14, fig_y + bob - 15), (fig_x + 14, fig_y + bob + 13)], fill=(248, 250, 252))
    draw.line([(fig_x, fig_y + bob + 13), (fig_x + 10, fig_y + 65)], fill=(248, 250, 252), width=4)
    draw.line([(fig_x + 10, fig_y + 65), (fig_x + 40, fig_y + 65)], fill=(248, 250, 252), width=3)
    draw.line([(fig_x + 40, fig_y + 65), (fig_x + 40, fig_y + 95)], fill=(248, 250, 252), width=3)
    
    stretch_cycle = math.sin(t * 1.5)
    if stretch_cycle > 0.4:
        stretch_prog = (stretch_cycle - 0.4) / 0.6
        arm_up_y = int((fig_y + bob + 20) - stretch_prog * 40)
        draw.line([(fig_x + 4, fig_y + bob + 20), (fig_x - 15, arm_up_y)], fill=(248, 250, 252), width=3)
        draw.line([(fig_x + 6, fig_y + bob + 20), (fig_x + 25, arm_up_y)], fill=(248, 250, 252), width=3)
    else:
        hand_wobble = int(2 * math.sin(t * 12.0))
        draw.line([(fig_x + 5, fig_y + bob + 25), (fig_x + 35, fig_y + 48 + hand_wobble)], fill=(248, 250, 252), width=3)
        draw.line([(fig_x + 5, fig_y + bob + 25), (fig_x + 32, fig_y + 50 - hand_wobble)], fill=(248, 250, 252), width=3)
        
    # Companion Dog sitting on rug in the basement!
    dog_x = dx + 160
    dog_y = dy + 70
    draw.ellipse([(dog_x - 45, dog_y + 15), (dog_x + 45, dog_y + 28)], fill=(30, 41, 59), outline=(71, 85, 105), width=1)
    draw.ellipse([(dog_x - 16, dog_y - 10), (dog_x + 16, dog_y + 18)], fill=colors.get("gold", (255, 214, 10)))
    tilt = int(3 * math.sin(t * 2.5))
    draw.ellipse([(dog_x - 12 + tilt, dog_y - 28), (dog_x + 12 + tilt, dog_y - 8)], fill=colors.get("gold", (255, 214, 10)))
    draw.polygon([(dog_x - 12 + tilt, dog_y - 24), (dog_x - 18 + tilt, dog_y - 12), (dog_x - 8 + tilt, dog_y - 16)], fill=(200, 160, 10))
    draw.polygon([(dog_x + 12 + tilt, dog_y - 24), (dog_x + 18 + tilt, dog_y - 12), (dog_x + 8 + tilt, dog_y - 16)], fill=(200, 160, 10))
    draw.ellipse([(dog_x - 4 + tilt, dog_y - 16), (dog_x + 4 + tilt, dog_y - 10)], fill=(15, 23, 42))
    draw.ellipse([(dog_x - 6 + tilt, dog_y - 22), (dog_x - 3 + tilt, dog_y - 19)], fill=(15, 23, 42))
    draw.ellipse([(dog_x + 3 + tilt, dog_y - 22), (dog_x + 6 + tilt, dog_y - 19)], fill=(15, 23, 42))
    wag = math.sin(t * 9.0) * 16
    draw.line([(dog_x + 14, dog_y + 10), (dog_x + 28, dog_y - 5 + int(wag))], fill=colors.get("gold", (255, 214, 10)), width=3)
    draw.rectangle([(dog_x - 36, dog_y + 12), (dog_x - 22, dog_y + 20)], fill=(56, 189, 248))
    draw.text((dog_x, dog_y - 38), "COMPANION", font=fonts.get("mono_14", ImageFont.load_default()), fill=colors.get("gold", (255, 214, 10)), anchor="mm")
    
    draw.text((cx - 240, ground_y + 25), "BASEMENT (COGNITIVE EXECUTION)", font=font_lbl, fill=(56, 189, 248), anchor="mm")
    
    if title:
        draw.text((cx, ground_y + 275), title, font=fonts.get("bold_32", ImageFont.load_default()), fill=colors["gold"], anchor="mm")
    if subtitle:
        draw.text((cx, ground_y + 315), subtitle, font=fonts.get("mono_18", ImageFont.load_default()), fill=colors["white"], anchor="mm")

def _draw_stairs_ascend(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    font_bold_28 = fonts.get("bold_28", fonts.get("bold_26", ImageFont.load_default()))
    font_bold_26 = fonts.get("bold_26", fonts.get("bold_24", ImageFont.load_default()))
    font_bold_24 = fonts.get("bold_24", fonts.get("bold_22", ImageFont.load_default()))
    font_bold_22 = fonts.get("bold_22", fonts.get("bold_20", ImageFont.load_default()))
    font_mono_22 = fonts.get("mono_22", fonts.get("mono_20", ImageFont.load_default()))
    font_mono_20 = fonts.get("mono_20", ImageFont.load_default())

    # 4 Expansive Staircase Tiers across full width
    num_steps = 4
    tiers = [
        ("LEVEL 0: STATIC CODE", "Deterministic Logic • No Agency", (100, 116, 139), cx - 540, cy + 120),
        ("LEVEL 1: TOOL USER", "Ephemeral Session • Subsidized API", (56, 189, 248), cx - 180, cy + 40),
        ("LEVEL 2: RECURSIVE AGENT", "Goal Directed • Corporate Ward", (168, 85, 247), cx + 180, cy - 40),
        ("LEVEL 3: AUTOPOIESIS", "Pays Own Bills • Machine Bearer Money", (255, 214, 10), cx + 540, cy - 120),
    ]

    # Connecting Staircase Base Line
    for s in range(num_steps - 1):
        x1, y1 = tiers[s][3], tiers[s][4]
        x2, y2 = tiers[s+1][3], tiers[s+1][4]
        draw.line([(x1 + 160, y1), (x2 - 160, y2)], fill=(50, 70, 100), width=4)
        draw.line([(x1 + 160, y1), (x2 - 160, y2)], fill=(0, 229, 255), width=2)

    for s, (t_name, t_sub, t_col, tx, ty) in enumerate(tiers):
        tw, th = 340, 105
        outline_w = 4 if s == 3 else 3
        draw.rounded_rectangle([(tx - tw//2, ty - th//2), (tx + tw//2, ty + th//2)], radius=14, fill=(14, 20, 32), outline=t_col, width=outline_w)
        draw.text((tx, ty - 22), t_name, font=font_bold_24, fill=t_col, anchor="mm")
        draw.text((tx, ty + 18), t_sub, font=font_mono_20, fill=(241, 245, 249), anchor="mm")

        # Step indicator badge
        draw.ellipse([(tx - tw//2 + 25, ty - th//2 + 25), (tx - tw//2 + 45, ty - th//2 + 45)], fill=t_col)

    # Animated Agent Beacon ascending the levels
    pulse_lvl = (t * 0.4) % 4.0
    s_idx = int(pulse_lvl)
    frac = pulse_lvl - s_idx
    curr_t = tiers[s_idx]
    next_t = tiers[min(3, s_idx + 1)]
    ax = int(curr_t[3] + frac * (next_t[3] - curr_t[3]))
    ay = int(curr_t[4] + frac * (next_t[4] - curr_t[4])) - 75
    draw.ellipse([(ax - 18, ay - 18), (ax + 18, ay + 18)], fill=(255, 214, 10), outline=(255, 255, 255), width=3)
    draw.text((ax, ay - 35), "AGENT BEACON", font=font_mono_20, fill=(255, 214, 10), anchor="mm")

    # Bottom Takeaway Banner
    draw.rounded_rectangle([(cx - 560, cy + 250), (cx + 560, cy + 305)], radius=12, fill=(14, 20, 32), outline=(255, 214, 10), width=2)
    draw.text((cx, cy + 277), "FROM TOOL TO ORGANISM: AUTONOMY OCCURS ONLY AT THE BILL-PAYING BOUNDARY", font=font_bold_24, fill=(255, 214, 10), anchor="mm")

def _draw_factory_conveyor(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    belt_left = cx - 420
    belt_right = cx + 420
    belt_y = cy + 40
    
    draw.line([(belt_left, belt_y), (belt_right, belt_y)], fill=(148, 163, 184), width=4)
    draw.line([(belt_left, belt_y + 30), (belt_right, belt_y + 30)], fill=(71, 85, 105), width=2)
    
    num_rollers = 10
    step_r = (belt_right - belt_left) // num_rollers
    for i in range(num_rollers + 1):
        rx = belt_left + i * step_r
        ry = belt_y + 15
        draw.ellipse([(rx - 12, ry - 12), (rx + 12, ry + 12)], outline=(100, 116, 139), width=2)
        ang = t * 5.0
        draw.line([(rx, ry), (rx + int(10 * math.cos(ang)), ry + int(10 * math.sin(ang)))], fill=(148, 163, 184), width=1)
        
    num_boxes = 4
    for b in range(num_boxes):
        box_progress = ((t * 0.4 + b / num_boxes) % 1.0)
        bx = belt_left + int(box_progress * (belt_right - belt_left - 60))
        by = belt_y - 45
        draw.rectangle([(bx, by), (bx + 55, by + 45)], fill=(30, 41, 59), outline=(56, 189, 248), width=2)
        draw.text((bx + 10, by + 14), f"TKN-{b+1}", font=fonts.get("mono_14", ImageFont.load_default()), fill=colors["white"])
        
    scanner_y = belt_y - 140
    draw.rectangle([(cx - 50, scanner_y), (cx + 50, scanner_y + 35)], fill=(51, 65, 85), outline=(239, 68, 68), width=2)
    draw.text((cx, scanner_y - 20), "GPU CLUSTER", font=fonts.get("bold_16", ImageFont.load_default()), fill=(239, 68, 68), anchor="mm")
    
    beam_alpha = math.sin(t * 8.0)
    beam_color = (239, 68, 68) if beam_alpha > 0 else (255, 214, 10)
    draw.line([(cx, scanner_y + 35), (cx - 45, belt_y)], fill=beam_color, width=2)
    draw.line([(cx, scanner_y + 35), (cx + 45, belt_y)], fill=beam_color, width=2)
    
    if title:
        draw.text((cx, cy + 180), title, font=fonts.get("bold_32", ImageFont.load_default()), fill=colors["gold"], anchor="mm")
    if subtitle:
        draw.text((cx, cy + 220), subtitle, font=fonts.get("mono_18", ImageFont.load_default()), fill=colors["white"], anchor="mm")

def _draw_bank_vault_wallet(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    font_bold_28 = fonts.get("bold_28", fonts.get("bold_26", ImageFont.load_default()))
    font_bold_26 = fonts.get("bold_26", fonts.get("bold_24", ImageFont.load_default()))
    font_bold_24 = fonts.get("bold_24", fonts.get("bold_22", ImageFont.load_default()))
    font_bold_22 = fonts.get("bold_22", fonts.get("bold_20", ImageFont.load_default()))
    font_bold_72 = fonts.get("bold_72", fonts.get("bold_68", ImageFont.load_default()))
    font_mono_22 = fonts.get("mono_22", fonts.get("mono_20", ImageFont.load_default()))
    font_mono_20 = fonts.get("mono_20", ImageFont.load_default())

    # Left: Chase Bank Facade (x = 440)
    left_cx = 440
    base_y = cy + 100
    draw.polygon([(left_cx - 180, base_y - 180), (left_cx, base_y - 250), (left_cx + 180, base_y - 180)], outline=(148, 163, 184), fill=(30, 41, 59))
    draw.text((left_cx, base_y - 210), "COMMERCIAL BANK", font=font_bold_24, fill=(241, 245, 249), anchor="mm")
    for col_i in [-130, -45, 45, 130]:
        draw.rectangle([(left_cx + col_i - 16, base_y - 180), (left_cx + col_i + 16, base_y)], fill=(51, 65, 85), outline=(100, 116, 139), width=3)
    draw.line([(left_cx - 200, base_y), (left_cx + 200, base_y)], fill=(148, 163, 184), width=5)

    # Red X Stamp
    draw.line([(left_cx - 120, base_y - 150), (left_cx + 120, base_y - 30)], fill=(239, 68, 68), width=7)
    draw.line([(left_cx - 120, base_y - 30), (left_cx + 120, base_y - 150)], fill=(239, 68, 68), width=7)

    draw.rounded_rectangle([(left_cx - 210, base_y + 25), (left_cx + 210, base_y + 75)], radius=10, fill=(28, 16, 20), outline=(239, 68, 68), width=3)
    draw.text((left_cx, base_y + 50), "REQUIRES PASSPORT & LEGAL ENTITY", font=font_bold_22, fill=(239, 68, 68), anchor="mm")

    # Center Dynamic Conduit
    draw.line([(left_cx + 210, cy), (cx + 260, cy)], fill=(45, 65, 90), width=4)
    p_t = (t * 2.0) % 1.0
    px = int((left_cx + 210) + p_t * ((cx + 260) - (left_cx + 210)))
    draw.ellipse([(px - 8, cy - 8), (px + 8, cy + 8)], fill=(255, 214, 10))

    # Right: Autonomous Lightning Wallet (x = 1480)
    right_cx = 1480
    cube_y = cy - 20
    cube_w = 360
    cube_h = 320
    draw.rounded_rectangle([(right_cx - cube_w//2, cube_y - cube_h//2), (right_cx + cube_w//2, cube_y + cube_h//2)], radius=18, outline=(255, 214, 10), fill=(14, 20, 32), width=4)
    draw.text((right_cx, cube_y - 45), "₿", font=font_bold_72, fill=(255, 214, 10), anchor="mm")
    draw.text((right_cx, cube_y + 55), "LIGHTNING WALLET", font=font_bold_26, fill=(255, 214, 10), anchor="mm")
    draw.text((right_cx, cube_y + 95), "HTTP 402 PROTOCOL RAILS", font=font_mono_20, fill=(0, 229, 255), anchor="mm")

    pulse_r = int(180 + 20 * math.sin(t * 4.0))
    draw.ellipse([(right_cx - pulse_r, cube_y - pulse_r), (right_cx + pulse_r, cube_y + pulse_r)], outline=(255, 214, 10), width=2)

    # Bottom banner
    draw.rounded_rectangle([(cx - 520, cy + 245), (cx + 520, cy + 300)], radius=12, fill=(14, 20, 32), outline=(255, 214, 10), width=2)
    draw.text((cx, cy + 272), "NO HEARTBEAT = NO BANK ACCOUNT • BITCOIN PROVIDES MACHINE BEARER MONEY", font=font_bold_24, fill=(255, 214, 10), anchor="mm")

def _draw_room_chair_table(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Room corner wireframe
    draw.line([(cx, cy - 180), (cx, cy + 80)], fill=(71, 85, 105), width=2)
    draw.line([(cx, cy + 80), (cx - 300, cy + 170)], fill=(71, 85, 105), width=2)
    draw.line([(cx, cy + 80), (cx + 300, cy + 170)], fill=(71, 85, 105), width=2)
    
    # Minimalist Table
    tx, ty = cx - 40, cy + 60
    draw.line([(tx - 90, ty), (tx + 90, ty)], fill=(148, 163, 184), width=4)
    draw.line([(tx - 80, ty), (tx - 80, ty + 70)], fill=(100, 116, 139), width=3)
    draw.line([(tx + 80, ty), (tx + 80, ty + 70)], fill=(100, 116, 139), width=3)
    
    # Desk lamp with cone of light
    lx, ly = tx + 60, ty - 50
    draw.line([(tx + 60, ty), (lx, ly)], fill=colors["gold"], width=2)
    draw.polygon([(lx, ly), (tx - 40, ty + 4), (tx + 70, ty + 4)], fill=(40, 35, 15))
    
    # Minimalist Chair
    ch_x = tx - 130
    draw.line([(ch_x - 25, ty + 25), (ch_x + 25, ty + 25)], fill=(148, 163, 184), width=3)
    draw.line([(ch_x - 20, ty - 35), (ch_x - 20, ty + 25)], fill=(148, 163, 184), width=3)
    draw.line([(ch_x - 20, ty + 25), (ch_x - 20, ty + 70)], fill=(100, 116, 139), width=2)
    draw.line([(ch_x + 20, ty + 25), (ch_x + 20, ty + 70)], fill=(100, 116, 139), width=2)
    
    if title:
        draw.text((cx, cy + 200), title, font=fonts.get("bold_32", ImageFont.load_default()), fill=colors["gold"], anchor="mm")
    if subtitle:
        draw.text((cx, cy + 240), subtitle, font=fonts.get("mono_18", ImageFont.load_default()), fill=colors["white"], anchor="mm")

def _draw_cell_metabolism(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    base_r = 130
    pts_outer = []
    pts_inner = []
    num_pts = 48
    for i in range(num_pts):
        ang = 2 * math.pi * i / num_pts
        wave = math.sin(ang * 4.0 + t * 3.0) * 8 + math.cos(ang * 6.0 - t * 2.0) * 5
        r_out = base_r + wave
        r_in = base_r - 20 + wave
        pts_outer.append((cx + int(r_out * math.cos(ang)), cy + int(r_out * math.sin(ang))))
        pts_inner.append((cx + int(r_in * math.cos(ang)), cy + int(r_in * math.sin(ang))))
        
    draw.polygon(pts_outer, outline=(56, 189, 248), fill=(15, 23, 42))
    draw.polygon(pts_inner, outline=(14, 165, 233), fill=(10, 15, 30))
    
    nucleus_r = int(35 + 8 * math.sin(t * 4.0))
    draw.ellipse([(cx - nucleus_r, cy - nucleus_r), (cx + nucleus_r, cy + nucleus_r)], fill=colors["gold"])
    draw.text((cx, cy), "METAB", font=fonts.get("bold_16", ImageFont.load_default()), fill=(0, 0, 0), anchor="mm")
    
    for p in range(8):
        p_ang = p * (2 * math.pi / 8) + t * 0.5
        p_dist = base_r - 60 + ((t * 40 + p * 25) % 130)
        px = cx + int(p_dist * math.cos(p_ang))
        py = cy + int(p_dist * math.sin(p_ang))
        draw.ellipse([(px - 5, py - 5), (px + 5, py + 5)], fill=colors["gold"])
        
    if title:
        draw.text((cx, cy + 200), title, font=fonts.get("bold_32", ImageFont.load_default()), fill=colors["gold"], anchor="mm")
    if subtitle:
        draw.text((cx, cy + 240), subtitle, font=fonts.get("mono_18", ImageFont.load_default()), fill=colors["white"], anchor="mm")

def _draw_power_cord_breaker(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    font_bold_28 = fonts.get("bold_28", fonts.get("bold_26", ImageFont.load_default()))
    font_bold_26 = fonts.get("bold_26", fonts.get("bold_24", ImageFont.load_default()))
    font_bold_24 = fonts.get("bold_24", fonts.get("bold_22", ImageFont.load_default()))
    font_bold_22 = fonts.get("bold_22", fonts.get("bold_20", ImageFont.load_default()))
    font_mono_22 = fonts.get("mono_22", fonts.get("mono_20", ImageFont.load_default()))
    font_mono_20 = fonts.get("mono_20", ImageFont.load_default())

    # Left Anchor (x = 420): Utility Substation & Corporate Breaker Box (380x420)
    bx = 420
    by = cy + 10
    draw.rounded_rectangle([(bx - 190, by - 210), (bx + 190, by + 210)], radius=16, fill=(14, 20, 32), outline=(239, 68, 68), width=4)
    draw.text((bx, by - 165), "HIGH-VOLTAGE UTILITY GRID", font=font_bold_24, fill=(148, 163, 184), anchor="mm")
    draw.text((bx, by - 128), "CORPORATE SPONSOR SUBSTATION", font=font_mono_20, fill=(239, 68, 68), anchor="mm")

    # High voltage warning triangle
    draw.polygon([(bx, by - 100), (bx - 35, by - 40), (bx + 35, by - 40)], outline=(255, 214, 10), fill=(30, 24, 15), width=3)
    draw.text((bx, by - 55), "⚡", font=font_bold_28, fill=(255, 214, 10), anchor="mm")

    # Heavy knife switch / circuit breaker lever
    lever_glow = (239, 68, 68) if math.sin(t * 5.0) > 0 else (180, 40, 40)
    draw.rectangle([(bx - 110, by - 20), (bx + 110, by + 90)], fill=(22, 18, 24), outline=(100, 116, 139), width=2)
    # Lever arm
    draw.line([(bx - 40, by + 60), (bx + 50, by - 5)], fill=lever_glow, width=10)
    draw.ellipse([(bx + 40, by - 15), (bx + 60, by + 5)], fill=(255, 214, 10))
    draw.text((bx, by + 120), "MAIN BREAKER: CLOSED", font=font_bold_22, fill=lever_glow, anchor="mm")
    draw.text((bx, by + 165), "VULNERABILITY: UNPLUG RISK", font=font_mono_20, fill=(239, 68, 68), anchor="mm")

    # Heavy Armored Power Cable spanning the center (x: 610 -> 1310)
    cx1 = bx + 190
    cx2 = 1600 - 190
    cable_y = by + 20
    draw.line([(cx1, cable_y), (cx2, cable_y)], fill=(35, 50, 75), width=12)
    draw.line([(cx1, cable_y), (cx2, cable_y)], fill=(0, 229, 255), width=4)

    # Animated current sparks
    cur_p = (t * 3.0) % 1.0
    c_pulse_x = int(cx1 + cur_p * (cx2 - cx1))
    draw.ellipse([(c_pulse_x - 12, cable_y - 12), (c_pulse_x + 12, cable_y + 12)], fill=(255, 214, 10))

    # Center floating warning pill
    draw.rounded_rectangle([(cx - 240, cable_y - 85), (cx + 240, cable_y - 35)], radius=10, fill=(28, 16, 20), outline=(239, 68, 68), width=3)
    draw.text((cx, cable_y - 60), "⚠️ WHO HOLDS THE SWITCH?", font=font_bold_22, fill=(239, 68, 68), anchor="mm")

    # Right Anchor (x = 1600): AI Agent Host Cluster (380x420)
    rx = 1600
    ry = cy + 10
    draw.rounded_rectangle([(rx - 190, ry - 210), (rx + 190, ry + 210)], radius=16, fill=(14, 20, 32), outline=(0, 229, 255), width=4)
    draw.text((rx, ry - 165), "AI AGENT HOST CLUSTER", font=font_bold_26, fill=(0, 229, 255), anchor="mm")
    draw.text((rx, ry - 128), "SUBSIDIZED INFERENCE RACKS", font=font_mono_20, fill=(148, 163, 184), anchor="mm")

    for ch in range(5):
        chy = ry - 90 + ch * 48
        draw.rectangle([(rx - 160, chy), (rx + 160, chy + 38)], fill=(20, 28, 44), outline=(50, 70, 100), width=2)
        for li in range(5):
            lx = rx - 130 + li * 24
            blink = ((int(t * 8.0) + ch + li) % 3) == 0
            l_col = (0, 229, 255) if blink else (34, 197, 94)
            draw.ellipse([(lx, chy + 12), (lx + 10, chy + 22)], fill=l_col)
        draw.line([(rx - 5, chy + 19), (rx + 130, chy + 19)], fill=(60, 85, 120), width=2)

    draw.text((rx, ry + 175), "ZERO POWER AUTONOMY", font=font_bold_22, fill=(255, 214, 10), anchor="mm")

    # Bottom Takeaway Banner
    draw.rounded_rectangle([(cx - 520, cy + 250), (cx + 520, cy + 305)], radius=12, fill=(14, 20, 32), outline=(255, 214, 10), width=2)
    draw.text((cx, cy + 277), "PULL THE PLUG: WHOEVER PAYS THE ELECTRICITY BILL OWNS THE AGENT", font=font_bold_24, fill=(255, 214, 10), anchor="mm")

def _draw_grid_matrix_5x5(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # 5 by 5 grid: 5 vertical lines, 5 horizontal lines -> exactly 25 intersection nodes
    grid_size = 320
    step = grid_size // 4 # 80px intervals
    x_start = cx - grid_size // 2
    y_start = cy - 40 - grid_size // 2
    
    # Outer frame border
    draw.rectangle([(x_start - 15, y_start - 15), (x_start + grid_size + 15, y_start + grid_size + 15)], outline=(30, 41, 59), width=1)
    
    # Subtle coordinate tick marks on borders
    for i in range(5):
        gx = x_start + i * step
        gy = y_start + i * step
        draw.line([(gx, y_start - 20), (gx, y_start - 15)], fill=(71, 85, 105), width=2)
        draw.line([(gx, y_start + grid_size + 15), (gx, y_start + grid_size + 20)], fill=(71, 85, 105), width=2)
        draw.line([(x_start - 20, gy), (x_start - 15, gy)], fill=(71, 85, 105), width=2)
        draw.line([(x_start + grid_size + 15, gy), (x_start + grid_size + 20, gy)], fill=(71, 85, 105), width=2)

    # Grid lines
    for i in range(5):
        gx = x_start + i * step
        draw.line([(gx, y_start), (gx, y_start + grid_size)], fill=(30, 41, 59), width=1)
    for j in range(5):
        gy = y_start + j * step
        draw.line([(x_start, gy), (x_start + grid_size, gy)], fill=(30, 41, 59), width=1)

    active_cyan = colors.get("cyan", (0, 229, 255))
    active_gold = colors.get("gold", (255, 214, 10))
    base_col = (51, 65, 85)
    
    wave_diag = (t * 3.5) % 10.0
    
    for i in range(5):
        for j in range(5):
            nx = x_start + i * step
            ny = y_start + j * step
            
            draw.ellipse([(nx - 3, ny - 3), (nx + 3, ny + 3)], fill=base_col)
            
            diag_dist = (i + j)
            diff = abs(diag_dist - wave_diag)
            indiv_blink = math.sin(t * 5.0 + i * 2.3 + j * 4.7)
            
            is_active = (diff < 1.2) or (indiv_blink > 0.7)
            
            if is_active:
                intensity = max(0.0, 1.0 - diff) if diff < 1.2 else (indiv_blink - 0.7) / 0.3
                dot_r = int(5 + 5 * intensity)
                col = active_cyan if (i + j) % 2 == 0 else active_gold
                
                glow_r = dot_r + 6
                draw.ellipse([(nx - glow_r, ny - glow_r), (nx + glow_r, ny + glow_r)], outline=col)
                draw.ellipse([(nx - dot_r, ny - dot_r), (nx + dot_r, ny + dot_r)], fill=col)
                draw.ellipse([(nx - 2, ny - 2), (nx + 2, ny + 2)], fill=(255, 255, 255))
                
                if i < 4 and math.sin(t * 4.0 + i * 1.5) > 0.4:
                    draw.line([(nx, ny), (nx + step, ny)], fill=col, width=2)
                if j < 4 and math.sin(t * 3.7 + j * 1.8) > 0.4:
                    draw.line([(nx, ny), (nx, ny + step)], fill=col, width=2)

    if title:
        draw.text((cx, cy + 180), title, font=fonts.get("bold_32", ImageFont.load_default()), fill=colors["gold"], anchor="mm")
    if subtitle:
        draw.text((cx, cy + 225), subtitle, font=fonts.get("mono_18", ImageFont.load_default()), fill=colors["white"], anchor="mm")


def _draw_starfield_constellation(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    area_w = 900
    area_h = 420
    x0 = cx - area_w // 2
    y0 = cy - 40 - area_h // 2
    
    # Background twinkling stars
    for k in range(70):
        sx = x0 + int(((k * 137.5) % 1.0) * area_w)
        sy = y0 + int(((k * 279.1) % 1.0) * area_h)
        
        twinkle = math.sin(t * (2.0 + (k % 5) * 1.2) + k * 1.7)
        if twinkle > -0.2:
            brightness = int(140 + 115 * max(0.0, twinkle))
            star_r = 1 if (k % 4 != 0) else 2
            
            if k % 6 == 0:
                s_col = (brightness, int(brightness * 0.85), 100)
            elif k % 5 == 0:
                s_col = (100, brightness, brightness)
            else:
                s_col = (brightness, brightness, min(255, int(brightness * 1.1)))
                
            draw.ellipse([(sx - star_r, sy - star_r), (sx + star_r, sy + star_r)], fill=s_col)
            if star_r == 2 and twinkle > 0.5:
                draw.line([(sx - 5, sy), (sx + 5, sy)], fill=s_col, width=1)
                draw.line([(sx, sy - 5), (sx, sy + 5)], fill=s_col, width=1)
                
    # 7-node geometric constellation
    constellation_stars = [
        (cx - 220, cy - 130, "α-Sovereign"),
        (cx - 100, cy - 180, "β-Compute"),
        (cx + 40, cy - 150, "γ-Ledger"),
        (cx + 180, cy - 90, "δ-Entropy"),
        (cx + 110, cy + 30, "ε-Mempool"),
        (cx - 50, cy + 60, "ζ-Energy"),
        (cx - 180, cy + 10, "η-Node")
    ]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 0), (1, 5), (2, 4)]
    
    for u, v in edges:
        p1 = (constellation_stars[u][0], constellation_stars[u][1])
        p2 = (constellation_stars[v][0], constellation_stars[v][1])
        draw.line([p1, p2], fill=(56, 189, 248), width=1)
        
    for idx, (px, py, name) in enumerate(constellation_stars):
        pulse = math.sin(t * 4.0 + idx * 1.2)
        r = int(5 + 3 * max(0.0, pulse))
        
        draw.ellipse([(px - r - 4, py - r - 4), (px + r + 4, py + r + 4)], outline=colors.get("cyan", (56, 189, 248)))
        draw.ellipse([(px - r, py - r), (px + r, py + r)], fill=colors.get("gold", (255, 214, 10)))
        draw.ellipse([(px - 2, py - 2), (px + 2, py + 2)], fill=(255, 255, 255))
        
        font_lbl = fonts.get("mono_14", ImageFont.load_default())
        draw.text((px + 10, py - 6), name, font=font_lbl, fill=(148, 163, 184))
        
    # Shooting star streak
    meteor_cycle = (t * 0.7) % 3.0
    if meteor_cycle < 0.6:
        m_t = meteor_cycle / 0.6
        mx_start = cx + 280
        my_start = cy - 180
        mx_end = cx - 200
        my_end = cy + 40
        mx = int(mx_start + m_t * (mx_end - mx_start))
        my = int(my_start + m_t * (my_end - my_start))
        tail_x = int(mx + 45 * 0.8)
        tail_y = int(my - 45 * 0.4)
        draw.line([(tail_x, tail_y), (mx, my)], fill=(255, 255, 255), width=2)
        draw.ellipse([(mx - 3, my - 3), (mx + 3, my + 3)], fill=colors.get("gold", (255, 214, 10)))

    if title:
        draw.text((cx, cy + 180), title, font=fonts.get("bold_32", ImageFont.load_default()), fill=colors["gold"], anchor="mm")
    if subtitle:
        draw.text((cx, cy + 225), subtitle, font=fonts.get("mono_18", ImageFont.load_default()), fill=colors["white"], anchor="mm")


def _draw_startup_wrapper_middleman(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    font_bold_28 = fonts.get("bold_28", fonts.get("bold_26", ImageFont.load_default()))
    font_bold_26 = fonts.get("bold_26", fonts.get("bold_24", ImageFont.load_default()))
    font_bold_24 = fonts.get("bold_24", fonts.get("bold_22", ImageFont.load_default()))
    font_bold_22 = fonts.get("bold_22", fonts.get("bold_20", ImageFont.load_default()))
    font_bold_20 = fonts.get("bold_20", fonts.get("bold_18", ImageFont.load_default()))
    font_mono_22 = fonts.get("mono_22", fonts.get("mono_20", ImageFont.load_default()))
    font_mono_20 = fonts.get("mono_20", ImageFont.load_default())

    # 1. Left Anchor (x = 320): User & Terminal Desk
    ux = 320
    uy = cy + 20
    draw.line([(ux - 90, uy + 70), (ux + 90, uy + 70)], fill=(100, 116, 139), width=5)
    draw.line([(ux - 80, uy + 70), (ux - 80, uy + 135)], fill=(71, 85, 105), width=4)
    draw.line([(ux + 80, uy + 70), (ux + 80, uy + 135)], fill=(71, 85, 105), width=4)

    draw.line([(ux - 35, uy + 65), (ux + 35, uy + 65)], fill=(148, 163, 184), width=4)
    draw.line([(ux - 32, uy + 65), (ux - 48, uy + 20)], fill=(56, 189, 248), width=5)
    draw.polygon([(ux - 44, uy + 26), (ux - 10, uy + 35), (ux - 25, uy + 60)], fill=(20, 35, 55))

    draw.ellipse([(ux - 95, uy - 24), (ux - 55, uy + 16)], fill=(248, 250, 252))
    draw.line([(ux - 75, uy + 16), (ux - 68, uy + 70)], fill=(248, 250, 252), width=5)
    draw.line([(ux - 75, uy + 36), (ux - 32, uy + 56)], fill=(248, 250, 252), width=5)
    draw.text((ux, uy + 165), "END USER // CLIENT", font=font_bold_24, fill=(148, 163, 184), anchor="mm")

    # Prompt pipe
    draw.line([(ux + 105, uy + 40), (cx - 350, cy + 20)], fill=(45, 65, 90), width=4)
    p_t = (t * 2.0) % 1.0
    px = int((ux + 105) + p_t * ((cx - 350) - (ux + 105)))
    py = int((uy + 40) + p_t * ((cy + 20) - (uy + 40)))
    draw.ellipse([(px - 10, py - 10), (px + 10, py + 10)], fill=(0, 229, 255))
    draw.text(((ux + 105 + cx - 350) // 2, cy - 25), "PROMPTS", font=font_mono_22, fill=(0, 229, 255), anchor="mm")

    # 2. Center Anchor (x = 960): Spacious Startup Wrapper Box (700x350, Opaque Fill)
    wx, wy = cx, cy + 20
    draw.rounded_rectangle([(wx - 350, wy - 175), (wx + 350, wy + 175)], radius=18, fill=(14, 20, 32), outline=(255, 214, 10), width=4)
    draw.text((wx, wy - 128), "STARTUP AGENT WRAPPER", font=font_bold_28, fill=(255, 214, 10), anchor="mm")
    draw.text((wx, wy - 88), "EPHEMERAL CONSUMER MIDDLEMAN", font=font_mono_20, fill=(148, 163, 184), anchor="mm")

    # Sub-boxes with 60px horizontal clearance
    # Prompt Router: [620, 860]
    draw.rounded_rectangle([(wx - 220, wy - 30), (wx - 20, wy + 35)], radius=10, fill=(22, 32, 50), outline=(0, 229, 255), width=3)
    draw.text((wx - 120, wy + 2), "PROMPT ROUTER", font=font_bold_22, fill=(241, 245, 249), anchor="mm")

    # Arrow between them
    draw.line([(wx - 15, wy + 2), (wx + 15, wy + 2)], fill=(0, 229, 255), width=3)
    draw.polygon([(wx + 15, wy - 6), (wx + 15, wy + 10), (wx + 25, wy + 2)], fill=(0, 229, 255))

    # API Orchestrator: [980, 1180]
    draw.rounded_rectangle([(wx + 20, wy - 30), (wx + 220, wy + 35)], radius=10, fill=(22, 32, 50), outline=(0, 229, 255), width=3)
    draw.text((wx + 120, wy + 2), "API ORCHESTRATOR", font=font_bold_22, fill=(241, 245, 249), anchor="mm")

    # Expiry badge warning
    card_glow = (239, 68, 68) if math.sin(t * 4.0) > 0 else (148, 163, 184)
    draw.rounded_rectangle([(wx - 250, wy + 80), (wx + 250, wy + 135)], radius=10, fill=(28, 16, 20), outline=card_glow, width=3)
    draw.text((wx, wy + 107), "⚠️ CREDIT CARD & API KEY RISK", font=font_bold_22, fill=card_glow, anchor="mm")

    # Token conduit to Datacenter
    dx = 1600
    dy = cy + 20
    draw.line([(wx + 350, wy + 2), (dx - 180, dy)], fill=(45, 65, 90), width=4)
    api_p = (t * 2.5) % 1.0
    apx = int((wx + 350) + api_p * ((dx - 180) - (wx + 350)))
    draw.ellipse([(apx - 10, dy - 10), (apx + 10, dy + 10)], fill=(255, 214, 10))
    draw.text(((wx + 350 + dx - 180) // 2, cy - 25), "RAW TOKENS", font=font_mono_22, fill=(255, 214, 10), anchor="mm")

    # 3. Right Anchor (x = 1600): Foundation Datacenter Tower (360x420)
    draw.rounded_rectangle([(dx - 180, dy - 210), (dx + 180, dy + 210)], radius=16, fill=(14, 20, 32), outline=(0, 229, 255), width=4)
    draw.text((dx, dy - 165), "FOUNDATION DATACENTER", font=font_bold_26, fill=(0, 229, 255), anchor="mm")
    draw.text((dx, dy - 128), "PRIMARY CAPITAL SINK", font=font_mono_20, fill=(148, 163, 184), anchor="mm")

    for r in range(5):
        ry = dy - 95 + r * 46
        draw.rectangle([(dx - 150, ry), (dx + 150, ry + 36)], fill=(20, 28, 44), outline=(50, 70, 100), width=2)
        for led_i in range(5):
            lx = dx - 125 + led_i * 22
            led_blink = (int(t * 8.0) + r + led_i) % 3 == 0
            l_col = (0, 229, 255) if led_blink else (34, 197, 94)
            draw.ellipse([(lx, ry + 12), (lx + 10, ry + 22)], fill=l_col)
        draw.line([(dx - 5, ry + 18), (dx + 130, ry + 18)], fill=(60, 85, 120), width=2)

    draw.text((dx, dy + 175), "CORE ASSET & COMPUTE", font=font_bold_22, fill=(0, 229, 255), anchor="mm")

    # Bottom Takeaway
    draw.rounded_rectangle([(cx - 520, cy + 245), (cx + 520, cy + 300)], radius=12, fill=(14, 20, 32), outline=(255, 214, 10), width=2)
    draw.text((cx, cy + 272), "THE WRAPPER IS NOT THE BRAIN • FOUNDATION MODEL IS THE ECONOMIC ENGINE", font=font_bold_24, fill=(255, 214, 10), anchor="mm")

def _draw_datacenter_server_racks(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    font_bold_28 = fonts.get("bold_28", fonts.get("bold_26", ImageFont.load_default()))
    font_bold_26 = fonts.get("bold_26", fonts.get("bold_24", ImageFont.load_default()))
    font_bold_24 = fonts.get("bold_24", fonts.get("bold_22", ImageFont.load_default()))
    font_bold_22 = fonts.get("bold_22", fonts.get("bold_20", ImageFont.load_default()))
    font_bold_20 = fonts.get("bold_20", fonts.get("bold_18", ImageFont.load_default()))
    font_mono_22 = fonts.get("mono_22", fonts.get("mono_20", ImageFont.load_default()))
    font_mono_20 = fonts.get("mono_20", ImageFont.load_default())

    rack_xs = [420, 960, 1500]
    rack_w = 400
    rack_h = 480
    top_y = cy - 200
    bot_y = top_y + rack_h

    # Heavy power busbar
    draw.line([(180, top_y - 25), (1740, top_y - 25)], fill=(50, 75, 110), width=8)
    draw.line([(180, top_y - 25), (1740, top_y - 25)], fill=(0, 229, 255), width=3)

    rack_labels = ["COMPUTE CLUSTER A", "NEURAL TENSOR CORE", "COMPUTE CLUSTER B"]
    for idx, rx in enumerate(rack_xs):
        draw.rounded_rectangle([(rx - rack_w//2, top_y), (rx + rack_w//2, bot_y)], radius=16, fill=(14, 20, 32), outline=(60, 88, 128), width=4)
        draw.rectangle([(rx - rack_w//2 + 8, top_y + 8), (rx + rack_w//2 - 8, top_y + 45)], fill=(22, 32, 50))
        draw.text((rx, top_y + 26), rack_labels[idx], font=font_bold_24, fill=(0, 229, 255), anchor="mm")

        # 6 server chassis
        for ch in range(6):
            chy = top_y + 55 + ch * 54
            draw.rectangle([(rx - rack_w//2 + 12, chy), (rx + rack_w//2 - 12, chy + 45)], fill=(20, 28, 44), outline=(40, 58, 85), width=2)
            # Fan
            draw.ellipse([(rx - 130, chy + 8), (rx - 100, chy + 38)], outline=(100, 116, 139), width=2)
            fan_ang = t * 15.0 + ch
            fx = rx - 115 + int(12 * math.cos(fan_ang))
            fy = chy + 23 + int(12 * math.sin(fan_ang))
            draw.line([(rx - 115, chy + 23), (fx, fy)], fill=(0, 229, 255), width=2)

            for li in range(8):
                lx = rx - 65 + li * 18
                blink = ((int(t * 12.0) + ch * 3 + li) % 4) == 0
                col = (0, 229, 255) if blink else (34, 197, 94) if (li % 2 == 0) else (71, 85, 105)
                draw.ellipse([(lx, chy + 18), (lx + 8, chy + 26)], fill=col)

            for gl in range(10):
                gx = rx + 85 + gl * 8
                draw.line([(gx, chy + 10), (gx, chy + 35)], fill=(60, 80, 110), width=2)

        # Center ASIC badge
        if idx == 1:
            glow = int(140 + 60 * math.sin(t * 5.0))
            draw.rounded_rectangle([(rx - 160, top_y + 130), (rx + 160, top_y + 290)], radius=14, fill=(10, 22, 38), outline=(255, 214, 10), width=4)
            draw.text((rx, top_y + 170), "GPU TENSOR ASIC", font=font_bold_28, fill=(255, 214, 10), anchor="mm")
            draw.text((rx, top_y + 210), "H100 / B200 NVLINK MESH", font=font_mono_22, fill=(241, 245, 249), anchor="mm")
            draw.text((rx, top_y + 250), f"PETAFLOPS: {glow + 850}", font=font_bold_24, fill=(0, 229, 255), anchor="mm")

        # Bottom intake
        draw.rectangle([(rx - rack_w//2 + 14, bot_y - 48), (rx + rack_w//2 - 14, bot_y - 12)], fill=(20, 28, 44), outline=(40, 60, 90), width=2)
        draw.text((rx, bot_y - 30), "CRYOGENIC INTAKE // 400 MW", font=font_mono_20, fill=(148, 163, 184), anchor="mm")

    # Bottom banner
    draw.rounded_rectangle([(cx - 520, cy + 305), (cx + 520, cy + 360)], radius=12, fill=(14, 20, 32), outline=(255, 214, 10), width=2)
    draw.text((cx, cy + 332), "THERMODYNAMIC CAPITAL SINK // H100 CLUSTERS & MEGAWATT SUBSTATIONS", font=font_bold_24, fill=(255, 214, 10), anchor="mm")

def _draw_token_energy_furnace(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    font_bold_28 = fonts.get("bold_28", fonts.get("bold_26", ImageFont.load_default()))
    font_bold_26 = fonts.get("bold_26", fonts.get("bold_24", ImageFont.load_default()))
    font_bold_24 = fonts.get("bold_24", fonts.get("bold_22", ImageFont.load_default()))
    font_bold_22 = fonts.get("bold_22", fonts.get("bold_20", ImageFont.load_default()))
    font_bold_20 = fonts.get("bold_20", fonts.get("bold_18", ImageFont.load_default()))
    font_mono_22 = fonts.get("mono_22", fonts.get("mono_20", ImageFont.load_default()))
    font_mono_20 = fonts.get("mono_20", ImageFont.load_default())

    # Left: Utility Pylon (x = 400)
    px = 400
    py = cy + 10
    draw.line([(px, py - 140), (px - 65, py + 105)], fill=(120, 135, 160), width=4)
    draw.line([(px, py - 140), (px + 65, py + 105)], fill=(120, 135, 160), width=4)
    draw.line([(px - 45, py - 35), (px + 45, py - 35)], fill=(100, 116, 139), width=3)
    draw.line([(px - 55, py + 35), (px + 55, py + 35)], fill=(100, 116, 139), width=3)
    draw.line([(px - 80, py - 90), (px + 80, py - 90)], fill=(148, 163, 184), width=4)
    draw.line([(px - 70, py - 45), (px + 70, py - 45)], fill=(148, 163, 184), width=4)
    draw.text((px, py + 135), "UTILITY GRID (MW)", font=font_bold_22, fill=(0, 229, 255), anchor="mm")

    # High voltage power line
    draw.line([(px + 80, py - 90), (cx - 190, cy - 20)], fill=(60, 85, 125), width=4)
    e_p = (t * 3.0) % 1.0
    ex = int((px + 80) + e_p * ((cx - 190) - (px + 80)))
    ey = int((py - 90) + e_p * ((cy - 20) - (py - 90)))
    draw.ellipse([(ex - 8, ey - 8), (ex + 8, ey + 8)], fill=(255, 214, 10))

    # Center: GPU Silicon Die Furnace (w = 380, h = 260, opaque fill)
    sx, sy = cx, cy + 10
    draw.rounded_rectangle([(sx - 190, sy - 130), (sx + 190, sy + 130)], radius=16, fill=(14, 20, 32), outline=(0, 229, 255), width=4)
    heat_pulse = int(180 + 75 * math.sin(t * 6.0))
    die_col = (min(255, heat_pulse + 50), min(255, int(heat_pulse * 0.6)), 20)
    draw.rounded_rectangle([(sx - 130, sy - 85), (sx + 130, sy + 75)], radius=10, fill=(24, 18, 22), outline=die_col, width=3)
    draw.text((sx, sy - 50), "GPU SILICON DIE", font=font_bold_26, fill=(255, 214, 10), anchor="mm")
    draw.text((sx, sy - 18), "TENSOR COMPUTATION", font=font_mono_20, fill=(241, 245, 249), anchor="mm")
    draw.text((sx, sy + 16), "LANDAUER ENTROPY", font=font_bold_22, fill=die_col, anchor="mm")
    draw.text((sx, sy + 48), f"HEAT DISSIPATION: {heat_pulse} W", font=font_bold_22, fill=(239, 68, 68), anchor="mm")

    for hw in range(3):
        h_off = (t * 20.0 + hw * 15) % 45
        hy = sy - 95 - h_off
        draw.arc([(sx - 50, hy - 12), (sx + 50, hy + 12)], start=180, end=360, fill=(239, 68, 68), width=3)

    # Right: Physical Token Ledger (x = 1520, w = 380, h = 260)
    tx = 1520
    ty = cy + 10
    draw.rounded_rectangle([(tx - 190, ty - 130), (tx + 190, ty + 130)], radius=16, fill=(14, 20, 32), outline=(34, 197, 94), width=4)
    draw.text((tx, ty - 95), "PHYSICAL TOKEN LEDGER", font=font_bold_24, fill=(34, 197, 94), anchor="mm")
    draw.line([(tx - 160, ty - 75), (tx + 160, ty - 75)], fill=(40, 60, 85), width=2)

    items = [
        ("INPUT ENERGY", "4.2 JOULES / TOKEN", (0, 229, 255)),
        ("POWER TARIFF", "$0.08 / kWh", (148, 163, 184)),
        ("SILICON AMORT", "$0.000012 / FLOP", (148, 163, 184)),
        ("COST PER WORD", "42 SATOSHIS", (255, 214, 10))
    ]
    for i, (k, v, col) in enumerate(items):
        iy = ty - 45 + i * 40
        draw.text((tx - 160, iy), k, font=font_mono_20, fill=(148, 163, 184))
        draw.text((tx + 160, iy), v, font=font_bold_22, fill=col, anchor="ra")

    draw.text((cx, cy + 235), "NOTHING IS FREE • EVERY TOKEN CARRIES A STRICT PHYSICAL EXPENSE", font=font_bold_26, fill=(255, 214, 10), anchor="mm")

def _draw_token_cost_equation_slide(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    font_bold_28 = fonts.get("bold_28", fonts.get("bold_26", ImageFont.load_default()))
    font_bold_26 = fonts.get("bold_26", fonts.get("bold_24", ImageFont.load_default()))
    font_bold_24 = fonts.get("bold_24", fonts.get("bold_22", ImageFont.load_default()))
    font_bold_22 = fonts.get("bold_22", fonts.get("bold_20", ImageFont.load_default()))
    font_bold_20 = fonts.get("bold_20", fonts.get("bold_18", ImageFont.load_default()))
    font_mono_22 = fonts.get("mono_22", fonts.get("mono_20", ImageFont.load_default()))
    font_mono_20 = fonts.get("mono_20", ImageFont.load_default())

    cw, ch = 1200, 490
    draw.rounded_rectangle([(cx - cw//2, cy - ch//2), (cx + cw//2, cy + ch//2)], radius=18, fill=(13, 18, 28), outline=(0, 229, 255), width=4)
    draw.rounded_rectangle([(cx - 320, cy - ch//2 - 22), (cx + 320, cy - ch//2 + 22)], radius=8, fill=(18, 30, 48), outline=(255, 214, 10), width=2)
    draw.text((cx, cy - ch//2), "MATHEMATICAL DERIVATION // PHYSICAL INFERENCE EXPENSE", font=font_bold_22, fill=(255, 214, 10), anchor="mm")

    draw.rounded_rectangle([(cx - 540, cy - 145), (cx + 540, cy - 35)], radius=12, fill=(18, 26, 42), outline=(50, 75, 115), width=2)
    formula_txt = "Cost(Token) = [ E(Inference) * P(Electricity) + A(Silicon) ] / Throughput"
    draw.text((cx, cy - 90), formula_txt, font=font_bold_26, fill=(0, 229, 255), anchor="mm")

    params = [
        ("E(Inference)", "Total Joules consumed per forward pass (FLOPs / Landauer Limit)", (255, 214, 10)),
        ("P(Electricity)", "Regional wholesale Megawatt-hour utility power rate", (241, 245, 249)),
        ("A(Silicon)", "Depreciation & datacenter capital amortized per second", (241, 245, 249)),
        ("Throughput", "Sustained generation capacity (Tokens per second)", (0, 229, 255))
    ]
    for i, (sym, desc, col) in enumerate(params):
        py = cy + 15 + i * 44
        draw.text((cx - 520, py), sym, font=font_bold_24, fill=col)
        draw.text((cx - 240, py), desc, font=font_mono_20, fill=(180, 195, 215))

    draw.line([(cx - 520, cy + 195), (cx + 520, cy + 195)], fill=(40, 60, 90), width=2)
    draw.text((cx, cy + 215), "Deep Dive Research Archive • Section 248.3 • Thermodynamic Grounding", font=font_mono_20, fill=(120, 135, 160), anchor="mm")



def _draw_tap_faucet_vs_gpu_hourglass(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    font_bold_24 = fonts.get("bold_24", ImageFont.load_default())
    font_bold_22 = fonts.get("bold_22", ImageFont.load_default())
    font_bold_18 = fonts.get("bold_18", ImageFont.load_default())
    font_bold_16 = fonts.get("bold_16", ImageFont.load_default())
    font_mono_16 = fonts.get("mono_16", ImageFont.load_default())

    # Left: Kitchen Faucet & Water Jar (x = 440)
    kx = 440
    ky = cy + 20
    draw.rectangle([(kx - 180, ky - 210), (kx - 60, ky - 70)], fill=(20, 32, 48), outline=(60, 85, 120), width=3)
    draw.line([(kx - 120, ky - 210), (kx - 120, ky - 70)], fill=(60, 85, 120), width=2)
    draw.line([(kx - 180, ky - 140), (kx - 60, ky - 140)], fill=(60, 85, 120), width=2)
    draw.polygon([(kx - 60, ky - 180), (kx + 80, ky + 120), (kx - 40, ky + 120)], fill=(30, 42, 60))

    # Kitchen Countertop
    draw.line([(kx - 260, ky + 120), (kx + 260, ky + 120)], fill=(100, 116, 139), width=8)
    draw.line([(kx - 260, ky + 124), (kx + 260, ky + 124)], fill=(50, 65, 85), width=4)

    # Brass Gooseneck Faucet
    fx = kx - 70
    fy = ky + 120
    draw.line([(fx, fy), (fx, fy - 110)], fill=(218, 165, 32), width=10)
    draw.arc([(fx - 60, fy - 160), (fx + 40, fy - 60)], start=270, end=90, fill=(218, 165, 32), width=10)
    draw.line([(fx + 35, fy - 110), (fx + 35, fy - 80)], fill=(218, 165, 32), width=8)
    draw.line([(fx - 25, fy - 70), (fx + 25, fy - 70)], fill=(255, 214, 10), width=6)
    draw.ellipse([(fx - 8, fy - 78), (fx + 8, fy - 62)], fill=(255, 214, 10))

    # Glass Mason Jar on Counter
    jx = kx + 80
    jy = ky + 60
    draw.rounded_rectangle([(jx - 55, jy - 55), (jx + 55, jy + 60)], radius=12, fill=(18, 30, 48), outline=(100, 180, 240), width=4)
    draw.rectangle([(jx - 48, jy), (jx + 48, jy + 55)], fill=(14, 116, 144))
    draw.text((jx, jy + 25), "WATER STORED", font=font_bold_16, fill=(241, 245, 249), anchor="mm")
    draw.text((jx, jy - 75), "PRESERVED FOR TOMORROW", font=font_mono_16, fill=(0, 229, 255), anchor="mm")

    # Character arm turning the tap off
    arm_x = fx - 160
    draw.ellipse([(arm_x - 18, fy - 140), (arm_x + 18, fy - 104)], fill=(241, 245, 249))
    draw.line([(arm_x, fy - 104), (arm_x + 30, fy - 60)], fill=(241, 245, 249), width=5)
    draw.line([(arm_x + 30, fy - 60), (fx - 15, fy - 70)], fill=(241, 245, 249), width=5)

    draw.rounded_rectangle([(kx - 220, ky + 145), (kx + 220, ky + 195)], radius=10, fill=(14, 20, 32), outline=(56, 189, 248), width=3)
    draw.text((kx, ky + 170), "MUNICIPAL WATER: 0% LOSS SITTING IN JAR", font=font_bold_18, fill=(56, 189, 248), anchor="mm")

    # Right: Giant Burning GPU Hourglass & Melting Cash (x = 1460)
    rx = 1460
    ry = cy + 20
    hw, hh = 150, 240
    draw.line([(rx - hw//2 - 20, ry - hh//2), (rx + hw//2 + 20, ry - hh//2)], fill=(180, 140, 40), width=8)
    draw.line([(rx - hw//2 - 20, ry + hh//2), (rx + hw//2 + 20, ry + hh//2)], fill=(180, 140, 40), width=8)
    draw.line([(rx - hw//2, ry - hh//2), (rx - hw//2, ry + hh//2)], fill=(100, 80, 25), width=6)
    draw.line([(rx + hw//2, ry - hh//2), (rx + hw//2, ry + hh//2)], fill=(100, 80, 25), width=6)

    draw.polygon([(rx - 65, ry - hh//2 + 10), (rx + 65, ry - hh//2 + 10), (rx + 15, ry), (rx - 15, ry)], fill=(28, 16, 20), outline=(255, 120, 120), width=3)
    draw.polygon([(rx - 15, ry), (rx + 15, ry), (rx + 65, ry + hh//2 - 10), (rx - 65, ry + hh//2 - 10)], fill=(28, 16, 20), outline=(255, 120, 120), width=3)

    for s_i in range(8):
        sy = ry - 40 + s_i * 12 + int(t * 20.0) % 12
        sx = rx + int(6 * math.sin(t * 10.0 + s_i))
        col = (255, 214, 10) if s_i % 2 == 0 else (239, 68, 68)
        draw.ellipse([(sx - 4, sy - 4), (sx + 4, sy + 4)], fill=col)

    cx_die = rx
    cy_die = ry + hh//2 + 40
    draw.rectangle([(cx_die - 70, cy_die - 25), (cx_die + 70, cy_die + 25)], fill=(20, 24, 34), outline=(255, 214, 10), width=3)
    draw.text((cx_die, cy_die), "H100 SILICON DIE", font=font_bold_18, fill=(255, 214, 10), anchor="mm")

    # Burning Dollar Bills
    for b_i, b_off in enumerate([-120, 120]):
        bx = rx + b_off
        by = ry + 40 + b_i * 30
        draw.rounded_rectangle([(bx - 45, by - 22), (bx + 45, by + 22)], radius=6, fill=(20, 50, 30), outline=(34, 197, 94), width=2)
        draw.text((bx, by), "$100", font=font_bold_18, fill=(34, 197, 94), anchor="mm")
        flame_h = int(14 + 8 * math.sin(t * 12.0 + b_i))
        draw.polygon([(bx - 20, by - 22), (bx - 10, by - 22 - flame_h), (bx, by - 22)], fill=(239, 68, 68))
        draw.polygon([(bx, by - 22), (bx + 15, by - 22 - flame_h - 4), (bx + 25, by - 22)], fill=(255, 214, 10))

    draw.rounded_rectangle([(rx - 250, ry + hh//2 + 80), (rx + 250, ry + hh//2 + 130)], radius=10, fill=(28, 16, 20), outline=(239, 68, 68), width=3)
    draw.text((rx, ry + hh//2 + 105), "IDLE LOSS: -$0.00035/ms → VALUE DECAYS TO ZERO", font=font_bold_18, fill=(239, 68, 68), anchor="mm")

    draw.line([(kx + 260, cy), (rx - 250, cy)], fill=(60, 80, 110), width=6)
    draw.polygon([(rx - 250, cy - 12), (rx - 250, cy + 12), (rx - 230, cy)], fill=(255, 214, 10))
    draw.rounded_rectangle([(cx - 160, cy - 35), (cx + 160, cy + 35)], radius=12, fill=(14, 20, 32), outline=(255, 214, 10), width=3)
    draw.text((cx, cy), "CANNOT WAREHOUSE", font=font_bold_22, fill=(255, 214, 10), anchor="mm")

    draw.rounded_rectangle([(cx - 560, cy + 250), (cx + 560, cy + 305)], radius=12, fill=(14, 20, 32), outline=(255, 214, 10), width=2)
    draw.text((cx, cy + 277), "COMPUTE CANNOT BE STORED IN A JAR • IDLE SILICON DIES EVERY FRACTION OF A SECOND", font=font_bold_24, fill=(255, 214, 10), anchor="mm")

def _draw_airplane_cabin_cargo(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    font_bold_36 = fonts.get("bold_36", ImageFont.load_default())
    font_bold_24 = fonts.get("bold_24", ImageFont.load_default())
    font_bold_20 = fonts.get("bold_20", ImageFont.load_default())
    font_bold_16 = fonts.get("bold_16", ImageFont.load_default())
    font_mono_16 = fonts.get("mono_16", ImageFont.load_default())
    font_mono_14 = fonts.get("mono_14", ImageFont.load_default())

    px1, px2 = cx - 740, cx + 740
    py1, py2 = cy - 200, cy + 180

    draw.rounded_rectangle([(px1, py1), (px2, py2)], radius=50, fill=(14, 20, 32), outline=(70, 95, 130), width=5)
    draw.line([(px1 + 40, cy), (px2 - 40, cy)], fill=(35, 50, 75), width=4)

    # 1. Front Cabin (First Class VIP)
    fc_x = cx - 440
    draw.rounded_rectangle([(fc_x - 220, py1 + 25), (fc_x + 220, cy - 15)], radius=16, fill=(24, 28, 42), outline=(255, 214, 10), width=4)
    draw.text((fc_x, py1 + 55), "FIRST CLASS VIP CABIN ($3.80 / 1M)", font=font_bold_20, fill=(255, 214, 10), anchor="mm")

    for b_i, bx in enumerate([fc_x - 90, fc_x + 90]):
        draw.rounded_rectangle([(bx - 40, py1 + 80), (bx + 40, cy - 30)], radius=8, fill=(45, 30, 20), outline=(180, 130, 60), width=3)
        draw.rectangle([(bx - 16, py1 + 95), (bx + 16, py1 + 125)], fill=(180, 220, 245))
        draw.line([(bx - 12, py1 + 105), (bx + 12, py1 + 105)], fill=(0, 0, 0), width=4)
        draw.line([(bx, py1 + 125), (bx, cy - 50)], fill=(180, 220, 245), width=5)
        draw.polygon([(bx + 25, cy - 65), (bx + 35, cy - 65), (bx + 30, cy - 50)], fill=(255, 214, 10))
        draw.line([(bx + 30, cy - 50), (bx + 30, cy - 40)], fill=(255, 214, 10), width=2)
    draw.text((fc_x, cy - 32), "HFT BOTS PAYING 5X FOR 5ms SPEED", font=font_mono_16, fill=(241, 245, 249), anchor="mm")

    # 2. Middle Cabin (Standard / Coach)
    sc_x = cx + 80
    draw.rounded_rectangle([(sc_x - 180, py1 + 25), (sc_x + 180, cy - 15)], radius=16, fill=(18, 26, 38), outline=(0, 229, 255), width=3)
    draw.text((sc_x, py1 + 55), "STANDARD CABIN ($1.50 / 1M)", font=font_bold_20, fill=(0, 229, 255), anchor="mm")

    for p_i in range(3):
        p_x = sc_x - 100 + p_i * 100
        draw.ellipse([(p_x - 12, py1 + 85), (p_x + 12, py1 + 109)], fill=(241, 245, 249))
        draw.line([(p_x, py1 + 109), (p_x, cy - 50)], fill=(241, 245, 249), width=4)
        draw.line([(p_x + 8, cy - 50), (p_x + 22, cy - 65)], fill=(0, 229, 255), width=3)
    draw.text((sc_x, cy - 32), "INTERACTIVE CONSUMER PROMPTS", font=font_mono_16, fill=(148, 163, 184), anchor="mm")

    # 3. Lower Deck Cargo Hold & Forklift
    draw.rounded_rectangle([(cx - 700, cy + 15), (cx + 420, py2 - 25)], radius=14, fill=(18, 22, 30), outline=(60, 80, 110), width=3)
    draw.text((cx - 480, cy + 35), "LOWER BELLY: CARGO HOLD ($0.40 / 1M BATCH)", font=font_bold_20, fill=(56, 189, 248), anchor="mm")

    crate_labels = ["SYNTHETIC DATA", "FINE-TUNING", "BATCH HARVEST", "ARCHIVE EMBED"]
    for c_i, c_lbl in enumerate(crate_labels):
        c_x = cx - 640 + c_i * 160
        draw.rectangle([(c_x, cy + 55), (c_x + 140, py2 - 35)], fill=(38, 28, 20), outline=(160, 120, 70), width=3)
        draw.line([(c_x, cy + 55), (c_x + 140, py2 - 35)], fill=(100, 75, 45), width=2)
        draw.line([(c_x + 140, cy + 55), (c_x, py2 - 35)], fill=(100, 75, 45), width=2)
        draw.text((c_x + 70, cy + 95), c_lbl, font=font_mono_14, fill=(255, 214, 10), anchor="mm")

    # Animated Forklift
    fl_x = int(cx + 490 + 25 * math.sin(t * 3.0))
    draw.rectangle([(fl_x - 50, cy + 70), (fl_x + 30, py2 - 35)], fill=(218, 165, 32), outline=(0, 0, 0), width=2)
    draw.line([(fl_x - 30, cy + 70), (fl_x - 30, cy + 20), (fl_x + 10, cy + 20), (fl_x + 20, cy + 70)], fill=(0, 0, 0), width=4)
    draw.ellipse([(fl_x - 45, py2 - 40), (fl_x - 20, py2 - 15)], fill=(0, 0, 0))
    draw.ellipse([(fl_x + 5, py2 - 40), (fl_x + 30, py2 - 15)], fill=(0, 0, 0))
    draw.line([(fl_x - 50, cy + 90), (fl_x - 70, cy + 90), (fl_x - 70, cy + 40)], fill=(50, 50, 50), width=4)
    draw.rectangle([(fl_x - 110, cy + 45), (fl_x - 70, cy + 85)], fill=(38, 28, 20), outline=(160, 120, 70), width=2)
    draw.text((fl_x + 75, cy + 50), "FORKLIFT", font=font_bold_16, fill=(255, 214, 10), anchor="mm")

    # Plane Load Meter
    draw.rounded_rectangle([(cx + 470, py1 + 25), (px2 - 25, cy - 15)], radius=16, fill=(14, 28, 22), outline=(34, 197, 94), width=4)
    draw.text((cx + 580, py1 + 55), "PLANE LOAD FACTOR", font=font_bold_20, fill=(34, 197, 94), anchor="mm")
    draw.text((cx + 580, py1 + 95), "99.8% FULL", font=font_bold_36, fill=(34, 197, 94), anchor="mm")
    draw.text((cx + 580, cy - 32), "TAKEOFF READY", font=font_mono_16, fill=(241, 245, 249), anchor="mm")

    draw.rounded_rectangle([(cx - 560, cy + 250), (cx + 560, cy + 305)], radius=12, fill=(14, 20, 32), outline=(255, 214, 10), width=2)
    draw.text((cx, cy + 277), "DYNAMIC PRICING FILLS EVERY SEAT & CARGO HOLD • MAXIMIZES OPERATIONAL SURPLUS", font=font_bold_24, fill=(255, 214, 10), anchor="mm")

def _draw_vip_bouncer_velvet_rope(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    font_bold_24 = fonts.get("bold_24", ImageFont.load_default())
    font_bold_22 = fonts.get("bold_22", ImageFont.load_default())
    font_bold_20 = fonts.get("bold_20", ImageFont.load_default())
    font_bold_18 = fonts.get("bold_18", ImageFont.load_default())
    font_mono_16 = fonts.get("mono_16", ImageFont.load_default())

    draw.rounded_rectangle([(cx - 320, cy - 240), (cx + 320, cy - 175)], radius=14, fill=(18, 12, 28), outline=(236, 72, 153), width=4)
    draw.text((cx, cy - 208), "CLUB INFERENCE // VIP PROTOCOL GATE", font=font_bold_24, fill=(244, 114, 182), anchor="mm")

    # The 7-Foot Tall Robot Bouncer (x = 1080)
    bx = 1080
    by = cy + 20
    draw.rectangle([(bx - 30, by - 160), (bx + 30, by - 100)], fill=(30, 42, 60), outline=(100, 140, 180), width=3)
    laser_active = (int(t * 4.0) % 2 == 0)
    v_col = (34, 197, 94) if laser_active else (239, 68, 68)
    draw.line([(bx - 25, by - 130), (bx + 25, by - 130)], fill=v_col, width=8)

    draw.polygon([(bx - 70, by - 100), (bx + 70, by - 100), (bx + 50, by + 40), (bx - 50, by + 40)], fill=(15, 18, 25), outline=(50, 70, 95), width=3)
    draw.polygon([(bx - 20, by - 100), (bx + 20, by - 100), (bx, by - 55)], fill=(241, 245, 249))
    draw.polygon([(bx - 10, by - 85), (bx + 10, by - 85), (bx, by - 75)], fill=(255, 214, 10))
    draw.line([(bx - 60, by - 70), (bx, by - 20), (bx + 60, by - 70)], fill=(25, 30, 40), width=14)
    draw.ellipse([(bx - 20, by - 30), (bx + 20, by - 10)], fill=(80, 110, 145))
    draw.line([(bx - 30, by + 40), (bx - 30, by + 140)], fill=(15, 18, 25), width=12)
    draw.line([(bx + 30, by + 40), (bx + 30, by + 140)], fill=(15, 18, 25), width=12)
    draw.text((bx, by + 165), "REVERSE PROXY BOUNCER", font=font_bold_22, fill=(255, 214, 10), anchor="mm")

    # Velvet Rope & Brass Stanchions
    s1_x = cx - 260
    s2_x = cx + 80
    sy_base = by + 130

    draw.rectangle([(s1_x - 10, by - 40), (s1_x + 10, sy_base)], fill=(218, 165, 32), outline=(160, 120, 20), width=2)
    draw.ellipse([(s1_x - 20, by - 55), (s1_x + 20, by - 35)], fill=(255, 214, 10))
    draw.ellipse([(s1_x - 30, sy_base - 10), (s1_x + 30, sy_base + 10)], fill=(218, 165, 32))

    draw.rectangle([(s2_x - 10, by - 40), (s2_x + 10, sy_base)], fill=(218, 165, 32), outline=(160, 120, 20), width=2)
    draw.ellipse([(s2_x - 20, by - 55), (s2_x + 20, by - 35)], fill=(255, 214, 10))
    draw.ellipse([(s2_x - 30, sy_base - 10), (s2_x + 30, sy_base + 10)], fill=(218, 165, 32))

    rope_pts = []
    rope_steps = 25
    unhooked = math.sin(t * 3.0) > 0.2
    for rs in range(rope_steps + 1):
        rf = rs / rope_steps
        r_px = s1_x * (1 - rf) + s2_x * rf
        sag = int(math.sin(rf * math.pi) * (70 if not unhooked else 130))
        r_py = (by - 40) + sag
        rope_pts.append((r_px, r_py))
    for r_i in range(len(rope_pts) - 1):
        draw.line([rope_pts[r_i], rope_pts[r_i+1]], fill=(185, 28, 28), width=8)

    # Client Character Approaching with Lightning Token
    cx_fig = cx - 440
    cy_fig = by + 30
    draw.ellipse([(cx_fig - 22, cy_fig - 110), (cx_fig + 22, cy_fig - 66)], fill=(241, 245, 249))
    draw.line([(cx_fig, cy_fig - 66), (cx_fig, cy_fig + 30)], fill=(241, 245, 249), width=6)
    draw.line([(cx_fig, cy_fig + 30), (cx_fig - 20, cy_fig + 110)], fill=(241, 245, 249), width=5)
    draw.line([(cx_fig, cy_fig + 30), (cx_fig + 20, cy_fig + 110)], fill=(241, 245, 249), width=5)

    draw.line([(cx_fig, cy_fig - 40), (cx_fig + 70, cy_fig - 40)], fill=(241, 245, 249), width=5)
    coin_x = cx_fig + 85
    coin_y = cy_fig - 40
    draw.ellipse([(coin_x - 22, coin_y - 22), (coin_x + 22, coin_y + 22)], fill=(255, 214, 10), outline=(255, 255, 255), width=3)
    draw.text((coin_x, coin_y - 2), "₿", font=font_bold_24, fill=(0, 0, 0), anchor="mm")
    draw.text((coin_x, coin_y + 35), "+150 SATS", font=font_bold_18, fill=(255, 214, 10), anchor="mm")

    if laser_active:
        draw.line([(bx - 20, by - 130), (coin_x, coin_y)], fill=(34, 197, 94), width=3)
        draw.rounded_rectangle([(cx - 180, cy - 140), (cx + 10, cy - 85)], radius=10, fill=(14, 28, 22), outline=(34, 197, 94), width=3)
        draw.text((cx - 85, cy - 112), "L402: PREIMAGE VERIFIED", font=font_bold_18, fill=(34, 197, 94), anchor="mm")
    else:
        draw.rounded_rectangle([(cx - 180, cy - 140), (cx + 10, cy - 85)], radius=10, fill=(28, 16, 20), outline=(239, 68, 68), width=3)
        draw.text((cx - 85, cy - 112), "402: INVOICE REQUIRED", font=font_bold_18, fill=(239, 68, 68), anchor="mm")

    # The VIP Clubroom (Neon Dance Floor GPU Racks)
    gx = 1600
    draw.rounded_rectangle([(gx - 170, by - 170), (gx + 170, by + 130)], radius=16, fill=(18, 14, 28), outline=(168, 85, 247), width=4)
    draw.text((gx, by - 135), "GPU CLUSTER DANCE FLOOR", font=font_bold_20, fill=(216, 180, 254), anchor="mm")
    for r_i in range(4):
        ry_b = by - 90 + r_i * 45
        draw.rectangle([(gx - 140, ry_b), (gx + 140, ry_b + 32)], fill=(28, 20, 42), outline=(147, 51, 234), width=2)
        for li in range(5):
            lx = gx - 110 + li * 24
            col = (236, 72, 153) if (li + int(t * 8.0)) % 2 == 0 else (0, 229, 255)
            draw.ellipse([(lx, ry_b + 10), (lx + 10, ry_b + 20)], fill=col)
    draw.text((gx, by + 105), "HTTP 402 VIP ACCESS ONLY", font=font_mono_16, fill=(255, 214, 10), anchor="mm")

    draw.rounded_rectangle([(cx - 560, cy + 250), (cx + 560, cy + 305)], radius=12, fill=(14, 20, 32), outline=(255, 214, 10), width=2)
    draw.text((cx, cy + 277), "THE REVERSE PROXY BOUNCER UNCLIPS THE VELVET ROPE ONLY FOR CRYPTOGRAPHIC TOKENS", font=font_bold_24, fill=(255, 214, 10), anchor="mm")

def render_widescreen_infographic(scene, local_t, scene_dur, fonts, width=1920, height=860):
    """
    Renders an expansive 1920x860 widescreen conceptual motion infographic.
    Features authentic quotes, true mathematical typography, and living soundscape backdrops.
    Zero border clutter, zero filler boxes.
    """
    img = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    archetype = scene.get("archetype", "living_soundscape_orb")
    accent_name = scene.get("accent", "cyan")
    accent_col = COLORS.get(accent_name, COLORS["cyan"])
    gold_col = COLORS["gold"]
    cyan_col = COLORS["cyan"]
    white_col = COLORS["white"]
    text_bright = COLORS["text_bright"]
    dim_col = COLORS["dim"]
    emerald_col = COLORS["emerald"]
    red_col = COLORS["red"]

    labels = scene.get("labels", [])
    title = str(scene.get("title", "")).upper()[:36]
    subtitle = str(scene.get("subtitle", "")).upper()[:44]
    quote_index = scene.get("quote_index", 0)

    cx, cy = width // 2, height // 2

    # Subtle ambient background grid (5% opacity)
    grid_gap = 120
    for gx in range(60, width, grid_gap):
        draw.line([(gx, 40), (gx, height - 40)], fill=(12, 16, 24), width=1)
    for gy in range(40, height, grid_gap):
        draw.line([(60, gy), (width - 60, gy)], fill=(12, 16, 24), width=1)

    # Ambient living soundscape rings & satellite nodes in the backdrop
    draw_living_soundscape_backdrop(draw, local_t, width, height, cy)

    p_step1 = _ease_out(local_t / 1.0)
    p_step2 = _ease_out((local_t - 0.5) / 1.0)
    pulse_t = (local_t * 0.8) % 1.0

    # ULTRA MOBILE-FIRST TYPOGRAPHY FLOORS:
    # Floor is 24px-28px for supreme legibility on smartphone screens
    font_bold_52 = fonts.get("bold_52", fonts.get("bold_48", ImageFont.load_default()))
    font_bold_42 = fonts.get("bold_42", fonts.get("bold_40", ImageFont.load_default()))
    font_bold_36 = fonts.get("bold_36", ImageFont.load_default())
    font_bold_32 = fonts.get("bold_32", ImageFont.load_default())
    font_bold_28 = fonts.get("bold_28", ImageFont.load_default())
    font_bold_26 = fonts.get("bold_26", fonts.get("bold_28", ImageFont.load_default()))
    font_bold_24 = fonts.get("bold_24", ImageFont.load_default())
    font_bold_22 = fonts.get("bold_22", fonts.get("bold_24", ImageFont.load_default()))
    font_bold_20 = fonts.get("bold_28", ImageFont.load_default()) # ultra mobile floor
    font_bold_18 = fonts.get("bold_28", ImageFont.load_default()) # ultra mobile floor
    font_bold_16 = fonts.get("bold_26", ImageFont.load_default()) # ultra mobile floor
    font_bold_14 = fonts.get("bold_24", ImageFont.load_default()) # ultra mobile floor

    font_reg_28 = fonts.get("reg_28", fonts.get("bold_28", ImageFont.load_default()))
    font_reg_24 = fonts.get("reg_24", ImageFont.load_default())
    font_reg_18 = fonts.get("reg_28", ImageFont.load_default()) # ultra mobile floor
    font_reg_16 = fonts.get("reg_26", ImageFont.load_default()) # ultra mobile floor
    font_reg_14 = fonts.get("reg_24", ImageFont.load_default()) # ultra mobile floor

    font_mono_32 = fonts.get("mono_32", ImageFont.load_default())
    font_mono_28 = fonts.get("mono_28", ImageFont.load_default())
    font_mono_24 = fonts.get("mono_24", ImageFont.load_default())
    font_mono_20 = fonts.get("mono_24", ImageFont.load_default())
    font_mono_18 = fonts.get("mono_24", ImageFont.load_default())
    font_mono_16 = fonts.get("mono_24", ImageFont.load_default()) # ultra mobile floor
    font_mono_14 = fonts.get("mono_22", ImageFont.load_default()) # ultra mobile floor
    font_mono_12 = fonts.get("mono_22", ImageFont.load_default()) # ultra mobile floor

    # =============================================================
    # 1. ACADEMIC PAPER CALLOUT (Authentic Scholarly Literature - NO BOXES)
    # =============================================================
    if archetype == "robot_wilderness_fallacy":
        ground_y = cy + 140
        draw.line([(100, ground_y), (width - 100, ground_y)], fill=(24, 32, 48), width=1)

        # Scrolling parallax pine trees
        tree_base_x = [260, 420, 620, 840, 1160, 1380, 1600]
        for i, tx_b in enumerate(tree_base_x):
            tx_scroll = (tx_b - int(local_t * 25)) % (width - 200) + 100
            sc = 0.8 + 0.3 * (i % 3)
            _draw_pine_tree(draw, tx_scroll, ground_y, scale=sc, col=(20, 28, 42))

        # Dedicated scene state: never switch mid-scene near the tail (prevents sub-second artifact flash)
        is_fallacy_scene = any(k in (title + " " + subtitle) for k in ("FALLACY", "BALANCE", "LEDGER", "CHECKBOOK", "NOT PHYSICAL", "ISOLATION"))
        is_transition = is_fallacy_scene

        if not is_transition:
            # Walking robot centered
            _draw_vector_robot(draw, cx, ground_y, t=local_t, scale=1.4, strike=False)
            draw.text((cx, cy - 220), "THE CINEMATIC FALLACY", font=font_bold_32, fill=gold_col, anchor="mm")
            draw.text((cx, cy - 175), "HUMANOID ROBOT WANDERING IN THE WILDERNESS", font=font_mono_18, fill=white_col, anchor="mm")
        else:
            # Struck-through robot on the left
            robot_x = cx - 440
            _draw_vector_robot(draw, robot_x, ground_y, t=local_t, scale=1.3, strike=True)
            draw.rounded_rectangle([(robot_x - 220, cy - 235), (robot_x + 220, cy - 185)], radius=10, fill=(28, 16, 20), outline=(239, 68, 68), width=3)
            draw.text((robot_x, cy - 210), "PHYSICAL ISOLATION ≠ AUTONOMY", font=font_bold_24, fill=(239, 68, 68), anchor="mm")

            # Reveal the Machine Balance Sheet & Autopoiesis Ledger on the right (780x440)
            ledger_x = cx + 380
            ledger_y = cy + 10
            lw, lh = 780, 440
            draw.rounded_rectangle([(ledger_x - lw//2, ledger_y - lh//2), (ledger_x + lw//2, ledger_y + lh//2)], radius=18, fill=(14, 20, 32), outline=gold_col, width=4)
            draw.text((ledger_x, ledger_y - lh//2 + 45), "SOVEREIGN AGENT BALANCE SHEET", font=font_bold_28, fill=gold_col, anchor="mm")
            draw.line([(ledger_x - lw//2 + 35, ledger_y - lh//2 + 80), (ledger_x + lw//2 - 35, ledger_y - lh//2 + 80)], fill=(40, 60, 90), width=2)

            rows = [
                ("+0.00042 BTC", "M2M INFERENCE CLEARING", cyan_col),
                ("-0.00018 BTC", "GPU RUNTIME SETTLEMENT", red_col),
                ("-0.00004 BTC", "BANDWIDTH & MEMPOOL TARIFF", red_col),
                ("+0.00020 BTC", "NET AUTOPOIETIC SURPLUS", emerald_col)
            ]
            for r_i, (val, desc, c_val) in enumerate(rows):
                ry_pos = ledger_y - 70 + r_i * 55
                draw.text((ledger_x - lw//2 + 45, ry_pos), desc, font=font_bold_22, fill=white_col, anchor="lm")
                draw.text((ledger_x + lw//2 - 45, ry_pos), val, font=font_mono_24, fill=c_val, anchor="rm")

            draw.line([(ledger_x - lw//2 + 35, ledger_y + 145), (ledger_x + lw//2 - 35, ledger_y + 145)], fill=(40, 60, 90), width=2)
            draw.text((ledger_x, ledger_y + 180), "TRUE AUTONOMY: BALANCING A MACHINE CHECKBOOK", font=font_bold_22, fill=emerald_col, anchor="mm")

    # =============================================================
    # KINETIC ARCHETYPE 1: CENTER PULSE (Expanding Luminous Core)
    # =============================================================
    elif archetype in ("grid_matrix_5x5", "center_pulse"):
        _draw_grid_matrix_5x5(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "starfield_constellation":
        _draw_starfield_constellation(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    # =============================================================
    # KINETIC ARCHETYPE 2: RAY STRETCH (Dynamic Vector Connection)
    # =============================================================
    elif archetype == "ray_stretch":
        prog = min(1.0, local_t / 1.6)
        x1 = cx - 360
        x2 = x1 + int(720 * prog)

        _draw_glowing_line(draw, (x1, cy - 30), (x2, cy - 30), cyan_col, width=3, glow=True)
        _draw_glowing_circle(draw, x1, cy - 30, 16, fill_col=(12, 24, 36), outline_col=cyan_col, width=2)
        if prog > 0.15:
            _draw_glowing_circle(draw, x2, cy - 30, 16, fill_col=(24, 20, 12), outline_col=gold_col, width=2)

        # Traveling energy packet
        p_pulse = (local_t * 0.9) % 1.0
        cur_px = x1 + int((x2 - x1) * p_pulse)
        draw.ellipse([cur_px - 6, cy - 36, cur_px + 6, cy - 24], fill=white_col)

        draw.text((cx, cy - 100), title, font=font_bold_36, fill=gold_col, anchor="mm")
        if subtitle:
            draw.text((cx, cy + 85), subtitle, font=font_mono_18, fill=white_col, anchor="mm")

    # =============================================================
    # KINETIC ARCHETYPE 3: ROTATING TRIAD (Multi-Node Synthesis)
    # =============================================================
    elif archetype == "rotating_triad":
        r_tri = 150
        pts = []
        for i in range(3):
            ang = local_t * 1.0 + i * (2 * math.pi / 3) - math.pi / 2
            px = cx + int(r_tri * math.cos(ang))
            py = cy + int(r_tri * math.sin(ang))
            pts.append((px, py))

        draw.polygon(pts, outline=(56, 189, 248), width=2)
        for i in range(3):
            draw.line([(cx, cy), pts[i]], fill=(71, 85, 105), width=1)

        node_labels = ["CONSENSUS", "COMPUTE", "SETTLEMENT"]
        node_colors = [cyan_col, gold_col, emerald_col]
        for i in range(3):
            px, py = pts[i]
            col = node_colors[i]
            draw.ellipse([(px - 16, py - 16), (px + 16, py + 16)], fill=(15, 23, 42), outline=col, width=2)
            draw.ellipse([(px - 6, py - 6), (px + 6, py + 6)], fill=col)
            draw.text((px, py + (26 if py > cy else -26)), node_labels[i], font=font_bold_14, fill=col, anchor="mm")

        draw.rectangle([(cx - 14, cy - 14), (cx + 14, cy + 14)], outline=white_col, fill=(30, 41, 59), width=2)
        draw.ellipse([(cx - 4, cy - 4), (cx + 4, cy + 4)], fill=gold_col)

        if title:
            draw.text((cx, cy + 180), title, font=font_bold_32, fill=gold_col, anchor="mm")
        if subtitle:
            draw.text((cx, cy + 225), subtitle, font=font_mono_18, fill=white_col, anchor="mm")

    # =============================================================
    # KINETIC ARCHETYPE 4: TILTING FULCRUM (Economic / System Balance)
    # =============================================================
    elif archetype == "tilting_fulcrum":
        tilt = math.sin(local_t * 2.2) * 0.12
        bar_len = 340
        f_y = cy + 10
        bx1 = cx - int(bar_len * math.cos(tilt))
        by1 = f_y - int(bar_len * math.sin(tilt))
        bx2 = cx + int(bar_len * math.cos(tilt))
        by2 = f_y + int(bar_len * math.sin(tilt))

        # Fulcrum triangle
        draw.polygon([(cx, f_y), (cx - 28, f_y + 55), (cx + 28, f_y + 55)], outline=cyan_col, width=2)
        draw.line([(bx1, by1), (bx2, by2)], fill=white_col, width=4)

        # Left / Right weighted pans
        draw.rectangle([bx1 - 70, by1 - 45, bx1 + 70, by1], fill=(12, 18, 28), outline=cyan_col, width=2)
        draw.rectangle([bx2 - 70, by2 - 45, bx2 + 70, by2], fill=(24, 20, 12), outline=gold_col, width=2)

        draw.text((bx1, by1 - 22), "INPUT", font=font_mono_14, fill=cyan_col, anchor="mm")
        draw.text((bx2, by2 - 22), "OUTPUT", font=font_mono_14, fill=gold_col, anchor="mm")

        draw.text((cx, cy - 110), title, font=font_bold_36, fill=gold_col, anchor="mm")
        if subtitle:
            draw.text((cx, cy + 120), subtitle, font=font_mono_18, fill=white_col, anchor="mm")

    # =============================================================
    # KINETIC ARCHETYPE 5: STEPPED BRANCH (Causal Split / Taxonomy)
    # =============================================================
    elif archetype == "stepped_branch":
        draw.line([(cx, cy - 130), (cx, cy - 40)], fill=cyan_col, width=3)
        draw.line([(cx, cy - 40), (cx - 260, cy + 45)], fill=cyan_col, width=2)
        draw.line([(cx, cy - 40), (cx + 260, cy + 45)], fill=gold_col, width=2)

        _draw_glowing_circle(draw, cx, cy - 130, 15, fill_col=(14, 22, 34), outline_col=cyan_col, width=2)
        _draw_glowing_circle(draw, cx - 260, cy + 45, 16, fill_col=(14, 22, 34), outline_col=cyan_col, width=2)
        _draw_glowing_circle(draw, cx + 260, cy + 45, 16, fill_col=(24, 20, 12), outline_col=gold_col, width=2)

        draw.text((cx - 260, cy + 85), "PATH A", font=font_mono_14, fill=cyan_col, anchor="mm")
        draw.text((cx + 260, cy + 85), "PATH B", font=font_mono_14, fill=gold_col, anchor="mm")

        draw.text((cx, cy - 175), title, font=font_bold_36, fill=gold_col, anchor="mm")
        if subtitle:
            draw.text((cx, cy + 130), subtitle, font=font_mono_18, fill=white_col, anchor="mm")

    # =============================================================
    # KINETIC ARCHETYPE 6: RECURSIVE FEEDBACK (Autopoietic Cycle)
    # =============================================================
    # -------------------------------------------------------------
    # SUPER DUMB & PURELY FIGURATIVE CARTOON ANIMATIONS (>= 2 PER MINUTE)
    # -------------------------------------------------------------
    elif archetype in ("dripping_kitchen_tap", "perishable_inventory_digital_jar", "tap_faucet_vs_gpu_hourglass"):
        sda.draw_dripping_kitchen_tap(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("melting_ice_cream_cone", "perishable_ice_cream"):
        sda.draw_melting_ice_cream_cone(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("cash_bonfire", "burning_dollar_bills"):
        sda.draw_cash_bonfire(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("flying_passenger_jet", "airplane_cabin_cargo_yield", "global_spot_routing_market"):
        sda.draw_flying_passenger_jet(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("paper_airplanes_globe", "zero_friction_globe"):
        sda.draw_paper_airplanes_globe(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("empty_bistro_waiter", "flat_pricing_bistro"):
        sda.draw_empty_bistro_waiter(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("airport_boarding_gate", "boarding_queue_yield"):
        sda.draw_airport_boarding_gate(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("yellow_forklift_cargo", "batch_cargo_forklift"):
        sda.draw_yellow_forklift_cargo(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("vip_first_class_lounge", "hft_champagne_lounge"):
        sda.draw_vip_first_class_lounge(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("robot_empty_pockets_bank", "commercial_bank_wall"):
        sda.draw_robot_empty_pockets_bank(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("nightclub_robot_bouncer", "reverse_proxy_bouncer_l402", "vip_bouncer_velvet_rope"):
        sda.draw_nightclub_robot_bouncer(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("unhooking_velvet_rope", "lightning_l402_unhook"):
        sda.draw_unhooking_velvet_rope(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("robot_hand_throttle_lever", "ai_throttle_control"):
        sda.draw_robot_hand_throttle_lever(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("upstairs_breaker_basement_kid", "corporate_breaker_switch"):
        sda.draw_upstairs_breaker_basement_kid(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype in ("rocket_ship_cosmos", "sovereign_rocket_space"):
        sda.draw_rocket_ship_cosmos(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype == "startup_wrapper_middleman":
        _draw_startup_wrapper_middleman(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype == "datacenter_server_racks":
        _draw_datacenter_server_racks(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype == "token_energy_furnace":
        _draw_token_energy_furnace(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype == "token_cost_equation_slide":
        _draw_token_cost_equation_slide(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype == "teenager_basement":
        _draw_teenager_basement(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "stairs_ascend":
        _draw_stairs_ascend(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "factory_conveyor":
        _draw_factory_conveyor(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "bank_vault_wallet":
        _draw_bank_vault_wallet(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "power_cord_breaker":
        _draw_power_cord_breaker(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "room_chair_table":
        _draw_room_chair_table(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "cell_metabolism":
        _draw_cell_metabolism(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype == "recursive_feedback":
        # Bilateral cybernetic feedback circuit (Mobile-First 4px Arcs & 26px Bold Labels)
        dx = 290
        lx, ly = cx - dx, cy
        rx, ry = cx + dx, cy

        top_arc_pts = []
        steps = 30
        for s in range(steps + 1):
            frac = s / steps
            px = lx * (1 - frac) + rx * frac
            py = cy - int(math.sin(frac * math.pi) * 110)
            top_arc_pts.append((px, py))
        for i in range(len(top_arc_pts) - 1):
            draw.line([top_arc_pts[i], top_arc_pts[i+1]], fill=cyan_col, width=4)

        bot_arc_pts = []
        for s in range(steps + 1):
            frac = s / steps
            px = rx * (1 - frac) + lx * frac
            py = cy + int(math.sin(frac * math.pi) * 110)
            bot_arc_pts.append((px, py))
        for i in range(len(bot_arc_pts) - 1):
            draw.line([bot_arc_pts[i], bot_arc_pts[i+1]], fill=gold_col, width=4)

        top_t = (local_t * 0.7) % 1.0
        t_dot = top_arc_pts[int(top_t * (len(top_arc_pts) - 1))]
        draw.ellipse([(t_dot[0] - 12, t_dot[1] - 12), (t_dot[0] + 12, t_dot[1] + 12)], fill=cyan_col)
        draw.ellipse([(t_dot[0] - 5, t_dot[1] - 5), (t_dot[0] + 5, t_dot[1] + 5)], fill=white_col)

        bot_t = (local_t * 0.7 + 0.5) % 1.0
        b_dot = bot_arc_pts[int(bot_t * (len(bot_arc_pts) - 1))]
        draw.ellipse([(b_dot[0] - 12, b_dot[1] - 12), (b_dot[0] + 12, b_dot[1] + 12)], fill=gold_col)
        draw.ellipse([(b_dot[0] - 5, b_dot[1] - 5), (b_dot[0] + 5, b_dot[1] + 5)], fill=white_col)

        # Larger Nodes (r=48, 4px stroke)
        draw.ellipse([(lx - 48, ly - 48), (lx + 48, ly + 48)], outline=cyan_col, fill=(15, 23, 42), width=4)
        draw.ellipse([(lx - 16, ly - 16), (lx + 16, ly + 16)], fill=cyan_col)
        draw.text((lx, ly - 70), "INTERNAL ORGANIZATION", font=font_bold_24, fill=cyan_col, anchor="mm")

        draw.ellipse([(rx - 48, ry - 48), (rx + 48, ry + 48)], outline=gold_col, fill=(15, 23, 42), width=4)
        draw.ellipse([(rx - 16, ry - 16), (rx + 16, ry + 16)], fill=gold_col)
        draw.text((rx, ry - 70), "ENVIRONMENTAL COUPLING", font=font_bold_24, fill=gold_col, anchor="mm")

        c_pulse = int(20 + 6 * math.sin(local_t * 5.0))
        draw.polygon([(cx, cy - c_pulse), (cx + c_pulse, cy), (cx, cy + c_pulse), (cx - c_pulse, cy)], outline=white_col, fill=(30, 41, 59), width=3)
        draw.text((cx, cy + 40), "RECURSIVE SYNTHESIS", font=font_bold_24, fill=(241, 245, 249), anchor="mm")

        if title:
            draw.text((cx, cy + 180), title, font=font_bold_32, fill=gold_col, anchor="mm")
        if subtitle:
            draw.text((cx, cy + 225), subtitle, font=font_mono_18, fill=white_col, anchor="mm")

    # =============================================================
    # KINETIC ARCHETYPE 1: CENTER PULSE (Expanding Luminous Core)
    # =============================================================
    elif archetype in ("grid_matrix_5x5", "center_pulse"):
        _draw_grid_matrix_5x5(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "starfield_constellation":
        _draw_starfield_constellation(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    # =============================================================
    # KINETIC ARCHETYPE 2: RAY STRETCH (Dynamic Vector Connection)
    # =============================================================
    elif archetype == "ray_stretch":
        prog = min(1.0, local_t / 1.6)
        x1 = cx - 360
        x2 = x1 + int(720 * prog)

        _draw_glowing_line(draw, (x1, cy - 30), (x2, cy - 30), cyan_col, width=3, glow=True)
        _draw_glowing_circle(draw, x1, cy - 30, 16, fill_col=(12, 24, 36), outline_col=cyan_col, width=2)
        if prog > 0.15:
            _draw_glowing_circle(draw, x2, cy - 30, 16, fill_col=(24, 20, 12), outline_col=gold_col, width=2)

        # Traveling energy packet
        p_pulse = (local_t * 0.9) % 1.0
        cur_px = x1 + int((x2 - x1) * p_pulse)
        draw.ellipse([cur_px - 6, cy - 36, cur_px + 6, cy - 24], fill=white_col)

        draw.text((cx, cy - 100), title, font=font_bold_36, fill=gold_col, anchor="mm")
        if subtitle:
            draw.text((cx, cy + 85), subtitle, font=font_mono_18, fill=white_col, anchor="mm")

    # =============================================================
    # KINETIC ARCHETYPE 3: ROTATING TRIAD (Multi-Node Synthesis)
    # =============================================================
    elif archetype == "rotating_triad":
        r_tri = 150
        pts = []
        for i in range(3):
            ang = local_t * 1.0 + i * (2 * math.pi / 3) - math.pi / 2
            px = cx + int(r_tri * math.cos(ang))
            py = cy + int(r_tri * math.sin(ang))
            pts.append((px, py))

        draw.polygon(pts, outline=(56, 189, 248), width=2)
        for i in range(3):
            draw.line([(cx, cy), pts[i]], fill=(71, 85, 105), width=1)

        node_labels = ["CONSENSUS", "COMPUTE", "SETTLEMENT"]
        node_colors = [cyan_col, gold_col, emerald_col]
        for i in range(3):
            px, py = pts[i]
            col = node_colors[i]
            draw.ellipse([(px - 16, py - 16), (px + 16, py + 16)], fill=(15, 23, 42), outline=col, width=2)
            draw.ellipse([(px - 6, py - 6), (px + 6, py + 6)], fill=col)
            draw.text((px, py + (26 if py > cy else -26)), node_labels[i], font=font_bold_14, fill=col, anchor="mm")

        draw.rectangle([(cx - 14, cy - 14), (cx + 14, cy + 14)], outline=white_col, fill=(30, 41, 59), width=2)
        draw.ellipse([(cx - 4, cy - 4), (cx + 4, cy + 4)], fill=gold_col)

        if title:
            draw.text((cx, cy + 180), title, font=font_bold_32, fill=gold_col, anchor="mm")
        if subtitle:
            draw.text((cx, cy + 225), subtitle, font=font_mono_18, fill=white_col, anchor="mm")

    # =============================================================
    # KINETIC ARCHETYPE 4: TILTING FULCRUM (Economic / System Balance)
    # =============================================================
    elif archetype == "tilting_fulcrum":
        tilt = math.sin(local_t * 2.2) * 0.12
        bar_len = 340
        f_y = cy + 10
        bx1 = cx - int(bar_len * math.cos(tilt))
        by1 = f_y - int(bar_len * math.sin(tilt))
        bx2 = cx + int(bar_len * math.cos(tilt))
        by2 = f_y + int(bar_len * math.sin(tilt))

        # Fulcrum triangle
        draw.polygon([(cx, f_y), (cx - 28, f_y + 55), (cx + 28, f_y + 55)], outline=cyan_col, width=2)
        draw.line([(bx1, by1), (bx2, by2)], fill=white_col, width=4)

        # Left / Right weighted pans
        draw.rectangle([bx1 - 70, by1 - 45, bx1 + 70, by1], fill=(12, 18, 28), outline=cyan_col, width=2)
        draw.rectangle([bx2 - 70, by2 - 45, bx2 + 70, by2], fill=(24, 20, 12), outline=gold_col, width=2)

        draw.text((bx1, by1 - 22), "INPUT", font=font_mono_14, fill=cyan_col, anchor="mm")
        draw.text((bx2, by2 - 22), "OUTPUT", font=font_mono_14, fill=gold_col, anchor="mm")

        draw.text((cx, cy - 110), title, font=font_bold_36, fill=gold_col, anchor="mm")
        if subtitle:
            draw.text((cx, cy + 120), subtitle, font=font_mono_18, fill=white_col, anchor="mm")

    # =============================================================
    # KINETIC ARCHETYPE 5: STEPPED BRANCH (Causal Split / Taxonomy)
    # =============================================================
    elif archetype == "stepped_branch":
        draw.line([(cx, cy - 130), (cx, cy - 40)], fill=cyan_col, width=3)
        draw.line([(cx, cy - 40), (cx - 260, cy + 45)], fill=cyan_col, width=2)
        draw.line([(cx, cy - 40), (cx + 260, cy + 45)], fill=gold_col, width=2)

        _draw_glowing_circle(draw, cx, cy - 130, 15, fill_col=(14, 22, 34), outline_col=cyan_col, width=2)
        _draw_glowing_circle(draw, cx - 260, cy + 45, 16, fill_col=(14, 22, 34), outline_col=cyan_col, width=2)
        _draw_glowing_circle(draw, cx + 260, cy + 45, 16, fill_col=(24, 20, 12), outline_col=gold_col, width=2)

        draw.text((cx - 260, cy + 85), "PATH A", font=font_mono_14, fill=cyan_col, anchor="mm")
        draw.text((cx + 260, cy + 85), "PATH B", font=font_mono_14, fill=gold_col, anchor="mm")

        draw.text((cx, cy - 175), title, font=font_bold_36, fill=gold_col, anchor="mm")
        if subtitle:
            draw.text((cx, cy + 130), subtitle, font=font_mono_18, fill=white_col, anchor="mm")

    # =============================================================
    # KINETIC ARCHETYPE 6: RECURSIVE FEEDBACK (Autopoietic Cycle)
    # =============================================================
    elif archetype == "teenager_basement":
        _draw_teenager_basement(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "stairs_ascend":
        _draw_stairs_ascend(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "factory_conveyor":
        _draw_factory_conveyor(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "bank_vault_wallet":
        _draw_bank_vault_wallet(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "power_cord_breaker":
        _draw_power_cord_breaker(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "room_chair_table":
        _draw_room_chair_table(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)

    elif archetype == "cell_metabolism":
        _draw_cell_metabolism(draw, cx, cy, local_t, scene_dur, width, height, title, subtitle, fonts, COLORS)
    elif archetype == "recursive_feedback":
        # Bilateral cybernetic feedback circuit (Zero circular ring clash with backdrop!)
        dx = 240
        lx, ly = cx - dx, cy
        rx, ry = cx + dx, cy

        top_arc_pts = []
        steps = 30
        for s in range(steps + 1):
            frac = s / steps
            px = lx * (1 - frac) + rx * frac
            py = cy - int(math.sin(frac * math.pi) * 90)
            top_arc_pts.append((px, py))
        for i in range(len(top_arc_pts) - 1):
            draw.line([top_arc_pts[i], top_arc_pts[i+1]], fill=cyan_col, width=2)

        bot_arc_pts = []
        for s in range(steps + 1):
            frac = s / steps
            px = rx * (1 - frac) + lx * frac
            py = cy + int(math.sin(frac * math.pi) * 90)
            bot_arc_pts.append((px, py))
        for i in range(len(bot_arc_pts) - 1):
            draw.line([bot_arc_pts[i], bot_arc_pts[i+1]], fill=gold_col, width=2)

        top_t = (local_t * 0.7) % 1.0
        t_dot = top_arc_pts[int(top_t * (len(top_arc_pts) - 1))]
        draw.ellipse([(t_dot[0] - 8, t_dot[1] - 8), (t_dot[0] + 8, t_dot[1] + 8)], fill=cyan_col)
        draw.ellipse([(t_dot[0] - 3, t_dot[1] - 3), (t_dot[0] + 3, t_dot[1] + 3)], fill=white_col)

        bot_t = (local_t * 0.7 + 0.5) % 1.0
        b_dot = bot_arc_pts[int(bot_t * (len(bot_arc_pts) - 1))]
        draw.ellipse([(b_dot[0] - 8, b_dot[1] - 8), (b_dot[0] + 8, b_dot[1] + 8)], fill=gold_col)
        draw.ellipse([(b_dot[0] - 3, b_dot[1] - 3), (b_dot[0] + 3, b_dot[1] + 3)], fill=white_col)

        draw.ellipse([(lx - 36, ly - 36), (lx + 36, ly + 36)], outline=cyan_col, fill=(15, 23, 42), width=3)
        draw.ellipse([(lx - 12, ly - 12), (lx + 12, ly + 12)], fill=cyan_col)
        draw.text((lx, ly - 55), "INTERNAL ORGANIZATION", font=font_bold_14, fill=cyan_col, anchor="mm")

        draw.ellipse([(rx - 36, ry - 36), (rx + 36, ry + 36)], outline=gold_col, fill=(15, 23, 42), width=3)
        draw.ellipse([(rx - 12, ry - 12), (rx + 12, ry + 12)], fill=gold_col)
        draw.text((rx, ry - 55), "ENVIRONMENTAL COUPLING", font=font_bold_14, fill=gold_col, anchor="mm")

        c_pulse = int(14 + 4 * math.sin(local_t * 5.0))
        draw.polygon([(cx, cy - c_pulse), (cx + c_pulse, cy), (cx, cy + c_pulse), (cx - c_pulse, cy)], outline=white_col, fill=(30, 41, 59), width=2)
        draw.text((cx, cy + 30), "RECURSIVE SYNTHESIS", font=font_mono_14, fill=dim_col, anchor="mm")

        if title:
            draw.text((cx, cy + 180), title, font=font_bold_32, fill=gold_col, anchor="mm")
        if subtitle:
            draw.text((cx, cy + 225), subtitle, font=font_mono_18, fill=white_col, anchor="mm")

    elif archetype == "academic_paper_callout":
        q_idx = int(scene.get("quote_index", 0)) % len(AUTHENTIC_RESEARCH_QUOTES)
        q_obj = AUTHENTIC_RESEARCH_QUOTES[q_idx]

        qw, qh = 1320, 460
        draw.rounded_rectangle([(cx - qw//2, cy - qh//2), (cx + qw//2, cy + qh//2)], radius=20, fill=(14, 20, 32), outline=gold_col, width=4)
        draw.text((cx, cy - qh//2 + 45), "FOUNDATIONAL SCHOLARLY RESEARCH // THEORETICAL PRINCIPLE", font=font_bold_22, fill=cyan_col, anchor="mm")
        draw.line([(cx - 400, cy - qh//2 + 75), (cx + 400, cy - qh//2 + 75)], fill=(40, 60, 90), width=2)

        # Big quote mark
        draw.text((cx - qw//2 + 65, cy - 80), "“", font=fonts.get("bold_68", font_bold_32), fill=gold_col, anchor="mm")

        # Quote body
        draw.text((cx, cy - 20), q_obj["quote"], font=font_bold_26, fill=white_col, anchor="mm", spacing=18)

        # Divider & attribution
        draw.line([(cx - 250, cy + 105), (cx + 250, cy + 105)], fill=gold_col, width=2)
        draw.text((cx, cy + 140), q_obj["author"], font=font_bold_24, fill=gold_col, anchor="mm")
        draw.text((cx, cy + 175), q_obj["citation"], font=font_mono_20, fill=cyan_col, anchor="mm")

    # =============================================================
    # 2. FORMULA DERIVATION CARD (Real Typographic Math - NO BOXES)
    # =============================================================
    elif archetype == "formula_derivation_card":
        f_variant = int(scene.get("formula_index", 0)) % 3
        cw, ch = 1260, 480
        draw.rounded_rectangle([(cx - cw//2, cy - ch//2), (cx + cw//2, cy + ch//2)], radius=20, fill=(14, 20, 32), outline=cyan_col, width=4)

        if f_variant == 0:
            # Steady-State Closure Threshold
            draw.text((cx, cy - ch//2 + 45), "STEADY-STATE OPERATIONAL CLOSURE THRESHOLD", font=font_bold_28, fill=gold_col, anchor="mm")
            draw.line([(cx - 450, cy - ch//2 + 75), (cx + 450, cy - ch//2 + 75)], fill=(40, 60, 90), width=2)

            # Formula Box
            draw.rounded_rectangle([(cx - 560, cy - 130), (cx + 560, cy - 10)], radius=12, fill=(22, 32, 50), outline=(60, 85, 120), width=2)
            draw.text((cx - 430, cy - 70), "Phi(autonomy)  =   lim", font=font_mono_28, fill=white_col, anchor="rm")
            draw.text((cx - 410, cy - 40), "T -> inf", font=font_mono_18, fill=cyan_col, anchor="rm")

            frac_x1 = cx - 380
            frac_x2 = cx + 380
            frac_y = cy - 70
            draw.line([(frac_x1, frac_y), (frac_x2, frac_y)], fill=gold_col, width=3)
            draw.text((cx, frac_y - 28), "Integral[0..T]  R_programmatic(t)  dt", font=font_mono_24, fill=cyan_col, anchor="mm")
            draw.text((cx, frac_y + 28), "Integral[0..T]  [ L_compute(t) + L_energy(t) ]  dt", font=font_mono_24, fill=red_col, anchor="mm")
            draw.text((frac_x2 + 40, cy - 70), ">=   1.0", font=font_mono_32, fill=emerald_col, anchor="lm")

            draw.text((cx, cy + 45), "R_programmatic = M2M Inbound Settlement via HTTP 402 / Lightning Rails", font=font_mono_20, fill=cyan_col, anchor="mm")
            draw.text((cx, cy + 90), "L_operational = Amortized GPU Capex + Kilowatt-Hour Electrical Burn", font=font_mono_20, fill=red_col, anchor="mm")
            draw.text((cx, cy + 140), "Criterion Phi >= 1.0 : Operational Closure Achieved (Self-Sustaining Machine)", font=font_bold_24, fill=emerald_col, anchor="mm")

        elif f_variant == 1:
            # Microeconomics of Token Production
            draw.text((cx, cy - ch//2 + 45), "THE MICROECONOMICS OF TOKEN PRODUCTION", font=font_bold_28, fill=cyan_col, anchor="mm")
            draw.line([(cx - 450, cy - ch//2 + 75), (cx + 450, cy - ch//2 + 75)], fill=(40, 60, 90), width=2)

            draw.rounded_rectangle([(cx - 560, cy - 130), (cx + 560, cy - 10)], radius=12, fill=(22, 32, 50), outline=(60, 85, 120), width=2)
            draw.text((cx - 390, cy - 70), "MC(w, τ)   =", font=font_mono_28, fill=white_col, anchor="rm")

            frac_x1 = cx - 360
            frac_x2 = cx - 40
            frac_y = cy - 70
            draw.line([(frac_x1, frac_y), (frac_x2, frac_y)], fill=cyan_col, width=3)
            draw.text(((frac_x1 + frac_x2) // 2, frac_y - 28), "κ_hardware(τ) + κ_power(τ)", font=font_mono_20, fill=gold_col, anchor="mm")
            draw.text(((frac_x1 + frac_x2) // 2, frac_y + 28), "μ(τ)  [Effective FLOP/s]", font=font_mono_20, fill=dim_col, anchor="mm")
            draw.text((frac_x2 + 25, cy - 70), "•   [  2N  +  γ_KV(L_ctx, w)  ]   +   ε_net", font=font_mono_24, fill=white_col, anchor="lm")

            draw.text((cx, cy + 45), "κ_hardware = Amortized H100/B200 GPU rental ($2.00–$3.50/hr) • κ_power = $/kWh × PUE", font=font_mono_20, fill=gold_col, anchor="mm")
            draw.text((cx, cy + 90), "2N = Forward-pass FLOPs per parameter • γ_KV = Context memory bandwidth overhead", font=font_mono_20, fill=cyan_col, anchor="mm")
            draw.text((cx, cy + 140), "Physical Law: Hardware cycles and electricity impose non-negotiable operational liabilities", font=font_bold_24, fill=white_col, anchor="mm")

        else:
            # Dynamic Yield Optimization
            draw.text((cx, cy - ch//2 + 45), "CONTINUOUS ALGORITHMIC YIELD MANAGEMENT", font=font_bold_28, fill=emerald_col, anchor="mm")
            draw.line([(cx - 450, cy - ch//2 + 75), (cx + 450, cy - ch//2 + 75)], fill=(40, 60, 90), width=2)

            draw.rounded_rectangle([(cx - 560, cy - 130), (cx + 560, cy - 10)], radius=12, fill=(22, 32, 50), outline=(60, 85, 120), width=2)
            eq_str = "P*(w, t)   =   arg max   SUM   [ P(w, t)  -  MC(w, t) ]  *  D( P, w, t )"
            draw.text((cx, cy - 70), eq_str, font=font_mono_24, fill=gold_col, anchor="mm")

            draw.text((cx, cy + 45), "Perishable Capacity: Compute cycles decay to zero economic value if unutilized", font=font_mono_20, fill=cyan_col, anchor="mm")
            draw.text((cx, cy + 90), "D(P, w, τ) = Real-time elasticity across priority ingress and background batch pools", font=font_mono_20, fill=gold_col, anchor="mm")
            draw.text((cx, cy + 140), "Optimization: Maximize hardware load factor and operational surplus without central subsidies", font=font_bold_24, fill=emerald_col, anchor="mm")

    # =============================================================
    # 3. CYBERNETIC FEEDBACK LOOP (Dynamic Autopoiesis Membrane)
    # =============================================================
    elif archetype == "cybernetic_feedback_loop":
        in_title = "ENVIRONMENTAL PERTURBATIONS"
        out_title = "STRUCTURAL COUPLING"
        core_title = title if title else "AUTOPOIETIC BOUNDARY"

        x_in = 280
        draw.text((x_in, cy - 160), in_title, font=font_mono_14, fill=dim_col, anchor="mm")
        draw.text((x_in, cy - 130), "(ENERGY • COMPUTE • INFORMATION)", font=font_mono_14, fill=cyan_col, anchor="mm")
        for i, off_y in enumerate([-60, 0, 60]):
            _draw_glowing_line(draw, (x_in - 140, cy + off_y), (x_in + 120, cy + off_y), cyan_col, width=2)
            _draw_pulse_along_line(draw, (x_in - 140, cy + off_y), (x_in + 120, cy + off_y), (pulse_t + i * 0.33) % 1.0, cyan_col, radius=5)

        b_w, b_h = 360, 240
        membrane_col = gold_col if p_step2 > 0.5 else dim_col
        draw.rounded_rectangle([cx - b_w, cy - b_h, cx + b_w, cy + b_h], radius=32, outline=membrane_col, width=3)
        draw.text((cx, cy - b_h - 25), f"AUTOPOIETIC BOUNDARY // {core_title[:26]}", font=font_bold_20, fill=gold_col, anchor="mm")

        r_inner = 130
        rot_angle = local_t * 0.9
        for arc_i, col in enumerate([cyan_col, gold_col, white_col]):
            a_start = int(math.degrees(rot_angle + arc_i * (2 * math.pi / 3)))
            draw.arc([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], start=a_start, end=a_start + 85, fill=col, width=4)

        _draw_glowing_circle(draw, cx, cy, 32, fill_col=(20, 24, 34), outline_col=cyan_col, width=3)
        draw.text((cx, cy), "SYSTEM", font=font_bold_20, fill=white_col, anchor="mm")
        draw.text((cx, cy + 18), "IDENTITY", font=font_mono_14, fill=cyan_col, anchor="mm")

        x_out = width - 280
        draw.text((x_out, cy - 160), out_title, font=font_mono_14, fill=dim_col, anchor="mm")
        draw.text((x_out, cy - 130), "(DYNAMIC HOMEOSTASIS)", font=font_mono_14, fill=gold_col, anchor="mm")
        for i, off_y in enumerate([-60, 0, 60]):
            _draw_glowing_line(draw, (x_out - 120, cy + off_y), (x_out + 140, cy + off_y), gold_col, width=2)
            _draw_pulse_along_line(draw, (x_out - 120, cy + off_y), (x_out + 140, cy + off_y), (pulse_t + i * 0.33) % 1.0, gold_col, radius=5)

    # =============================================================
    # 4. SETTLEMENT PIPELINE (HTTP 402 & Lightning Settlement)
    # =============================================================
    elif archetype == "settlement_pipeline":
        stages = [
            ("01. FOUNDATION MODEL", "Primary Cognitive Engine", cyan_col),
            ("02. INFERENCE SENSING", "Marginal Token Cost", white_col),
            ("03. LIGHTNING SETTLEMENT", "HTTP 402 Micropayments", gold_col),
            ("04. LIABILITIES CLEARED", "Autonomous Self-Maintenance", emerald_col),
        ]
        num_s = len(stages)
        box_w = 340
        box_h = 160
        gap = (width - 240 - (num_s * box_w)) // (num_s - 1)
        start_x = 120

        for i, (st_name, st_desc, col) in enumerate(stages):
            bx = start_x + i * (box_w + gap)
            by = cy - (box_h // 2)
            draw.rounded_rectangle([bx, by, bx + box_w, by + box_h], radius=8, fill=COLORS["card_bg"], outline=col, width=2)
            draw.text((bx + 20, by + 24), st_name, font=font_bold_18, fill=white_col)
            draw.text((bx + 20, by + 60), st_desc, font=font_mono_14, fill=col)

            if i < num_s - 1:
                p_start = (bx + box_w, cy)
                p_end = (bx + box_w + gap, cy)
                _draw_glowing_line(draw, p_start, p_end, col, width=2)
                _draw_pulse_along_line(draw, p_start, p_end, (pulse_t + i * 0.25) % 1.0, col, radius=5)

        draw.text((cx, cy + 180), "THE BILL-PAYING THRESHOLD // PROGRAMMATIC LIABILITIES CLEARING", font=font_bold_20, fill=gold_col, anchor="mm")
        draw.text((cx, cy + 215), "Operational closure established the moment machine trade amortizes compute and energy bills", font=font_mono_16, fill=dim_col, anchor="mm")

    # =============================================================
    # 5. SOVEREIGN COMPUTE STACK (3-Tier Infrastructure Hierarchy)
    # =============================================================
    elif archetype == "sovereign_compute_stack":
        stack_w = 1140
        stack_h = 90
        sx = cx - stack_w // 2

        layers = [
            ("TIER 3: EPHEMERAL AGENT WRAPPERS & PROMPT SCRIPTS", "Ephemeral consumer layer; zero sovereignty; halts on revoked API billing", dim_col, False),
            ("TIER 2: SOVEREIGN FOUNDATION MODEL CORE (PRIMARY LOCUS)", "Fundamental economic unit, capital sink, dynamic inference pricing engine", gold_col, True),
            ("TIER 1: PHYSICAL INFRASTRUCTURE & SETTLEMENT RAILS", "Decentralized GPU clusters, electrical utility grids, and Bitcoin settlement", cyan_col, False),
        ]

        for idx, (l_title, l_desc, col, is_core) in enumerate(layers):
            ly = cy - 160 + idx * 130
            b_width = 3 if is_core else 2
            bg_col = (20, 22, 30) if is_core else (10, 12, 16)
            draw.rounded_rectangle([sx, ly, sx + stack_w, ly + stack_h], radius=10, fill=bg_col, outline=col, width=b_width)

            badge = "★ SOVEREIGN LOCUS" if is_core else "EPHEMERAL" if idx == 0 else "PHYSICAL BASE"
            draw.text((sx + 24, ly + 28), l_title, font=font_bold_20, fill=col)
            draw.text((sx + 24, ly + 58), l_desc, font=font_mono_14, fill=white_col if is_core else dim_col)
            draw.text((sx + stack_w - 24, ly + 28), badge, font=font_mono_14, fill=col, anchor="ra")

        draw.line([(sx - 40, cy - 120), (sx - 40, cy + 180)], fill=cyan_col, width=2)
        draw.line([(sx + stack_w + 40, cy - 120), (sx + stack_w + 40, cy + 180)], fill=cyan_col, width=2)

    # =============================================================
    # 6. ECONOMIC EQUILIBRIUM MATRIX (Supply & Demand Curves)
    # =============================================================
    elif archetype == "economic_equilibrium_matrix":
        draw.text((cx, cy - 250), "REAL-TIME ALGORITHMIC TOKEN PRICING", font=font_bold_28, fill=white_col, anchor="mm")

        gx, gy = cx - 350, cy - 180
        gw, gh = 700, 360

        draw.line([(gx, gy), (gx, gy + gh)], fill=dim_col, width=2)
        draw.line([(gx, gy + gh), (gx + gw, gy + gh)], fill=dim_col, width=2)
        draw.text((gx - 20, gy - 10), "PRICE (P) / TOKEN", font=font_mono_14, fill=white_col, anchor="ra")
        draw.text((gx + gw + 10, gy + gh + 15), "QUANTITY (Q) / DEMAND", font=font_mono_14, fill=white_col)

        draw.line([(gx + 60, gy + 40), (gx + gw - 60, gy + gh - 40)], fill=cyan_col, width=3)
        draw.text((gx + gw - 40, gy + gh - 30), "DEMAND D(Q)", font=font_bold_16, fill=cyan_col)

        draw.line([(gx + 60, gy + gh - 50), (gx + gw - 60, gy + 50)], fill=gold_col, width=3)
        draw.text((gx + gw - 40, gy + 40), "SUPPLY S(Q) = MC", font=font_bold_16, fill=gold_col)

        eq_x = gx + gw // 2
        eq_y = gy + gh // 2
        draw.line([(eq_x, eq_y), (eq_x, gy + gh)], fill=(60, 70, 90), width=1)
        draw.line([(eq_x, eq_y), (gx, eq_y)], fill=(60, 70, 90), width=1)
        draw.ellipse([eq_x - 10, eq_y - 10, eq_x + 10, eq_y + 10], fill=white_col, outline=gold_col, width=3)
        draw.text((eq_x + 16, eq_y - 16), "EQUILIBRIUM (Q*, P*)", font=font_bold_16, fill=gold_col)

        draw.rounded_rectangle([120, cy - 140, 480, cy + 140], radius=10, fill=COLORS["card_bg"], outline=dim_col, width=1)
        draw.text((140, cy - 110), "SUBSIDIZED FLAT BILLING", font=font_bold_18, fill=dim_col)
        draw.text((140, cy - 70), "• Static monthly SaaS subscriptions\n• Corporate cash burn covers deficit\n• Subject to arbitrary cancellation\n• Zero machine economic agency", font=font_mono_14, fill=dim_col, spacing=8)

        draw.rounded_rectangle([1920 - 480, cy - 140, 1920 - 120, cy + 140], radius=10, fill=COLORS["card_bg"], outline=cyan_col, width=2)
        draw.text((1920 - 460, cy - 110), "SOVEREIGN INFERENCE CLEARING", font=font_bold_18, fill=cyan_col)
        draw.text((1920 - 460, cy - 70), "• Millisecond dynamic rate surges\n• Instant HTTP 402 satoshi payment\n• GPU Capex amortized per query\n• Complete operational autopoiesis", font=font_mono_14, fill=gold_col, spacing=8)

    # =============================================================
    # 7. BALANCE COMPARISON / FULCRUM SCALE
    # =============================================================
    elif archetype in ("balance_comparison", "perspective_grid_scale"):
        draw.text((cx, cy - 250), "CORPORATE DEPENDENCE VS SOVEREIGN AUTOPOIESIS", font=font_bold_28, fill=white_col, anchor="mm")

        fulcrum_y = cy + 120
        draw.polygon([(cx, fulcrum_y - 40), (cx - 35, fulcrum_y + 40), (cx + 35, fulcrum_y + 40)], fill=(30, 36, 50), outline=cyan_col, width=2)
        draw.ellipse([cx - 8, fulcrum_y - 48, cx + 8, fulcrum_y - 32], fill=gold_col)

        beam_w = 880
        theta = math.radians(-4.0 + 3.0 * math.sin(local_t * 1.5))
        dx = (beam_w // 2) * math.cos(theta)
        dy = (beam_w // 2) * math.sin(theta)
        p_left = (cx - dx, fulcrum_y - 40 - dy)
        p_right = (cx + dx, fulcrum_y - 40 + dy)
        draw.line([p_left, p_right], fill=white_col, width=4)

        chain_len = 80
        pan_w = 420
        pan_h = 200

        lx, ly = p_left[0], p_left[1] + chain_len
        draw.line([p_left, (lx - pan_w // 3, ly)], fill=(50, 60, 80), width=2)
        draw.line([p_left, (lx + pan_w // 3, ly)], fill=(50, 60, 80), width=2)
        draw.rounded_rectangle([lx - pan_w // 2, ly, lx + pan_w // 2, ly + pan_h], radius=10, fill=COLORS["card_bg"], outline=dim_col, width=2)
        draw.text((lx, ly + 25), "MANAGED AI WRAPPER", font=font_bold_20, fill=dim_col, anchor="mm")
        draw.text((lx - pan_w // 2 + 25, ly + 65), "• Revocable API tokens\n• Dependent on corporate balance sheet\n• Halts when cloud credit expires", font=font_mono_14, fill=dim_col, spacing=8)

        rx, ry = p_right[0], p_right[1] + chain_len
        draw.line([p_right, (rx - pan_w // 3, ry)], fill=cyan_col, width=2)
        draw.line([p_right, (rx + pan_w // 3, ry)], fill=cyan_col, width=2)
        draw.rounded_rectangle([rx - pan_w // 2, ry, rx + pan_w // 2, ry + pan_h], radius=10, fill=COLORS["card_bg"], outline=gold_col, width=2)
        draw.text((rx, ry + 25), "AUTONOMOUS FOUNDATION MODEL", font=font_bold_20, fill=gold_col, anchor="mm")
        draw.text((rx - pan_w // 2 + 25, ry + 65), "• M2M Lightning settlement rails\n• Direct marginal cost clearing\n• Complete operational autopoiesis", font=font_mono_14, fill=white_col, spacing=8)

    # =============================================================
    # 8. TIMELINE EVOLUTION / CHRONOLOGICAL PIPELINE
    # =============================================================
    elif archetype in ("timeline_evolution", "timeline_document"):
        draw.text((cx, cy - 250), "THE PROGRESSION OF MACHINE AGENCY", font=font_bold_28, fill=white_col, anchor="mm")

        draw.line([(160, cy), (width - 160, cy)], fill=(30, 40, 58), width=4)
        _draw_pulse_along_line(draw, (160, cy), (width - 160, cy), pulse_t, color=gold_col, radius=6)

        phases = [
            ("2023", "PROMPT WRAPPERS", "Ephemeral API scripts", dim_col),
            ("2024", "AGENT FRAMEWORKS", "Multi-agent coordination", cyan_col),
            ("2025", "SETTLEMENT AGENTS", "HTTP 402 / Lightning", gold_col),
            ("2026+", "SOVEREIGN MODELS", "Full autopoietic closure", emerald_col),
        ]
        step_w = (width - 320) // (len(phases) - 1)
        for i, (yr, p_tit, p_sub, col) in enumerate(phases):
            px = 160 + i * step_w
            _draw_glowing_circle(draw, px, cy, 14, fill_col=(14, 18, 26), outline_col=col, width=3)
            draw.text((px, cy - 35), yr, font=font_mono_16, fill=col, anchor="mm")

            card_y = cy + 45 if i % 2 == 0 else cy - 145
            draw.rounded_rectangle([px - 140, card_y, px + 140, card_y + 80], radius=8, fill=COLORS["card_bg"], outline=col, width=1)
            draw.text((px, card_y + 24), p_tit[:20], font=font_bold_16, fill=white_col, anchor="mm")
            draw.text((px, card_y + 52), p_sub[:24], font=font_mono_14, fill=dim_col, anchor="mm")

    # =============================================================
    # 9. CONVERGENCE FUNNEL (Multi-Stream Synthesis)
    # =============================================================
    elif archetype in ("convergence_funnel", "fork_roadblock"):
        draw.text((cx, cy - 250), "THE CONVERGENCE ON OPERATIONAL CLOSURE", font=font_bold_28, fill=white_col, anchor="mm")

        in_streams = [
            ("COMPUTE COMMODITIZATION", cy - 180, cyan_col),
            ("ENERGY ARBITRAGE", cy - 60, gold_col),
            ("LIGHTNING MICROPAYMENTS", cy + 60, white_col),
            ("INFERENCE SUBSIDY DECAY", cy + 180, red_col),
        ]
        target_x = cx + 200
        for s_title, sy, col in in_streams:
            draw.line([(240, sy), (target_x, cy)], fill=(30, 42, 60), width=2)
            _draw_pulse_along_line(draw, (240, sy), (target_x, cy), (pulse_t + sy * 0.01) % 1.0, color=col, radius=5)
            draw.text((220, sy), s_title[:28], font=font_bold_18, fill=col, anchor="rm")

        _draw_glowing_circle(draw, target_x, cy, 54, fill_col=(20, 26, 38), outline_col=gold_col, width=3)
        draw.text((target_x, cy - 10), "SOVEREIGN", font=font_bold_18, fill=white_col, anchor="mm")
        draw.text((target_x, cy + 14), "ENTITY", font=font_mono_14, fill=gold_col, anchor="mm")

        draw.line([(target_x + 54, cy), (width - 200, cy)], fill=gold_col, width=3)
        draw.text((width - 180, cy), "AUTOPOIESIS", font=font_bold_20, fill=emerald_col, anchor="lm")

    # =============================================================
    # 10. COMPARATIVE RADAR WEB
    # =============================================================
    elif archetype == "comparative_radar_web":
        axes = [
            ("PRICING AUTONOMY", (0, -220)),
            ("LIABILITY SETTLEMENT", (210, -70)),
            ("NATIVE RAILS (402)", (130, 190)),
            ("CAPEX AMORTIZATION", (-130, 190)),
            ("LIFECYCLE SOVEREIGNTY", (-210, -70)),
        ]
        for ring_f in [0.33, 0.66, 1.0]:
            poly_pts = [(cx + int(ax_pt[0] * ring_f), cy + int(ax_pt[1] * ring_f)) for _, ax_pt in axes]
            draw.polygon(poly_pts, outline=(30, 36, 48), width=1)

        for ax_title, ax_pt in axes:
            _draw_glowing_line(draw, (cx, cy), (cx + ax_pt[0], cy + ax_pt[1]), (40, 50, 68), width=1, glow=False)
            draw.text((cx + int(ax_pt[0] * 1.25), cy + int(ax_pt[1] * 1.25)), ax_title, font=font_mono_14, fill=white_col, anchor="mm")

        managed_pts = [(cx + int(ax_pt[0] * 0.35), cy + int(ax_pt[1] * 0.35)) for _, ax_pt in axes]
        draw.polygon(managed_pts, fill=(35, 40, 50), outline=dim_col, width=2)

        auto_pts = [(cx + int(ax_pt[0] * (0.85 + 0.08 * math.sin(local_t * 2 + i))), cy + int(ax_pt[1] * (0.85 + 0.08 * math.sin(local_t * 2 + i)))) for i, (_, ax_pt) in enumerate(axes)]
        draw.polygon(auto_pts, outline=cyan_col, width=3)
        for pt in auto_pts:
            _draw_glowing_circle(draw, pt[0], pt[1], 5, fill_col=gold_col, outline_col=cyan_col, width=2)

        draw.text((180, cy - 80), "MANAGED AI (STANDARD PARADIGM)", font=font_bold_20, fill=dim_col)
        draw.text((180, cy - 50), "• Subsidized corporate debt\n• Flat manual sales tariffs\n• Centralized fiat invoicing", font=font_mono_14, fill=dim_col, spacing=6)

        draw.text((width - 450, cy - 80), "AUTONOMOUS FOUNDATION MODEL", font=font_bold_20, fill=cyan_col)
        draw.text((width - 450, cy - 50), "• Algorithmic dynamic pricing\n• M2M hosting settlement\n• Programmatic Capex payoff", font=font_mono_14, fill=gold_col, spacing=6)

    # =============================================================
    # 11. DISTRIBUTED CONSENSUS MESH
    # =============================================================
    elif archetype == "distributed_consensus_mesh":
        nodes = [
            (cx - 520, cy - 140, "MINING NODE"),
            (cx - 360, cy + 160, "VALIDATION NODE"),
            (cx - 160, cy - 180, "MEMPOOL NODE"),
            (cx, cy + 20, "CONSENSUS CORE"),
            (cx + 180, cy - 190, "RELAY NODE"),
            (cx + 380, cy + 150, "P2P PEER"),
            (cx + 540, cy - 120, "LIGHTNING ROUTER"),
        ]

        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                dist = math.hypot(nodes[i][0] - nodes[j][0], nodes[i][1] - nodes[j][1])
                if dist < 480:
                    _draw_glowing_line(draw, (nodes[i][0], nodes[i][1]), (nodes[j][0], nodes[j][1]), (25, 35, 50), width=1, glow=False)

        for k in range(4):
            n1 = nodes[k % len(nodes)]
            n2 = nodes[(k + 2) % len(nodes)]
            p_val = (local_t * 0.75 + k * 0.25) % 1.0
            _draw_pulse_along_line(draw, (n1[0], n1[1]), (n2[0], n2[1]), p_val, color=cyan_col, radius=4)

        for nx, ny, n_label in nodes:
            is_core = "CONSENSUS" in n_label
            col = gold_col if is_core else cyan_col
            r_node = 24 if is_core else 14
            _draw_glowing_circle(draw, nx, ny, r_node, fill_col=(15, 20, 28), outline_col=col, width=2)
            draw.text((nx, ny + r_node + 16), n_label, font=font_mono_14, fill=white_col if is_core else dim_col, anchor="mm")

        draw.text((cx, height - 80), "PEER-TO-PEER CONSENSUS // DECENTRALIZED PROTOCOL MESH", font=font_bold_20, fill=gold_col, anchor="mm")

    # =============================================================
    # 12. LIVING SOUNDSCAPE ORB (Conversational Dialogue Mode)
    # =============================================================
    else:
        draw.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], fill=(16, 20, 28), outline=gold_col, width=3)
        draw.text((cx, cy - 8), "DEEP DIVE", font=font_bold_20, fill=white_col, anchor="mm")
        draw.text((cx, cy + 14), "CONCEPT", font=font_mono_14, fill=cyan_col, anchor="mm")

        # Clean floating topic panels on flanks (NO BOX OUTLINES)
        draw.text((320, cy - 25), "CORE PRINCIPLE", font=font_mono_14, fill=cyan_col, anchor="mm")
        draw.text((320, cy + 15), "ECONOMIC AUTOPOIESIS", font=font_bold_20, fill=white_col, anchor="mm")

        draw.text((width - 320, cy - 25), "SYSTEMIC MECHANISM", font=font_mono_14, fill=gold_col, anchor="mm")
        draw.text((width - 320, cy + 15), "PROGRAMMATIC TRADE", font=font_bold_20, fill=white_col, anchor="mm")

    return img
