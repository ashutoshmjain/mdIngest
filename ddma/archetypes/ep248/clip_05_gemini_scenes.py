import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# CANVAS CONFIGURATION

# (Using universal get_footer_and_title from manim_compat)

class Scene05_01(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON NOTHING IS FREE !")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # FIGURATIVE: Balance Scale
        pivot = Triangle(color=WHITE).scale(0.2).move_to(DOWN * 2)
        beam = Line(LEFT * 2, RIGHT * 2, color=WHITE).move_to(DOWN * 1.2)
        
        left_plate = Line(LEFT * 0.5, RIGHT * 0.5, color=WHITE).move_to(beam.get_start() + DOWN * 0.5)
        right_plate = Line(LEFT * 0.5, RIGHT * 0.5, color=WHITE).move_to(beam.get_end() + DOWN * 0.5)
        
        left_wire = VGroup(Line(beam.get_start(), left_plate.get_start()), Line(beam.get_start(), left_plate.get_end()))
        right_wire = VGroup(Line(beam.get_end(), right_plate.get_start()), Line(beam.get_end(), right_plate.get_end()))
        
        gift = VGroup(Rectangle(width=0.6, height=0.6), Line(UP*0.3, DOWN*0.3), Line(LEFT*0.3, RIGHT*0.3)).next_to(left_plate, UP, buff=0)
        cost = Text("$", font="Arial", font_size=36).next_to(right_plate, UP, buff=0.1)
        
        scale = VGroup(beam, left_plate, right_plate, left_wire, right_wire, gift, cost)
        
        self.play(Create(pivot), Create(scale), run_time=1.5)
        self.play(scale.animate.rotate(0.2, about_point=pivot.get_top()), run_time=2)
        self.play(scale.animate.rotate(-0.4, about_point=pivot.get_top()), run_time=2)
        self.play(scale.animate.rotate(0.2, about_point=pivot.get_top()), run_time=1.4)
        self.wait(0.5)

class Scene05_02(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON NOTHING IS FREE !")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # FIGURATIVE: Mouse Trap
        base = Rectangle(width=3, height=1.5, color=WHITE).move_to(DOWN * 1.5)
        spring = Circle(radius=0.2, color=WHITE).move_to(base.get_center())
        arm = Line(base.get_left() + UP*0.2, base.get_right() + UP*0.2, color=WHITE)
        
        cheese = Triangle(color=WHITE).scale(0.3).set_fill(WHITE, opacity=0.8).move_to(base.get_center() + UP*0.4)
        label = Text("FREE", font="Arial", font_size=14, color=BLACK).move_to(cheese.get_center())
        
        trap = VGroup(base, spring, arm, cheese, label)
        
        self.play(FadeIn(trap, shift=UP), run_time=1.5)
        self.play(trap.animate.shake(), run_time=2)
        
        snap_arm = Line(base.get_right() + UP*0.2, base.get_left() + UP*0.2, color=WHITE).move_to(base.get_center() + UP*0.1)
        self.play(Transform(arm, snap_arm), cheese.animate.scale(0.8).set_opacity(0.3), run_time=0.4)
        self.wait(3.0)

class Scene05_03(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON NOTHING IS FREE !")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # FIGURATIVE: Fishing Hook
        line = Line(UP * 0.5, DOWN * 1.5, color=WHITE).move_to(UP * 0.4)
        hook = Arc(radius=0.4, start_angle=PI, angle=1.5*PI, color=WHITE).next_to(line, DOWN, buff=0)
        tip = Arrow(hook.get_end() + LEFT*0.1, hook.get_end() + UP*0.2, color=WHITE, stroke_width=2, tip_length=0.1)
        
        bait = RoundedRectangle(width=0.6, height=0.3, corner_radius=0.1, color=WHITE).move_to(hook.get_start() + DOWN*0.2)
        bait_text = Text("FREE", font="Arial", font_size=12, color=WHITE).move_to(bait.get_center())
        
        fishing_rig = VGroup(line, hook, tip, bait, bait_text)
        
        self.play(fishing_rig.animate.shift(DOWN * 0.5), run_time=2, rate_func=slow_into)
        for _ in range(3):
            self.play(fishing_rig.animate.shift(UP * 0.2), run_time=0.5)
            self.play(fishing_rig.animate.shift(DOWN * 0.2), run_time=0.5)
        self.wait(1.9)

class Scene05_04(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON NOTHING IS FREE !")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # FIGURATIVE: Iceberg
        water_line = DashedLine(LEFT * 3.5, RIGHT * 3.5, color=WHITE).move_to(ORIGIN)
        iceberg_top = Polygon([-0.8, 0, 0], [0, 0.4, 0], [0.8, 0, 0], color=WHITE, stroke_width=2)
        iceberg_bottom = Polygon([-0.8, 0, 0], [-1.5, -2, 0], [1.5, -2, 0], [0.8, 0, 0], color=WHITE, stroke_width=2).set_fill(WHITE, opacity=0.1)
        
        free_text = Text("FREE", font="Arial", font_size=20).move_to(UP * 0.25)
        hidden_text = Text("HIDDEN COSTS", font="Arial", font_size=24, weight=BOLD).move_to(DOWN * 1)
        
        self.play(Create(water_line), run_time=1)
        self.play(Create(iceberg_top), Write(free_text), run_time=1.5)
        self.play(Create(iceberg_bottom), Write(hidden_text), run_time=2.5)
        self.play(VGroup(iceberg_top, iceberg_bottom, free_text, hidden_text).animate.shift(UP * 0.1), run_time=1)
        self.play(VGroup(iceberg_top, iceberg_bottom, free_text, hidden_text).animate.shift(DOWN * 0.1), run_time=0.9)

class Scene05_05(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON NOTHING IS FREE !")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # FIGURATIVE: Gift Box with Strings
        box = Rectangle(width=1.5, height=1.2, color=WHITE).move_to(DOWN * 1)
        lid = Rectangle(width=1.7, height=0.3, color=WHITE).next_to(box, UP, buff=0)
        ribbon_v = Line(box.get_top(), box.get_bottom(), color=WHITE)
        
        strings = VGroup(*[Line(box.get_top() + RIGHT*i, UP*0.4 + RIGHT*i*2, color=WHITE).set_opacity(0.5) for i in np.linspace(-0.5, 0.5, 6)])
        
        gift_label = Text("FREE GIFT", font="Arial", font_size=16).move_to(box.get_center())
        
        self.play(Create(box), Create(lid), Create(ribbon_v), Write(gift_label), run_time=2)
        self.play(Create(strings), run_time=2)
        self.play(VGroup(box, lid, ribbon_v, gift_label, strings).animate.scale(1.1), run_time=1.5)
        self.play(VGroup(box, lid, ribbon_v, gift_label, strings).animate.scale(0.9), run_time=1.4)

class Scene05_06(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON NOTHING IS FREE !")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # FIGURATIVE: Hourglass (Time is the cost)
        top = Polygon([-1, 0.4, 0], [1, 0.4, 0], [0, -0.5, 0], color=WHITE)
        bottom = Polygon([-1, -1.4, 0], [1, -1.4, 0], [0, -0.5, 0], color=WHITE)
        
        sand_top = Polygon([-0.8, 0.3, 0], [0.8, 0.3, 0], [0, -0.5, 0], color=WHITE).set_fill(WHITE, opacity=0.8)
        sand_bottom = Polygon([0, -0.5, 0], [0, -0.5, 0], [0, -0.5, 0], color=WHITE).set_fill(WHITE, opacity=0.8)
        
        free_label = Text("FREE", font="Arial", font_size=14).move_to(UP * 0.1)
        time_label = Text("YOUR TIME", font="Arial", font_size=14).move_to(DOWN * 1.7)
        
        self.add(top, bottom, sand_top, free_label, time_label)
        
        new_sand_top = Polygon([0, -0.5, 0], [0, -0.5, 0], [0, -0.5, 0], color=WHITE).set_fill(WHITE, opacity=0.8)
        new_sand_bottom = Polygon([-0.9, -1.4, 0], [0.9, -1.4, 0], [0, -0.5, 0], color=WHITE).set_fill(WHITE, opacity=0.8)
        
        self.play(Transform(sand_top, new_sand_top), Transform(sand_bottom, new_sand_bottom), run_time=6.0, rate_func=linear)
        self.wait(0.9)

class Scene05_07(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON NOTHING IS FREE !")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # FIGURATIVE: Contract with Fine Print
        paper = Rectangle(width=2.5, height=3, color=WHITE).move_to(DOWN * 1)
        header = Text("FREE SERVICE", font="Arial", font_size=18, weight=BOLD).move_to(paper.get_top() + DOWN * 0.4)
        
        fine_print = VGroup(*[Line(LEFT*1, RIGHT*1, stroke_width=1).move_to(DOWN * (0.8 + i*0.2)) for i in range(8)])
        fine_print.set_opacity(0.5)
        
        magnifying_glass_circle = Circle(radius=0.5, color=WHITE).move_to(DOWN * 1.5 + RIGHT * 0.5)
        handle = Line(magnifying_glass_circle.get_bottom() + LEFT*0.1, magnifying_glass_circle.get_bottom() + DOWN*0.4 + RIGHT*0.4, color=WHITE)
        glass = VGroup(magnifying_glass_circle, handle)
        
        self.play(Create(paper), Write(header), run_time=1.5)
        self.play(Create(fine_print), run_time=2)
        self.play(FadeIn(glass), run_time=0.8)
        self.play(glass.animate.shift(LEFT * 1), run_time=1.5)
        self.play(glass.animate.shift(UP * 0.5), run_time=1.1)

# Global Configuration

# (Using universal get_footer_and_title from manim_compat)

class Scene05_08(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "NOTHING IS FREE")
        
        # Illustration: Balance Scale
        base = Polygon([-0.5, -2, 0], [0.5, -2, 0], [0, -1.5, 0], color="#FFFFFF", stroke_width=2)
        beam = Line([-2, -0.5, 0], [2, -0.5, 0], color="#FFFFFF", stroke_width=4)
        pivot = Circle(radius=0.1, color="#FFFFFF", fill_opacity=1).move_to([0, -0.5, 0])
        
        left_pan = Line([-2.5, -0.5, 0], [-1.5, -0.5, 0], color="#FFFFFF").move_to([-2, -1.2, 0])
        right_pan = Line([1.5, -0.5, 0], [2.5, -0.5, 0], color="#FFFFFF").move_to([2, -1.2, 0])
        
        left_strings = VGroup(Line([-2, -0.5, 0], [-2.5, -1.2, 0]), Line([-2, -0.5, 0], [-1.5, -1.2, 0]))
        right_strings = VGroup(Line([2, -0.5, 0], [1.5, -1.2, 0]), Line([2, -0.5, 0], [2.5, -1.2, 0]))
        
        gift = VGroup(Rectangle(width=0.8, height=0.6), Line([0, 0.3, 0], [0, -0.3, 0]), Line([-0.4, 0, 0], [0.4, 0, 0]))
        gift.move_to([-2, -0.9, 0])
        gift_label = Text("FREE", font_size=14).next_to(gift, UP, buff=0.1)
        
        cost_weight = Circle(radius=0.4, color="#FFFFFF", fill_opacity=0.2).move_to([2, -0.8, 0])
        cost_label = Text("COST", font_size=14).move_to(cost_weight.get_center())

        scale_group = VGroup(beam, left_pan, right_pan, left_strings, right_strings, gift, gift_label, cost_weight, cost_label)

        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(base), Create(pivot), Create(beam), run_time=1)
        self.play(Create(left_strings), Create(right_strings), Create(left_pan), Create(right_pan), run_time=1)
        self.play(FadeIn(gift, shift=DOWN), Write(gift_label), run_time=1)
        self.play(FadeIn(cost_weight, shift=DOWN), Write(cost_label), run_time=1)
        
        # Tipping the scale
        self.play(
            Rotate(beam, angle=-0.2, about_point=[0, -0.5, 0]),
            scale_group.animate.shift(UP * 0), # Dummy to keep group together
            gift.animate.shift(UP * 0.4),
            gift_label.animate.shift(UP * 0.4),
            cost_weight.animate.shift(DOWN * 0.4),
            cost_label.animate.shift(DOWN * 0.4),
            left_pan.animate.shift(UP * 0.4),
            right_pan.animate.shift(DOWN * 0.4),
            left_strings.animate.shift(UP * 0.2), # Simplified movement
            right_strings.animate.shift(DOWN * 0.2),
            run_time=2
        )
        self.wait(0.9)

class Scene05_09(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "THE PRICE TAG")
        
        # Illustration: Price Tag Transformation
        tag = RoundedRectangle(width=2.5, height=1.5, corner_radius=0.2, color="#FFFFFF", stroke_width=3).move_to([0, -1, 0])
        hole = Circle(radius=0.15, color="#FFFFFF").move_to([-0.9, -1, 0])
        free_text = Text("FREE", font="Arial", weight=BOLD, font_size=40).move_to([0.2, -1, 0])
        
        strike = Line([-1, -1, 0], [1.4, -1, 0], color="#FFFFFF", stroke_width=6).set_opacity(0)
        hidden_cost = Text("$ 99.99", font="Arial", weight=BOLD, font_size=35).move_to([0.2, -1, 0]).set_opacity(0)

        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(tag), Create(hole), run_time=1)
        self.play(Write(free_text), run_time=1)
        self.wait(1)
        self.play(strike.animate.set_opacity(1).set_stroke(width=8), run_time=0.8)
        self.play(
            free_text.animate.shift(UP * 0.4).set_opacity(0.3),
            hidden_cost.animate.set_opacity(1).shift(DOWN * 0.2),
            run_time=1.5
        )
        self.wait(1.6)

class Scene05_10(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "THE BAIT")
        
        # Illustration: Literal Mousetrap
        base = Rectangle(width=3, height=0.4, color="#FFFFFF", fill_opacity=0.1).move_to([0, -2, 0])
        spring = Arc(radius=0.3, start_angle=0, angle=PI, color="#FFFFFF").move_to([0, -1.7, 0])
        bar = Line([-1.2, -1.8, 0], [1.2, -1.8, 0], color="#FFFFFF", stroke_width=4)
        
        cheese = Polygon([-0.3, -1.8, 0], [0.3, -1.8, 0], [0, -1.3, 0], color="#FFFFFF", fill_opacity=1)
        label = Text("FREE GIFT", font_size=20).next_to(cheese, UP, buff=0.3)
        
        snap_arm = Line([0, -1.7, 0], [-1.4, -1.0, 0], color="#FFFFFF", stroke_width=3)

        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(base), Create(bar), run_time=1)
        self.play(Create(spring), Create(snap_arm), run_time=1)
        self.play(FadeIn(cheese, shift=UP), Write(label), run_time=1.5)
        
        # The "Snap" animation
        self.play(
            snap_arm.animate.rotate(-1.2, about_point=[0, -1.7, 0]),
            label.animate.scale(1.2).set_opacity(0.5),
            run_time=0.4, rate_func=exponential_decay
        )
        self.wait(3.0)

class Scene05_11(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "THE CATCH")
        
        # Illustration: Fishing Hook and Gift
        hook = VGroup(
            Line([0, 1, 0], [0, -1, 0]),
            Arc(radius=0.4, start_angle=PI, angle=1.5*PI),
            Line([-0.4, -1.4, 0], [-0.2, -1.2, 0])
        ).move_to([0, 0, 0]).set_stroke(width=4)
        
        gift_box = Rectangle(width=1.2, height=1.0, color="#FFFFFF", fill_opacity=0.1).move_to([0, -1.8, 0])
        ribbon_v = Line([0, -1.3, 0], [0, -2.3, 0])
        ribbon_h = Line([-0.6, -1.8, 0], [0.6, -1.8, 0])
        gift = VGroup(gift_box, ribbon_v, ribbon_h)
        
        free_label = Text("FREE", font_size=24).move_to(gift_box.get_center())

        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)
        self.play(gift.animate.shift(UP * 0), FadeIn(gift), Write(free_label), run_time=1)
        self.play(hook.animate.shift(DOWN * 0.5), run_time=1.5)
        
        # Hooking the gift
        self.play(
            VGroup(hook, gift, free_label).animate.shift(UP * 1.5),
            run_time=2,
            rate_func=running_start
        )
        catch_text = Text("THE CATCH", font_size=20).move_to([0, -2, 0])
        self.play(Write(catch_text), run_time=1)
        self.wait(1.4)

class Scene05_12(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "TIME IS CURRENCY")
        
        # Illustration: Hourglass
        top_tri = Polygon([-1, 0, 0], [1, 0, 0], [0, -0.8, 0], color="#FFFFFF", stroke_width=3)
        bot_tri = Polygon([-1, -1.6, 0], [1, -1.6, 0], [0, -0.8, 0], color="#FFFFFF", stroke_width=3)
        frame_l = Line([-1.1, 0.1, 0], [-1.1, -1.7, 0])
        frame_r = Line([1.1, 0.1, 0], [1.1, -1.7, 0])
        
        sand_top = Polygon([-0.8, -0.1, 0], [0.8, -0.1, 0], [0, -0.8, 0], fill_opacity=0.8, color="#FFFFFF")
        sand_bot = Polygon([0, -0.8, 0], [0, -0.8, 0], [0, -0.8, 0], fill_opacity=0.8, color="#FFFFFF") # Start empty
        
        free_text = Text("FREE", font_size=20).move_to([0, 0.4, 0])
        time_text = Text("YOUR TIME", font_size=20).move_to([0, -2.1, 0])

        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(top_tri), Create(bot_tri), Create(frame_l), Create(frame_r), run_time=1)
        self.play(FadeIn(sand_top), Write(free_text), Write(time_text), run_time=1)
        
        # Sand falling
        self.play(
            sand_top.animate.scale(0.1, about_point=[0, -0.8, 0]).set_opacity(0),
            sand_bot.animate.become(Polygon([-0.8, -1.5, 0], [0.8, -1.5, 0], [0, -0.8, 0], fill_opacity=0.8, color="#FFFFFF")),
            run_time=4
        )
        self.wait(0.9)

class Scene05_13(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "HIDDEN DATA")
        
        # Illustration: Phone and Server
        phone = RoundedRectangle(width=1.2, height=2.2, corner_radius=0.1).move_to([-1.5, -1, 0])
        screen = Rectangle(width=1.0, height=1.6).move_to([-1.5, -1, 0])
        app_icon = Square(side_length=0.4).move_to([-1.5, -0.8, 0])
        app_text = Text("FREE", font_size=10).move_to([-1.5, -1.2, 0])
        
        server = VGroup(
            Rectangle(width=1.5, height=0.5),
            Rectangle(width=1.5, height=0.5).shift(DOWN*0.6),
            Rectangle(width=1.5, height=0.5).shift(DOWN*1.2)
        ).move_to([1.5, -0.7, 0])
        
        arrow1 = DashedLine([-0.8, -0.5, 0], [0.7, -0.5, 0], dash_length=0.1).add_tip()
        arrow2 = DashedLine([-0.8, -1.0, 0], [0.7, -1.0, 0], dash_length=0.1).add_tip()
        
        data_label = Text("YOUR DATA", font_size=14).move_to([0, -0.2, 0])

        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(phone), Create(screen), FadeIn(app_icon), Write(app_text), run_time=1.5)
        self.play(Create(server), run_time=1.5)
        self.play(Write(data_label), run_time=0.8)
        self.play(Create(arrow1), Create(arrow2), run_time=2)
        self.wait(1.1)

class Scene05_14(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "THE FINE PRINT")
        
        # Illustration: Contract with Magnifying Glass
        paper = Rectangle(width=2.5, height=3, color="#FFFFFF").move_to([0, -1, 0])
        lines = VGroup(*[Line([-1, -0.5 - i*0.3, 0], [1, -0.5 - i*0.3, 0], stroke_width=1) for i in range(6)])
        header = Text("FREE CONTRACT", font_size=18, weight=BOLD).move_to([0, 0.2, 0])
        
        mag_glass_circle = Circle(radius=0.6, color="#FFFFFF", stroke_width=4, fill_opacity=0.1).move_to([0.5, -1.2, 0])
        mag_handle = Line([0.9, -1.6, 0], [1.4, -2.1, 0], stroke_width=6)
        mag_glass = VGroup(mag_glass_circle, mag_handle)
        
        hidden_text = Text("COSTS EVERYTHING", font_size=10).move_to(mag_glass_circle.get_center())

        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)
        self.play(Create(paper), Write(header), run_time=1.5)
        self.play(Create(lines), run_time=1.5)
        self.play(FadeIn(mag_glass, shift=LEFT), run_time=1.5)
        self.play(Write(hidden_text), mag_glass_circle.animate.scale(1.2), run_time=1.5)
        self.wait(0.9)

