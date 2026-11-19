import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Configuration for 740x740 monochrome output

# (Using universal get_footer_and_title from manim_compat)

class Scene03_01(Scene):
    def construct(self):
        # UI Elements
        title, footer, left_meta, right_meta = get_footer_and_title( "DISCUSSION ON TEENAGED AI", "ARTIFICIAL INTELLIGENCE")
        self.add(footer, left_meta, right_meta)
        
        # Visual: Robot with a backwards baseball cap (Teenager trope)
        head = RoundedRectangle(corner_radius=0.2, height=1.5, width=1.5, color="#FFFFFF", stroke_width=4).move_to([0, -0.8, 0])
        eye_l = Circle(radius=0.15, color="#FFFFFF", fill_opacity=1).move_to(head.get_center() + LEFT * 0.35 + UP * 0.1)
        eye_r = Circle(radius=0.15, color="#FFFFFF", fill_opacity=1).move_to(head.get_center() + RIGHT * 0.35 + UP * 0.1)
        
        # Backwards Cap
        cap_base = Rectangle(height=0.3, width=1.6, color="#FFFFFF", fill_opacity=1).next_to(head, UP, buff=0)
        cap_brim = Rectangle(height=0.1, width=1.0, color="#FFFFFF", fill_opacity=1).next_to(cap_base, LEFT, buff=-0.2)
        cap = VGroup(cap_base, cap_brim)
        
        robot = VGroup(head, eye_l, eye_r, cap)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(robot), run_time=1.5)
        self.play(robot.animate.shift(UP * 0.2), run_time=2.5, rate_func=there_and_back)
        self.wait(2.8)

class Scene03_02(Scene):
    def construct(self):
        title, footer, left_meta, right_meta = get_footer_and_title( "DISCUSSION ON TEENAGED AI", "ARTIFICIAL INTELLIGENCE")
        self.add(footer, left_meta, right_meta)
        
        # Visual: Two robot heads with a speech bubble (Discussion)
        r1 = RoundedRectangle(corner_radius=0.1, height=1, width=1, color="#FFFFFF", stroke_width=3).move_to([-1.5, -1, 0])
        r2 = RoundedRectangle(corner_radius=0.1, height=1, width=1, color="#FFFFFF", stroke_width=3).move_to([1.5, -1, 0])
        
        bubble = RoundedRectangle(corner_radius=0.3, height=1.2, width=2.5, color="#FFFFFF", stroke_width=2).move_to([0, 0, 0])
        bubble_tail = Polygon([0.2, -0.6, 0], [-0.2, -0.6, 0], [0, -0.9, 0], color="#FFFFFF", fill_opacity=1)
        ai_text = Text("AI", font="Arial", weight=BOLD, font_size=30, color="#FFFFFF").move_to(bubble)
        
        discussion = VGroup(r1, r2, bubble, bubble_tail, ai_text)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(r1), Create(r2), run_time=1.0)
        self.play(GrowFromCenter(bubble), FadeIn(bubble_tail), Write(ai_text), run_time=1.5)
        self.play(bubble.animate.scale(1.1), run_time=2.0, rate_func=there_and_back)
        self.wait(2.3)

class Scene03_03(Scene):
    def construct(self):
        title, footer, left_meta, right_meta = get_footer_and_title( "DISCUSSION ON TEENAGED AI", "ARTIFICIAL INTELLIGENCE")
        self.add(footer, left_meta, right_meta)
        
        # Visual: Robot on a skateboard (Literal "Teenager")
        board = RoundedRectangle(corner_radius=0.1, height=0.2, width=2.5, color="#FFFFFF", fill_opacity=1).move_to([0, -1.8, 0])
        wheel1 = Circle(radius=0.15, color="#FFFFFF", stroke_width=3).move_to([-0.8, -2.05, 0])
        wheel2 = Circle(radius=0.15, color="#FFFFFF", stroke_width=3).move_to([0.8, -2.05, 0])
        
        body = Rectangle(height=1.2, width=0.8, color="#FFFFFF", stroke_width=4).next_to(board, UP, buff=0.1)
        head = RoundedRectangle(corner_radius=0.1, height=0.6, width=0.6, color="#FFFFFF", stroke_width=4).next_to(body, UP, buff=0.1)
        
        teen_ai = VGroup(board, wheel1, wheel2, body, head)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(teen_ai), run_time=1.5)
        self.play(teen_ai.animate.shift(RIGHT * 0.5), run_time=2.0, rate_func=linear)
        self.play(teen_ai.animate.shift(LEFT * 1.0), run_time=2.0, rate_func=linear)
        self.wait(1.3)

