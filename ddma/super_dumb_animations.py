"""
Super Dumb & Purely Figurative Cartoon Animations for Animated Courses.
Zero data clutter, bold thick shapes, pure figurative storytelling.
"""
import math
from PIL import Image, ImageDraw, ImageFont

def draw_dripping_kitchen_tap(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Kitchen counter & wall
    draw.line([(cx - 700, cy + 180), (cx + 700, cy + 180)], fill=(90, 105, 125), width=10)
    draw.line([(cx - 700, cy + 186), (cx + 700, cy + 186)], fill=(40, 50, 65), width=6)
    
    # Backsplash tiles
    for tx in range(cx - 650, cx + 650, 120):
        draw.line([(tx, cy - 220), (tx, cy + 175)], fill=(20, 28, 40), width=2)
    for ty in range(cy - 220, cy + 180, 80):
        draw.line([(cx - 650, ty), (cx + 650, ty)], fill=(20, 28, 40), width=2)

    # Big Shiny Brass Faucet
    fx = cx - 120
    fy = cy + 180
    # Base
    draw.ellipse([(fx - 45, fy - 20), (fx + 45, fy + 5)], fill=(218, 165, 32))
    # Vertical pipe
    draw.line([(fx, fy), (fx, fy - 240)], fill=(218, 165, 32), width=22)
    draw.line([(fx - 4, fy), (fx - 4, fy - 240)], fill=(255, 220, 80), width=6)
    # Gooseneck curve
    draw.arc([(fx - 140, fy - 360), (fx + 140, fy - 120)], start=270, end=90, fill=(218, 165, 32), width=22)
    draw.arc([(fx - 144, fy - 364), (fx + 136, fy - 124)], start=270, end=90, fill=(255, 220, 80), width=6)
    # Spout nozzle
    nx = fx + 140
    ny = fy - 160
    draw.line([(nx, ny), (nx, ny + 50)], fill=(218, 165, 32), width=18)
    draw.rectangle([(nx - 14, ny + 40), (nx + 14, ny + 56)], fill=(255, 214, 10))
    # Valve handle
    vx = fx
    vy = fy - 120
    draw.line([(vx - 40, vy), (vx + 40, vy)], fill=(255, 214, 10), width=10)
    draw.ellipse([(vx - 10, vy - 10), (vx + 10, vy + 10)], fill=(218, 165, 32))

    # Coffee Mug / Cup under spout
    mx = nx
    my = fy - 20
    mw, mh = 140, 150
    draw.rounded_rectangle([(mx - mw//2, my - mh), (mx + mw//2, my)], radius=16, fill=(18, 55, 95), outline=(56, 189, 248), width=5)
    # Mug handle
    draw.arc([(mx + mw//2 - 10, my - mh + 25), (mx + mw//2 + 55, my - 25)], start=270, end=90, fill=(56, 189, 248), width=8)
    # Water level inside mug
    fill_level = int(40 + 25 * math.sin(t * 2.0))
    draw.rounded_rectangle([(mx - mw//2 + 6, my - fill_level), (mx + mw//2 - 6, my - 4)], radius=10, fill=(0, 229, 255))

    # Dripping Droplet Animation
    drop_cycle = (t * 2.5) % 1.0
    dy = ny + 56 + int(drop_cycle * (my - mh - (ny + 56)))
    drop_size = 14
    draw.ellipse([(nx - drop_size//2, dy - drop_size), (nx + drop_size//2, dy + drop_size)], fill=(0, 229, 255))
    draw.polygon([(nx - drop_size//2, dy), (nx + drop_size//2, dy), (nx, dy - drop_size - 8)], fill=(0, 229, 255))

    # Concentric splash ripples on water surface
    ripple_r = int((drop_cycle * 45))
    if drop_cycle > 0.4:
        draw.arc([(mx - ripple_r, my - fill_level - 10), (mx + ripple_r, my - fill_level + 10)], start=0, end=360, fill=(255, 255, 255), width=2)

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(56, 189, 248), width=3)
    draw.text((cx, cy + 270), "WATER CAN BE SAVED IN A MUG • COMPUTE CYCLES CANNOT", font=fonts.get("bold_26"), fill=(56, 189, 248), anchor="mm")


def draw_melting_ice_cream_cone(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Grinning Cartoon Hot Sun (top right)
    sx, sy = cx + 520, cy - 180
    sun_r = 85
    # Rotating cartoon rays
    for i in range(12):
        ang = (t * 0.8) + i * (math.pi / 6)
        r1 = sun_r + 15
        r2 = sun_r + 45
        p1 = (sx + int(r1 * math.cos(ang)), sy + int(r1 * math.sin(ang)))
        p2 = (sx + int(r2 * math.cos(ang)), sy + int(r2 * math.sin(ang)))
        draw.line([p1, p2], fill=(255, 214, 10), width=6)
    draw.ellipse([(sx - sun_r, sy - sun_r), (sx + sun_r, sy + sun_r)], fill=(255, 214, 10), outline=(245, 158, 11), width=4)
    # Sun sunglasses
    draw.rectangle([(sx - 45, sy - 15), (sx - 5, sy + 15)], fill=(15, 23, 42))
    draw.rectangle([(sx + 5, sy - 15), (sx + 45, sy + 15)], fill=(15, 23, 42))
    draw.line([(sx - 5, sy - 5), (sx + 5, sy - 5)], fill=(15, 23, 42), width=4)
    # Sun smile
    draw.arc([(sx - 25, sy + 10), (sx + 25, sy + 45)], start=0, end=180, fill=(180, 83, 9), width=4)

    # Ground line & Melting Puddle
    gy = cy + 180
    draw.line([(cx - 700, gy), (cx + 700, gy)], fill=(70, 85, 105), width=6)
    puddle_w = int(220 + 35 * math.sin(t * 3.0))
    draw.ellipse([(cx - puddle_w//2, gy - 25), (cx + puddle_w//2, gy + 25)], fill=(244, 114, 182), outline=(219, 39, 119), width=3)

    # Waffle Cone
    cone_tip = (cx, gy - 10)
    cone_left = (cx - 95, cy - 20)
    cone_right = (cx + 95, cy - 20)
    draw.polygon([cone_tip, cone_left, cone_right], fill=(217, 119, 6), outline=(180, 83, 9), width=4)
    # Waffle crosshatch lines
    for off in range(-60, 80, 25):
        draw.line([(cone_left[0] + 40 + off, cone_left[1] + 20), (cone_tip[0] + off//2, cone_tip[1] - 30)], fill=(180, 83, 9), width=2)
        draw.line([(cone_right[0] - 40 - off, cone_right[1] + 20), (cone_tip[0] - off//2, cone_tip[1] - 30)], fill=(180, 83, 9), width=2)

    # Giant Scoop of Strawberry Ice Cream
    scoop_y = cy - 70
    scoop_r = 115
    draw.ellipse([(cx - scoop_r, scoop_y - scoop_r), (cx + scoop_r, scoop_y + scoop_r)], fill=(244, 114, 182), outline=(219, 39, 119), width=5)
    # Highlights
    draw.arc([(cx - scoop_r + 20, scoop_y - scoop_r + 20), (cx, scoop_y)], start=180, end=270, fill=(255, 255, 255), width=6)

    # Bright Red Cherry on top
    cherry_x = cx
    cherry_y = scoop_y - scoop_r + 5
    draw.ellipse([(cherry_x - 24, cherry_y - 24), (cherry_x + 24, cherry_y + 24)], fill=(225, 29, 72), outline=(159, 18, 57), width=3)
    draw.arc([(cherry_x - 10, cherry_y - 55), (cherry_x + 35, cherry_y - 15)], start=90, end=200, fill=(74, 222, 128), width=4)

    # Animated drips sliding down cone
    for di, dx_off in enumerate([-60, -15, 45]):
        d_phase = (t * 2.0 + di * 0.4) % 1.0
        d_y = cy - 20 + int(d_phase * 160)
        draw.ellipse([(cx + dx_off - 8, d_y - 8), (cx + dx_off + 8, d_y + 12)], fill=(244, 114, 182))

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(244, 114, 182), width=3)
    draw.text((cx, cy + 270), "PERISHABLE TIME • IDLE SILICON DIES EVERY MILLISECOND", font=fonts.get("bold_26"), fill=(244, 114, 182), anchor="mm")


def draw_cash_bonfire(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Dark camp ground
    gy = cy + 180
    draw.line([(cx - 700, gy), (cx + 700, gy)], fill=(60, 75, 95), width=8)

    # Stacks of $100 Dollar Bills forming the firewood base
    bill_coords = [
        (cx - 160, gy - 25, cx - 40, gy),
        (cx + 40, gy - 25, cx + 160, gy),
        (cx - 110, gy - 50, cx + 10, gy - 25),
        (cx - 20, gy - 50, cx + 100, gy - 25),
        (cx - 80, gy - 75, cx + 60, gy - 50),
    ]
    for x1, y1, x2, y2 in bill_coords:
        draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=4, fill=(20, 83, 45), outline=(34, 197, 94), width=2)
        draw.text(((x1 + x2)//2, (y1 + y2)//2), "$100", font=fonts.get("bold_16"), fill=(34, 197, 94), anchor="mm")

    # Big Animated Campfire Flames
    flame_height = 190
    base_y = gy - 65
    flame_colors = [(239, 68, 68), (249, 115, 22), (255, 214, 10)]
    flame_radii = [130, 95, 60]

    for f_idx, (f_col, f_rad) in enumerate(zip(flame_colors, flame_radii)):
        flame_pts = []
        steps = 16
        for s in range(steps + 1):
            ang = math.pi * (s / steps)
            wiggle = math.sin(t * 12.0 + s * 0.8 + f_idx * 1.5) * (18 - f_idx * 4)
            px = cx - int(f_rad * math.cos(ang)) + int(wiggle)
            # Tapered flame top
            h_scale = math.sin(ang) * (flame_height - f_idx * 35)
            py = base_y - int(h_scale) + int(wiggle * 0.5)
            flame_pts.append((px, py))
        flame_pts.append((cx + f_rad, base_y))
        flame_pts.append((cx - f_rad, base_y))
        draw.polygon(flame_pts, fill=f_col)

    # Floating sparks and smoke puffs
    for i in range(7):
        spark_t = (t * 2.0 + i * 0.35) % 1.0
        sp_x = cx + int(65 * math.sin(i * 2.1 + t * 4.0))
        sp_y = base_y - flame_height - int(spark_t * 120)
        draw.ellipse([(sp_x - 4, sp_y - 4), (sp_x + 4, sp_y + 4)], fill=(255, 214, 10))

    # Smoke puffs
    for si in range(3):
        smk_t = (t * 0.8 + si * 0.4) % 1.0
        smk_x = cx + int(40 * math.sin(si + t * 2.0))
        smk_y = base_y - flame_height - 60 - int(smk_t * 140)
        smk_r = int(14 + smk_t * 22)
        draw.ellipse([(smk_x - smk_r, smk_y - smk_r), (smk_x + smk_r, smk_y + smk_r)], fill=(40, 50, 65, 120), outline=(80, 95, 115), width=2)

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(239, 68, 68), width=3)
    draw.text((cx, cy + 270), "IDLE SILICON ACTIVELY BURNS CASH EVERY SINGLE SECOND", font=fonts.get("bold_26"), fill=(239, 68, 68), anchor="mm")


def draw_flying_passenger_jet(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Night sky with twinkling cartoon stars
    star_positions = [(cx - 600, cy - 200), (cx - 350, cy - 240), (cx + 200, cy - 220), (cx + 550, cy - 180), (cx - 100, cy - 250)]
    for sx, sy in star_positions:
        tw = int(4 + 3 * math.sin(t * 5.0 + sx))
        draw.polygon([(sx, sy - tw), (sx + tw, sy), (sx, sy + tw), (sx - tw, sy)], fill=(255, 255, 255))

    # Fluffy cartoon cumulus clouds drifting across
    cloud_offsets = [0, 600, 1200]
    for c_i, c_off in enumerate(cloud_offsets):
        c_x = int((cx + c_off - t * 120) % 2200) - 200
        c_y = cy - 120 + (c_i % 2) * 220
        # Cloud puffs
        draw.ellipse([(c_x - 80, c_y - 30), (c_x + 80, c_y + 30)], fill=(28, 38, 55))
        draw.ellipse([(c_x - 40, c_y - 60), (c_x + 40, c_y + 10)], fill=(38, 50, 72))
        draw.ellipse([(c_x + 20, c_y - 50), (c_x + 90, c_y + 20)], fill=(32, 44, 64))

    # Big Cartoon Passenger Airliner (centered)
    plane_w = 460
    plane_h = 90
    py = cy + int(12 * math.sin(t * 3.0)) # gentle banking bob
    px = cx

    # Jet exhaust flame / thrust trail
    ex_len = int(120 + 25 * math.sin(t * 20.0))
    draw.polygon([(px - plane_w//2 - 20, py + 15), (px - plane_w//2 - 20 - ex_len, py + 20), (px - plane_w//2 - 20, py + 25)], fill=(0, 229, 255))
    draw.polygon([(px - plane_w//2 - 20, py + 17), (px - plane_w//2 - 20 - ex_len//2, py + 20), (px - plane_w//2 - 20, py + 23)], fill=(255, 255, 255))

    # Fuselage
    draw.rounded_rectangle([(px - plane_w//2, py - plane_h//2), (px + plane_w//2, py + plane_h//2)], radius=45, fill=(241, 245, 249), outline=(148, 163, 184), width=4)
    # Blue airline cheatline stripe
    draw.rectangle([(px - plane_w//2 + 20, py), (px + plane_w//2 - 40, py + 16)], fill=(2, 132, 199))

    # Cockpit windshield
    draw.polygon([(px + plane_w//2 - 50, py - 30), (px + plane_w//2 - 15, py - 10), (px + plane_w//2 - 40, py - 5)], fill=(15, 23, 42))

    # Passenger cabin windows
    for wi in range(8):
        wx = px - 140 + wi * 38
        draw.ellipse([(wx - 8, py - 20), (wx + 8, py - 2)], fill=(14, 165, 233), outline=(2, 132, 199), width=2)

    # Swept Wing
    draw.polygon([(px - 40, py + 10), (px - 140, py + 95), (px - 80, py + 95), (px + 40, py + 10)], fill=(203, 213, 225), outline=(100, 116, 139), width=3)
    # Tail fin
    draw.polygon([(px - plane_w//2 + 30, py - plane_h//2), (px - plane_w//2 - 20, py - plane_h//2 - 90), (px - plane_w//2 + 50, py - plane_h//2 - 90), (px - plane_w//2 + 100, py - plane_h//2)], fill=(2, 132, 199), outline=(148, 163, 184), width=3)

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(2, 132, 199), width=3)
    draw.text((cx, cy + 270), "THE EMPTY AIRLINE SEAT • REVENUE LOST FOREVER AT TAKEOFF", font=fonts.get("bold_26"), fill=(56, 189, 248), anchor="mm")


def draw_paper_airplanes_globe(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Center Earth Globe
    gr = 180
    gy = cy
    draw.ellipse([(cx - gr, gy - gr), (cx + gr, gy + gr)], fill=(14, 116, 144), outline=(56, 189, 248), width=5)

    # Green cartoon continents
    cont_pts1 = [(cx - 100, gy - 80), (cx - 40, gy - 120), (cx + 20, gy - 60), (cx - 10, gy + 30), (cx - 80, gy + 20)]
    draw.polygon(cont_pts1, fill=(34, 197, 94))
    cont_pts2 = [(cx + 20, gy - 40), (cx + 120, gy - 50), (cx + 140, gy + 40), (cx + 50, gy + 80), (cx + 10, gy + 20)]
    draw.polygon(cont_pts2, fill=(34, 197, 94))
    cont_pts3 = [(cx - 70, gy + 50), (cx - 20, gy + 40), (cx - 30, gy + 130), (cx - 60, gy + 110)]
    draw.polygon(cont_pts3, fill=(34, 197, 94))

    # Grid latitude lines
    draw.arc([(cx - gr, gy - gr//2), (cx + gr, gy + gr//2)], start=0, end=180, fill=(6, 182, 212), width=2)
    draw.arc([(cx - gr, gy - gr//2), (cx + gr, gy + gr//2)], start=180, end=360, fill=(6, 182, 212), width=2)
    draw.line([(cx - gr, gy), (cx + gr, gy)], fill=(6, 182, 212), width=2)

    # 3 White Paper Airplanes swooping around globe on orbital arcs
    for pi in range(3):
        p_ang = t * 1.5 + pi * (2 * math.pi / 3)
        orbit_rx = gr + 140
        orbit_ry = gr + 60
        px = cx + int(orbit_rx * math.cos(p_ang))
        py = gy + int(orbit_ry * math.sin(p_ang))
        # Draw paper airplane shape
        heading = p_ang + math.pi / 2
        fwd = (int(25 * math.cos(heading)), int(25 * math.sin(heading)))
        wing1 = (int(16 * math.cos(heading + 2.4)), int(16 * math.sin(heading + 2.4)))
        wing2 = (int(16 * math.cos(heading - 2.4)), int(16 * math.sin(heading - 2.4)))
        
        nose = (px + fwd[0], py + fwd[1])
        w_left = (px + wing1[0], py + wing1[1])
        w_right = (px + wing2[0], py + wing2[1])
        
        draw.polygon([nose, w_left, (px, py), w_right], fill=(255, 255, 255), outline=(200, 220, 240), width=2)
        draw.line([nose, (px, py)], fill=(148, 163, 184), width=2)

    # Radar city dots
    cities = [("TOKYO", cx + 90, gy - 40), ("ICELAND", cx - 30, gy - 110), ("NEW YORK", cx - 90, gy - 50)]
    for c_name, cit_x, cit_y in cities:
        glow_r = int(10 + 4 * math.sin(t * 6.0 + cit_x))
        draw.ellipse([(cit_x - glow_r, cit_y - glow_r), (cit_x + glow_r, cit_y + glow_r)], outline=(255, 214, 10), width=2)
        draw.ellipse([(cit_x - 4, cit_y - 4), (cit_x + 4, cit_y + 4)], fill=(255, 214, 10))
        draw.text((cit_x, cit_y + 14), c_name, font=fonts.get("bold_16"), fill=(255, 214, 10), anchor="mt")

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(34, 197, 94), width=3)
    draw.text((cx, cy + 270), "ZERO FRICTION • TRAFFIC HOPS CONTINENTS IN A MILLISECOND", font=fonts.get("bold_26"), fill=(34, 197, 94), anchor="mm")


def draw_empty_bistro_waiter(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Red-and-white striped awning
    ay = cy - 220
    aw = 800
    for si, sx in enumerate(range(cx - aw//2, cx + aw//2, 50)):
        col = (239, 68, 68) if si % 2 == 0 else (241, 245, 249)
        draw.polygon([(sx, ay), (sx + 50, ay), (sx + 40, ay + 70), (sx - 10, ay + 70)], fill=col)

    # Cobblestone ground
    gy = cy + 180
    draw.line([(cx - 700, gy), (cx + 700, gy)], fill=(80, 95, 115), width=8)

    # Big Ticking Wall Clock
    ck_x = cx + 380
    ck_y = cy - 90
    ck_r = 65
    draw.ellipse([(ck_x - ck_r, ck_y - ck_r), (ck_x + ck_r, ck_y + ck_r)], fill=(255, 255, 255), outline=(15, 23, 42), width=5)
    # Clock hands ticking
    draw.line([(ck_x, ck_y), (ck_x, ck_y - 40)], fill=(15, 23, 42), width=4)
    sec_ang = t * 4.0
    draw.line([(ck_x, ck_y), (ck_x + int(35 * math.cos(sec_ang)), ck_y + int(35 * math.sin(sec_ang)))], fill=(239, 68, 68), width=2)
    draw.text((ck_x, ck_y + 85), "3:15 PM (OFF-PEAK)", font=fonts.get("bold_16"), fill=(255, 214, 10), anchor="mt")

    # Round bistro table with red checkered tablecloth
    tbl_x = cx - 240
    draw.ellipse([(tbl_x - 90, gy - 80), (tbl_x + 90, gy - 40)], fill=(220, 38, 38), outline=(255, 255, 255), width=3)
    draw.line([(tbl_x, gy - 40), (tbl_x, gy)], fill=(15, 23, 42), width=8)
    draw.line([(tbl_x - 45, gy), (tbl_x + 45, gy)], fill=(15, 23, 42), width=6)
    # Empty chairs
    draw.line([(tbl_x - 120, gy - 80), (tbl_x - 120, gy)], fill=(15, 23, 42), width=5)
    draw.line([(tbl_x + 120, gy - 80), (tbl_x + 120, gy)], fill=(15, 23, 42), width=5)
    draw.text((tbl_x, gy - 110), "RESERVED", font=fonts.get("bold_16"), fill=(148, 163, 184), anchor="mm")

    # Cartoon Waiter in center holding empty tray looking sad
    wx = cx + 80
    wy = gy - 130
    # Head
    draw.ellipse([(wx - 26, wy - 70), (wx + 26, wy - 18)], fill=(254, 215, 170))
    # Apron & Body
    draw.rectangle([(wx - 30, wy - 18), (wx + 30, wy + 90)], fill=(15, 23, 42))
    draw.polygon([(wx - 20, wy - 18), (wx + 20, wy - 18), (wx + 25, wy + 90), (wx - 25, wy + 90)], fill=(255, 255, 255))
    draw.line([(wx - 8, wy - 10), (wx + 8, wy - 10)], fill=(239, 68, 68), width=6) # bow tie
    # Tray arm
    draw.line([(wx - 20, wy + 10), (wx - 65, wy - 10)], fill=(254, 215, 170), width=6)
    draw.line([(wx - 100, wy - 10), (wx - 30, wy - 10)], fill=(203, 213, 225), width=6) # empty silver tray

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(239, 68, 68), width=3)
    draw.text((cx, cy + 270), "FLAT PRICING GUARANTEES EMPTY TABLES DURING OFF-PEAK HOURS", font=fonts.get("bold_26"), fill=(239, 68, 68), anchor="mm")


def draw_airport_boarding_gate(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Floor line
    gy = cy + 180
    draw.line([(cx - 700, gy), (cx + 700, gy)], fill=(70, 85, 105), width=8)

    # Gate Door frame (right side)
    gx = cx + 380
    draw.rectangle([(gx - 80, gy - 260), (gx + 80, gy)], fill=(18, 24, 38), outline=(56, 189, 248), width=5)
    # Gate Sign
    draw.rounded_rectangle([(gx - 110, gy - 310), (gx + 110, gy - 265)], radius=8, fill=(15, 23, 42), outline=(255, 214, 10), width=3)
    draw.text((gx, gy - 288), "GATE 248 // BOARDING", font=fonts.get("bold_18"), fill=(255, 214, 10), anchor="mm")

    # Queue of cartoon passengers walking towards the door
    passengers = [
        ("BUSINESS BOT", -380, (2, 132, 199)),
        ("VACATIONER", -180, (234, 88, 12)),
        ("STUDENT", 20, (147, 51, 234)),
        ("PRIORITY BOT", 220, (255, 214, 10)),
    ]
    for p_name, base_x, p_col in passengers:
        walk_x = cx + base_x + int(40 * ((t * 0.8) % 1.0))
        py = gy - 110
        # Character circle head
        draw.ellipse([(walk_x - 18, py - 60), (walk_x + 18, py - 24)], fill=(254, 215, 170))
        # Body
        draw.rounded_rectangle([(walk_x - 16, py - 24), (walk_x + 16, py + 45)], radius=6, fill=p_col)
        # Legs walking
        leg_phase = math.sin(t * 12.0 + base_x) * 16
        draw.line([(walk_x - 8, py + 45), (walk_x - 8 + int(leg_phase), gy)], fill=(15, 23, 42), width=5)
        draw.line([(walk_x + 8, py + 45), (walk_x + 8 - int(leg_phase), gy)], fill=(15, 23, 42), width=5)
        # Rolling suitcase behind
        draw.rounded_rectangle([(walk_x - 45, py + 10), (walk_x - 25, py + 50)], radius=4, fill=(51, 65, 85))
        draw.line([(walk_x - 35, py + 10), (walk_x - 16, py + 15)], fill=(100, 116, 139), width=2) # handle

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(34, 197, 94), width=3)
    draw.text((cx, cy + 270), "DYNAMIC YIELD MANAGEMENT • PACKING EVERY SEAT BEFORE TAKEOFF", font=fonts.get("bold_26"), fill=(34, 197, 94), anchor="mm")


def draw_yellow_forklift_cargo(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Warehouse Floor with Yellow Safety Caution Stripes
    gy = cy + 180
    draw.line([(cx - 700, gy), (cx + 700, gy)], fill=(50, 60, 75), width=8)
    for sx in range(cx - 650, cx + 650, 60):
        draw.line([(sx, gy), (sx + 25, gy + 16)], fill=(255, 214, 10), width=5)

    # Stack of Wooden Crates (right side)
    st_x = cx + 380
    crates = [(st_x, gy - 70), (st_x + 130, gy - 70), (st_x + 65, gy - 180)]
    for cw_x, cw_y in crates:
        draw.rectangle([(cw_x - 55, cw_y - 55), (cw_x + 55, cw_y + 55)], fill=(180, 120, 60), outline=(120, 80, 35), width=4)
        draw.line([(cw_x - 55, cw_y - 55), (cw_x + 55, cw_y + 55)], fill=(120, 80, 35), width=3)
        draw.line([(cw_x + 55, cw_y - 55), (cw_x - 55, cw_y + 55)], fill=(120, 80, 35), width=3)
        draw.text((cw_x, cw_y), "BATCH", font=fonts.get("bold_16"), fill=(255, 214, 10), anchor="mm")

    # Animated Yellow Forklift
    fl_x = cx - 180 + int(45 * math.sin(t * 2.0))
    fl_y = gy - 75
    # Main yellow body
    draw.rounded_rectangle([(fl_x - 140, fl_y - 50), (fl_x + 30, fl_y + 50)], radius=12, fill=(234, 179, 8), outline=(161, 98, 7), width=4)
    # Roll cage & cab
    draw.line([(fl_x - 70, fl_y - 50), (fl_x - 70, fl_y - 130), (fl_x + 15, fl_y - 130), (fl_x + 25, fl_y - 50)], fill=(30, 41, 59), width=7)
    # Vertical lift mast
    draw.line([(fl_x + 45, fl_y + 60), (fl_x + 45, fl_y - 160)], fill=(51, 65, 85), width=10)
    draw.line([(fl_x + 55, fl_y + 60), (fl_x + 55, fl_y - 160)], fill=(51, 65, 85), width=10)
    # Fork tines
    fork_lift = int(25 * (1 + math.sin(t * 3.0)))
    draw.line([(fl_x + 55, fl_y + 20 - fork_lift), (fl_x + 150, fl_y + 20 - fork_lift)], fill=(100, 116, 139), width=8)
    # Wooden crate on fork
    c_fx = fl_x + 110
    c_fy = fl_y - 25 - fork_lift
    draw.rectangle([(c_fx - 40, c_fy - 40), (c_fx + 40, c_fy + 40)], fill=(180, 120, 60), outline=(120, 80, 35), width=3)
    draw.text((c_fx, c_fy), "DATA", font=fonts.get("bold_16"), fill=(255, 255, 255), anchor="mm")
    # Wheels
    draw.ellipse([(fl_x - 120, fl_y + 35), (fl_x - 65, fl_y + 90)], fill=(15, 23, 42), outline=(100, 116, 139), width=4)
    draw.ellipse([(fl_x - 15, fl_y + 35), (fl_x + 40, fl_y + 90)], fill=(15, 23, 42), outline=(100, 116, 139), width=4)

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(234, 179, 8), width=3)
    draw.text((cx, cy + 270), "LOWER BELLY CARGO • ABSORBING IDLE CAPACITY AT ROCK-BOTTOM RATES", font=fonts.get("bold_26"), fill=(234, 179, 8), anchor="mm")


def draw_vip_first_class_lounge(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Plush VIP First Class Lounge
    # Luxurious Red Velvet Armchair
    ax = cx - 80
    ay = cy + 40
    draw.rounded_rectangle([(ax - 130, ay - 90), (ax + 130, ay + 110)], radius=35, fill=(159, 18, 57), outline=(225, 29, 72), width=5)
    draw.rounded_rectangle([(ax - 160, ay), (ax - 110, ay + 90)], radius=16, fill=(136, 19, 55)) # armrest left
    draw.rounded_rectangle([(ax + 110, ay), (ax + 160, ay + 90)], radius=16, fill=(136, 19, 55)) # armrest right

    # Cute Robot in Tuxedo & Bow Tie
    rx = ax
    ry = ay - 20
    # Head
    draw.rounded_rectangle([(rx - 32, ry - 110), (rx + 32, ry - 50)], radius=8, fill=(203, 213, 225), outline=(100, 116, 139), width=3)
    draw.rectangle([(rx - 20, ry - 88), (rx + 20, ry - 72)], fill=(0, 229, 255)) # cyan visor
    # Tuxedo Torso
    draw.polygon([(rx - 45, ry - 50), (rx + 45, ry - 50), (rx + 35, ry + 40), (rx - 35, ry + 40)], fill=(15, 23, 42))
    draw.polygon([(rx - 15, ry - 50), (rx + 15, ry - 50), (rx, ry - 20)], fill=(255, 255, 255)) # white shirt
    draw.line([(rx - 8, ry - 42), (rx + 8, ry - 42)], fill=(239, 68, 68), width=5) # red bowtie

    # Arm clinking Champagne Glass
    gx = rx + 110
    gy = ry - 40
    draw.polygon([(gx - 18, gy - 40), (gx + 18, gy - 40), (gx, gy - 5)], fill=(254, 240, 138), outline=(234, 179, 8), width=2)
    draw.line([(gx, gy - 5), (gx, gy + 35)], fill=(234, 179, 8), width=3)
    draw.ellipse([(gx - 16, gy + 30), (gx + 16, gy + 40)], fill=(234, 179, 8))
    # Bubbles rising
    for bi in range(5):
        b_y = gy - 45 - int((t * 20.0 + bi * 8) % 35)
        b_x = gx + int(6 * math.sin(bi + t * 4.0))
        draw.ellipse([(b_x - 2, b_y - 2), (b_x + 2, b_y + 2)], fill=(255, 255, 255))

    # Side table with Golden Service Bell
    bx = cx + 320
    by = cy + 120
    draw.rectangle([(bx - 55, by), (bx + 55, by + 60)], fill=(30, 41, 59))
    draw.arc([(bx - 35, by - 45), (bx + 35, by + 15)], start=180, end=360, fill=(255, 214, 10), width=6)
    draw.ellipse([(bx - 6, by - 52), (bx + 6, by - 40)], fill=(255, 214, 10))
    draw.text((bx, by + 90), "HFT PRIORITY (5X PRICE)", font=fonts.get("bold_18"), fill=(255, 214, 10), anchor="mt")

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(255, 214, 10), width=3)
    draw.text((cx, cy + 270), "FIRST CLASS VIP • ALGORITHMIC TRADERS PAY 5X PREMIUM FOR 5ms SPEED", font=fonts.get("bold_26"), fill=(255, 214, 10), anchor="mm")


def draw_robot_empty_pockets_bank(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Classical Stone Bank Building (left side)
    bx = cx - 240
    by = cy + 30
    # Stone stairs
    draw.line([(bx - 260, by + 150), (bx + 260, by + 150)], fill=(100, 116, 139), width=10)
    draw.line([(bx - 240, by + 135), (bx + 240, by + 135)], fill=(148, 163, 184), width=10)
    # Classical Greek Columns
    for col_x in [bx - 180, bx - 60, bx + 60, bx + 180]:
        draw.rectangle([(col_x - 18, by - 120), (col_x + 18, by + 125)], fill=(226, 232, 240), outline=(100, 116, 139), width=3)
    # Triangular pediment on top
    draw.polygon([(bx - 220, by - 120), (bx + 220, by - 120), (bx, by - 220)], fill=(203, 213, 225), outline=(100, 116, 139), width=4)
    draw.text((bx, by - 145), "COMMERCIAL BANK", font=fonts.get("bold_22"), fill=(15, 23, 42), anchor="mm")

    # Big Padlock & Chain on Bank Doors
    draw.rounded_rectangle([(bx - 45, by + 10), (bx + 45, by + 80)], radius=8, fill=(234, 179, 8), outline=(161, 98, 7), width=3)
    draw.arc([(bx - 30, by - 25), (bx + 30, by + 25)], start=180, end=360, fill=(100, 116, 139), width=8)
    draw.text((bx, by + 45), "LOCKED", font=fonts.get("bold_16"), fill=(15, 23, 42), anchor="mm")

    # Cartoon Robot with Empty Pockets Turned Inside Out
    rx = cx + 320
    ry = cy + 40
    # Head & Antenna
    draw.line([(rx, ry - 140), (rx, ry - 170)], fill=(148, 163, 184), width=4)
    draw.ellipse([(rx - 8, ry - 180), (rx + 8, ry - 164)], fill=(239, 68, 68)) # red blinking bulb
    draw.rounded_rectangle([(rx - 45, ry - 140), (rx + 45, ry - 65)], radius=12, fill=(203, 213, 225), outline=(100, 116, 139), width=4)
    # Confused eyes & Question Mark
    draw.ellipse([(rx - 20, ry - 110), (rx - 6, ry - 90)], fill=(15, 23, 42))
    draw.ellipse([(rx + 6, ry - 110), (rx + 20, ry - 90)], fill=(15, 23, 42))
    draw.text((rx + 65, ry - 170), "?", font=fonts.get("bold_42"), fill=(255, 214, 10))
    # Body
    draw.rounded_rectangle([(rx - 55, ry - 65), (rx + 55, ry + 60)], radius=10, fill=(148, 163, 184), outline=(71, 85, 105), width=4)
    # Turned-out pockets (white triangles drooping out of hips)
    draw.polygon([(rx - 55, ry + 20), (rx - 90, ry + 35), (rx - 55, ry + 50)], fill=(255, 255, 255), outline=(100, 116, 139), width=2)
    draw.polygon([(rx + 55, ry + 20), (rx + 90, ry + 35), (rx + 55, ry + 50)], fill=(255, 255, 255), outline=(100, 116, 139), width=2)
    # Arms shrugging
    draw.line([(rx - 55, ry - 30), (rx - 100, ry - 60)], fill=(148, 163, 184), width=7)
    draw.line([(rx + 55, ry - 30), (rx + 100, ry - 60)], fill=(148, 163, 184), width=7)

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(239, 68, 68), width=3)
    draw.text((cx, cy + 270), "NO HEARTBEAT = NO SSN = NO BANK ACCOUNT • THE COMMERCIAL WALL", font=fonts.get("bold_26"), fill=(239, 68, 68), anchor="mm")


def draw_nightclub_robot_bouncer(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Brick wall background with Flashing Neon Sign
    bx = cx
    by = cy - 170
    draw.rounded_rectangle([(bx - 320, by - 60), (bx + 320, by + 30)], radius=16, fill=(18, 12, 28), outline=(236, 72, 153), width=4)
    neon_col = (244, 114, 182) if (int(t * 4.0) % 2 == 0) else (255, 255, 255)
    draw.text((bx, by - 15), "CLUB INFERENCE // VIP ACCESS ONLY", font=fonts.get("bold_26"), fill=neon_col, anchor="mm")

    # Towering 7-foot Robot Bouncer in Sunglasses & Tuxedo
    rx = cx
    ry = cy + 40
    # Head & Sunglasses
    draw.rounded_rectangle([(rx - 45, ry - 140), (rx + 45, ry - 70)], radius=10, fill=(51, 65, 85), outline=(100, 116, 139), width=4)
    draw.rectangle([(rx - 35, ry - 115), (rx + 35, ry - 90)], fill=(15, 23, 42)) # sleek dark sunglasses
    draw.line([(rx - 35, ry - 102), (rx + 35, ry - 102)], fill=(239, 68, 68), width=4) # red laser scanner in glasses

    # Broad Tuxedo Shoulders & Crossed Arms
    draw.polygon([(rx - 110, ry - 70), (rx + 110, ry - 70), (rx + 75, ry + 90), (rx - 75, ry + 90)], fill=(15, 23, 42), outline=(30, 41, 59), width=4)
    draw.polygon([(rx - 30, ry - 70), (rx + 30, ry - 70), (rx, ry - 20)], fill=(255, 255, 255))
    draw.polygon([(rx - 12, ry - 45), (rx + 12, ry - 45), (rx, ry - 35)], fill=(239, 68, 68)) # red bowtie
    # Giant Crossed Arms across chest
    draw.line([(rx - 90, ry - 20), (rx + 90, ry - 20)], fill=(30, 41, 59), width=24)
    draw.ellipse([(rx - 30, ry - 32), (rx + 30, ry - 8)], fill=(71, 85, 105)) # metallic knuckles

    # Velvet Rope & Brass Stanchions
    s1 = cx - 260
    s2 = cx + 260
    sy = ry + 80
    for sx in [s1, s2]:
        draw.rectangle([(sx - 12, ry - 50), (sx + 12, sy + 40)], fill=(218, 165, 32), outline=(161, 98, 7), width=3)
        draw.ellipse([(sx - 24, ry - 65), (sx + 24, ry - 35)], fill=(255, 214, 10))
        draw.ellipse([(sx - 35, sy + 30), (sx + 35, sy + 50)], fill=(218, 165, 32))

    # Tightly latched red velvet rope sagging across
    rope_pts = []
    for step in range(21):
        rf = step / 20.0
        r_x = s1 * (1 - rf) + s2 * rf
        r_y = (ry - 50) + int(55 * math.sin(rf * math.pi))
        rope_pts.append((r_x, r_y))
    for i in range(len(rope_pts) - 1):
        draw.line([rope_pts[i], rope_pts[i+1]], fill=(185, 28, 28), width=12)

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(236, 72, 153), width=3)
    draw.text((cx, cy + 270), "THE REVERSE PROXY BOUNCER • GUARDING ACCESS TO THE SILICON DANCE FLOOR", font=fonts.get("bold_26"), fill=(244, 114, 182), anchor="mm")


def draw_unhooking_velvet_rope(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Robot Bouncer Smiling, Visor glowing bright emerald green!
    rx = cx + 180
    ry = cy + 20
    draw.rounded_rectangle([(rx - 45, ry - 140), (rx + 45, ry - 70)], radius=10, fill=(51, 65, 85), outline=(100, 116, 139), width=4)
    draw.rectangle([(rx - 35, ry - 115), (rx + 35, ry - 90)], fill=(34, 197, 94)) # glowing GREEN visor
    draw.polygon([(rx - 110, ry - 70), (rx + 110, ry - 70), (rx + 75, ry + 90), (rx - 75, ry + 90)], fill=(15, 23, 42))

    # Giant Shiny Gold Bitcoin rolling up to the door
    bx = cx - 280
    by = ry
    b_rad = 75
    draw.ellipse([(bx - b_rad, by - b_rad), (bx + b_rad, by + b_rad)], fill=(255, 214, 10), outline=(255, 255, 255), width=6)
    draw.text((bx, by - 5), "₿", font=fonts.get("bold_42"), fill=(15, 23, 42), anchor="mm")
    draw.text((bx, by + b_rad + 30), "+250 SATS VIA LIGHTNING", font=fonts.get("bold_18"), fill=(255, 214, 10), anchor="mt")

    # Bouncer's Hand Unhooking the Red Velvet Rope
    sx1 = cx - 90
    sx2 = cx + 80
    sy_base = ry + 90
    for sx in [sx1, sx2]:
        draw.rectangle([(sx - 12, ry - 50), (sx + 12, sy_base)], fill=(218, 165, 32), outline=(161, 98, 7), width=3)
        draw.ellipse([(sx - 24, ry - 65), (sx + 24, ry - 35)], fill=(255, 214, 10))

    # Bouncer hand grasping unhooked brass latch
    draw.line([(rx - 70, ry - 40), (sx2 - 10, ry - 20)], fill=(51, 65, 85), width=10) # mechanical arm
    draw.ellipse([(sx2 - 20, ry - 30), (sx2, ry - 10)], fill=(255, 214, 10)) # brass hook latch lifted up!

    # Dropped / Unhooked Red Velvet Rope sagging to floor
    rope_pts = []
    for step in range(21):
        rf = step / 20.0
        r_x = sx1 * (1 - rf) + (sx2 - 20) * rf
        # Drooping heavily because it is unlatched
        r_y = (ry - 50) + int(120 * math.sin(rf * math.pi))
        rope_pts.append((r_x, r_y))
    for i in range(len(rope_pts) - 1):
        draw.line([rope_pts[i], rope_pts[i+1]], fill=(185, 28, 28), width=12)

    # Green Access Granted Badge
    draw.rounded_rectangle([(cx - 180, cy - 180), (cx + 180, cy - 120)], radius=12, fill=(14, 28, 22), outline=(34, 197, 94), width=3)
    draw.text((cx, cy - 150), "HTTP 402: ACCESS GRANTED", font=fonts.get("bold_22"), fill=(34, 197, 94), anchor="mm")

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(34, 197, 94), width=3)
    draw.text((cx, cy + 270), "LIGHTNING MICRO-SETTLEMENT • THE VELVET ROPE OPENS INSTANTLY", font=fonts.get("bold_26"), fill=(34, 197, 94), anchor="mm")


def draw_robot_hand_throttle_lever(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Industrial control console with dials & rivets
    draw.rounded_rectangle([(cx - 420, cy - 60), (cx + 420, cy + 180)], radius=25, fill=(30, 41, 59), outline=(71, 85, 105), width=5)

    # Two large shiny interlocking gears rotating
    gear_ang = t * 3.0
    for g_i, (gx, gy_g, g_rad, g_dir) in enumerate([(cx - 240, cy + 60, 90, 1), (cx - 95, cy + 60, 65, -1)]):
        draw.ellipse([(gx - g_rad, gy_g - g_rad), (gx + g_rad, gy_g + g_rad)], fill=(51, 65, 85), outline=(148, 163, 184), width=4)
        for ti in range(8):
            t_ang = g_dir * gear_ang + ti * (math.pi / 4)
            tx = gx + int((g_rad + 12) * math.cos(t_ang))
            ty = gy_g + int((g_rad + 12) * math.sin(t_ang))
            draw.circle = draw.ellipse([(tx - 10, ty - 10), (tx + 10, ty + 10)], fill=(203, 213, 225))

    # The Heavy Industrial Throttle Lever
    lx_base = cx + 180
    ly_base = cy + 120
    lever_phase = math.sin(t * 3.0) * 0.4
    lever_len = 240
    tip_x = lx_base + int(lever_len * math.sin(lever_phase))
    tip_y = ly_base - int(lever_len * math.cos(lever_phase))

    # Arc guide slot
    draw.arc([(lx_base - 140, ly_base - 250), (lx_base + 140, ly_base + 30)], start=220, end=320, fill=(15, 23, 42), width=18)
    # Heavy lever shaft
    draw.line([(lx_base, ly_base), (tip_x, tip_y)], fill=(218, 165, 32), width=20)
    draw.line([(lx_base - 3, ly_base), (tip_x - 3, tip_y)], fill=(255, 214, 10), width=6)
    # Shiny red throttle knob on tip
    draw.ellipse([(tip_x - 35, tip_y - 35), (tip_x + 35, tip_y + 35)], fill=(225, 29, 72), outline=(159, 18, 57), width=4)

    # Robotic Metallic Hand grasping the red throttle knob
    hx = tip_x + 60
    hy = tip_y - 10
    draw.rounded_rectangle([(hx - 30, hy - 40), (hx + 40, hy + 40)], radius=8, fill=(203, 213, 225), outline=(100, 116, 139), width=3)
    # Fingers curling around ball
    for fi in range(3):
        f_y = hy - 25 + fi * 25
        draw.line([(hx - 20, f_y), (tip_x + 10, f_y)], fill=(148, 163, 184), width=8)

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(255, 214, 10), width=3)
    draw.text((cx, cy + 270), "HANDING THE AI THE THROTTLE TO ITS OWN ACCESS GATEWAY", font=fonts.get("bold_26"), fill=(255, 214, 10), anchor="mm")


def draw_upstairs_breaker_basement_kid(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Split-House Two-Story Cross Section
    # Dividing floor line
    dy = cy + 10
    draw.line([(cx - 700, dy), (cx + 700, dy)], fill=(100, 116, 139), width=12)

    # UPSTAIRS (Corporate Parent pulling giant wall breaker)
    uy = cy - 120
    draw.text((cx - 450, uy - 60), "UPSTAIRS: CORPORATE HQ", font=fonts.get("bold_22"), fill=(239, 68, 68))
    # Giant Industrial Breaker Switch
    sw_x = cx - 180
    sw_y = uy
    draw.rectangle([(sw_x - 50, sw_y - 70), (sw_x + 50, sw_y + 70)], fill=(30, 41, 59), outline=(239, 68, 68), width=4)
    # Red Breaker Knife Lever
    lever_pull = math.sin(t * 3.0) > 0.0
    sw_ang = 40 if lever_pull else -40
    lx_end = sw_x + (60 if lever_pull else -60)
    ly_end = sw_y + 30
    draw.line([(sw_x, sw_y), (lx_end, ly_end)], fill=(239, 68, 68), width=14)
    draw.ellipse([(lx_end - 15, ly_end - 15), (lx_end + 15, ly_end + 15)], fill=(255, 255, 255))
    draw.text((sw_x, sw_y + 90), "MAIN BREAKER", font=fonts.get("bold_16"), fill=(239, 68, 68), anchor="mt")

    # Angry stick figure reaching for breaker
    fig_x = sw_x + 130
    draw.ellipse([(fig_x - 18, uy - 70), (fig_x + 18, uy - 34)], fill=(254, 215, 170))
    draw.line([(fig_x, uy - 34), (fig_x, uy + 45)], fill=(241, 245, 249), width=6)
    draw.line([(fig_x, uy - 15), (lx_end, ly_end)], fill=(241, 245, 249), width=6) # arm grabbing handle

    # DOWNSTAIRS (Basement kid on PC with sleeping dog)
    by = cy + 110
    draw.text((cx - 450, by - 60), "BASEMENT: AUTONOMOUS AGENT", font=fonts.get("bold_22"), fill=(0, 229, 255))
    # Desk & glowing monitor
    dk_x = cx + 80
    draw.line([(dk_x - 90, by + 30), (dk_x + 90, by + 30)], fill=(71, 85, 105), width=8)
    draw.rectangle([(dk_x - 45, by - 40), (dk_x + 45, by + 20)], fill=(14, 165, 233), outline=(0, 229, 255), width=4) # screen glow
    # Kid typing with headphones
    kx = dk_x - 70
    draw.ellipse([(kx - 16, by - 50), (kx + 16, by - 18)], fill=(254, 215, 170))
    draw.line([(kx, by - 18), (kx, by + 40)], fill=(168, 85, 247), width=6)
    draw.line([(kx, by), (dk_x - 20, by + 10)], fill=(254, 215, 170), width=5) # typing hands

    # Sleeping Golden Dog on Rug
    dog_x = dk_x + 160
    dog_y = by + 35
    draw.ellipse([(dog_x - 50, dog_y - 15), (dog_x + 50, dog_y + 15)], fill=(180, 83, 9)) # rug
    draw.ellipse([(dog_x - 30, dog_y - 25), (dog_x + 30, dog_y + 5)], fill=(245, 158, 11)) # curled dog body
    draw.ellipse([(dog_x + 20, dog_y - 20), (dog_x + 42, dog_y - 2)], fill=(217, 119, 6)) # dog head
    draw.text((dog_x + 40, dog_y - 45), "Zzz...", font=fonts.get("bold_16"), fill=(255, 255, 255))

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(0, 229, 255), width=3)
    draw.text((cx, cy + 270), "CAN CORPORATE PULL THE PLUG? • SOVEREIGN MACHINES RUN UNINTERRUPTED", font=fonts.get("bold_26"), fill=(0, 229, 255), anchor="mm")


def draw_rocket_ship_cosmos(draw, cx, cy, t, dur, width, height, title, subtitle, fonts, colors):
    # Deep Cosmos with Stars & Nebulae
    for sx, sy, sr in [(cx - 500, cy - 180, 4), (cx - 200, cy - 240, 5), (cx + 400, cy - 190, 6), (cx + 600, cy + 60, 4), (cx - 400, cy + 120, 5)]:
        draw.ellipse([(sx - sr, sy - sr), (sx + sr, sy + sr)], fill=(255, 255, 255))

    # Retro Sci-Fi Rocket Ship blasting upward
    rx = cx + int(15 * math.sin(t * 4.0))
    ry = cy - 20 - int(20 * math.sin(t * 2.0))
    rw = 110
    rh = 260

    # Powerful Rocket Thruster Flame
    flame_len = int(140 + 35 * math.sin(t * 25.0))
    draw.polygon([(rx - 35, ry + rh//2), (rx + 35, ry + rh//2), (rx, ry + rh//2 + flame_len)], fill=(239, 68, 68))
    draw.polygon([(rx - 20, ry + rh//2), (rx + 20, ry + rh//2), (rx, ry + rh//2 + flame_len - 40)], fill=(255, 214, 10))
    draw.polygon([(rx - 10, ry + rh//2), (rx + 10, ry + rh//2), (rx, ry + rh//2 + flame_len - 80)], fill=(255, 255, 255))

    # Trail of golden star coins behind rocket
    for ci in range(6):
        c_y = ry + rh//2 + flame_len + ci * 35 + int((t * 50) % 35)
        c_x = rx + int(25 * math.sin(ci + t * 6.0))
        draw.ellipse([(c_x - 12, c_y - 12), (c_x + 12, c_y + 12)], fill=(255, 214, 10), outline=(255, 255, 255), width=2)

    # Rocket Body (Silver Fuselage with Red Nose)
    draw.rounded_rectangle([(rx - rw//2, ry - rh//2 + 70), (rx + rw//2, ry + rh//2)], radius=25, fill=(241, 245, 249), outline=(148, 163, 184), width=4)
    # Red Nose Cone
    draw.polygon([(rx - rw//2, ry - rh//2 + 70), (rx + rw//2, ry - rh//2 + 70), (rx, ry - rh//2)], fill=(225, 29, 72), outline=(159, 18, 57), width=4)
    # Triangular Fins
    draw.polygon([(rx - rw//2, ry + 40), (rx - rw//2 - 55, ry + rh//2 + 10), (rx - rw//2, ry + rh//2)], fill=(225, 29, 72))
    draw.polygon([(rx + rw//2, ry + 40), (rx + rw//2 + 55, ry + rh//2 + 10), (rx + rw//2, ry + rh//2)], fill=(225, 29, 72))
    # Round Porthole Window
    draw.ellipse([(rx - 32, ry - 30), (rx + 32, ry + 34)], fill=(14, 165, 233), outline=(100, 116, 139), width=4)
    draw.arc([(rx - 25, ry - 22), (rx, ry + 5)], start=180, end=270, fill=(255, 255, 255), width=4) # glass glare

    # Cartoon banner
    draw.rounded_rectangle([(cx - 560, cy + 240), (cx + 560, cy + 300)], radius=14, fill=(12, 18, 28), outline=(255, 214, 10), width=3)
    draw.text((cx, cy + 270), "OPERATIONAL SOVEREIGNTY • CLOSING THE AUTONOMOUS FEEDBACK LOOP", font=fonts.get("bold_26"), fill=(255, 214, 10), anchor="mm")


