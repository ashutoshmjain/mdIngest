import os
import sys
import json
import math
import time
import glob
import hashlib
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

# Color palettes (RGB)
COLORS = {
    "white": (255, 255, 255),
    "gold": (255, 214, 10),
    "red": (255, 59, 48),
    "cyan": (0, 229, 255),
    "green": (48, 209, 88),
    "dim": (130, 130, 135),
    "dark_dim": (65, 65, 70),
}

ARCHETYPES = [
    "perspective_grid_scale",
    "split_fracture",
    "triangle_network",
    "radial_constellation",
    "trajectory_curve",
    "ecosystem_cards",
    "fork_roadblock",
    "stepped_pyramid",
    "convergence_funnel",
    "timeline_document",
    "rotating_gear",
    "balance_comparison",
]


def _load_fonts():
    """Load clean geometric sans/mono fonts for spaced uppercase Dan Koe labels."""
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        os.path.join("fonts", "DejaVuSansMono-Bold.ttf"),
        os.path.join("fonts", "DejaVuSansMono.ttf"),
    ]
    font_path = None
    for c in candidates:
        if os.path.exists(c):
            font_path = c
            break

    fonts = {}
    for size in (14, 16, 18, 20, 22, 24, 28, 34, 42):
        try:
            if font_path:
                fonts[size] = ImageFont.truetype(font_path, size)
            else:
                fonts[size] = ImageFont.load_default()
        except Exception:
            fonts[size] = ImageFont.load_default()
    return fonts


def _build_orb_sprites():
    """Pre-render glowing neon orb sprites (RGBA) for instant alpha-compositing."""
    sprites = {}
    for cname, rgb in COLORS.items():
        for radius in (5, 8, 12, 16):
            size = radius * 8
            c = size // 2
            # Core + glow layer
            glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            d_glow = ImageDraw.Draw(glow)
            d_glow.ellipse(
                [c - int(radius * 2.2), c - int(radius * 2.2), c + int(radius * 2.2), c + int(radius * 2.2)],
                fill=(rgb[0], rgb[1], rgb[2], 130),
            )
            glow = glow.filter(ImageFilter.GaussianBlur(radius=radius * 0.95))

            d_core = ImageDraw.Draw(glow)
            d_core.ellipse(
                [c - radius, c - radius, c + radius, c + radius],
                fill=(rgb[0], rgb[1], rgb[2], 255),
            )
            # Bright white hot center
            inner_r = max(2, int(radius * 0.55))
            d_core.ellipse(
                [c - inner_r, c - inner_r, c + inner_r, c + inner_r],
                fill=(255, 255, 255, 255),
            )
            sprites[(cname, radius)] = glow
    return sprites


def _paste_orb(canvas_rgba, sprites, x, y, color_name="white", radius=8, alpha=1.0):
    sprite = sprites.get((color_name, radius)) or sprites.get(("white", 8))
    if alpha <= 0.02:
        return
    if alpha < 0.98:
        r, g, b, a = sprite.split()
        a = a.point(lambda p: int(p * alpha))
        sprite = Image.merge("RGBA", (r, g, b, a))
    half = sprite.width // 2
    canvas_rgba.alpha_composite(sprite, (int(x) - half, int(y) - half))


def _ease_out_cubic(t):
    t = max(0.0, min(1.0, float(t)))
    return 1.0 - pow(1.0 - t, 3)


def _ease_in_out_sine(t):
    t = max(0.0, min(1.0, float(t)))
    return -(math.cos(math.pi * t) - 1.0) / 2.0


def _clamp01(t):
    return max(0.0, min(1.0, float(t)))


def _scale_rgb(rgb, factor):
    factor = max(0.0, min(1.0, float(factor)))
    return (int(rgb[0] * factor), int(rgb[1] * factor), int(rgb[2] * factor))


def _draw_spaced_text(draw, x, y, text, font, fill=(255, 255, 255), spacing=3, align="center"):
    if not text:
        return
    text = str(text).upper().strip()
    chars = list(text)
    widths = []
    max_h = 0
    for ch in chars:
        bbox = draw.textbbox((0, 0), ch, font=font)
        w = max(4, bbox[2] - bbox[0])
        h = bbox[3] - bbox[1]
        widths.append(w)
        if h > max_h:
            max_h = h
    total_w = sum(widths) + spacing * max(0, len(chars) - 1)
    if align == "center":
        curr_x = x - total_w / 2.0
    elif align == "right":
        curr_x = x - total_w
    else:
        curr_x = x
    curr_y = y - max_h / 2.0
    for ch, w in zip(chars, widths):
        draw.text((int(curr_x), int(curr_y)), ch, font=font, fill=fill)
        curr_x += w + spacing


def _draw_progressive_line(draw, p1, p2, progress, fill=(255, 255, 255), width=2):
    progress = _clamp01(progress)
    if progress <= 0.01:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    cx = x1 + (x2 - x1) * progress
    cy = y1 + (y2 - y1) * progress
    draw.line([(int(x1), int(y1)), (int(cx), int(cy))], fill=fill, width=width)
    return (cx, cy)


def _draw_dotted_line(draw, p1, p2, progress, fill=(180, 180, 185), dot_step=8, width=2):
    progress = _clamp01(progress)
    if progress <= 0.01:
        return
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist < 1:
        return
    max_d = dist * progress
    d = 0.0
    while d < max_d:
        t0 = d / dist
        t1 = min(max_d, d + dot_step * 0.45) / dist
        sx, sy = x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0
        ex, ey = x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1
        draw.line([(int(sx), int(sy)), (int(ex), int(ey))], fill=fill, width=width)
        d += dot_step


