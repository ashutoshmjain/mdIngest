import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Configure canvas for pure monochrome white-on-black and strict dimensions

def add_common_elements(scene, category_text="SYSTEMIC TURBULENCE"):
    """Adds the required bottom title, footer bar, and meta labels to maintain consistency."""
    # Bottom Title at y = -2.95 (Leaving upper canvas [0.5, 3.5] clear for captions)
    title = Text("INTENSE SYSTEMIC TURBULENCE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.4)

    # Footer bar and meta labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

class Scene22_01(Scene):
    def construct(self):
        add_common_elements(self, "PART 1 • OVERVIEW")
        
        # Literal "painting a picture" visual: An easel with a canvas showing a jagged turbulence wave
        easel_leg1 = Line(ORIGIN, DOWN * 2.2, color="#FFFFFF", stroke_width=3).shift(LEFT * 0.8 + UP * 0.2)
        easel_leg2 = Line(ORIGIN, DOWN * 2.2, color="#FFFFFF", stroke_width=3).shift(RIGHT * 0.8 + UP * 0.2)
        easel_spine = Line(UP * 1.5, DOWN * 2.2, color="#FFFFFF", stroke_width=2).shift(UP * 0.2)
        
        canvas = Rectangle(width=3.2, height=2.2, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.15).move_to(UP * 0.5)
        
        # Jagged turbulence lines inside canvas
        turb_line = VGroup(
            Line(canvas.get_corner(DL) + RIGHT * 0.3 + UP * 0.5, canvas.get_center() + LEFT * 0.8 + UP * 0.4, color="#FFFFFF", stroke_width=3),
            Line(canvas.get_center() + LEFT * 0.8 + UP * 0.4, canvas.get_center() + UP * 0.8, color="#FFFFFF", stroke_width=3),
            Line(canvas.get_center() + UP * 0.8, canvas.get_center() + RIGHT * 0.6 + DOWN * 0.3, color="#FFFFFF", stroke_width=3),
            Line(canvas.get_center() + RIGHT * 0.6 + DOWN * 0.3, canvas.get_corner(DR) + LEFT * 0.3 + UP * 0.7, color="#FFFFFF", stroke_width=3)
        )
        
        brush = Line(UP * 1.5, UP * 2.3, color="#FFFFFF", stroke_width=4).rotate(0.5).shift(RIGHT * 1.2 + UP * 0.2)
        
        easel_group = VGroup(easel_leg1, easel_leg2, easel_spine, canvas, turb_line, brush)
        
        self.play(FadeIn(easel_group, shift=UP * 0.3), run_time=1.5)
        self.play(Wiggle(turb_line, scale_value=1.1, rotation_angle=0.05), run_time=4.5)
        self.wait(1.0)

class Scene22_02(Scene):
    def construct(self):
        add_common_elements(self, "PART 1 • SYSTEMIC CRACK")

        # Literal "systemic structure cracking": A monolithic server rack/block fracturing down the middle
        rack = Rectangle(width=2.5, height=4.0, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.1).move_to(UP * -0.5)
        
        # Horizontal lines representing server slots
        slots = VGroup(*[
            Line(rack.get_left() + RIGHT * 0.2, rack.get_right() + LEFT * 0.2, color="#FFFFFF", stroke_width=1.5)
            for _ in range(6)
        ]).arrange(DOWN, buff=0.5).move_to(rack.get_center())
        
        # Jagged crack line running vertically through the center
        crack = VGroup(
            Line(UP * 1.7, UP * 1.0 + LEFT * 0.2, color="#FFFFFF", stroke_width=4),
            Line(UP * 1.0 + LEFT * 0.2, UP * 0.3 + RIGHT * 0.3, color="#FFFFFF", stroke_width=4),
            Line(UP * 0.3 + RIGHT * 0.3, DOWN * 0.5 + LEFT * 0.1, color="#FFFFFF", stroke_width=4),
            Line(DOWN * 0.5 + LEFT * 0.1, DOWN * 1.5 + RIGHT * 0.2, color="#FFFFFF", stroke_width=4),
            Line(DOWN * 1.5 + RIGHT * 0.2, DOWN * 2.3, color="#FFFFFF", stroke_width=4),
        )
        
        structure = VGroup(rack, slots, crack)
        
        self.play(Create(structure), run_time=2.0)
        # Shift halves apart slightly to show systemic failure
        self.play(
            rack.animate.set_opacity(0.05),
            crack.animate.scale(1.05),
            run_time=4.4
        )
        self.wait(1.0)

class Scene22_03(Scene):
    def construct(self):
        add_common_elements(self, "PART 1 • INTENSE WAVES")

        # Literal "intense systemic turbulence": Concentric shockwaves / violent oscillation waves
        center_dot = Circle(radius=0.15, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to(UP * -0.5)
        
        waves = VGroup(*[
            Circle(radius=r, color="#FFFFFF", stroke_width=2.5).move_to(UP * -0.5)
            for r in [0.8, 1.6, 2.4, 3.2]
        ])
        
        # Dashed erratic crosshairs/vectors cutting through waves
        v1 = DashedLine(UP * 2.5, DOWN * 3.0, color="#FFFFFF", stroke_width=2).move_to(UP * -0.5)
        v2 = DashedLine(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=2).move_to(UP * -0.5)

        turbulence_group = VGroup(center_dot, waves, v1, v2)

        self.play(FadeIn(center_dot), Create(waves), run_time=2.0)
        self.play(
            FadeIn(v1, v2),
            waves.animate.stretch(1.1, 0).stretch(0.9, 1),
            run_time=4.4
        )
        self.wait(1.0)

class Scene22_04(Scene):
    def construct(self):
        add_common_elements(self, "PART 1 • VOLATILITY")

        # Literal "volatile metrics": A chaotic stock/system meter bouncing wildly
        axis_box = Rectangle(width=6.0, height=3.5, color="#FFFFFF", stroke_width=2).move_to(UP * -0.5)
        
        # Wildly fluctuating polyline chart
        chart_line = VGroup(
            Line(LEFT * 2.7 + DOWN * 1.5, LEFT * 1.8 + UP * 0.8, color="#FFFFFF", stroke_width=3),
            Line(LEFT * 1.8 + UP * 0.8, LEFT * 0.9 + DOWN * 1.2, color="#FFFFFF", stroke_width=3),
            Line(LEFT * 0.9 + DOWN * 1.2, ORIGIN + UP * 1.3, color="#FFFFFF", stroke_width=3),
            Line(ORIGIN + UP * 1.3, RIGHT * 0.9 + DOWN * 1.8, color="#FFFFFF", stroke_width=3),
            Line(RIGHT * 0.9 + DOWN * 1.8, RIGHT * 1.8 + UP * 0.5, color="#FFFFFF", stroke_width=3),
            Line(RIGHT * 1.8 + UP * 0.5, RIGHT * 2.7 + DOWN * 0.2, color="#FFFFFF", stroke_width=3),
        ).move_to(UP * -0.5)

        # Warning marker arrows pointing at peaks
        arrow_up = Arrow(UP * 1.0, UP * 1.7, color="#FFFFFF", stroke_width=3, buff=0).move_to(ORIGIN + UP * 0.4)
        arrow_down = Arrow(DOWN * 1.0, DOWN * 1.8, color="#FFFFFF", stroke_width=3, buff=0).move_to(RIGHT * 0.9 + DOWN * 0.9)

        chart_group = VGroup(axis_box, chart_line, arrow_up, arrow_down)

        self.play(Create(axis_box), Create(chart_line), run_time=2.5)
        self.play(FadeIn(arrow_up), FadeIn(arrow_down), chart_line.animate.shift(UP * 0.1), run_time=3.9)
        self.wait(1.0)

class Scene22_05(Scene):
    def construct(self):
        add_common_elements(self, "PART 1 • PRESSURE TEST")

        # Literal "pressure scaling": A heavy vertical pressure gauge showing extreme levels
        gauge_body = RoundedRectangle(corner_radius=0.3, width=2.0, height=4.2, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.1).move_to(UP * -0.5)
        
        # Inner mercury/level bar filling up to the top (danger zone)
        fill_bar = Rectangle(width=1.4, height=3.2, color="#FFFFFF", stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.6).align_to(gauge_body, DOWN).shift(UP * 0.3)
        
        # Gauge tick marks
        ticks = VGroup(*[
            Line(gauge_body.get_left() + RIGHT * 0.1, gauge_body.get_left() + RIGHT * 0.5, color="#FFFFFF", stroke_width=2)
            for _ in range(6)
        ]).arrange(DOWN, buff=0.6).move_to(gauge_body.get_center())

        # Danger warning label box at top
        warning_box = Rectangle(width=3.0, height=0.6, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.3).move_to(UP * 1.9)
        warning_text = Text("HIGH PRESSURE", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(warning_box.get_center())

        gauge_group = VGroup(gauge_body, fill_bar, ticks, warning_box, warning_text)

        self.play(Create(gauge_body), FadeIn(ticks), run_time=1.5)
        self.play(GrowFromBottom(fill_bar), FadeIn(warning_box), FadeIn(warning_text), run_time=4.9)
        self.wait(1.0)

class Scene22_06(Scene):
    def construct(self):
        add_common_elements(self, "PART 1 • SYSTEMIC FRICTION")

        # Literal "systemic friction": Two heavy mechanical gear cogs grinding against each other with sparks/force arrows
        gear1 = Circle(radius=1.5, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.15).move_to(LEFT * 1.2 + UP * -0.5)
        gear2 = Circle(radius=1.5, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.15).move_to(RIGHT * 1.2 + UP * -0.5)
        
        # Center core axles
        axle1 = Circle(radius=0.3, color="#FFFFFF", stroke_width=2).move_to(gear1.get_center())
        axle2 = Circle(radius=0.3, color="#FFFFFF", stroke_width=2).move_to(gear2.get_center())

        # Force/friction opposing arrows between gears
        push_left = Arrow(ORIGIN + LEFT * 0.3 + UP * 0.5, ORIGIN + LEFT * 0.9 + UP * 0.5, color="#FFFFFF", stroke_width=3, buff=0)
        push_right = Arrow(ORIGIN + RIGHT * 0.3 + DOWN * 0.5, ORIGIN + RIGHT * 0.9 + DOWN * 0.5, color="#FFFFFF", stroke_width=3, buff=0)
        
        spark_center = Dot(color="#FFFFFF", point=UP * -0.5)

        gears_group = VGroup(gear1, gear2, axle1, axle2, push_left, push_right, spark_center)

        self.play(Create(gear1), Create(gear2), FadeIn(axle1), FadeIn(axle2), run_time=2.0)
        self.play(
            Rotate(gear1, angle=0.5, about_point=gear1.get_center()),
            Rotate(gear2, angle=-0.5, about_point=gear2.get_center()),
            FadeIn(push_left), FadeIn(push_right), FadeIn(spark_center),
            run_time=4.4
        )
        self.wait(1.0)

class Scene22_07(Scene):
    def construct(self):
        add_common_elements(self, "PART 1 • CONCLUSION")

        # Literal "intense systemic turbulence picture": A complete overview dashboard breaking down into warning blocks
        frame = Rectangle(width=6.5, height=4.2, color="#FFFFFF", stroke_width=2).move_to(UP * -0.5)
        
        # Inner warning grid boxes
        box1 = Rectangle(width=2.8, height=1.6, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).move_to(LEFT * 1.6 + UP * 0.2)
        box2 = Rectangle(width=2.8, height=1.6, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).move_to(RIGHT * 1.6 + UP * 0.2)
        box3 = Rectangle(width=6.0, height=1.4, color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.1).move_to(UP * -1.5)

        # Text/Visual indicators inside boxes
        alert_text1 = Text("TURBULENCE DETECTED", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(box1.get_center())
        alert_text2 = Text("SYSTEM UNSTABLE", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(box2.get_center())
        
        # Pulsing warning line inside bottom box
        warn_line = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=3).move_to(box3.get_center())

        dashboard = VGroup(frame, box1, box2, box3, alert_text1, alert_text2, warn_line)

        self.play(Create(frame), FadeIn(box1, box2, box3), run_time=2.0)
        self.play(FadeIn(alert_text1, alert_text2), Create(warn_line), run_time=2.4)
        self.play(dashboard.animate.scale(1.02), run_time=2.0)
        self.wait(1.0)

# Configure canvas strictly

def setup_scene_frame(scene, category_text):
    """Utility to set up standard bottom title, footer line, and meta labels."""
    title = Text("IT PAINTS A PICTURE OF INTENSE SYSTEMIC TURBULENCE", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

class Scene22_08(Scene):
    def construct(self):
        setup_scene_frame(self, "SYSTEMIC SHOCK WAVE")
        
        # Literal figurative visual: Central server/core shaking with concentric shock waves (turbulence)
        core = RoundedRectangle(corner_radius=0.2, width=1.6, height=1.6, color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([0, -1.0, 0])
        
        # Inner server details
        line1 = Line(LEFT*0.6, RIGHT*0.6, color="#FFFFFF", stroke_width=2).move_to(core.get_center() + UP*0.4)
        line2 = Line(LEFT*0.6, RIGHT*0.6, color="#FFFFFF", stroke_width=2).move_to(core.get_center() + DOWN*0.4)
        dot1 = Circle(radius=0.08, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1).move_to(core.get_center() + LEFT*0.4)
        server_group = VGroup(core, line1, line2, dot1)
        
        # Shockwaves (concentric jagged/curved rings)
        wave1 = Circle(radius=1.5, color="#FFFFFF", stroke_width=2).set_opacity(0.8).move_to([0, -1.0, 0])
        wave2 = Circle(radius=2.3, color="#FFFFFF", stroke_width=1.5).set_opacity(0.4).move_to([0, -1.0, 0])
        
        self.play(FadeIn(server_group, scale=0.8), run_time=1.0)
        self.play(GrowFromCenter(wave1), GrowFromCenter(wave2), run_time=1.5)
        
        # Shake effect representing turbulence
        self.play(
            server_group.animate.shift(LEFT * 0.2),
            wave1.animate.scale(1.05),
            run_time=0.4
        )
        self.play(
            server_group.animate.shift(RIGHT * 0.4),
            wave2.animate.scale(0.95),
            run_time=0.4
        )
        self.play(
            server_group.animate.shift(LEFT * 0.2),
            run_time=0.4
        )
        
        self.wait(3.3)

class Scene22_09(Scene):
    def construct(self):
        setup_scene_frame(self, "ERRATIC OSCILLATIONS")
        
        # Literal figurative visual: Wildly jagged upward/downward systemic graph lines
        axes_box = Rectangle(width=6.0, height=3.5, color="#FFFFFF", stroke_width=1.5).set_opacity(0.3).move_to([0, -1.0, 0])
        
        # Jagged turbulence path
        points = [
            [ -2.8, -2.0, 0 ],
            [ -2.0, -0.2, 0 ],
            [ -1.4, -2.2, 0 ],
            [ -0.8,  0.2, 0 ],
            [ -0.2, -1.8, 0 ],
            [  0.4,  0.6, 0 ],
            [  1.0, -1.5, 0 ],
            [  1.8,  0.0, 0 ],
            [  2.4, -2.5, 0 ],
            [  2.8, -0.8, 0 ]
        ]
        graph_line = VMobject(color="#FFFFFF", stroke_width=3.5)
        graph_line.set_points_as_corners(points)
        
        self.play(Create(axes_box), run_time=1.0)
        self.play(Create(graph_line), run_time=2.5)
        
        # Pulsing flash effect
        flash_box = Rectangle(width=6.0, height=3.5, color="#FFFFFF", stroke_width=3).set_opacity(0.8).move_to([0, -1.0, 0])
        self.play(FadeIn(flash_box), run_time=0.2)
        self.play(FadeOut(flash_box), run_time=0.5)
        
        self.wait(3.2)

class Scene22_10(Scene):
    def construct(self):
        setup_scene_frame(self, "STRUCTURAL PRESSURE")
        
        # Literal figurative visual: Heavy weights crushing a vertical pillar/structure
        base = Rectangle(width=4.0, height=0.4, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.5).move_to([0, -2.5, 0])
        pillar = Rectangle(width=1.2, height=2.2, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.2, stroke_width=2.5).move_to([0, -1.2, 0])
        
        # Crushing weight on top
        weight = RoundedRectangle(corner_radius=0.1, width=3.0, height=0.8, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.8, stroke_width=3).move_to([0, 0.3, 0])
        weight_hook = Arc(radius=0.4, start_angle=0, angle=PI, color="#FFFFFF", stroke_width=3).move_to([0, 0.7, 0])
        
        # Compression pressure arrows pointing inward from top and bottom of pillar
        arrow_down = Arrow(start=[0, 0.1, 0], end=[0, -0.4, 0], color="#FFFFFF", stroke_width=3, buff=0)
        arrow_up = Arrow(start=[0, -2.1, 0], end=[0, -1.7, 0], color="#FFFFFF", stroke_width=3, buff=0)
        
        weight_group = VGroup(weight, weight_hook)
        
        self.play(FadeIn(base), FadeIn(pillar), run_time=1.0)
        self.play(FadeIn(weight_group, shift=DOWN*0.5), run_time=1.2)
        
        # Squeeze/compress animation
        self.play(
            pillar.animate.stretch_to_fit_height(1.6).move_to([0, -1.5, 0]),
            weight_group.animate.shift(DOWN * 0.6),
            GrowArrow(arrow_down),
            GrowArrow(arrow_up),
            run_time=1.0
        )
        
        self.wait(4.2)

class Scene22_11(Scene):
    def construct(self):
        setup_scene_frame(self, "FRAGILE NETWORK NODES")
        
        # Literal figurative visual: A grid of interconnected nodes with lightning bolts breaking connections
        nodes_coords = [
            [-2.0, -0.5, 0], [0.0, 0.2, 0], [2.0, -0.5, 0],
            [-1.2, -2.0, 0], [1.2, -2.0, 0]
        ]
        
        dots = VGroup(*[Circle(radius=0.2, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.9).move_to(coord) for coord in nodes_coords])
        
        # Connecting lines
        line1 = Line(nodes_coords[0], nodes_coords[1], color="#FFFFFF", stroke_width=2)
        line2 = Line(nodes_coords[1], nodes_coords[2], color="#FFFFFF", stroke_width=2)
        line3 = Line(nodes_coords[0], nodes_coords[3], color="#FFFFFF", stroke_width=2)
        line4 = Line(nodes_coords[2], nodes_coords[4], color="#FFFFFF", stroke_width=2)
        line5 = Line(nodes_coords[3], nodes_coords[4], color="#FFFFFF", stroke_width=2)
        lines = VGroup(line1, line2, line3, line4, line5)
        
        # Lightning fracture in the middle
        fracture = VGroup(
            Line(nodes_coords[1], [0.5, -0.8, 0], color="#FFFFFF", stroke_width=4),
            Line([0.5, -0.8, 0], [-0.3, -1.2, 0], color="#FFFFFF", stroke_width=4),
            Line([-0.3, -1.2, 0], [0.2, -2.0, 0], color="#FFFFFF", stroke_width=4)
        )
        
        self.play(Create(lines), FadeIn(dots, lag_ratio=0.2), run_time=1.5)
        self.play(FadeOut(line2), FadeOut(line3), run_time=0.5)
        self.play(Create(fracture), run_time=1.0)
        
        # Flash breaking nodes
        self.play(dots[1].animate.set_fill(opacity=0.2), dots[3].animate.set_fill(opacity=0.2), run_time=0.8)
        
        self.wait(3.6)

class Scene22_12(Scene):
    def construct(self):
        setup_scene_frame(self, "CASCADING SYSTEM FAILURE")
        
        # Literal figurative visual: Dominino blocks falling sequentially over
        dominoes = VGroup()
        for i in range(5):
            d = Rectangle(width=0.3, height=1.8, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.7, stroke_width=2)
            d.move_to([-2.2 + i * 1.1, -1.0, 0])
            dominoes.add(d)
            
        self.play(FadeIn(dominoes, lag_ratio=0.15), run_time=1.5)
        
        # Tip them over sequentially
        self.play(dominoes[0].animate.rotate(-PI/3, about_point=dominoes[0].get_corner(DL)), run_time=0.4)
        self.play(dominoes[1].animate.rotate(-PI/2.5, about_point=dominoes[1].get_corner(DL)), run_time=0.3)
        self.play(dominoes[2].animate.rotate(-PI/2.2, about_point=dominoes[2].get_corner(DL)), run_time=0.3)
        self.play(dominoes[3].animate.rotate(-PI/2, about_point=dominoes[3].get_corner(DL)), run_time=0.3)
        self.play(dominoes[4].animate.rotate(-PI/2, about_point=dominoes[4].get_corner(DL)), run_time=0.3)
        
        self.wait(3.6)

class Scene22_13(Scene):
    def construct(self):
        setup_scene_frame(self, "OVERLOADED CIRCUITRY")
        
        # Literal figurative visual: Power meter gauge spiking straight into the red/max zone
        gauge_arc = Arc(radius=1.8, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=4).move_to([0, -1.5, 0])
        
        # Tick marks on gauge
        ticks = VGroup()
        for angle in np.linspace(PI, 0, 7):
            p1 = np.array([1.8 * np.cos(angle), 1.8 * np.sin(angle), 0]) + np.array([0, -1.5, 0])
            p2 = np.array([2.1 * np.cos(angle), 2.1 * np.sin(angle), 0]) + np.array([0, -1.5, 0])
            ticks.add(Line(p1, p2, color="#FFFFFF", stroke_width=2))
            
        # Needle pointing to max overload (right side)
        needle = Line([0, -1.5, 0], [1.5, -0.2, 0], color="#FFFFFF", stroke_width=4)
        center_pin = Circle(radius=0.2, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1).move_to([0, -1.5, 0])
        
        self.play(Create(gauge_arc), Create(ticks), run_time=1.2)
        self.play(FadeIn(center_pin), GrowFromPoint(needle, [0, -1.5, 0]), run_time=1.0)
        
        # Spike vibration
        for _ in range(3):
            self.play(needle.animate.rotate(0.1, about_point=[0, -1.5, 0]), run_time=0.15)
            self.play(needle.animate.rotate(-0.1, about_point=[0, -1.5, 0]), run_time=0.15)
            
        # Flash warning box
        warning = Rectangle(width=7.0, height=3.5, color="#FFFFFF", stroke_width=3).set_opacity(0.7).move_to([0, -1.0, 0])
        self.play(FadeIn(warning), run_time=0.2)
        self.play(FadeOut(warning), run_time=0.5)
        
        self.wait(2.7)

class Scene22_14(Scene):
    def construct(self):
        setup_scene_frame(self, "INTENSE SYSTEMIC TURBULENCE")
        
        # Literal figurative visual: Complex multi-layered chaotic vortex / storm rings
        ring1 = Circle(radius=0.8, color="#FFFFFF", stroke_width=3).set_opacity(0.9).move_to([0, -1.0, 0])
        ring2 = Circle(radius=1.6, color="#FFFFFF", stroke_width=2.5).set_opacity(0.6).move_to([0, -1.0, 0])
        ring3 = Circle(radius=2.4, color="#FFFFFF", stroke_width=2).set_opacity(0.3).move_to([0, -1.0, 0])
        
        # Crosshairs / turbulence vectors shooting outward
        v1 = Arrow(start=[0, -1.0, 0], end=[2.2, 0.8, 0], color="#FFFFFF", stroke_width=3, buff=0)
        v2 = Arrow(start=[0, -1.0, 0], end=[-2.2, 0.8, 0], color="#FFFFFF", stroke_width=3, buff=0)
        v3 = Arrow(start=[0, -1.0, 0], end=[1.8, -2.6, 0], color="#FFFFFF", stroke_width=3, buff=0)
        v4 = Arrow(start=[0, -1.0, 0], end=[-1.8, -2.6, 0], color="#FFFFFF", stroke_width=3, buff=0)
        
        center_core = Circle(radius=0.3, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1).move_to([0, -1.0, 0])
        
        vortex_group = VGroup(ring1, ring2, ring3, v1, v2, v3, v4, center_core)
        
        self.play(FadeIn(center_core), GrowFromCenter(ring1), run_time=1.0)
        self.play(GrowFromCenter(ring2), GrowFromCenter(ring3), run_time=1.2)
        self.play(
            GrowArrow(v1), GrowArrow(v2), GrowArrow(v3), GrowArrow(v4),
            run_time=1.0
        )
        
        # Rapid pulse rotation simulation
        self.play(vortex_group.animate.rotate(PI / 4), run_time=0.5)
        self.play(vortex_group.animate.rotate(-PI / 2), run_time=0.5)
        
        self.wait(3.2)

# Configure canvas for a pure monochrome aesthetic, strict dimensions, and safe zones.

def create_base_layout(scene, category_text):
    """Creates the standard bottom title, footer line, and metadata labels."""
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

def create_scene_title(scene, title_text):
    """Places the title strictly at the bottom (y = -2.95) to leave upper canvas clear for captions."""
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    return title

class Scene22_15(Scene):
    def construct(self):
        create_base_layout(self, "SYSTEMIC TURBULENCE")
        title = create_scene_title(self, "IT PAINTS A PICTURE OF INTENSE SYSTEMIC TURBULENCE")
        
        # Literal figurative visual: A large server/system box being struck by jagged turbulence/lightning/waves.
        # Safe area: x in [-3.2, 3.2], y in [-2.5, 0.4]
        
        # Central system box (Server/Processor)
        system_box = RoundedRectangle(corner_radius=0.15, width=3.0, height=2.2, color="#FFFFFF", stroke_width=2.0)
        system_box.move_to([0, -1.05, 0])
        system_box.set_fill("#FFFFFF", opacity=0.08)
        
        # Internal server racks (lines inside box)
        rack_1 = Line(LEFT * 1.2, RIGHT * 1.2, color="#FFFFFF", stroke_width=1.5).move_to([0, -0.3, 0])
        rack_2 = Line(LEFT * 1.2, RIGHT * 1.2, color="#FFFFFF", stroke_width=1.5).move_to([0, -1.05, 0])
        rack_3 = Line(LEFT * 1.2, RIGHT * 1.2, color="#FFFFFF", stroke_width=1.5).move_to([0, -1.8, 0])
        
        # Indicator dots on racks
        dots = VGroup(*[
            Circle(radius=0.06, color="#FFFFFF", fill_opacity=0.8).move_to([1.0, y_pos, 0])
            for y_pos in [-0.3, -1.05, -1.8]
        ])
        
        server_group = VGroup(system_box, rack_1, rack_2, rack_3, dots)
        
        # Jagged turbulence strokes crashing across the system (Intense Systemic Turbulence)
        turb_1 = Line([-2.5, 0.3, 0], [-1.0, -0.5, 0], color="#FFFFFF", stroke_width=3.5)
        turb_2 = Line([-1.0, -0.5, 0], [-0.5, 0.1, 0], color="#FFFFFF", stroke_width=3.5)
        turb_3 = Line([-0.5, 0.1, 0], [0.8, -0.8, 0], color="#FFFFFF", stroke_width=3.5)
        turb_4 = Line([0.8, -0.8, 0], [1.5, -0.2, 0], color="#FFFFFF", stroke_width=3.5)
        turb_5 = Line([1.5, -0.2, 0], [2.6, 0.4, 0], color="#FFFFFF", stroke_width=3.5)
        
        turbulence_lightning = VGroup(turb_1, turb_2, turb_3, turb_4, turb_5).move_to([0, -0.3, 0])
        
        # Shockwaves radiating outward
        wave_left = Arc(radius=1.8, start_angle=PI/2, angle=PI, color="#FFFFFF", stroke_width=1.5).move_to([-1.5, -1.05, 0])
        wave_right = Arc(radius=1.8, start_angle=-PI/2, angle=PI, color="#FFFFFF", stroke_width=1.5).move_to([1.5, -1.05, 0])
        wave_left.set_opacity(0.4)
        wave_right.set_opacity(0.4)
        
        waves = VGroup(wave_left, wave_right)
        
        # Entrance animations
        self.play(
            FadeIn(server_group, shift=DOWN * 0.2),
            run_time=1.5
        )
        
        self.play(
            Create(turbulence_lightning),
            FadeIn(waves),
            run_time=1.8
        )
        
        # Pulsing turbulence effect to show intensity
        self.play(
            turbulence_lightning.animate.set_opacity(0.4),
            waves.animate.scale(1.15).set_opacity(0.8),
            run_time=1.0
        )
        self.play(
            turbulence_lightning.animate.set_opacity(1.0),
            waves.animate.scale(1.0).set_opacity(0.3),
            run_time=1.0
        )
        
        # Hold state for remaining duration
        self.wait(1.5)

class Scene22_16(Scene):
    def construct(self):
        create_base_layout(self, "SYSTEMIC TURBULENCE")
        title = create_scene_title(self, "IT PAINTS A PICTURE OF INTENSE SYSTEMIC TURBULENCE")
        
        # Literal figurative visual: A complex multi-node network grid breaking / fracturing under extreme pressure waves.
        # Safe area: x in [-3.2, 3.2], y in [-2.5, 0.4]
        
        # Create a grid of interconnected nodes representing a "system"
        node_coords = [
            [-1.8, 0.0, 0], [-0.6, 0.2, 0], [0.6, -0.1, 0], [1.8, 0.1, 0],
            [-1.8, -1.5, 0], [-0.6, -1.3, 0], [0.6, -1.6, 0], [1.8, -1.4, 0]
        ]
        
        nodes = VGroup(*[
            Circle(radius=0.18, color="#FFFFFF", fill_opacity=0.3).move_to(coord)
            for coord in node_coords
        ])
        
        # Connections between nodes forming the "picture" / system map
        connections = VGroup(
            Line(node_coords[0], node_coords[1], color="#FFFFFF", stroke_width=1.5),
            Line(node_coords[1], node_coords[2], color="#FFFFFF", stroke_width=1.5),
            Line(node_coords[2], node_coords[3], color="#FFFFFF", stroke_width=1.5),
            Line(node_coords[4], node_coords[5], color="#FFFFFF", stroke_width=1.5),
            Line(node_coords[5], node_coords[6], color="#FFFFFF", stroke_width=1.5),
            Line(node_coords[6], node_coords[7], color="#FFFFFF", stroke_width=1.5),
            Line(node_coords[0], node_coords[4], color="#FFFFFF", stroke_width=1.5),
            Line(node_coords[1], node_coords[5], color="#FFFFFF", stroke_width=1.5),
            Line(node_coords[2], node_coords[6], color="#FFFFFF", stroke_width=1.5),
            Line(node_coords[3], node_coords[7], color="#FFFFFF", stroke_width=1.5),
            # Diagonal cross-links
            Line(node_coords[1], node_coords[4], color="#FFFFFF", stroke_width=1.0).set_opacity(0.4),
            Line(node_coords[2], node_coords[7], color="#FFFFFF", stroke_width=1.0).set_opacity(0.4),
        )
        
        system_network = VGroup(connections, nodes).move_to([0, -0.75, 0])
        
        # Intense turbulence slash lines crossing the system matrix diagonally
        slash_1 = Line([-2.8, 0.8, 0], [2.8, -2.3, 0], color="#FFFFFF", stroke_width=4.0)
        slash_2 = Line([-2.5, -2.1, 0], [2.5, 0.6, 0], color="#FFFFFF", stroke_width=4.0)
        slash_1.set_opacity(0.8)
        slash_2.set_opacity(0.8)
        
        slashes = VGroup(slash_1, slash_2)
        
        # Disruption shock rings expanding outward
        ring_1 = Circle(radius=1.2, color="#FFFFFF", stroke_width=2.0).move_to([0, -0.75, 0])
        ring_2 = Circle(radius=2.2, color="#FFFFFF", stroke_width=1.0).move_to([0, -0.75, 0])
        ring_1.set_opacity(0.6)
        ring_2.set_opacity(0.3)
        
        rings = VGroup(ring_1, ring_2)
        
        # Build sequence
        self.play(
            Create(system_network),
            run_time=1.5
        )
        
        self.play(
            FadeIn(rings, scale=0.8),
            run_time=1.2
        )
        
        self.play(
            Create(slashes),
            system_network.animate.shift(DOWN * 0.1).set_opacity(0.7),
            run_time=1.0
        )
        
        # Jitter/turbulence motion
        self.play(
            slashes.animate.shift(UP * 0.2),
            rings.animate.scale(1.2).set_opacity(0.1),
            run_time=1.2
        )
        
        self.play(
            slashes.animate.shift(DOWN * 0.1),
            run_time=1.0
        )
        
        # Hold state for remaining duration
        self.wait(1.5)