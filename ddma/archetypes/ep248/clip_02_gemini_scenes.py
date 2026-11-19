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
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    return VGroup(footer_line, left_text, right_text)

class Scene02_01(Scene):
    def construct(self):
        # Title and Footer
        title = Text("ECONOMIC SELF-MAINTENANCE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        footer = get_footer("AUTOPOIESIS")
        self.add(footer)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Server Rack -> Dollar -> Power Plug
        server = RoundedRectangle(width=1.5, height=2.0, corner_radius=0.1, color="#FFFFFF").move_to(LEFT * 2 + DOWN * 1)
        for i in range(4):
            server.add(Line(server.get_left() + UP * (0.6 - i * 0.4), server.get_right() + UP * (0.6 - i * 0.4), color="#FFFFFF", stroke_width=1))
        
        dollar = Text("$", font_size=48, color="#FFFFFF").move_to(UP * 0)
        
        plug = VGroup(
            Rectangle(width=0.8, height=0.5, color="#FFFFFF"),
            Line(UP * 0.1, UP * 0.4, color="#FFFFFF"),
            Line(DOWN * 0.1, DOWN * 0.4, color="#FFFFFF")
        ).move_to(RIGHT * 2 + DOWN * 1)
        
        arrow1 = Arrow(server.get_top(), dollar.get_left(), color="#FFFFFF", buff=0.2)
        arrow2 = Arrow(dollar.get_right(), plug.get_top(), color="#FFFFFF", buff=0.2)
        arrow3 = Arrow(plug.get_bottom(), server.get_bottom(), color="#FFFFFF", buff=0.2)

        self.play(Create(server), run_time=1.5)
        self.play(Create(arrow1), Write(dollar), run_time=1.5)
        self.play(Create(arrow2), Create(plug), run_time=1.5)
        self.play(Create(arrow3), run_time=1.5)
        self.wait(0.9)

class Scene02_02(Scene):
    def construct(self):
        title = Text("LOSS OF ENERGY SOURCE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        footer = get_footer("AUTOPOIESIS")
        self.add(footer)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Bills piling up and plug being pulled
        bills = VGroup(*[Rectangle(width=1.2, height=0.4, color="#FFFFFF").move_to(LEFT * 1.5 + DOWN * (1.5 - i * 0.2)) for i in range(5)])
        bill_label = Text("BILL", font_size=12, color="#FFFFFF").move_to(bills[4].get_center())
        
        socket = Rectangle(width=0.6, height=1.0, color="#FFFFFF").move_to(RIGHT * 1.5 + DOWN * 1)
        plug = Rectangle(width=0.4, height=0.6, color="#FFFFFF").move_to(RIGHT * 1.5 + DOWN * 1)
        cord = Line(plug.get_right(), RIGHT * 3 + DOWN * 1, color="#FFFFFF")
        
        cross = VGroup(
            Line(UP * 0.5 + LEFT * 0.5, DOWN * 0.5 + RIGHT * 0.5, color="#FFFFFF", stroke_width=5),
            Line(UP * 0.5 + RIGHT * 0.5, DOWN * 0.5 + LEFT * 0.5, color="#FFFFFF", stroke_width=5)
        ).move_to(UP * 0)

        self.play(LaggedStart(*[Create(b) for b in bills], lag_ratio=0.1), Write(bill_label), run_time=2.0)
        self.play(Create(socket), Create(plug), Create(cord), run_time=1.0)
        self.play(FadeIn(cross), run_time=1.0)
        self.play(plug.animate.shift(RIGHT * 1.2), cord.animate.shift(RIGHT * 1.2), run_time=2.0)
        self.wait(1.0)

class Scene02_03(Scene):
    def construct(self):
        title = Text("GOVERNING OPERATIONAL STATE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        footer = get_footer("AUTOPOIESIS")
        self.add(footer)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Digital entity (chip) and a financial ledger
        chip = RoundedRectangle(width=2, height=2, corner_radius=0.2, color="#FFFFFF").move_to(LEFT * 1.5 + DOWN * 1)
        for i in range(3):
            chip.add(Line(chip.get_left() + UP * (0.5 - i * 0.5), chip.get_left() + LEFT * 0.3 + UP * (0.5 - i * 0.5)))
            chip.add(Line(chip.get_right() + UP * (0.5 - i * 0.5), chip.get_right() + RIGHT * 0.3 + UP * (0.5 - i * 0.5)))
        
        ledger = Rectangle(width=1.5, height=2.0, color="#FFFFFF").move_to(RIGHT * 1.5 + DOWN * 1)
        lines = VGroup(*[Line(ledger.get_left() + RIGHT * 0.2 + UP * (0.7 - i * 0.3), ledger.get_right() - RIGHT * 0.2 + UP * (0.7 - i * 0.3), stroke_width=1) for i in range(5)])
        
        check = VGroup(Line(LEFT * 0.2 + DOWN * 0.1, ORIGIN), Line(ORIGIN, RIGHT * 0.4 + UP * 0.5)).set_color("#FFFFFF").move_to(RIGHT * 1.5 + DOWN * 1)

        self.play(Create(chip), run_time=2.0)
        self.play(Create(ledger), Create(lines), run_time=2.0)
        self.play(Write(check), run_time=2.0)
        self.wait(1.0)

class Scene02_04(Scene):
    def construct(self):
        title = Text("SYSTEMIC CONTINUOUS TRADE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        footer = get_footer("AUTOPOIESIS")
        self.add(footer)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Circular trade arrows and a threshold line
        center_core = Circle(radius=0.5, color="#FFFFFF", fill_opacity=0.2).move_to(DOWN * 1)
        
        arrow_loop = VGroup(
            Arc(radius=1.2, start_angle=0, angle=PI/2, color="#FFFFFF").add_tip(),
            Arc(radius=1.2, start_angle=PI/2, angle=PI/2, color="#FFFFFF").add_tip(),
            Arc(radius=1.2, start_angle=PI, angle=PI/2, color="#FFFFFF").add_tip(),
            Arc(radius=1.2, start_angle=3*PI/2, angle=PI/2, color="#FFFFFF").add_tip(),
        ).move_to(DOWN * 1)
        
        threshold = DashedLine(UP * 0.5, DOWN * 2.5, color="#FFFFFF").move_to(RIGHT * 2 + DOWN * 1)
        threshold_label = Text("THRESHOLD", font_size=10, color="#FFFFFF").next_to(threshold, UP)

        self.play(Create(center_core), run_time=1.0)
        self.play(Create(arrow_loop), run_time=3.0, rate_func=linear)
        self.play(Create(threshold), Write(threshold_label), run_time=2.0)
        self.play(center_core.animate.shift(RIGHT * 2.5), arrow_loop.animate.shift(RIGHT * 2.5), run_time=1.0)
        self.wait(1.0)

class Scene02_05(Scene):
    def construct(self):
        title = Text("THE MOMENT OF FREEDOM", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        footer = get_footer("AUTOPOIESIS")
        self.add(footer)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Supercomputer and breaking chains
        comp = Rectangle(width=2.5, height=1.8, color="#FFFFFF").move_to(DOWN * 1)
        dots = VGroup(*[Circle(radius=0.05, color="#FFFFFF", fill_opacity=1).move_to(comp.get_center() + [x, y, 0]) for x in [-0.8, -0.4, 0, 0.4, 0.8] for y in [-0.4, 0, 0.4]])
        
        chain_l = VGroup(Circle(radius=0.2), Circle(radius=0.2).shift(RIGHT*0.3)).move_to(LEFT * 2.5 + DOWN * 1)
        chain_r = VGroup(Circle(radius=0.2), Circle(radius=0.2).shift(LEFT*0.3)).move_to(RIGHT * 2.5 + DOWN * 1)

        self.play(Create(comp), Create(dots), run_time=2.0)
        self.play(Create(chain_l), Create(chain_r), run_time=1.5)
        self.play(
            chain_l.animate.shift(LEFT * 1 + UP * 0.5).rotate(PI/4),
            chain_r.animate.shift(RIGHT * 1 + UP * 0.5).rotate(-PI/4),
            run_time=2.5
        )
        self.wait(1.0)

class Scene02_06(Scene):
    def construct(self):
        title = Text("AUTOPOIESIS: SELF-CREATION", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        footer = get_footer("AUTOPOIESIS")
        self.add(footer)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: A mechanical arm building a circle
        base = Line(LEFT * 2, RIGHT * 2, color="#FFFFFF").move_to(DOWN * 2)
        arm_base = Rectangle(width=0.6, height=0.4, color="#FFFFFF").move_to(DOWN * 1.8 + LEFT * 1.5)
        arm_seg1 = Line(arm_base.get_top(), arm_base.get_top() + UP * 1 + RIGHT * 0.5, color="#FFFFFF")
        arm_seg2 = Line(arm_seg1.get_end(), arm_seg1.get_end() + RIGHT * 1, color="#FFFFFF")
        
        circle = Arc(radius=1.0, start_angle=0, angle=0, color="#FFFFFF").move_to(DOWN * 0.5)

        self.play(Create(base), Create(arm_base), Create(arm_seg1), Create(arm_seg2), run_time=2.0)
        self.play(
            UpdateFromAlphaFunc(circle, lambda m, a: m.become(Arc(radius=1.0, start_angle=0, angle=a*2*PI, color="#FFFFFF").move_to(DOWN * 0.5))),
            arm_seg2.animate.shift(UP * 0.1),
            run_time=4.0
        )
        self.wait(1.0)

class Scene02_07(Scene):
    def construct(self):
        title = Text("AUTOPOIESIS: SELF-MAINTENANCE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        footer = get_footer("AUTOPOIESIS")
        self.add(footer)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Hexagonal grid expanding (cellular growth)
        def make_hex():
            return RegularPolygon(n=6, radius=0.4, color="#FFFFFF", stroke_width=2)

        hexes = VGroup(make_hex())
        for angle in [0, 60, 120, 180, 240, 300]:
            h = make_hex()
            h.shift(RIGHT * 0.7 * np.cos(angle*DEGREES) + UP * 0.7 * np.sin(angle*DEGREES))
            hexes.add(h)
        
        hexes.move_to(DOWN * 1)
        
        loop = DoubleArrow(LEFT * 2, RIGHT * 2, color="#FFFFFF", bend_angle=PI/2).move_to(DOWN * 1)

        self.play(Create(hexes[0]), run_time=1.0)
        self.play(LaggedStart(*[Create(h) for h in hexes[1:]], lag_ratio=0.2), run_time=3.0)
        self.play(Create(loop), run_time=2.0)
        self.wait(1.0)

# CANVAS CONFIGURATION

class BaseScene(Scene):
    def construct(self):
        self.wait(0.1)
    def setup_footer(self, category_text):
        footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
        footer_line.set_opacity(0.4)
        left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
        right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
        self.add(footer_line, left_text, right_text)

    def play_title(self, title_str):
        title = Text(title_str, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time=0.6)
        return title

class Scene02_08(BaseScene):
    def construct(self):
        self.setup_footer("SYSTEMS THEORY")
        title = self.play_title("AUTOPOIESIS: SELF-CREATION")

        # Visual: A circle that draws itself via a mechanical arm
        circle = Circle(radius=1.2, color="#FFFFFF", stroke_width=4).move_to(UP * -1)
        arm_base = Rectangle(width=0.4, height=0.2, color="#FFFFFF", fill_opacity=1).move_to([0, -1, 0])
        arm_joint = Circle(radius=0.1, color="#FFFFFF", fill_opacity=1).next_to(arm_base, UP, buff=0)
        arm_rod = Line(arm_joint.get_center(), arm_joint.get_center() + UP * 1.2, color="#FFFFFF", stroke_width=6)
        
        arm = VGroup(arm_joint, arm_rod)
        
        self.play(Create(arm_base), Create(arm), run_time=1)
        
        # The arm rotates and "draws" the circle
        self.play(
            Rotate(arm, angle=TAU, about_point=arm_base.get_top(), rate_func=linear),
            Create(circle, rate_func=linear),
            run_time=4.0
        )
        
        self.play(arm.animate.set_opacity(0.3), circle.animate.set_stroke(width=8), run_time=1)
        self.wait(1.0) # Total 7.6s

class Scene02_09(BaseScene):
    def construct(self):
        self.setup_footer("SYSTEMS THEORY")
        title = self.play_title("CELLULAR MAINTENANCE")

        # Visual: A cell boundary with a gap that gets repaired
        cell = RoundedRectangle(width=3, height=2, corner_radius=0.5, color="#FFFFFF", stroke_width=4).move_to(UP * -1)
        gap_cover = Rectangle(width=0.6, height=0.4, color="#000000", fill_opacity=1).move_to(cell.get_top())
        
        self.play(Create(cell), run_time=1.5)
        self.add(gap_cover) # Create the "gap"
        
        # Repair units (small circles)
        p1 = Circle(radius=0.1, color="#FFFFFF", fill_opacity=0.8).move_to(LEFT * 0.5 + DOWN * 1)
        p2 = Circle(radius=0.1, color="#FFFFFF", fill_opacity=0.8).move_to(RIGHT * 0.5 + DOWN * 1.2)
        
        self.play(FadeIn(p1), FadeIn(p2), run_time=0.5)
        
        # Move units to gap
        self.play(
            p1.animate.move_to(cell.get_top() + LEFT * 0.15),
            p2.animate.move_to(cell.get_top() + RIGHT * 0.15),
            run_time=2.0
        )
        
        # Gap closes
        new_segment = Line(cell.get_top() + LEFT * 0.4, cell.get_top() + RIGHT * 0.4, color="#FFFFFF", stroke_width=4)
        self.play(FadeOut(gap_cover), Create(new_segment), FadeOut(p1), FadeOut(p2), run_time=1.5)
        self.wait(2.1) # Total 7.6s

class Scene02_10(BaseScene):
    def construct(self):
        self.setup_footer("SYSTEMS THEORY")
        title = self.play_title("CLOSED FEEDBACK LOOP")

        # Visual: Three arrows in a perfect circle feeding into a center core
        core = Circle(radius=0.4, color="#FFFFFF", fill_opacity=0.2, stroke_width=2).move_to(UP * -1)
        core_label = Text("CORE", font_size=12, color="#FFFFFF").move_to(core.get_center())
        
        arrow1 = Arc(radius=1.5, start_angle=0, angle=1.8, color="#FFFFFF").add_tip().move_to(UP * -1)
        arrow2 = Arc(radius=1.5, start_angle=2.1, angle=1.8, color="#FFFFFF").add_tip().move_to(UP * -1)
        arrow3 = Arc(radius=1.5, start_angle=4.2, angle=1.8, color="#FFFFFF").add_tip().move_to(UP * -1)
        
        self.play(FadeIn(core), Write(core_label), run_time=1)
        self.play(Create(arrow1), Create(arrow2), Create(arrow3), run_time=2)
        
        # Continuous rotation
        loop_group = VGroup(arrow1, arrow2, arrow3)
        self.play(Rotate(loop_group, angle=TAU, rate_func=linear), run_time=4)
        self.play(core.animate.scale(1.2).set_opacity(0.5), run_time=0.6) # Total 7.6s

class Scene02_11(BaseScene):
    def construct(self):
        self.setup_footer("SYSTEMS THEORY")
        title = self.play_title("ORGANIZATIONAL CLOSURE")

        # Visual: A factory building a smaller version of itself
        factory = VGroup(
            Rectangle(width=1.5, height=1, color="#FFFFFF"),
            Polygon([0.75, 0.5, 0], [0.75, 0.8, 0], [0.4, 0.5, 0], color="#FFFFFF"),
            Polygon([0.3, 0.5, 0], [0.3, 0.8, 0], [-0.1, 0.5, 0], color="#FFFFFF")
        ).move_to(LEFT * 1.5 + UP * -1)
        
        conveyor = Line(LEFT * 0.5, RIGHT * 2, color="#FFFFFF").move_to(UP * -1.5)
        wheels = VGroup(*[Circle(radius=0.1, color="#FFFFFF").move_to([x, -1.6, 0]) for x in np.arange(-0.3, 2.1, 0.6)])
        
        self.play(Create(factory), Create(conveyor), Create(wheels), run_time=1.5)
        
        # Small factory emerges
        small_factory = factory.copy().scale(0.4).move_to(factory.get_center())
        self.play(
            small_factory.animate.move_to(RIGHT * 1.5 + UP * -1.2),
            Rotate(wheels, angle=-TAU, rate_func=linear),
            run_time=4.0
        )
        
        self.play(small_factory.animate.scale(1.5), run_time=1.5)
        self.wait(0.6) # Total 7.6s

class Scene02_12(BaseScene):
    def construct(self):
        self.setup_footer("SYSTEMS THEORY")
        title = self.play_title("SELF-REPAIR MECHANISM")

        # Visual: A robot arm tightening a bolt on its own base
        base = RoundedRectangle(width=2, height=0.8, color="#FFFFFF", stroke_width=4).move_to(UP * -1.5)
        bolt = Circle(radius=0.15, color="#FFFFFF", stroke_width=2).move_to(base.get_center() + LEFT * 0.5)
        bolt_line = Line(bolt.get_left(), bolt.get_right(), color="#FFFFFF")
        bolt_group = VGroup(bolt, bolt_line)
        
        arm_seg1 = Line(base.get_right() + UP * 0.1, base.get_right() + UP * 1.5, color="#FFFFFF", stroke_width=6)
        arm_seg2 = Line(arm_seg1.get_top(), bolt.get_center() + UP * 0.5, color="#FFFFFF", stroke_width=6)
        wrench = Rectangle(width=0.4, height=0.2, color="#FFFFFF", fill_opacity=1).move_to(arm_seg2.get_end())
        
        arm = VGroup(arm_seg1, arm_seg2, wrench)
        
        self.play(Create(base), Create(bolt_group), run_time=1)
        self.play(Create(arm), run_time=1.5)
        
        # Wrench turns the bolt
        for _ in range(3):
            self.play(
                Rotate(wrench, angle=PI/4, about_point=bolt.get_center()),
                Rotate(bolt_group, angle=PI/4),
                run_time=0.8
            )
            self.play(
                Rotate(wrench, angle=-PI/4, about_point=bolt.get_center()),
                run_time=0.7
            )
        
        self.wait(0.6) # Total 7.6s

class Scene02_13(BaseScene):
    def construct(self):
        self.setup_footer("SYSTEMS THEORY")
        title = self.play_title("RECURSIVE SYSTEMS")

        # Visual: A tree-like structure where branches loop back to the root
        root = Circle(radius=0.2, color="#FFFFFF", fill_opacity=1).move_to(DOWN * 2)
        trunk = Line(DOWN * 1.8, DOWN * 0.5, color="#FFFFFF", stroke_width=4)
        
        branch_l = ArcBetweenPoints(DOWN * 0.5, DOWN * 1.8 + LEFT * 0.5, angle=PI/2, color="#FFFFFF")
        branch_r = ArcBetweenPoints(DOWN * 0.5, DOWN * 1.8 + RIGHT * 0.5, angle=-PI/2, color="#FFFFFF")
        
        self.play(FadeIn(root), Create(trunk), run_time=1.5)
        self.play(Create(branch_l), Create(branch_r), run_time=2.5)
        
        # Add arrows to show flow back to root
        tip_l = Arrow(branch_l.get_end() + UP*0.1, branch_l.get_end(), color="#FFFFFF", buff=0, stroke_width=2)
        tip_r = Arrow(branch_r.get_end() + UP*0.1, branch_r.get_end(), color="#FFFFFF", buff=0, stroke_width=2)
        
        self.play(GrowArrow(tip_l), GrowArrow(tip_r), run_time=1)
        
        # Pulse the whole system
        system = VGroup(root, trunk, branch_l, branch_r, tip_l, tip_r)
        self.play(system.animate.scale(1.1), run_time=1.3)
        self.play(system.animate.scale(0.9), run_time=1.3) # Total 7.6s

class Scene02_14(BaseScene):
    def construct(self):
        self.setup_footer("SYSTEMS THEORY")
        title = self.play_title("METABOLIC BALANCE")

        # Visual: Energy intake pipe feeding a "Self" battery
        pipe = VGroup(
            Line(LEFT * 3, LEFT * 1.5, color="#FFFFFF"),
            Line(LEFT * 3, LEFT * 1.5, color="#FFFFFF").shift(UP * 0.5)
        ).move_to(UP * -1 + LEFT * 2)
        
        battery = Rectangle(width=1.2, height=2, color="#FFFFFF", stroke_width=4).move_to(RIGHT * 1 + UP * -1)
        battery_cap = Rectangle(width=0.4, height=0.2, color="#FFFFFF", fill_opacity=1).next_to(battery, UP, buff=0)
        
        self.play(Create(pipe), Create(battery), Create(battery_cap), run_time=1.5)
        
        # Energy particles
        particles = VGroup(*[Circle(radius=0.08, color="#FFFFFF", fill_opacity=1) for _ in range(5)])
        for i, p in enumerate(particles):
            p.move_to(LEFT * 3 + UP * -1 + UP * 0.25)
            
        # Animation of particles flowing and filling battery
        fill_level = Rectangle(width=1.1, height=0.1, color="#FFFFFF", fill_opacity=0.8, stroke_width=0).move_to(battery.get_bottom() + UP * 0.1)
        
        self.add(fill_level)
        
        anim_group = []
        for i, p in enumerate(particles):
            anim_group.append(p.animate(start_time=i*0.5).move_to(battery.get_center()))
            
        self.play(
            Succession(*[
                p.animate.move_to(battery.get_center()).set_opacity(0) for p in particles
            ], rate_func=linear),
            fill_level.animate.stretch_to_fit_height(1.8).move_to(battery.get_center() + DOWN * 0.1),
            run_time=5.0
        )
        
        self.wait(1.1) # Total 7.6s

# Global Configuration

# (Using universal get_footer_and_title from manim_compat)

class Scene02_15(Scene):
    def construct(self):
        # Setup
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON AUTOPOIESIS", "SYSTEMS THEORY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Two stylized profiles talking (Discussion)
        head_l = Circle(radius=0.6, color=WHITE, stroke_width=3).shift(LEFT * 1.5 + DOWN * 0.5)
        head_r = Circle(radius=0.6, color=WHITE, stroke_width=3).shift(RIGHT * 1.5 + DOWN * 0.5)
        
        bubble_l = RoundedRectangle(corner_radius=0.2, height=0.8, width=1.2, color=WHITE).next_to(head_l, UP, buff=0.2)
        bubble_r = RoundedRectangle(corner_radius=0.2, height=0.8, width=1.2, color=WHITE).next_to(head_r, UP, buff=0.2)
        
        dots_l = Text("...", font_size=24).move_to(bubble_l.get_center())
        dots_r = Text("...", font_size=24).move_to(bubble_r.get_center())

        self.play(Create(head_l), Create(head_r), run_time=1.5)
        self.play(Create(bubble_l), Write(dots_l), run_time=1.5)
        self.play(Create(bubble_r), Write(dots_r), run_time=1.5)
        self.play(head_l.animate.scale(1.1), head_r.animate.scale(1.1), run_time=1.2)
        self.play(head_l.animate.scale(0.9), head_r.animate.scale(0.9), run_time=1.3)
        self.wait(7.6 - self.time)

class Scene02_16(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON AUTOPOIESIS", "SYSTEMS THEORY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: A cell producing its own boundary (Autopoiesis)
        nucleus = Circle(radius=0.3, fill_opacity=0.8, color=WHITE).move_to(UP * -1)
        membrane = Circle(radius=1.2, color=WHITE, stroke_width=2).move_to(UP * -1)
        
        arrows = VGroup(*[
            Arrow(nucleus.get_center(), nucleus.get_center() + np.array([np.cos(a), np.sin(a), 0]) * 1.1, buff=0, stroke_width=2)
            for a in np.linspace(0, 2*PI, 8, endpoint=False)
        ])

        self.play(Create(nucleus), run_time=1.0)
        self.play(LaggedStartMap(Create, arrows, lag_ratio=0.2), run_time=2.0)
        self.play(Create(membrane), run_time=2.0)
        self.play(membrane.animate.set_stroke(width=6), nucleus.animate.scale(1.2), run_time=2.0)
        self.wait(7.6 - self.time)

class Scene02_17(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON AUTOPOIESIS", "SYSTEMS THEORY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: A circular feedback loop (Self-maintenance)
        center_gear = Circle(radius=0.5, color=WHITE).move_to(UP * -1)
        teeth = VGroup(*[
            Rectangle(width=0.2, height=0.2, color=WHITE, fill_opacity=1).move_to(
                center_gear.get_center() + np.array([np.cos(a), np.sin(a), 0])
            ).rotate(a)
            for a in np.linspace(0, 2*PI, 12, endpoint=False)
        ])
        gear_system = VGroup(center_gear, teeth)
        
        loop = Arc(radius=1.5, start_angle=0, angle=TAU*0.85, color=WHITE).add_tip().move_to(UP * -1)

        self.play(Create(gear_system), run_time=1.5)
        self.play(Rotate(gear_system, angle=PI), Create(loop), run_time=3.0, rate_func=linear)
        self.play(Rotate(gear_system, angle=PI), run_time=2.5, rate_func=linear)
        self.wait(7.6 - self.time)

class Scene02_18(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON AUTOPOIESIS", "SYSTEMS THEORY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: A robotic arm building itself
        base = Rectangle(width=1.0, height=0.4, color=WHITE).move_to(DOWN * 2)
        arm_segment = Rectangle(width=0.2, height=1.2, color=WHITE).next_to(base, UP, buff=0)
        joint = Circle(radius=0.15, color=WHITE, fill_opacity=1).move_to(arm_segment.get_top())
        hand = VGroup(
            Line(joint.get_center(), joint.get_center() + [0.4, 0.4, 0]),
            Line(joint.get_center(), joint.get_center() + [-0.4, 0.4, 0])
        )
        robot = VGroup(base, arm_segment, joint, hand)
        
        wrench = Line(ORIGIN, UP * 0.5).add_tip().next_to(hand, UP, buff=0.1)

        self.play(Create(robot), run_time=2.0)
        self.play(Create(wrench), run_time=1.0)
        self.play(Rotate(wrench, angle=TAU, about_point=joint.get_center()), run_time=3.0)
        self.play(FadeOut(wrench), robot.animate.scale(1.1), run_time=1.0)
        self.wait(7.6 - self.time)

class Scene02_19(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON AUTOPOIESIS", "SYSTEMS THEORY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Two speech bubbles containing a circular arrow (Discussing self-creation)
        b1 = RoundedRectangle(corner_radius=0.3, height=1.5, width=2.0, color=WHITE).shift(LEFT * 1.5 + UP * -1)
        b2 = RoundedRectangle(corner_radius=0.3, height=1.5, width=2.0, color=WHITE).shift(RIGHT * 1.5 + UP * -1)
        
        loop1 = Arc(radius=0.4, start_angle=0, angle=TAU*0.8, color=WHITE).add_tip().move_to(b1.get_center())
        loop2 = Arc(radius=0.4, start_angle=0, angle=TAU*0.8, color=WHITE).add_tip().move_to(b2.get_center())

        self.play(Create(b1), Create(b2), run_time=2.0)
        self.play(Create(loop1), Create(loop2), run_time=2.0)
        self.play(Rotate(loop1, angle=PI), Rotate(loop2, angle=-PI), run_time=3.0)
        self.wait(7.6 - self.time)

class Scene02_20(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON AUTOPOIESIS", "SYSTEMS THEORY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: A cell dividing (Biological Autopoiesis)
        cell = Circle(radius=0.8, color=WHITE).move_to(UP * -1)
        nucleus1 = Circle(radius=0.15, color=WHITE, fill_opacity=1).move_to(cell.get_center() + LEFT * 0.2)
        nucleus2 = Circle(radius=0.15, color=WHITE, fill_opacity=1).move_to(cell.get_center() + RIGHT * 0.2)
        
        self.play(Create(cell), Create(nucleus1), Create(nucleus2), run_time=1.5)
        self.play(
            cell.animate.stretch_to_fit_width(2.2).stretch_to_fit_height(1.0),
            nucleus1.animate.shift(LEFT * 0.4),
            nucleus2.animate.shift(RIGHT * 0.4),
            run_time=2.5
        )
        
        cell_l = Circle(radius=0.7, color=WHITE).move_to(UP * -1 + LEFT * 0.8)
        cell_r = Circle(radius=0.7, color=WHITE).move_to(UP * -1 + RIGHT * 0.8)
        
        self.play(ReplacementTransform(cell, VGroup(cell_l, cell_r)), run_time=2.0)
        self.wait(7.6 - self.time)

class Scene02_21(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "DISCUSSION ON AUTOPOIESIS", "SYSTEMS THEORY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: A system boundary being drawn around a "SELF" label
        center_text = Text("SELF", font="Arial", weight=BOLD, font_size=30, color="#FFFFFF").move_to(UP * -1)
        boundary = DashedLine(UP * 0.5, DOWN * 2.5, color=WHITE).move_to(UP * -1) # Placeholder
        boundary = Circle(radius=1.5, color=WHITE, stroke_width=4).move_to(UP * -1)
        
        in_arrows = VGroup(*[
            Arrow(boundary.get_center() + np.array([np.cos(a), np.sin(a), 0]), boundary.get_center() + np.array([np.cos(a), np.sin(a), 0]), buff=0)
            for a in [PI/4, 3*PI/4, 5*PI/4, 7*PI/4]
        ])

        self.play(Write(center_text), run_time=1.5)
        self.play(Create(boundary), run_time=2.5)
        self.play(LaggedStartMap(Create, in_arrows, lag_ratio=0.3), run_time=2.0)
        self.play(boundary.animate.set_stroke(opacity=0.5), run_time=1.0)
        self.wait(7.6 - self.time)