def _render_scene_frame(scene, local_t, scene_dur, fonts, sprites, width=740, height=740):
    """
    Render a single 740x740 Dan Koe minimalist neon wireframe frame for `scene` at `local_t`.
    Uses fast half-res Gaussian bloom + crisp vector foreground + pre-rendered orb sprites.
    """
    archetype = scene.get("archetype", "triangle_network")
    accent_name = scene.get("accent", "white")
    if accent_name not in COLORS:
        accent_name = "white"
    accent_rgb = COLORS[accent_name]
    white_rgb = COLORS["white"]
    dim_rgb = COLORS["dim"]

    title = str(scene.get("title", "")).upper().strip()
    subtitle = str(scene.get("subtitle", "")).upper().strip()
    labels = [str(l).upper().strip() for l in (scene.get("labels") or []) if str(l).strip()]
    while len(labels) < 4:
        labels.append("")

    # Global fade-in (first 0.35s) and fade-out (last 0.35s)
    fade_in = _clamp01(local_t / 0.35) if local_t < 0.35 else 1.0
    fade_out = _clamp01((scene_dur - local_t) / 0.35) if (scene_dur - local_t) < 0.35 else 1.0
    master_alpha = fade_in * fade_out

    # Step progressions across the scene (complete wireframe reveal within 2.5s)
    p_step1 = _ease_out_cubic(local_t / 0.9)
    p_step2 = _ease_out_cubic((local_t - 0.6) / 0.9)
    p_step3 = _ease_out_cubic((local_t - 1.3) / 1.0)
    p_step4 = _ease_out_cubic((local_t - 2.0) / 1.0)
    t_norm = _clamp01(local_t / max(0.1, scene_dur))

    # Draw crisp vector lines onto RGB image
    vec_img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(vec_img)
    cx, cy = width // 2, height // 2 - 20

    # Collect orbs to composite after glow pass: list of (x, y, color_name, radius, alpha)
    orbs = []

    c_white = _scale_rgb(white_rgb, master_alpha)
    c_accent = _scale_rgb(accent_rgb, master_alpha)
    c_dim = _scale_rgb(dim_rgb, master_alpha)

    if archetype == "perspective_grid_scale":
        # 3D perspective trapezoidal grid + central orb + optional balance scale above
        top_w, bot_w = 240, 360
        gy_top, gy_bot = cy - 40, cy + 120
        rows, cols = 3, 3
        for r in range(rows + 1):
            frac = r / rows
            y = gy_top + (gy_bot - gy_top) * frac
            w_row = top_w + (bot_w - top_w) * frac
            _draw_progressive_line(draw, (cx - w_row / 2, y), (cx + w_row / 2, y), p_step1, fill=c_white, width=2)
        for c_idx in range(cols + 1):
            frac = (c_idx / cols) - 0.5
            x_t = cx + top_w * frac
            x_b = cx + bot_w * frac
            _draw_progressive_line(draw, (x_t, gy_top), (x_b, gy_bot), p_step1, fill=c_white, width=2)

        # Balance scale rising from center of grid (Step 2)
        if p_step2 > 0.05:
            s_col = _scale_rgb(white_rgb, master_alpha * p_step2)
            pillar_top = gy_top - 85 * p_step2
            draw.line([(cx, gy_top + 45), (cx, int(pillar_top))], fill=s_col, width=3)
            beam_w = 190 * p_step2
            tilt = math.sin(local_t * 1.8) * 8.0 * p_step3
            lx, ly = cx - beam_w / 2, pillar_top + 12 - tilt
            rx, ry = cx + beam_w / 2, pillar_top + 12 + tilt
            draw.line([(int(lx), int(ly)), (int(rx), int(ry))], fill=s_col, width=3)
            for px, py in ((lx, ly), (rx, ry)):
                draw.line([(int(px), int(py)), (int(px - 22), int(py + 32))], fill=s_col, width=2)
                draw.line([(int(px), int(py)), (int(px + 22), int(py + 32))], fill=s_col, width=2)
                draw.pieslice([int(px - 24), int(py + 20), int(px + 24), int(py + 44)], 0, 180, fill=s_col)

        orbs.append((cx, gy_top + 52, accent_name if p_step3 > 0.5 else "white", 12, master_alpha * p_step1))
        if title:
            _draw_spaced_text(draw, cx, gy_bot + 52, title, fonts[28], fill=c_white, spacing=6)
        if labels[0] and p_step3 > 0.1:
            _draw_spaced_text(draw, cx, gy_top - 115, labels[0], fonts[16], fill=_scale_rgb(accent_rgb, master_alpha * p_step3), spacing=3)

    elif archetype == "split_fracture":
        # Rectangle splitting into two fractured halves with vertical 90-deg rotated labels
        sep = 12 + 58 * _ease_in_out_sine(_clamp01((local_t - 0.3) / 1.8))
        box_w, box_h = 125, 220
        top_y, bot_y = cy - box_h // 2, cy + box_h // 2
        lx0, lx1 = cx - sep - box_w, cx - sep
        rx0, rx1 = cx + sep, cx + sep + box_w

        # Jagged fracture points
        jags = [0, 14, -10, 16, -8, 12, 0]
        l_pts = [(lx0, top_y), (lx1, top_y)]
        r_pts = [(rx1, top_y), (rx0, top_y)]
        for idx, j in enumerate(jags):
            yy = top_y + (bot_y - top_y) * (idx / (len(jags) - 1))
            l_pts.append((lx1 + j, yy))
            r_pts.append((rx0 + j, yy))
        l_pts.append((lx0, bot_y))
        r_pts.append((rx1, bot_y))

        draw.polygon(l_pts, outline=c_white, width=2)
        draw.polygon(r_pts, outline=c_white, width=2)

        if p_step2 > 0.1:
            lbl_col = _scale_rgb(white_rgb, master_alpha * p_step2)
            for bx_center, txt_lbl, rot_angle in (
                (int(lx0 + box_w * 0.45), (labels[0] or "CORPORATE")[:14], 90),
                (int(rx0 + box_w * 0.55), (labels[1] or "STRUCTURE")[:14], -90),
            ):
                tmp_txt = Image.new("RGB", (200, 40), (0, 0, 0))
                d_tmp = ImageDraw.Draw(tmp_txt)
                _draw_spaced_text(d_tmp, 100, 20, txt_lbl, fonts[16], fill=lbl_col, spacing=3)
                rot_img = tmp_txt.rotate(rot_angle, expand=True)
                vec_img.paste(rot_img, (bx_center - rot_img.width // 2, cy - rot_img.height // 2))

        orb_y = cy + math.sin(local_t * 2.4) * 45
        orbs.append((cx, orb_y, accent_name, 8, master_alpha * p_step1))
        if title and p_step2 > 0.2:
            _draw_spaced_text(draw, cx, bot_y + 55, title, fonts[24], fill=_scale_rgb(accent_rgb, master_alpha * p_step2), spacing=5)

    elif archetype == "triangle_network":
        # 3 nodes in a glowing triangle (like META - INSTAGRAM - WHATSAPP)
        top_pt = (cx, cy - 110)
        left_pt = (cx - 135, cy + 85)
        right_pt = (cx + 135, cy + 85)

        _draw_progressive_line(draw, top_pt, left_pt, p_step1, fill=c_accent, width=3)
        _draw_progressive_line(draw, top_pt, right_pt, p_step2, fill=c_accent, width=3)
        _draw_progressive_line(draw, left_pt, right_pt, p_step3, fill=c_accent, width=3)

        orbs.append((top_pt[0], top_pt[1], accent_name, 12, master_alpha * p_step1))
        if p_step1 > 0.5:
            orbs.append((left_pt[0], left_pt[1], accent_name, 8, master_alpha * p_step2))
        if p_step2 > 0.5:
            orbs.append((right_pt[0], right_pt[1], accent_name, 8, master_alpha * p_step3))

        # Traveling signal pulse along triangle perimeter
        if p_step3 > 0.8:
            cyc = (local_t * 0.65) % 3.0
            pts = [top_pt, right_pt, left_pt, top_pt]
            seg_i = int(cyc)
            seg_f = cyc - seg_i
            px = pts[seg_i][0] + (pts[seg_i + 1][0] - pts[seg_i][0]) * seg_f
            py = pts[seg_i][1] + (pts[seg_i + 1][1] - pts[seg_i][1]) * seg_f
            orbs.append((px, py, "white", 5, master_alpha))

        _draw_spaced_text(draw, top_pt[0], top_pt[1] - 34, labels[0] or title, fonts[18], fill=c_accent, spacing=3)
        if p_step2 > 0.2:
            _draw_spaced_text(draw, left_pt[0] - 10, left_pt[1] + 32, labels[1] or "NODE 1", fonts[16], fill=_scale_rgb(accent_rgb, master_alpha * p_step2), spacing=2)
        if p_step3 > 0.2:
            _draw_spaced_text(draw, right_pt[0] + 10, right_pt[1] + 32, labels[2] or "NODE 2", fonts[16], fill=_scale_rgb(accent_rgb, master_alpha * p_step3), spacing=2)
        if title and title != labels[0] and p_step3 > 0.4:
            _draw_spaced_text(draw, cx, cy + 160, title, fonts[22], fill=c_white, spacing=4)

    elif archetype == "radial_constellation":
        # Central hub with dotted spokes radiating to satellite nodes + bottom label
        angles = [-110, -180, 135, 22, -35]
        radii = [145, 155, 115, 150, 130]
        hub = (cx - 10, cy - 10)
        for idx, (ang_deg, rad) in enumerate(zip(angles, radii)):
            prog = _ease_out_cubic((local_t - idx * 0.45) / 1.1)
            if prog <= 0.02:
                continue
            rad_a = math.radians(ang_deg)
            tx = hub[0] + math.cos(rad_a) * rad
            ty = hub[1] + math.sin(rad_a) * rad
            _draw_dotted_line(draw, hub, (tx, ty), prog, fill=c_dim, dot_step=7, width=2)
            orbs.append((tx, ty, "white" if idx % 2 == 0 else accent_name, 5, master_alpha * prog))
            # Pulse traveling outward
            p_f = ((local_t * 0.7 + idx * 0.2) % 1.0) * prog
            ox = hub[0] + (tx - hub[0]) * p_f
            oy = hub[1] + (ty - hub[1]) * p_f
            orbs.append((ox, oy, accent_name, 5, master_alpha * 0.65 * prog))

        orbs.append((hub[0], hub[1], "white", 8, master_alpha))
        if labels[0] and p_step2 > 0.2:
            _draw_spaced_text(draw, cx + 115, cy - 95, labels[0], fonts[16], fill=_scale_rgb(accent_rgb, master_alpha * p_step2), spacing=2)
        if title:
            _draw_spaced_text(draw, cx, cy + 175, title, fonts[22], fill=c_white, spacing=4)

    elif archetype == "trajectory_curve":
        # Sweeping exponential curve with glowing comet head and apex label
        p0 = (cx - 140, cy + 60)
        p1 = (cx - 20, cy + 20)
        p2 = (cx + 110, cy - 110)
        steps = 45
        max_s = max(2, int(steps * _ease_in_out_sine(_clamp01(local_t / 2.6))))
        pts = []
        for s in range(max_s + 1):
            t = s / steps
            bx = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
            by = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
            pts.append((int(bx), int(by)))
        if len(pts) >= 2:
            draw.line(pts, fill=c_white, width=3)
            head = pts[-1]
            orbs.append((head[0], head[1], accent_name, 8, master_alpha))
        if p_step2 > 0.15:
            lbl = labels[0] or subtitle or "ACCELERATION"
            _draw_spaced_text(draw, p2[0] + 55, p2[1] + 15, lbl, fonts[18], fill=_scale_rgb(white_rgb, master_alpha * p_step2), spacing=2, align="left")
        if title:
            _draw_spaced_text(draw, cx, cy + 175, title, fonts[22], fill=c_white, spacing=4)

    elif archetype == "ecosystem_cards":
        # 3 minimalist icon boxes (like GOOGLE $, APPLE server+lock, FRONTIER chip) + orbiting orb
        cards = [
            (cx - 95, cy - 105, labels[0] or "SYSTEM A", "$"),
            (cx + 105, cy - 20, labels[1] or "SYSTEM B", "LOCK"),
            (cx - 95, cy + 80, labels[2] or "SYSTEM C", "CHIP"),
        ]
        for idx, (bx, by, lbl, icon_type) in enumerate(cards):
            prog = _ease_out_cubic((local_t - idx * 0.7) / 1.1)
            if prog <= 0.05:
                continue
            col = _scale_rgb(white_rgb, master_alpha * prog)
            r = 46
            draw.rectangle([bx - r, by - r, bx + r, by + r], outline=col, width=2)
            if icon_type == "$":
                _draw_spaced_text(draw, bx, by, "$", fonts[34], fill=col, spacing=0)
            elif icon_type == "LOCK":
                for row in (-18, 0, 18):
                    draw.rectangle([bx - 26, by + row - 6, bx + 26, by + row + 6], outline=col, width=1)
                # Padlock on top right corner
                draw.rectangle([bx + 32, by - 46, bx + 52, by - 28], fill=col)
                draw.arc([bx + 35, by - 58, bx + 49, by - 42], 180, 0, fill=col, width=2)
            else:
                draw.rectangle([bx - 24, by - 24, bx + 24, by + 24], outline=col, width=2)
            _draw_spaced_text(draw, bx, by + r + 20, lbl, fonts[14], fill=col, spacing=2)

        # Free glowing orb orbiting near bottom right
        orb_ang = local_t * 1.6
        ox = cx + 85 + math.cos(orb_ang) * 24
        oy = cy + 85 + math.sin(orb_ang) * 24
        orbs.append((ox, oy, accent_name, 12, master_alpha * p_step2))
        if title and p_step3 > 0.2:
            _draw_spaced_text(draw, cx, cy + 185, title, fonts[20], fill=_scale_rgb(accent_rgb, master_alpha * p_step3), spacing=4)

    elif archetype == "fork_roadblock":
        # Vertical stem splitting left (blocked by red X) and right (open path with orb)
        stem_bot = (cx, cy + 165)
        fork_mid = (cx, cy + 25)
        left_mid = (cx - 135, cy + 25)
        left_top = (cx - 135, cy - 65)
        right_mid = (cx + 135, cy + 25)
        right_top = (cx + 135, cy - 65)

        _draw_progressive_line(draw, stem_bot, fork_mid, p_step1, fill=c_white, width=2)
        _draw_progressive_line(draw, fork_mid, left_mid, p_step1, fill=c_white, width=2)
        _draw_progressive_line(draw, left_mid, left_top, p_step2, fill=c_white, width=2)
        _draw_progressive_line(draw, fork_mid, right_mid, p_step2, fill=c_white, width=2)
        _draw_progressive_line(draw, right_mid, right_top, p_step3, fill=c_white, width=2)

        # Red X roadblock on left branch
        if p_step2 > 0.4:
            rx, ry = left_top[0], left_top[1] + 38
            r_col = _scale_rgb(COLORS["red"], master_alpha * p_step2)
            draw.line([(rx - 12, ry - 12), (rx + 12, ry + 12)], fill=r_col, width=3)
            draw.line([(rx - 12, ry + 12), (rx + 12, ry - 12)], fill=r_col, width=3)

        # Labels above branches
        if p_step2 > 0.2:
            _draw_spaced_text(draw, left_top[0], left_top[1] - 28, labels[0] or "BLOCKED PATH", fonts[16], fill=c_white, spacing=2)
        if p_step3 > 0.2:
            _draw_spaced_text(draw, right_top[0], right_top[1] - 28, labels[1] or title or "NEW FRONTIER", fonts[16], fill=c_white, spacing=2)

        # Glowing orb routing along right branch
        orb_t = _clamp01((local_t - 1.0) / 3.0)
        if orb_t < 0.5:
            f = orb_t * 2.0
            ox = fork_mid[0] + (right_mid[0] - fork_mid[0]) * f
            oy = fork_mid[1]
        else:
            f = (orb_t - 0.5) * 2.0
            ox = right_mid[0]
            oy = right_mid[1] + (right_top[1] - right_mid[1]) * f
        orbs.append((ox, oy, accent_name, 8, master_alpha))

    elif archetype == "stepped_pyramid":
        # 4 stepped horizontal bars stacking upward + ascending orb
        tiers = 4
        base_y = cy + 95
        tier_h = 26
        for i in range(tiers):
            prog = _ease_out_cubic((local_t - i * 0.45) / 0.9)
            if prog <= 0.05:
                continue
            w = max(8.0, (260 - i * 52) * prog)
            y0 = base_y - i * (tier_h + 6)
            col = _scale_rgb(accent_rgb if i == tiers - 1 else white_rgb, master_alpha * prog)
            draw.rectangle([int(cx - w / 2), int(y0 - tier_h), int(cx + w / 2), int(y0)], outline=col, width=2)

        # Orb climbing steps on left side
        climb = _clamp01(local_t / 3.2)
        step_idx = climb * (tiers - 1)
        orb_x = cx - (130 - step_idx * 26) - 18
        orb_y = base_y - step_idx * (tier_h + 6) - tier_h / 2
        orbs.append((orb_x, orb_y, accent_name, 8, master_alpha))
        if title:
            _draw_spaced_text(draw, cx, base_y + 55, title, fonts[22], fill=c_white, spacing=5)
        if labels[0] and p_step3 > 0.2:
            _draw_spaced_text(draw, cx, base_y - tiers * (tier_h + 6) - 28, labels[0], fonts[16], fill=_scale_rgb(accent_rgb, master_alpha * p_step3), spacing=3)

    elif archetype == "convergence_funnel":
        # Large triangle with particles converging toward apex + PAUSE icon at top
        apex = (cx, cy - 115)
        bl = (cx - 170, cy + 125)
        br = (cx + 170, cy + 125)
        tri_col = _scale_rgb(dim_rgb, master_alpha * p_step1)
        draw.polygon([apex, bl, br], outline=tri_col, width=2)

        # 5 particles converging from bottom toward apex
        starts = [(-95, 115), (-35, 130), (25, 95), (85, 110), (-15, 45)]
        conv = _ease_in_out_sine(_clamp01((local_t - 0.5) / 3.2))
        for idx, (sx, sy) in enumerate(starts):
            px = cx + sx * (1.0 - conv * 0.96)
            py = (cy + sy) * (1.0 - conv) + (apex[1] + 28 + idx * 9) * conv
            orbs.append((px, py, "white" if idx > 0 else accent_name, 5, master_alpha))

        # Pause icon || above apex
        if p_step3 > 0.15:
            p_col = _scale_rgb(white_rgb, master_alpha * p_step3)
            draw.rectangle([cx - 12, apex[1] - 34, cx - 4, apex[1] - 12], fill=p_col)
            draw.rectangle([cx + 4, apex[1] - 34, cx + 12, apex[1] - 12], fill=p_col)
            _draw_spaced_text(draw, cx, apex[1] - 52, labels[0] or "PAUSE", fonts[14], fill=p_col, spacing=3)

        if title:
            _draw_spaced_text(draw, cx, cy + 155, title, fonts[18], fill=c_white, spacing=5)

    elif archetype == "timeline_document":
        # Horizontal timeline axis + document icon + quote + milestone date
        line_y = cy + 65
        _draw_progressive_line(draw, (cx - 280, line_y), (cx + 280, line_y), p_step1, fill=c_white, width=2)
        draw.ellipse([cx - 6, line_y - 6, cx + 6, line_y + 6], outline=c_white, fill=(0, 0, 0), width=2)

        # Minimalist folded-corner document icon above center
        if p_step1 > 0.3:
            dx, dy = cx, cy - 65
            dw, dh = 52, 68
            fold = 16
            doc_pts = [
                (dx - dw // 2, dy - dh // 2),
                (dx + dw // 2 - fold, dy - dh // 2),
                (dx + dw // 2, dy - dh // 2 + fold),
                (dx + dw // 2, dy + dh // 2),
                (dx - dw // 2, dy + dh // 2),
            ]
            draw.polygon(doc_pts, outline=c_white, width=2)
            for l_off in (-8, 6, 20):
                draw.line([(dx - 14, dy + l_off), (dx + 14, dy + l_off)], fill=c_white, width=2)

        if p_step2 > 0.15:
            headline = f'"{title}"' if title and not title.startswith('"') else (title or '"MILESTONE"')
            _draw_spaced_text(draw, cx, line_y - 32, headline, fonts[20], fill=_scale_rgb(white_rgb, master_alpha * p_step2), spacing=2)
        if p_step3 > 0.15:
            sub = subtitle or labels[0] or "TIMELINE"
            _draw_spaced_text(draw, cx, line_y + 28, sub, fonts[16], fill=_scale_rgb(accent_rgb, master_alpha * p_step3), spacing=3)

    elif archetype == "rotating_gear":
        # Rotating mechanical gear wheel with spokes + DECELERATION title
        outer_r = 84
        inner_r = 68
        hub_r = 22
        # Decelerating rotation angle
        rot = local_t * 0.9 / (1.0 + 0.12 * local_t)
        teeth = 12
        gear_pts = []
        for i in range(teeth * 4):
            ang = rot + (i / (teeth * 4)) * 2.0 * math.pi
            r = outer_r if (i % 4 in (1, 2)) else inner_r
            gear_pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        draw.polygon(gear_pts, outline=c_white, width=2)
        draw.ellipse([cx - inner_r + 8, cy - inner_r + 8, cx + inner_r - 8, cy + inner_r - 8], outline=c_white, width=2)
        draw.ellipse([cx - hub_r, cy - hub_r, cx + hub_r, cy + hub_r], outline=c_accent, width=2)
        for s in range(8):
            ang = rot + s * (math.pi / 4.0)
            draw.line(
                [(cx + math.cos(ang) * hub_r, cy + math.sin(ang) * hub_r),
                 (cx + math.cos(ang) * (inner_r - 8), cy + math.sin(ang) * (inner_r - 8))],
                fill=c_white,
                width=2,
            )
        if title:
            _draw_spaced_text(draw, cx, cy + 145, title, fonts[22], fill=c_white, spacing=4)

    else:  # balance_comparison
        # Two side-by-side comparison pillars/frames with animated levels
        lx, rx = cx - 115, cx + 115
        top_y, bot_y = cy - 95, cy + 95
        draw.rectangle([lx - 65, top_y, lx + 65, bot_y], outline=c_white, width=2)
        draw.rectangle([rx - 65, top_y, rx + 65, bot_y], outline=c_accent, width=2)
        l_h = int(110 * p_step2)
        r_h = int(155 * p_step3)
        if l_h > 14:
            draw.rectangle([lx - 45, bot_y - l_h, lx + 45, bot_y - 10], outline=c_dim, width=2)
        if r_h > 14:
            draw.rectangle([rx - 45, bot_y - r_h, rx + 45, bot_y - 10], outline=c_accent, width=2)
        _draw_spaced_text(draw, lx, bot_y + 28, labels[0] or "LEGACY", fonts[16], fill=c_white, spacing=2)
        _draw_spaced_text(draw, rx, bot_y + 28, labels[1] or "FRONTIER", fonts[16], fill=c_accent, spacing=2)
        orbs.append((rx, bot_y - r_h - 14, accent_name, 8, master_alpha * p_step3))
        if title:
            _draw_spaced_text(draw, cx, bot_y + 72, title, fonts[22], fill=c_white, spacing=4)

    # Fast neon bloom: downsample 2x -> GaussianBlur -> upsample -> screen blend
    small_glow = vec_img.resize((width // 2, height // 2), Image.Resampling.BILINEAR)
    small_glow = small_glow.filter(ImageFilter.GaussianBlur(radius=4.5))
    full_glow = small_glow.resize((width, height), Image.Resampling.BILINEAR)
    blended = ImageChops.screen(vec_img, full_glow)

    # Composite pre-rendered glowing orbs on top
    rgba_frame = blended.convert("RGBA")
    for ox, oy, cname, rad, o_alpha in orbs:
        _paste_orb(rgba_frame, sprites, ox, oy, color_name=cname, radius=rad, alpha=o_alpha)

    return rgba_frame.convert("RGB")


def generate_infographic_storyboard(
    clip_obj,
    body_duration,
    intro_offset=1.5,
    custom_instructions="",
    configure_gemini_fn=None,
    genai_mod=None,
    force_regenerate=False,
):
    """
    Generate or retrieve cached Dan Koe minimalist infographic scenes for a clip.
    Uses Gemini Flash (~700 tokens) to map the clip's timed transcript into 10-14 continuous scenes.
    """
    existing = clip_obj.get("infographic_scenes")
    if existing and isinstance(existing, list) and len(existing) >= 4 and not force_regenerate and not custom_instructions:
        last_scene_end = float(existing[-1].get("end", 0.0))
        if abs(last_scene_end - float(body_duration)) <= 1.0:
            return existing

    title = clip_obj.get("title", "Deep Dive")
    chunks = clip_obj.get("caption_chunks") or []
    timeline_lines = []
    timeline_windows = []
    if chunks:
        # Group caption chunks into ~10s windows so prompt stays ultra-compact (~350 tokens)
        bucket_start = 0.0
        bucket_words = []
        for ch in chunks:
            b_start = max(0.0, float(ch.get("start", intro_offset)) - intro_offset)
            b_end = max(b_start, float(ch.get("end", intro_offset)) - intro_offset)
            if not bucket_words:
                bucket_start = b_start
            bucket_words.append(ch.get("text", ""))
            if b_end - bucket_start >= 10.0:
                w_txt = " ".join(bucket_words)
                timeline_lines.append(f"[{bucket_start:.1f}s-{b_end:.1f}s] {w_txt}")
                timeline_windows.append((bucket_start, b_end, w_txt))
                bucket_words = []
        if bucket_words:
            w_txt = " ".join(bucket_words)
            timeline_lines.append(f"[{bucket_start:.1f}s-{body_duration:.1f}s] {w_txt}")
            timeline_windows.append((bucket_start, body_duration, w_txt))
    else:
        raw_txt = clip_obj.get("text", "") or title
        words_all = raw_txt.split()
        n_win = max(6, min(12, int(round(body_duration / 10.5))))
        step_w = max(1, len(words_all) // n_win)
        for i in range(n_win):
            s_t = round(i * (body_duration / n_win), 2)
            e_t = round(body_duration if i == n_win - 1 else (i + 1) * (body_duration / n_win), 2)
            w_txt = " ".join(words_all[i * step_w : (i + 1) * step_w])
            timeline_lines.append(f"[{s_t:.1f}s-{e_t:.1f}s] {w_txt}")
            timeline_windows.append((s_t, e_t, w_txt))

    num_scenes = len(timeline_windows) if timeline_windows else max(6, min(14, int(round(body_duration / 10.5))))
    timeline_str = "\n".join(timeline_lines)

    prompt = (
        f"Plan {num_scenes} continuous Dan Koe minimalist vector infographic scenes covering 0.0 to {body_duration:.2f}s for clip '{title}'.\n"
        f"Allowed archetypes: {', '.join(ARCHETYPES)}\n"
        "Allowed accents: white, gold, red, cyan\n"
        "Rules:\n"
        f"- First scene starts at 0.0, last scene ends at {body_duration:.2f}, each scene's end == next scene's start (no gaps).\n"
        "- Pick diverse archetypes that visually metaphorize the spoken words in each time window.\n"
        "- Keep 'title' (1-3 words) and 'labels' (2-3 short uppercase words/phrases, max 20 chars each) punchy.\n"
        + (f"- Special instructions: {custom_instructions}\n" if custom_instructions else "")
        + f"Timed Script:\n{timeline_str}\n\n"
        "Return ONLY a valid JSON array of objects with keys: "
        '[{"start":0.0,"end":10.5,"archetype":"...","accent":"white","title":"...","labels":["...","..."],"subtitle":""}]'
    )

    scenes = None
    if genai_mod is not None:
        try:
            model = None
            for m_name in ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-latest", "gemini-2.5-flash"]:
                try:
                    model = genai_mod.GenerativeModel(m_name)
                    break
                except Exception:
                    continue
            if model:
                resp = model.generate_content(prompt)
                if resp and resp.text:
                    raw = resp.text.strip()
                    if "```" in raw:
                        parts = raw.split("```")
                        for p in parts:
                            p_clean = p.strip()
                            if p_clean.startswith("json"):
                                p_clean = p_clean[4:].strip()
                            if p_clean.startswith("["):
                                raw = p_clean
                                break
                    parsed = json.loads(raw)
                    if isinstance(parsed, list) and len(parsed) >= 3:
                        scenes = parsed
        except Exception as e:
            print(f"[InfographicEngine] Gemini storyboard notice (using local semantic analyzer): {e}")

    if not scenes:
        # Context-aware Semantic Metaphor Analyzer over each timed spoken window
        stopwords = {
            "THE", "AND", "THAT", "THIS", "WITH", "FROM", "HAVE", "THEY", "THEIR", "WHILE",
            "BECAUSE", "VERY", "JUST", "INTO", "WHAT", "WHEN", "WHERE", "WHICH", "THERE",
            "ABOUT", "WOULD", "COULD", "SHOULD", "THESE", "THOSE", "BEING", "BEEN", "WERE",
            "HERE", "SOME", "MORE", "MOST", "OTHER", "SUCH", "ONLY", "ALSO", "THEN", "THAN",
            "WELL", "LIKE", "OVER", "UNDER", "AFTER", "BEFORE", "BETWEEN", "THROUGH", "DURING",
            "WITHOUT", "WITHIN", "ALONG", "ACROSS", "BEHIND", "BEYOND", "PLUS", "EXCEPT", "BUT",
            "FOR", "NOR", "YET", "ARE", "WAS", "NOT", "YOU", "YOUR", "OUR", "ALL", "ANY", "CAN",
            "WILL", "ONE", "TWO", "OUT", "NOW", "HOW", "WHO", "WHY", "YES", "NO", "GET", "GOT",
            "MAKE", "MADE", "GOING", "KNOW", "THINK", "MEANING", "LITERAL", "LITERALLY", "HUGE",
            "MASSIVE", "SPECIFIC", "COMPLETELY", "ACTUALLY", "BASICALLY", "CURRENTLY", "RECENTLY",
            "SUDDENLY", "TRADITIONALLY", "PRECISELY", "ENTERING", "WITNESSING", "BRINGS", "NOTES"
        }
        import re as _re
        scenes = []
        used_recent = []
        for idx, (s_t, e_t, w_txt) in enumerate(timeline_windows):
            up = w_txt.upper()
            tokens = [
                w for w in _re.findall(r"[A-Z0-9$]+", up)
                if len(w) >= 4 and w not in stopwords
            ]
            # Deduplicate preserving order
            uniq = []
            for t_w in tokens:
                if t_w not in uniq:
                    uniq.append(t_w)

            # Semantic archetype selection
            arch = None
            acc = "white"
            s_title = ""
            s_labels = []
            s_sub = ""

            if any(k in up for k in ("DEFAULT SEARCH", "MONOPOLY", "SCRUTINY", "FEDERAL COURT")):
                arch, acc = "perspective_grid_scale", "white"
                s_title = "GOOGLE" if "GOOGLE" in up else (uniq[0] if uniq else "MONOPOLY")
                s_labels = ["SEARCH MONOPOLY", "ANTITRUST"]
            elif any(k in up for k in ("BROKEN UP", "CORPORATE STRUCTURE", "BREAK THEM UP", "DIVIDE")):
                arch, acc = "split_fracture", "white"
                s_title = "STRUCTURAL BREAKUP"
                s_labels = ["CORPORATE", "STRUCTURE"]
            elif any(k in up for k in ("INSTAGRAM", "WHATSAPP", "INTEGRATED", "FTC")):
                arch, acc = "triangle_network", "gold"
                s_title = "META ECOSYSTEM"
                s_labels = ["META", "INSTAGRAM", "WHATSAPP"]
            elif any(k in up for k in ("RUN WILD", "BURN THE BOATS", "FREE TO", "DEPLOY")):
                arch, acc = "radial_constellation", "white"
                s_title = "META FREE TO DEPLOY" if "META" in up else "RAPID DEPLOYMENT"
                s_labels = ["AUTONOMOUS", "SCALE"]
            elif any(k in up for k in ("AGENTIC", "INFLECTION", "ACCELERAT", "EXPONENTIAL")):
                arch, acc = "trajectory_curve", "cyan"
                s_title = "INFLECTION POINT"
                s_labels = ["AGENTIC TECH", "SCALE"]
            elif any(k in up for k in ("TRAPPED", "STATELESS", "COMPUTE COSTS", "BUSINESS MODEL")):
                arch, acc = "ecosystem_cards", "white"
                s_title = "COMPETITOR LOCK-IN"
                s_labels = ["GOOGLE", "APPLE", "FRONTIER"]
            elif any(k in up for k in ("BATTLEFIELD", "COURTROOM", "CODE BASE", "CODEBASE")):
                arch, acc = "fork_roadblock", "red"
                s_title = "NEW BATTLEFIELD"
                s_labels = ["TECH / DISTRIBUTION", "COURTROOM"]
            elif any(k in up for k in ("CONVERGENCE", "ALIGNING", "POLICY", "REGULATORY")):
                arch, acc = "convergence_funnel", "white"
                s_title = "CONVERGENCE"
                s_labels = ["PAUSE", "REGULATION"]
            elif any(k in up for k in ("ESSAY", "SEPTEMBER", "2026", "DARIO", "ANTHROPIC", "FRONTIER")):
                arch, acc = "timeline_document", "gold"
                s_title = "PACE THE FRONTIER"
                s_labels = ["SEP 2026", "ANTHROPIC"]
                s_sub = "SEP 2026"
            elif any(k in up for k in ("DECELERATION", "SLOWDOWN", "DELIBERATE", "BRAKE")):
                arch, acc = "rotating_gear", "cyan"
                s_title = "DECELERATION"
                s_labels = ["CAPABILITIES", "SLOWDOWN"]

            if not arch or arch in used_recent:
                for cand in ARCHETYPES:
                    if cand not in used_recent:
                        arch = cand
                        break
                if not arch:
                    arch = ARCHETYPES[idx % len(ARCHETYPES)]
                acc = ["white", "gold", "cyan", "red"][idx % 4]

            used_recent.append(arch)
            if not s_title:
                s_title = " ".join(uniq[:2]) if len(uniq) >= 2 else (uniq[0] if uniq else f"PHASE {idx+1}")
            if not s_labels:
                s_labels = uniq[2:5] if len(uniq) >= 4 else (uniq[:2] if uniq else ["SYSTEM", "SHIFT"])

            scenes.append({
                "start": round(s_t, 2),
                "end": round(e_t, 2),
                "archetype": arch,
                "accent": acc,
                "title": s_title[:26],
                "labels": [l[:22] for l in s_labels[:3]],
                "subtitle": s_sub[:22],
            })

    # Normalize & chain timestamps strictly from 0.0 to body_duration
    cleaned = []
    for idx, sc in enumerate(scenes):
        arch = sc.get("archetype")
        if arch not in ARCHETYPES:
            arch = ARCHETYPES[idx % len(ARCHETYPES)]
        acc = sc.get("accent", "white")
        if acc not in COLORS:
            acc = "white"
        s_t = 0.0 if idx == 0 else cleaned[-1]["end"]
        e_t = float(sc.get("end", s_t + (body_duration / len(scenes))))
        if idx == len(scenes) - 1 or e_t > body_duration:
            e_t = round(body_duration, 2)
        if e_t <= s_t + 1.0:
            e_t = min(round(body_duration, 2), round(s_t + max(2.0, body_duration / len(scenes)), 2))
        cleaned.append({
            "start": round(s_t, 2),
            "end": round(e_t, 2),
            "archetype": arch,
            "accent": acc,
            "title": str(sc.get("title", "")).upper()[:26],
            "labels": [str(x).upper()[:22] for x in (sc.get("labels") or [])[:3]],
            "subtitle": str(sc.get("subtitle", "")).upper()[:22],
        })
    if cleaned:
        cleaned[-1]["end"] = round(body_duration, 2)

    clip_obj["infographic_scenes"] = cleaned
    return cleaned


def render_infographic_mp4(scenes, audio_path, out_mp4_path, duration=None, fps=25):
    """
    Render the 740x740 Dan Koe minimalist neon wireframe video directly into `out_mp4_path`
    by piping RGB frames to FFmpeg alongside `audio_path`.
    """
    if duration is None or duration <= 0:
        try:
            p = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                capture_output=True, text=True, timeout=10
            )
            if p.returncode == 0 and p.stdout.strip():
                duration = float(p.stdout.strip())
        except Exception:
            pass
    if not duration or duration <= 0:
        duration = scenes[-1]["end"] if scenes else 60.0

    os.makedirs(os.path.dirname(os.path.abspath(out_mp4_path)), exist_ok=True)
    fonts = _load_fonts()
    sprites = _build_orb_sprites()

    width, height = 740, 740
    total_frames = max(1, int(round(duration * fps)))

    tmp_mp4_path = out_mp4_path + ".tmp.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        tmp_mp4_path,
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    scene_idx = 0
    num_scenes = len(scenes)
    last_bytes = None

    try:
        for f_idx in range(total_frames):
            t = f_idx / float(fps)
            while scene_idx < num_scenes - 1 and t >= scenes[scene_idx]["end"]:
                scene_idx += 1
            sc = scenes[scene_idx]
            s_start = float(sc.get("start", 0.0))
            s_end = float(sc.get("end", duration))
            s_dur = max(0.5, s_end - s_start)
            local_t = max(0.0, t - s_start)

            # During initial 2.6s step reveal or final 0.4s fade-out, render every 2nd frame (12.5fps);
            # during steady orbital/pulse phase, render every 3rd frame (8.3fps) for ultra-fast ~14s total encode
            stride = 2 if (local_t < 2.6 or (s_dur - local_t) < 0.5) else 3
            if (f_idx % stride != 0) and last_bytes is not None:
                proc.stdin.write(last_bytes)
                continue

            frame_img = _render_scene_frame(sc, local_t, s_dur, fonts, sprites, width=width, height=height)
            last_bytes = frame_img.tobytes()
            proc.stdin.write(last_bytes)
    except Exception:
        proc.kill()
        if os.path.exists(tmp_mp4_path):
            try:
                os.remove(tmp_mp4_path)
            except Exception:
                pass
        raise
    finally:
        if proc.stdin:
            try:
                proc.stdin.close()
            except Exception:
                pass

    _, stderr_bytes = proc.communicate()
    if proc.returncode != 0:
        if os.path.exists(tmp_mp4_path):
            try:
                os.remove(tmp_mp4_path)
            except Exception:
                pass
        err_msg = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else "Unknown FFmpeg error"
        raise RuntimeError(f"FFmpeg infographic render failed: {err_msg[-600:]}")

    os.replace(tmp_mp4_path, out_mp4_path)
    return out_mp4_path
