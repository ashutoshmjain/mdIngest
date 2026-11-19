import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Configuration for 740x740 square monochrome output

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

    """Standard footer and title placement for all scenes."""
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    title = Text("AGENTIC AUTONOMY MYTH", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    return VGroup(footer_line, left_text, right_text, title)

class Scene04_01(Scene):
    def construct(self):
        # UI Elements
        footer = get_footer(self)
        self.add(footer[0], footer[1], footer[2])
        self.play(FadeIn(footer[3]), run_time=0.6)

        # Visual: Robot Head with Cut Wires (Literal "Autonomy Myth")
        head = RoundedRectangle(corner_radius=0.2, height=1.5, width=1.8, color="#FFFFFF", stroke_width=4).move_to(UP * -0.8)
        eye_l = Circle(radius=0.15, color="#FFFFFF", stroke_width=2).move_to(head.get_center() + LEFT * 0.4 + UP * 0.2)
        eye_r = Circle(radius=0.15, color="#FFFFFF", stroke_width=2).move_to(head.get_center() + RIGHT * 0.4 + UP * 0.2)
        antenna = Line(head.get_top(), head.get_top() + UP * 0.4, color="#FFFFFF", stroke_width=4)
        antenna_tip = Circle(radius=0.08, color="#FFFFFF", fill_opacity=1).move_to(antenna.get_end())
        
        wire_left = DashedLine(head.get_bottom() + LEFT * 0.3, head.get_bottom() + DOWN * 0.8 + LEFT * 0.6, color="#FFFFFF")
        wire_right = DashedLine(head.get_bottom() + RIGHT * 0.3, head.get_bottom() + DOWN * 0.8 + RIGHT * 0.6, color="#FFFFFF")
        
        robot = VGroup(head, eye_l, eye_r, antenna, antenna_tip, wire_left, wire_right).move_to(ORIGIN + DOWN * 0.5)
        
        self.play(Create(robot), run_time=1.5)
        self.play(robot.animate.shift(UP * 0.2), run_time=2)
        self.play(robot.animate.shift(DOWN * 0.2), run_time=2.3)
        self.wait(1.0)

class Scene04_02(Scene):
    def construct(self):
        footer = get_footer(self)
        self.add(footer[0], footer[1], footer[2])
        self.play(FadeIn(footer[3]), run_time=0.6)

        # Visual: Puppet Strings (Literal "Controlled Autonomy")
        control_bar = Line(LEFT * 1.5, RIGHT * 1.5, color="#FFFFFF", stroke_width=6).move_to(UP * 0.2)
        string_l = Line(control_bar.get_left(), DOWN * 1.5 + LEFT * 1.0, color="#FFFFFF", stroke_width=1).set_opacity(0.6)
        string_r = Line(control_bar.get_right(), DOWN * 1.5 + RIGHT * 1.0, color="#FFFFFF", stroke_width=1).set_opacity(0.6)
        
        puppet_body = RoundedRectangle(height=1.0, width=0.8, color="#FFFFFF", stroke_width=3).move_to(DOWN * 1.5)
        puppet_head = Circle(radius=0.3, color="#FFFFFF", stroke_width=3).next_to(puppet_body, UP, buff=0.1)
        puppet = VGroup(puppet_body, puppet_head)
        
        self.play(Create(control_bar), Create(string_l), Create(string_r), FadeIn(puppet), run_time=1.5)
        self.play(VGroup(control_bar, string_l, string_r, puppet).animate.shift(LEFT * 0.5), run_time=2.1)
        self.play(VGroup(control_bar, string_l, string_r, puppet).animate.shift(RIGHT * 1.0), run_time=2.2)
        self.wait(1.0)

class Scene04_03(Scene):
    def construct(self):
        footer = get_footer(self)
        self.add(footer[0], footer[1], footer[2])
        self.play(FadeIn(footer[3]), run_time=0.6)

        # Visual: A Robot with a giant "Remote Control" pointing at it
        robot = VGroup(
            Circle(radius=0.4, color="#FFFFFF", stroke_width=3),
            Rectangle(height=0.8, width=0.6, color="#FFFFFF", stroke_width=3).shift(DOWN * 0.7)
        ).move_to(LEFT * 1.2 + DOWN * 0.5)
        
        remote = RoundedRectangle(height=1.2, width=0.6, color="#FFFFFF", stroke_width=3).move_to(RIGHT * 1.5 + DOWN * 0.5)
        button = Circle(radius=0.1, color="#FFFFFF", fill_opacity=1).move_to(remote.get_center() + UP * 0.3)
        antenna = Line(remote.get_top(), remote.get_top() + UP * 0.3 + LEFT * 0.2, color="#FFFFFF")
        signal = VGroup(
            Arc(radius=0.3, start_angle=150*DEGREES, angle=60*DEGREES, color="#FFFFFF"),
            Arc(radius=0.5, start_angle=150*DEGREES, angle=60*DEGREES, color="#FFFFFF")
        ).move_to(remote.get_left() + LEFT * 0.4 + UP * 0.2).rotate(PI/2)

        self.play(Create(robot), Create(remote), Create(button), Create(antenna), run_time=1.5)
        self.play(Create(signal), run_time=1.0)
        self.play(robot.animate.shift(UP * 0.3), run_time=1.5)
        self.play(robot.animate.shift(DOWN * 0.3), run_time=1.8)
        self.wait(1.0)

class Scene04_04(Scene):
    def construct(self):
        footer = get_footer(self)
        self.add(footer[0], footer[1], footer[2])
        self.play(FadeIn(footer[3]), run_time=0.6)

        # Visual: Robot plugged into a wall (Literal dependence)
        wall = Line(LEFT * 3, LEFT * 3 + DOWN * 2, color="#FFFFFF", stroke_width=8).move_to(LEFT * 2.5 + DOWN * 1)
        socket = Rectangle(height=0.4, width=0.3, color="#FFFFFF").move_to(wall.get_center() + RIGHT * 0.2)
        
        robot = VGroup(
            Circle(radius=0.5, color="#FFFFFF", stroke_width=4),
            Line(DOWN * 0.5, DOWN * 1.2, color="#FFFFFF", stroke_width=4)
        ).move_to(RIGHT * 1.5 + DOWN * 0.5)
        
        cord = Line(robot.get_left(), socket.get_center(), color="#FFFFFF", stroke_width=2)
        
        self.play(Create(wall), Create(socket), Create(robot), run_time=1.5)
        self.play(Create(cord), run_time=1.0)
        self.play(robot.animate.shift(RIGHT * 0.3), run_time=2.0)
        self.play(robot.animate.shift(LEFT * 0.3), run_time=1.3)
        self.wait(1.0)

class Scene04_05(Scene):
    def construct(self):
        footer = get_footer(self)
        self.add(footer[0], footer[1], footer[2])
        self.play(FadeIn(footer[3]), run_time=0.6)

        # Visual: "MYTH" Stamp over a robot icon
        robot_icon = VGroup(
            Circle(radius=0.6, color="#FFFFFF", stroke_width=2),
            Line(UP * 0.3, DOWN * 0.3, color="#FFFFFF"),
            Line(LEFT * 0.3, RIGHT * 0.3, color="#FFFFFF")
        ).move_to(DOWN * 0.8)
        
        stamp_box = Rectangle(height=1.0, width=2.5, color="#FFFFFF", stroke_width=5).move_to(UP * 2)
        stamp_text = Text("FALSE", font="Arial", weight=BOLD, font_size=30, color="#FFFFFF").move_to(stamp_box.get_center())
        stamp = VGroup(stamp_box, stamp_text)

        self.play(Create(robot_icon), run_time=1.0)
        self.play(stamp.animate.move_to(DOWN * 0.8), run_time=0.8, rate_func=exponential_decay)
        self.play(Flash(robot_icon, color="#FFFFFF", line_length=0.4), run_time=0.5)
        self.wait(3.5)
        self.wait(1.0)

class Scene04_06(Scene):
    def construct(self):
        footer = get_footer(self)
        self.add(footer[0], footer[1], footer[2])
        self.play(FadeIn(footer[3]), run_time=0.6)

        # Visual: A "Cloud" server controlling a small robot
        cloud = VGroup(
            Circle(radius=0.5).shift(LEFT * 0.4),
            Circle(radius=0.6).shift(UP * 0.2),
            Circle(radius=0.5).shift(RIGHT * 0.4),
            Rectangle(height=0.4, width=1.2).shift(DOWN * 0.2)
        ).set_fill("#000000", opacity=1).set_stroke("#FFFFFF", width=2).move_to(UP * 0.2)
        
        robot = RoundedRectangle(height=0.6, width=0.5, color="#FFFFFF").move_to(DOWN * 1.8)
        connection = DashedLine(cloud.get_bottom(), robot.get_top(), color="#FFFFFF")
        
        self.play(Create(cloud), run_time=1.5)
        self.play(Create(robot), run_time=1.0)
        self.play(Create(connection), run_time=1.0)
        self.play(connection.animate.set_stroke(width=5), run_time=1.0)
        self.play(connection.animate.set_stroke(width=1), run_time=1.3)
        self.wait(1.0)

class Scene04_07(Scene):
    def construct(self):
        footer = get_footer(self)
        self.add(footer[0], footer[1], footer[2])
        self.play(FadeIn(footer[3]), run_time=0.6)

        # Visual: Balance Scale - "Autonomy" vs "Control"
        base = Line(LEFT * 2, RIGHT * 2, color="#FFFFFF").move_to(DOWN * 2)
        pivot = Polygon([0,0,0], [0.3,-0.5,0], [-0.3,-0.5,0], color="#FFFFFF").move_to(DOWN * 1.75)
        beam = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=4).move_to(DOWN * 1.2)
        
        left_pan = Line(LEFT * 0.5, RIGHT * 0.5, color="#FFFFFF").move_to(beam.get_left() + DOWN * 0.5)
        right_pan = Line(LEFT * 0.5, RIGHT * 0.5, color="#FFFFFF").move_to(beam.get_right() + DOWN * 0.5)
        
        label_l = Text("AGENT", font_size=12, color="#FFFFFF").next_to(left_pan, DOWN)
        label_r = Text("CONTROL", font_size=12, color="#FFFFFF").next_to(right_pan, DOWN)
        
        scale = VGroup(beam, left_pan, right_pan, label_l, label_r)

        self.play(Create(base), Create(pivot), Create(scale), run_time=1.5)
        self.play(scale.animate.rotate(0.2, about_point=pivot.get_top()), run_time=2.0)
        self.play(scale.animate.rotate(-0.4, about_point=pivot.get_top()), run_time=2.3)
        self.wait(1.0)


