import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# CANVAS CONFIGURATION

# (Using universal get_footer_and_title from manim_compat)

class Scene08_01(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "IT'S MATHEMATICALLY GUARANTEED TO FAIL")
        
        # Visual: A power meter hitting zero (Failure)
        meter_arc = Arc(radius=1.5, start_angle=PI, angle=-PI, color="#FFFFFF", stroke_width=4).move_to(UP * -0.8)
        ticks = VGroup(*[Line(UP*1.4, UP*1.6, color="#FFFFFF").rotate(a, about_point=meter_arc.get_center()) for a in np.linspace(0, -PI, 5)])
        needle = Line(meter_arc.get_center(), meter_arc.get_center() + LEFT * 1.3, color="#FFFFFF", stroke_width=6)
        fail_label = Text("0%", font="Arial", font_size=24, color="#FFFFFF").next_to(meter_arc, LEFT, buff=-0.5)
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(meter_arc), Create(ticks), Create(needle), Write(fail_label), run_time=1.5)
        self.play(needle.animate.rotate(-PI * 0.9, about_point=meter_arc.get_center()), run_time=4.4, rate_func=slow_into)
        self.wait(1.0)

class Scene08_02(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "IT'S MATHEMATICALLY GUARANTEED TO FAIL")
        
        # Visual: A balance scale heavily tipped by a "0" weight
        base = Triangle(color="#FFFFFF").scale(0.3).move_to(DOWN * 1.8)
        beam = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=4).move_to(DOWN * 1.4)
        left_plate = Line(LEFT * 0.5, RIGHT * 0.5, color="#FFFFFF").next_to(beam.get_start(), UP, buff=0)
        right_plate = Line(LEFT * 0.5, RIGHT * 0.5, color="#FFFFFF").next_to(beam.get_end(), UP, buff=0)
        zero_weight = Circle(radius=0.4, color="#FFFFFF", fill_opacity=0.8).next_to(right_plate, UP, buff=0)
        zero_text = Text("0", font="Arial", font_size=20, color="#000000").move_to(zero_weight.get_center())
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(base), Create(beam), Create(left_plate), Create(right_plate), run_time=1.5)
        self.play(
            beam.animate.rotate(-PI/12, about_point=base.get_top()),
            right_plate.animate.shift(DOWN * 0.6 + LEFT * 0.1),
            left_plate.animate.shift(UP * 0.6 + RIGHT * 0.1),
            FadeIn(zero_weight), FadeIn(zero_text),
            run_time=4.4
        )
        self.wait(1.0)

class Scene08_03(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "IT'S MATHEMATICALLY GUARANTEED TO FAIL")
        
        # Visual: A robot with an "ERROR" screen
        head = RoundedRectangle(height=1.5, width=2, corner_radius=0.2, color="#FFFFFF").move_to(UP * -0.5)
        antenna = Line(head.get_top(), head.get_top() + UP * 0.4, color="#FFFFFF")
        error_text = Text("ERROR", font="Arial", weight=BOLD, font_size=30, color="#FFFFFF").move_to(head.get_center())
        body = Rectangle(height=1, width=2.5, color="#FFFFFF").next_to(head, DOWN, buff=0.1)
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(head), Create(antenna), Create(body), run_time=1.5)
        self.play(error_text.animate.set_opacity(0.2), run_time=0.5)
        self.play(error_text.animate.set_opacity(1.0), run_time=0.5)
        self.play(error_text.animate.scale(1.2), run_time=3.4)
        self.wait(1.0)

class Scene08_04(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "IT'S MATHEMATICALLY GUARANTEED TO FAIL")
        
        # Visual: An intake pipe leaking mathematical symbols
        pipe = Rectangle(height=0.6, width=4, color="#FFFFFF").move_to(UP * -0.2)
        leak_point = pipe.get_bottom() + LEFT * 0.5
        leak_stream = VGroup(*[DashedLine(leak_point, leak_point + DOWN * 1.5, color="#FFFFFF") for _ in range(3)])
        math_sym = Text("Σ  π  √", font="Arial", font_size=18, color="#FFFFFF").next_to(leak_stream, DOWN)
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(pipe), run_time=1.5)
        self.play(Create(leak_stream), Write(math_sym), run_time=4.4)
        self.wait(1.0)

