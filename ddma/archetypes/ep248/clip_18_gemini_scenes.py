import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Global configuration enforcing 740x740 pure monochrome white-on-black canvas

def setup_base_scene(*args, **kwargs):
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

    """Applies the strict mandatory bottom title, footer, meta labels, and safe area bounds."""
    # Strict Bottom Title Placement (y = -2.95)
    title = Text("Discussion on No Matter How Autonomous Its Code is", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

class Scene18_01(Scene):
    def construct(self):
        setup_base_scene(self, "AUTONOMY & CODE")
        
        # Literal figurative visual: A central robotic core with autonomous gears and data streaming
        robot_head = RoundedRectangle(corner_radius=0.3, width=2.6, height=2.2, stroke_width=2.5, color="#FFFFFF")
        robot_head.move_to([0, -1.0, 0])
        
        # Eyes (glowing white rectangles)
        eye_left = Rectangle(width=0.5, height=0.3, stroke_width=2, color="#FFFFFF").move_to([-0.6, -0.6, 0])
        eye_right = Rectangle(width=0.5, height=0.3, stroke_width=2, color="#FFFFFF").move_to([0.6, -0.6, 0])
        
        # Antenna
        antenna_stem = Line([0, 0.1, 0], [0, 1.0, 0], stroke_width=2.5, color="#FFFFFF")
        antenna_bulb = Circle(radius=0.15, stroke_width=2.5, color="#FFFFFF").move_to([0, 1.15, 0])
        
        # Code brackets representing autonomy
        code_left = Text("{", font="Arial", weight=BOLD, font_size=48, color="#FFFFFF").move_to([-2.2, -1.0, 0])
        code_right = Text("}", font="Arial", weight=BOLD, font_size=48, color="#FFFFFF").move_to([2.2, -1.0, 0])
        
        robot_group = VGroup(robot_head, eye_left, eye_right, antenna_stem, antenna_bulb, code_left, code_right)
        
        self.play(DrawBorderThenFill(robot_group), run_time=3.5)
        self.play(robot_group.animate.scale(1.05), run_time=1.5)
        self.play(robot_group.animate.scale(0.95), run_time=1.4)
        self.wait(1.0)

class Scene18_02(Scene):
    def construct(self):
        setup_base_scene(self, "AUTONOMOUS CORE")
        
        # Literal figurative visual: Nested rotating gears inside a mainframe
        outer_gear = Circle(radius=1.5, stroke_width=2.5, color="#FFFFFF").move_to([0, -1.0, 0])
        inner_gear = Circle(radius=0.8, stroke_width=2.5, color="#FFFFFF").move_to([0, -1.0, 0])
        
        # Spokes for gears
        spoke1 = Line([0, -2.5, 0], [0, 0.5, 0], stroke_width=2, color="#FFFFFF").move_to([0, -1.0, 0])
        spoke2 = Line([-1.5, -1.0, 0], [1.5, -1.0, 0], stroke_width=2, color="#FFFFFF").move_to([0, -1.0, 0])
        
        core_system = VGroup(outer_gear, inner_gear, spoke1, spoke2)
        
        # Pulse waves outward
        wave1 = Circle(radius=1.8, stroke_width=1.5, color="#FFFFFF").set_opacity(0.6).move_to([0, -1.0, 0])
        wave2 = Circle(radius=2.2, stroke_width=1.0, color="#FFFFFF").set_opacity(0.3).move_to([0, -1.0, 0])
        
        self.play(Create(core_system), run_time=3.0)
        self.play(FadeIn(wave1), FadeIn(wave2), run_time=2.0)
        self.play(core_system.animate.rotate(0.5), run_time=1.4)
        self.wait(1.0)

class Scene18_03(Scene):
    def construct(self):
        setup_base_scene(self, "CODE EXECUTION")
        
        # Literal figurative visual: Terminal screen executing code lines
        screen = RoundedRectangle(corner_radius=0.2, width=5.0, height=2.8, stroke_width=2.5, color="#FFFFFF")
        screen.move_to([0, -1.0, 0])
        
        line1 = Line([-2.0, -0.2, 0], [-0.5, -0.2, 0], stroke_width=3, color="#FFFFFF")
        line2 = Line([-2.0, -0.8, 0], [1.2, -0.8, 0], stroke_width=3, color="#FFFFFF")
        line3 = Line([-2.0, -1.4, 0], [0.3, -1.4, 0], stroke_width=3, color="#FFFFFF")
        line4 = Line([-2.0, -2.0, 0], [-1.0, -2.0, 0], stroke_width=3, color="#FFFFFF")
        
        terminal_group = VGroup(screen, line1, line2, line3, line4)
        
        self.play(Create(screen), run_time=2.0)
        self.play(Create(line1), Create(line2), run_time=2.0)
        self.play(Create(line3), Create(line4), run_time=2.0)
        self.wait(1.4)

class Scene18_04(Scene):
    def construct(self):
        setup_base_scene(self, "SYSTEM INDEPENDENCE")
        
        # Literal figurative visual: A server tower splitting/standing completely unbound
        server1 = RoundedRectangle(corner_radius=0.1, width=1.4, height=2.6, stroke_width=2.5, color="#FFFFFF").move_to([-1.5, -1.0, 0])
        server2 = RoundedRectangle(corner_radius=0.1, width=1.4, height=2.6, stroke_width=2.5, color="#FFFFFF").move_to([1.5, -1.0, 0])
        
        # Lightning / data bridge disconnecting in the middle
        bridge1 = Line([-0.8, -0.3, 0], [-0.2, -0.3, 0], stroke_width=2.5, color="#FFFFFF")
        bridge2 = Line([0.2, -0.3, 0], [0.8, -0.3, 0], stroke_width=2.5, color="#FFFFFF")
        
        arrow_left = Arrow([-0.8, -1.0, 0], [-1.8, -1.0, 0], stroke_width=2.5, color="#FFFFFF", buff=0)
        arrow_right = Arrow([0.8, -1.0, 0], [1.8, -1.0, 0], stroke_width=2.5, color="#FFFFFF", buff=0)
        
        unbound_group = VGroup(server1, server2, bridge1, bridge2, arrow_left, arrow_right)
        
        self.play(Create(server1), Create(server2), run_time=3.0)
        self.play(Create(bridge1), Create(bridge2), run_time=2.0)
        self.play(GrowArrow(arrow_left), GrowArrow(arrow_right), run_time=1.4)
        self.wait(1.0)

class Scene18_05(Scene):
    def construct(self):
        setup_base_scene(self, "DECISION MATRIX")
        
        # Literal figurative visual: A flow chart / decision tree of autonomous logic paths
        box_top = RoundedRectangle(corner_radius=0.15, width=2.0, height=0.8, stroke_width=2.5, color="#FFFFFF").move_to([0, 0.0, 0])
        box_left = RoundedRectangle(corner_radius=0.15, width=1.8, height=0.8, stroke_width=2.5, color="#FFFFFF").move_to([-1.8, -1.8, 0])
        box_right = RoundedRectangle(corner_radius=0.15, width=1.8, height=0.8, stroke_width=2.5, color="#FFFFFF").move_to([1.8, -1.8, 0])
        
        arrow_l = Arrow([box_top.get_center(), box_left.get_center()], stroke_width=2.0, color="#FFFFFF", buff=0.2)
        arrow_r = Arrow([box_top.get_center(), box_right.get_center()], stroke_width=2.0, color="#FFFFFF", buff=0.2)
        
        decision_tree = VGroup(box_top, box_left, box_right, arrow_l, arrow_r)
        
        self.play(Create(box_top), run_time=2.0)
        self.play(GrowArrow(arrow_l), GrowArrow(arrow_r), run_time=2.0)
        self.play(Create(box_left), Create(box_right), run_time=2.4)
        self.wait(1.0)

class Scene18_06(Scene):
    def construct(self):
        setup_base_scene(self, "AUTONOMOUS FEEDBACK")
        
        # Literal figurative visual: Infinite circular feedback loop of code
        loop_arc1 = Arc(radius=1.2, start_angle=0, angle=PI, stroke_width=3, color="#FFFFFF").move_to([0, -1.0, 0])
        loop_arc2 = Arc(radius=1.2, start_angle=PI, angle=PI, stroke_width=3, color="#FFFFFF").move_to([0, -1.0, 0])
        
        arrow1 = Arrow([1.2, -1.0, 0], [1.3, -0.8, 0], stroke_width=2, color="#FFFFFF", buff=0)
        arrow2 = Arrow([-1.2, -1.0, 0], [-1.3, -1.2, 0], stroke_width=2, color="#FFFFFF", buff=0)
        
        core_dot = Circle(radius=0.3, stroke_width=2.5, color="#FFFFFF").move_to([0, -1.0, 0])
        
        feedback_group = VGroup(loop_arc1, loop_arc2, arrow1, arrow2, core_dot)
        
        self.play(Create(loop_arc1), Create(loop_arc2), run_time=3.0)
        self.play(GrowArrow(arrow1), GrowArrow(arrow2), Create(core_dot), run_time=3.0)
        self.wait(1.4)

class Scene18_07(Scene):
    def construct(self):
        setup_base_scene(self, "ENDLESS AUTONOMY")
        
        # Literal figurative visual: Infinity symbol made of solid neon white code trails
        inf_left = Circle(radius=0.9, stroke_width=3, color="#FFFFFF").move_to([-1.0, -1.0, 0])
        inf_right = Circle(radius=0.9, stroke_width=3, color="#FFFFFF").move_to([1.0, -1.0, 0])
        
        center_pulse = Circle(radius=0.3, stroke_width=2, color="#FFFFFF").move_to([0, -1.0, 0])
        
        infinity_group = VGroup(inf_left, inf_right, center_pulse)
        
        self.play(Create(inf_left), Create(inf_right), run_time=3.5)
        self.play(GrowFromCenter(center_pulse), run_time=2.0)
        self.play(infinity_group.animate.scale(1.08), run_time=0.9)
        self.play(infinity_group.animate.scale(0.92), run_time=1.0)
        self.wait(1.0)

# Global configuration for monochrome aesthetic and tight framing

def setup_scene(scene, category_text="AUTONOMOUS CODE"):
    # Footer and Metadata
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)
    
    # Bottom Title Placement (Invariant: never at top, keeping upper canvas clear)
    title = Text("NO MATTER HOW AUTONOMOUS ITS CODE IS", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)

