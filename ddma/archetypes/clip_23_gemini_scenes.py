import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Configure canvas precisely

def setup_footer_and_title(scene, title_text):
    # Bottom Title (y = -2.95)
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("RADICAL REFRAMING", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene23_01(Scene):
    def construct(self):
        setup_footer_and_title(self, "IT IS A RADICAL REFRAMING")
        
        # Literal figurative visual: A large brain outline flipping upside down (reframing)
        brain_box = RoundedRectangle(corner_radius=0.5, width=3.5, height=2.5, color="#FFFFFF", stroke_width=2.5)
        brain_box.move_to([0, -1.0, 0])
        
        # Internal neural nodes inside the box
        nodes = VGroup(*[
            Circle(radius=0.1, color="#FFFFFF", fill_opacity=0.8).move_to([x, y, 0])
            for x, y in [[-1, 0], [1, 0], [0, 0.8], [-0.8, -0.8], [0.8, -0.8]]
        ])
        nodes.shift(DOWN * 1.0)
        
        lines = VGroup(
            Line(nodes[0].get_center(), nodes[2].get_center(), color="#FFFFFF", stroke_width=1.5),
            Line(nodes[1].get_center(), nodes[2].get_center(), color="#FFFFFF", stroke_width=1.5),
            Line(nodes[0].get_center(), nodes[3].get_center(), color="#FFFFFF", stroke_width=1.5),
            Line(nodes[1].get_center(), nodes[4].get_center(), color="#FFFFFF", stroke_width=1.5),
        )
        
        brain_group = VGroup(brain_box, nodes, lines)
        
        # Rotation arrows indicating "reframing"
        reframing_arrow = CurvedArrow(start_point=LEFT*2.2 + DOWN*0.5, end_point=RIGHT*2.2 + DOWN*0.5, radius=2.0, color="#FFFFFF", stroke_width=2)
        reframing_arrow_back = CurvedArrow(start_point=RIGHT*2.2 + DOWN*1.5, end_point=LEFT*2.2 + DOWN*1.5, radius=2.0, color="#FFFFFF", stroke_width=2)
        
        self.play(FadeIn(brain_group, shift=UP*0.5), run_time=1.5)
        self.play(Create(reframing_arrow), Create(reframing_arrow_back), run_time=2.0)
        self.play(brain_group.animate.rotate(PI), run_time=3.0)
        self.wait(0.5)

class Scene23_02(Scene):
    def construct(self):
        setup_footer_and_title(self, "WHAT INTELLIGENCE MEANS")
        
        # Literal figurative visual: Balance scale of intelligence vs old paradigm
        pivot = Triangle(color="#FFFFFF", fill_opacity=0.3).scale(0.5).move_to([0, -1.8, 0])
        beam = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=3).move_to([0, -1.2, 0])
        
        pan_left = VGroup(
            Line(LEFT*2.5, LEFT*2.5 + DOWN*1, color="#FFFFFF", stroke_width=2),
            Circle(radius=0.6, color="#FFFFFF", fill_opacity=0.2).move_to(LEFT*2.5 + DOWN*1)
        ).move_to(LEFT*2.5 + UP*0.5) # Wait, let's keep it simpler
        
        # Simple clean scales
        scale_line = Line(UP*0.5, DOWN*2.2, color="#FFFFFF", stroke_width=3).move_to([0, -0.5, 0])
        cross_bar = Line(LEFT*2.5, RIGHT*2.5, color="#FFFFFF", stroke_width=3).move_to([0, 0.5, 0])
        
        left_pan = VGroup(
            Line(LEFT*2.5, LEFT*2.5 + DOWN*1.5, color="#FFFFFF", stroke_width=2),
            Arc(radius=1.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2).move_to(LEFT*2.5 + DOWN*1.5)
        )
        right_pan = VGroup(
            Line(RIGHT*2.5, RIGHT*2.5 + DOWN*1.5, color="#FFFFFF", stroke_width=2),
            Arc(radius=1.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2).move_to(RIGHT*2.5 + DOWN*1.5)
        )
        
        scale = VGroup(scale_line, cross_bar, left_pan, right_pan).move_to([0, -0.8, 0])
        
        # Lightbulb on right pan (Intelligence)
        bulb = Circle(radius=0.4, color="#FFFFFF", fill_opacity=0.7).move_to([2.5, -1.2, 0])
        
        self.play(Create(scale), run_time=2.0)
        self.play(FadeIn(bulb, shift=UP*0.5), run_time=1.5)
        self.play(scale.animate.rotate(0.2, about_point=[0, -0.3, 0]), run_time=1.5)
        self.play(scale.animate.rotate(-0.4, about_point=[0, -0.3, 0]), run_time=1.5)
        self.wait(0.7)