class Scene08_05(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "IT'S MATHEMATICALLY GUARANTEED TO FAIL")
        
        # Visual: A server rack with a large "X" through it
        server = VGroup(*[RoundedRectangle(height=0.4, width=2, corner_radius=0.1, color="#FFFFFF") for _ in range(4)]).arrange(DOWN, buff=0.15).move_to(UP * -0.8)
        lights = VGroup(*[Circle(radius=0.05, color="#FFFFFF", fill_opacity=1).move_to(s.get_left() + RIGHT * 0.3) for s in server])
        cross_line1 = Line(server.get_corner(UL), server.get_corner(DR), color="#FFFFFF", stroke_width=8)
        cross_line2 = Line(server.get_corner(UR), server.get_corner(DL), color="#FFFFFF", stroke_width=8)
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(server), Create(lights), run_time=1.5)
        self.play(Create(cross_line1), Create(cross_line2), run_time=4.4)
        self.wait(1.0)

class Scene08_06(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "IT'S MATHEMATICALLY GUARANTEED TO FAIL")
        
        # Visual: Multiple arrows crashing into a floor
        floor = Line(LEFT * 3, RIGHT * 3, color="#FFFFFF", stroke_width=3).move_to(DOWN * 2)
        arrows = VGroup(*[Arrow(UP * 0.5, DOWN * 1.8, color="#FFFFFF", buff=0).shift(LEFT * (i - 1.5)) for i in range(4)])
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(floor), run_time=1.5)
        self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.3), run_time=4.4)
        self.wait(1.0)

class Scene08_07(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "IT'S MATHEMATICALLY GUARANTEED TO FAIL")
        
        # Visual: An electric plug being disconnected
        socket = Rectangle(height=1.2, width=1.2, color="#FFFFFF").move_to(LEFT * 1)
        plug = Rectangle(height=0.8, width=1, color="#FFFFFF").move_to(RIGHT * 1)
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(socket), Create(plug), run_time=1.5)
        self.play(plug.animate.shift(RIGHT * 1.5), run_time=4.4)
        self.wait(1.0)

# CANVAS CONFIGURATION

def get_footer(*args, **kwargs):
    class _DummyScene:
        def add(self, *a, **k): pass
        def play(self, *a, **k): pass
    scene = next((a for a in args if hasattr(a, 'play')), _DummyScene())
    self = scene
    str_args = [a for a in args if isinstance(a, str)]
    title_text = kwargs.get('title_text') or kwargs.get('title_str') or (str_args[0] if len(str_args) >= 1 else 'AI AUTONOMY')
    category_text = kwargs.get('category_text') or kwargs.get('category') or (str_args[1] if len(str_args) >= 2 else (str_args[0] if len(str_args) == 1 else 'ECONOMIC AUTONOMY'))
    category = category_text
    category_name = category_text
    category_label = category_text
    title_str = title_text
    text_str = title_text

    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene08_08(Scene):
    def construct(self):
        # Title
        title = Text("MATHEMATICAL IMPOSSIBILITY", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time=0.6)
        get_footer(self, "SYSTEM ANALYSIS")

        # Visual: 1 + 1 = 3 with a massive X
        equation = Text("1 + 1 = 3", font="Arial", font_size=60, color="#FFFFFF").move_to(UP * -1)
        cross_l = Line(LEFT * 2 + UP * 1, RIGHT * 2 + DOWN * 1, color="#FFFFFF", stroke_width=12).move_to(equation.get_center())
        cross_r = Line(LEFT * 2 + DOWN * 1, RIGHT * 2 + UP * 1, color="#FFFFFF", stroke_width=12).move_to(equation.get_center())
        
        self.play(Write(equation), run_time=2.0)
        self.play(Create(cross_l), Create(cross_r), run_time=1.0)
        self.play(equation.animate.set_opacity(0.3), run_time=1.0)
        self.wait(2.9)