# CANVAS CONFIGURATION

# (Using universal get_footer_and_title from manim_compat)

class Scene05_15(Scene):
    def construct(self):
        # Setup
        title, footer_line, left_text, right_text = get_footer_and_title( "NOTHING IS FREE")
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Price Tag on a Gift
        gift_box = RoundedRectangle(corner_radius=0.1, width=2, height=1.5, color=WHITE, stroke_width=4).move_to(DOWN * 0.8)
        ribbon_v = Line(gift_box.get_top(), gift_box.get_bottom(), color=WHITE)
        ribbon_h = Line(gift_box.get_left(), gift_box.get_right(), color=WHITE)
        gift = VGroup(gift_box, ribbon_v, ribbon_h)
        
        tag = Polygon([0,0,0], [0.8,0.4,0], [0.8,-0.4,0], [0,-0.8,0], color=WHITE, stroke_width=3).move_to(UP * 0.2 + RIGHT * 1.2)
        tag_hole = Circle(radius=0.05, color=WHITE).move_to(tag.get_left() + RIGHT * 0.15)
        tag_text = Text("FREE", font="Arial", font_size=14).move_to(tag.get_center())
        price_tag = VGroup(tag, tag_hole, tag_text)
        
        strike = Line(tag_text.get_left(), tag_text.get_right(), color=WHITE, stroke_width=4)
        cost_text = Text("$$$", font="Arial", font_size=18, weight=BOLD).next_to(tag, UP, buff=0.2)

        # Animation
        self.play(Create(gift), run_time=1.5)
        self.play(FadeIn(price_tag, shift=LEFT), run_time=1.0)
        self.wait(0.5)
        self.play(Create(strike), run_time=0.5)
        self.play(Write(cost_text), run_time=1.0)
        self.wait(2.4)

