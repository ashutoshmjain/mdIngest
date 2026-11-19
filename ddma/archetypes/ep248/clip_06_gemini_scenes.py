import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



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
    left_text = Text(category, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

def get_title(scene, text="PERISHABLE COMPUTE !"):
    title = Text(text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    return title

class Scene06_01(Scene):
    def construct(self):
        get_footer(self)
        # Visual: Commercial airplane flying past clouds with empty cabin seats (We should show a commercial airplane flying)
        fuselage = RoundedRectangle(width=3.6, height=0.82, corner_radius=0.41, color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0).move_to([0, -0.35, 0])
        nose_cockpit = Arc(radius=0.38, start_angle=-PI/3, angle=2*PI/3, color="#FFFFFF", stroke_width=3).move_to([1.52, -0.32, 0])
        tail_fin = Polygon([-1.65, 0.0, 0], [-2.25, 1.05, 0], [-1.15, 0.0, 0], color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0)
        wing_bottom = Polygon([-0.55, -0.45, 0], [-1.35, -1.55, 0], [-0.25, -1.55, 0], [0.55, -0.45, 0], color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0)
        wing_top = Polygon([-0.35, 0.05, 0], [-0.95, 0.78, 0], [-0.15, 0.78, 0], [0.35, 0.05, 0], color="#FFFFFF", stroke_width=3, fill_color="#000000", fill_opacity=1.0)
        engine = RoundedRectangle(width=0.65, height=0.30, corner_radius=0.12, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.18).move_to([-0.5, -1.12, 0])

        # Illuminated empty passenger windows along the cabin
        windows = VGroup(*[
            RoundedRectangle(width=0.22, height=0.26, corner_radius=0.06, color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([-1.05 + i * 0.44, -0.32, 0])
            for i in range(6)
        ])
        tag = Text("EMPTY SEATS • PERISHABLE CAPACITY", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, -2.05, 0]).set_opacity(0.85)

        plane = VGroup(wing_top, tail_fin, fuselage, nose_cockpit, windows, wing_bottom, engine).shift(LEFT * 0.4 + DOWN * 0.15)

        # Fluffy clouds & slipstream lines rushing past
        cloud1 = VGroup(
            Circle(radius=0.28, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.1, 0.85, 0]),
            Circle(radius=0.36, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.45, 0.92, 0]),
            Circle(radius=0.26, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.8, 0.82, 0]),
        ).set_opacity(0.75)
        cloud2 = VGroup(
            Circle(radius=0.24, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.5, -1.55, 0]),
            Circle(radius=0.32, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.85, -1.48, 0]),
        ).set_opacity(0.65)
        wind_lines = VGroup(
            DashedLine([3.2, 0.35, 0], [-3.2, 0.35, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.45),
            DashedLine([3.2, -0.95, 0], [-3.2, -0.95, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.45),
        )

        self.play(FadeIn(plane, shift=RIGHT * 0.4 + UP * 0.15), FadeIn(cloud1), FadeIn(cloud2), Create(wind_lines), FadeIn(tag), run_time=1.6)
        self.play(
            plane.animate.shift(RIGHT * 0.85 + UP * 0.32).rotate(0.06),
            cloud1.animate.shift(LEFT * 4.4),
            cloud2.animate.shift(LEFT * 4.8),
            windows.animate.set_fill(opacity=0.45),
            run_time=10.3,
            rate_func=linear
        )
        self.wait(0.8)

class Scene06_02(Scene):
    def construct(self):
        get_footer(self)
        title = get_title(self)
        
        # Visual: Hourglass with compute blocks falling
        top_tri = Polygon([-1, 0.4, 0], [1, 0.4, 0], [0, -0.6, 0], color="#FFFFFF", stroke_width=2)
        bot_tri = Polygon([-1, -1.6, 0], [1, -1.6, 0], [0, -0.6, 0], color="#FFFFFF", stroke_width=2)
        block = Rectangle(width=0.3, height=0.2, color="#FFFFFF", fill_opacity=1).move_to([0, 0.1, 0])
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(top_tri), Create(bot_tri), run_time=1.0)
        
        # Falling blocks animation
        for i in range(5):
            b = block.copy()
            self.add(b)
            self.play(b.animate.move_to([0, -1.4, 0]).set_opacity(0), run_time=0.9, rate_func=ease_in_sine)
        
        self.wait(0.5)

class Scene06_03(Scene):
    def construct(self):
        get_footer(self)
        title = get_title(self)
        
        # Visual: A gauge/meter dropping from Full to Empty
        gauge = Arc(radius=1.8, start_angle=0, angle=PI, color="#FFFFFF", stroke_width=4).move_to(DOWN * 1.2)
        needle = Arrow(gauge.get_center(), gauge.get_center() + RIGHT * 1.5, buff=0, color="#FFFFFF", stroke_width=5)
        label_f = Text("F", font_size=15, color="#FFFFFF").next_to(gauge, RIGHT, buff=0.1)
        label_e = Text("E", font_size=15, color="#FFFFFF").next_to(gauge, LEFT, buff=0.1)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(gauge), Create(needle), Write(label_f), Write(label_e), run_time=1.0)
        self.play(Rotate(needle, angle=PI, about_point=gauge.get_center()), run_time=5.4, rate_func=slow_into)
        self.wait(0.6)