# (Using universal get_footer_and_title from manim_compat)

class Scene04_08(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "AGENTIC AUTONOMY MYTH !")
        
        # Visual: Robot Puppet (The myth of independence)
        hand = VGroup(
            Rectangle(width=1.2, height=0.4, stroke_width=2),
            Line(ORIGIN, DOWN * 0.3).shift(LEFT * 0.4),
            Line(ORIGIN, DOWN * 0.3).shift(RIGHT * 0.4)
        ).move_to([0, 0.2, 0])
        
        strings = VGroup(
            DashedLine(hand.get_bottom() + LEFT*0.4, [ -0.5, -1.5, 0], stroke_width=1),
            DashedLine(hand.get_bottom() + RIGHT*0.4, [ 0.5, -1.5, 0], stroke_width=1)
        )
        
        robot = VGroup(
            RoundedRectangle(corner_radius=0.1, width=1.2, height=1.0, stroke_width=3),
            Circle(radius=0.15, stroke_width=2).shift(LEFT * 0.3 + UP * 0.1),
            Circle(radius=0.15, stroke_width=2).shift(RIGHT * 0.3 + UP * 0.1),
            Line(LEFT * 0.2, RIGHT * 0.2).shift(DOWN * 0.2)
        ).move_to([0, -1.8, 0])
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        
        self.play(Create(hand), Create(robot), run_time=1.5)
        self.play(Create(strings), run_time=1.0)
        
        # Puppet movement
        self.play(
            hand.animate.shift(RIGHT * 0.5),
            robot.animate.shift(RIGHT * 0.5),
            strings.animate.shift(RIGHT * 0.5),
            rate_func=wiggle,
            run_time=3.3
        )
        self.wait(1.0)