class Scene23_03(Scene):
    def construct(self):
        setup_footer_and_title(self, "SHIFTING PERSPECTIVES")
        
        # Literal figurative visual: Shifting lens / magnifying glass focusing on a core concept
        handle = Line(ORIGIN, DOWN*1.5, color="#FFFFFF", stroke_width=5).move_to([1.5, -1.8, 0])
        handle.rotate(-PI/4, about_point=[1.5, -1.0, 0])
        
        lens_rim = Circle(radius=1.5, color="#FFFFFF", stroke_width=4).move_to([0, -0.5, 0])
        
        # Inside lens: grid transforming
        grid = VGroup(*[
            Line(LEFT*1.2 + DOWN*y, RIGHT*1.2 + DOWN*y, color="#FFFFFF", stroke_width=1).set_opacity(0.5)
            for y in [-0.8, -0.4, 0, 0.4, 0.8]
        ]).move_to([0, -0.5, 0])
        
        lens_group = VGroup(lens_rim, grid, handle)
        
        self.play(FadeIn(lens_group, scale=0.5), run_time=2.0)
        self.play(lens_group.animate.shift(LEFT * 1.5), run_time=1.8)
        self.play(lens_group.animate.shift(RIGHT * 3.0), run_time=1.8)
        self.play(lens_group.animate.shift(LEFT * 1.5), run_time=1.5)
        self.wait(0.5)

class Scene23_04(Scene):
    def construct(self):
        setup_footer_and_title(self, "DEEP COGNITIVE SHIFT")
        
        # Literal figurative visual: Layers of blocks flipping over sequentially
        blocks = VGroup(*[
            RoundedRectangle(corner_radius=0.2, width=4.0, height=0.6, color="#FFFFFF", stroke_width=2, fill_opacity=0.2)
            for _ in range(4)
        ]).arrange(DOWN, buff=0.3).move_to([0, -0.8, 0])
        
        self.play(FadeIn(blocks, lag_ratio=0.3), run_time=2.0)
        
        # Flip blocks one by one
        for i in range(4):
            self.play(blocks[i].animate.rotate(PI, axis=UP), run_time=1.0)
            
        self.wait(0.6)