class Scene05_16(Scene):
    def construct(self):
        # Setup
        title, footer_line, left_text, right_text = get_footer_and_title( "NOTHING IS FREE")
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Balance Scale
        base = Triangle(color=WHITE).scale(0.3).move_to(DOWN * 2)
        beam = Line(LEFT * 2.5, RIGHT * 2.5, color=WHITE, stroke_width=5).move_to(DOWN * 1.2)
        left_pan = Circle(radius=0.6, color=WHITE).move_to(beam.get_left() + DOWN * 0.6)
        right_pan = Circle(radius=0.6, color=WHITE).move_to(beam.get_right() + DOWN * 0.6)
        
        free_label = Text("FREE", font_size=15).move_to(left_pan.get_center())
        cost_weight = Square(side_length=0.8, color=WHITE, fill_opacity=1).move_to(UP * 1)
        cost_label = Text("COST", font_size=15, color=BLACK).move_to(cost_weight.get_center())
        weight_grp = VGroup(cost_weight, cost_label)

        scale_grp = VGroup(beam, left_pan, right_pan, free_label)

        # Animation
        self.add(base)
        self.play(Create(scale_grp), run_time=1.5)
        self.play(weight_grp.animate.move_to(right_pan.get_center()), run_time=1.5)
        self.play(
            beam.animate.rotate(0.3),
            left_pan.animate.shift(UP * 0.7 + RIGHT * 0.1),
            right_pan.animate.shift(DOWN * 0.7 + LEFT * 0.1),
            weight_grp.animate.shift(DOWN * 0.7 + LEFT * 0.1),
            free_label.animate.shift(UP * 0.7 + RIGHT * 0.1),
            run_time=1.0
        )
        self.wait(2.9)

