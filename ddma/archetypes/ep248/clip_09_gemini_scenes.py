import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Global Configuration

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

def get_title(scene, text="NEURAL NETWORK DISCUSSION"):
    title = Text(text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    return title

class Scene09_01(Scene):
    def construct(self):
        get_footer(self)
        get_title(self, "NEURAL NETWORK STRUCTURE")
        
        # Literal Neural Network: 3 layers
        l1 = VGroup(*[Circle(radius=0.2, color="#FFFFFF", stroke_width=2) for _ in range(3)]).arrange(DOWN, buff=0.4).shift(LEFT * 1.5 + DOWN * 1)
        l2 = VGroup(*[Circle(radius=0.2, color="#FFFFFF", stroke_width=2) for _ in range(4)]).arrange(DOWN, buff=0.3).shift(DOWN * 1)
        l3 = VGroup(*[Circle(radius=0.2, color="#FFFFFF", stroke_width=2) for _ in range(2)]).arrange(DOWN, buff=0.5).shift(RIGHT * 1.5 + DOWN * 1)
        
        connections = VGroup()
        for start in l1:
            for end in l2:
                connections.add(Line(start.get_right(), end.get_left(), stroke_width=1, color="#FFFFFF").set_opacity(0.4))
        for start in l2:
            for end in l3:
                connections.add(Line(start.get_right(), end.get_left(), stroke_width=1, color="#FFFFFF").set_opacity(0.4))

        self.play(Create(l1), Create(l2), Create(l3), run_time=2.0)
        self.play(Create(connections), run_time=3.0)
        self.play(l2.animate.scale(1.1).set_opacity(1), run_time=1.0)
        self.play(l2.animate.scale(1/1.1), run_time=1.0)

class Scene09_02(Scene):
    def construct(self):
        get_footer(self)
        get_title(self, "TALKING ABOUT THE NETWORK")
        
        # Two heads (circles) with speech lines
        head_l = Circle(radius=0.4, color="#FFFFFF", stroke_width=3).shift(LEFT * 2 + DOWN * 1)
        head_r = Circle(radius=0.4, color="#FFFFFF", stroke_width=3).shift(RIGHT * 2 + DOWN * 1)
        
        speech_l = VGroup(Line(ORIGIN, RIGHT*0.5), Line(ORIGIN, RIGHT*0.5).shift(UP*0.2)).next_to(head_l, RIGHT, buff=0.2).shift(UP*0.2)
        speech_r = VGroup(Line(ORIGIN, LEFT*0.5), Line(ORIGIN, LEFT*0.5).shift(UP*0.2)).next_to(head_r, LEFT, buff=0.2).shift(UP*0.2)
        
        network = VGroup(Circle(radius=0.15), Circle(radius=0.15).shift(UP*0.4), Circle(radius=0.15).shift(DOWN*0.4)).move_to(DOWN*1)
        for c in network: c.set_stroke(color="#FFFFFF", width=2)
        
        self.play(FadeIn(head_l), FadeIn(head_r), run_time=1.0)
        self.play(Create(network), run_time=2.0)
        for _ in range(2):
            self.play(Create(speech_l), Create(speech_r), run_time=1.0)
            self.play(FadeOut(speech_l), FadeOut(speech_r), run_time=1.0)

class Scene09_03(Scene):
    def construct(self):
        get_footer(self)
        get_title(self, "EXAMINING THE NEURONS")
        
        # Magnifying glass over a network
        network = VGroup(*[Circle(radius=0.1, color="#FFFFFF") for _ in range(12)]).arrange_in_grid(3, 4, buff=0.4).shift(DOWN * 1)
        glass_circle = Circle(radius=0.7, color="#FFFFFF", stroke_width=4).shift(LEFT * 1.5 + DOWN * 0.8)
        glass_handle = Line(glass_circle.get_bottom() + LEFT*0.1, glass_circle.get_bottom() + DOWN*0.5 + LEFT*0.5, color="#FFFFFF", stroke_width=4)
        magnifier = VGroup(glass_circle, glass_handle)
        
        self.play(FadeIn(network), run_time=1.5)
        self.play(FadeIn(magnifier), run_time=1.0)
        self.play(magnifier.animate.shift(RIGHT * 3), run_time=4.5, rate_func=smooth)

class Scene09_04(Scene):
    def construct(self):
        get_footer(self)
        get_title(self, "THE NEURAL BRAIN")
        
        # Brain silhouette made of nodes
        nodes = VGroup()
        for x in range(-3, 4):
            for y in range(-2, 3):
                if (x**2 + y**2) < 7:
                    nodes.add(Circle(radius=0.1, color="#FFFFFF", fill_opacity=0.2).move_to([x*0.4, y*0.4 - 1, 0]))
        
        lines = VGroup()
        for i in range(len(nodes)-1):
            if i % 3 == 0:
                lines.add(Line(nodes[i].get_center(), nodes[i+1].get_center(), color="#FFFFFF", stroke_width=0.5).set_opacity(0.3))

        self.play(Create(nodes), run_time=2.5)
        self.play(Create(lines), run_time=2.5)
        self.play(nodes.animate.set_opacity(0.8), run_time=1.0)
        self.play(nodes.animate.set_opacity(0.2), run_time=1.0)

class Scene09_05(Scene):
    def construct(self):
        get_footer(self)
        get_title(self, "POINTING TO THE MODEL")
        
        # A hand pointing at a central node
        central_node = Circle(radius=0.5, color="#FFFFFF", stroke_width=3).shift(DOWN * 1)
        outer_nodes = VGroup(*[Circle(radius=0.2, color="#FFFFFF").move_to([cos(a)*1.5, sin(a)*1.5 - 1, 0]) for a in np.linspace(0, 2*PI, 7)])
        
        hand_palm = RoundedRectangle(height=0.6, width=0.4, corner_radius=0.1, color="#FFFFFF").shift(RIGHT*2.5 + DOWN*0.5)
        hand_finger = Rectangle(height=0.1, width=0.6, color="#FFFFFF").next_to(hand_palm, LEFT, buff=0)
        hand = VGroup(hand_palm, hand_finger).rotate(PI/12)

        self.play(Create(central_node), Create(outer_nodes), run_time=2.0)
        self.play(hand.animate.shift(LEFT * 1.2), run_time=2.0)
        self.play(central_node.animate.scale(1.2).set_stroke(width=6), run_time=1.0)
        self.play(central_node.animate.scale(1/1.2).set_stroke(width=3), run_time=2.0)

class Scene09_06(Scene):
    def construct(self):
        get_footer(self)
        get_title(self, "DATA FLOWING THROUGH")
        
        # Network with arrows passing through
        box = Rectangle(height=1.5, width=2.5, color="#FFFFFF", stroke_width=2).shift(DOWN * 1)
        nodes = VGroup(*[Circle(radius=0.1, color="#FFFFFF") for _ in range(6)]).arrange_in_grid(2, 3, buff=0.4).move_to(box)
        
        arrows = VGroup(*[Arrow(LEFT*3, LEFT*1.5, color="#FFFFFF", stroke_width=2, max_tip_length_to_length_ratio=0.2).shift(UP*y + DOWN*1) for y in [-0.4, 0, 0.4]])
        
        self.play(Create(box), Create(nodes), run_time=2.0)
        self.play(LaggedStart(*[a.animate.shift(RIGHT*5) for a in arrows], lag_ratio=0.3), run_time=5.0)

class Scene09_07(Scene):
    def construct(self):
        get_footer(self)
        get_title(self, "GROUP DISCUSSION")
        
        # Circle of figures around a network
        center_net = VGroup(Circle(radius=0.3), Circle(radius=0.3).shift(LEFT*0.4), Circle(radius=0.3).shift(RIGHT*0.4)).move_to(DOWN*1)
        for c in center_net: c.set_stroke(color="#FFFFFF", width=2)
        
        figures = VGroup()
        for i in range(6):
            angle = i * 60 * DEGREES
            fig = VGroup(Circle(radius=0.15), Arc(radius=0.25, start_angle=0, angle=PI, color="#FFFFFF")).arrange(DOWN, buff=0.05)
            fig.move_to([cos(angle)*1.8, sin(angle)*1.2 - 1, 0])
            figures.add(fig)
            
        self.play(FadeIn(center_net), run_time=1.5)
        self.play(Create(figures), run_time=3.0)
        self.play(figures.animate.shift(UP*0.1), run_time=1.0)
        self.play(figures.animate.shift(DOWN*0.1), run_time=1.5)