import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Configure canvas & resolution globally

def setup_footer(scene):
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("MONEY ALLOCATION", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

def setup_title(scene, text_str):
    title = Text(text_str, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)

class Scene15_01(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "WHAT DOES IT DO WITH THE MONEY")
        
        # Literal visual: A massive wallet opening up, dollar signs pouring out
        wallet = RoundedRectangle(corner_radius=0.2, width=3.0, height=2.0, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.1).move_to([0, -1.0, 0])
        wallet_flap = Line(wallet.get_corner(UL), wallet.get_corner(UR), color="#FFFFFF", stroke_width=3)
        
        dollar_signs = VGroup(*[
            Text("$", font="Arial", weight=BOLD, font_size=36, color="#FFFFFF").move_to([x, y, 0])
            for x, y in [(-1, 0), (0, 0.5), (1, 0), (-0.5, 1.2), (0.5, 1.5)]
        ])
        
        question_mark = Text("?", font="Arial", weight=BOLD, font_size=72, color="#FFFFFF").move_to([0, -0.8, 0])
        
        self.play(Create(wallet), Create(wallet_flap), FadeIn(question_mark), run_time=1.5)
        self.play(FadeIn(dollar_signs, shift=UP*0.5), run_time=3.5)
        self.wait(2.6)

class Scene15_02(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "TRACKING THE CASH FLOW")
        
        # Literal visual: Checkbook and a glowing pen / checkmark checking items off
        checkbook = Rectangle(width=3.6, height=2.4, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.05).move_to([0, -0.5, 0])
        lines = VGroup(*[
            Line(LEFT*1.4, RIGHT*1.4, color="#FFFFFF", stroke_width=1.5).set_opacity(0.5).move_to([0, y, 0])
            for y in [0.2, -0.2, -0.6]
        ])
        
        checks = VGroup(*[
            Text("✓", font="Arial", weight=BOLD, font_size=28, color="#FFFFFF").move_to([-1.2, y, 0])
            for y in [0.2, -0.2, -0.6]
        ])
        
        magnifier = Circle(radius=0.8, stroke_color="#FFFFFF", stroke_width=3).move_to([0.5, -0.2, 0])
        mag_handle = Line([1.1, -0.8, 0], [1.7, -1.4, 0], color="#FFFFFF", stroke_width=4)
        
        self.play(Create(checkbook), Create(lines), run_time=2.0)
        self.play(FadeIn(checks), Create(magnifier), Create(mag_handle), run_time=2.5)
        self.wait(3.1)

class Scene15_03(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "WHERE DOES EVERY DOLLAR GO")
        
        # Literal visual: A central vault with arrows splitting outwards to expenses
        vault = RoundedRectangle(corner_radius=0.3, width=2.2, height=1.8, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.15).move_to([0, -0.5, 0])
        vault_dial = Circle(radius=0.4, stroke_color="#FFFFFF", stroke_width=2).move_to([0, -0.5, 0])
        
        arrows = VGroup(
            Arrow(start=[0, -0.5, 0], end=[-2.5, 1.0, 0], color="#FFFFFF", stroke_width=3, buff=0.1),
            Arrow(start=[0, -0.5, 0], end=[2.5, 1.0, 0], color="#FFFFFF", stroke_width=3, buff=0.1),
            Arrow(start=[0, -0.5, 0], end=[0, 1.5, 0], color="#FFFFFF", stroke_width=3, buff=0.1),
        )
        
        destinations = VGroup(
            RoundedRectangle(corner_radius=0.1, width=1.0, height=0.5, stroke_color="#FFFFFF", stroke_width=2).move_to([-2.5, 1.2, 0]),
            RoundedRectangle(corner_radius=0.1, width=1.0, height=0.5, stroke_color="#FFFFFF", stroke_width=2).move_to([2.5, 1.2, 0]),
            RoundedRectangle(corner_radius=0.1, width=1.0, height=0.5, stroke_color="#FFFFFF", stroke_width=2).move_to([0, 1.7, 0]),
        )
        
        self.play(Create(vault), Create(vault_dial), run_time=1.5)
        self.play(GrowArrow(arrows[0]), GrowArrow(arrows[1]), GrowArrow(arrows[2]), run_time=2.0)
        self.play(Create(destinations), run_time=1.5)
        self.wait(2.6)

class Scene15_04(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "BREAKING DOWN THE EXPENSES")
        
        # Literal visual: A balance scale weighing cash vs assets
        base = Triangle(color="#FFFFFF", stroke_width=2).scale(0.5).move_to([0, -1.8, 0])
        pole = Line([0, -1.5, 0], [0, 0.5, 0], color="#FFFFFF", stroke_width=4)
        beam = Line([-2.5, 0.5, 0], [2.5, 0.5, 0], color="#FFFFFF", stroke_width=3)
        
        pan_left = VGroup(
            Line([-2.5, 0.5, 0], [-3.0, -0.5, 0], color="#FFFFFF", stroke_width=2),
            Line([-2.5, 0.5, 0], [-2.0, -0.5, 0], color="#FFFFFF", stroke_width=2),
            Arc(radius=1.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2).move_to([-2.5, -0.5, 0])
        )
        pan_right = VGroup(
            Line([2.5, 0.5, 0], [2.0, -0.5, 0], color="#FFFFFF", stroke_width=2),
            Line([2.5, 0.5, 0], [3.0, -0.5, 0], color="#FFFFFF", stroke_width=2),
            Arc(radius=1.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2).move_to([2.5, -0.5, 0])
        )
        
        cash_stack = Rectangle(width=0.8, height=0.6, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.3).move_to([-2.5, -0.7, 0])
        gear = Circle(radius=0.4, stroke_color="#FFFFFF", stroke_width=2).move_to([2.5, -0.7, 0])
        
        self.play(Create(base), Create(pole), Create(beam), run_time=2.0)
        self.play(Create(pan_left), Create(pan_right), run_time=1.5)
        self.play(FadeIn(cash_stack), FadeIn(gear), run_time=1.5)
        self.wait(2.6)

class Scene15_05(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "INVESTING BACK INTO GROWTH")
        
        # Literal visual: A rising bar chart with an upward trend arrow
        bars = VGroup(*[
            Rectangle(width=0.6, height=h, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2)
            .move_to([x, y, 0])
            for x, h, y in [(-1.5, 1.0, -1.0), (-0.5, 1.8, -0.6), (0.5, 2.6, -0.2), (1.5, 3.4, 0.2)]
        ])
        
        trend_line = Arrow(start=[-2.0, -1.5, 0], end=[2.0, 1.5, 0], color="#FFFFFF", stroke_width=4, buff=0.1)
        
        self.play(Create(bars), run_time=3.0)
        self.play(GrowArrow(trend_line), run_time=2.0)
        self.wait(2.6)

class Scene15_06(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "ALLOCATION TRANSPARENCY")
        
        # Literal visual: A magnifying glass inspecting a giant document / bill
        doc = Rectangle(width=3.0, height=3.8, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.05).move_to([0, -0.3, 0])
        text_lines = VGroup(*[
            Line(LEFT*1.1, RIGHT*1.1, color="#FFFFFF", stroke_width=1.5).set_opacity(0.6).move_to([0, y, 0])
            for y in [1.0, 0.5, 0.0, -0.5, -1.0, -1.5]
        ])
        
        glass = Circle(radius=1.1, stroke_color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=0.5).move_to([0.5, 0.2, 0])
        handle = Line([1.3, -0.6, 0], [2.1, -1.4, 0], color="#FFFFFF", stroke_width=5)
        
        dollar_focus = Text("$", font="Arial", weight=BOLD, font_size=48, color="#FFFFFF").move_to([0.5, 0.2, 0])
        
        self.play(Create(doc), Create(text_lines), run_time=2.5)
        self.play(Create(glass), Create(handle), FadeIn(dollar_focus), run_time=2.5)
        self.wait(2.6)

class Scene15_07(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "THE BOTTOM LINE")
        
        # Literal visual: A giant cash register totaling up, showing a clear total
        register_body = RoundedRectangle(corner_radius=0.2, width=3.4, height=2.2, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.1).move_to([0, -0.8, 0])
        screen = RoundedRectangle(corner_radius=0.1, width=2.6, height=0.8, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).move_to([0, 0.6, 0])
        
        total_text = Text("$100%", font="Arial", weight=BOLD, font_size=32, color="#FFFFFF").move_to([0, 0.6, 0])
        
        drawer = RoundedRectangle(corner_radius=0.1, width=3.0, height=0.6, stroke_color="#FFFFFF", stroke_width=2).move_to([0, -1.4, 0])
        handle_drawer = Line([-0.4, -1.4, 0], [0.4, -1.4, 0], color="#FFFFFF", stroke_width=3)
        
        self.play(Create(register_body), Create(screen), Write(total_text), run_time=2.5)
        self.play(Create(drawer), Create(handle_drawer), run_time=2.0)
        self.wait(3.1)

# Configure canvas strictly for pure monochrome vertical podcast requirements

def setup_footer_and_title(scene, title_text):
    # Strict bottom title placement (y = -2.95)
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)

    # Bottom footer bar & meta labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("FINANCIAL ALLOCATION", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene15_08(Scene):
    def construct(self):
        setup_footer_and_title(self, "WHAT DOES IT DO WITH THE MONEY")
        
        # Literal figurative visual: Large Checkbook & Dollar Sign entering intake
        checkbook = RoundedRectangle(corner_radius=0.1, width=3.5, height=2.2, color="#FFFFFF", stroke_width=2.0)
        checkbook.move_to([0, -0.8, 0])
        
        lines = VGroup(*[
            Line(LEFT * 1.3, RIGHT * 1.3, color="#FFFFFF", stroke_width=1.5).shift(UP * y)
            for y in [0.5, 0.0, -0.5]
        ]).move_to(checkbook.get_center() + DOWN * 0.1)
        
        dollar = Text("$", font="Arial", weight=BOLD, font_size=54, color="#FFFFFF").move_to([0, 1.3, 0])
        arrow = Arrow(start=UP * 2.2, end=UP * 1.7, color="#FFFFFF", stroke_width=2.0, buff=0)
        
        group = VGroup(checkbook, lines, dollar, arrow)
        
        self.play(FadeIn(group, shift=DOWN * 0.5), run_time=3.5)
        self.play(dollar.animate.scale(1.1), run_time=2.0)
        self.wait(1.5)