class Scene05_17(Scene):
    def construct(self):
        # Setup
        title, footer_line, left_text, right_text = get_footer_and_title( "NOTHING IS FREE")
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Mouse Trap
        trap_base = Rectangle(width=3, height=0.4, color=WHITE).move_to(DOWN * 1.5)
        spring = Arc(radius=0.4, start_angle=0, angle=PI, color=WHITE).next_to(trap_base, UP, buff=0)
        cheese = Triangle(color=WHITE, fill_opacity=0.5).scale(0.4).move_to(UP * 0.2)
        bait_text = Text("FREE", font_size=18, weight=BOLD).next_to(cheese, UP, buff=0.1)
        
        snap_bar = Line(LEFT * 1.2, RIGHT * 1.2, color=WHITE, stroke_width=6).move_to(UP * 0.5)

        # Animation
        self.play(Create(trap_base), Create(spring), run_time=1.5)
        self.play(FadeIn(cheese), Write(bait_text), run_time=1.5)
        self.wait(1.0)
        self.play(snap_bar.animate.move_to(cheese.get_center()), run_time=0.2)
        self.play(Flash(cheese, color=WHITE, line_length=0.3), run_time=0.5)
        self.wait(2.7)

class Scene05_18(Scene):
    def construct(self):
        # Setup
        title, footer_line, left_text, right_text = get_footer_and_title( "NOTHING IS FREE")
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Data Intake Pipe
        user_phone = RoundedRectangle(width=1.2, height=2.2, corner_radius=0.1, color=WHITE).move_to(LEFT * 1.8 + DOWN * 0.8)
        screen = Rectangle(width=1.0, height=1.8, color=WHITE).move_to(user_phone.get_center())
        free_app = Text("FREE\nAPP", font_size=12).move_to(screen.get_center())
        
        server = Rectangle(width=1.5, height=1.5, color=WHITE).move_to(RIGHT * 1.8 + DOWN * 0.8)
        server_lines = VGroup(*[Line(LEFT*0.5, RIGHT*0.5).move_to(server.get_center() + UP*i) for i in [-0.3, 0, 0.3]])
        
        pipe = DoubleArrow(user_phone.get_right(), server.get_left(), color=WHITE, buff=0.2)
        data_label = Text("USER DATA", font_size=14).next_to(pipe, UP, buff=0.1)

        # Animation
        self.play(Create(user_phone), Create(screen), Write(free_app), run_time=1.5)
        self.play(Create(server), Create(server_lines), run_time=1.5)
        self.play(GrowFromCenter(pipe), Write(data_label), run_time=1.0)
        
        # Flowing dots
        dots = VGroup(*[Circle(radius=0.05, color=WHITE, fill_opacity=1) for _ in range(5)])
        self.play(
            Succession(*[MoveAlongPath(dot, Line(user_phone.get_right(), server.get_left())) for dot in dots]),
            run_time=2.0, rate_func=linear
        )
        self.wait(0.9)