class Scene23_05(Scene):
    def construct(self):
        setup_footer_and_title(self, "EXPANDING DEFINITIONS")
        
        # Literal figurative visual: Expanding boundary box (scaling up)
        core_box = Square(side_length=1.0, color="#FFFFFF", stroke_width=2, fill_opacity=0.4).move_to([0, -0.8, 0])
        outer_box_1 = Square(side_length=2.2, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to([0, -0.8, 0])
        outer_box_2 = Square(side_length=3.4, color="#FFFFFF", stroke_width=2, fill_opacity=0.1).move_to([0, -0.8, 0])
        
        expansion_group = VGroup(core_box, outer_box_1, outer_box_2)
        
        self.play(FadeIn(core_box), run_time=1.5)
        self.play(GrowFromCenter(outer_box_1), run_time=2.0)
        self.play(GrowFromCenter(outer_box_2), run_time=2.0)
        self.play(expansion_group.animate.scale(1.1), run_time=1.1)
        self.wait(1.0)

class Scene23_06(Scene):
    def construct(self):
        setup_footer_and_title(self, "THE NEW PARADIGM")
        
        # Literal figurative visual: A central glowing core with incoming and outgoing data streams
        core_circle = Circle(radius=0.8, color="#FFFFFF", fill_opacity=0.8).move_to([0, -0.8, 0])
        
        incoming_arrows = VGroup(*[
            Arrow(start=ORIGIN, end=ORIGIN, color="#FFFFFF", stroke_width=2)
            for _ in range(4)
        ])
        
        incoming_arrows[0].put_start_and_end_on(LEFT*3.5 + UP*0.5, LEFT*0.9 + DOWN*0.8)
        incoming_arrows[1].put_start_and_end_on(LEFT*3.5 + DOWN*2.1, LEFT*0.9 + DOWN*0.8)
        incoming_arrows[2].put_start_and_end_on(RIGHT*3.5 + UP*0.5, RIGHT*0.9 + DOWN*0.8)
        incoming_arrows[3].put_start_and_end_on(RIGHT*3.5 + DOWN*2.1, RIGHT*0.9 + DOWN*0.8)
        
        self.play(FadeIn(core_circle, scale=0.2), run_time=1.5)
        self.play(Create(incoming_arrows, lag_ratio=0.2), run_time=3.0)
        self.play(core_circle.animate.set_fill(opacity=0.2), run_time=1.5)
        self.play(core_circle.animate.set_fill(opacity=0.9), run_time=1.0)
        self.wait(0.6)

class Scene23_07(Scene):
    def construct(self):
        setup_footer_and_title(self, "INTELLIGENCE REDEFINED")
        
        # Literal figurative visual: A soaring vector arrow breaking through an upper ceiling barrier
        barrier = Line(LEFT*3.0, RIGHT*3.0, color="#FFFFFF", stroke_width=3).move_to([0, 0.2, 0])
        barrier_label = Text("OLD LIMIT", font="Arial", font_size=10, color="#FFFFFF").set_opacity(0.6).next_to(barrier, UP, buff=0.1)
        
        soaring_arrow = Arrow(start=[0, -2.2, 0], end=[0, 1.8, 0], color="#FFFFFF", stroke_width=4, buff=0)
        
        # Sparks/fragments at the barrier break point
        sparks = VGroup(*[
            Line(ORIGIN, [0.3 * (-1)**i, 0.3 * i, 0], color="#FFFFFF", stroke_width=2)
            for i in range(6)
        ]).move_to([0, 0.2, 0])
        
        self.play(Create(barrier), FadeIn(barrier_label), run_time=1.5)
        self.play(GrowArrow(soaring_arrow), run_time=2.5)
        self.play(FadeIn(sparks, scale=1.5), run_time=1.0)
        self.play(soaring_arrow.animate.scale(1.1), run_time=1.5)
        self.wait(1.1)

# Configure canvas strictly

def add_base_elements(scene, category_text):
    """Adds the mandatory bottom title, footer line, and meta labels."""
    title = Text("RADICAL REFRAMING OF INTELLIGENCE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.4)
    
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

class Scene23_08(Scene):
    def construct(self):
        add_base_elements(self, "COGNITIVE SHIFT")
        
        # Literal figurative visual: Old brain/box flipping into a new bright structure (Reframing)
        box_old = Rectangle(width=2.5, height=2.5, color="#FFFFFF", stroke_width=3).move_to([-1.5, -0.8, 0])
        box_old.set_fill("#FFFFFF", opacity=0.1)
        text_old = Text("OLD", font="Arial", font_size=16, color="#FFFFFF").move_to(box_old.get_center())
        
        arrow = Arrow(start=LEFT*0.8, end=RIGHT*0.8, color="#FFFFFF", stroke_width=3).move_to([0, -0.8, 0])
        
        box_new = Rectangle(width=2.5, height=2.5, color="#FFFFFF", stroke_width=4).move_to([1.5, -0.8, 0])
        box_new.set_fill("#FFFFFF", opacity=0.3)
        text_new = Text("NEW", font="Arial", weight=BOLD, font_size=18, color="#FFFFFF").move_to(box_new.get_center())
        
        group = VGroup(box_old, text_old, arrow, box_new, text_new).move_to([0, -1.0, 0])
        
        self.play(FadeIn(group, shift=UP*0.5), run_time=1.5)
        self.play(box_new.animate.scale(1.08), run_time=1.0)
        self.play(box_new.animate.scale(1.0), run_time=1.0)
        self.wait(3.7)

class Scene23_09(Scene):
    def construct(self):
        add_base_elements(self, "STRUCTURAL FLIP")
        
        # Literal figurative visual: A balance scale completely inverting upside down
        pivot = Circle(radius=0.1, color="#FFFFFF", fill_opacity=1).move_to([0, -1.0, 0])
        beam = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=4).move_to([0, -1.0, 0])
        
        pan_left = Circle(radius=0.6, color="#FFFFFF", stroke_width=2).move_to([-2.5, -1.8, 0])
        pan_right = Circle(radius=0.6, color="#FFFFFF", stroke_width=2).move_to([2.5, -0.2, 0])
        
        scale_group = VGroup(pivot, beam, pan_left, pan_right)
        
        self.play(FadeIn(scale_group), run_time=1.0)
        self.play(Rotate(scale_group, angle=PI, about_point=pivot.get_center()), run_time=2.0)
        self.wait(4.2)

class Scene23_10(Scene):
    def construct(self):
        add_base_elements(self, "CORE ARCHITECTURE")
        
        # Literal figurative visual: Central processing server grid with glowing core
        grid = VGroup(*[
            Rectangle(width=1.2, height=1.2, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.15)
            for _ in range(4)
        ]).arrange_in_grid(rows=2, cols=2, buff=0.3).move_to([0, -1.0, 0])
        
        core_circle = Circle(radius=0.8, color="#FFFFFF", stroke_width=3).set_fill("#FFFFFF", opacity=0.4).move_to([0, -1.0, 0])
        core_text = Text("AI", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to([0, -1.0, 0])
        
        self.play(FadeIn(grid), run_time=1.0)
        self.play(FadeIn(core_circle), FadeIn(core_text), run_time=1.0)
        self.play(grid.animate.set_opacity(0.8), run_time=1.5)
        self.wait(4.1)

class Scene23_11(Scene):
    def construct(self):
        add_base_elements(self, "PARADIGM SHIFT")
        
        # Literal figurative visual: Two massive colliding/merging rectangular frames representing radical reframing
        rect1 = Rectangle(width=3.0, height=2.0, color="#FFFFFF", stroke_width=3).move_to([-1.0, -1.0, 0])
        rect2 = Rectangle(width=3.0, height=2.0, color="#FFFFFF", stroke_width=3).move_to([1.0, -1.0, 0])
        rect1.set_fill("#FFFFFF", opacity=0.1)
        rect2.set_fill("#FFFFFF", opacity=0.2)
        
        intersec = Rectangle(width=1.5, height=2.0, color="#FFFFFF", stroke_width=4).set_fill("#FFFFFF", opacity=0.5).move_to([0, -1.0, 0])
        
        self.play(FadeIn(rect1, shift=RIGHT*0.5), FadeIn(rect2, shift=LEFT*0.5), run_time=1.5)
        self.play(FadeIn(intersec, scale=0.5), run_time=1.5)
        self.wait(4.6)

class Scene23_12(Scene):
    def construct(self):
        add_base_elements(self, "INTELLIGENCE MATRIX")
        
        # Literal figurative visual: Expanding geometric lattice of intelligence nodes
        nodes = VGroup(*[
            Circle(radius=0.3, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.3)
            for _ in range(6)
        ]).arrange(RIGHT, buff=0.8).move_to([0, -1.0, 0])
        
        lines = VGroup(*[
            Line(nodes[i].get_center(), nodes[i+1].get_center(), color="#FFFFFF", stroke_width=2)
            for i in range(5)
        ])
        
        matrix_group = VGroup(lines, nodes)
        
        self.play(Create(lines), run_time=1.5)
        self.play(FadeIn(nodes, scale=0.5), run_time=1.5)
        self.play(matrix_group.animate.scale(1.1), run_time=1.0)
        self.wait(3.6)

class Scene23_13(Scene):
    def construct(self):
        add_base_elements(self, "DEEP RESTRUCTURING")
        
        # Literal figurative visual: Concentric rotating square layers
        sq1 = Square(side_length=3.0, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.05).move_to([0, -1.0, 0])
        sq2 = Square(side_length=2.0, color="#FFFFFF", stroke_width=3).set_fill("#FFFFFF", opacity=0.15).move_to([0, -1.0, 0])
        sq3 = Square(side_length=1.0, color="#FFFFFF", stroke_width=4).set_fill("#FFFFFF", opacity=0.35).move_to([0, -1.0, 0])
        
        self.play(FadeIn(sq1), run_time=1.0)
        self.play(FadeIn(sq2), Rotate(sq1, angle=PI/4), run_time=1.5)
        self.play(FadeIn(sq3), Rotate(sq2, angle=-PI/4), run_time=1.5)
        self.wait(3.6)

class Scene23_14(Scene):
    def construct(self):
        add_base_elements(self, "COMPLETE SYNTHESIS")
        
        # Literal figurative visual: Unfolding cube/box representing the fully reframed concept
        outer_box = RoundedRectangle(corner_radius=0.2, width=3.5, height=2.5, color="#FFFFFF", stroke_width=4)
        outer_box.set_fill("#FFFFFF", opacity=0.2).move_to([0, -1.0, 0])
        
        inner_line_1 = Line([-1.2, -0.1, 0], [1.2, -1.9, 0], color="#FFFFFF", stroke_width=2)
        inner_line_2 = Line([-1.2, -1.9, 0], [1.2, -0.1, 0], color="#FFFFFF", stroke_width=2)
        
        center_node = Circle(radius=0.4, color="#FFFFFF", stroke_width=3).set_fill("#FFFFFF", opacity=0.8).move_to([0, -1.0, 0])
        
        synthesis_group = VGroup(outer_box, inner_line_1, inner_line_2, center_node)
        
        self.play(FadeIn(outer_box, scale=0.8), run_time=1.5)
        self.play(Create(inner_line_1), Create(inner_line_2), run_time=1.5)
        self.play(FadeIn(center_node, scale=0.5), run_time=1.0)
        self.wait(3.6)

# Configure canvas & resolution globally

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

    """Utility to set up the bottom title, footer line, and meta labels consistently."""
    # Bottom Title (y = -2.95)
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

class Scene23_15(Scene):
    def construct(self):
        setup_base_scene(self, "RADICAL REFRAMING OF INTELLIGENCE", "INTELLIGENCE RE-EXAMINED")
        
        # Literal illustration: A classic brain silhouette / network splitting and reframing inside a massive frame
        frame = RoundedRectangle(corner_radius=0.2, width=5.0, height=3.5, stroke_width=2.5, color="#FFFFFF").move_to([0, -1.0, 0])
        frame.set_fill("#FFFFFF", opacity=0.05)
        
        # Internal nodes representing intelligence reframing
        node1 = Circle(radius=0.3, stroke_width=2, color="#FFFFFF").move_to([-1.2, -0.5, 0])
        node2 = Circle(radius=0.3, stroke_width=2, color="#FFFFFF").move_to([1.2, -0.5, 0])
        core_node = RoundedRectangle(corner_radius=0.1, width=1.2, height=0.8, stroke_width=2, color="#FFFFFF").move_to([0, -1.5, 0])
        
        conn1 = Line(node1.get_center(), core_node.get_center(), stroke_width=2, color="#FFFFFF")
        conn2 = Line(node2.get_center(), core_node.get_center(), stroke_width=2, color="#FFFFFF")
        
        # Radical shift arrows pointing outwards
        arrow_left = Arrow(start=[-0.5, -0.5, 0], end=[-2.0, -0.5, 0], stroke_width=2, buff=0, color="#FFFFFF")
        arrow_right = Arrow(start=[0.5, -0.5, 0], end=[2.0, -0.5, 0], stroke_width=2, buff=0, color="#FFFFFF")
        
        group = VGroup(frame, node1, node2, core_node, conn1, conn2, arrow_left, arrow_right)
        
        self.play(Create(frame), run_time=1.0)
        self.play(FadeIn(node1), FadeIn(node2), FadeIn(core_node), run_time=1.0)
        self.play(Create(conn1), Create(conn2), run_time=1.0)
        self.play(GrowArrow(arrow_left), GrowArrow(arrow_right), run_time=1.5)
        self.wait(2.5)

class Scene23_16(Scene):
    def construct(self):
        setup_base_scene(self, "SHIFTING THE CORE PARADIGM", "PARADIGM SHIFT")
        
        # Literal illustration: A heavy balance scale pivoting dramatically
        fulcrum = Polygon([0, -2.0, 0], [-0.5, -2.6, 0], [0.5, -2.6, 0], stroke_width=2, color="#FFFFFF").set_fill("#FFFFFF", opacity=0.2)
        beam = Line(LEFT * 2.5, RIGHT * 2.5, stroke_width=3, color="#FFFFFF").move_to([0, -1.2, 0])
        
        # Pans
        pan_left = VGroup(
            Line(LEFT * 2.5, LEFT * 2.5 + DOWN * 1.0, stroke_width=2, color="#FFFFFF"),
            Arc(radius=0.8, start_angle=PI, angle=PI, stroke_width=2, color="#FFFFFF").move_to([-2.5, -2.2, 0])
        ).move_to([-2.5, -1.7, 0])
        
        pan_right = VGroup(
            Line(RIGHT * 2.5, RIGHT * 2.5 + UP * 1.0, stroke_width=2, color="#FFFFFF"),
            Arc(radius=0.8, start_angle=PI, angle=PI, stroke_width=2, color="#FFFFFF").move_to([2.5, -0.2, 0])
        ).move_to([2.5, -0.7, 0])
        
        # Tilt beam animation group
        scale_group = VGroup(beam, pan_left, pan_right).move_to([0, -1.2, 0])
        
        self.play(FadeIn(fulcrum), Create(scale_group), run_time=1.5)
        self.play(scale_group.animate.rotate(0.35, about_point=[0, -1.2, 0]), run_time=2.0)
        self.play(scale_group.animate.rotate(-0.7, about_point=[0, -1.2, 0]), run_time=2.0)
        self.wait(1.1)

class Scene23_17(Scene):
    def construct(self):
        setup_base_scene(self, "DECONSTRUCTING OLD MODELS", "MODEL ANALYSIS")
        
        # Literal illustration: A structured block diagram being pulled apart
        box1 = Rectangle(width=1.5, height=1.0, stroke_width=2, color="#FFFFFF").move_to([-2.0, -1.0, 0]).set_fill("#FFFFFF", opacity=0.1)
        box2 = Rectangle(width=1.5, height=1.0, stroke_width=2, color="#FFFFFF").move_to([0, -1.0, 0]).set_fill("#FFFFFF", opacity=0.1)
        box3 = Rectangle(width=1.5, height=1.0, stroke_width=2, color="#FFFFFF").move_to([2.0, -1.0, 0]).set_fill("#FFFFFF", opacity=0.1)
        
        conn_line1 = Line(box1.get_right(), box2.get_left(), stroke_width=2, color="#FFFFFF")
        conn_line2 = Line(box2.get_right(), box3.get_left(), stroke_width=2, color="#FFFFFF")
        
        # Explode arrows
        exp_left = Arrow(start=[-2.5, 0.2, 0], end=[-3.5, 0.2, 0], stroke_width=2, color="#FFFFFF")
        exp_right = Arrow(start=[2.5, 0.2, 0], end=[3.5, 0.2, 0], stroke_width=2, color="#FFFFFF")
        
        self.play(Create(box1), Create(box2), Create(box3), run_time=1.5)
        self.play(Create(conn_line1), Create(conn_line2), run_time=1.0)
        self.play(box1.animate.shift(LEFT * 0.5), box3.animate.shift(RIGHT * 0.5), run_time=1.5)
        self.play(GrowArrow(exp_left), GrowArrow(exp_right), run_time=1.5)
        self.wait(1.1)

class Scene23_18(Scene):
    def construct(self):
        setup_base_scene(self, "THE NEW ARCHITECTURE", "NEW BLUEPRINT")
        
        # Literal illustration: A futuristic multi-tier network pyramid or server rack stack
        base_rect = RoundedRectangle(corner_radius=0.1, width=5.0, height=0.8, stroke_width=2, color="#FFFFFF").move_to([0, -2.0, 0]).set_fill("#FFFFFF", opacity=0.1)
        mid_rect = RoundedRectangle(corner_radius=0.1, width=3.8, height=0.8, stroke_width=2, color="#FFFFFF").move_to([0, -1.0, 0]).set_fill("#FFFFFF", opacity=0.2)
        top_rect = RoundedRectangle(corner_radius=0.1, width=2.4, height=0.8, stroke_width=2, color="#FFFFFF").move_to([0, 0.0, 0]).set_fill("#FFFFFF", opacity=0.3)
        
        # Vertical connecting flow lines
        v_line1 = DashedLine(start=[0, -1.6, 0], end=[0, -1.0, 0], stroke_width=2, color="#FFFFFF")
        v_line2 = DashedLine(start=[0, -0.6, 0], end=[0, 0.0, 0], stroke_width=2, color="#FFFFFF")
        
        self.play(FadeIn(base_rect), run_time=1.0)
        self.play(Create(v_line1), FadeIn(mid_rect), run_time=1.5)
        self.play(Create(v_line2), FadeIn(top_rect), run_time=1.5)
        
        # Pulse highlight effect (simulated via scaling up slightly)
        self.play(
            base_rect.animate.scale(1.03),
            mid_rect.animate.scale(1.03),
            top_rect.animate.scale(1.03),
            run_time=1.0
        )
        self.play(
            base_rect.animate.scale(1/1.03),
            mid_rect.animate.scale(1/1.03),
            top_rect.animate.scale(1/1.03),
            run_time=1.0
        )
        self.wait(0.6)

class Scene23_19(Scene):
    def construct(self):
        setup_base_scene(self, "SYNTHESIS & EXPANSION", "COMPREHENSIVE VIEW")
        
        # Literal illustration: Expanding concentric intelligence rings radiating outward
        center_circle = Circle(radius=0.4, stroke_width=2, color="#FFFFFF").move_to([0, -1.0, 0]).set_fill("#FFFFFF", opacity=0.3)
        ring_1 = Circle(radius=1.5, stroke_width=2, color="#FFFFFF").move_to([0, -1.0, 0])
        ring_1.set_opacity(0.6)
        ring_2 = Circle(radius=2.8, stroke_width=1.5, color="#FFFFFF").move_to([0, -1.0, 0])
        ring_2.set_opacity(0.3)
        
        # Expanding vector nodes along the outer ring
        node_top = Circle(radius=0.15, stroke_width=2, color="#FFFFFF").move_to([0, 1.8, 0]).set_fill("#FFFFFF", opacity=1.0)
        node_left = Circle(radius=0.15, stroke_width=2, color="#FFFFFF").move_to([-2.8, -1.0, 0]).set_fill("#FFFFFF", opacity=1.0)
        node_right = Circle(radius=0.15, stroke_width=2, color="#FFFFFF").move_to([2.8, -1.0, 0]).set_fill("#FFFFFF", opacity=1.0)
        
        ray_top = Line([0, -0.6, 0], [0, 1.65, 0], stroke_width=1.5, color="#FFFFFF")
        ray_left = Line([-1.5, -1.0, 0], [-2.65, -1.0, 0], stroke_width=1.5, color="#FFFFFF")
        ray_right = Line([1.5, -1.0, 0], [2.65, -1.0, 0], stroke_width=1.5, color="#FFFFFF")
        
        self.play(FadeIn(center_circle), run_time=1.0)
        self.play(Create(ring_1), run_time=1.5)
        self.play(Create(ring_2), run_time=1.5)
        self.play(Create(ray_top), Create(ray_left), Create(ray_right), run_time=1.0)
        self.play(FadeIn(node_top), FadeIn(node_left), FadeIn(node_right), run_time=1.0)
        self.wait(1.6)