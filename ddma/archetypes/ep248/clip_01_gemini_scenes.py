import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)

class Scene01_03_CheckbookBalance(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "BALANCING THE CHECKBOOK", "ECONOMIC AUTONOMY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Visual: Balance Scale
        base = Line(DOWN * 2, DOWN * 1, color="#FFFFFF")
        pivot = Triangle(color="#FFFFFF").scale(0.2).move_to(DOWN * 1)
        beam = Line(LEFT * 2, RIGHT * 2, color="#FFFFFF").move_to(DOWN * 0.8)
        
        # Left Pan: Robot Arm
        left_pan = Line(LEFT * 0.5, RIGHT * 0.5, color="#FFFFFF").move_to(beam.get_left() + DOWN * 0.5)
        arm = VGroup(
            Line(ORIGIN, UP * 0.5), Circle(radius=0.05), Line(UP * 0.5, UP * 0.8 + RIGHT * 0.3)
        ).scale(0.7).next_to(left_pan, UP, buff=0)
        
        # Right Pan: Checkbook
        right_pan = Line(LEFT * 0.5, RIGHT * 0.5, color="#FFFFFF").move_to(beam.get_right() + DOWN * 0.5)
        checkbook = RoundedRectangle(width=0.8, height=0.5, corner_radius=0.05, color="#FFFFFF")
        dollar = Text("$", font="Arial", font_size=18, color="#FFFFFF").move_to(checkbook.get_center())
        ledger = VGroup(checkbook, dollar).next_to(right_pan, UP, buff=0)

        scale_system = VGroup(beam, left_pan, arm, right_pan, ledger)
        self.add(base, pivot, scale_system)
        
        # Tipping animation
        self.play(
            Rotate(scale_system, angle=-15 * DEGREES, about_point=pivot.get_top()),
            run_time=1.4,
            rate_func=ease_in_out_sine
        )
        self.wait(5.0)

class Scene01_04_MacroDisruption(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "SYSTEMIC DISRUPTION", "MACROECONOMIC SHIFT")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Flow chart nodes
        center_node = Circle(radius=0.3, color="#FFFFFF", stroke_width=4).move_to(UP * -1)
        nodes = VGroup(*[Circle(radius=0.15, color="#FFFFFF").move_to([np.cos(a)*1.8, np.sin(a)*1.2 - 1, 0]) for a in np.linspace(0, 2*PI, 7, endpoint=False)])
        lines = VGroup(*[Line(center_node.get_center(), n.get_center(), color="#FFFFFF").set_opacity(0.3) for n in nodes])
        
        self.add(center_node, nodes, lines)
        
        # Pulse wave
        pulse = Circle(radius=0.1, color="#FFFFFF", stroke_width=2).move_to(center_node.get_center())
        
        self.play(
            pulse.animate.scale(30).set_stroke(width=0, opacity=0),
            center_node.animate.scale(1.2).set_stroke(width=8),
            *[l.animate.set_stroke(width=4).set_opacity(1) for l in lines],
            run_time=1.4
        )
        self.wait(5.0)

class Scene01_05_ThermodynamicReality(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "THERMODYNAMIC REALITY", "ENERGY SUSTENANCE")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Battery Meter
        battery_case = RoundedRectangle(width=1.5, height=2.5, corner_radius=0.1, color="#FFFFFF")
        battery_tip = Rectangle(width=0.4, height=0.15, color="#FFFFFF").next_to(battery_case, UP, buff=0)
        fill = Rectangle(width=1.3, height=0.1, color="#FFFFFF", fill_opacity=1).move_to(battery_case.get_bottom() + UP * 0.2)
        
        gauge_lines = VGroup(*[Line(LEFT*0.2, RIGHT*0.2, color="#FFFFFF").move_to(battery_case.get_left() + UP * y) for y in np.linspace(-1, 1, 6)])
        
        # Heat waves
        waves = VGroup(*[Arc(radius=0.3, start_angle=0, angle=PI, color="#FFFFFF").rotate(PI/2).move_to(battery_case.get_right() + RIGHT * 0.4 + UP * i * 0.5) for i in range(-1, 2)])
        waves.set_opacity(0.4)

        self.add(battery_case, battery_tip, gauge_lines, fill)
        
        self.play(
            fill.animate.stretch_to_fit_height(2.0).move_to(battery_case.get_center() + DOWN * 0.1),
            waves.animate.shift(UP * 0.3).set_opacity(0),
            run_time=2.4,
            rate_func=linear
        )
        self.wait(5.0)

class Scene01_06_OntologicalFallacy(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "THE ONTOLOGICAL FALLACY", "ISOLATION ≠ AUTONOMY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Fortress Wall
        wall = Rectangle(width=2.5, height=2.5, color="#FFFFFF", stroke_width=8).move_to(UP * -1)
        
        # Robot inside
        head = Circle(radius=0.15, color="#FFFFFF").move_to(wall.get_center() + UP * 0.3)
        body = Rectangle(width=0.4, height=0.5, color="#FFFFFF").next_to(head, DOWN, buff=0.1)
        robot = VGroup(head, body)
        
        # Outside lines
        outside_lines = VGroup(*[DashedLine(LEFT * 4, RIGHT * 4, color="#FFFFFF").move_to(UP * y) for y in [0, 0.5, -2, -2.5]])
        outside_lines.set_opacity(0.3)

        self.add(wall, robot, outside_lines)
        
        self.play(
            outside_lines.animate.shift(RIGHT * 2),
            robot.animate.scale(0.9),
            run_time=2.4,
            rate_func=linear
        )
        self.wait(5.0)

class Scene01_07_SeveredIndependence(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "CONFUSION OF CONCEPTS", "FALSE ISOLATION")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Path A: Isolation
        path_a = Line(LEFT * 3, LEFT * 0.5, color="#FFFFFF").move_to(UP * -0.5 + LEFT * 1.5)
        label_a = Text("ISOLATION", font="Arial", font_size=12, color="#FFFFFF").next_to(path_a, UP)
        severed = VGroup(Line(UP*0.2+LEFT*0.2, DOWN*0.2+RIGHT*0.2), Line(DOWN*0.2+LEFT*0.2, UP*0.2+RIGHT*0.2)).move_to(path_a.get_right() + RIGHT * 0.3)
        
        # Path B: Interdependence
        path_b = Circle(radius=0.6, color="#FFFFFF").move_to(UP * -0.5 + RIGHT * 1.5)
        label_b = Text("INTERDEPENDENCE", font="Arial", font_size=12, color="#FFFFFF").next_to(path_b, UP)
        circuit_arrows = VGroup(*[Arrow(color="#FFFFFF", stroke_width=2).scale(0.5) for _ in range(3)])

        self.add(path_a, label_a, severed, path_b, label_b)
        
        self.play(
            ShowCreationThenFadeOut(circuit_arrows),
            path_b.animate.set_stroke(width=4),
            run_time=1.4
        )
        self.wait(5.0)

class Scene01_08_BiologicalReality(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "BIOLOGICAL REALITY", "INPUT DEPENDENCE")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Human Silhouette
        head = Circle(radius=0.2, color="#FFFFFF").move_to(UP * -0.5)
        body = Line(UP * -0.7, UP * -1.5, color="#FFFFFF")
        arms = Line(LEFT * 0.5, RIGHT * 0.5, color="#FFFFFF").move_to(UP * -0.9)
        legs = VGroup(Line(UP*-1.5, DOWN*2+LEFT*0.3), Line(UP*-1.5, DOWN*2+RIGHT*0.3)).move_to(UP * -1.8)
        human = VGroup(head, body, arms, legs)
        
        # Inputs
        inputs = VGroup(
            VGroup(Arrow(LEFT*2, LEFT*0.5), Text("FOOD", font_size=10)).move_to(UP*0 + LEFT*1.5),
            VGroup(Arrow(LEFT*2, LEFT*0.5), Text("WATER", font_size=10)).move_to(UP*-1 + LEFT*1.5),
            VGroup(Arrow(RIGHT*2, RIGHT*0.5), Text("SHELTER", font_size=10)).move_to(UP*-0.5 + RIGHT*1.5)
        )

        self.add(human)
        self.play(LaggedStart(*[FadeIn(i, shift=RIGHT*0.5) for i in inputs], lag_ratio=0.4), run_time=2.4)
        self.wait(5.0)

class Scene01_09_CaloricStarvation(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "COLLAPSE IN ISOLATION", "SUPPLY CHAIN CUT")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Heart rate monitor
        hr_line = VMobject(color="#FFFFFF")
        points = [LEFT*3 + DOWN*1, LEFT*2 + DOWN*1, LEFT*1.8 + UP*0.2, LEFT*1.6 + DOWN*1.8, LEFT*1.4 + DOWN*1, LEFT*0.5 + DOWN*1, LEFT*0.3 + UP*0.5, LEFT*0.1 + DOWN*2, RIGHT*0.1 + DOWN*1, RIGHT*3 + DOWN*2.2]
        hr_line.set_points_as_corners(points)
        
        # Severed supply arrows
        arrow1 = Arrow(UP*0.5+LEFT*1, UP*0.5+RIGHT*1, color="#FFFFFF")
        cross = VGroup(Line(UP*0.2+LEFT*0.2, DOWN*0.2+RIGHT*0.2), Line(DOWN*0.2+LEFT*0.2, UP*0.2+RIGHT*0.2)).move_to(arrow1.get_center())

        self.add(arrow1)
        self.play(Create(cross), run_time=0.4)
        self.play(Create(hr_line), run_time=2.0, rate_func=linear)
        self.wait(5.0)

class Scene01_10_AutopoiesisDefinition(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "AUTOPOIESIS: SELF-MAINTENANCE", "BOUNDARY INTEGRITY")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Double ring membrane
        outer = Circle(radius=1.5, color="#FFFFFF", stroke_width=2).move_to(UP * -1)
        inner = Circle(radius=1.2, color="#FFFFFF", stroke_width=1).move_to(UP * -1)
        
        # Internal struts
        struts = VGroup(*[Line(inner.point_at_angle(a), outer.point_at_angle(a), color="#FFFFFF").set_opacity(0.5) for a in np.linspace(0, 2*PI, 12)])

        self.add(outer, inner)
        self.play(
            LaggedStart(*[Create(s) for s in struts], lag_ratio=0.1),
            outer.animate.set_stroke(width=6),
            run_time=2.4
        )
        self.wait(5.0)

class Scene01_11_MetabolicLoop(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "OPEN METABOLIC LOOP", "ENVIRONMENTAL TRADE")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Core Engine
        core = RoundedRectangle(width=1, height=1, color="#FFFFFF", fill_opacity=0.1).move_to(UP * -1)
        gear = Circle(radius=0.3, color="#FFFFFF").move_to(core.get_center())
        
        # Loop
        intake = Arrow(LEFT*3 + UP*0, core.get_left(), color="#FFFFFF", buff=0.1)
        waste = Arrow(core.get_right(), RIGHT*3 + DOWN*2, color="#FFFFFF", buff=0.1)
        
        label_in = Text("RAW MATTER", font_size=12).next_to(intake, UP)
        label_out = Text("WASTE", font_size=12).next_to(waste, DOWN)

        self.add(core, gear, label_in, label_out)
        self.play(
            GrowArrow(intake),
            Rotate(gear, angle=2*PI),
            GrowArrow(waste),
            run_time=2.4
        )
        self.wait(5.0)

class Scene01_12_ComputeGridSurvival(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "THE DIGITAL COMPUTE GRID", "SERVER METABOLISM")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Server Rack
        rack = Rectangle(width=1.2, height=1.8, color="#FFFFFF").move_to(UP * -1)
        slots = VGroup(*[Line(rack.get_left()+RIGHT*0.1+UP*y, rack.get_right()+LEFT*0.1+UP*y) for y in np.linspace(-0.7, 0.7, 5)])
        
        # Connections
        power = Line(LEFT*3 + DOWN*1, rack.get_left(), color="#FFFFFF")
        socket = Square(side_length=0.3).move_to(LEFT*3 + DOWN*1)
        
        tokens = VGroup(*[Circle(radius=0.05, color="#FFFFFF", fill_opacity=1) for _ in range(5)])
        
        self.add(rack, slots, power, socket)
        self.play(
            LaggedStart(*[t.animate.move_to(rack.get_center()).set_opacity(0) for t in tokens], lag_ratio=0.2),
            rack.animate.set_fill(opacity=0.3),
            run_time=2.4
        )
        self.wait(5.0)

class Scene01_13_AutonomyEquilibrium(Scene):
    def construct(self):
        title, footer, left, right = get_footer_and_title( "ECONOMIC EQUILIBRIUM", "SOVEREIGN SURVIVAL")
        self.add(footer, left, right)
        self.play(FadeIn(title), run_time=0.6)

        # Equilibrium Balance
        beam = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF").move_to(UP * -1)
        pivot = Triangle().scale(0.2).move_to(UP * -1.2)
        
        rev_text = Text("REVENUE", font_size=15).move_to(LEFT * 1.5 + UP * -0.7)
        cost_text = Text("COSTS", font_size=15).move_to(RIGHT * 1.5 + UP * -0.7)
        
        math_label = Text("REVENUE ≥ COSTS", font="Arial", font_size=24).move_to(UP * 0.2)

        self.add(beam, pivot, rev_text, cost_text, math_label)
        self.play(
            beam.animate.rotate(10 * DEGREES),
            math_label.animate.scale(1.1),
            run_time=1.4
        )
        self.wait(5.0)