class Scene04_09(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "AGENTIC AUTONOMY MYTH !")
        
        # Visual: Steering wheel not connected to anything
        wheel = VGroup(
            Circle(radius=1.2, stroke_width=4),
            Line(LEFT * 1.2, RIGHT * 1.2),
            Line(UP * 1.2, DOWN * 1.2),
            Circle(radius=0.2, fill_opacity=1, color="#FFFFFF")
        ).move_to([0, -1.0, 0])
        
        broken_shaft = VGroup(
            Line([0, -2.2, 0], [0, -2.5, 0], stroke_width=2),
            Line([-0.2, -2.3, 0], [0.2, -2.4, 0], stroke_width=2)
        )
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        
        self.play(Create(wheel), run_time=1.5)
        self.play(Create(broken_shaft), run_time=0.8)
        
        # Spin wheel pointlessly
        self.play(Rotate(wheel, angle=PI*4), run_time=4.0, rate_func=linear)
        self.wait(0.5)

class Scene04_10(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "AGENTIC AUTONOMY MYTH !")
        
        # Visual: Robot head with a massive power cord (Dependence)
        head = VGroup(
            RoundedRectangle(width=1.8, height=1.5, corner_radius=0.2, stroke_width=3),
            Circle(radius=0.2).shift(LEFT*0.4 + UP*0.2),
            Circle(radius=0.2).shift(RIGHT*0.4 + UP*0.2),
            Rectangle(width=0.6, height=0.1).shift(DOWN*0.3)
        ).move_to([0, -0.5, 0])
        
        cord = VGroup(
            Line(head.get_bottom(), [0, -2.0, 0], stroke_width=4),
            Rectangle(width=0.8, height=0.5).move_to([0, -2.2, 0]),
            Line([-0.2, -2.45, 0], [-0.2, -2.7, 0], stroke_width=4),
            Line([0.2, -2.45, 0], [0.2, -2.7, 0], stroke_width=4)
        )
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        
        self.play(Create(head), run_time=1.5)
        self.play(Create(cord), run_time=1.5)
        
        # Pulse the cord to show energy flow/control
        self.play(cord.animate.set_stroke(opacity=0.3), run_time=0.8)
        self.play(cord.animate.set_stroke(opacity=1.0), run_time=0.8)
        self.play(cord.animate.set_stroke(opacity=0.3), run_time=0.8)
        self.play(cord.animate.set_stroke(opacity=1.0), run_time=1.4)