class Scene18_08(Scene):
    def construct(self):
        setup_scene(self, "CODE INDEPENDENCE")
        
        # Literal figurative visual: A central server/processor unit with independent glowing code streams radiating out
        server = RoundedRectangle(corner_radius=0.2, width=2.0, height=2.6, stroke_width=2, color="#FFFFFF", fill_opacity=0.15).move_to([0, -1.0, 0])
        screen = RoundedRectangle(corner_radius=0.1, width=1.4, height=1.0, stroke_width=1.5, color="#FFFFFF", fill_opacity=0.3).move_to([0, -0.6, 0])
        
        # Code lines inside screen
        c1 = Line(LEFT*0.5, RIGHT*0.2, color="#FFFFFF", stroke_width=2).move_to([0, -0.4, 0])
        c2 = Line(LEFT*0.5, RIGHT*0.5, color="#FFFFFF", stroke_width=2).move_to([0, -0.7, 0])
        c3 = Line(LEFT*0.5, RIGHT*0.1, color="#FFFFFF", stroke_width=2).move_to([0, -1.0, 0])
        
        code_group = VGroup(server, screen, c1, c2, c3)
        
        # Autonomous radiating paths (independent floating brackets)
        b1 = Text("{ }", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to([-2.2, 0.5, 0])
        b2 = Text("[ ]", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to([2.2, 0.5, 0])
        b3 = Text("< / >", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, 1.2, 0])
        
        arrows = VGroup(
            Arrow(server.get_top(), b3.get_bottom(), buff=0.1, stroke_width=2, color="#FFFFFF"),
            Arrow(server.get_left(), b1.get_right(), buff=0.1, stroke_width=2, color="#FFFFFF"),
            Arrow(server.get_right(), b2.get_left(), buff=0.1, stroke_width=2, color="#FFFFFF")
        )
        
        self.play(FadeIn(code_group), run_time=1.5)
        self.play(GrowArrow(arrows[0]), FadeIn(b3), run_time=1.5)
        self.play(GrowArrow(arrows[1]), GrowArrow(arrows[2]), FadeIn(b1), FadeIn(b2), run_time=2.0)
        self.wait(1.8)

class Scene18_09(Scene):
    def construct(self):
        setup_scene(self, "SYSTEM BOUNDARIES")
        
        # Literal figurative visual: A locked vault/boundary box containing autonomous logic chips
        box = RoundedRectangle(corner_radius=0.3, width=4.5, height=2.8, stroke_width=2.5, color="#FFFFFF", fill_opacity=0.1).move_to([0, -0.8, 0])
        
        # Internal chips
        chip1 = Rectangle(width=1.0, height=1.0, stroke_width=2, color="#FFFFFF", fill_opacity=0.3).move_to([-1.2, -0.8, 0])
        chip2 = Rectangle(width=1.0, height=1.0, stroke_width=2, color="#FFFFFF", fill_opacity=0.3).move_to([1.2, -0.8, 0])
        
        # Connecting bus line
        bus = Line(chip1.get_right(), chip2.get_left(), stroke_width=3, color="#FFFFFF")
        
        # Outer barrier pulse waves
        wave1 = RoundedRectangle(corner_radius=0.4, width=5.1, height=3.4, stroke_width=1.5, color="#FFFFFF", fill_opacity=0).move_to([0, -0.8, 0]).set_opacity(0.5)
        wave2 = RoundedRectangle(corner_radius=0.5, width=5.7, height=4.0, stroke_width=1.0, color="#FFFFFF", fill_opacity=0).move_to([0, -0.8, 0]).set_opacity(0.2)
        
        self.play(Create(box), run_time=1.5)
        self.play(FadeIn(chip1), FadeIn(chip2), Create(bus), run_time=1.5)
        self.play(Create(wave1), Create(wave2), run_time=2.0)
        self.wait(1.8)

class Scene18_10(Scene):
    def construct(self):
        setup_scene(self, "SELF EXECUTION")
        
        # Literal figurative visual: A giant robotic gear mechanism turning independently
        outer_ring = Circle(radius=1.5, stroke_width=3, color="#FFFFFF", fill_opacity=0.1).move_to([0, -0.8, 0])
        inner_core = Circle(radius=0.5, stroke_width=2, color="#FFFFFF", fill_opacity=0.4).move_to([0, -0.8, 0])
        
        # Gear teeth representation using lines
        teeth = VGroup()
        for i in range(8):
            angle = i * PI / 4
            p1 = np.array([0, -0.8, 0]) + np.array([1.3 * np.cos(angle), 1.3 * np.sin(angle), 0])
            p2 = np.array([0, -0.8, 0]) + np.array([1.7 * np.cos(angle), 1.7 * np.sin(angle), 0])
            teeth.add(Line(p1, p2, stroke_width=4, color="#FFFFFF"))
            
        gear = VGroup(outer_ring, inner_core, teeth)
        
        # Play button icon floating in center
        play_poly = Polygon([-0.2, -0.5, 0], [-0.2, -1.1, 0], [0.3, -0.8, 0], stroke_width=2, color="#FFFFFF", fill_opacity=0.8)
        
        self.play(FadeIn(gear), run_time=2.0)
        self.play(Rotate(gear, angle=PI/4, about_point=[0, -0.8, 0]), run_time=2.0)
        self.play(FadeIn(play_poly), run_time=1.0)
        self.wait(1.8)

class Scene18_11(Scene):
    def construct(self):
        setup_scene(self, "LOGIC GATES")
        
        # Literal figurative visual: Connected logic gates processing data flow automatically
        gate_body = Polygon([-1.0, 0.0, 0], [-1.0, -1.6, 0], [0.0, -1.6, 0], [1.0, -0.8, 0], [0.0, 0.0, 0], stroke_width=2.5, color="#FFFFFF", fill_opacity=0.2).move_to([0, -0.8, 0])
        
        # Input lines
        in1 = Line([-2.5, -0.4, 0], [-1.0, -0.4, 0], stroke_width=2, color="#FFFFFF")
        in2 = Line([-2.5, -1.2, 0], [-1.0, -1.2, 0], stroke_width=2, color="#FFFFFF")
        
        # Output line
        out = Line([0.6, -0.8, 0], [2.5, -0.8, 0], stroke_width=2, color="#FFFFFF")
        
        # Binary text indicators
        b_in1 = Text("1", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([-2.7, -0.4, 0])
        b_in2 = Text("0", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([-2.7, -1.2, 0])
        b_out = Text("1", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([2.7, -0.8, 0])
        
        circuit_group = VGroup(gate_body, in1, in2, out, b_in1, b_in2, b_out)
        
        self.play(Create(in1), Create(in2), FadeIn(b_in1), FadeIn(b_in2), run_time=1.5)
        self.play(Create(gate_body), run_time=2.0)
        self.play(Create(out), FadeIn(b_out), run_time=1.5)
        self.wait(1.8)

class Scene18_12(Scene):
    def construct(self):
        setup_scene(self, "DECISION MATRIX")
        
        # Literal figurative visual: A branching flowchart representing autonomous decisions
        node_top = RoundedRectangle(corner_radius=0.15, width=1.8, height=0.7, stroke_width=2, color="#FFFFFF", fill_opacity=0.2).move_to([0, 0.2, 0])
        text_top = Text("INPUT", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, 0.2, 0])
        
        node_left = RoundedRectangle(corner_radius=0.15, width=1.8, height=0.7, stroke_width=2, color="#FFFFFF", fill_opacity=0.2).move_to([-1.8, -1.2, 0])
        text_l = Text("PATH A", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([-1.8, -1.2, 0])
        
        node_right = RoundedRectangle(corner_radius=0.15, width=1.8, height=0.7, stroke_width=2, color="#FFFFFF", fill_opacity=0.2).move_to([1.8, -1.2, 0])
        text_r = Text("PATH B", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([1.8, -1.2, 0])
        
        arrow_l = Arrow(node_top.get_bottom(), node_left.get_top(), buff=0.1, stroke_width=2, color="#FFFFFF")
        arrow_r = Arrow(node_top.get_bottom(), node_right.get_top(), buff=0.1, stroke_width=2, color="#FFFFFF")
        
        flowchart = VGroup(node_top, text_top, node_left, text_l, node_right, text_r, arrow_l, arrow_r)
        
        self.play(FadeIn(node_top), FadeIn(text_top), run_time=1.5)
        self.play(GrowArrow(arrow_l), GrowArrow(arrow_r), run_time=1.5)
        self.play(FadeIn(node_left), FadeIn(text_l), FadeIn(node_right), FadeIn(text_r), run_time=2.0)
        self.wait(1.8)

class Scene18_13(Scene):
    def construct(self):
        setup_scene(self, "INFINITE LOOPS")
        
        # Literal figurative visual: A continuous circular looping arrow representing perpetual code execution
        loop_arc_1 = Arc(radius=1.2, start_angle=0, angle=PI*1.5, stroke_width=4, color="#FFFFFF").move_to([0, -0.8, 0])
        loop_arc_2 = Arc(radius=1.2, start_angle=PI*1.5, angle=PI*0.5, stroke_width=4, color="#FFFFFF").move_to([0, -0.8, 0])
        
        arrow_head = Arrow(start=[0, 0.4, 0], end=[0.4, 0.4, 0], stroke_width=3, color="#FFFFFF").move_to([1.2, -0.8, 0])
        
        center_text = Text("WHILE(TRUE)", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, -0.8, 0])
        
        loop_group = VGroup(loop_arc_1, loop_arc_2, arrow_head, center_text)
        
        self.play(Create(loop_arc_1), run_time=2.0)
        self.play(Create(loop_arc_2), GrowArrow(arrow_head), run_time=2.0)
        self.play(FadeIn(center_text), run_time=1.0)
        self.wait(1.8)

class Scene18_14(Scene):
    def construct(self):
        setup_scene(self, "CORE ARCHITECTURE")
        
        # Literal figurative visual: Multi-layered core infrastructure stack representing deep code foundation
        layer1 = RoundedRectangle(corner_radius=0.2, width=5.0, height=0.8, stroke_width=2, color="#FFFFFF", fill_opacity=0.1).move_to([0, 0.0, 0])
        t1 = Text("APPLICATION LAYER", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, 0.0, 0])
        
        layer2 = RoundedRectangle(corner_radius=0.2, width=4.0, height=0.8, stroke_width=2, color="#FFFFFF", fill_opacity=0.3).move_to([0, -0.9, 0])
        t2 = Text("LOGIC ENGINE", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, -0.9, 0])
        
        layer3 = RoundedRectangle(corner_radius=0.2, width=3.0, height=0.8, stroke_width=2, color="#FFFFFF", fill_opacity=0.5).move_to([0, -1.8, 0])
        t3 = Text("CORE KERNEL", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, -1.8, 0])
        
        stack = VGroup(layer1, t1, layer2, t2, layer3, t3)
        
        self.play(FadeIn(layer3), FadeIn(t3), run_time=1.5)
        self.play(FadeIn(layer2), FadeIn(t2), run_time=1.5)
        self.play(FadeIn(layer1), FadeIn(t1), run_time=2.0)
        self.wait(1.8)

# Global configuration requirements

def add_standard_elements(scene, category_text):
    """Adds the mandatory title, footer line, and footer meta labels following strict rules."""
    title = Text("NO MATTER HOW AUTONOMOUS ITS CODE IS", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.4)
    
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

class Scene18_15(Scene):
    def construct(self):
        add_standard_elements(self, "AUTONOMY & CODE")
        
        # Literal figurative visual: A central robot head with code matrix background
        robot_head = RoundedRectangle(corner_radius=0.3, width=2.2, height=2.2, stroke_color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([0, -1.0, 0])
        eye_left = Circle(radius=0.2, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.8).move_to([-0.5, -0.6, 0])
        eye_right = Circle(radius=0.2, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.8).move_to([0.5, -0.6, 0])
        antenna_line = Line([0, 1.1, 0], [0, 1.8, 0], color="#FFFFFF", stroke_width=2.5)
        antenna_dot = Circle(radius=0.15, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=1).move_to([0, 1.95, 0])
        
        # Code snippets floating around
        code1 = Text("{ }", font="Arial", weight=BOLD, font_size=18, color="#FFFFFF").set_opacity(0.7).move_to([-2.0, 0.2, 0])
        code2 = Text("while(true):", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").set_opacity(0.7).move_to([2.0, -0.2, 0])
        code3 = Text("auto_exec()", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").set_opacity(0.7).move_to([1.8, -1.8, 0])
        
        robot_group = VGroup(robot_head, eye_left, eye_right, antenna_line, antenna_dot, code1, code2, code3)
        
        self.play(FadeIn(robot_group, shift=UP*0.3), run_time=1.5)
        self.play(robot_head.animate.set_fill(opacity=0.3), run_time=2.0)
        self.wait(3.5)

class Scene18_16(Scene):
    def construct(self):
        add_standard_elements(self, "AUTONOMY & CODE")
        
        # Literal figurative visual: A server rack with flashing data streams representing complex code execution
        rack = RoundedRectangle(corner_radius=0.1, width=2.6, height=3.4, stroke_color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.1).move_to([0, -1.0, 0])
        
        slot1 = Line([-1.1, 0.2, 0], [1.1, 0.2, 0], color="#FFFFFF", stroke_width=2)
        slot2 = Line([-1.1, -0.6, 0], [1.1, -0.6, 0], color="#FFFFFF", stroke_width=2)
        slot3 = Line([-1.1, -1.4, 0], [1.1, -1.4, 0], color="#FFFFFF", stroke_width=2)
        
        led1 = Circle(radius=0.08, color="#FFFFFF", stroke_width=1, fill_color="#FFFFFF", fill_opacity=1).move_to([0.8, 0.5, 0])
        led2 = Circle(radius=0.08, color="#FFFFFF", stroke_width=1, fill_color="#FFFFFF", fill_opacity=0.4).move_to([0.5, 0.5, 0])
        led3 = Circle(radius=0.08, color="#FFFFFF", stroke_width=1, fill_color="#FFFFFF", fill_opacity=1).move_to([0.8, -0.2, 0])
        
        stream = VGroup(
            Arrow(UP*1.8 + LEFT*2.2, UP*0.5 + LEFT*0.5, color="#FFFFFF", stroke_width=2, tip_length=0.15),
            Arrow(UP*1.8 + RIGHT*2.2, UP*0.5 + RIGHT*0.5, color="#FFFFFF", stroke_width=2, tip_length=0.15)
        )
        
        server_group = VGroup(rack, slot1, slot2, slot3, led1, led2, led3, stream)
        
        self.play(Create(server_group), run_time=2.0)
        self.play(led2.animate.set_opacity(1.0), led1.animate.set_opacity(0.3), run_time=2.0)
        self.wait(3.4)

class Scene18_17(Scene):
    def construct(self):
        add_standard_elements(self, "AUTONOMY & CODE")
        
        # Literal figurative visual: A large balance scale measuring code vs autonomy rules
        beam = Line([-2.2, 0, 0], [2.2, 0, 0], color="#FFFFFF", stroke_width=3).move_to([0, -0.5, 0])
        fulcrum = Polygon([0, -0.5, 0], [-0.5, -1.8, 0], [0.5, -1.8, 0], color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.2).move_to([0, -1.15, 0])
        
        pan_left = VGroup(
            Line([-2.2, 0, 0], [-2.7, -1.2, 0], color="#FFFFFF", stroke_width=2),
            Line([-2.2, 0, 0], [-1.7, -1.2, 0], color="#FFFFFF", stroke_width=2),
            Arc(radius=1.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2).move_to([-2.2, -1.2, 0])
        ).shift(UP*0.5)
        
        pan_right = VGroup(
            Line([2.2, 0, 0], [1.7, -0.8, 0], color="#FFFFFF", stroke_width=2),
            Line([2.2, 0, 0], [2.7, -0.8, 0], color="#FFFFFF", stroke_width=2),
            Arc(radius=1.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2).move_to([2.2, -0.8, 0])
        ).shift(UP*0.5)
        
        scale_group = VGroup(beam, fulcrum, pan_left, pan_right).move_to([0, -0.8, 0])
        
        code_label = Text("CODE", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([-2.2, -0.7, 0])
        auto_label = Text("AUTO", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([2.2, -0.3, 0])
        
        self.play(FadeIn(scale_group, shift=UP*0.2), FadeIn(code_label), FadeIn(auto_label), run_time=2.0)
        self.play(beam.animate.rotate(0.15, about_point=fulcrum.get_top()), run_time=1.5)
        self.play(beam.animate.rotate(-0.3, about_point=fulcrum.get_top()), run_time=1.5)
        self.wait(2.4)

class Scene18_18(Scene):
    def construct(self):
        add_standard_elements(self, "AUTONOMY & CODE")
        
        # Literal figurative visual: Interlocking gears representing autonomous background mechanics
        gear1 = Circle(radius=1.2, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.1).move_to([-1.0, -0.8, 0])
        gear2 = Circle(radius=0.9, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.1).move_to([1.2, -0.3, 0])
        
        center1 = Circle(radius=0.3, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.4).move_to([-1.0, -0.8, 0])
        center2 = Circle(radius=0.25, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.4).move_to([1.2, -0.3, 0])
        
        spoke1_1 = Line([-1.0, -2.0, 0], [-1.0, 0.4, 0], color="#FFFFFF", stroke_width=2)
        spoke1_2 = Line([-2.2, -0.8, 0], [0.2, -0.8, 0], color="#FFFFFF", stroke_width=2)
        
        spoke2_1 = Line([1.2, -1.2, 0], [1.2, 0.6, 0], color="#FFFFFF", stroke_width=2)
        spoke2_2 = Line([0.3, -0.3, 0], [2.1, -0.3, 0], color="#FFFFFF", stroke_width=2)
        
        gears = VGroup(gear1, gear2, center1, center2, spoke1_1, spoke1_2, spoke2_1, spoke2_2)
        
        self.play(Create(gears), run_time=2.0)
        self.play(Rotate(gear1, angle=PI/2, about_point=[-1.0, -0.8, 0]),
                  Rotate(gear2, angle=-PI/2, about_point=[1.2, -0.3, 0]), run_time=3.0, rate_func=linear)
        self.wait(2.4)

class Scene18_19(Scene):
    def construct(self):
        add_standard_elements(self, "AUTONOMY & CODE")
        
        # Literal figurative visual: A bold structural wall/shield blocking/filtering raw code streams
        shield = RoundedRectangle(corner_radius=0.4, width=3.0, height=3.2, stroke_color="#FFFFFF", stroke_width=3.5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([0, -1.0, 0])
        
        inner_lines = VGroup(
            Line([-1.0, 0.1, 0], [1.0, 0.1, 0], color="#FFFFFF", stroke_width=2),
            Line([-1.0, -0.5, 0], [1.0, -0.5, 0], color="#FFFFFF", stroke_width=2),
            Line([-1.0, -1.1, 0], [1.0, -1.1, 0], color="#FFFFFF", stroke_width=2),
            Line([-1.0, -1.7, 0], [1.0, -1.7, 0], color="#FFFFFF", stroke_width=2)
        )
        
        check = VGroup(
            Line([-0.4, -1.0, 0], [-0.1, -1.5, 0], color="#FFFFFF", stroke_width=4),
            Line([-0.1, -1.5, 0], [0.6, -0.4, 0], color="#FFFFFF", stroke_width=4)
        ).move_to([0, -0.9, 0])
        
        shield_group = VGroup(shield, inner_lines, check)
        
        self.play(DrawBorderThenFill(shield), run_time=1.5)
        self.play(Create(inner_lines), run_time=1.5)
        self.play(FadeIn(check, scale=0.5), run_time=1.5)
        self.wait(2.9)