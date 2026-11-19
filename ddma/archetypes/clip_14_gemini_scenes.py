import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)




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

    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene14_01(Scene):
    def construct(self):
        setup_base_scene(self, "AND THE NETWORK GENERATES THIS UNIQUE", "NETWORK GENERATION")
        
        # Literal illustration: A central neural network node radiating unique output streams
        center_node = Circle(radius=0.6, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.2).move_to([0, -1.0, 0])
        core_dot = Dot(point=[0, -1.0, 0], color="#FFFFFF", radius=0.15)
        
        rays = VGroup()
        for angle in range(0, 360, 45):
            rad = angle * DEGREES
            start_pt = np.array([np.cos(rad) * 0.7, -1.0 + np.sin(rad) * 0.7, 0])
            end_pt = np.array([np.cos(rad) * 2.5, -1.0 + np.sin(rad) * 2.5, 0])
            rays.add(Line(start_pt, end_pt, color="#FFFFFF", stroke_width=2).set_opacity(0.7))
            rays.add(Dot(point=end_pt, color="#FFFFFF", radius=0.08))
            
        self.play(FadeIn(center_node), FadeIn(core_dot), run_time=1.0)
        self.play(Create(rays), run_time=3.5)
        self.wait(3.0)

class Scene14_02(Scene):
    def construct(self):
        setup_base_scene(self, "AND THE NETWORK GENERATES THIS UNIQUE", "UNIQUE PATTERNS")
        
        # Literal illustration: A complex interconnected web of nodes generating a distinct star shape
        nodes = VGroup()
        coords = [
            [0, 0.5, 0], [-1.5, -0.5, 0], [1.5, -0.5, 0],
            [-0.8, -2.0, 0], [0.8, -2.0, 0], [0, -1.2, 0]
        ]
        
        dot_group = VGroup()
        for c in coords:
            dot_group.add(Circle(radius=0.2, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.4).move_to(c))
            
        lines = VGroup(
            Line(coords[0], coords[1], color="#FFFFFF", stroke_width=2),
            Line(coords[0], coords[2], color="#FFFFFF", stroke_width=2),
            Line(coords[1], coords[5], color="#FFFFFF", stroke_width=2),
            Line(coords[2], coords[5], color="#FFFFFF", stroke_width=2),
            Line(coords[5], coords[3], color="#FFFFFF", stroke_width=2),
            Line(coords[5], coords[4], color="#FFFFFF", stroke_width=2),
            Line(coords[1], coords[3], color="#FFFFFF", stroke_width=2),
            Line(coords[2], coords[4], color="#FFFFFF", stroke_width=2),
        )
        
        self.play(Create(lines), run_time=3.0)
        self.play(FadeIn(dot_group, scale=0.5), run_time=2.5)
        self.wait(2.0)

class Scene14_03(Scene):
    def construct(self):
        setup_base_scene(self, "AND THE NETWORK GENERATES THIS UNIQUE", "DATA SYNTHESIS")
        
        # Literal illustration: Converging data streams into a central processing box
        box = Rectangle(width=2.5, height=2.0, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.1).move_to([0, -1.0, 0])
        
        in_arrows = VGroup(
            Arrow(start=[-3.0, 0.2, 0], end=[-1.25, -0.5, 0], color="#FFFFFF", stroke_width=2, buff=0),
            Arrow(start=[-3.0, -1.0, 0], end=[-1.25, -1.0, 0], color="#FFFFFF", stroke_width=2, buff=0),
            Arrow(start=[-3.0, -2.2, 0], end=[-1.25, -1.5, 0], color="#FFFFFF", stroke_width=2, buff=0),
        )
        
        out_arrow = Arrow(start=[1.25, -1.0, 0], end=[3.0, -1.0, 0], color="#FFFFFF", stroke_width=4, buff=0)
        
        gear = Circle(radius=0.5, color="#FFFFFF", stroke_width=2).move_to([0, -1.0, 0])
        
        self.play(Create(in_arrows), run_time=2.0)
        self.play(Create(box), FadeIn(gear), run_time=2.0)
        self.play(GrowArrow(out_arrow), run_time=1.5)
        self.wait(2.0)