class Scene04_11(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "AGENTIC AUTONOMY MYTH !")
        
        # Visual: A curtain revealing the "Code" behind the "Agent"
        curtain_l = Rectangle(width=1.6, height=2.5, fill_opacity=1, color="#000000", stroke_color="#FFFFFF").move_to([-0.8, -1.0, 0])
        curtain_r = Rectangle(width=1.6, height=2.5, fill_opacity=1, color="#000000", stroke_color="#FFFFFF").move_to([0.8, -1.0, 0])
        
        label = Text("AUTONOMY", font="Arial", weight=BOLD, font_size=24).move_to([0, -1.0, 0])
        hidden_code = VGroup(
            Line([-1, -0.5, 0], [1, -0.5, 0]),
            Line([-1, -1.0, 0], [0.5, -1.0, 0]),
            Line([-1, -1.5, 0], [0.8, -1.5, 0])
        ).set_opacity(0.5)
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        
        self.add(hidden_code, label, curtain_l, curtain_r)
        self.play(
            curtain_l.animate.shift(LEFT * 1.5),
            curtain_r.animate.shift(RIGHT * 1.5),
            label.animate.set_opacity(0.2),
            run_time=3.0
        )
        
        # Reveal the "Myth"
        myth_text = Text("HARD-CODED", font="Arial", weight=BOLD, font_size=30).move_to([0, -1.0, 0])
        self.play(Write(myth_text), run_time=2.0)
        self.wait(1.8)