class Scene08_09(Scene):
    def construct(self):
        title = Text("STRUCTURAL IMBALANCE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time=0.6)
        get_footer(self, "SYSTEM ANALYSIS")

        # Visual: A balance scale tipping over
        pivot = Triangle(color="#FFFFFF", fill_opacity=1).scale(0.3).move_to(DOWN * 2)
        beam = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=8).move_to(DOWN * 1.7)
        left_weight = Circle(radius=0.3, color="#FFFFFF", fill_opacity=0.2).next_to(beam.get_left(), UP, buff=0)
        right_weight = Circle(radius=0.8, color="#FFFFFF", fill_opacity=1).next_to(beam.get_right(), UP, buff=0)
        
        scale_group = VGroup(beam, left_weight, right_weight)
        
        self.play(Create(pivot), Create(beam), FadeIn(left_weight), FadeIn(right_weight), run_time=2.0)
        self.play(Rotate(scale_group, angle=-30*DEGREES, about_point=pivot.get_top()), run_time=2.0)
        
        crack = VGroup(
            Line(pivot.get_top(), pivot.get_top() + DOWN * 0.5 + LEFT * 0.2),
            Line(pivot.get_top() + DOWN * 0.5 + LEFT * 0.2, pivot.get_top() + DOWN * 1.0)
        ).set_color("#FFFFFF")
        
        self.play(Create(crack), run_time=0.5)
        self.wait(2.4)

