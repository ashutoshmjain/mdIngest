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
# Scene 01: Master Key Unlocking Paper (Golden Key & Mechanical Blueprint Padlock)
# ==============================================================================
class Scene02_01(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        padlock_body = RoundedRectangle(width=1.6, height=1.3, corner_radius=0.15, color="#FFFFFF", stroke_width=2.5, fill_opacity=0.2).move_to(DOWN * 1.3)
        shackle = Arc(radius=0.6, start_angle=0, angle=PI, color="#FFFFFF", stroke_width=3).move_to(DOWN * 0.45)
        keyhole_circle = Circle(radius=0.12, color="#FFD700", fill_opacity=1, stroke_width=0).move_to(DOWN * 1.25)
        keyhole_slit = Polygon(DOWN * 1.25 + LEFT * 0.05, DOWN * 1.25 + RIGHT * 0.05, DOWN * 1.5 + RIGHT * 0.08, DOWN * 1.5 + LEFT * 0.08, color="#FFD700", fill_opacity=1, stroke_width=0)
        lock = VGroup(shackle, padlock_body, keyhole_circle, keyhole_slit)

        key_bow = Circle(radius=0.25, color="#FFD700", stroke_width=3).move_to(LEFT * 2.2 + DOWN * 1.0)
        key_stem = Line(LEFT * 1.95 + DOWN * 1.0, LEFT * 0.8 + DOWN * 1.0, color="#FFD700", stroke_width=3)
        bit1 = Line(LEFT * 1.0 + DOWN * 1.0, LEFT * 1.0 + DOWN * 1.2, color="#FFD700", stroke_width=3)
        bit2 = Line(LEFT * 1.2 + DOWN * 1.0, LEFT * 1.2 + DOWN * 1.15, color="#FFD700", stroke_width=3)
        key = VGroup(key_bow, key_stem, bit1, bit2)

        self.play(FadeIn(lock), run_time=1.0)
        self.play(FadeIn(key), run_time=0.8)
        self.play(
            key.animate.move_to(DOWN * 1.35 + LEFT * 0.2),
            run_time=2.0,
            rate_func=ease_in_out_sine
        )
        self.play(
            shackle.animate.shift(UP * 0.35),
            padlock_body.animate.set_stroke(color="#FFD700", width=3.5),
            run_time=1.5
        )
        self.wait(2.3)


# ==============================================================================
# Scene 02: Equations to Geometric Crystals (Math Symbols Morphing to Polyhedra)
# ==============================================================================
class Scene02_02(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        eq_txt = Text("e^{i pi} + 1 = 0", font="Arial", weight=BOLD, font_size=18, color="#64748b").move_to(LEFT * 1.8 + DOWN * 1.0)
        sym_box = RoundedRectangle(width=2.6, height=1.4, corner_radius=0.1, color="#334155", stroke_width=1.5).move_to(LEFT * 1.8 + DOWN * 1.0)
        math_grp = VGroup(sym_box, eq_txt)

        arrow = Arrow(LEFT * 0.3 + DOWN * 1.0, RIGHT * 0.5 + DOWN * 1.0, color="#FFFFFF", stroke_width=2.5, max_tip_length_to_length_ratio=0.25)

        poly_center = RIGHT * 1.8 + DOWN * 1.0
        poly_pts = [poly_center + np.array([np.cos(a)*1.1, np.sin(a)*1.1, 0]) for a in np.linspace(0, 2*PI, 6, endpoint=False)]
        hexagon = Polygon(*poly_pts, color="#FFFFFF", stroke_width=2.5, fill_opacity=0.15)
        chords = VGroup(*[Line(poly_pts[i], poly_pts[(i+2)%6], color="#FFD700", stroke_width=1.5).set_opacity(0.6) for i in range(6)])
        crystal = VGroup(hexagon, chords)

        self.play(FadeIn(math_grp), run_time=1.2)
        self.play(GrowArrow(arrow), run_time=0.8)
        self.play(Create(crystal), run_time=1.8)
        self.play(Rotate(crystal, angle=PI / 3, about_point=poly_center), run_time=2.2, rate_func=ease_in_out_sine)
        self.wait(1.6)


# ==============================================================================
# Scene 03: Deep Dive Website Open (3D Holographic Viewport & Wireframe)
# ==============================================================================
class Scene03_03(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        window = RoundedRectangle(width=4.4, height=2.6, corner_radius=0.12, color="#334155", stroke_width=2).move_to(DOWN * 1.0)
        top_bar = Line(window.get_corner(UL), window.get_corner(UR), color="#334155", stroke_width=2).shift(DOWN * 0.35)
        d1 = Dot(window.get_corner(UL) + DR * 0.18, radius=0.05, color="#64748b")
        d2 = Dot(window.get_corner(UL) + DR * 0.18 + RIGHT * 0.2, radius=0.05, color="#64748b")
        d3 = Dot(window.get_corner(UL) + DR * 0.18 + RIGHT * 0.4, radius=0.05, color="#64748b")
        url_tag = Text("deepdive.shutri.com", font="Consolas", font_size=8, color="#64748b").next_to(d3, RIGHT, buff=0.3)
        browser = VGroup(window, top_bar, d1, d2, d3, url_tag)

        cube_c = DOWN * 1.15
        front_sq = Square(side_length=1.2, color="#FFFFFF", stroke_width=2).move_to(cube_c + DL * 0.15)
        back_sq = Square(side_length=1.2, color="#FFD700", stroke_width=1.5).set_opacity(0.5).move_to(cube_c + UR * 0.15)
        connectors = VGroup(*[Line(front_sq.get_corner(c), back_sq.get_corner(c), color="#FFFFFF", stroke_width=1.5).set_opacity(0.7) for c in [UL, UR, DL, DR]])
        cube_3d = VGroup(back_sq, connectors, front_sq)

        self.play(FadeIn(browser), run_time=1.2)
        self.play(Create(cube_3d), run_time=1.8)
        self.play(Rotate(cube_3d, angle=PI / 4, about_point=cube_c), run_time=3.0, rate_func=linear)
        self.wait(1.6)


# ==============================================================================
# Scene 04: Eight-Dimensional Totality (Octahedral 8D Node Array)
# ==============================================================================
class Scene04_04(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        center = DOWN * 1.0
        rings = VGroup(*[Circle(radius=0.4 + i * 0.45, color="#334155", stroke_width=1.5).move_to(center) for i in range(4)])
        
        nodes = VGroup()
        for i in range(8):
            ang = i * (2 * PI / 8)
            rad = 1.3
            p = center + np.array([np.cos(ang) * rad, np.sin(ang) * rad, 0])
            n = Dot(p, radius=0.12, color="#FFFFFF")
            spoke = Line(center, p, color="#FFFFFF", stroke_width=1.2).set_opacity(0.35)
            nodes.add(VGroup(spoke, n))

        core = Dot(center, radius=0.2, color="#FFD700")
        tag_8d = Text("8D TOTALITY", font="Arial", weight=BOLD, font_size=11, color="#FFD700").move_to(UP * 0.15)

        self.play(Create(rings), FadeIn(tag_8d), run_time=1.4)
        self.play(Create(nodes), FadeIn(core), run_time=1.8)
        self.play(Rotate(nodes, angle=PI / 4, about_point=center), core.animate.scale(1.4), run_time=3.0, rate_func=ease_in_out_sine)
        self.wait(1.4)


# ==============================================================================
# Scene 05: Unbracketed Sentence & Brain Editor (Typography Stream & Pencil Desk)
# ==============================================================================
class Scene05_05(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        raw_stream = Text("REALITYISANEIGHTDIMENSIONALUNBRACKETEDSENTENCE", font="Consolas", font_size=9, color="#FFFFFF").move_to(UP * 0.0)
        stream_box = RoundedRectangle(width=4.8, height=0.6, corner_radius=0.08, color="#334155", stroke_width=1.5).move_to(UP * 0.0)

        brain_outline = Circle(radius=0.8, color="#FFD700", stroke_width=2.5, fill_opacity=0.2).move_to(DOWN * 1.5)
        brain_label = Text("BRAIN EDITOR", font="Arial", weight=BOLD, font_size=9, color="#FFFFFF").move_to(brain_outline.get_center())

        pencil = Line(brain_outline.get_top() + LEFT * 0.2, brain_outline.get_top() + RIGHT * 0.6 + UP * 0.6, color="#FFFFFF", stroke_width=4)
        lead = Dot(pencil.get_start(), radius=0.06, color="#FFD700")
        editor_pen = VGroup(pencil, lead)

        self.play(Create(stream_box), FadeIn(raw_stream), run_time=1.2)
        self.play(FadeIn(brain_outline), FadeIn(brain_label), FadeIn(editor_pen), run_time=1.4)
        self.play(
            raw_stream.animate.shift(LEFT * 0.6),
            editor_pen.animate.rotate(-PI / 6, about_point=pencil.get_start()).shift(UP * 0.2),
            run_time=3.4,
            rate_func=linear
        )
        self.wait(1.6)


# ==============================================================================
# Scene 06: Zooming Way Beyond Normal Math (Scaling Coordinate Dimensions)
# ==============================================================================
class Scene06_06(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        d1 = Line(LEFT * 1.5, RIGHT * 1.5, color="#64748b", stroke_width=2).move_to(DOWN * 2.0)
        lbl_1d = Text("1D", font="Consolas", font_size=9, color="#64748b").next_to(d1, LEFT, buff=0.2)

        d3 = Square(side_length=1.4, color="#64748b", stroke_width=2).move_to(DOWN * 1.1)
        lbl_3d = Text("3D", font="Consolas", font_size=9, color="#64748b").next_to(d3, LEFT, buff=0.2)

        d8 = Circle(radius=1.2, color="#FFD700", stroke_width=3, fill_opacity=0.15).move_to(DOWN * 0.6)
        star = VGroup(*[Line(d8.get_center(), d8.get_center() + np.array([np.cos(a)*1.2, np.sin(a)*1.2, 0]), color="#FFD700", stroke_width=1.5) for a in np.linspace(0, 2*PI, 8, endpoint=False)])
        d8_group = VGroup(d8, star)
        lbl_8d = Text("8D BEYOND", font="Consolas", weight=BOLD, font_size=10, color="#FFD700").next_to(d8, RIGHT, buff=0.2)

        self.play(Create(d1), FadeIn(lbl_1d), run_time=0.8)
        self.play(Create(d3), FadeIn(lbl_3d), run_time=1.0)
        self.play(Create(d8_group), FadeIn(lbl_8d), run_time=1.8)
        self.play(d8_group.animate.scale(1.3), run_time=2.4, rate_func=ease_in_out_sine)
        self.wait(1.6)


# ==============================================================================
# Scene 07: Octonians Mathematical Space (Fano Plane 7-Point Geometry)
# ==============================================================================
class Scene07_07(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        center = DOWN * 1.1
        tri_pts = [center + UP * 1.2, center + DOWN * 0.8 + LEFT * 1.4, center + DOWN * 0.8 + RIGHT * 1.4]
        outer_tri = Polygon(*tri_pts, color="#FFFFFF", stroke_width=2.5)

        mids = [(tri_pts[0] + tri_pts[1])/2, (tri_pts[1] + tri_pts[2])/2, (tri_pts[2] + tri_pts[0])/2]
        altitudes = VGroup(Line(tri_pts[0], mids[1], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5), Line(tri_pts[1], mids[2], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5), Line(tri_pts[2], mids[0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5))

        in_circle = Circle(radius=0.55, color="#FFD700", stroke_width=2).move_to(center + DOWN * 0.15)
        all_pts = tri_pts + mids + [center + DOWN * 0.15]
        dots = VGroup(*[Dot(p, radius=0.08, color="#FFFFFF") for p in all_pts])
        fano = VGroup(outer_tri, altitudes, in_circle, dots)

        tag = Text("OCTONION FANO PLANE", font="Arial", weight=BOLD, font_size=10, color="#FFD700").move_to(UP * 0.2)

        self.play(FadeIn(tag), Create(fano), run_time=2.2)
        self.play(Rotate(fano, angle=PI / 3, about_point=center), run_time=3.5, rate_func=linear)
        self.wait(1.9)


# ==============================================================================
# Scene 08: Massive Sentence With Zero Spaces (Continuous Typography Tape)
# ==============================================================================
class Scene08_08(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        tape = RoundedRectangle(width=5.2, height=1.4, corner_radius=0.1, color="#334155", stroke_width=2, fill_opacity=0.15).move_to(DOWN * 1.0)
        letters = Text("ZEROSPACESBETWEENTHEWORDSAWALLOFLETTERSCONTINUOUS", font="Consolas", font_size=11, color="#FFFFFF").move_to(DOWN * 1.0)
        tape_group = VGroup(tape, letters)

        slash_zero = Circle(radius=0.35, color="#FFD700", stroke_width=2.5).move_to(UP * 0.1)
        slash_bar = Line(slash_zero.get_corner(DL), slash_zero.get_corner(UR), color="#FFD700", stroke_width=2.5)
        zero_spaces = VGroup(slash_zero, slash_bar)
        no_space_lbl = Text("ZERO SPACES", font="Arial", weight=BOLD, font_size=9, color="#FFD700").next_to(zero_spaces, RIGHT, buff=0.2)

        self.play(FadeIn(tape_group), run_time=1.2)
        self.play(FadeIn(zero_spaces), FadeIn(no_space_lbl), run_time=1.0)
        self.play(letters.animate.shift(LEFT * 1.8), run_time=3.8, rate_func=linear)
        self.wait(1.6)


# ==============================================================================
# Scene 09: Wall of Letters Without Spaces (Masonry Brick Wall of Glyphs)
# ==============================================================================
class Scene09_09(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        wall_bricks = VGroup()
        for row in range(4):
            y = -0.3 - row * 0.45
            offset = 0.2 if row % 2 == 1 else 0.0
            for col in range(6):
                x = -2.0 + col * 0.75 + offset
                brick = Rectangle(width=0.7, height=0.4, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.2).move_to([x, y, 0])
                glyph = Text("A", font="Consolas", font_size=9, color="#64748b").move_to([x, y, 0])
                wall_bricks.add(VGroup(brick, glyph))

        tag = Text("WALL OF LETTERS", font="Arial", weight=BOLD, font_size=11, color="#FFFFFF").move_to(DOWN * 2.2)

        self.play(LaggedStart(*[FadeIn(b, shift=DOWN*0.1) for b in wall_bricks], lag_ratio=0.04), run_time=2.2)
        self.play(FadeIn(tag), run_time=0.8)
        self.play(wall_bricks.animate.set_stroke(color="#FFD700", width=2.5), run_time=2.6)
        self.wait(2.0)


# ==============================================================================
# Scene 10: Undefined Totality (Cloud of Latent Meaning With Zero Narrative)
# ==============================================================================
class Scene0 these10(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        center = DOWN * 1.0
        rings = VGroup()
        for i in range(12):
            ang = i * (2 * PI / 12)
            pt = center + np.array([np.cos(ang) * 1.2, np.sin(ang) * 0.8, 0])
            rings.add(Circle(radius=0.45, color="#64748b", stroke_width=1.5, fill_opacity=0.12).move_to(pt))

        center_core = Circle(radius=0.7, color="#FFFFFF", stroke_width=2.5, fill_opacity=0.25).move_to(center)
        lbl = Text("ALL POTENTIAL MEANING", font="Arial", weight=BOLD, font_size=10, color="#FFD700").move_to(center)
        nebula = VGroup(rings, center_core, lbl)

        self.play(FadeIn(nebula), run_time=1.8)
        self.play(rings.animate.scale(1.2).set_opacity(0.4), run_time=3.5, rate_func=ease_in_out_sine)
        self.wait(2.3)


# ==============================================================================
# Scene 11: Brackets in Algebraic Topology (Punctuation Vices Dropping Down)
# ==============================================================================
class Scene02_11(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        text_chars = Text("N O N A S S O C I A T I V E", font="Consolas", font_size=12, color="#FFFFFF").move_to(DOWN * 1.2)
        bracket_l = Text("(", font="Arial", weight=BOLD, font_size=42, color="#FFD700").move_to(LEFT * 2.2 + UP * 0.2)
        bracket_r = Text(")", font="Arial", weight=BOLD, font_size=42, color="#FFD700").move_to(RIGHT * 2.2 + UP * 0.2)

        tag = Text("ALGEBRAIC TOPOLOGY BRACKETING", font="Arial", weight=BOLD, font_size=9, color="#64748b").move_to(UP * 0.3)

        self.play(FadeIn(text_chars), FadeIn(tag), run_time=1.2)
        self.play(FadeIn(bracket_l), FadeIn(bracket_r), run_time=0.8)
        self.play(
            bracket_l.animate.move_to(LEFT * 1.4 + DOWN * 1.2),
            bracket_r.animate.move_to(RIGHT * 1.4 + DOWN * 1.2),
            run_time=2.5,
            rate_func=ease_in_out_sine
        )
        self.wait(3.1)


# ==============================================================================
# Scene 12: Grouping Letters into Words (Parentheses Forming Partitioned Blocks)
# ==============================================================================
class Scene02_12(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        b1 = RoundedRectangle(width=1.4, height=0.7, corner_radius=0.1, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to(LEFT * 1.8 + DOWN * 1.0)
        t1 = Text("WORD 1", font="Consolas", font_size=10, color="#FFFFFF").move_to(b1.get_center())
        grp1 = VGroup(b1, t1)

        b2 = RoundedRectangle(width=1.4, height=0.7, corner_radius=0.1, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to(DOWN * 1.0)
        t2 = Text("WORD 2", font="Consolas", font_size=10, color="#FFFFFF").move_to(b2.get_center())
        grp2 = VGroup(b2, t2)

        b3 = RoundedRectangle(width=1.4, height=0.7, corner_radius=0.1, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to(RIGHT * 1.8 + DOWN * 1.0)
        t3 = Text("WORD 3", font="Consolas", font_size=10, color="#FFFFFF").move_to(b3.get_center())
        grp3 = VGroup(b3, t3)

        separator1 = Line(UP * 0.3, DOWN * 0.3, color="#FFD700", stroke_width=2.5).move_to(LEFT * 0.9 + DOWN * 1.0)
        separator2 = Line(UP * 0.3, DOWN * 0.3, color="#FFD700", stroke_width=2.5).move_to(RIGHT * 0.9 + DOWN * 1.0)

        self.play(FadeIn(grp1), FadeIn(grp2), FadeIn(grp3), run_time=1.4)
        self.play(Create(separator1), Create(separator2), run_time=1.2)
        self.play(
            grp1.animate.shift(LEFT * 0.2),
            grp3.animate.shift(RIGHT * 0.2),
            run_time=2.5,
            rate_func=ease_in_out_sine
        )
        self.wait(2.5)


# ==============================================================================
# Scene 13: Stasheff Associahedron (3D Polyhedron Geometric Space of Brackets)
# ==============================================================================
class Scene02_13(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        center = DOWN * 1.0
        # 3D Associahedron Wireframe
        outer_p = Polygon(*[center + np.array([np.cos(a)*1.4, np.sin(a)*1.4, 0]) for a in np.linspace(0, 2*PI, 7, endpoint=False)], color="#FFFFFF", stroke_width=2.5)
        inner_p = Polygon(*[center + np.array([np.cos(a + 0.2)*0.8, np.sin(a + 0.2)*0.8, 0]) for a in np.linspace(0, 2*PI, 7, endpoint=False)], color="#FFD700", stroke_width=1.5)
        connectors = VGroup(*[Line(outer_p.get_vertices()[i], inner_p.get_vertices()[i], color="#FFFFFF", stroke_width=1.2).set_opacity(0.5) for i in range(7)])
        associahedron = VGroup(outer_p, inner_p, connectors)

        tag = Text("STASHEFF ASSOCIAHEDRON", font="Arial", weight=BOLD, font_size=10, color="#FFD700").move_to(UP * 0.2)

        self.play(FadeIn(tag), Create(associahedron), run_time=2.0)
        self.play(Rotate(associahedron, angle=PI / 2, about_point=center), run_time=3.5, rate_func=linear)
        self.wait(2.1)


# ==============================================================================
# Scene 14: Linear Tuesday Calendar vs Multidimensional Chaos
# ==============================================================================
class Scene02_14(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # Background 8D wavy chaos
        chaos = VGroup(*[Arc(radius=1.5, start_angle=i*0.5, angle=PI, color="#334155", stroke_width=1.5).move_to(DOWN * 1.0 + RIGHT*np.sin(i)*0.4) for i in range(6)])

        # Linear Tuesday Calendar Strip
        cal_box = RoundedRectangle(width=4.4, height=0.9, corner_radius=0.1, color="#FFFFFF", stroke_width=2.5, fill_opacity=0.9).move_to(DOWN * 1.0)
        cal_txt = Text("TUESDAY: 09:00 -> 17:00 (LINEAR STORY)", font="Consolas", weight=BOLD, font_size=9, color="#000000").move_to(cal_box.get_center())
        timeline_line = Line(LEFT * 2.0, RIGHT * 2.0, color="#FFD700", stroke_width=3).next_to(cal_box, DOWN, buff=0.15)

        self.play(FadeIn(chaos), run_time=1.0)
        self.play(FadeIn(cal_box), FadeIn(cal_txt), Create(timeline_line), run_time=1.5)
        self.play(timeline_line.animate.shift(RIGHT * 0.4), run_time=3.0, rate_func=linear)
        self.wait(2.1)


# ==============================================================================
# Scene 15: Paper's Main Heuristic: The Sensory Funnel
# ==============================================================================
class Scene02_15(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        funnel_top = Line(LEFT * 1.8, RIGHT * 1.8, color="#FFFFFF", stroke_width=2.5).move_to(UP * 0.1)
        funnel_neck_l = Line(LEFT * 1.8 + UP * 0.1, LEFT * 0.4 + DOWN * 1.2, color="#FFFFFF", stroke_width=2.5)
        funnel_neck_r = Line(RIGHT * 1.8 + UP * 0.1, RIGHT * 0.4 + DOWN * 1.2, color="#FFFFFF", stroke_width=2.5)
        funnel_spout_l = Line(LEFT * 0.4 + DOWN * 1.2, LEFT * 0.4 + DOWN * 2.0, color="#FFFFFF", stroke_width=2.5)
        funnel_spout_r = Line(RIGHT * 0.4 + DOWN * 1.2, RIGHT * 0.4 + DOWN * 2.0, color="#FFFFFF", stroke_width=2.5)
        funnel = VGroup(funnel_top, funnel_neck_l, funnel_neck_r, funnel_spout_l, funnel_spout_r)

        intake_dots = VGroup(*[Dot(UP * 0.1 + LEFT * 1.4 + RIGHT * i * 0.4, radius=0.09, color="#FFD700") for i in range(8)])
        lbl_in = Text("8D INPUT", font="Arial", weight=BOLD, font_size=9, color="#FFD700").next_to(funnel_top, UP, buff=0.1)

        output_beam = Line(DOWN * 2.0, DOWN * 2.5, color="#FFFFFF", stroke_width=4)
        lbl_out = Text("3D REALITY", font="Arial", weight=BOLD, font_size=9, color="#FFFFFF").next_to(output_beam, DOWN, buff=0.1)

        self.play(Create(funnel), FadeIn(lbl_in), FadeIn(intake_dots), run_time=1.4)
        self.play(Create(output_beam), FadeIn(lbl_out), run_time=1.0)
        self.play(intake_dots.animate.shift(DOWN * 1.2).scale(0.3), run_time=3.0, rate_func=ease_in_sine)
        self.wait(2.2)


# ==============================================================================
# Scene 16: Five Sensory Filters Stripping Dimensions (5 Filter Sieves)
# ==============================================================================
class Scene02_16(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        sieves = VGroup()
        for i in range(5):
            y = 0.0 - i * 0.45
            bar = Line(LEFT * 1.5, RIGHT * 1.5, color="#64748b", stroke_width=3).move_to([0, y, 0])
            lbl = Text(f"FILTER {i+1}", font="Consolas", font_size=8, color="#64748b").next_to(bar, LEFT, buff=0.15)
            sieves.add(VGroup(bar, lbl))

        beam = Line(UP * 0.3, DOWN * 2.2, color="#FFD700", stroke_width=3.5)

        self.play(Create(sieves), run_time=1.4)
        self.play(Create(beam), run_time=1.2)
        self.play(sieves.animate.set_color("#FFFFFF"), run_time=2.8)
        self.wait(2.2)


# ==============================================================================
# Scene 17: Lost Dimensions Stripped Away (8D - 5D = 3D Ghosted Rings)
# ==============================================================================
class Scene02_17(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        retained = VGroup(*[Circle(radius=0.4 + i*0.25, color="#FFFFFF", stroke_width=2.5).move_to(LEFT * 1.4 + DOWN * 1.0) for i in range(3)])
        lbl_3d = Text("3D PERCEIVED", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").next_to(retained, UP, buff=0.2)

        lost = VGroup(*[Circle(radius=0.3 + i*0.2, color="#64748b", stroke_width=1.5).move_to(RIGHT * 1.4 + DOWN * 1.0).set_opacity(0.4) for i in range(5)])
        lbl_5d = Text("5D LOST", font="Arial", weight=BOLD, font_size=10, color="#64748b").next_to(lost, UP, buff=0.2)

        self.play(FadeIn(retained), FadeIn(lbl_3d), run_time=1.2)
        self.play(FadeIn(lost), FadeIn(lbl_5d), run_time=1.2)
        self.play(lost.animate.shift(RIGHT * 0.8).set_opacity(0.1), run_time=3.0, rate_func=linear)
        self.wait(2.2)


# ==============================================================================
# Scene 18: Lost Dimensions Become Aging Time (5 Ghosted Rings to Clock)
# ==============================================================================
class Scene02_18(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        clock_face = Circle(radius=1.3, color="#FFFFFF", stroke_width=2.5).move_to(DOWN * 1.0)
        hour_hand = Line(DOWN * 1.0, DOWN * 1.0 + UP * 0.7, color="#FFFFFF", stroke_width=3)
        minute_hand = Line(DOWN * 1.0, DOWN * 1.0 + RIGHT * 0.9, color="#FFD700", stroke_width=2.5)
        clock = VGroup(clock_face, hour_hand, minute_hand)

        tag = Text("LOST DIMENSIONS = TIME", font="Arial", weight=BOLD, font_size=10, color="#FFD700").move_to(UP * 0.2)

        self.play(FadeIn(tag), Create(clock), run_time=1.4)
        self.play(
            Rotate(minute_hand, angle=-2 * PI, about_point=DOWN * 1.0),
            Rotate(hour_hand, angle=-PI / 3, about_point=DOWN * 1.0),
            run_time=4.0,
            rate_func=linear
        )
        self.wait(2.2)


# ==============================================================================
# Scene 19: Sensory Slice (Five-Pronged Beam Slicing 3D Cube)
# ==============================================================================
class Scene02_19(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        cube = Square(side_length=1.6, color="#FFFFFF", stroke_width=2.5, fill_opacity=0.2).move_to(DOWN * 1.0)
        
        laser_beam = Line(UP * 0.2 + LEFT * 2.0, DOWN * 2.2 + RIGHT * 2.0, color="#FFD700", stroke_width=4)
        slice_glow = Line(UP * 0.2 + LEFT * 2.0, DOWN * 2.2 + RIGHT * 2.0, color="#FFD700", stroke_width=8).set_opacity(0.25)
        laser = VGroup(laser_beam, slice_glow)

        tag = Text("SENSORY SLICE", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").move_to(UP * 0.2)

        self.play(FadeIn(tag), FadeIn(cube), run_time=1.2)
        self.play(Create(laser), run_time=1.2)
        self.play(cube.animate.shift(LEFT * 0.2).set_color("#64748b"), run_time=3.0)
        self.wait(2.2)


# ==============================================================================
# Scene 20: Sensory Perception Conceptual Translation (Receptor Neural Spike)
# ==============================================================================
class Scene02_20(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        # Sensory waveform coming from left
        wave_pts = [np.array([-2.4 + i*0.3, -1.0 + np.sin(i*1.2)*0.4, 0]) for i in range(8)]
        wave = VMobject(color="#FFFFFF", stroke_width=2)
        wave.set_points_smoothly(wave_pts)

        # Neural spike translator on right
        spike_pts = [np.array([0.2, -1.0, 0]), np.array([0.5, -0.4, 0]), np.array([0.7, -1.4, 0]), np.array([0.9, -1.0, 0]), np.array([1.8, -1.0, 0])]
        spike = VMobject(color="#FFD700", stroke_width=2.5)
        spike.set_points_as_corners(spike_pts)

        barrier = DashedLine(UP * 0.2, DOWN * 2.2, color="#64748b", stroke_width=2).move_to(LEFT * 0.1 + DOWN * 1.0)

        self.play(Create(barrier), Create(wave), run_time=1.4)
        self.play(Create(spike), run_time=1.4)
        self.play(spike.animate.shift(RIGHT * 0.3), run_time=2.8)
        self.wait(2.0)


# ==============================================================================
# Scene 21: Neural Representation (Associative Graph Network Representation)
# ==============================================================================
class Scene02_21(Scene):
    def construct(self):
        self.add(get_footer_bar("KineticVector"))

        center = DOWN * 1.0
        # Associative Neural Network Graph
        nodes_l = VGroup(*[Dot(center + LEFT * 1.5 + UP * (0.8 - i*0.8), radius=0.12, color="#FFFFFF") for i in range(3)])
        nodes_m = VGroup(*[Dot(center + UP * (1.1 - i*0.7), radius=0.12, color="#FFD700") for i in range(4)])
        nodes_r = VGroup(*[Dot(center + RIGHT * 1.5 + UP * (0.8 - i*0.8), radius=0.12, color="#FFFFFF") for i in range(3)])

        edges = VGroup()
        for nl in nodes_l:
            for nm in nodes_m:
                edges.add(Line(nl.get_center(), nm.get_center(), color="#FFFFFF", stroke_width=1).set_opacity(0.3))
        for nm in nodes_m:
            for nr in nodes_r:
                edges.add(Line(nm.get_center(), nr.get_center(), color="#FFFFFF", stroke_width=1).set_opacity(0.3))

        network = VGroup(edges, nodes_l, nodes_m, nodes_r)
        tag = Text("ASSOCIATIVE NEURAL REPRESENTATION", font="Arial", weight=BOLD, font_size=10, color="#FFD700").move_to(UP * 0.2)

        self.play(FadeIn(tag), Create(network), run_time=2.0)
        self.play(nodes_m.animate.scale(1.3), edges.animate.set_opacity(0.7), run_time=3.2, rate_func=ease_in_out_sine)
        self.wait(2.4)