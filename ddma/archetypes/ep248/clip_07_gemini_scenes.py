import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# CANVAS CONFIGURATION

def get_ui_elements(title_str, category_str):
    """Standardized UI elements for all scenes."""
    title = Text(title_str, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_str, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    return title, footer_line, left_text, right_text

class Scene07_01(Scene):
    def construct(self):
        # UI Setup
        title, footer, left, right = get_ui_elements("WHAT DO YOU MEAN", "COMMUNICATION")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Figurative Visual: Speech Bubbles
        bubble_left = RoundedRectangle(corner_radius=0.2, width=2.0, height=1.2, color="#FFFFFF", stroke_width=3).move_to([-1.5, -0.8, 0])
        bubble_right = RoundedRectangle(corner_radius=0.2, width=2.0, height=1.2, color="#FFFFFF", stroke_width=3).move_to([1.5, -0.8, 0])
        q_mark = Text("?", font="Arial", font_size=60, color="#FFFFFF").move_to([0, -0.8, 0])
        
        self.play(Create(bubble_left), Create(bubble_right), run_time=1.5)
        self.play(Write(q_mark), bubble_left.animate.shift(RIGHT*0.3), bubble_right.animate.shift(LEFT*0.3), run_time=2.0)
        self.play(q_mark.animate.scale(1.2).set_opacity(0.5), run_time=1.5)
        self.wait(2.0) # Total 7.6s

class Scene07_02(Scene):
    def construct(self):
        # UI Setup
        title, footer, left, right = get_ui_elements("WHAT DO YOU MEAN", "SEMANTICS")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Figurative Visual: Magnifying Glass over Text
        meaning_text = Text("MEANING", font="Arial", font_size=40, color="#FFFFFF").move_to([0, -1.0, 0])
        glass_circle = Circle(radius=0.6, color="#FFFFFF", stroke_width=4).move_to([-1.5, -1.0, 0])
        glass_handle = Line([-1.5, -1.0, 0], [-2.0, -1.5, 0], color="#FFFFFF", stroke_width=4).next_to(glass_circle, DL, buff=-0.1)
        magnifier = VGroup(glass_circle, glass_handle)

        self.play(Write(meaning_text), run_time=1.0)
        self.play(Create(magnifier), run_time=1.0)
        self.play(magnifier.animate.move_to([0, -1.0, 0]), run_time=3.0, rate_func=smooth)
        self.play(meaning_text.animate.scale(1.1), run_time=1.0)
        self.wait(1.0) # Total 7.6s

class Scene07_03(Scene):
    def construct(self):
        # UI Setup
        title, footer, left, right = get_ui_elements("WHAT DO YOU MEAN", "DIALOGUE")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Figurative Visual: Two heads with exchange arrows
        head1 = Circle(radius=0.5, color="#FFFFFF", stroke_width=3).move_to([-2, -1, 0])
        head2 = Circle(radius=0.5, color="#FFFFFF", stroke_width=3).move_to([2, -1, 0])
        arrow1 = Arrow(head1.get_right(), head2.get_left(), color="#FFFFFF", buff=0.2)
        arrow2 = Arrow(head2.get_left(), head1.get_right(), color="#FFFFFF", buff=0.2).shift(DOWN*0.3)
        arrow1.shift(UP*0.15)

        self.play(Create(head1), Create(head2), run_time=1.5)
        self.play(GrowArrow(arrow1), run_time=1.5)
        self.play(GrowArrow(arrow2), run_time=1.5)
        self.play(head1.animate.scale(1.1), head2.animate.scale(1.1), run_time=1.0)
        self.wait(1.5) # Total 7.6s

class Scene07_04(Scene):
    def construct(self):
        # UI Setup
        title, footer, left, right = get_ui_elements("WHAT DO YOU MEAN", "DEFINITION")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Figurative Visual: Open Dictionary
        page_l = Rectangle(width=1.5, height=2.0, color="#FFFFFF", stroke_width=3).move_to([-0.76, -1.0, 0])
        page_r = Rectangle(width=1.5, height=2.0, color="#FFFFFF", stroke_width=3).move_to([0.76, -1.0, 0])
        lines = VGroup(*[Line([-0.5, -0.5 - (i*0.3), 0], [0.5, -0.5 - (i*0.3), 0], color="#FFFFFF", stroke_width=1).set_opacity(0.5) for i in range(4)])
        lines.move_to(page_r.get_center())
        q_mark = Text("?", font="Arial", font_size=50, color="#FFFFFF").move_to(page_l.get_center())

        self.play(Create(page_l), Create(page_r), run_time=1.5)
        self.play(Write(lines), Write(q_mark), run_time=2.0)
        self.play(VGroup(page_l, page_r, lines, q_mark).animate.shift(UP*0.2), run_time=1.5)
        self.wait(2.0) # Total 7.6s

class Scene07_05(Scene):
    def construct(self):
        get_footer(self)
        # Visual: Show a pipe from Japan to San Francisco across pacific
        outer_frame = RoundedRectangle(width=4.4, height=2.6, corner_radius=0.18, color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0).move_to([0, -0.35, 0])
        core_hub = Circle(radius=0.72, color="#FFFFFF", stroke_width=5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([-1.05, -0.35, 0])
        target_node = RoundedRectangle(width=1.3, height=1.3, corner_radius=0.15, color="#FFFFFF", stroke_width=4, fill_color="#FFFFFF", fill_opacity=0.12).move_to([1.15, -0.35, 0])
        flow_arrow = Arrow(core_hub.get_right(), target_node.get_left(), buff=0.15, color="#FFFFFF", stroke_width=6)
        orbit_dot = Circle(radius=0.14, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to(core_hub.get_top())
        caption_lbl = Text("SHOW A PIPE FROM", font="Arial", weight=BOLD, font_size=13, color="#FFFFFF").move_to([0, -2.05, 0]).set_opacity(0.85)

        scene_grp = VGroup(outer_frame, core_hub, target_node, flow_arrow, orbit_dot, caption_lbl)
        self.play(Create(outer_frame), FadeIn(core_hub), FadeIn(target_node), GrowArrow(flow_arrow), FadeIn(orbit_dot), FadeIn(caption_lbl), run_time=1.6)
        self.play(
            Rotate(orbit_dot, angle=4*PI, about_point=core_hub.get_center()),
            target_node.animate.set_fill(opacity=0.45).scale(1.08),
            run_time=5.87,
            rate_func=linear
        )
        self.wait(0.8)

class Scene07_06(Scene):
    def construct(self):
        # UI Setup
        title, footer, left, right = get_ui_elements("WHAT DO YOU MEAN", "CLARITY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Figurative Visual: Puzzle Pieces
        piece1 = Square(side_length=1.2, color="#FFFFFF", stroke_width=3).move_to([-1.0, -1.0, 0])
        piece2 = Square(side_length=1.2, color="#FFFFFF", stroke_width=3).move_to([1.0, -1.0, 0])
        
        # Add "tabs" to make them look like puzzle pieces
        tab1 = Circle(radius=0.2, color="#FFFFFF", stroke_width=3, fill_opacity=1).move_to([-0.4, -1.0, 0])
        tab2 = Circle(radius=0.2, color="#000000", stroke_width=3, fill_opacity=1).move_to([0.4, -1.0, 0])
        
        p1 = VGroup(piece1, tab1)
        p2 = VGroup(piece2, tab2)

        self.play(FadeIn(p1, shift=RIGHT), FadeIn(p2, shift=LEFT), run_time=2.0)
        self.play(p1.animate.shift(RIGHT*0.3), p2.animate.shift(LEFT*0.3), run_time=2.0)
        self.play(p1.animate.scale(1.1), p2.animate.scale(1.1), run_time=1.0)
        self.wait(2.0) # Total 7.6s

class Scene07_07(Scene):
    def construct(self):
        # UI Setup
        title, footer, left, right = get_ui_elements("WHAT DO YOU MEAN", "BROADCAST")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Figurative Visual: Sound Waves / Signal
        center_q = Text("?", font="Arial", font_size=60, color="#FFFFFF").move_to([0, -1.0, 0])
        wave1 = Arc(radius=0.8, start_angle=-PI/4, angle=PI/2, color="#FFFFFF", stroke_width=2).move_to([0.5, -1.0, 0])
        wave2 = Arc(radius=1.2, start_angle=-PI/4, angle=PI/2, color="#FFFFFF", stroke_width=2).move_to([0.8, -1.0, 0])
        wave3 = Arc(radius=0.8, start_angle=3*PI/4, angle=PI/2, color="#FFFFFF", stroke_width=2).move_to([-0.5, -1.0, 0])
        wave4 = Arc(radius=1.2, start_angle=3*PI/4, angle=PI/2, color="#FFFFFF", stroke_width=2).move_to([-0.8, -1.0, 0])

        self.play(Write(center_q), run_time=1.0)
        self.play(Create(wave1), Create(wave3), run_time=1.5)
        self.play(Create(wave2), Create(wave4), run_time=1.5)
        self.play(VGroup(wave1, wave2, wave3, wave4).animate.set_opacity(0.3), run_time=1.0)
        self.wait(2.0) # Total 7.6s

# Global Configuration

# (Using universal get_footer_and_title from manim_compat)

class Scene07_08(Scene):
    def construct(self):
        # UI Elements
        title, footer_line, left_text, right_text = get_footer_and_title( "DIALOGUE EXCHANGE", "COMMUNICATION")
        
        # Figurative: Two speech bubbles facing each other
        bubble_l = RoundedRectangle(corner_radius=0.2, height=1.2, width=1.8, color=WHITE).move_to(LEFT * 1.5 + DOWN * 0.8)
        bubble_r = RoundedRectangle(corner_radius=0.2, height=1.2, width=1.8, color=WHITE).move_to(RIGHT * 1.5 + DOWN * 0.8)
        q_mark = Text("?", font="Arial", font_size=48, color=WHITE).move_to(bubble_l.get_center())
        a_mark = Text("!", font="Arial", font_size=48, color=WHITE).move_to(bubble_r.get_center())
        
        arrow_mid = DoubleArrow(bubble_l.get_right(), bubble_r.get_left(), color=WHITE, buff=0.2)

        # Animation
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(bubble_l), Create(bubble_r), run_time=1.5)
        self.play(Write(q_mark), Write(a_mark), run_time=1.5)
        self.play(GrowFromCenter(arrow_mid), run_time=1.0)
        self.play(arrow_mid.animate.set_stroke(width=8).set_stroke(width=2), run_time=2.0, rate_func=there_and_back)
        self.wait(1.0)

class Scene07_09(Scene):
    def construct(self):
        get_footer(self)
        # Visual: Instead of writing MEANING in the circle - write 'Loyalty'  .. implying that you are searching for loyalty with a magnifying glass !
        outer_frame = RoundedRectangle(width=4.4, height=2.6, corner_radius=0.18, color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0).move_to([0, -0.35, 0])
        core_hub = Circle(radius=0.72, color="#FFFFFF", stroke_width=5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([-1.05, -0.35, 0])
        target_node = RoundedRectangle(width=1.3, height=1.3, corner_radius=0.15, color="#FFFFFF", stroke_width=4, fill_color="#FFFFFF", fill_opacity=0.12).move_to([1.15, -0.35, 0])
        flow_arrow = Arrow(core_hub.get_right(), target_node.get_left(), buff=0.15, color="#FFFFFF", stroke_width=6)
        orbit_dot = Circle(radius=0.14, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to(core_hub.get_top())
        caption_lbl = Text("INSTEAD OF WRITING MEANING", font="Arial", weight=BOLD, font_size=13, color="#FFFFFF").move_to([0, -2.05, 0]).set_opacity(0.85)

        scene_grp = VGroup(outer_frame, core_hub, target_node, flow_arrow, orbit_dot, caption_lbl)
        self.play(Create(outer_frame), FadeIn(core_hub), FadeIn(target_node), GrowArrow(flow_arrow), FadeIn(orbit_dot), FadeIn(caption_lbl), run_time=1.6)
        self.play(
            Rotate(orbit_dot, angle=4*PI, about_point=core_hub.get_center()),
            target_node.animate.set_fill(opacity=0.45).scale(1.08),
            run_time=5.86,
            rate_func=linear
        )
        self.wait(0.8)

class Scene07_10(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "ACTIVE LISTENING", "COMMUNICATION")
        
        # Figurative: Ear icon and sound waves
        ear_outer = Arc(radius=0.7, start_angle=PI/2, angle=-1.5*PI, color=WHITE).move_to(LEFT * 1.2 + DOWN * 0.5)
        ear_inner = Arc(radius=0.3, start_angle=PI/2, angle=-PI, color=WHITE).move_to(ear_outer.get_center() + RIGHT*0.1)
        
        wave1 = Arc(radius=0.5, start_angle=-PI/4, angle=PI/2, color=WHITE).move_to(RIGHT * 0.5 + DOWN * 0.5)
        wave2 = Arc(radius=0.8, start_angle=-PI/4, angle=PI/2, color=WHITE).move_to(RIGHT * 0.8 + DOWN * 0.5)
        wave3 = Arc(radius=1.1, start_angle=-PI/4, angle=PI/2, color=WHITE).move_to(RIGHT * 1.1 + DOWN * 0.5)
        waves = VGroup(wave1, wave2, wave3)

        # Animation
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(ear_outer), Create(ear_inner), run_time=1.5)
        self.play(LaggedStart(*[Create(w) for w in waves], lag_ratio=0.3), run_time=2.0)
        self.play(waves.animate.shift(LEFT * 0.5).set_opacity(0), run_time=2.5, rate_func=linear)
        self.wait(1.0)

class Scene07_11(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "DEFINING TERMS", "COMMUNICATION")
        
        # Figurative: An open dictionary/book
        book_left = Rectangle(height=1.5, width=1.2, color=WHITE).move_to(LEFT * 0.6 + DOWN * 0.8)
        book_right = Rectangle(height=1.5, width=1.2, color=WHITE).move_to(RIGHT * 0.6 + DOWN * 0.8)
        lines_l = VGroup(*[Line(LEFT*1.0, LEFT*0.2, color=WHITE, stroke_width=1).move_to(book_left.get_center() + UP*(0.4 - i*0.2)) for i in range(4)])
        q_mark = Text("?", font="Arial", font_size=40, color=WHITE).move_to(book_right.get_center())

        # Animation
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(book_left), Create(book_right), run_time=1.5)
        self.play(Create(lines_l), Write(q_mark), run_time=2.0)
        self.play(book_left.animate.rotate(0.1, about_point=book_left.get_right()), book_right.animate.rotate(-0.1, about_point=book_right.get_left()), run_time=2.5)
        self.wait(1.0)

class Scene07_12(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "GROUP ANALYSIS", "COMMUNICATION")
        
        # Figurative: Four circles in a square connected by dashed lines
        c1 = Circle(radius=0.3, color=WHITE).move_to(UP*0.2 + LEFT*1.2)
        c2 = Circle(radius=0.3, color=WHITE).move_to(UP*0.2 + RIGHT*1.2)
        c3 = Circle(radius=0.3, color=WHITE).move_to(DOWN*1.5 + LEFT*1.2)
        c4 = Circle(radius=0.3, color=WHITE).move_to(DOWN*1.5 + RIGHT*1.2)
        
        l1 = DashedLine(c1.get_right(), c2.get_left(), color=WHITE)
        l2 = DashedLine(c2.get_bottom(), c4.get_top(), color=WHITE)
        l3 = DashedLine(c4.get_left(), c3.get_right(), color=WHITE)
        l4 = DashedLine(c3.get_top(), c1.get_bottom(), color=WHITE)
        l5 = DashedLine(c1.get_corner(DR), c4.get_corner(UL), color=WHITE)

        # Animation
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(LaggedStartMap(Create, VGroup(c1, c2, c3, c4), lag_ratio=0.2), run_time=1.5)
        self.play(Create(l1), Create(l2), Create(l3), Create(l4), Create(l5), run_time=2.5)
        self.play(VGroup(c1, c2, c3, c4).animate.scale(1.1), run_time=2.0)
        self.wait(1.0)

class Scene07_13(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "RESOLVING AMBIGUITY", "COMMUNICATION")
        
        # Figurative: A tangled line becoming a straight arrow
        tangle = VMobject(color=WHITE)
        tangle.set_points_as_corners([
            LEFT*2.5 + DOWN*0.5, LEFT*2.2 + UP*0.2, LEFT*1.9 + DOWN*0.8, 
            LEFT*1.6 + UP*0.4, LEFT*1.3 + DOWN*0.2, LEFT*1.0 + UP*0.1
        ])
        straight_line = Line(LEFT*1.0 + UP*0.1, RIGHT*2.0 + UP*0.1, color=WHITE)
        arrow_head = Arrow(LEFT*0.5 + UP*0.1, RIGHT*2.2 + UP*0.1, color=WHITE, buff=0)

        # Animation
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(tangle), run_time=1.5)
        self.play(Create(straight_line), run_time=2.0)
        self.play(ReplacementTransform(straight_line, arrow_head), run_time=1.5)
        self.play(tangle.animate.set_opacity(0.3), run_time=1.5)
        self.wait(0.5)

class Scene07_14(Scene):
    def construct(self):
        title, footer_line, left_text, right_text = get_footer_and_title( "SHARED UNDERSTANDING", "COMMUNICATION")
        
        # Figurative: Two puzzle pieces locking together
        piece1 = Polygon(
            [-1.5, 0, 0], [-0.5, 0, 0], [-0.5, 0.3, 0], [-0.2, 0.3, 0], 
            [-0.2, 0, 0], [0, 0, 0], [0, -1, 0], [-1.5, -1, 0],
            color=WHITE, stroke_width=4
        ).shift(LEFT * 0.5 + UP * 0.2)
        
        piece2 = Polygon(
            [0, 0, 0], [0.2, 0, 0], [0.2, 0.3, 0], [0.5, 0.3, 0], 
            [0.5, 0, 0], [1.5, 0, 0], [1.5, -1, 0], [0, -1, 0],
            color=WHITE, stroke_width=4
        ).shift(RIGHT * 0.5 + UP * 0.2)

        # Animation
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)
        self.play(piece1.animate.shift(RIGHT*0.3), piece2.animate.shift(LEFT*0.3), run_time=2.0)
        
        # Lock them
        lock_group = VGroup(piece1, piece2)
        self.play(lock_group.animate.move_to(ORIGIN + DOWN*0.5), run_time=2.0)
        
        # Final pulse
        self.play(lock_group.animate.scale(1.1), run_time=1.5)
        self.play(lock_group.animate.scale(1/1.1), run_time=1.5)