class Scene04_12(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "AGENTIC AUTONOMY MYTH !")
        
        # Visual: A maze with a single pre-defined path
        maze_walls = VGroup(
            Line([-2, 0, 0], [2, 0, 0]),
            Line([-2, -2, 0], [2, -2, 0]),
            Line([-2, 0, 0], [-2, -2, 0]),
            Line([2, 0, 0], [2, -2, 0]),
            Line([-1, 0, 0], [-1, -1.5, 0]),
            Line([1, -2, 0], [1, -0.5, 0])
        ).shift(UP * 0.2)
        
        path = Line([-1.5, -1.7, 0], [1.5, -0.3, 0], stroke_width=8, color="#FFFFFF").set_opacity(0.2)
        robot_dot = Circle(radius=0.15, fill_opacity=1, color="#FFFFFF").move_to([-1.5, -1.7, 0])
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        
        self.play(Create(maze_walls), run_time=1.5)
        self.play(Create(path), run_time=1.0)
        
        # Robot follows the only possible path
        self.play(
            robot_dot.animate.move_to([-1.5, -0.3, 0]),
            run_time=1.0
        )
        self.play(
            robot_dot.animate.move_to([1.5, -0.3, 0]),
            run_time=1.5
        )
        self.play(
            robot_dot.animate.move_to([1.5, -1.7, 0]),
            run_time=1.0
        )
        self.wait(0.8)

class Scene04_13(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "AGENTIC AUTONOMY MYTH !")
        
        # Visual: Gears inside a brain (Mechanical, not autonomous)
        brain_outline = Circle(radius=1.2, stroke_width=3).move_to([0, -1.0, 0])
        gear1 = VGroup(Circle(radius=0.4), *[Line(ORIGIN, UP*0.5).rotate(a*PI/4) for a in range(8)]).move_to([-0.3, -0.8, 0])
        gear2 = VGroup(Circle(radius=0.3), *[Line(ORIGIN, UP*0.4).rotate(a*PI/4) for a in range(8)]).move_to([0.4, -1.2, 0])
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        
        self.play(Create(brain_outline), run_time=1.2)
        self.play(Create(gear1), Create(gear2), run_time=1.2)
        
        # Rotate gears
        self.play(
            Rotate(gear1, angle=2*PI),
            Rotate(gear2, angle=-2*PI),
            run_time=4.0,
            rate_func=linear
        )
        self.wait(0.4)

class Scene04_14(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "AGENTIC AUTONOMY MYTH !")
        
        # Visual: Scale tipping toward "Human Control"
        base = Polygon([-0.5, -2.2, 0], [0.5, -2.2, 0], [0, -1.8, 0], stroke_width=2)
        beam = Line([-2.5, -1.5, 0], [2.5, -2.1, 0], stroke_width=4) # Already tipped
        
        agent_side = VGroup(
            Circle(radius=0.3, stroke_width=2),
            Text("AGENT", font_size=12)
        ).move_to([-2.0, -1.2, 0])
        
        control_side = VGroup(
            Rectangle(width=1.5, height=1.0, stroke_width=2),
            Text("HUMAN\nINPUT", font_size=12)
        ).move_to([2.0, -2.3, 0])
        
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        
        self.play(Create(base), run_time=1.0)
        self.play(Create(beam), run_time=1.0)
        self.play(FadeIn(agent_side), FadeIn(control_side), run_time=1.5)
        
        # Tipping animation
        self.play(
            beam.animate.rotate(0.1, about_point=[0, -1.8, 0]),
            control_side.animate.shift(DOWN * 0.2),
            agent_side.animate.shift(UP * 0.2),
            run_time=2.0,
            rate_func=there_and_back
        )
        self.wait(1.3)

# --- CANVAS CONFIGURATION ---