class Scene14_04(Scene):
    def construct(self):
        setup_base_scene(self, "AND THE NETWORK GENERATES THIS UNIQUE", "FINGERPRINT OUTPUT")
        
        # Literal illustration: A stylized biometric fingerprint made of concentric arcs
        center_pt = np.array([0, -1.0, 0])
        arcs = VGroup()
        for r in np.linspace(0.4, 1.8, 6):
            arcs.add(Arc(radius=r, start_angle=0, angle=PI*1.5, color="#FFFFFF", stroke_width=3).move_to(center_pt))
            
        scanner_bar = Line(start=[-2.5, 0.5, 0], end=[2.5, 0.5, 0], color="#FFFFFF", stroke_width=4).set_opacity(0.8)
        
        self.play(FadeIn(scanner_bar), run_time=1.0)
        self.play(Create(arcs), run_time=4.0)
        self.play(scanner_bar.animate.shift(DOWN * 3.0), run_time=1.5)
        self.wait(1.0)

class Scene14_05(Scene):
    def construct(self):
        setup_base_scene(self, "AND THE NETWORK GENERATES THIS UNIQUE", "CODE GENERATION")
        
        # Literal illustration: Terminal screen output brackets with dynamic binary streams
        frame = RoundedRectangle(corner_radius=0.2, width=6.0, height=3.0, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.05).move_to([0, -1.0, 0])
        
        code_lines = VGroup(
            Text("> INIT_GENERATE_SEQUENCE()", font="Arial", font_size=14, color="#FFFFFF").move_to([-0.5, -0.2, 0]),
            Text("> PARSING_WEIGHTS... [OK]", font="Arial", font_size=14, color="#FFFFFF").move_to([-0.4, -0.9, 0]),
            Text("> OUTPUT: UNIQUE_ID_#8942", font="Arial", font_size=14, color="#FFFFFF").move_to([-0.3, -1.6, 0]),
        )
        
        cursor = Rectangle(width=0.12, height=0.2, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([1.8, -1.6, 0])
        
        self.play(Create(frame), run_time=1.5)
        self.play(FadeIn(code_lines[0]), run_time=1.0)
        self.play(FadeIn(code_lines[1]), run_time=1.0)
        self.play(FadeIn(code_lines[2]), FadeIn(cursor), run_time=1.0)
        self.wait(3.0)

class Scene14_06(Scene):
    def construct(self):
        setup_base_scene(self, "AND THE NETWORK GENERATES THIS UNIQUE", "DISTINCT ENTITY")
        
        # Literal illustration: A central highlighted diamond object standing out among standard blocks
        grid = VGroup()
        for x in [-2.0, 0.0, 2.0]:
            for y in [0.0, -1.0, -2.0]:
                if x == 0.0 and y == -1.0:
                    continue
                grid.add(Square(side_length=0.8, color="#FFFFFF", stroke_width=1.5).set_opacity(0.3).move_to([x, y, 0]))
                
        special_diamond = Polygon([-0.7, -1.0, 0], [0, -0.3, 0], [0.7, -1.0, 0], [0, -1.7, 0], color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.5)
        
        pulse_ring = Circle(radius=0.8, color="#FFFFFF", stroke_width=2).move_to([0, -1.0, 0])
        
        self.play(FadeIn(grid), run_time=2.0)
        self.play(GrowFromCenter(special_diamond), run_time=1.5)
        self.play(Create(pulse_ring), pulse_ring.animate.scale(1.5).set_opacity(0), run_time=2.0)
        self.wait(2.0)

class Scene14_07(Scene):
    def construct(self):
        setup_base_scene(self, "AND THE NETWORK GENERATES THIS UNIQUE", "FINAL SYNTHESIS")
        
        # Literal illustration: A complete glowing crest/emblem emerging from structured vectors
        crest_outer = Circle(radius=1.5, color="#FFFFFF", stroke_width=3).move_to([0, -1.0, 0])
        crest_inner = Circle(radius=1.0, color="#FFFFFF", stroke_width=1.5).set_opacity(0.5).move_to([0, -1.0, 0])
        
        cross_lines = VGroup(
            Line([0, -2.5, 0], [0, 0.5, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.5),
            Line([-1.5, -1.0, 0], [1.5, -1.0, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.5)
        )
        
        center_star = Polygon([0, -0.2, 0], [-0.4, -1.2, 0], [0.6, -0.7, 0], [-0.6, -0.7, 0], [0.4, -1.2, 0], color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.8).move_to([0, -1.0, 0])
        
        self.play(Create(cross_lines), run_time=1.5)
        self.play(Create(crest_outer), Create(crest_inner), run_time=2.5)
        self.play(FadeIn(center_star, scale=0.5), run_time=1.5)
        self.wait(2.0)

# Global Canvas Configuration

def setup_scene_base(*args, **kwargs):
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

    """Sets up the mandatory title, footer, and borders for strict compliance."""
    # Title at y = -2.95 (SAFE from upper karaoke region)
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.4)

    # Footer bar & meta labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

class Scene14_08(Scene):
    def construct(self):
        setup_scene_base(self, "NETWORK GENERATES UNIQUE SIGNATURE", "NEURAL GENERATION")
        
        # Literal figurative visual: Central server outputting distinct glowing nodes/patterns
        server = RoundedRectangle(corner_radius=0.1, width=2.0, height=3.0, stroke_width=2, color="#FFFFFF", fill_opacity=0.1).move_to([-2.0, -1.0, 0])
        # Server racks lines
        racks = VGroup(*[Line(LEFT*0.8, RIGHT*0.8, stroke_width=1.5, color="#FFFFFF").move_to(server.get_center() + UP*y) for y in [1.0, 0.4, -0.2, -0.8]])
        
        # Output beam / arrows
        beam = Arrow(start=[-0.9, -1.0, 0], end=[0.8, -1.0, 0], stroke_width=3, color="#FFFFFF", buff=0.1)
        
        # Unique generated item (a complex geometric crystal / key symbol)
        unique_box = RoundedRectangle(corner_radius=0.2, width=1.8, height=1.8, stroke_width=2.5, color="#FFFFFF", fill_opacity=0.2).move_to([2.0, -1.0, 0])
        inner_star = VGroup(
            Line([-1.5, -1.5, 0], [-2.5, -0.5, 0], stroke_width=2, color="#FFFFFF"), # placeholder
        )
        # Draw explicit unique geometric lines inside
        u_line1 = Line(unique_box.get_corner(DL) + [0.2, 0.2, 0], unique_box.get_corner(UR) + [-0.2, -0.2, 0], stroke_width=2, color="#FFFFFF")
        u_line2 = Line(unique_box.get_corner(UL) + [0.2, -0.2, 0], unique_box.get_corner(DR) + [-0.2, 0.2, 0], stroke_width=2, color="#FFFFFF")
        u_circle = Circle(radius=0.4, stroke_width=2, color="#FFFFFF").move_to(unique_box.get_center())

        network_group = VGroup(server, racks, beam, unique_box, u_line1, u_line2, u_circle)
        
        self.play(FadeIn(server, shift=RIGHT*0.5), Create(racks), run_time=1.5)
        self.play(GrowArrow(beam), run_time=1.0)
        self.play(Create(unique_box), Create(u_circle), Create(u_line1), Create(u_line2), run_time=2.0)
        
        # Pulsing unique generation effect
        self.play(unique_box.animate.set_fill(0.4), run_time=1.5)
        self.wait(1.5)

class Scene14_09(Scene):
    def construct(self):
        setup_scene_base(self, "UNIQUE PATTERN EXPANSION", "PATTERN SYNTHESIS")

        # Literal figurative visual: Expanding unique nodes radiating outwards from a core
        center_node = Circle(radius=0.6, stroke_width=3, color="#FFFFFF", fill_opacity=0.3).move_to([0, -1.0, 0])
        
        # Radiating rings & nodes
        ring1 = Circle(radius=1.5, stroke_width=1.5, color="#FFFFFF").set_opacity(0.5).move_to([0, -1.0, 0])
        ring2 = Circle(radius=2.4, stroke_width=1.0, color="#FFFFFF").set_opacity(0.3).move_to([0, -1.0, 0])
        
        node_top = Circle(radius=0.2, stroke_width=2, color="#FFFFFF", fill_opacity=0.8).move_to([0, 1.4, 0])
        node_left = Circle(radius=0.2, stroke_width=2, color="#FFFFFF", fill_opacity=0.8).move_to([-2.4, -1.0, 0])
        node_right = Circle(radius=0.2, stroke_width=2, color="#FFFFFF", fill_opacity=0.8).move_to([2.4, -1.0, 0])
        
        conn1 = Line(center_node.get_center(), node_top.get_center(), stroke_width=2, color="#FFFFFF").set_opacity(0.7)
        conn2 = Line(center_node.get_center(), node_left.get_center(), stroke_width=2, color="#FFFFFF").set_opacity(0.7)
        conn3 = Line(center_node.get_center(), node_right.get_center(), stroke_width=2, color="#FFFFFF").set_opacity(0.7)

        self.play(GrowFromCenter(center_node), run_time=1.0)
        self.play(Create(ring1), Create(ring2), run_time=1.5)
        self.play(Create(conn1), Create(conn2), Create(conn3), FadeIn(node_top), FadeIn(node_left), FadeIn(node_right), run_time=2.0)
        
        # Rotate and pulse
        self.play(Rotate(ring2, angle=0.5, about_point=[0, -1.0, 0]), center_node.animate.set_fill(0.7), run_time=2.0)
        self.wait(1.0)

class Scene14_10(Scene):
    def construct(self):
        setup_scene_base(self, "DISTINCTIVE DATA STRUCTURES", "TOPOLOGY MAPPING")

        # Literal figurative visual: 3 distinct data blocks / puzzle pieces clicking together uniquely
        box1 = RoundedRectangle(corner_radius=0.15, width=1.4, height=1.4, stroke_width=2.5, color="#FFFFFF", fill_opacity=0.2).move_to([-2.0, -0.5, 0])
        box2 = RoundedRectangle(corner_radius=0.15, width=1.4, height=1.4, stroke_width=2.5, color="#FFFFFF", fill_opacity=0.4).move_to([0, -0.5, 0])
        box3 = RoundedRectangle(corner_radius=0.15, width=1.4, height=1.4, stroke_width=2.5, color="#FFFFFF", fill_opacity=0.6).move_to([2.0, -0.5, 0])
        
        # Unique internal icons (Lines inside boxes)
        b1_line = Line([-2.5, -1.0, 0], [-1.5, 0.0, 0], stroke_width=2, color="#FFFFFF")
        b2_cross = VGroup(
            Line([-0.5, -1.0, 0], [0.5, 0.0, 0], stroke_width=2, color="#FFFFFF"),
            Line([-0.5, 0.0, 0], [0.5, -1.0, 0], stroke_width=2, color="#FFFFFF")
        )
        b3_circ = Circle(radius=0.4, stroke_width=2, color="#FFFFFF").move_to([2.0, -0.5, 0])

        group = VGroup(box1, box2, box3, b1_line, b2_cross, b3_circ)
        
        self.play(FadeIn(box1, shift=RIGHT*1.0), FadeIn(b1_line), run_time=1.5)
        self.play(FadeIn(box2, shift=DOWN*1.0), FadeIn(b2_cross), run_time=1.5)
        self.play(FadeIn(box3, shift=LEFT*1.0), FadeIn(b3_circ), run_time=1.5)
        
        # Connective flow line underneath
        flow_line = Line([-2.5, -1.8, 0], [2.5, -1.8, 0], stroke_width=2, color="#FFFFFF").set_opacity(0.5)
        arrow_flow = Arrow([-0.1, -1.8, 0], [0.1, -1.8, 0], stroke_width=2, color="#FFFFFF")
        
        self.play(Create(flow_line), GrowArrow(arrow_flow), run_time=1.5)
        self.wait(1.5)

class Scene14_11(Scene):
    def construct(self):
        setup_scene_base(self, "GENERATIVE FINGERPRINT CREATION", "FINGERPRINT MATRIX")

        # Literal figurative visual: A grid of unique wave/bar signatures forming a unique ID
        bars = VGroup()
        heights = [0.8, 1.6, 1.2, 2.2, 0.5, 1.9, 1.4, 2.0, 0.9, 1.5]
        
        for i, h in enumerate(heights):
            x_pos = -2.7 + i * 0.6
            bar = Line([x_pos, -1.8, 0], [x_pos, -1.8 + h, 0], stroke_width=5, color="#FFFFFF")
            bars.add(bar)

        # Scanning line moving across
        scanner = Line([0, -2.2, 0], [0, 0.6, 0], stroke_width=2, color="#FFFFFF")
        scanner.set_opacity(0.8)
        scanner.move_to([-3.2, -0.8, 0])

        self.play(Create(bars, lag_ratio=0.1), run_time=3.0)
        self.play(FadeIn(scanner), run_time=0.5)
        self.play(scanner.animate.shift(RIGHT * 6.4), run_time=2.5, rate_func=linear)
        self.play(FadeOut(scanner), run_time=0.5)
        self.wait(1.0)

class Scene14_12(Scene):
    def construct(self):
        setup_scene_base(self, "UNIQUE ARTIFACT EXTRACTION", "ARTIFACT EXTRACTION")

        # Literal figurative visual: Funnel/Filter extracting a single brilliant crystal from messy stream
        funnel_left = Line([-2.5, 0.5, 0], [-0.5, -1.5, 0], stroke_width=3, color="#FFFFFF")
        funnel_right = Line([2.5, 0.5, 0], [0.5, -1.5, 0], stroke_width=3, color="#FFFFFF")
        
        # Messy incoming particle dots at top
        particles = VGroup(*[Circle(radius=0.08, fill_opacity=0.8, color="#FFFFFF").move_to([x, 0.8, 0]) for x in np.linspace(-2.0, 2.0, 9)])
        
        # Extracted crystal at bottom
        crystal = RoundedRectangle(corner_radius=0.1, width=0.8, height=1.2, stroke_width=2.5, color="#FFFFFF", fill_opacity=0.7).move_to([0, -1.8, 0])

        self.play(Create(funnel_left), Create(funnel_right), FadeIn(particles), run_time=2.0)
        
        # Animate particles moving down into funnel
        self.play(particles.animate.shift(DOWN * 1.8).set_opacity(0.2), run_time=2.0)
        
        # Reveal crystal
        self.play(GrowFromCenter(crystal), run_time=1.5)
        self.wait(2.0)

class Scene14_13(Scene):
    def construct(self):
        setup_scene_base(self, "THE FINAL UNIQUE MANIFESTATION", "MANIFESTATION COMPLETE")

        # Literal figurative visual: A large central glowing star/key representing the final unique output
        outer_ring = Circle(radius=2.0, stroke_width=2, color="#FFFFFF", fill_opacity=0.1).move_to([0, -0.9, 0])
        inner_box = Square(side_length=2.0, stroke_width=3, color="#FFFFFF", fill_opacity=0.3).move_to([0, -0.9, 0])
        inner_box.rotate(PI / 4)
        
        core_dot = Circle(radius=0.3, stroke_width=2, color="#FFFFFF", fill_opacity=1.0).move_to([0, -0.9, 0])
        
        # Radiating corner brackets
        bracket_tl = VGroup(
            Line([-1.8, 0.5, 0], [-1.2, 0.5, 0], stroke_width=3, color="#FFFFFF"),
            Line([-1.8, 0.5, 0], [-1.8, -0.1, 0], stroke_width=3, color="#FFFFFF")
        )
        bracket_br = VGroup(
            Line([1.8, -2.3, 0], [1.2, -2.3, 0], stroke_width=3, color="#FFFFFF"),
            Line([1.8, -2.3, 0], [1.8, -1.7, 0], stroke_width=3, color="#FFFFFF")
        )

        self.play(Create(outer_ring), run_time=1.5)
        self.play(GrowFromCenter(inner_box), run_time=1.5)
        self.play(FadeIn(core_dot), Create(bracket_tl), Create(bracket_br), run_time=2.0)
        
        # Final emphatic pulse
        self.play(outer_ring.animate.scale(1.1), inner_box.animate.scale(1.05), run_time=1.0)
        self.play(outer_ring.animate.scale(1/1.1), inner_box.animate.scale(1/1.05), run_time=1.0)
        self.wait(0.5)