class Scene15_09(Scene):
    def construct(self):
        setup_footer_and_title(self, "CAPITAL FLOW & DISTRIBUTION")
        
        # Literal figurative visual: Central vault / server splitting into outgoing streams
        center_box = Rectangle(width=1.8, height=1.8, color="#FFFFFF", stroke_width=2.0).move_to([0, -0.5, 0])
        core_dollar = Text("$", font="Arial", weight=BOLD, font_size=40, color="#FFFFFF").move_to(center_box.get_center())
        
        # Outgoing arrows to 3 mini boxes
        arrows = VGroup(
            Arrow(start=center_box.get_left(), end=LEFT * 2.8, color="#FFFFFF", stroke_width=1.5, buff=0.1),
            Arrow(start=center_box.get_top(), end=UP * 1.5, color="#FFFFFF", stroke_width=1.5, buff=0.1),
            Arrow(start=center_box.get_right(), end=RIGHT * 2.8, color="#FFFFFF", stroke_width=1.5, buff=0.1)
        )
        
        boxes = VGroup(
            Rectangle(width=0.8, height=0.6, color="#FFFFFF", stroke_width=1.5).move_to(LEFT * 3.2),
            Rectangle(width=0.8, height=0.6, color="#FFFFFF", stroke_width=1.5).move_to(UP * 1.9),
            Rectangle(width=0.8, height=0.6, color="#FFFFFF", stroke_width=1.5).move_to(RIGHT * 3.2)
        )
        
        group = VGroup(center_box, core_dollar, arrows, boxes)
        
        self.play(Create(group), run_time=4.0)
        self.play(center_box.animate.set_fill("#FFFFFF", opacity=0.15), run_time=2.0)
        self.wait(1.0)