class Scene06_04(Scene):
    def construct(self):
        get_footer(self)
        title = get_title(self)
        
        # Visual: Server with a "USE BY" stamp
        server = RoundedRectangle(width=2.5, height=1.5, color="#FFFFFF", stroke_width=2).move_to(DOWN * 0.8)
        label = Text("COMPUTE UNIT", font_size=15, color="#FFFFFF").move_to(server.get_center())
        stamp_box = Rectangle(width=1.8, height=0.6, color="#FFFFFF", stroke_width=3).move_to(DOWN * 0.8).set_opacity(0)
        stamp_text = Text("EXPIRED", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to(stamp_box.get_center()).set_opacity(0)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(server), Write(label), run_time=1.0)
        self.wait(1.0)
        self.play(
            stamp_box.animate.set_opacity(1).scale(1.2),
            stamp_text.animate.set_opacity(1).scale(1.2),
            run_time=0.4, rate_func=bounce_it
        )
        self.play(VGroup(server, label, stamp_box, stamp_text).animate.set_opacity(0.2), run_time=4.0)
        self.wait(0.6)

class Scene06_05(Scene):
    def construct(self):
        get_footer(self)
        # Visual: 100-meter sprinter racing against a ticking stopwatch toward the finish line (Visualize race against time as a 100 meter race)
        track_top = Line([-3.1, -0.85, 0], [3.1, -0.85, 0], color="#FFFFFF", stroke_width=3).set_opacity(0.6)
        track_mid = DashedLine([-3.1, -1.35, 0], [3.1, -1.35, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.45)
        track_bot = Line([-3.1, -1.85, 0], [3.1, -1.85, 0], color="#FFFFFF", stroke_width=4)
        finish_pole = Line([2.55, 0.25, 0], [2.55, -1.85, 0], color="#FFFFFF", stroke_width=4)
        finish_banner = RoundedRectangle(width=1.05, height=0.34, corner_radius=0.05, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.55, 0.45, 0])
        finish_txt = Text("100M", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(finish_banner.get_center())

        # Ticking Stopwatch above the track
        clock_ring = Circle(radius=0.58, color="#FFFFFF", stroke_width=3.5).move_to([0.0, 0.45, 0])
        clock_btn = Rectangle(width=0.22, height=0.12, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).next_to(clock_ring, UP, buff=0.02)
        clock_hand = Line(clock_ring.get_center(), clock_ring.get_center() + UP * 0.44, color="#FFFFFF", stroke_width=4)

        # Dynamic Sprinter Figure (Head, Torso, Pumping Arms & Striding Legs)
        r_head = Circle(radius=0.18, color="#FFFFFF", stroke_width=3.5, fill_color="#FFFFFF", fill_opacity=0.2).move_to([-2.0, -0.15, 0])
        r_torso = Line([-2.05, -0.33, 0], [-2.25, -0.95, 0], color="#FFFFFF", stroke_width=5)
        r_arm_f = Line([-2.12, -0.52, 0], [-1.72, -0.38, 0], color="#FFFFFF", stroke_width=3.5)
        r_arm_b = Line([-2.12, -0.52, 0], [-2.52, -0.68, 0], color="#FFFFFF", stroke_width=3.5)
        r_leg_f = Line([-2.25, -0.95, 0], [-1.82, -1.55, 0], color="#FFFFFF", stroke_width=4)
        r_leg_b = Line([-2.25, -0.95, 0], [-2.65, -1.52, 0], color="#FFFFFF", stroke_width=4)
        speed_lines = VGroup(
            Line([-3.0, -0.35, 0], [-2.45, -0.35, 0], color="#FFFFFF", stroke_width=2.5).set_opacity(0.6),
            Line([-3.1, -0.75, 0], [-2.55, -0.75, 0], color="#FFFFFF", stroke_width=2.5).set_opacity(0.6),
        )
        sprinter = VGroup(r_head, r_torso, r_arm_f, r_arm_b, r_leg_f, r_leg_b, speed_lines)
        tag = Text("100M SPRINT • RACE AGAINST TIME", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, -2.25, 0]).set_opacity(0.85)

        self.play(
            Create(track_top), Create(track_mid), Create(track_bot),
            Create(finish_pole), FadeIn(finish_banner), FadeIn(finish_txt),
            Create(clock_ring), FadeIn(clock_btn), Create(clock_hand),
            FadeIn(sprinter, shift=RIGHT * 0.3), FadeIn(tag),
            run_time=1.6
        )
        self.play(
            sprinter.animate.shift(RIGHT * 4.15),
            Rotate(clock_hand, angle=-6 * PI, about_point=clock_ring.get_center()),
            finish_banner.animate.set_fill(color="#FFFFFF", opacity=0.25),
            run_time=10.3,
            rate_func=linear
        )
        self.wait(0.8)