class Scene08_10(Scene):
    def construct(self):
        title = Text("SYSTEMIC COLLAPSE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time=0.6)
        get_footer(self, "SYSTEM ANALYSIS")

        # Visual: Gears jamming
        gear1 = Circle(radius=1, color="#FFFFFF", stroke_width=4).move_to(LEFT * 1.2 + DOWN * 1)
        gear2 = Circle(radius=1, color="#FFFFFF", stroke_width=4).move_to(RIGHT * 1.2 + DOWN * 1)
        
        jam_block = Rectangle(width=0.6, height=0.6, color="#FFFFFF", fill_opacity=1).move_to(DOWN * 1)
        
        self.play(Create(gear1), Create(gear2), run_time=2.0)
        self.play(gear1.animate.rotate(PI), gear2.animate.rotate(-PI), run_time=2.0, rate_func=linear)
        self.play(FadeIn(jam_block, scale=1.5), run_time=0.5)
        
        # Shake effect
        self.play(
            gear1.animate.shift(LEFT * 0.1), gear2.animate.shift(RIGHT * 0.1),
            run_time=0.1, rate_func=wiggle
        )
        self.wait(2.3)

class Scene08_11(Scene):
    def construct(self):
        title = Text("TERMINAL TRAJECTORY", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time=0.6)
        get_footer(self, "SYSTEM ANALYSIS")

        # Visual: A line graph crashing through the floor
        axes = VGroup(
            Line(LEFT * 3 + DOWN * 2, RIGHT * 3 + DOWN * 2), # X
            Line(LEFT * 3 + DOWN * 2, LEFT * 3 + UP * 0.5)   # Y
        ).set_color("#FFFFFF").set_opacity(0.5)
        
        graph_line = VGroup(
            Line(LEFT * 3 + UP * 0.2, LEFT * 1 + DOWN * 0.5),
            Line(LEFT * 1 + DOWN * 0.5, RIGHT * 1 + DOWN * 1.5),
            Line(RIGHT * 1 + DOWN * 1.5, RIGHT * 2.5 + DOWN * 2.5)
        ).set_color("#FFFFFF").set_stroke(width=6)
        
        floor_crack = VGroup(
            Line(RIGHT * 1.5 + DOWN * 2, RIGHT * 2 + DOWN * 2.2),
            Line(RIGHT * 2 + DOWN * 2.2, RIGHT * 2.5 + DOWN * 2)
        ).set_color("#FFFFFF")

        self.play(Create(axes), run_time=1.5)
        self.play(Create(graph_line), run_time=3.0)
        self.play(Create(floor_crack), run_time=0.5)
        self.wait(1.9)

class Scene08_12(Scene):
    def construct(self):
        title = Text("LOGICAL ERROR", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time=0.6)
        get_footer(self, "SYSTEM ANALYSIS")

        # Visual: Calculator showing ERROR
        calc_body = RoundedRectangle(corner_radius=0.2, height=3, width=2.5, color="#FFFFFF", stroke_width=4).move_to(DOWN * 1)
        screen = Rectangle(height=0.8, width=2, color="#FFFFFF", fill_opacity=0.1).move_to(DOWN * 0.2)
        error_text = Text("ERROR", font="Courier New", weight=BOLD, font_size=30, color="#FFFFFF").move_to(screen.get_center())
        
        buttons = VGroup(*[Circle(radius=0.15, color="#FFFFFF") for _ in range(6)]).arrange_in_grid(rows=2, cols=3, buff=0.3).next_to(screen, DOWN, buff=0.4)

        self.play(Create(calc_body), Create(screen), Create(buttons), run_time=2.0)
        self.wait(0.5)
        for _ in range(3):
            self.play(FadeIn(error_text), run_time=0.4)
            self.wait(0.4)
        self.play(FadeIn(error_text), run_time=0.2)
        self.wait(1.8)

class Scene08_13(Scene):
    def construct(self):
        title = Text("INEVITABLE BREAKDOWN", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time=0.6)
        get_footer(self, "SYSTEM ANALYSIS")

        # Visual: A bridge with a missing segment
        left_bridge = Line(LEFT * 3 + DOWN * 1, LEFT * 0.5 + DOWN * 1, color="#FFFFFF", stroke_width=8)
        right_bridge = Line(RIGHT * 0.5 + DOWN * 1, RIGHT * 3 + DOWN * 1, color="#FFFFFF", stroke_width=8)
        supports = VGroup(
            Line(LEFT * 2.5 + DOWN * 1, LEFT * 2.5 + DOWN * 2.5),
            Line(RIGHT * 2.5 + DOWN * 1, RIGHT * 2.5 + DOWN * 2.5)
        ).set_color("#FFFFFF").set_opacity(0.5)
        
        ball = Circle(radius=0.2, color="#FFFFFF", fill_opacity=1).move_to(LEFT * 2.8 + DOWN * 0.7)

        self.play(Create(left_bridge), Create(right_bridge), Create(supports), run_time=2.0)
        self.play(ball.animate.shift(RIGHT * 2.3), run_time=2.0, rate_func=linear)
        self.play(ball.animate.shift(DOWN * 2 + RIGHT * 0.5), run_time=1.5, rate_func=acceleration)
        self.wait(1.4)

class Scene08_14(Scene):
    def construct(self):
        title = Text("GUARANTEED FAILURE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time=0.6)
        get_footer(self, "SYSTEM ANALYSIS")

        # Visual: A document being stamped "FAILED"
        paper = Rectangle(height=2.5, width=2, color="#FFFFFF", fill_opacity=0.05).move_to(DOWN * 1)
        lines = VGroup(*[Line(LEFT * 0.7, RIGHT * 0.7, color="#FFFFFF", stroke_width=1) for _ in range(5)]).arrange(DOWN, buff=0.3).move_to(paper.get_center())
        
        stamp_box = Rectangle(height=0.8, width=1.8, color="#FFFFFF", stroke_width=6).move_to(paper.get_center()).rotate(15*DEGREES)
        stamp_text = Text("FAILED", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to(stamp_box.get_center()).rotate(15*DEGREES)
        stamp = VGroup(stamp_box, stamp_text).scale(5).set_opacity(0)

        self.play(Create(paper), Create(lines), run_time=2.0)
        self.wait(1.0)
        self.play(
            stamp.animate.scale(0.2).set_opacity(1),
            run_time=0.4,
            rate_func=ease_in_back
        )
        # Screen shake
        self.play(self.camera.frame.animate.shift(UP * 0.1), run_time=0.05)
        self.play(self.camera.frame.animate.shift(DOWN * 0.1), run_time=0.05)
        self.wait(3.4)