class Scene03_04(Scene):
    def construct(self):
        title, footer, left_meta, right_meta = get_footer_and_title( "DISCUSSION ON TEENAGED AI", "ARTIFICIAL INTELLIGENCE")
        self.add(footer, left_meta, right_meta)
        
        # Visual: Growth Chart (Teenage phase)
        ruler = Line([ -2, -2, 0], [-2, 0.2, 0], color="#FFFFFF", stroke_width=3)
        ticks = VGroup(*[Line([-2.1, y, 0], [-1.9, y, 0], color="#FFFFFF") for y in np.arange(-2, 0.3, 0.4)])
        
        robot_child = Rectangle(height=0.5, width=0.5, color="#FFFFFF").move_to([-0.5, -1.75, 0]).set_opacity(0.3)
        robot_teen = Rectangle(height=1.2, width=0.8, color="#FFFFFF", stroke_width=4).move_to([0.5, -1.4, 0])
        robot_adult = Rectangle(height=2.0, width=1.0, color="#FFFFFF").move_to([2.0, -1.0, 0]).set_opacity(0.3)
        
        arrow = Arrow(start=UP*0.5, end=DOWN*0.2, color="#FFFFFF").next_to(robot_teen, UP, buff=0.2)
        label = Text("TEEN PHASE", font="Arial", font_size=14, color="#FFFFFF").next_to(arrow, UP, buff=0.1)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(ruler), Create(ticks), run_time=1.0)
        self.play(FadeIn(robot_child), FadeIn(robot_adult), run_time=1.0)
        self.play(Create(robot_teen), run_time=1.0)
        self.play(GrowArrow(arrow), Write(label), run_time=1.0)
        self.wait(2.8)

class Scene03_05(Scene):
    def construct(self):
        title, footer, left_meta, right_meta = get_footer_and_title( "DISCUSSION ON TEENAGED AI", "ARTIFICIAL INTELLIGENCE")
        self.add(footer, left_meta, right_meta)
        
        # Visual: Loading bar at 60% (Developmental stage)
        frame = RoundedRectangle(corner_radius=0.1, height=0.6, width=4, color="#FFFFFF", stroke_width=3).move_to([0, -1, 0])
        progress = Rectangle(height=0.4, width=2.4, color="#FFFFFF", fill_opacity=1).align_to(frame, LEFT).shift(RIGHT * 0.1)
        
        status_text = Text("AI MATURITY: 60%", font="Arial", weight=BOLD, font_size=18, color="#FFFFFF").next_to(frame, UP, buff=0.4)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(frame), run_time=1.0)
        self.play(progress.animate(run_time=3.0).stretch_to_fit_width(2.4), Write(status_text), run_time=3.0)
        self.play(status_text.animate.set_opacity(0.3), run_time=1.0)
        self.wait(1.8)

class Scene03_06(Scene):
    def construct(self):
        title, footer, left_meta, right_meta = get_footer_and_title( "DISCUSSION ON TEENAGED AI", "ARTIFICIAL INTELLIGENCE")
        self.add(footer, left_meta, right_meta)
        
        # Visual: Robot with a backpack (Literal student/teen)
        body = RoundedRectangle(corner_radius=0.1, height=1.2, width=0.9, color="#FFFFFF", stroke_width=4).move_to([0, -1.2, 0])
        head = Circle(radius=0.4, color="#FFFFFF", stroke_width=4).next_to(body, UP, buff=0.1)
        
        backpack = RoundedRectangle(corner_radius=0.05, height=0.8, width=0.3, color="#FFFFFF", fill_opacity=0.5).next_to(body, LEFT, buff=-0.1)
        strap1 = Line(backpack.get_top(), body.get_top() + LEFT*0.2, color="#FFFFFF")
        strap2 = Line(backpack.get_bottom(), body.get_bottom() + LEFT*0.2, color="#FFFFFF")
        
        teen_robot = VGroup(body, head, backpack, strap1, strap2)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(teen_robot), run_time=1.5)
        self.play(teen_robot.animate.rotate(0.1), run_time=1.5, rate_func=there_and_back)
        self.play(teen_robot.animate.shift(UP * 0.1), run_time=1.5, rate_func=there_and_back)
        self.wait(2.3)