class Scene06_06(Scene):
    def construct(self):
        get_footer(self)
        # Visual: Commercial airplane flying past clouds with empty cabin seats (We should simply show a commercial aeroplane)
        fuselage = RoundedRectangle(width=3.6, height=0.82, corner_radius=0.41, color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0).move_to([0, -0.35, 0])
        nose_cockpit = Arc(radius=0.38, start_angle=-PI/3, angle=2*PI/3, color="#FFFFFF", stroke_width=3).move_to([1.52, -0.32, 0])
        tail_fin = Polygon([-1.65, 0.0, 0], [-2.25, 1.05, 0], [-1.15, 0.0, 0], color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0)
        wing_bottom = Polygon([-0.55, -0.45, 0], [-1.35, -1.55, 0], [-0.25, -1.55, 0], [0.55, -0.45, 0], color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0)
        wing_top = Polygon([-0.35, 0.05, 0], [-0.95, 0.78, 0], [-0.15, 0.78, 0], [0.35, 0.05, 0], color="#FFFFFF", stroke_width=3, fill_color="#000000", fill_opacity=1.0)
        engine = RoundedRectangle(width=0.65, height=0.30, corner_radius=0.12, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.18).move_to([-0.5, -1.12, 0])

        # Illuminated empty passenger windows along the cabin
        windows = VGroup(*[
            RoundedRectangle(width=0.22, height=0.26, corner_radius=0.06, color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([-1.05 + i * 0.44, -0.32, 0])
            for i in range(6)
        ])
        tag = Text("EMPTY SEATS • PERISHABLE CAPACITY", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, -2.05, 0]).set_opacity(0.85)

        plane = VGroup(wing_top, tail_fin, fuselage, nose_cockpit, windows, wing_bottom, engine).shift(LEFT * 0.4 + DOWN * 0.15)

        # Fluffy clouds & slipstream lines rushing past
        cloud1 = VGroup(
            Circle(radius=0.28, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.1, 0.85, 0]),
            Circle(radius=0.36, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.45, 0.92, 0]),
            Circle(radius=0.26, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.8, 0.82, 0]),
        ).set_opacity(0.75)
        cloud2 = VGroup(
            Circle(radius=0.24, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.5, -1.55, 0]),
            Circle(radius=0.32, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.85, -1.48, 0]),
        ).set_opacity(0.65)
        wind_lines = VGroup(
            DashedLine([3.2, 0.35, 0], [-3.2, 0.35, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.45),
            DashedLine([3.2, -0.95, 0], [-3.2, -0.95, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.45),
        )

        self.play(FadeIn(plane, shift=RIGHT * 0.4 + UP * 0.15), FadeIn(cloud1), FadeIn(cloud2), Create(wind_lines), FadeIn(tag), run_time=1.6)
        self.play(
            plane.animate.shift(RIGHT * 0.85 + UP * 0.32).rotate(0.06),
            cloud1.animate.shift(LEFT * 4.4),
            cloud2.animate.shift(LEFT * 4.8),
            windows.animate.set_fill(opacity=0.45),
            run_time=10.3,
            rate_func=linear
        )
        self.wait(0.8)

class Scene06_07(Scene):
    def construct(self):
        get_footer(self)
        title = get_title(self)
        
        # Visual: A server inside a melting ice cube
        ice_cube = RoundedRectangle(width=2.2, height=2.2, corner_radius=0.4, color="#FFFFFF", stroke_width=2).move_to(DOWN * 1.0)
        server_core = Rectangle(width=1.0, height=0.6, color="#FFFFFF", fill_opacity=1).move_to(ice_cube.get_center())
        drips = VGroup(Circle(radius=0.05, fill_opacity=1).move_to(DOWN*2.1 + LEFT*0.5), Circle(radius=0.05, fill_opacity=1).move_to(DOWN*2.1 + RIGHT*0.3))
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(ice_cube), Create(server_core), run_time=1.0)
        
        self.play(
            ice_cube.animate.scale(0.4).set_opacity(0.2),
            server_core.animate.set_opacity(0.1),
            drips.animate.shift(DOWN * 0.5).set_opacity(0),
            run_time=5.4, rate_func=linear
        )
        self.wait(0.6)

# Configuration for 740x740 Square Video

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
    left_text = Text(category, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene06_15(Scene):
    def construct(self):
        # Title and Footer
        title = Text("PERISHABLE COMPUTE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        get_footer(self, "COMPUTE ECONOMICS")
        
        # Visual: Server Rack with a Clock (Time is running out)
        server = VGroup(
            RoundedRectangle(corner_radius=0.1, height=1.5, width=1.2, color="#FFFFFF", stroke_width=3),
            Line(LEFT*0.4, RIGHT*0.4, color="#FFFFFF").shift(UP*0.3),
            Line(LEFT*0.4, RIGHT*0.4, color="#FFFFFF").shift(ORIGIN),
            Line(LEFT*0.4, RIGHT*0.4, color="#FFFFFF").shift(DOWN*0.3)
        ).move_to(LEFT * 1.2 + DOWN * 1.0)
        
        clock_face = Circle(radius=0.8, color="#FFFFFF", stroke_width=3).move_to(RIGHT * 1.2 + DOWN * 1.0)
        hour_hand = Line(clock_face.get_center(), clock_face.get_center() + UP * 0.5, color="#FFFFFF", stroke_width=4)
        minute_hand = Line(clock_face.get_center(), clock_face.get_center() + RIGHT * 0.6, color="#FFFFFF", stroke_width=2)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(server), Create(clock_face), Create(hour_hand), Create(minute_hand))
        
        # Animation: Clock spinning fast while server flickers/fades
        self.play(
            Rotate(hour_hand, -2 * PI, about_point=clock_face.get_center()),
            Rotate(minute_hand, -8 * PI, about_point=clock_face.get_center()),
            server.animate.set_opacity(0.2),
            run_time=5.0,
            rate_func=linear
        )
        self.wait(2.0)

class Scene06_16(Scene):
    def construct(self):
        title = Text("VANISHING CAPACITY", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        get_footer(self, "COMPUTE ECONOMICS")
        
        # Visual: A CPU chip that is "melting"
        chip = VGroup(
            Square(side_length=1.5, color="#FFFFFF", stroke_width=4),
            *[Line(ORIGIN, UP*0.2, color="#FFFFFF").shift(UP*0.75 + LEFT*(0.6 - i*0.4)) for i in range(4)],
            *[Line(ORIGIN, DOWN*0.2, color="#FFFFFF").shift(DOWN*0.75 + LEFT*(0.6 - i*0.4)) for i in range(4)],
            *[Line(ORIGIN, LEFT*0.2, color="#FFFFFF").shift(LEFT*0.75 + UP*(0.6 - i*0.4)) for i in range(4)],
            *[Line(ORIGIN, RIGHT*0.2, color="#FFFFFF").shift(RIGHT*0.75 + UP*(0.6 - i*0.4)) for i in range(4)]
        ).move_to(UP * -0.5)
        
        drips = VGroup(*[Circle(radius=0.05, color="#FFFFFF", fill_opacity=1).move_to(chip.get_bottom() + RIGHT*x) for x in np.arange(-0.6, 0.7, 0.3)])
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(chip))
        
        # Animation: Drips falling from the chip
        animations = []
        for drip in drips:
            animations.append(drip.animate(rate_func=slow_into).shift(DOWN * 1.5).set_opacity(0))
            
        self.play(AnimationGroup(*animations, lag_ratio=0.2), chip.animate.scale(0.8).set_opacity(0.5), run_time=6.0)
        self.wait(1.0)

class Scene06_17(Scene):
    def construct(self):
        title = Text("TIME-BOUND UTILITY", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        get_footer(self, "COMPUTE ECONOMICS")
        
        # Visual: Hourglass with binary code falling
        top_tri = Polygon([-1, 1, 0], [1, 1, 0], [0, 0, 0], color="#FFFFFF", stroke_width=3)
        bot_tri = Polygon([-1, -1, 0], [1, -1, 0], [0, 0, 0], color="#FFFFFF", stroke_width=3)
        hourglass = VGroup(top_tri, bot_tri).move_to(UP * -0.8)
        
        binary_0 = Text("0", font="Courier", font_size=15, color="#FFFFFF").move_to(UP * -0.5)
        binary_1 = Text("1", font="Courier", font_size=15, color="#FFFFFF").move_to(UP * -0.3)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(hourglass))
        
        # Animation: Binary digits falling through the center
        def fall_binary(mobject):
            mobject.shift(DOWN * 0.1)
            if mobject.get_center()[1] < -1.8:
                mobject.move_to(UP * -0.5 + RIGHT * np.random.uniform(-0.2, 0.2))

        b_stream = VGroup(*[Text(np.random.choice(["0", "1"]), font="Courier", font_size=12).move_to(UP * -0.5 + RIGHT * np.random.uniform(-0.3, 0.3) + UP * np.random.uniform(0, 0.5)) for _ in range(10)])
        
        self.play(FadeIn(b_stream))
        self.play(
            *[m.animate.shift(DOWN * 1.2).set_opacity(0) for m in b_stream],
            run_time=6.0,
            rate_func=linear
        )
        self.wait(1.0)

class Scene06_18(Scene):
    def construct(self):
        title = Text("IDLE LOSS", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        get_footer(self, "COMPUTE ECONOMICS")
        
        # Visual: Conveyor belt moving server icons into a trash bin
        belt = Line(LEFT * 2.5, RIGHT * 1.0, color="#FFFFFF", stroke_width=2).shift(DOWN * 1.0)
        wheels = VGroup(Circle(radius=0.15, color="#FFFFFF").move_to(LEFT*2.3 + DOWN*1.2), Circle(radius=0.15, color="#FFFFFF").move_to(RIGHT*0.8 + DOWN*1.2))
        bin_obj = VGroup(
            Line(LEFT*0.5, LEFT*0.4 + DOWN*0.8),
            Line(RIGHT*0.5, RIGHT*0.4 + DOWN*0.8),
            Line(LEFT*0.4 + DOWN*0.8, RIGHT*0.4 + DOWN*0.8)
        ).move_to(RIGHT * 2.0 + DOWN * 1.8)
        
        server_icon = Square(side_length=0.4, color="#FFFFFF", fill_opacity=0.2).move_to(LEFT * 2.0 + DOWN * 0.8)
        
        self.play(FadeIn(title), run_time=0.6)
        self.add(belt, wheels, bin_obj)
        
        # Animation: Servers moving across and falling
        for i in range(3):
            s = server_icon.copy()
            self.add(s)
            self.play(
                s.animate.move_to(RIGHT * 0.8 + DOWN * 0.8),
                run_time=1.5,
                rate_func=linear
            )
            self.play(
                s.animate.move_to(RIGHT * 2.0 + DOWN * 2.0).set_opacity(0),
                run_time=0.5
            )
            
        self.wait(1.0)

class Scene06_19(Scene):
    def construct(self):
        title = Text("EXPIRING RESOURCES", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        get_footer(self, "COMPUTE ECONOMICS")
        
        # Visual: A battery meter labeled "COMPUTE" draining rapidly
        battery_shell = RoundedRectangle(corner_radius=0.1, height=1.2, width=2.5, color="#FFFFFF", stroke_width=4).move_to(UP * -0.8)
        battery_tip = Rectangle(height=0.4, width=0.2, color="#FFFFFF", fill_opacity=1).next_to(battery_shell, RIGHT, buff=0)
        
        fill = Rectangle(height=1.0, width=2.3, color="#FFFFFF", fill_opacity=0.8).move_to(battery_shell.get_center())
        label = Text("COMPUTE", font="Arial", weight=BOLD, font_size=15, color="#000000").move_to(fill.get_center())
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(battery_shell), Create(battery_tip), FadeIn(fill), FadeIn(label))
        
        # Animation: Battery draining to zero
        self.play(
            fill.animate.scale(0.01, about_edge=LEFT).set_opacity(0),
            label.animate.set_opacity(0),
            run_time=5.5,
            rate_func=linear
        )
        
        # Final flash of "EXPIRED"
        expired = Text("EXPIRED", font="Arial", weight=BOLD, font_size=30, color="#FFFFFF").move_to(UP * -0.8)
        self.play(Write(expired), run_time=0.5)
        self.wait(1.0)