class Scene15_10(Scene):
    def construct(self):
        setup_footer_and_title(self, "BALANCE SCALE OF EXPENDITURE")
        
        # Literal figurative visual: Balance Scale
        fulcrum = Polygon([0, -1.2, 0], [-0.6, -2.2, 0], [0.6, -2.2, 0], color="#FFFFFF", stroke_width=2.0)
        beam = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=2.5).move_to([-0.0, -1.2, 0])
        beam.rotate(0.15)
        
        pan_left = VGroup(
            Line(LEFT * 2.5, LEFT * 2.5 + DOWN * 0.8, color="#FFFFFF", stroke_width=1.5),
            Arc(radius=0.8, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=1.5).move_to(LEFT * 2.5 + DOWN * 0.8)
        ).shift(UP * 0.38)
        
        pan_right = VGroup(
            Line(RIGHT * 2.5, RIGHT * 2.5 + DOWN * 0.8, color="#FFFFFF", stroke_width=1.5),
            Arc(radius=0.8, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=1.5).move_to(RIGHT * 2.5 + DOWN * 0.8)
        ).shift(DOWN * 0.38)
        
        d_left = Text("$", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to(LEFT * 2.5 + DOWN * 1.1)
        d_right = Text("$", font="Arial", weight=BOLD, font_size=32, color="#FFFFFF").move_to(RIGHT * 2.5 + DOWN * 0.3)
        
        scale_group = VGroup(fulcrum, beam, pan_left, pan_right, d_left, d_right).move_to([0, -0.6, 0])
        
        self.play(FadeIn(scale_group), run_time=4.0)
        self.play(Rotate(beam, -0.3, about_point=fulcrum.get_top()), run_time=2.0)
        self.wait(1.0)

class Scene15_11(Scene):
    def construct(self):
        setup_footer_and_title(self, "POWER METER & RESOURCE DRAIN")
        
        # Literal figurative visual: Power Meter / Gauge with needle
        gauge_arc = Arc(radius=2.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=3.0).move_to([0, -1.2, 0])
        
        ticks = VGroup(*[
            Line(UP * 1.8, UP * 2.0, color="#FFFFFF", stroke_width=2.0).rotate(angle, about_point=[0, -1.2, 0])
            for angle in [-PI/2, -PI/4, 0, PI/4, PI/2]
        ]).move_to([0, -1.2, 0])
        
        needle = Line([0, -1.2, 0], [1.2, 0.2, 0], color="#FFFFFF", stroke_width=3.0)
        center_pin = Circle(radius=0.15, color="#FFFFFF", fill_opacity=1.0).move_to([0, -1.2, 0])
        
        dollar_label = Text("$", font="Arial", weight=BOLD, font_size=36, color="#FFFFFF").move_to([0, 0.4, 0])
        
        meter_group = VGroup(gauge_arc, ticks, needle, center_pin, dollar_label)
        
        self.play(Create(meter_group), run_time=4.0)
        self.play(Rotate(needle, -1.2, about_point=[0, -1.2, 0]), run_time=2.0)
        self.wait(1.0)

class Scene15_12(Scene):
    def construct(self):
        setup_footer_and_title(self, "DATA SERVERS PROCESSING FUNDS")
        
        # Literal figurative visual: Stack of Server Racks with blinking lights
        servers = VGroup(*[
            RoundedRectangle(corner_radius=0.1, width=4.0, height=0.9, color="#FFFFFF", stroke_width=2.0).shift(UP * y)
            for y in [1.0, 0.0, -1.0]
        ]).move_to([0, -0.4, 0])
        
        lights = VGroup()
        for s in servers:
            for x_offset in [-1.5, -1.1, 1.5]:
                lights.add(Circle(radius=0.08, color="#FFFFFF", fill_opacity=0.9).move_to(s.get_center() + RIGHT * x_offset))
                
        dollar_badge = Text("$", font="Arial", weight=BOLD, font_size=28, color="#FFFFFF").move_to(servers[1].get_center())
        
        group = VGroup(servers, lights, dollar_badge)
        
        self.play(FadeIn(group, shift=UP * 0.5), run_time=4.0)
        self.play(lights.animate.set_opacity(0.2), run_time=2.0)
        self.wait(1.0)

class Scene15_13(Scene):
    def construct(self):
        setup_footer_and_title(self, "TRANSACTION PIPELINE & CONDUIT")
        
        # Literal figurative visual: Large horizontal pipe / funnel with money entering
        pipe_top = Line(LEFT * 3.0, RIGHT * 3.0, color="#FFFFFF", stroke_width=2.5).shift(UP * 0.2)
        pipe_bottom = Line(LEFT * 3.0, RIGHT * 3.0, color="#FFFFFF", stroke_width=2.5).shift(DOWN * 1.2)
        
        left_funnel = Line(LEFT * 3.0, LEFT * 1.5 + UP * 1.2, color="#FFFFFF", stroke_width=2.0)
        left_funnel_bottom = Line(LEFT * 3.0, LEFT * 1.5 + DOWN * 2.2, color="#FFFFFF", stroke_width=2.0)
        
        d1 = Text("$", font="Arial", weight=BOLD, font_size=30, color="#FFFFFF").move_to([ -2.0, -0.5, 0])
        d2 = Text("$", font="Arial", weight=BOLD, font_size=40, color="#FFFFFF").move_to([ 0.0, -0.5, 0])
        d3 = Text("$", font="Arial", weight=BOLD, font_size=50, color="#FFFFFF").move_to([ 2.0, -0.5, 0])
        
        flow_group = VGroup(pipe_top, pipe_bottom, d1, d2, d3).move_to([0, -0.5, 0])
        
        self.play(Create(flow_group), run_time=4.0)
        self.play(
            d1.animate.shift(RIGHT * 2.0).scale(1.2),
            d2.animate.shift(RIGHT * 2.0).scale(1.2),
            run_time=2.0
        )
        self.wait(1.6)

class Scene15_14(Scene):
    def construct(self):
        setup_footer_and_title(self, "FINAL ALLOCATION SUMMARY")
        
        # Literal figurative visual: Target / Bullseye with dollar in center
        ring_outer = Circle(radius=1.8, color="#FFFFFF", stroke_width=2.0).move_to([0, -0.6, 0])
        ring_inner = Circle(radius=1.0, color="#FFFFFF", stroke_width=2.0).move_to([0, -0.6, 0])
        center_dot = Circle(radius=0.3, color="#FFFFFF", fill_opacity=0.8).move_to([0, -0.6, 0])
        
        central_dollar = Text("$", font="Arial", weight=BOLD, font_size=32, color="#FFFFFF").move_to([0, -0.6, 0])
        
        target_group = VGroup(ring_outer, ring_inner, center_dot, central_dollar)
        
        self.play(FadeIn(target_group, scale=0.8), run_time=4.0)
        self.play(ring_inner.animate.set_fill("#FFFFFF", opacity=0.2), run_time=2.0)
        self.wait(1.6)

# Configure canvas strictly for pure monochrome vertical/square constraints

def add_standard_footer(scene, category_text):
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

def add_standard_title(scene, title_text):
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)


