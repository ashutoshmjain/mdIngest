from manim import *
import numpy as np

# COMPATIBILITY SHIMS
ease_in_out_sine = smooth
ease_in_sine = smooth
ease_out_sine = smooth
def ShowCreationThenFadeOut(mob):
    return Succession(Create(mob), FadeOut(mob))

config.pixel_width = 740
config.pixel_height = 740
config.frame_width = 8.0
config.frame_height = 8.0
config.background_color = "#000000"

def get_footer_bar(category_str="KineticVector"):
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#334155", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.6)
    left_text = Text(category_str, font="Arial", weight=NORMAL, font_size=10, color="#64748b").next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("deepDive podcast", font="Arial", weight=NORMAL, font_size=10, color="#64748b").next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    return VGroup(footer_line, left_text, right_text)


# ==============================================================================
# Scene 01: Aging & Relentless Time (Hourglass & Escapement Gear)
# Spoken: "So what if the reason you age, the reason time just relentlessly moves forward has absolutely nothing to do with the"
# ==============================================================================
class Scene01_01(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # Hourglass frame
        top_bar = Line(LEFT * 1.2, RIGHT * 1.2, color="#FFFFFF", stroke_width=3).move_to(UP * 0.2)
        bot_bar = Line(LEFT * 1.2, RIGHT * 1.2, color="#FFFFFF", stroke_width=3).move_to(DOWN * 2.2)
        left_strut = Line(top_bar.get_left(), bot_bar.get_left(), color="#FFFFFF", stroke_width=1.5).set_opacity(0.4)
        right_strut = Line(top_bar.get_right(), bot_bar.get_right(), color="#FFFFFF", stroke_width=1.5).set_opacity(0.4)

        glass_top = Polygon(
            top_bar.get_left() + RIGHT * 0.1,
            top_bar.get_right() + LEFT * 0.1,
            DOWN * 1.0,
            color="#FFFFFF", stroke_width=2.5, fill_opacity=0.08
        )
        glass_bot = Polygon(
            DOWN * 1.0,
            bot_bar.get_right() + LEFT * 0.1,
            bot_bar.get_left() + RIGHT * 0.1,
            color="#FFFFFF", stroke_width=2.5, fill_opacity=0.08
        )

        sand_top = Polygon(
            glass_top.get_top() + DOWN * 0.1 + LEFT * 0.9,
            glass_top.get_top() + DOWN * 0.1 + RIGHT * 0.9,
            DOWN * 1.0,
            color="#FFFFFF", fill_opacity=0.85, stroke_width=0
        )
        stream = Line(DOWN * 1.0, DOWN * 2.1, color="#FFFFFF", stroke_width=2)
        sand_pile = Polygon(
            DOWN * 2.15 + LEFT * 0.8,
            DOWN * 2.15 + RIGHT * 0.8,
            DOWN * 1.8,
            color="#FFFFFF", fill_opacity=0.9, stroke_width=0
        )

        # Rotating escapement gear behind
        gear_center = DOWN * 1.0
        teeth = VGroup()
        for i in range(12):
            ang = i * (2 * PI / 12)
            pt1 = gear_center + np.array([np.cos(ang) * 1.7, np.sin(ang) * 1.7, 0])
            pt2 = gear_center + np.array([np.cos(ang + 0.1) * 1.9, np.sin(ang + 0.1) * 1.9, 0])
            pt3 = gear_center + np.array([np.cos(ang + 0.2) * 1.7, np.sin(ang + 0.2) * 1.7, 0])
            teeth.add(Polygon(pt1, pt2, pt3, color="#FFFFFF", stroke_width=1.5).set_opacity(0.35))
        gear_ring = Circle(radius=1.7, color="#FFFFFF", stroke_width=1.5).move_to(gear_center).set_opacity(0.35)
        gear = VGroup(gear_ring, teeth)

        hourglass = VGroup(top_bar, bot_bar, left_strut, right_strut, glass_top, glass_bot)

        self.play(FadeIn(gear), FadeIn(hourglass), run_time=1.2)
        self.play(FadeIn(sand_top), Create(stream), FadeIn(sand_pile), run_time=1.0)
        self.play(
            Rotate(gear, angle=PI / 2, run_time=4.0, rate_func=linear),
            sand_top.animate.scale([0.1, 0.1, 1], about_point=DOWN * 1.0).set_opacity(0.1),
            sand_pile.animate.scale([1.4, 1.4, 1], about_point=DOWN * 2.15)
        )
        self.wait(1.3)


# ==============================================================================
# Scene 02: Biological Lens vs River (DNA Double Helix & Biometric Eye)
# Spoken: "universe itself? Right. Like what if it's entirely about your own biology? Exactly. What if time isn't, you know, a flowing river, but basically"
# ==============================================================================
class Scene02_02(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # DNA Double Helix strand running horizontally
        helix_rungs = VGroup()
        curve1_pts = []
        curve2_pts = []
        xs = np.linspace(-2.8, 2.8, 24)
        for x in xs:
            y1 = np.sin(x * 2.2) * 0.6 - 1.0
            y2 = -np.sin(x * 2.2) * 0.6 - 1.0
            curve1_pts.append([x, y1, 0])
            curve2_pts.append([x, y2, 0])
            if len(curve1_pts) % 2 == 0:
                rung = Line([x, y1, 0], [x, y2, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5)
                node1 = Dot([x, y1, 0], radius=0.06, color="#FFFFFF")
                node2 = Dot([x, y2, 0], radius=0.06, color="#FFD700")
                helix_rungs.add(VGroup(rung, node1, node2))

        strand1 = VMobject(color="#FFFFFF", stroke_width=2.5)
        strand1.set_points_smoothly([np.array(p) for p in curve1_pts])
        strand2 = VMobject(color="#FFFFFF", stroke_width=2.5)
        strand2.set_points_smoothly([np.array(p) for p in curve2_pts])

        # Biological focal eye lens aperture above
        eye_top = Arc(radius=2.0, start_angle=PI * 0.25, angle=PI * 0.5, color="#FFFFFF", stroke_width=2).move_to(UP * 0.0)
        eye_bot = Arc(radius=2.0, start_angle=-PI * 0.75, angle=PI * 0.5, color="#FFFFFF", stroke_width=2).move_to(DOWN * 0.6)
        pupil = Circle(radius=0.35, color="#FFD700", stroke_width=2.5, fill_opacity=0.15).move_to(DOWN * 0.3)
        pupil_inner = Dot(DOWN * 0.3, radius=0.12, color="#FFFFFF")
        lens = VGroup(eye_top, eye_bot, pupil, pupil_inner)

        self.play(Create(strand1), Create(strand2), run_time=1.4)
        self.play(Create(helix_rungs), FadeIn(lens), run_time=1.5)
        self.play(
            pupil.animate.scale(1.5).set_opacity(0.35),
            helix_rungs.animate.shift(LEFT * 0.4),
            run_time=3.2,
            rate_func=ease_in_out_sine
        )
        self.wait(1.4)


# ==============================================================================
# Scene 03: Sensory Exhaust (Five Senses Pentagonal Hub & Exhaust Fumes)
# Spoken: "just the exhaust fume of your five senses? It's a wild thought. It really is."
# ==============================================================================
class Scene03_03(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        center_hub = Circle(radius=0.45, color="#FFFFFF", stroke_width=3, fill_opacity=0.2).move_to(LEFT * 1.2 + DOWN * 1.0)
        core_label = Text("5 SENSES", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").move_to(center_hub.get_center())

        # 5 sensory intake conduits
        intakes = VGroup()
        for i in range(5):
            ang = PI * 0.6 + i * (2 * PI / 5.5)
            pt_end = center_hub.get_center() + np.array([np.cos(ang) * 1.4, np.sin(ang) * 1.0, 0])
            line = Arrow(pt_end, center_hub.get_center() + np.array([np.cos(ang) * 0.45, np.sin(ang) * 0.45, 0]), buff=0, color="#FFFFFF", stroke_width=2, max_tip_length_to_length_ratio=0.2)
            dot = Dot(pt_end, radius=0.08, color="#FFD700")
            intakes.add(VGroup(line, dot))

        # Exhaust manifold emitting trailing cloud trails to the right
        exhaust_pipe = Line(center_hub.get_right(), center_hub.get_right() + RIGHT * 0.8, color="#FFFFFF", stroke_width=4)
        
        clouds = VGroup()
        for i in range(7):
            cx = center_hub.get_right()[0] + 0.8 + (i * 0.35)
            cy = center_hub.get_center()[1] + np.sin(i * 1.2) * 0.3
            r = 0.15 + (i * 0.08)
            cloud = Circle(radius=r, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.15 - (i * 0.015)).move_to([cx, cy, 0])
            clouds.add(cloud)

        fume_tag = Text("EXHAUST TIME", font="Arial", weight=BOLD, font_size=9, color="#64748b").next_to(clouds, UP, buff=0.2)

        self.play(FadeIn(center_hub), FadeIn(core_label), Create(intakes), run_time=1.4)
        self.play(Create(exhaust_pipe), FadeIn(fume_tag), run_time=0.8)
        self.play(
            LaggedStart(*[GrowFromCenter(c) for c in clouds], lag_ratio=0.18),
            clouds.animate.shift(RIGHT * 0.6).set_opacity(0.4),
            run_time=3.8,
            rate_func=linear
        )
        self.wait(1.5)


# ==============================================================================
# Scene 04: Submarine Deep Dive (Descent Capsule & Precision Sonar Depth)
# Spoken: "Today we are going on a massive deep dive. We're taking that desire for visible,"
# ==============================================================================
class Scene04_04(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # Depth measurement scale along left
        depth_axis = Line(UP * 0.3, DOWN * 2.4, color="#334155", stroke_width=2).move_to(LEFT * 2.5 + DOWN * 1.05)
        ticks = VGroup()
        for i in range(6):
            y = 0.2 - i * 0.5
            t_line = Line(LEFT * 0.15, RIGHT * 0.15, color="#64748b", stroke_width=1.5).move_to([LEFT[0] * 2.5, y, 0])
            t_val = Text(f"-{i*200}m", font="Consolas", font_size=8, color="#64748b").next_to(t_line, LEFT, buff=0.1)
            ticks.add(t_line, t_val)

        # Deep dive bathysphere capsule
        capsule_body = Circle(radius=0.75, color="#FFFFFF", stroke_width=3, fill_opacity=0.25).move_to(UP * 0.1)
        porthole = Circle(radius=0.35, color="#FFFFFF", stroke_width=2, fill_opacity=0.6).move_to(capsule_body.get_center())
        cross1 = Line(porthole.get_left(), porthole.get_right(), color="#000000", stroke_width=1.5)
        cross2 = Line(porthole.get_top(), porthole.get_bottom(), color="#000000", stroke_width=1.5)
        antenna = Line(capsule_body.get_top(), capsule_body.get_top() + UP * 0.4, color="#FFFFFF", stroke_width=2)
        capsule = VGroup(capsule_body, porthole, cross1, cross2, antenna)

        # Spotlight cone projecting down-right into abyss
        light_cone = Polygon(
            capsule_body.get_bottom() + RIGHT * 0.2,
            DOWN * 2.3 + RIGHT * 0.5,
            DOWN * 2.3 + RIGHT * 2.8,
            color="#FFD700", fill_opacity=0.12, stroke_width=1.5
        )

        self.play(Create(depth_axis), FadeIn(ticks), FadeIn(capsule), run_time=1.2)
        self.play(FadeIn(light_cone), run_time=0.8)
        self.play(
            capsule.animate.shift(DOWN * 1.3),
            light_cone.animate.shift(DOWN * 0.5).scale(1.2),
            run_time=4.2,
            rate_func=ease_in_out_sine
        )
        self.wait(1.3)


# ==============================================================================
# Scene 05: Medical X-Ray Diagnostic Precision (Laser Scanner & Lattice)
# Spoken: "categorized precision, like what you'd want from a medical x -ray, and we're applying it to the fundamental nature of reality. And"
# ==============================================================================
class Scene05_05(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # Diagnostic specimen frame
        specimen_frame = RoundedRectangle(width=4.4, height=2.4, corner_radius=0.1, color="#334155", stroke_width=2).move_to(DOWN * 1.0)
        reticle_tl = Line(UP * 0.2 + LEFT * 0.2, UP * 0.2, color="#FFFFFF", stroke_width=2).move_to(specimen_frame.get_corner(UL) + DR * 0.2)
        reticle_br = Line(DOWN * 0.2 + RIGHT * 0.2, DOWN * 0.2, color="#FFFFFF", stroke_width=2).move_to(specimen_frame.get_corner(DR) + UL * 0.2)

        # Fundamental atomic lattice grid inside
        lattice_dots = VGroup()
        lattice_lines = VGroup()
        for ix in range(5):
            for iy in range(3):
                pt = np.array([-1.6 + ix * 0.8, -1.8 + iy * 0.8, 0])
                lattice_dots.add(Dot(pt, radius=0.07, color="#FFFFFF"))
                if ix < 4:
                    lattice_lines.add(Line(pt, pt + RIGHT * 0.8, color="#FFFFFF", stroke_width=1).set_opacity(0.3))
                if iy < 2:
                    lattice_lines.add(Line(pt, pt + UP * 0.8, color="#FFFFFF", stroke_width=1).set_opacity(0.3))

        # Vertical scanning X-Ray laser beam
        scan_bar = Line(specimen_frame.get_top() + LEFT * 2.0, specimen_frame.get_bottom() + LEFT * 2.0, color="#FFD700", stroke_width=3.5)
        scan_glow = Line(specimen_frame.get_top() + LEFT * 2.0, specimen_frame.get_bottom() + LEFT * 2.0, color="#FFD700", stroke_width=8).set_opacity(0.25)
        scanner = VGroup(scan_bar, scan_glow)

        self.play(Create(specimen_frame), FadeIn(reticle_tl), FadeIn(reticle_br), run_time=1.0)
        self.play(Create(lattice_lines), FadeIn(lattice_dots), run_time=1.2)
        self.play(FadeIn(scanner), run_time=0.5)
        self.play(
            scanner.animate.shift(RIGHT * 4.0),
            run_time=3.5,
            rate_func=linear
        )
        self.wait(1.3)


# ==============================================================================
# Scene 06: Mind-Bending Diagnostic Landscape (Curved Spacetime Warp)
# Spoken: "I got to warn you, the diagnostic landscape we are looking at in this research is, well, it is completely mind bending. Yeah, to say the"
# ==============================================================================
class Scene06_06(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # 2D topological grid that bends downward into a gravitational funnel
        grid_lines = VGroup()
        for x in np.linspace(-2.8, 2.8, 11):
            pts = []
            for y in np.linspace(0.2, -2.2, 15):
                dist = np.sqrt(x**2 + (y + 1.0)**2)
                disp = -0.55 / (1.0 + (dist * 1.5)**2)
                pts.append([x, y + disp, 0])
            line = VMobject(color="#FFFFFF", stroke_width=1.2).set_opacity(0.4)
            line.set_points_smoothly([np.array(p) for p in pts])
            grid_lines.add(line)

        for y in np.linspace(0.2, -2.2, 9):
            pts = []
            for x in np.linspace(-2.8, 2.8, 21):
                dist = np.sqrt(x**2 + (y + 1.0)**2)
                disp = -0.55 / (1.0 + (dist * 1.5)**2)
                pts.append([x, y + disp, 0])
            line = VMobject(color="#FFFFFF", stroke_width=1.2).set_opacity(0.4)
            line.set_points_smoothly([np.array(p) for p in pts])
            grid_lines.add(line)

        # Core singularity knot at center
        knot = Circle(radius=0.25, color="#FFD700", stroke_width=3, fill_opacity=0.9).move_to(DOWN * 1.35)
        pulse_rings = VGroup(*[Circle(radius=0.4 + i*0.35, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 1.35).set_opacity(0.6 - i*0.15) for i in range(3)])

        self.play(Create(grid_lines), run_time=1.8)
        self.play(FadeIn(knot), FadeIn(pulse_rings), run_time=1.0)
        self.play(
            Rotate(grid_lines, angle=PI / 6, about_point=DOWN * 1.35),
            pulse_rings.animate.scale(1.4).set_opacity(0.0),
            knot.animate.scale(1.2),
            run_time=3.5,
            rate_func=ease_in_out_sine
        )
        self.wait(1.2)


# ==============================================================================
# Scene 07: White Paper Redefining Reality (Paper Blueprint & Geometry)
# Spoken: "least. So what's our mission today? We are going to explore this incredible white paper that redefines reality through pure geometry."
# ==============================================================================
class Scene07_07(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # White research paper sheet
        sheet = RoundedRectangle(width=2.2, height=2.8, corner_radius=0.08, color="#FFFFFF", stroke_width=2.5, fill_opacity=0.1).move_to(LEFT * 1.4 + DOWN * 1.0)
        header_bar = Line(sheet.get_top() + DOWN * 0.3 + LEFT * 0.8, sheet.get_top() + DOWN * 0.3 + RIGHT * 0.8, color="#FFD700", stroke_width=3)
        doc_lines = VGroup(*[Line(sheet.get_top() + DOWN * (0.6 + i*0.25) + LEFT * 0.8, sheet.get_top() + DOWN * (0.6 + i*0.25) + RIGHT * 0.8, color="#FFFFFF", stroke_width=1.5).set_opacity(0.4) for i in range(6)])
        paper = VGroup(sheet, header_bar, doc_lines)

        # Geometric transformation arrow
        arrow = Arrow(LEFT * 0.1 + DOWN * 1.0, RIGHT * 0.8 + DOWN * 1.0, color="#FFFFFF", stroke_width=3, max_tip_length_to_length_ratio=0.25)

        # Unfolding 3D geometric polyhedra (Tetrahedron & Cube projection)
        poly_center = RIGHT * 2.0 + DOWN * 1.0
        p1 = poly_center + UP * 0.9
        p2 = poly_center + DOWN * 0.7 + LEFT * 0.9
        p3 = poly_center + DOWN * 0.7 + RIGHT * 0.9
        p4 = poly_center + DOWN * 0.2
        poly_faces = VGroup(
            Polygon(p1, p2, p4, color="#FFFFFF", stroke_width=2, fill_opacity=0.15),
            Polygon(p1, p3, p4, color="#FFFFFF", stroke_width=2, fill_opacity=0.25),
            Polygon(p2, p3, p4, color="#FFFFFF", stroke_width=2, fill_opacity=0.35),
            Line(p1, p2, color="#FFFFFF", stroke_width=2.5),
            Line(p1, p3, color="#FFFFFF", stroke_width=2.5),
            Line(p2, p3, color="#FFFFFF", stroke_width=2.5)
        )

        self.play(FadeIn(paper), run_time=1.2)
        self.play(GrowArrow(arrow), run_time=0.8)
        self.play(Create(poly_faces), run_time=1.8)
        self.play(
            Rotate(poly_faces, angle=PI / 2, about_point=poly_center),
            run_time=2.5,
            rate_func=ease_in_out_sine
        )
        self.wait(1.2)


# ==============================================================================
# Scene 08: Quantum Cloud Swept Away (Murky Wavy Cloud vs Sharp Razor Lines)
# Spoken: "Right. For a century, quantum physics has relied on these murky, highly abstract symmetries. But this research replaces"
# ==============================================================================
class Scene08_08(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # Murky abstract wavy probability cloud
        cloud_rings = VGroup()
        for i in range(16):
            ang = i * (2 * PI / 16)
            rad = 1.0 + np.sin(i * 3.0) * 0.35
            pt = DOWN * 1.0 + np.array([np.cos(ang) * rad, np.sin(ang) * rad, 0])
            cloud_rings.add(Circle(radius=0.45, color="#64748b", stroke_width=1.5, fill_opacity=0.1).move_to(pt))
        murky_label = Text("MURKY SYMMETRIES", font="Arial", weight=BOLD, font_size=11, color="#64748b").move_to(DOWN * 1.0)
        cloud = VGroup(cloud_rings, murky_label)

        # Razor-sharp geometric slicing barrier
        blade = Line(UP * 0.3 + LEFT * 2.8, DOWN * 2.3 + LEFT * 2.8, color="#FFFFFF", stroke_width=4)
        blade_edge = Line(UP * 0.3 + LEFT * 2.8, DOWN * 2.3 + LEFT * 2.8, color="#FFD700", stroke_width=1.5)
        razor = VGroup(blade, blade_edge)

        # Clean geometric vectors following behind
        clean_square = Square(side_length=1.4, color="#FFFFFF", stroke_width=2.5).move_to(LEFT * 3.8 + DOWN * 1.0)
        clean_diag = Line(clean_square.get_corner(DL), clean_square.get_corner(UR), color="#FFFFFF", stroke_width=2)
        clean_geom = VGroup(clean_square, clean_diag)

        self.play(FadeIn(cloud), run_time=1.4)
        self.play(FadeIn(razor), FadeIn(clean_geom), run_time=0.8)
        self.play(
            razor.animate.shift(RIGHT * 4.6),
            clean_geom.animate.shift(RIGHT * 3.8),
            cloud.animate.set_opacity(0.0).scale(0.4),
            run_time=3.8,
            rate_func=ease_in_out_sine
        )
        self.wait(1.5)


# ==============================================================================
# Scene 09: Inescapable 3D Geometry (X,Y,Z Coordinate Frame, Quark Triad, Charge)
# Spoken: "all that quantum magic with inescapable three -dimensional geometry. I mean, we're talking about showing how quarks, photons, charge, and"
# ==============================================================================
class Scene09_09(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        origin = DOWN * 1.2
        # 3D Coordinate Orthogonal Frame
        axis_x = Arrow(origin, origin + RIGHT * 2.2, buff=0, color="#FFFFFF", stroke_width=2.5, max_tip_length_to_length_ratio=0.15)
        axis_y = Arrow(origin, origin + UP * 1.5, buff=0, color="#FFFFFF", stroke_width=2.5, max_tip_length_to_length_ratio=0.15)
        axis_z = Arrow(origin, origin + DL * 1.2, buff=0, color="#FFFFFF", stroke_width=2.5, max_tip_length_to_length_ratio=0.15)
        lbl_x = Text("X", font="Consolas", font_size=10, color="#FFFFFF").next_to(axis_x, RIGHT, buff=0.1)
        lbl_y = Text("Y", font="Consolas", font_size=10, color="#FFFFFF").next_to(axis_y, UP, buff=0.1)
        lbl_z = Text("Z", font="Consolas", font_size=10, color="#FFFFFF").next_to(axis_z, DL, buff=0.1)
        axes = VGroup(axis_x, axis_y, axis_z, lbl_x, lbl_y, lbl_z)

        # Quark triad: 3 colored charge nodes in equilateral triangle
        q1 = Dot(origin + UP * 0.9 + RIGHT * 0.8, radius=0.14, color="#FFD700")
        q2 = Dot(origin + DOWN * 0.2 + RIGHT * 1.4, radius=0.14, color="#FFFFFF")
        q3 = Dot(origin + DOWN * 0.4 + RIGHT * 0.4, radius=0.14, color="#FFFFFF")
        bond1 = Line(q1.get_center(), q2.get_center(), color="#FFFFFF", stroke_width=1.5).set_opacity(0.6)
        bond2 = Line(q2.get_center(), q3.get_center(), color="#FFFFFF", stroke_width=1.5).set_opacity(0.6)
        bond3 = Line(q3.get_center(), q1.get_center(), color="#FFFFFF", stroke_width=1.5).set_opacity(0.6)
        quark_cluster = VGroup(bond1, bond2, bond3, q1, q2, q3)

        # Photon sinusoidal transverse wave
        wave_pts = [np.array([-2.4 + i*0.2, -1.2 + np.sin(i*0.9)*0.4, 0]) for i in range(12)]
        photon_wave = VMobject(color="#FFD700", stroke_width=2)
        photon_wave.set_points_smoothly(wave_pts)

        self.play(Create(axes), run_time=1.4)
        self.play(Create(quark_cluster), Create(photon_wave), run_time=1.8)
        self.play(
            Rotate(quark_cluster, angle=PI, about_point=origin + UP * 0.3 + RIGHT * 0.8),
            photon_wave.animate.shift(RIGHT * 0.5),
            run_time=3.0,
            rate_func=linear
        )
        self.wait(1.3)


# ==============================================================================
# Scene 10: Spatial Rotations to Time (Concentric Gimbal Rings & Time Arrow)
# Spoken: "even time itself just emerge from spatial rotations. Exactly. But we're going to take our time. This deep dive is going to be slow,"
# ==============================================================================
class Scene10_10(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        center = DOWN * 1.0
        # 3 Concentric Gimbal rings
        ring1 = Circle(radius=1.8, color="#FFFFFF", stroke_width=2.5).move_to(center).set_opacity(0.8)
        ring2 = Ellipse(width=3.2, height=1.6, color="#FFFFFF", stroke_width=2).move_to(center).set_opacity(0.6)
        ring3 = Ellipse(width=1.4, height=3.0, color="#FFFFFF", stroke_width=2).move_to(center).set_opacity(0.6)
        gimbal = VGroup(ring1, ring2, ring3)

        # Central core chronon node
        core_node = Dot(center, radius=0.18, color="#FFD700")

        # Emergent Time Vector arrow projecting forward
        time_vector = Arrow(center, center + RIGHT * 2.2 + UP * 0.8, buff=0, color="#FFD700", stroke_width=3.5, max_tip_length_to_length_ratio=0.2)
        t_label = Text("EMERGENT TIME", font="Arial", weight=BOLD, font_size=10, color="#FFD700").next_to(time_vector.get_end(), UP, buff=0.1)

        self.play(FadeIn(gimbal), FadeIn(core_node), run_time=1.4)
        self.play(GrowArrow(time_vector), FadeIn(t_label), run_time=1.0)
        self.play(
            Rotate(ring1, angle=PI / 2, run_time=3.5, rate_func=linear),
            Rotate(ring2, angle=-PI / 2, run_time=3.5, rate_func=linear),
            Rotate(ring3, angle=PI, run_time=3.5, rate_func=linear),
            core_node.animate.scale(1.3)
        )
        self.wait(1.6)


# ==============================================================================
# Scene 11: Recursive Ground-Up Foundation (Foundation Blocks Stacking)
# Spoken: "recursive, layered. We really want to build this from the ground up. Yeah, you really have to with this material. So we need to establish"
# ==============================================================================
class Scene11_11(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # Bedrock baseline
        bedrock = Line(LEFT * 3.0, RIGHT * 3.0, color="#FFFFFF", stroke_width=3).move_to(DOWN * 2.2)

        # Layer 1: Ground foundation stones
        b1 = Rectangle(width=1.4, height=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to(DOWN * 1.9 + LEFT * 1.5)
        b2 = Rectangle(width=1.4, height=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to(DOWN * 1.9)
        b3 = Rectangle(width=1.4, height=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to(DOWN * 1.9 + RIGHT * 1.5)
        layer1 = VGroup(b1, b2, b3)

        # Layer 2: Middle structural blocks
        m1 = Rectangle(width=1.8, height=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.5).move_to(DOWN * 1.35 + LEFT * 0.95)
        m2 = Rectangle(width=1.8, height=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.5).move_to(DOWN * 1.35 + RIGHT * 0.95)
        layer2 = VGroup(m1, m2)

        # Layer 3: Keystone arch block
        keystone = Rectangle(width=2.2, height=0.6, color="#FFD700", stroke_width=3, fill_opacity=0.4).move_to(DOWN * 0.75)
        k_label = Text("GROUND TRUTH", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").move_to(keystone.get_center())
        layer3 = VGroup(keystone, k_label)

        self.play(Create(bedrock), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.3) for b in layer1], lag_ratio=0.2), run_time=1.4)
        self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.3) for m in layer2], lag_ratio=0.2), run_time=1.4)
        self.play(FadeIn(layer3, shift=DOWN * 0.4), run_time=1.2)
        self.play(keystone.animate.set_stroke(color="#FFFFFF", width=4), run_time=1.2)
        self.wait(1.5)


# ==============================================================================
# Scene 12: Anchor Line Premise (Heavy Nautical Anchor Locking on Baseline)
# Spoken: "an anchor line right now, a premise you need to keep in the back of your mind for this whole deep dive. Are you ready? Let's hear it. Okay. So"
# ==============================================================================
class Scene12_12(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        baseline = Line(LEFT * 3.0, RIGHT * 3.0, color="#334155", stroke_width=2).move_to(DOWN * 2.2)

        # Heavy Anchor Geometry
        anchor_shank = Line(UP * 0.2, DOWN * 1.8, color="#FFFFFF", stroke_width=5)
        anchor_ring = Circle(radius=0.25, color="#FFFFFF", stroke_width=3.5).next_to(anchor_shank, UP, buff=0)
        stock = Line(LEFT * 1.0, RIGHT * 1.0, color="#FFFFFF", stroke_width=4).move_to(anchor_shank.get_top() + DOWN * 0.3)
        
        # Flukes (curved arms at bottom)
        fluke_arc = Arc(radius=1.1, start_angle=-PI * 0.85, angle=PI * 0.7, color="#FFFFFF", stroke_width=5).move_to(DOWN * 1.8)
        left_tip = Triangle(color="#FFFFFF").scale(0.12).rotate(PI * 0.35).move_to(fluke_arc.get_left())
        right_tip = Triangle(color="#FFFFFF").scale(0.12).rotate(-PI * 0.35).move_to(fluke_arc.get_right())
        flukes = VGroup(fluke_arc, left_tip, right_tip)

        anchor = VGroup(anchor_ring, stock, anchor_shank, flukes).move_to(UP * 0.8)

        # Tension chain links from top
        chain = VGroup(*[Circle(radius=0.1, color="#64748b", stroke_width=1.5).move_to(UP * (1.6 - i*0.25)) for i in range(5)])

        self.play(Create(baseline), FadeIn(chain), FadeIn(anchor), run_time=1.2)
        self.play(
            anchor.animate.move_to(DOWN * 1.1),
            run_time=2.2,
            rate_func=ease_in_sine
        )
        # Impact shockwave
        shockwave = Line(LEFT * 2.2, RIGHT * 2.2, color="#FFD700", stroke_width=3).move_to(DOWN * 2.2)
        self.play(
            Create(shockwave),
            flukes.animate.set_color("#FFD700"),
            run_time=0.8
        )
        self.play(FadeOut(shockwave), run_time=0.8)
        self.wait(1.5)


# ==============================================================================
# Scene 13: Chiral Instantiation (Mirror Plane & Handed Chiral Spirals)
# Spoken: "intelligence is nothing but an abstraction of the physical world. Right. Or to flip it around, the physical world is a chiral"
# ==============================================================================
class Scene13_13(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # Central Mirror Plane Divider
        mirror_line = DashedLine(UP * 0.3, DOWN * 2.3, color="#64748b", stroke_width=2).move_to(DOWN * 1.0)
        lbl_left = Text("INTELLIGENCE", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").move_to(LEFT * 1.8 + UP * 0.1)
        lbl_right = Text("PHYSICAL CHIRAL", font="Arial", weight=BOLD, font_size=10, color="#FFD700").move_to(RIGHT * 1.8 + UP * 0.1)

        # Left chiral spiral (counter-clockwise)
        t_vals = np.linspace(0, 3 * PI, 60)
        left_pts = [np.array([-1.8 + (t/10.0)*np.cos(t), -1.1 + (t/10.0)*np.sin(t), 0]) for t in t_vals]
        left_spiral = VMobject(color="#FFFFFF", stroke_width=3)
        left_spiral.set_points_smoothly(left_pts)

        # Right chiral twin spiral (clockwise mirrored)
        right_pts = [np.array([1.8 - (t/10.0)*np.cos(t), -1.1 + (t/10.0)*np.sin(t), 0]) for t in t_vals]
        right_spiral = VMobject(color="#FFD700", stroke_width=3)
        right_spiral.set_points_smoothly(right_pts)

        self.play(Create(mirror_line), FadeIn(lbl_left), FadeIn(lbl_right), run_time=1.2)
        self.play(Create(left_spiral), run_time=1.8)
        self.play(Create(right_spiral), run_time=1.8)
        self.play(
            Rotate(left_spiral, angle=PI, about_point=LEFT * 1.8 + DOWN * 1.1),
            Rotate(right_spiral, angle=-PI, about_point=RIGHT * 1.8 + DOWN * 1.1),
            run_time=2.2,
            rate_func=ease_in_out_sine
        )
        self.wait(1.5)


# ==============================================================================
# Scene 14: Sensory Instantiation (Cognitive Hub Projecting 5 Sensory Conduits)
# Spoken: "instantiation of intelligence. Which is a heavy sentence, I know. Right. But here's the rest of it. Our five senses basically"
# ==============================================================================
class Scene14_14(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        hub = Circle(radius=0.5, color="#FFFFFF", stroke_width=3, fill_opacity=0.3).move_to(DOWN * 1.0)
        hub_dot = Dot(hub.get_center(), radius=0.15, color="#FFD700")
        hub_group = VGroup(hub, hub_dot)

        # 5 sensory projection beams
        channels = VGroup()
        target_nodes = VGroup()
        for i in range(5):
            angle = i * (2 * PI / 5) - PI / 2
            end_pt = hub.get_center() + np.array([np.cos(angle) * 1.9, np.sin(angle) * 1.1, 0])
            beam = Line(hub.get_center(), end_pt, color="#FFFFFF", stroke_width=2).set_opacity(0.4)
            node = Circle(radius=0.18, color="#FFFFFF", stroke_width=2, fill_opacity=0.8).move_to(end_pt)
            dot = Dot(end_pt, radius=0.06, color="#FFD700")
            channels.add(beam)
            target_nodes.add(VGroup(node, dot))

        self.play(FadeIn(hub_group), run_time=1.0)
        self.play(Create(channels), run_time=1.5)
        self.play(FadeIn(target_nodes), run_time=1.2)
        self.play(
            hub.animate.scale(1.2),
            channels.animate.set_opacity(0.85).set_stroke(width=3),
            run_time=2.5,
            rate_func=linear
        )
        self.wait(1.3)


# ==============================================================================
# Scene 15: 8D Non-Associative Logic Splitting to Dual 4D (Octonion to Quaternions)
# Spoken: "split an eight -dimensional, non -associative logic into two parts. And each of those parts has four dimensions of associative"
# ==============================================================================
class Scene15_15(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        center = DOWN * 1.0
        # 8-dimensional Octonion Unified Cluster (8 interconnected nodes in a circle)
        octo_dots = VGroup()
        octo_lines = VGroup()
        angles = [i * (2 * PI / 8) for i in range(8)]
        pts = [center + np.array([np.cos(a) * 1.3, np.sin(a) * 1.0, 0]) for a in angles]

        for p in pts:
            octo_dots.add(Dot(p, radius=0.12, color="#FFFFFF"))

        for i in range(8):
            for j in range(i + 1, 8):
                if (j - i) in (1, 2, 7):
                    octo_lines.add(Line(pts[i], pts[j], color="#FFFFFF", stroke_width=1.2).set_opacity(0.35))

        octo_unified = VGroup(octo_lines, octo_dots)
        badge_8d = Text("8D OCTONION (NON-ASSOCIATIVE)", font="Arial", weight=BOLD, font_size=10, color="#FFD700").move_to(UP * 0.1)

        # Labels for the two 4D split halves
        badge_4d_l = Text("4D ASSOCIATIVE", font="Arial", weight=BOLD, font_size=9, color="#FFFFFF").move_to(LEFT * 1.8 + UP * 0.1)
        badge_4d_r = Text("4D ASSOCIATIVE", font="Arial", weight=BOLD, font_size=9, color="#FFFFFF").move_to(RIGHT * 1.8 + UP * 0.1)

        self.play(FadeIn(badge_8d), Create(octo_unified), run_time=1.8)
        self.play(FadeOut(badge_8d), FadeIn(badge_4d_l), FadeIn(badge_4d_r), run_time=0.8)

        # Split 8 nodes into left 4 (0,1,2,3) and right 4 (4,5,6,7)
        left_half = VGroup(*octo_dots[:4])
        right_half = VGroup(*octo_dots[4:])

        self.play(
            octo_lines.animate.set_opacity(0.1),
            left_half.animate.shift(LEFT * 0.9),
            right_half.animate.shift(RIGHT * 0.9),
            run_time=3.4,
            rate_func=ease_in_out_sine
        )
        self.wait(1.5)