class Scene04_22(Scene):
    def construct(self):
        # 1. PURE MONOCHROME WHITE-ON-BLACK
        # All elements use #FFFFFF and #000000
        
        # --- FOOTER BAR & META LABELS ---
        footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
        footer_line.set_opacity(0.4)
        
        left_text = Text("AI SYSTEMS", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
        right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
        
        self.add(footer_line, left_text, right_text)

        # --- STRICT BOTTOM TITLE PLACEMENT ---
        title = Text("AGENTIC AUTONOMY MYTH", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time=0.6)

        # --- FIGURATIVE ILLUSTRATION: ROBOT TETHERED TO SERVER ---
        # Safe Area: x in [-3.2, 3.2], y in [-2.5, 0.4]
        
        # Robot Head (The "Agent")
        robot_head = RoundedRectangle(width=1.4, height=1.2, corner_radius=0.15, color="#FFFFFF", stroke_width=3).move_to([-1.6, -0.8, 0])
        eye_l = Circle(radius=0.12, color="#FFFFFF", fill_opacity=1).move_to(robot_head.get_center() + LEFT * 0.35 + UP * 0.15)
        eye_r = Circle(radius=0.12, color="#FFFFFF", fill_opacity=1).move_to(robot_head.get_center() + RIGHT * 0.35 + UP * 0.15)
        mouth = Line(LEFT * 0.3, RIGHT * 0.3, color="#FFFFFF").next_to(eye_l, DOWN, buff=0.3).shift(RIGHT * 0.35)
        antenna = Line(robot_head.get_top(), robot_head.get_top() + UP * 0.3, color="#FFFFFF")
        antenna_tip = Circle(radius=0.05, color="#FFFFFF", fill_opacity=1).move_to(antenna.get_end())
        robot = VGroup(robot_head, eye_l, eye_r, mouth, antenna, antenna_tip)

        # Server (The "Control Source")
        server_box = Rectangle(width=1.2, height=1.6, color="#FFFFFF", stroke_width=3).move_to([1.8, -0.8, 0])
        s_line1 = Line(LEFT * 0.4, RIGHT * 0.4, color="#FFFFFF").move_to(server_box.get_center() + UP * 0.4)
        s_line2 = Line(LEFT * 0.4, RIGHT * 0.4, color="#FFFFFF").move_to(server_box.get_center())
        s_line3 = Line(LEFT * 0.4, RIGHT * 0.4, color="#FFFFFF").move_to(server_box.get_center() + DOWN * 0.4)
        server_lights = VGroup(
            Circle(radius=0.04, color="#FFFFFF", fill_opacity=1).next_to(s_line1, LEFT, buff=0.1),
            Circle(radius=0.04, color="#FFFFFF", fill_opacity=1).next_to(s_line2, LEFT, buff=0.1),
            Circle(radius=0.04, color="#FFFFFF", fill_opacity=1).next_to(s_line3, LEFT, buff=0.1)
        )
        server = VGroup(server_box, s_line1, s_line2, s_line3, server_lights)

        # The Tether (The "Myth" of Autonomy)
        tether = Line(robot_head.get_right(), server_box.get_left(), color="#FFFFFF", stroke_width=6)
        plug_end = Rectangle(width=0.2, height=0.4, color="#FFFFFF", fill_opacity=1).move_to(robot_head.get_right())
        
        # The "MYTH" Label
        myth_box = Rectangle(width=2.2, height=0.8, color="#FFFFFF", stroke_width=4).move_to([0, 0.1, 0])
        myth_text = Text("MYTH", font="Arial", weight=BOLD, font_size=32, color="#FFFFFF").move_to(myth_box.get_center())
        myth_strike = Line(myth_box.get_left() + LEFT*0.2, myth_box.get_right() + RIGHT*0.2, color="#FFFFFF", stroke_width=8).rotate(10*DEGREES)
        myth_group = VGroup(myth_box, myth_text, myth_strike)

        # --- ANIMATION SEQUENCE (Total 7.4s) ---
        # 0.6s already used for title
        
        # 1. Draw Robot and Server (0.6 - 2.0s)
        self.play(
            Create(robot),
            FadeIn(server, shift=LEFT),
            run_time=1.4,
            rate_func=smooth
        )

        # 2. Connect the tether (2.0 - 3.5s)
        self.play(
            Create(tether),
            FadeIn(plug_end),
            robot.animate.shift(LEFT * 0.2),
            run_time=1.5,
            rate_func=ease_out_expo
        )

        # 3. Reveal the "MYTH" label (3.5 - 5.0s)
        self.play(
            GrowFromCenter(myth_group),
            Flash(myth_box, color="#FFFFFF", line_length=0.3, num_lines=12),
            run_time=1.5
        )

        # 4. Final emphasis and hold (5.0 - 7.4s)
        # Subtle pulsing of the tether to show data flow/dependence
        self.play(
            tether.animate.set_stroke(width=10),
            server_lights.animate.set_opacity(0.2),
            run_time=0.6
        )
        self.play(
            tether.animate.set_stroke(width=6),
            server_lights.animate.set_opacity(1.0),
            run_time=0.6
        )
        self.wait(1.2)

# --- END OF SCENE ---