class Scene15_15(Scene):
    def construct(self):
        add_standard_footer(self, "MONEY ALLOCATION")
        add_standard_title(self, "WHAT DOES IT ACTUALLY DO WITH THE MONEY")
        
        # Literal figurative visual: Wallet/Vault opening up and releasing dollar signs
        vault = RoundedRectangle(corner_radius=0.2, width=3.0, height=2.2, stroke_color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([0, -1.0, 0])
        dial = Circle(radius=0.35, stroke_color="#FFFFFF", stroke_width=2, fill_color="#000000", fill_opacity=1).move_to(vault.get_center())
        dial_dot = Circle(radius=0.06, stroke_color="#FFFFFF", stroke_width=1, fill_color="#FFFFFF", fill_opacity=1).move_to(dial.get_center() + UP * 0.15)
        
        handle = Rectangle(width=0.4, height=0.15, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.8).next_to(vault, RIGHT, buff=0.05)
        
        # Dollar signs emerging
        d1 = Text("$", font="Arial", weight=BOLD, font_size=36, color="#FFFFFF").move_to([-1.0, 0.8, 0])
        d2 = Text("$", font="Arial", weight=BOLD, font_size=48, color="#FFFFFF").move_to([0.0, 1.2, 0])
        d3 = Text("$", font="Arial", weight=BOLD, font_size=36, color="#FFFFFF").move_to([1.0, 0.8, 0])
        
        money_group = VGroup(d1, d2, d3)
        vault_group = VGroup(vault, dial, dial_dot, handle)
        
        self.play(FadeIn(vault_group, shift=DOWN * 0.3), run_time=1.0)
        self.play(
            money_group.animate.shift(UP * 0.8).set_opacity(1.0),
            run_time=2.5,
            rate_func=rate_functions.ease_out_sine
        )
        self.wait(3.5)


class Scene15_16(Scene):
    def construct(self):
        add_standard_footer(self, "CAPITAL FLOW")
        add_standard_title(self, "WHAT DOES IT ACTUALLY DO WITH THE MONEY")
        
        # Literal figurative visual: Intake pipe funneling money into a central processing box
        funnel = Polygon([-1.8, 1.5, 0], [1.8, 1.5, 0], [0.8, -0.2, 0], [-0.8, -0.2, 0], stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.1)
        pipe = Rectangle(width=1.2, height=1.5, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).move_to([0, -1.3, 0])
        
        coin1 = Circle(radius=0.25, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.8).move_to([0, 2.0, 0])
        coin_text = Text("$", font="Arial", weight=BOLD, font_size=20, color="#000000").move_to(coin1.get_center())
        coin = VGroup(coin1, coin_text)
        
        arrow_down = Arrow(start=UP * 0.2, end=DOWN * 0.6, stroke_width=3, color="#FFFFFF").move_to([0, -0.6, 0])
        
        self.play(Create(funnel), Create(pipe), run_time=1.0)
        self.play(FadeIn(coin, shift=DOWN*0.5), run_time=1.0)
        self.play(coin.animate.move_to([0, -0.5, 0]), run_time=1.5)
        self.play(FadeOut(coin), FadeIn(arrow_down), run_time=1.0)
        self.wait(2.1)


class Scene15_17(Scene):
    def construct(self):
        add_standard_footer(self, "EXPENSE TRACKING")
        add_standard_title(self, "WHAT DOES IT ACTUALLY DO WITH THE MONEY")
        
        # Literal figurative visual: Checkbook and a glowing checkmark
        book = RoundedRectangle(corner_radius=0.1, width=3.4, height=2.4, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.08).move_to([0, -0.4, 0])
        line1 = Line(LEFT * 1.2, RIGHT * 1.2, stroke_width=2, color="#FFFFFF").move_to([-0.2, 0.4, 0])
        line2 = Line(LEFT * 1.2, RIGHT * 1.2, stroke_width=2, color="#FFFFFF").move_to([-0.2, 0.0, 0])
        line3 = Line(LEFT * 1.2, RIGHT * 1.2, stroke_width=2, color="#FFFFFF").move_to([-0.2, -0.4, 0])
        
        check = VGroup(
            Line(START, DOWN * 0.3 + RIGHT * 0.3, stroke_width=4, color="#FFFFFF"),
            Line(DOWN * 0.3 + RIGHT * 0.3, UP * 0.5 + RIGHT * 0.9, stroke_width=4, color="#FFFFFF")
        ).move_to([0.6, -1.0, 0])
        
        doc_group = VGroup(book, line1, line2, line3)
        
        self.play(FadeIn(doc_group, scale=0.9), run_time=1.5)
        self.play(Create(check), run_time=1.5)
        self.wait(4.6)


class Scene15_18(Scene):
    def construct(self):
        add_standard_footer(self, "ASSET ALLOCATION")
        add_standard_title(self, "WHAT DOES IT ACTUALLY DO WITH THE MONEY")
        
        # Literal figurative visual: Balance Scale weighing investments vs returns
        base = Triangle(stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).scale(0.6).move_to([0, -1.8, 0])
        pillar = Line(UP * 2.2, DOWN * 1.2, stroke_width=3, color="#FFFFFF").move_to([0, -0.3, 0])
        beam = Line(LEFT * 2.0, RIGHT * 2.0, stroke_width=3, color="#FFFFFF").move_to([0, 0.9, 0])
        
        pan_left = VGroup(
            Line(UP * 0, DOWN * 0.8 + LEFT * 0.6, stroke_width=1.5, color="#FFFFFF"),
            Line(UP * 0, DOWN * 0.8 + RIGHT * 0.6, stroke_width=1.5, color="#FFFFFF"),
            Arc(radius=0.8, start_angle=PI, angle=PI, stroke_width=2, color="#FFFFFF").move_to([(-2.0), 0.1, 0])
        ).move_to([-2.0, 0.1, 0])
        # Simplify scale pans representation using clear geometry
        pan_l = RoundedRectangle(corner_radius=0.1, width=1.2, height=0.3, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.3).move_to([-2.0, -0.2, 0])
        string_l1 = Line([-2.4, 0.9, 0], [-2.3, -0.05, 0], stroke_width=1.5, color="#FFFFFF")
        string_l2 = Line([-1.6, 0.9, 0], [-1.7, -0.05, 0], stroke_width=1.5, color="#FFFFFF")
        
        pan_r = RoundedRectangle(corner_radius=0.1, width=1.2, height=0.3, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.3).move_to([2.0, 0.4, 0])
        string_r1 = Line([1.6, 0.9, 0], [1.7, 0.55, 0], stroke_width=1.5, color="#FFFFFF")
        string_r2 = Line([2.4, 0.9, 0], [2.3, 0.55, 0], stroke_width=1.5, color="#FFFFFF")
        
        scale_group = VGroup(base, pillar, beam, pan_l, string_l1, string_l2, pan_r, string_r1, string_r2)
        
        self.play(Create(base), Create(pillar), run_time=1.0)
        self.play(Create(beam), run_time=0.8)
        self.play(FadeIn(scale_group[3:]), run_time=1.2)
        self.play(
            scale_group.animate.rotate(0.1, about_point=pillar.get_top()),
            run_time=1.5,
            rate_func=rate_functions.there_and_back
        )
        self.wait(3.1)


class Scene15_19(Scene):
    def construct(self):
        add_standard_footer(self, "PORTFOLIO SPREAD")
        add_standard_title(self, "WHAT DOES IT ACTUALLY DO WITH THE MONEY")
        
        # Literal figurative visual: Network nodes distributing money (Hub and spoke style)
        center_node = Circle(radius=0.6, stroke_color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.2).move_to([0, -0.4, 0])
        center_dollar = Text("$", font="Arial", weight=BOLD, font_size=28, color="#FFFFFF").move_to(center_node.get_center())
        
        n1 = Circle(radius=0.35, stroke_color="#FFFFFF", stroke_width=2, fill_color="#000000", fill_opacity=1).move_to([-2.2, 1.0, 0])
        n2 = Circle(radius=0.35, stroke_color="#FFFFFF", stroke_width=2, fill_color="#000000", fill_opacity=1).move_to([2.2, 1.0, 0])
        n3 = Circle(radius=0.35, stroke_color="#FFFFFF", stroke_width=2, fill_color="#000000", fill_opacity=1).move_to([-2.2, -1.8, 0])
        n4 = Circle(radius=0.35, stroke_color="#FFFFFF", stroke_width=2, fill_color="#000000", fill_opacity=1).move_to([2.2, -1.8, 0])
        
        l1 = Line(center_node.get_center(), n1.get_center(), stroke_width=2, color="#FFFFFF").set_opacity(0.7)
        l2 = Line(center_node.get_center(), n2.get_center(), stroke_width=2, color="#FFFFFF").set_opacity(0.7)
        l3 = Line(center_node.get_center(), n3.get_center(), stroke_width=2, color="#FFFFFF").set_opacity(0.7)
        l4 = Line(center_node.get_center(), n4.get_center(), stroke_width=2, color="#FFFFFF").set_opacity(0.7)
        
        network = VGroup(l1, l2, l3, l4, n1, n2, n3, n4, center_node, center_dollar)
        
        self.play(FadeIn(center_node), FadeIn(center_dollar), run_time=1.0)
        self.play(Create(l1), Create(l2), Create(l3), Create(l4), run_time=1.5)
        self.play(FadeIn(n1), FadeIn(n2), FadeIn(n3), FadeIn(n4), run_time=1.0)
        self.wait(4.1)