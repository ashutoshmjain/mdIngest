import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Canvas Configuration

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

    # Strict Bottom Title Placement
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("BITCOIN NETWORK DEMAND", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene20_01(Scene):
    def construct(self):
        setup_base_scene(self, "NONSTOP DEMAND HITTING BITCOIN")
        
        # Literal figurative visual: A large Bitcoin symbol being bombarded by multiple incoming demand arrows
        btc_circle = Circle(radius=1.0, color="#FFFFFF", stroke_width=3).move_to([0, -1.0, 0])
        btc_text = Text("B", font="Arial", weight=BOLD, font_size=48, color="#FFFFFF").move_to(btc_circle.get_center())
        btc_group = VGroup(btc_circle, btc_text)
        
        arrows = VGroup()
        for i in range(5):
            y_pos = -2.2 + i * 0.6
            arr = Arrow(start=[-3.5, y_pos, 0], end=[-1.2, y_pos, 0], color="#FFFFFF", stroke_width=3, tip_length=0.2)
            arrows.add(arr)
            
        self.play(FadeIn(btc_group, scale=0.8), run_time=1.0)
        self.play(LaggedStart(*(FadeIn(arr, shift=RIGHT*0.3) for arr in arrows), lag_ratio=0.15), run_time=2.0)
        self.wait(4.0)

class Scene20_02(Scene):
    def construct(self):
        setup_base_scene(self, "NONSTOP DEMAND HITTING BITCOIN")
        
        # Literal figurative visual: Server rack continuously receiving heavy incoming data blocks
        server = RoundedRectangle(corner_radius=0.15, width=2.0, height=3.0, color="#FFFFFF", stroke_width=2).move_to([0, -1.0, 0])
        shelf1 = Line([-1.0, -0.5, 0], [1.0, -0.5, 0], color="#FFFFFF", stroke_width=1.5)
        shelf2 = Line([-1.0, -1.5, 0], [1.0, -1.5, 0], color="#FFFFFF", stroke_width=1.5)
        
        lights = VGroup()
        for y in [-0.2, -1.0, -2.0]:
            for x in [-0.6, -0.2, 0.2]:
                lights.add(Circle(radius=0.04, color="#FFFFFF", fill_opacity=1).move_to([x, y, 0]))
                
        server_group = VGroup(server, shelf1, shelf2, lights)
        
        blocks = VGroup()
        for i in range(3):
            b = Square(side_length=0.4, color="#FFFFFF", stroke_width=2).move_to([-3.0, -1.0 + (i-1)*0.8, 0])
            blocks.add(b)
            
        self.play(Create(server_group), run_time=1.0)
        self.play(LaggedStart(*(Wiggle(b, scale_factor=1.1) for b in blocks), lag_ratio=0.2), run_time=1.5)
        self.play(LaggedStart(*(b.animate.move_to([-1.0, b.get_y(), 0]).set_opacity(0.2) for b in blocks), lag_ratio=0.2), run_time=2.0)
        self.wait(3.1)

class Scene20_03(Scene):
    def construct(self):
        setup_base_scene(self, "NONSTOP DEMAND HITTING BITCOIN")
        
        # Literal figurative visual: High volume meter scaling up infinitely
        meter_arc = Arc(radius=1.5, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=3).move_to([0, -1.5, 0])
        needle = Line([0, -1.5, 0], [1.2, -0.5, 0], color="#FFFFFF", stroke_width=3)
        center_pin = Circle(radius=0.15, color="#FFFFFF", fill_opacity=1).move_to([0, -1.5, 0])
        
        ticks = VGroup()
        for ang in [PI, PI*0.75, PI*0.5, PI*0.25, 0]:
            p1 = np.array([0, -1.5, 0]) + 1.4 * np.array([np.cos(ang), np.sin(ang), 0])
            p2 = np.array([0, -1.5, 0]) + 1.6 * np.array([np.cos(ang), np.sin(ang), 0])
            ticks.add(Line(p1, p2, color="#FFFFFF", stroke_width=2))
            
        label = Text("OVERLOAD", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([0, -0.6, 0])
        
        self.play(Create(meter_arc), Create(ticks), run_time=1.0)
        self.play(FadeIn(center_pin), GrowFromPoint(needle, [0, -1.5, 0]), run_time=1.0)
        self.play(Rotate(needle, angle=-0.5, about_point=[0, -1.5, 0]), FadeIn(label, shift=UP*0.2), run_time=2.0)
        self.wait(3.6)

class Scene20_04(Scene):
    def construct(self):
        setup_base_scene(self, "NONSTOP DEMAND HITTING BITCOIN")
        
        # Literal figurative visual: A pipeline with heavy traffic flowing nonstop through nodes
        pipe_top = Line([-3.0, -0.2, 0], [3.0, -0.2, 0], color="#FFFFFF", stroke_width=2)
        pipe_bot = Line([-3.0, -1.8, 0], [3.0, -1.8, 0], color="#FFFFFF", stroke_width=2)
        
        nodes = VGroup()
        for x in [-2.0, 0.0, 2.0]:
            nodes.add(Square(side_length=0.8, color="#FFFFFF", stroke_width=2).move_to([x, -1.0, 0]))
            
        packets = VGroup()
        for x in [-2.8, -1.8, -0.8, 0.2, 1.2]:
            packets.add(Rectangle(width=0.4, height=0.2, color="#FFFFFF", fill_opacity=0.8).move_to([x, -1.0, 0]))
            
        self.play(Create(pipe_top), Create(pipe_bot), run_time=0.8)
        self.play(FadeIn(nodes), run_time=0.8)
        self.play(FadeIn(packets), run_time=0.6)
        self.play(packets.animate.shift(RIGHT * 1.5), rate_func=linear, run_time=3.0)
        self.wait(2.4)

class Scene20_05(Scene):
    def construct(self):
        setup_base_scene(self, "NONSTOP DEMAND HITTING BITCOIN")
        
        # Literal figurative visual: Incoming transactional blocks stacking up into an unyielding wall
        wall_base = Line([-3.0, -2.3, 0], [3.0, -2.3, 0], color="#FFFFFF", stroke_width=2)
        
        bricks = VGroup()
        for row in range(3):
            for col in range(5):
                b = Rectangle(width=1.0, height=0.4, color="#FFFFFF", stroke_width=2, fill_opacity=0.2)
                b.move_to([-2.0 + col * 1.0, -2.0 + row * 0.45, 0])
                bricks.add(b)
                
        incoming = Rectangle(width=1.0, height=0.4, color="#FFFFFF", stroke_width=2, fill_opacity=0.8).move_to([0, 0.5, 0])
        arr = Arrow([0, 0.1, 0], [0, -0.4, 0], color="#FFFFFF", stroke_width=2)
        
        self.play(Create(wall_base), FadeIn(bricks, lag_ratio=0.1), run_time=2.0)
        self.play(FadeIn(incoming, shift=DOWN*0.5), Create(arr), run_time=1.0)
        self.play(incoming.animate.move_to([0, -0.2, 0]), run_time=1.5)
        self.wait(3.1)

class Scene20_06(Scene):
    def construct(self):
        setup_base_scene(self, "NONSTOP DEMAND HITTING BITCOIN")
        
        # Literal figurative visual: Continuous pulsating rings radiating outward from a central bitcoin node
        center_node = Circle(radius=0.6, color="#FFFFFF", stroke_width=3, fill_opacity=0.3).move_to([0, -1.1, 0])
        b_text = Text("B", font="Arial", weight=BOLD, font_size=28, color="#FFFFFF").move_to(center_node.get_center())
        
        rings = VGroup()
        for i in range(3):
            r = Circle(radius=0.6 + (i+1)*0.6, color="#FFFFFF", stroke_width=1.5).move_to([0, -1.1, 0])
            r.set_opacity(1.0 - (i*0.3))
            rings.add(r)
            
        self.play(FadeIn(center_node), FadeIn(b_text), run_time=0.8)
        self.play(LaggedStart(*(Create(r) for r in rings), lag_ratio=0.3), run_time=2.5)
        self.play(rings.animate.scale(1.2).set_opacity(0.1), run_time=2.0)
        self.wait(2.3)

class Scene20_07(Scene):
    def construct(self):
        setup_base_scene(self, "NONSTOP DEMAND HITTING BITCOIN")
        
        # Literal figurative visual: Solid concrete pillar representing unbreakable, nonstop network resilience under massive weight
        pillar = Rectangle(width=2.0, height=3.0, color="#FFFFFF", stroke_width=3, fill_opacity=0.2).move_to([0, -1.0, 0])
        cap = Rectangle(width=2.6, height=0.4, color="#FFFFFF", stroke_width=3, fill_opacity=0.4).move_to([0, 0.6, 0])
        
        load_arrow_left = Arrow([-1.5, 1.5, 0], [-0.5, 0.8, 0], color="#FFFFFF", stroke_width=3, tip_length=0.2)
        load_arrow_right = Arrow([1.5, 1.5, 0], [0.5, 0.8, 0], color="#FFFFFF", stroke_width=3, tip_length=0.2)
        
        label = Text("CONSTANT DEMAND", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, -1.0, 0])
        
        self.play(Create(cap), Create(pillar), run_time=1.5)
        self.play(GrowArrow(load_arrow_left), GrowArrow(load_arrow_right), run_time=1.0)
        self.play(FadeIn(label, shift=UP*0.2), run_time=1.0)
        self.wait(4.1)

# Configure canvas & resolution strictly as required

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

    # Strict Bottom Title Placement at y = -2.95
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene20_08(Scene):
    def construct(self):
        setup_base_scene(self, "NONSTOP BITCOIN DEMAND", "NETWORK DEMAND")
        
        # Literal figurative visual: Massive incoming arrows hitting a central Bitcoin vault/server box
        box = RoundedRectangle(corner_radius=0.2, width=2.2, height=2.2, stroke_width=2.5, color="#FFFFFF")
        box.move_to([0, -1.0, 0])
        b_text = Text("B", font="Arial", weight=BOLD, font_size=40, color="#FFFFFF").move_to(box.get_center())
        
        arrows = VGroup()
        for i in range(5):
            y_pos = -2.0 + i * 0.5
            arr = Arrow(start=[-3.5, y_pos, 0], end=[-1.3, y_pos, 0], buff=0, stroke_width=3, color="#FFFFFF")
            arrows.add(arr)
            
        self.play(Create(box), Write(b_text), run_time=1.0)
        self.play(LaggedStart(*(GrowArrow(a) for a in arrows), lag_ratio=0.15), run_time=3.0)
        
        # Continuous pulse to show "nonstop"
        self.play(box.animate.scale(1.08), run_time=1.5)
        self.play(box.animate.scale(1.0), run_time=1.5)
        self.wait(1.0)

class Scene20_09(Scene):
    def construct(self):
        setup_base_scene(self, "INCOMING TRANSACTION SURGE", "NETWORK DEMAND")
        
        # Literal figurative visual: Stacks of transaction blocks rising endlessly
        stack = VGroup()
        for i in range(4):
            rect = RoundedRectangle(corner_radius=0.1, width=3.0, height=0.6, stroke_width=2.0, color="#FFFFFF")
            rect.move_to([0, -2.0 + i * 0.7, 0])
            txt = Text(f"TX BLOCK #{i+1}", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(rect.get_center())
            stack.add(VGroup(rect, txt))
            
        self.play(LaggedStart(*(FadeIn(block, shift=UP*0.5) for block in stack), lag_ratio=0.2), run_time=3.5)
        
        # Highlight top showing continuous additions
        top_arrow = Arrow(start=[0, 1.2, 0], end=[0, 2.0, 0], stroke_width=3, color="#FFFFFF")
        top_text = Text("NONSTOP", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").next_to(top_arrow, UP, buff=0.1)
        
        self.play(GrowArrow(top_arrow), FadeIn(top_text), run_time=2.0)
        self.wait(2.1)

class Scene20_10(Scene):
    def construct(self):
        setup_base_scene(self, "NETWORK LOAD INTENSITY", "NETWORK DEMAND")
        
        # Literal figurative visual: Power Meter / Gauge showing maximum load
        arc = Arc(radius=1.5, start_angle=PI, angle=PI, stroke_width=4, color="#FFFFFF").move_to([0, -1.0, 0])
        needle = Line([0, -1.0, 0], [1.2, 0.2, 0], stroke_width=3, color="#FFFFFF")
        
        labels = VGroup(
            Text("0", font="Arial", size=12, color="#FFFFFF").move_to([-1.8, -1.0, 0]),
            Text("MAX", font="Arial", size=12, color="#FFFFFF").move_to([1.8, -1.0, 0]),
            Text("NONSTOP FLOW", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, 0.8, 0])
        )
        
        self.play(Create(arc), FadeIn(labels), run_time=2.0)
        self.play(GrowFromPoint(needle, [0, -1.0, 0]), run_time=2.0)
        
        # Needle vibrating at max
        for _ in range(3):
            self.play(needle.animate.rotate(0.1, about_point=[0, -1.0, 0]), run_time=0.3)
            self.play(needle.animate.rotate(-0.1, about_point=[0, -1.0, 0]), run_time=0.3)
        self.wait(1.7)

class Scene20_11(Scene):
    def construct(self):
        setup_base_scene(self, "CONTINUOUS BLOCKCHAIN INTAKE", "NETWORK DEMAND")
        
        # Literal figurative visual: Funnel feeding into a server core
        funnel = Polygon([-1.5, 1.0, 0], [1.5, 1.0, 0], [0.4, -0.8, 0], [-0.4, -0.8, 0], stroke_width=2.5, color="#FFFFFF")
        funnel.move_to([0, 0, 0])
        
        server = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.2, stroke_width=2.5, color="#FFFFFF")
        server.move_to([0, -1.8, 0])
        
        incoming_dots = VGroup(*[Circle(radius=0.08, color="#FFFFFF", fill_opacity=1).move_to([np.sin(i)*1.2, 2.0 + i*0.2, 0]) for i in range(8)])
        
        self.play(Create(funnel), Create(server), run_time=2.0)
        self.play(LaggedStart(*(FadeIn(d, shift=DOWN*0.5) for d in incoming_dots), lag_ratio=0.1), run_time=3.0)
        self.wait(2.6)

class Scene20_12(Scene):
    def construct(self):
        setup_base_scene(self, "GLOBAL NODES PROCESSING", "NETWORK DEMAND")
        
        # Literal figurative visual: Network of connected nodes pulsing simultaneously
        nodes = VGroup()
        coords = [[-2, 0, 0], [2, 0, 0], [0, 1.2, 0], [-1.2, -1.5, 0], [1.2, -1.5, 0]]
        for c in coords:
            nodes.add(Circle(radius=0.3, stroke_width=2, color="#FFFFFF", fill_opacity=0.2).move_to(c))
            
        lines = VGroup(
            Line(coords[0], coords[2], stroke_width=1.5, color="#FFFFFF"),
            Line(coords[1], coords[2], stroke_width=1.5, color="#FFFFFF"),
            Line(coords[0], coords[3], stroke_width=1.5, color="#FFFFFF"),
            Line(coords[1], coords[4], stroke_width=1.5, color="#FFFFFF"),
            Line(coords[3], coords[4], stroke_width=1.5, color="#FFFFFF"),
            Line(coords[2], coords[3], stroke_width=1.5, color="#FFFFFF"),
            Line(coords[2], coords[4], stroke_width=1.5, color="#FFFFFF"),
        )
        
        self.play(Create(lines), run_time=2.0)
        self.play(LaggedStart(*(GrowFromCenter(n) for n in nodes), lag_ratio=0.15), run_time=2.5)
        
        # Pulse all nodes to show constant activity
        self.play(nodes.animate.set_fill(color="#FFFFFF", opacity=0.8), run_time=1.5)
        self.play(nodes.animate.set_fill(color="#FFFFFF", opacity=0.2), run_time=1.6)

class Scene20_13(Scene):
    def construct(self):
        setup_base_scene(self, "UNRELENTING BITCOIN DEMAND", "NETWORK DEMAND")
        
        # Literal figurative visual: Big bold upward arrow crushing resistance lines
        arrow = Arrow(start=[0, -2.2, 0], end=[0, 1.8, 0], stroke_width=5, color="#FFFFFF")
        
        lines = VGroup()
        for y_val in [-1.0, 0.0, 1.0]:
            l = Line([-2.5, y_val, 0], [2.5, y_val, 0], stroke_width=1.5, color="#FFFFFF")
            l.set_opacity(0.5)
            lines.add(l)
            
        label = Text("NONSTOP", font="Arial", weight=BOLD, font_size=18, color="#FFFFFF").move_to([0, 2.3, 0])
        
        self.play(Create(lines), run_time=1.5)
        self.play(GrowArrow(arrow), FadeIn(label), run_time=3.5)
        
        # Quick flash
        self.play(arrow.animate.set_opacity(0.5), run_time=0.6)
        self.play(arrow.animate.set_opacity(1.0), run_time=0.6)
        self.wait(1.4)

class Scene20_14(Scene):
    def construct(self):
        setup_base_scene(self, "THE PERPETUAL LEDGER", "NETWORK DEMAND")
        
        # Literal figurative visual: An open ledger book with pages flipping infinitely
        left_page = RoundedRectangle(corner_radius=0.1, width=2.2, height=2.8, stroke_width=2, color="#FFFFFF").move_to([-1.2, -0.4, 0])
        right_page = RoundedRectangle(corner_radius=0.1, width=2.2, height=2.8, stroke_width=2, color="#FFFFFF").move_to([1.2, -0.4, 0])
        
        # Lines representing text inside ledger
        text_lines = VGroup()
        for p in [left_page, right_page]:
            for i in range(5):
                tl = Line(p.get_corner(UL) + [0.2, -0.4 - i*0.4, 0], p.get_corner(UL) + [1.8, -0.4 - i*0.4, 0], stroke_width=1, color="#FFFFFF")
                tl.set_opacity(0.7)
                text_lines.add(tl)
                
        b_stamp = Text("B", font="Arial", weight=BOLD, font_size=32, color="#FFFFFF").move_to([0, -0.4, 0])
        
        self.play(Create(left_page), Create(right_page), run_time=2.0)
        self.play(FadeIn(text_lines), Write(b_stamp), run_time=3.0)
        
        # Final emphatic pulse
        self.play(left_page.animate.scale(1.05), right_page.animate.scale(1.05), run_time=1.3)
        self.wait(1.3)

# Canvas Configuration

def setup_scene(scene, category_text="BITCOIN NETWORK"):
    # Bottom Title Placement
    title = Text("Discussion on Nonstop Demand Hitting the Bitcoin Network", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene20_15(Scene):
    def construct(self):
        setup_scene(self)
        
        # Literal visual: A massive network server box receiving non-stop incoming demand arrows
        server = RoundedRectangle(corner_radius=0.2, width=3.0, height=2.0, stroke_width=2.5, color="#FFFFFF")
        server.move_to([0, -0.8, 0])
        
        # Server racks (horizontal lines)
        rack1 = Line(LEFT*1.2, RIGHT*1.2, stroke_width=1.5, color="#FFFFFF").move_to(server.get_center() + UP*0.4)
        rack2 = Line(LEFT*1.2, RIGHT*1.2, stroke_width=1.5, color="#FFFFFF").move_to(server.get_center())
        rack3 = Line(LEFT*1.2, RIGHT*1.2, stroke_width=1.5, color="#FFFFFF").move_to(server.get_center() + DOWN*0.4)
        
        # Bitcoin symbol "B" literal outline inside server
        btc_text = Text("₿", font="Arial", weight=BOLD, font_size=40, color="#FFFFFF").move_to(server.get_center() + RIGHT*0.9 + UP*0.6)
        
        server_group = VGroup(server, rack1, rack2, rack3, btc_text)
        
        # Incoming demand arrows (non-stop onslaught from left)
        arrows = VGroup()
        for i in range(5):
            y_pos = -1.8 + i * 0.5
            arr = Arrow(start=[-3.5, y_pos, 0], end=[-1.7, y_pos, 0], stroke_width=2.5, buff=0, color="#FFFFFF")
            arrows.add(arr)
            
        self.play(FadeIn(server_group, shift=DOWN*0.2), run_time=1.5)
        self.play(LaggedStart(*(GrowArrow(arr) for arr in arrows), lag_ratio=0.1), run_time=2.5)
        
        # Pulsing effect to show "nonstop demand hitting"
        self.play(server.animate.set_fill("#FFFFFF", opacity=0.15), run_time=1.0)
        self.play(server.animate.set_fill("#FFFFFF", opacity=0.0), run_time=1.0)
        
        self.wait(1.0)

class Scene20_16(Scene):
    def construct(self):
        setup_scene(self)
        
        # Literal visual: Intake pipe funneling massive volume into a bottleneck/node
        funnel_top = Line([-2.5, 0.5, 0], [2.5, 0.5, 0], stroke_width=3, color="#FFFFFF")
        funnel_left = Line([-2.5, 0.5, 0], [-0.5, -1.5, 0], stroke_width=3, color="#FFFFFF")
        funnel_right = Line([2.5, 0.5, 0], [0.5, -1.5, 0], stroke_width=3, color="#FFFFFF")
        
        pipe_bottom = RoundedRectangle(corner_radius=0.1, width=1.0, height=1.2, stroke_width=2.5, color="#FFFFFF")
        pipe_bottom.move_to([0, -2.1, 0])
        
        funnel_group = VGroup(funnel_top, funnel_left, funnel_right, pipe_bottom)
        
        # Demand bars crashing down into the funnel
        bars = VGroup()
        for i in range(6):
            x_pos = -1.8 + i * 0.7
            bar = Rectangle(width=0.4, height=1.2, stroke_width=2, color="#FFFFFF")
            bar.set_fill("#FFFFFF", opacity=0.3)
            bar.move_to([x_pos, 2.0, 0])
            bars.add(bar)
            
        self.play(Create(funnel_group), run_time=1.5)
        self.play(LaggedStart(*(bar.animate.shift(DOWN*2.2) for bar in bars), lag_ratio=0.15), run_time=3.0)
        
        # Pressure waves flashing out
        wave1 = Circle(radius=1.2, stroke_width=2, color="#FFFFFF").move_to([0, -1.5, 0])
        wave1.set_opacity(0.8)
        self.play(Create(wave1), wave1.animate.scale(1.8).set_opacity(0), run_time=2.1)
        
        self.wait(1.0)

class Scene20_17(Scene):
    def construct(self):
        setup_scene(self)
        
        # Literal visual: A towering pressure meter / gauge hitting maximum capacity
        gauge_bg = Circle(radius=1.8, stroke_width=3, color="#FFFFFF").move_to([0, -0.6, 0])
        gauge_bg.set_fill("#FFFFFF", opacity=0.05)
        
        # Tick marks around gauge
        ticks = VGroup()
        for angle in range(-220, 41, 35):
            rad = angle * DEGREES
            start_pt = [1.5 * np.cos(rad), -0.6 + 1.5 * np.sin(rad), 0]
            end_pt = [1.7 * np.cos(rad), -0.6 + 1.7 * np.sin(rad), 0]
            ticks.add(Line(start_pt, end_pt, stroke_width=2, color="#FFFFFF"))
            
        # Needle pointing straight to max (top right or heavy right)
        needle = Arrow(start=[0, -0.6, 0], end=[1.2, 0.8, 0], stroke_width=3, buff=0, color="#FFFFFF")
        
        # Center pivot
        pivot = Circle(radius=0.15, stroke_width=2, color="#FFFFFF").move_to([0, -0.6, 0])
        pivot.set_fill("#FFFFFF", opacity=1.0)
        
        gauge_group = VGroup(gauge_bg, ticks, needle, pivot)
        
        # "DEMAND" text label right inside
        demand_label = Text("DEMAND", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([0, -1.6, 0])
        
        self.play(Create(gauge_bg), Create(ticks), FadeIn(demand_label), run_time=2.0)
        self.play(GrowArrow(needle), FadeIn(pivot), run_time=1.5)
        
        # Rapid vibration / shaking of the needle to show intense nonstop pressure
        for _ in range(3):
            self.play(needle.animate.rotate(0.15, about_point=[0, -0.6, 0]), run_time=0.2)
            self.play(needle.animate.rotate(-0.3, about_point=[0, -0.6, 0]), run_time=0.2)
            self.play(needle.animate.rotate(0.15, about_point=[0, -0.6, 0]), run_time=0.2)
            
        self.wait(1.9)

class Scene20_18(Scene):
    def construct(self):
        setup_scene(self)
        
        # Literal visual: Bitcoin block grid continuously filling up with stacked transaction blocks
        grid_box = Rectangle(width=5.0, height=3.0, stroke_width=2.5, color="#FFFFFF").move_to([0, -0.6, 0])
        
        # Sub-blocks representing incoming demand transactions piling up
        blocks = VGroup()
        coords = [
            [-1.8, 0.4], [-0.6, 0.4], [0.6, 0.4], [1.8, 0.4],
            [-1.8, -0.4], [-0.6, -0.4], [0.6, -0.4], [1.8, -0.4],
            [-1.8, -1.2], [-0.6, -1.2], [0.6, -1.2], [1.8, -1.2]
        ]
        
        for c in coords:
            b = RoundedRectangle(corner_radius=0.08, width=1.0, height=0.6, stroke_width=2, color="#FFFFFF")
            b.move_to([c[0], c[1]-0.2, 0])
            b.set_fill("#FFFFFF", opacity=0.2)
            blocks.add(b)
            
        # Top banner label inside grid frame
        header_line = Line([-2.3, 0.6, 0], [2.3, 0.6, 0], stroke_width=1.5, color="#FFFFFF")
        title_tag = Text("BLOCKCHAIN CAPACITY", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, 0.85, 0])
        
        self.play(Create(grid_box), Create(header_line), FadeIn(title_tag), run_time=1.5)
        
        # Rapidly stack blocks filling the network
        self.play(LaggedStart(*(FadeIn(b, scale=0.8) for b in blocks), lag_ratio=0.08), run_time=3.5)
        
        # Final flash highlight showing nonstop hitting capacity
        flash_rect = Rectangle(width=5.2, height=3.2, stroke_width=3, color="#FFFFFF").move_to([0, -0.6, 0])
        self.play(FadeIn(flash_rect), run_time=0.3)
        self.play(FadeOut(flash_rect), run_time=0.3)
        
        self.wait(1.0)