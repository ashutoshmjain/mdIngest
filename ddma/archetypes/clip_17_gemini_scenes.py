import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Configure canvas and resolution

def setup_scene(scene, category_text):
    # Standard Title at bottom (y = -2.95)
    title = Text("CRYPTO ECOSYSTEM", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.4)
    
    # Footer elements
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene17_01(Scene):
    def construct(self):
        setup_scene(self, "VAST NETWORK")
        
        # Central hub with radiating nodes representing the vast ecosystem
        hub = Circle(radius=0.6, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to([0, -1.0, 0])
        hub_text = Text("ECO", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(hub.get_center())
        
        nodes = VGroup()
        lines = VGroup()
        
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        for angle in angles:
            rad = np.radians(angle)
            pos = np.array([np.cos(rad) * 2.2, np.sin(rad) * 1.5 - 1.0, 0])
            node = Circle(radius=0.3, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.1).move_to(pos)
            line = Line(hub.get_center(), pos, color="#FFFFFF", stroke_width=1)
            line.set_opacity(0.5)
            nodes.add(node)
            lines.add(line)
            
        self.play(FadeIn(hub), FadeIn(hub_text), run_time=1.0)
        self.play(LaggedStart(FadeIn(lines), FadeIn(nodes), lag_ratio=0.1), run_time=4.0)
        self.wait(2.2)

class Scene17_02(Scene):
    def construct(self):
        setup_scene(self, "INTERCONNECTED LAYERS")
        
        # Stacked ecosystem layers (representing vast depth)
        layer1 = RoundedRectangle(corner_radius=0.2, width=5.0, height=0.8, color="#FFFFFF", stroke_width=2, fill_opacity=0.15).move_to([0, 0.5, 0])
        t1 = Text("LAYER 1 : BASE BLOCKCHAIN", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(layer1.get_center())
        
        layer2 = RoundedRectangle(corner_radius=0.2, width=4.0, height=0.8, color="#FFFFFF", stroke_width=2, fill_opacity=0.15).move_to([0, -0.6, 0])
        t2 = Text("LAYER 2 : SCALING PROTOCOLS", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(layer2.get_center())
        
        layer3 = RoundedRectangle(corner_radius=0.2, width=3.0, height=0.8, color="#FFFFFF", stroke_width=2, fill_opacity=0.15).move_to([0, -1.7, 0])
        t3 = Text("APPLICATIONS / DAPPS", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(layer3.get_center())
        
        arr1 = Arrow(layer1.get_bottom(), layer2.get_top(), color="#FFFFFF", stroke_width=2, buff=0.05)
        arr2 = Arrow(layer2.get_bottom(), layer3.get_top(), color="#FFFFFF", stroke_width=2, buff=0.05)
        
        self.play(FadeIn(layer1), FadeIn(t1), run_time=1.5)
        self.play(GrowArrow(arr1), FadeIn(layer2), FadeIn(t2), run_time=2.0)
        self.play(GrowArrow(arr2), FadeIn(layer3), FadeIn(t3), run_time=2.0)
        self.wait(2.1)

class Scene17_03(Scene):
    def construct(self):
        setup_scene(self, "EXPANSIVE GLOBE")
        
        # Literal globe outline with grid lines representing vast global reach
        globe = Circle(radius=1.8, color="#FFFFFF", stroke_width=2, fill_opacity=0.05).move_to([0, -1.0, 0])
        lat1 = Arc(radius=1.8, start_angle=0, angle=TAU, color="#FFFFFF", stroke_width=1).move_to([0, -1.0, 0])
        lat1.stretch_to_fit_height(0.8)
        lat2 = Arc(radius=1.8, start_angle=0, angle=TAU, color="#FFFFFF", stroke_width=1).move_to([0, -1.0, 0])
        lat2.stretch_to_fit_height(2.4)
        lon = Line([0, 0.8, 0], [0, -2.8, 0], color="#FFFFFF", stroke_width=1)
        
        # Nodes on globe
        dot1 = Dot([1.0, -0.5, 0], color="#FFFFFF", radius=0.08)
        dot2 = Dot([-1.2, -1.5, 0], color="#FFFFFF", radius=0.08)
        dot3 = Dot([0.3, -2.2, 0], color="#FFFFFF", radius=0.08)
        dot4 = Dot([-0.8, -0.2, 0], color="#FFFFFF", radius=0.08)
        
        self.play(Create(globe), FadeIn(lat1), FadeIn(lat2), Create(lon), run_time=3.5)
        self.play(FadeIn(dot1), FadeIn(dot2), FadeIn(dot3), FadeIn(dot4), run_time=2.0)
        self.wait(2.1)

class Scene17_04(Scene):
    def construct(self):
        setup_scene(self, "DIVERSE SECTORS")
        
        # Four quadrants representing DeFI, NFTs, Infrastructure, DAOs
        box1 = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.2, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.1).move_to([-1.5, -0.2, 0])
        txt1 = Text("DeFi", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(box1.get_center())
        
        box2 = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.2, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.1).move_to([1.5, -0.2, 0])
        txt2 = Text("NFTs", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(box2.get_center())
        
        box3 = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.2, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.1).move_to([-1.5, -1.8, 0])
        txt3 = Text("INFRA", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(box3.get_center())
        
        box4 = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.2, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.1).move_to([1.5, -1.8, 0])
        txt4 = Text("DAOs", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(box4.get_center())
        
        center_core = Circle(radius=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to([0, -1.0, 0])
        c_txt = Text("VAST", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").move_to(center_core.get_center())
        
        self.play(FadeIn(center_core), FadeIn(c_txt), run_time=1.0)
        self.play(FadeIn(box1), FadeIn(txt1), FadeIn(box2), FadeIn(txt2), run_time=2.5)
        self.play(FadeIn(box3), FadeIn(txt3), FadeIn(box4), FadeIn(txt4), run_time=2.5)
        self.wait(1.6)

class Scene17_05(Scene):
    def construct(self):
        setup_scene(self, "EXPANSION METRICS")
        
        # Upward expanding bar graph showing ecosystem growth
        axes_base = Line([-3.0, -2.5, 0], [3.0, -2.5, 0], color="#FFFFFF", stroke_width=2)
        axes_vert = Line([-3.0, -2.5, 0], [-3.0, 0.2, 0], color="#FFFFFF", stroke_width=2)
        
        bar1 = Rectangle(width=0.6, height=1.0, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.2).move_to([-2.0, -2.0, 0], aligned_edge=DOWN)
        bar2 = Rectangle(width=0.6, height=1.8, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.3).move_to([-0.8, -1.6, 0], aligned_edge=DOWN)
        bar3 = Rectangle(width=0.6, height=2.5, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.4).make_allocatable().move_to([0.4, -1.25, 0], aligned_edge=DOWN)
        bar4 = Rectangle(width=0.6, height=3.4, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.6).move_to([1.6, -0.8, 0], aligned_edge=DOWN)
        
        trend_line = Line([-2.0, -1.5, 0], [1.6, 0.4, 0], color="#FFFFFF", stroke_width=2)
        
        self.play(Create(axes_base), Create(axes_vert), run_time=1.0)
        self.play(FadeIn(bar1), FadeIn(bar2), run_time=2.0)
        self.play(FadeIn(bar3), FadeIn(bar4), run_time=2.0)
        self.play(Create(trend_line), run_time=1.0)
        self.wait(1.6)

class Scene17_06(Scene):
    def construct(self):
        setup_scene(self, "LIMITLESS HORIZONS")
        
        # Concentric expanding rings representing vastness
        ring1 = Circle(radius=0.8, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.1).move_to([0, -1.0, 0])
        ring2 = Circle(radius=1.6, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.08).move_to([0, -1.0, 0])
        ring3 = Circle(radius=2.4, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.05).move_to([0, -1.0, 0])
        ring4 = Circle(radius=3.2, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.02).move_to([0, -1.0, 0])
        
        core_dot = Dot([0, -1.0, 0], color="#FFFFFF", radius=0.1)
        
        self.play(FadeIn(core_dot), run_time=0.6)
        self.play(Create(ring1), run_time=1.5)
        self.play(Create(ring2), run_time=1.5)
        self.play(Create(ring3), run_time=1.5)
        self.play(Create(ring4), run_time=1.5)
        self.wait(1.0)

class Scene17_07(Scene):
    def construct(self):
        setup_scene(self, "THE VAST ECOSYSTEM")
        
        # Central glowing box enclosing the summation of the vast ecosystem
        outer_box = RoundedRectangle(corner_radius=0.3, width=6.0, height=3.0, color="#FFFFFF", stroke_width=2, fill_opacity=0.1).move_to([0, -1.0, 0])
        
        text_line1 = Text("THE CRYPTO ECOSYSTEM", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([0, -0.3, 0])
        text_line2 = Text("IS IMMENSE & GROWING", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, -1.0, 0])
        text_line3 = Text("INFINITE POSSIBILITIES", font="Arial", weight=NORMAL, font_size=12, color="#FFFFFF").move_to([0, -1.7, 0])
        
        self.play(Create(outer_box), run_time=2.0)
        self.play(FadeIn(text_line1), run_time=1.5)
        self.play(FadeIn(text_line2), run_time=1.5)
        self.play(FadeIn(text_line3), run_time=1.5)
        self.wait(1.1)

# Global Config

def setup_footer_and_title(scene, title_text, category_text="CRYPTO ECOSYSTEM"):
    # Bottom title placement
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Bottom footer bar & meta labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene17_08(Scene):
    def construct(self):
        setup_footer_and_title(self, "CRYPTO ECOSYSTEM: THE VAST NETWORK")
        
        # Literal illustration: Central server connected to multiple nodes (vast network)
        center_node = RoundedRectangle(corner_radius=0.15, width=1.2, height=1.2, stroke_width=2, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.2).move_to([0, -1.0, 0])
        center_text = Text("CORE", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(center_node.get_center())
        core_group = VGroup(center_node, center_text)
        
        satellites = VGroup()
        lines = VGroup()
        
        positions = [
            [-2.5, 1.2, 0], [0, 1.8, 0], [2.5, 1.2, 0],
            [-2.8, -0.2, 0], [2.8, -0.2, 0]
        ]
        
        for pos in positions:
            box = RoundedRectangle(corner_radius=0.1, width=0.8, height=0.6, stroke_width=1.5, color="#FFFFFF", fill_opacity=0.1).move_to(pos)
            line = Line(center_node.get_center(), box.get_center(), stroke_width=1, color="#FFFFFF").set_opacity(0.5)
            satellites.add(box)
            lines.add(line)
            
        self.play(FadeIn(core_group), run_time=1.0)
        self.play(Create(lines), FadeIn(satellites), run_time=2.5)
        
        # Pulsing expansion effect
        self.play(satellites.animate.scale(1.1), run_time=1.5)
        self.play(satellites.animate.scale(0.9), run_time=1.5)
        self.wait(1.1)

class Scene17_09(Scene):
    def construct(self):
        setup_footer_and_title(self, "EXPANDING NODES & PROTOCOLS")
        
        # Literal illustration: Expanding concentric rings of protocols
        rings = VGroup()
        for i in range(1, 5):
            ring = Circle(radius=0.7 * i, stroke_width=2, color="#FFFFFF").set_opacity(1.0 / i).move_to([0, -0.6, 0])
            rings.add(ring)
            
        core_dot = Circle(radius=0.3, stroke_width=2, color="#FFFFFF", fill_opacity=0.8).move_to([0, -0.6, 0])
        
        self.play(FadeIn(core_dot), run_time=1.0)
        self.play(Create(rings), run_time=4.0)
        
        # Rotate rings for dynamic ecosystem feel
        self.play(Rotate(rings, angle=PI/2, about_point=[0, -0.6, 0]), run_time=2.6)

class Scene17_10(Scene):
    def construct(self):
        setup_footer_and_title(self, "INTERCONNECTED BLOCKCHAINS")
        
        # Literal illustration: Three distinct blocks linked by data bridges
        block1 = RoundedRectangle(corner_radius=0.2, width=1.4, height=1.4, stroke_width=2, color="#FFFFFF", fill_opacity=0.15).move_to([-2.2, -0.6, 0])
        block2 = RoundedRectangle(corner_radius=0.2, width=1.4, height=1.4, stroke_width=2, color="#FFFFFF", fill_opacity=0.3).move_to([0, -0.6, 0])
        block3 = RoundedRectangle(corner_radius=0.2, width=1.4, height=1.4, stroke_width=2, color="#FFFFFF", fill_opacity=0.15).move_to([2.2, -0.6, 0])
        
        bridge1 = DoubleArrow(block1.get_right(), block2.get_left(), buff=0.1, stroke_width=2, color="#FFFFFF")
        bridge2 = DoubleArrow(block2.get_right(), block3.get_left(), buff=0.1, stroke_width=2, color="#FFFFFF")
        
        chain_group = VGroup(block1, block2, block3, bridge1, bridge2)
        
        t1 = Text("L1", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to(block1.get_center())
        t2 = Text("L2", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to(block2.get_center())
        t3 = Text("APP", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to(block3.get_center())
        
        text_group = VGroup(t1, t2, t3)
        
        self.play(FadeIn(chain_group), FadeIn(text_group), run_time=2.0)
        
        # Data flow simulation
        pulse = Circle(radius=0.2, color="#FFFFFF", stroke_width=2).move_to(block1.get_center())
        self.play(pulse.animate.move_to(block2.get_center()), run_time=1.5)
        self.play(pulse.animate.move_to(block3.get_center()), run_time=1.5)
        self.play(FadeOut(pulse), run_time=0.6)
        self.wait(2.0)

class Scene17_11(Scene):
    def construct(self):
        setup_footer_and_title(self, "DECENTRALIZED VAULTS & CONTRACTS")
        
        # Literal illustration: Safe / Vault door opening up
        vault_body = RoundedRectangle(corner_radius=0.2, width=3.0, height=2.2, stroke_width=2.5, color="#FFFFFF", fill_opacity=0.1).move_to([0, -0.6, 0])
        vault_dial = Circle(radius=0.5, stroke_width=2, color="#FFFFFF", fill_opacity=0.2).move_to([0, -0.6, 0])
        dial_center = Circle(radius=0.1, stroke_width=1, color="#FFFFFF", fill_opacity=1.0).move_to([0, -0.6, 0])
        
        handle = Line([0.8, -0.6, 0], [1.2, -0.6, 0], stroke_width=3, color="#FFFFFF")
        
        vault_group = VGroup(vault_body, vault_dial, dial_center, handle)
        
        self.play(DrawBorderThenFill(vault_body), run_time=1.5)
        self.play(FadeIn(vault_dial), FadeIn(dial_center), FadeIn(handle), run_time=1.5)
        
        # Rotating dial action
        self.play(Rotate(vault_dial, angle=2*PI, about_point=vault_dial.get_center()), run_time=3.0)
        self.wait(1.6)

class Scene17_12(Scene):
    def construct(self):
        setup_footer_and_title(self, "GLOBAL VALUE FLOWS")
        
        # Literal illustration: Globe grid with sweeping transaction arrows
        globe_circle = Circle(radius=1.8, stroke_width=2, color="#FFFFFF", fill_opacity=0.05).move_to([0, -0.6, 0])
        lat1 = Arc(radius=1.8, start_angle=0, angle=TAU, stroke_width=1, color="#FFFFFF").move_to([0, -0.6, 0])
        lat1.stretch_to_fit_height(1.0)
        lat2 = Arc(radius=1.8, start_angle=0, angle=TAU, stroke_width=1, color="#FFFFFF").move_to([0, -0.6, 0])
        lat2.stretch_to_fit_width(1.0)
        
        arrow1 = CurvedArrow([-1.5, 0.2, 0], [1.5, -1.4, 0], radius=2.0, stroke_width=2, color="#FFFFFF")
        arrow2 = CurvedArrow([1.5, 0.2, 0], [-1.5, -1.4, 0], radius=2.0, stroke_width=2, color="#FFFFFF")
        
        globe_group = VGroup(globe_circle, lat1, lat2, arrow1, arrow2)
        
        self.play(Create(globe_circle), run_time=1.5)
        self.play(FadeIn(lat1), FadeIn(lat2), run_time=1.5)
        self.play(GrowArrow(arrow1), GrowArrow(arrow2), run_time=3.0)
        self.wait(1.6)

class Scene17_13(Scene):
    def construct(self):
        setup_footer_and_title(self, "SCALE & ADOPTION METRICS")
        
        # Literal illustration: Bar chart rising dynamically
        baseline = Line([-2.5, -1.8, 0], [2.5, -1.8, 0], stroke_width=2, color="#FFFFFF")
        bar1 = Rectangle(width=0.6, height=1.2, stroke_width=2, color="#FFFFFF", fill_opacity=0.3).align_to(baseline, DOWN).shift(LEFT * 1.5)
        bar2 = Rectangle(width=0.6, height=2.2, stroke_width=2, color="#FFFFFF", fill_opacity=0.5).align_to(baseline, DOWN).shift(LEFT * 0.5)
        bar3 = Rectangle(width=0.6, height=3.0, stroke_width=2, color="#FFFFFF", fill_opacity=0.8).align_to(baseline, DOWN).shift(RIGHT * 0.7)
        
        chart_group = VGroup(baseline, bar1, bar2, bar3)
        
        self.play(Create(baseline), run_time=1.0)
        self.play(FadeIn(bar1, shift=UP), run_time=1.5)
        self.play(FadeIn(bar2, shift=UP), run_time=1.5)
        self.play(FadeIn(bar3, shift=UP), run_time=1.5)
        self.wait(1.1)

class Scene17_14(Scene):
    def construct(self):
        setup_footer_and_title(self, "THE VAST UNIVERSE OF CRYPTO")
        
        # Literal illustration: Expanding starfield / node cluster representing vastness
        dots = VGroup()
        import random
        random.seed(42)
        for _ in range(25):
            x = random.uniform(-3.0, 3.0)
            y = random.uniform(-2.2, 0.4)
            r = random.uniform(0.04, 0.12)
            dot = Circle(radius=r, stroke_width=1, color="#FFFFFF", fill_opacity=random.uniform(0.3, 1.0)).move_to([x, y, 0])
            dots.add(dot)
            
        central_hub = Circle(radius=0.4, stroke_width=2.5, color="#FFFFFF", fill_opacity=0.5).move_to([0, -0.9, 0])
        
        connecting_lines = VGroup()
        for dot in dots:
            if np.linalg.norm(dot.get_center() - central_hub.get_center()) < 2.0:
                line = Line(central_hub.get_center(), dot.get_center(), stroke_width=0.5, color="#FFFFFF").set_opacity(0.3)
                connecting_lines.add(line)
                
        universe = VGroup(connecting_lines, dots, central_hub)
        
        self.play(FadeIn(central_hub), run_time=1.0)
        self.play(FadeIn(dots), Create(connecting_lines), run_time=4.0)
        self.play(universe.animate.scale(1.05), run_time=1.5)
        self.wait(1.1)