class Scene03_07(Scene):
    def construct(self):
        title, footer, left_meta, right_meta = get_footer_and_title( "DISCUSSION ON TEENAGED AI", "ARTIFICIAL INTELLIGENCE")
        self.add(footer, left_meta, right_meta)
        
        # Visual: A hoodie-wearing robot silhouette
        hoodie_body = Polygon([-0.8, -2, 0], [0.8, -2, 0], [0.6, -0.8, 0], [-0.6, -0.8, 0], color="#FFFFFF", stroke_width=4)
        hood = Arc(radius=0.5, start_angle=0, angle=PI, color="#FFFFFF", stroke_width=4).move_to([0, -0.4, 0])
        face_hole = Ellipse(width=0.4, height=0.5, color="#FFFFFF").move_to(hood.get_center() + DOWN*0.1)
        
        pocket = RoundedRectangle(corner_radius=0.05, height=0.3, width=0.6, color="#FFFFFF", stroke_width=2).move_to([0, -1.5, 0])
        
        teen_ai = VGroup(hoodie_body, hood, face_hole, pocket)
        
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(teen_ai), run_time=1.5)
        self.play(teen_ai.animate.scale(1.05), run_time=2.0, rate_func=there_and_back)
        self.play(FadeToColor(teen_ai, "#FFFFFF"), run_time=1.0)
        self.wait(2.3)

# Global Configuration

# (Using universal get_footer_and_title from manim_compat)

class Scene03_08(Scene):
    def construct(self):
        # Setup
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Illustration: Robot with Headphones (Literal Teenager)
        head = RoundedRectangle(width=1.8, height=1.6, corner_radius=0.3, color="#FFFFFF", stroke_width=3).move_to(DOWN * 0.8)
        eye_l = Circle(radius=0.15, color="#FFFFFF", stroke_width=2).move_to(head.get_center() + LEFT * 0.4 + UP * 0.2)
        eye_r = Circle(radius=0.15, color="#FFFFFF", stroke_width=2).move_to(head.get_center() + RIGHT * 0.4 + UP * 0.2)
        mouth = Line(LEFT * 0.3, RIGHT * 0.3, color="#FFFFFF").next_to(eye_l, DOWN, buff=0.4).shift(RIGHT * 0.4)
        
        headphone_arc = Arc(radius=1.1, start_angle=0, angle=PI, color="#FFFFFF", stroke_width=6).move_to(head.get_top() + DOWN * 0.2)
        ear_l = RoundedRectangle(width=0.4, height=0.8, corner_radius=0.1, color="#FFFFFF", fill_opacity=1).next_to(head, LEFT, buff=-0.1)
        ear_r = RoundedRectangle(width=0.4, height=0.8, corner_radius=0.1, color="#FFFFFF", fill_opacity=1).next_to(head, RIGHT, buff=-0.1)
        
        teen_robot = VGroup(head, eye_l, eye_r, mouth, headphone_arc, ear_l, ear_r)
        
        self.play(Create(teen_robot), run_time=1.5)
        self.play(teen_robot.animate.scale(1.1).set_stroke(width=4), run_time=2.0, rate_func=there_and_back)
        self.play(mouth.animate.stretch(1.5, 0), run_time=1.5, rate_func=wiggle)
        self.wait(1.8)

