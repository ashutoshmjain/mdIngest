import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Canvas Configuration

def setup_footer_and_title(scene, title_text_str):
    # Bottom Title Placement (y = -2.95)
    title = Text(title_text_str, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("LIGHTNING NETWORK", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)
    return title

class Scene13_01(Scene):
    def construct(self):
        title = setup_footer_and_title(self, "AND IT ACHIEVES THIS BY UTILIZING THE LIGHTNING NETWORK")
        
        # Literal figurative visual: A central server hub connected to fast nodes (Lightning/Speed theme)
        hub = Circle(radius=0.8, color="#FFFFFF", stroke_width=2).move_to([0, -1.0, 0])
        hub.set_fill("#FFFFFF", opacity=0.15)
        
        node_left = Rectangle(width=0.8, height=0.8, color="#FFFFFF", stroke_width=2).move_to([-2.5, 0.5, 0])
        node_left.set_fill("#FFFFFF", opacity=0.1)
        node_right = Rectangle(width=0.8, height=0.8, color="#FFFFFF", stroke_width=2).move_to([2.5, 0.5, 0])
        node_right.set_fill("#FFFFFF", opacity=0.1)
        
        line_left = Line([-2.1, 0.3, 0], [-0.6, -0.7, 0], color="#FFFFFF", stroke_width=2)
        line_right = Line([2.1, 0.3, 0], [0.6, -0.7, 0], color="#FFFFFF", stroke_width=2)
        
        # Lightning bolt in center
        bolt = Polygon([-0.1, 0.2, 0], [0.3, -0.1, 0], [0.0, -0.1, 0], [0.2, -0.5, 0], [-0.2, 0.0, 0], [0.0, 0.0, 0], color="#FFFFFF", stroke_width=2)
        bolt.set_fill("#FFFFFF", opacity=0.8).scale(0.8).move_to([0, -1.0, 0])

        group = VGroup(hub, node_left, node_right, line_left, line_right, bolt)
        
        self.play(FadeIn(group, shift=UP), run_time=1.5)
        
        # Pulse animation
        self.play(hub.animate.set_fill("#FFFFFF", opacity=0.4), bolt.animate.scale(1.2), run_time=1.5)
        self.play(hub.animate.set_fill("#FFFFFF", opacity=0.15), bolt.animate.scale(1/1.2), run_time=1.5)
        
        self.wait(1.8)

class Scene13_02(Scene):
    def construct(self):
        title = setup_footer_and_title(self, "AND IT ACHIEVES THIS BY UTILIZING THE LIGHTNING NETWORK")
        
        # Literal figurative visual: Two payment channels opening up (Parallel tracks with arrows)
        track_top = RoundedRectangle(corner_radius=0.1, width=5.0, height=0.8, color="#FFFFFF", stroke_width=2).move_to([0, 0.2, 0])
        track_bottom = RoundedRectangle(corner_radius=0.1, width=5.0, height=0.8, color="#FFFFFF", stroke_width=2).move_to([0, -1.5, 0])
        
        track_top.set_fill("#FFFFFF", opacity=0.1)
        track_bottom.set_fill("#FFFFFF", opacity=0.1)
        
        arrow_top = Arrow([-2.0, 0.2, 0], [2.0, 0.2, 0], color="#FFFFFF", stroke_width=2, buff=0)
        arrow_bottom = Arrow([2.0, -1.5, 0], [-2.0, -1.5, 0], color="#FFFFFF", stroke_width=2, buff=0)
        
        channels = VGroup(track_top, track_bottom, arrow_top, arrow_bottom)
        
        self.play(GrowFromCenter(channels), run_time=2.0)
        self.play(arrow_top.animate.shift(RIGHT * 0.3), arrow_bottom.animate.shift(LEFT * 0.3), run_time=1.5)
        self.play(arrow_top.animate.shift(LEFT * 0.3), arrow_bottom.animate.shift(RIGHT * 0.3), run_time=1.5)
        
        self.wait(1.3)

class Scene13_03(Scene):
    def construct(self):
        title = setup_footer_and_title(self, "AND IT ACHIEVES THIS BY UTILIZING THE LIGHTNING NETWORK")
        
        # Literal figurative visual: High-speed micro-transactions (multiple tiny blocks flying fast)
        blocks = VGroup(*[
            Square(side_length=0.6, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.2)
            for _ in range(5)
        ]).arrange(RIGHT, buff=0.4).move_to([0, -0.6, 0])
        
        speed_lines = VGroup(*[
            Line(LEFT * 3.5 + UP * i * 0.5, LEFT * 2.0 + UP * i * 0.5, color="#FFFFFF", stroke_width=1.5)
            for i in range(-2, 3)
        ])
        
        self.play(FadeIn(speed_lines, shift=RIGHT), FadeIn(blocks, shift=RIGHT), run_time=2.0)
        self.play(blocks.animate.shift(RIGHT * 1.5), run_time=2.0)
        self.play(blocks.animate.shift(LEFT * 1.5), run_time=2.0)
        
        self.wait(1.3)

class Scene13_04(Scene):
    def construct(self):
        title = setup_footer_and_title(self, "AND IT ACHIEVES THIS BY UTILIZING THE LIGHTNING NETWORK")
        
        # Literal figurative visual: Network mesh of nodes interconnected instantly
        nodes = VGroup()
        coords = [(-2, 0), (0, 1), (2, 0), (-1, -1.5), (1, -1.5)]
        
        for c in coords:
            circle = Circle(radius=0.35, color="#FFFFFF", stroke_width=2).move_to([c[0], c[1], 0])
            circle.set_fill("#FFFFFF", opacity=0.3)
            nodes.add(circle)
            
        lines = VGroup(
            Line(nodes[0].get_center(), nodes[1].get_center(), color="#FFFFFF", stroke_width=1.5),
            Line(nodes[1].get_center(), nodes[2].get_center(), color="#FFFFFF", stroke_width=1.5),
            Line(nodes[0].get_center(), nodes[3].get_center(), color="#FFFFFF", stroke_width=1.5),
            Line(nodes[2].get_center(), nodes[4].get_center(), color="#FFFFFF", stroke_width=1.5),
            Line(nodes[3].get_center(), nodes[4].get_center(), color="#FFFFFF", stroke_width=1.5),
            Line(nodes[0].get_center(), nodes[2].get_center(), color="#FFFFFF", stroke_width=1.5),
        )
        
        network = VGroup(lines, nodes).move_to([0, -0.5, 0])
        
        self.play(Create(lines), run_time=2.0)
        self.play(FadeIn(nodes, scale=0.5), run_time=1.5)
        self.play(network.animate.scale(1.05), run_time=1.5)
        self.play(network.animate.scale(1/1.05), run_time=1.3)
        
        self.wait(1.0)

class Scene13_05(Scene):
    def construct(self):
        title = setup_footer_and_title(self, "AND IT ACHIEVES THIS BY UTILIZING THE LIGHTNING NETWORK")
        
        # Literal figurative visual: Lightning bolt breaking through a barrier/wall
        wall = VGroup(*[
            Line([-0.2, i, 0], [-0.2, i + 0.4, 0], color="#FFFFFF", stroke_width=4)
            for i in np.arange(-2.0, 1.0, 0.6)
        ]).move_to([0, -0.5, 0])
        
        bolt = Polygon(
            [-2.0, 0.5, 0], [-0.5, -0.2, 0], [-1.2, -0.2, 0], 
            [0.5, -1.5, 0], [0.0, -0.5, 0], [1.0, -0.5, 0], [-2.0, 0.5, 0]
        , color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.5).scale(0.8).move_to([0, -0.5, 0])
        
        self.play(Create(wall), run_time=1.5)
        self.play(FadeIn(bolt, shift=RIGHT), run_time=2.0)
        self.play(wall.animate.shift(LEFT * 0.5).set_opacity(0.3), bolt.animate.scale(1.1), run_time=2.0)
        
        self.wait(1.8)

class Scene13_06(Scene):
    def construct(self):
        title = setup_footer_and_title(self, "AND IT ACHIEVES THIS BY UTILIZING THE LIGHTNING NETWORK")
        
        # Literal figurative visual: Efficiency gear/cog with lightning center
        outer_circle = Circle(radius=1.2, color="#FFFFFF", stroke_width=2).move_to([0, -0.6, 0])
        outer_circle.set_fill("#FFFFFF", opacity=0.1)
        
        inner_bolt = Polygon(
            [0, 0.6, 0], [-0.3, 0.1, 0], [-0.1, 0.1, 0],
            [-0.3, -0.6, 0], [0.4, 0.0, 0], [0.1, 0.0, 0], [0, 0.6, 0]
        , color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.7).move_to([0, -0.6, 0]).scale(1.2)
        
        radii = VGroup(*[
            Line([0, -0.6, 0], [1.2 * np.cos(i), -0.6 + 1.2 * np.sin(i), 0], color="#FFFFFF", stroke_width=1.5)
            for i in np.linspace(0, 2*np.pi, 6, endpoint=False)
        ])
        
        gear = VGroup(outer_circle, radii, inner_bolt)
        
        self.play(Rotate(gear, angle=2*np.pi, about_point=[0, -0.6, 0]), run_time=4.0, rate_func=linear)
        self.play(gear.animate.scale(1.15), run_time=1.5)
        self.play(gear.animate.scale(1/1.15), run_time=1.8)

class Scene13_07(Scene):
    def construct(self):
        title = setup_footer_and_title(self, "AND IT ACHIEVES THIS BY UTILIZING THE LIGHTNING NETWORK")
        
        # Literal figurative visual: Scaling up - multiple layers stacked representing off-chain scaling
        box1 = RoundedRectangle(corner_radius=0.1, width=4.0, height=0.8, color="#FFFFFF", stroke_width=2).move_to([0, 0.5, 0]).set_fill("#FFFFFF", opacity=0.1)
        box2 = RoundedRectangle(corner_radius=0.1, width=4.5, height=0.8, color="#FFFFFF", stroke_width=2).move_to([0, -0.4, 0]).set_fill("#FFFFFF", opacity=0.2)
        box3 = RoundedRectangle(corner_radius=0.1, width=5.0, height=0.8, color="#FFFFFF", stroke_width=2).move_to([0, -1.3, 0]).set_fill("#FFFFFF", opacity=0.3)
        
        stack = VGroup(box1, box2, box3)
        
        up_arrow = Arrow([0, -1.8, 0], [0, 1.3, 0], color="#FFFFFF", stroke_width=3, buff=0.1)
        
        self.play(FadeIn(stack, shift=UP), run_time=2.0)
        self.play(GrowArrow(up_arrow), run_time=2.0)
        self.play(stack.animate.shift(UP * 0.1), run_time=1.5)
        
        self.wait(1.8)

# Configure canvas

def setup_footer():
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("LIGHTNING NETWORK", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    return VGroup(footer_line, left_text, right_text)

def setup_title(text_str):
    return Text(text_str, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])

class Scene13_08(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("UTILIZING THE LIGHTNING NETWORK")
        self.play(FadeIn(title), run_time=0.6)
        
        # Literal lightning bolt icon + server nodes
        bolt = Polygon(
            [0, 1.5, 0], [-0.8, 0.2, 0], [0.2, 0.2, 0],
            [-0.4, -1.2, 0], [0.9, -0.1, 0], [-0.1, -0.1, 0],
            color="#FFFFFF", stroke_width=3, fill_opacity=0.3
        ).move_to([0, -0.5, 0])
        
        node_left = RoundedRectangle(corner_radius=0.1, width=1.2, height=0.8, stroke_width=2, color="#FFFFFF").move_to([-2.2, -0.5, 0])
        node_right = RoundedRectangle(corner_radius=0.1, width=1.2, height=0.8, stroke_width=2, color="#FFFFFF").move_to([2.2, -0.5, 0])
        
        arrow_l = Arrow(node_left.get_right(), bolt.get_left(), buff=0.1, stroke_width=2, color="#FFFFFF")
        arrow_r = Arrow(bolt.get_right(), node_right.get_left(), buff=0.1, stroke_width=2, color="#FFFFFF")
        
        self.play(
            FadeIn(node_left, shift=RIGHT*0.2),
            FadeIn(node_right, shift=LEFT*0.2),
            run_time=1.0
        )
        self.play(GrowArrow(arrow_l), GrowArrow(arrow_r), FadeIn(bolt, scale=0.8), run_time=1.5)
        self.wait(4.2)

class Scene13_09(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("FAST LAYER-2 CHANNELS")
        self.play(FadeIn(title), run_time=0.6)
        
        # Two parallel tracks representing layer 1 and layer 2
        track1 = Line(LEFT * 2.8, RIGHT * 2.8, stroke_width=2, color="#FFFFFF").set_opacity(0.4).move_to([0, 0.8, 0])
        track2 = Line(LEFT * 2.8, RIGHT * 2.8, stroke_width=4, color="#FFFFFF").move_to([0, -0.8, 0])
        
        label1 = Text("LAYER 1", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").set_opacity(0.5).next_to(track1, UP, buff=0.1)
        label2 = Text("LIGHTNING LAYER 2", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").next_to(track2, UP, buff=0.1)
        
        # Fast moving dashes/pulses on layer 2
        pulse = Dot(color="#FFFFFF", radius=0.12).move_to(track2.get_left())
        
        self.play(Create(track1), Create(track2), FadeIn(label1), FadeIn(label2), run_time=1.0)
        self.play(FadeIn(pulse), run_time=0.3)
        self.play(pulse.animate.move_to(track2.get_right()), run_time=2.0, rate_func=linear)
        self.play(FadeOut(pulse), run_time=0.2)
        self.wait(3.2)

class Scene13_10(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("INSTANT MICROTRANSACTIONS")
        self.play(FadeIn(title), run_time=0.6)
        
        # Clock face showing instant speed
        clock = Circle(radius=1.2, stroke_width=2.5, color="#FFFFFF").move_to([0, -0.5, 0])
        center_dot = Dot(color="#FFFFFF", radius=0.08).move_to(clock.get_center())
        hand = Line(clock.get_center(), clock.get_center() + UP * 0.9, stroke_width=3, color="#FFFFFF")
        
        # Dollar signs popping out instantly
        d1 = Text("$", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to([-1.5, 0.8, 0])
        d2 = Text("$", font="Arial", weight=BOLD, font_size=28, color="#FFFFFF").move_to([0, 1.2, 0])
        d3 = Text("$", font="Arial", weight=BOLD, font_size=32, color="#FFFFFF").move_to([1.5, 0.8, 0])
        
        self.play(Create(clock), FadeIn(center_dot), Create(hand), run_time=1.0)
        self.play(
            FadeIn(d1, scale=0.5),
            FadeIn(d2, scale=0.5),
            FadeIn(d3, scale=0.5),
            run_time=0.8
        )
        self.play(Rotate(hand, angle=-PI * 1.5, about_point=clock.get_center()), run_time=1.0)
        self.wait(3.9)

class Scene13_11(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("PEER-TO-PEER PAYMENT HUBS")
        self.play(FadeIn(title), run_time=0.6)
        
        # Central hub circle and surrounding nodes with connecting lines
        hub = Circle(radius=0.6, stroke_width=3, color="#FFFFFF", fill_opacity=0.2).move_to([0, -0.5, 0])
        hub_text = Text("HUB", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(hub.get_center())
        
        nodes = []
        lines = []
        angles = [0, PI/2, PI, 3*PI/2]
        for i, ang in enumerate(angles):
            pos = np.array([np.cos(ang) * 2.2, np.sin(ang) * 1.2 - 0.5, 0])
            n = Circle(radius=0.3, stroke_width=2, color="#FFFFFF").move_to(pos)
            l = Line(hub.get_center(), n.get_center(), stroke_width=1.5, color="#FFFFFF").set_opacity(0.6)
            nodes.append(n)
            lines.append(l)
            
        self.play(Create(hub), FadeIn(hub_text), run_time=0.8)
        self.play(
            *[AnimationGroup(Create(l), Create(n)) for l, n in zip(lines, nodes)],
            run_time=1.5
        )
        self.wait(4.4)

class Scene13_12(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("BYPASSING BLOCKCHAIN CONGESTION")
        self.play(FadeIn(title), run_time=0.6)
        
        # Maze / Block obstruction vs Direct Tunnel (Lightning)
        block_rect = RoundedRectangle(corner_radius=0.1, width=2.0, height=1.2, stroke_width=2, color="#FFFFFF").move_to([0, -0.5, 0])
        block_text = Text("BLOCK", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(block_rect.get_center())
        
        # Curved bypass arrow over the top
        bypass_arc = Arc(radius=1.8, start_angle=0, angle=PI, stroke_width=3, color="#FFFFFF").move_to([0, -0.5, 0])
        arrow_head = Arrow(bypass_arc.get_start() + LEFT*0.1, bypass_arc.get_start(), stroke_width=2, color="#FFFFFF")
        
        self.play(FadeIn(block_rect), FadeIn(block_text), run_time=1.0)
        self.play(Create(bypass_arc), GrowArrow(arrow_head), run_time=1.5)
        self.wait(4.2)

class Scene13_13(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("SCALING BITCOIN GLOBALLY")
        self.play(FadeIn(title), run_time=0.6)
        
        # Globe wireframe representation (circles crossing)
        globe = Circle(radius=1.3, stroke_width=2, color="#FFFFFF").move_to([0, -0.5, 0])
        equator = Ellipse(width=2.6, height=0.8, stroke_width=1.5, color="#FFFFFF").move_to([0, -0.5, 0])
        meridian = Ellipse(width=0.8, height=2.6, stroke_width=1.5, color="#FFFFFF").move_to([0, -0.5, 0])
        
        # Expanding pulse rings outward
        ring1 = Circle(radius=1.5, stroke_width=1, color="#FFFFFF").move_to([0, -0.5, 0]).set_opacity(0.8)
        ring2 = Circle(radius=1.8, stroke_width=1, color="#FFFFFF").move_to([0, -0.5, 0]).set_opacity(0.4)
        
        self.play(Create(globe), Create(equator), Create(meridian), run_time=1.2)
        self.play(
            ring1.animate.scale(1.3).set_opacity(0),
            ring2.animate.scale(1.4).set_opacity(0),
            run_time=2.0,
            rate_func=linear
        )
        self.wait(3.5)

class Scene13_14(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("ZERO TRUST ARCHITECTURE")
        self.play(FadeIn(title), run_time=0.6)
        
        # Two secure vaults / lock symbols connected securely
        lock_box = RoundedRectangle(corner_radius=0.15, width=1.6, height=1.4, stroke_width=2.5, color="#FFFFFF").move_to([-1.8, -0.5, 0])
        lock_shackle = Arc(radius=0.5, start_angle=0, angle=PI, stroke_width=2.5, color="#FFFFFF").move_to([-1.8, 0.3, 0])
        
        lock_box2 = RoundedRectangle(corner_radius=0.15, width=1.6, height=1.4, stroke_width=2.5, color="#FFFFFF").move_to([1.8, -0.5, 0])
        lock_shackle2 = Arc(radius=0.5, start_angle=0, angle=PI, stroke_width=2.5, color="#FFFFFF").move_to([1.8, 0.3, 0])
        
        secure_line = DoubleArrow(lock_box.get_right(), lock_box2.get_left(), buff=0.1, stroke_width=2, color="#FFFFFF")
        shield_icon = Polygon([0, 0.8, 0], [0.7, 0.2, 0], [0.5, -0.8, 0], [-0.5, -0.8, 0], [-0.7, 0.2, 0], stroke_width=2, color="#FFFFFF", fill_opacity=0.2).scale(0.6).move_to([0, -0.5, 0])
        
        self.play(
            Create(lock_box), Create(lock_shackle),
            Create(lock_box2), Create(lock_shackle2),
            run_time=1.0
        )
        self.play(GrowArrow(secure_line), FadeIn(shield_icon, scale=0.5), run_time=1.2)
        self.wait(4.5)

# Canvas Configuration

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

    # Strict bottom title placement
    title = Text("AND IT ACHIEVES THIS BY UTILIZING THE LIGHTNING NETWORK", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    self.play(FadeIn(title), run_time=0.6)
    
    # Bottom footer bar & meta labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    self.add(footer_line, left_text, right_text)

class Scene13_15(Scene):
    def construct(self):
        setup_scene_base(self, "LIGHTNING NETWORK PROTOCOL")
        
        # Literal figurative visual: A central server splitting heavy load into rapid lightning paths (Lightning bolt + nodes)
        center_node = RoundedRectangle(corner_radius=0.15, width=1.2, height=1.2, stroke_color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([-2.0, -1.0, 0])
        server_text = Text("BASE", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(center_node.get_center())
        
        target_node = RoundedRectangle(corner_radius=0.15, width=1.2, height=1.2, stroke_color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([2.0, -1.0, 0])
        target_text = Text("PEER", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(target_node.get_center())
        
        # Giant literal Lightning Bolt bridging them across the top safe area (y in [-2.5, 0.4])
        lightning = Polygon(
            [-0.5, 0.2, 0],
            [0.3, 0.8, 0],
            [-0.1, 0.0, 0],
            [0.6, -0.4, 0],
            [-0.2, -0.4, 0],
            [0.1, -1.0, 0],
            stroke_color="#FFFFFF",
            stroke_width=3.5,
            fill_color="#FFFFFF",
            fill_opacity=0.3
        ).scale(1.2).move_to([0, -0.3, 0])
        
        # Connecting pathways
        path1 = Line(center_node.get_top(), lightning.get_left(), color="#FFFFFF", stroke_width=2).set_opacity(0.7)
        path2 = Line(lightning.get_right(), target_node.get_top(), color="#FFFFFF", stroke_width=2).set_opacity(0.7)
        
        group = VGroup(center_node, server_text, target_node, target_text, lightning, path1, path2)
        
        self.play(FadeIn(group, shift=UP*0.3), run_time=1.5)
        self.play(Indicate(lightning, scale_factor=1.1, color="#FFFFFF"), run_time=1.0)
        self.wait(4.2)

class Scene13_16(Scene):
    def construct(self):
        setup_scene_base(self, "CHANNEL CAPACITY")
        
        # Literal figurative visual: Dual payment channel balance scales / channels
        box_left = RoundedRectangle(corner_radius=0.2, width=2.0, height=2.2, stroke_color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.1).move_to([-1.8, -0.8, 0])
        box_right = RoundedRectangle(corner_radius=0.2, width=2.0, height=2.2, stroke_color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.1).move_to([1.8, -0.8, 0])
        
        label_l = Text("CHANNEL A", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").next_to(box_left, UP, buff=0.1)
        label_r = Text("CHANNEL B", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").next_to(box_right, UP, buff=0.1)
        
        # Fast double arrows moving back and forth (Lightning speed transactions)
        arrow1 = DoubleArrow(start=[-0.8, -0.5, 0], end=[0.8, -0.5, 0], color="#FFFFFF", stroke_width=3, tip_length=0.2)
        arrow2 = DoubleArrow(start=[-0.8, -1.1, 0], end=[0.8, -1.1, 0], color="#FFFFFF", stroke_width=3, tip_length=0.2)
        
        transfer_label = Text("INSTANT MICRO-PAYMENTS", font="Arial", weight=BOLD, font_size=11, color="#FFFFFF").move_to([0, 0.4, 0])
        
        group = VGroup(box_left, box_right, label_l, label_r, arrow1, arrow2, transfer_label)
        
        self.play(FadeIn(group), run_time=1.5)
        self.play(
            arrow1.animate.shift(RIGHT * 0.3),
            arrow2.animate.shift(LEFT * 0.3),
            run_time=1.0
        )
        self.play(
            arrow1.animate.shift(LEFT * 0.3),
            arrow2.animate.shift(RIGHT * 0.3),
            run_time=1.0
        )
        self.wait(3.8)

class Scene13_17(Scene):
    def construct(self):
        setup_scene_base(self, "OFF-CHAIN SETTLEMENT")
        
        # Literal figurative visual: Layered structure (Base chain at bottom, Fast Lightning Network grid above)
        base_layer = RoundedRectangle(corner_radius=0.1, width=5.0, height=0.8, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.1).move_to([0, -1.8, 0])
        base_text = Text("L1: BASE BLOCKCHAIN SETTLEMENT", font="Arial", weight=BOLD, font_size=11, color="#FFFFFF").move_to(base_layer.get_center())
        
        net_box1 = RoundedRectangle(corner_radius=0.1, width=1.4, height=1.0, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).move_to([-1.8, -0.2, 0])
        net_box2 = RoundedRectangle(corner_radius=0.1, width=1.4, height=1.0, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).move_to([0, -0.2, 0])
        net_box3 = RoundedRectangle(corner_radius=0.1, width=1.4, height=1.0, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).move_to([1.8, -0.2, 0])
        
        net_label = Text("L2: LIGHTNING NETWORK MESH", font="Arial", weight=BOLD, font_size=11, color="#FFFFFF").move_to([0, 0.7, 0])
        
        conn1 = Line(net_box1.get_top(), net_label.get_bottom(), color="#FFFFFF", stroke_width=1.5).set_opacity(0.6)
        conn2 = Line(net_box2.get_top(), net_label.get_bottom(), color="#FFFFFF", stroke_width=1.5).set_opacity(0.6)
        conn3 = Line(net_box3.get_top(), net_label.get_bottom(), color="#FFFFFF", stroke_width=1.5).set_opacity(0.6)
        
        bridge_arrow = DoubleArrow(start=[0, -0.7, 0], end=[0, -1.3, 0], color="#FFFFFF", stroke_width=2, tip_length=0.15)
        
        group = VGroup(base_layer, base_text, net_box1, net_box2, net_box3, net_label, conn1, conn2, conn3, bridge_arrow)
        
        self.play(FadeIn(group, shift=UP*0.2), run_time=1.5)
        self.play(Flash(bridge_arrow, color="#FFFFFF", flash_radius=0.4), run_time=1.0)
        self.wait(4.8)