class Scene05_19(Scene):
    def construct(self):
        # Setup
        title, footer_line, left_text, right_text = get_footer_and_title( "NOTHING IS FREE")
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Long Receipt (Hidden Bill)
        gift = RoundedRectangle(width=1.5, height=1, color=WHITE).move_to(UP * 0.2)
        gift_label = Text("FREE GIFT", font_size=15).move_to(gift.get_center())
        
        receipt = Rectangle(width=1.2, height=3.5, color=WHITE, fill_opacity=0.1).move_to(DOWN * 2)
        receipt_lines = VGroup(*[Line(LEFT*0.4, RIGHT*0.4, stroke_width=1).move_to(receipt.get_top() + DOWN*(0.3 + i*0.25)) for i in range(12)])
        total = Text("TOTAL: $$$", font_size=12, weight=BOLD).move_to(receipt.get_bottom() + UP * 0.3)

        # Animation
        self.play(Create(gift), Write(gift_label), run_time=1.5)
        self.wait(0.5)
        self.play(receipt.animate.shift(UP * 1.5), run_time=2.0)
        self.play(Create(receipt_lines), Write(total), run_time=2.0)
        self.wait(0.9)

class Scene05_20(Scene):
    def construct(self):
        # Setup
        title, footer_line, left_text, right_text = get_footer_and_title( "NOTHING IS FREE")
        self.add(footer_line, left_text, right_text)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Fishing Hook with "Free" Bait
        line = Line(UP * 1, DOWN * 0.5, color=WHITE).move_to(UP * 0.5)
        hook = Arc(radius=0.3, start_angle=PI, angle=1.5*PI, color=WHITE).next_to(line, DOWN, buff=0)
        hook_tip = Arrow(hook.get_end(), hook.get_end() + UP*0.1, color=WHITE, stroke_width=2)
        
        bait = RoundedRectangle(width=1.2, height=0.6, color=WHITE, fill_opacity=1).move_to(hook.get_center() + DOWN * 0.2)
        bait_text = Text("FREE", font_size=16, color=BLACK, weight=BOLD).move_to(bait.get_center())
        
        fishing_rig = VGroup(line, hook, hook_tip, bait, bait_text)

        # Animation
        self.play(fishing_rig.animate.shift(DOWN * 0.5), run_time=1.5, rate_func=slow_into)
        self.wait(1.0)
        # Bobbing animation
        self.play(fishing_rig.animate.shift(UP * 0.2), run_time=0.5)
        self.play(fishing_rig.animate.shift(DOWN * 0.2), run_time=0.5)
        self.wait(0.5)
        # The "Catch"
        self.play(fishing_rig.animate.shift(UP * 3), run_time=0.8, rate_func=anticipate)
        self.wait(2.1)