class Scene03_09(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Illustration: Robot with a Baseball Cap (Literal Teenager)
        head = Circle(radius=0.9, color="#FFFFFF", stroke_width=3).move_to(DOWN * 1.0)
        cap_base = Polygon([-1.0, 0, 0], [1.0, 0, 0], [0.6, 0.5, 0], [-0.6, 0.5, 0], color="#FFFFFF", fill_opacity=1).next_to(head, UP, buff=-0.2)
        cap_brim = Rectangle(width=1.4, height=0.15, color="#FFFFFF", fill_opacity=1).next_to(cap_base, DOWN, buff=-0.1).shift(RIGHT * 0.4)
        
        eyes = VGroup(Dot(color="#FFFFFF").shift(LEFT*0.3 + DOWN*0.8), Dot(color="#FFFFFF").shift(RIGHT*0.3 + DOWN*0.8))
        
        teen_cap = VGroup(head, cap_base, cap_brim, eyes)
        
        self.play(FadeIn(head, shift=UP), run_time=1.0)
        self.play(DrawBorderThenFill(cap_base), Create(cap_brim), run_time=1.5)
        self.play(teen_cap.animate.rotate(0.1), run_time=2.0, rate_func=there_and_back)
        self.wait(2.3)

class Scene03_10(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Illustration: Growth Chart (Literal Development)
        chart_line = Line(DOWN * 2.2, UP * 0.2, color="#FFFFFF", stroke_width=2).shift(LEFT * 1.5)
        ticks = VGroup(*[Line(LEFT*0.1, RIGHT*0.1, color="#FFFFFF").move_to(chart_line.point_from_proportion(i/5)) for i in range(6)])
        
        robot_body = Rectangle(width=1.2, height=0.5, color="#FFFFFF", fill_opacity=0.2).move_to(DOWN * 2.0)
        robot_head = Square(side_length=0.6, color="#FFFFFF").next_to(robot_body, UP, buff=0.1)
        robot = VGroup(robot_body, robot_head)

        self.play(Create(chart_line), Create(ticks), run_time=1.0)
        self.play(FadeIn(robot), run_time=0.8)
        self.play(robot.animate.stretch_to_fit_height(2.2).move_to(DOWN * 1.1), run_time=3.0, rate_func=slow_into)
        
        arrow = Arrow(LEFT * 0.5, RIGHT * 0.5, color="#FFFFFF").next_to(robot, RIGHT)
        self.play(Create(arrow), run_time=1.0)
        self.wait(1.0)

class Scene03_11(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Illustration: Breaking the Power Cord (Literal Independence/Rebellion)
        socket = Rectangle(width=0.8, height=1.0, color="#FFFFFF", stroke_width=2).move_to(LEFT * 2 + DOWN * 1)
        plug = Rectangle(width=0.5, height=0.3, color="#FFFFFF", fill_opacity=1).next_to(socket, RIGHT, buff=0)
        cord = DashedLine(plug.get_right(), RIGHT * 2 + DOWN * 1, color="#FFFFFF", stroke_width=3)
        robot_hand = RoundedRectangle(width=0.6, height=0.8, color="#FFFFFF").move_to(RIGHT * 2 + DOWN * 1)

        self.play(Create(socket), Create(plug), Create(cord), Create(robot_hand), run_time=1.5)
        self.play(
            plug.animate.shift(RIGHT * 1.5),
            cord.animate.become(DashedLine(RIGHT * 0.5 + DOWN * 1, RIGHT * 2 + DOWN * 1, color="#FFFFFF")),
            robot_hand.animate.shift(RIGHT * 0.5),
            run_time=2.0,
            rate_func=exponential_decay
        )
        
        spark = Star(n=8, outer_radius=0.3, inner_radius=0.1, color="#FFFFFF").move_to(socket.get_right() + RIGHT*0.2)
        self.play(FadeIn(spark), run_time=0.5)
        self.play(FadeOut(spark), run_time=0.5)
        self.wait(2.3)

class Scene03_12(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Illustration: Robot with Backpack (Literal Schooling/Learning)
        body = Rectangle(width=1.2, height=1.5, color="#FFFFFF", stroke_width=3).move_to(DOWN * 1.2)
        backpack = RoundedRectangle(width=0.5, height=1.2, corner_radius=0.1, color="#FFFFFF", fill_opacity=0.3).next_to(body, LEFT, buff=-0.2)
        head = Circle(radius=0.5, color="#FFFFFF").next_to(body, UP, buff=0.1)
        
        book = Rectangle(width=0.8, height=1.0, color="#FFFFFF", fill_opacity=0.1).move_to(RIGHT * 1.8 + DOWN * 1)
        lines = VGroup(*[Line(LEFT*0.2, RIGHT*0.2, color="#FFFFFF", stroke_width=1).move_to(book.get_center() + UP*(0.3 - i*0.2)) for i in range(4)])
        
        student = VGroup(body, backpack, head)
        
        self.play(Create(student), run_time=1.5)
        self.play(Create(book), Create(lines), run_time=1.5)
        self.play(student.animate.shift(RIGHT * 0.2), run_time=2.0, rate_func=there_and_back)
        self.wait(1.8)

class Scene03_13(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Illustration: Discussion (Two Robot Heads with Speech Bubbles)
        bot1 = Circle(radius=0.6, color="#FFFFFF").move_to(LEFT * 1.8 + DOWN * 1.2)
        bot2 = Circle(radius=0.6, color="#FFFFFF").move_to(RIGHT * 1.8 + DOWN * 1.2)
        
        bubble1 = RoundedRectangle(width=1.5, height=0.8, corner_radius=0.2, color="#FFFFFF").next_to(bot1, UP, buff=0.4).shift(RIGHT*0.5)
        bubble2 = RoundedRectangle(width=1.5, height=0.8, corner_radius=0.2, color="#FFFFFF").next_to(bot2, UP, buff=0.4).shift(LEFT*0.5)
        
        txt1 = Text("0101", font_size=15, color="#FFFFFF").move_to(bubble1)
        txt2 = Text("1010", font_size=15, color="#FFFFFF").move_to(bubble2)

        self.play(Create(bot1), Create(bot2), run_time=1.0)
        self.play(Create(bubble1), Write(txt1), run_time=1.5)
        self.play(Create(bubble2), Write(txt2), run_time=1.5)
        self.play(VGroup(bubble1, txt1).animate.shift(UP*0.2), run_time=1.0, rate_func=there_and_back)
        self.play(VGroup(bubble2, txt2).animate.shift(UP*0.2), run_time=1.0, rate_func=there_and_back)
        self.wait(0.8)

class Scene03_14(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Illustration: Robot with Smartphone (Modern Teenager)
        hand = Rectangle(width=0.4, height=0.8, color="#FFFFFF", stroke_width=2).move_to(DOWN * 1.5)
        phone = RoundedRectangle(width=1.0, height=1.8, corner_radius=0.1, color="#FFFFFF", stroke_width=4).move_to(DOWN * 0.8)
        screen = Rectangle(width=0.8, height=1.4, color="#FFFFFF", fill_opacity=0.1).move_to(phone)
        
        # App icons (literal squares)
        icons = VGroup(*[Square(side_length=0.2, color="#FFFFFF", fill_opacity=1) for _ in range(6)]).arrange_in_grid(rows=3, cols=2, buff=0.2).move_to(screen)

        self.play(FadeIn(phone), FadeIn(screen), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(icon) for icon in icons], lag_ratio=0.2), run_time=2.0)
        
        # Simulate "scrolling"
        self.play(icons.animate.shift(UP * 0.3), run_time=1.5, rate_func=linear)
        self.play(icons.animate.shift(DOWN * 0.3), run_time=1.5, rate_func=linear)
        self.wait(0.6)

# --- CONFIGURATION ---

# (Using universal get_footer_and_title from manim_compat)

class Scene03_15(Scene):
    def construct(self):
        # Setup
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Robot Head with a Baseball Cap (Teenager Literal)
        head = RoundedRectangle(width=1.5, height=1.2, corner_radius=0.2, color="#FFFFFF", stroke_width=3).move_to([0, -0.8, 0])
        eye_l = Circle(radius=0.15, color="#FFFFFF", fill_opacity=1).move_to(head.get_center() + LEFT * 0.35 + UP * 0.1)
        eye_r = Circle(radius=0.15, color="#FFFFFF", fill_opacity=1).move_to(head.get_center() + RIGHT * 0.35 + UP * 0.1)
        
        # The Cap
        cap_base = Line(LEFT * 0.8, RIGHT * 0.8, color="#FFFFFF", stroke_width=4).next_to(head, UP, buff=0)
        cap_top = Arc(radius=0.7, start_angle=0, angle=PI, color="#FFFFFF", stroke_width=3).move_to(cap_base.get_center() + UP * 0.3)
        cap_brim = Line(RIGHT * 0.7, RIGHT * 1.4, color="#FFFFFF", stroke_width=4).move_to(cap_base.get_right() + RIGHT * 0.3)
        cap = VGroup(cap_base, cap_top, cap_brim)

        robot_teen = VGroup(head, eye_l, eye_r, cap)
        
        self.play(Create(head), Create(eye_l), Create(eye_r), run_time=1.5)
        self.play(Create(cap), run_time=1.0)
        self.play(robot_teen.animate.shift(UP * 0.1), run_time=2.0, rate_func=there_and_back)
        self.wait(2.3)

class Scene03_16(Scene):
    def construct(self):
        # Setup
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: A Skateboard (Literal Teenager Symbol)
        board = RoundedRectangle(width=3.0, height=0.3, corner_radius=0.1, color="#FFFFFF", stroke_width=3).move_to([0, -1.2, 0])
        wheel_l = Circle(radius=0.2, color="#FFFFFF", stroke_width=3).move_to(board.get_left() + RIGHT * 0.5 + DOWN * 0.3)
        wheel_r = Circle(radius=0.2, color="#FFFFFF", stroke_width=3).move_to(board.get_right() + LEFT * 0.5 + DOWN * 0.3)
        
        # Robot on board
        body = Rectangle(width=0.8, height=1.0, color="#FFFFFF", stroke_width=3).next_to(board, UP, buff=0.1)
        head = Circle(radius=0.3, color="#FFFFFF", stroke_width=3).next_to(body, UP, buff=0.1)
        
        skater = VGroup(board, wheel_l, wheel_r, body, head)
        
        self.play(Create(board), Create(wheel_l), Create(wheel_r), run_time=1.5)
        self.play(FadeIn(body), FadeIn(head), run_time=1.0)
        self.play(skater.animate.shift(RIGHT * 0.5), run_time=2.0, rate_func=slow_into)
        self.play(skater.animate.shift(LEFT * 0.5), run_time=2.3)

class Scene03_17(Scene):
    def construct(self):
        # Setup
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Smartphone with Chat Bubbles (Teen Communication)
        phone = RoundedRectangle(width=1.4, height=2.4, corner_radius=0.15, color="#FFFFFF", stroke_width=3).move_to([0, -1.0, 0])
        screen = RoundedRectangle(width=1.2, height=2.0, corner_radius=0.1, color="#FFFFFF", stroke_width=1).move_to(phone.get_center())
        
        bubble1 = RoundedRectangle(width=0.7, height=0.3, corner_radius=0.1, color="#FFFFFF", fill_opacity=0.2).move_to(screen.get_center() + UP * 0.5 + LEFT * 0.2)
        bubble2 = RoundedRectangle(width=0.7, height=0.3, corner_radius=0.1, color="#FFFFFF", fill_opacity=0.5).move_to(screen.get_center() + RIGHT * 0.2)
        bubble3 = RoundedRectangle(width=0.7, height=0.3, corner_radius=0.1, color="#FFFFFF", fill_opacity=0.8).move_to(screen.get_center() + DOWN * 0.5 + LEFT * 0.2)

        self.play(Create(phone), Create(screen), run_time=1.5)
        self.play(FadeIn(bubble1, shift=RIGHT), run_time=0.8)
        self.play(FadeIn(bubble2, shift=LEFT), run_time=0.8)
        self.play(FadeIn(bubble3, shift=RIGHT), run_time=0.8)
        self.play(VGroup(bubble1, bubble2, bubble3).animate.shift(UP * 0.1), run_time=2.9)

class Scene03_18(Scene):
    def construct(self):
        # Setup
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: A Backpack (Literal Schooling/Teenage)
        pack_main = RoundedRectangle(width=1.8, height=2.2, corner_radius=0.4, color="#FFFFFF", stroke_width=3).move_to([0, -1.0, 0])
        pocket = RoundedRectangle(width=1.2, height=0.8, corner_radius=0.2, color="#FFFFFF", stroke_width=2).move_to(pack_main.get_bottom() + UP * 0.6)
        strap_l = Arc(radius=0.5, start_angle=PI/2, angle=PI, color="#FFFFFF").move_to(pack_main.get_left() + UP * 0.5)
        strap_r = Arc(radius=0.5, start_angle=-PI/2, angle=PI, color="#FFFFFF").move_to(pack_main.get_right() + UP * 0.5)
        
        # Circuit lines on backpack to show it's AI
        line1 = Line(pocket.get_left(), pocket.get_right(), color="#FFFFFF", stroke_width=1).set_opacity(0.5)
        line2 = Line(pack_main.get_top(), pocket.get_top(), color="#FFFFFF", stroke_width=1).set_opacity(0.5)

        backpack = VGroup(pack_main, pocket, strap_l, strap_r, line1, line2)
        
        self.play(Create(pack_main), run_time=1.5)
        self.play(Create(pocket), Create(strap_l), Create(strap_r), run_time=1.5)
        self.play(backpack.animate.scale(1.1), run_time=2.0, rate_func=there_and_back)
        self.wait(1.8)

class Scene03_19(Scene):
    def construct(self):
        # Setup
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Game Controller (Teenage Leisure)
        body_l = Circle(radius=0.6, color="#FFFFFF", stroke_width=3).move_to([-0.8, -1.0, 0])
        body_r = Circle(radius=0.6, color="#FFFFFF", stroke_width=3).move_to([0.8, -1.0, 0])
        bridge = Rectangle(width=1.0, height=0.6, color="#FFFFFF", stroke_width=3).move_to([0, -1.0, 0])
        
        dpad = VGroup(Line(UP*0.2, DOWN*0.2), Line(LEFT*0.2, RIGHT*0.2)).move_to(body_l.get_center()).set_stroke(width=4)
        btn1 = Circle(radius=0.1, color="#FFFFFF", fill_opacity=1).move_to(body_r.get_center() + UP*0.2)
        btn2 = Circle(radius=0.1, color="#FFFFFF", fill_opacity=1).move_to(body_r.get_center() + DOWN*0.2)
        
        controller = VGroup(body_l, body_r, bridge, dpad, btn1, btn2)
        
        self.play(Create(bridge), run_time=1.0)
        self.play(Create(body_l), Create(body_r), run_time=1.5)
        self.play(FadeIn(dpad), FadeIn(btn1), FadeIn(btn2), run_time=1.0)
        self.play(controller.animate.rotate(0.1), run_time=1.5, rate_func=there_and_back)
        self.wait(1.8)

class Scene03_20(Scene):
    def construct(self):
        # Setup
        title, footer, left, right = get_footer_and_title( "TEENAGED AI")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Mirror Reflection (Identity Crisis/Teenage)
        mirror_frame = Rectangle(width=3.0, height=2.0, color="#FFFFFF", stroke_width=4).move_to([0, -1.0, 0])
        divider = Line(UP * 0, DOWN * 2.0, color="#FFFFFF", stroke_width=1).move_to([0, -1.0, 0]).set_opacity(0.3)
        
        # Left side: Simple Robot
        bot_l = VGroup(Circle(radius=0.3), Rectangle(width=0.4, height=0.5)).arrange(DOWN, buff=0.1).move_to([-0.8, -1.0, 0])
        # Right side: Complex Robot (Reflection)
        bot_r = VGroup(Circle(radius=0.3), Rectangle(width=0.4, height=0.5)).arrange(DOWN, buff=0.1).move_to([0.8, -1.0, 0])
        extra_detail = DashedLine(bot_r.get_top(), bot_r.get_bottom(), color="#FFFFFF").move_to(bot_r.get_center())
        
        self.play(Create(mirror_frame), Create(divider), run_time=1.5)
        self.play(FadeIn(bot_l), run_time=1.0)
        self.play(FadeIn(bot_r), FadeIn(extra_detail), run_time=1.5)
        self.play(bot_l.animate.shift(RIGHT * 0.1), bot_r.animate.shift(LEFT * 0.1), run_time=2.0, rate_func=there_and_back)
        self.wait(0.8)