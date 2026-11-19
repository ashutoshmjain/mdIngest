from manim_compat import *
from manim import *
import numpy as np
from numpy import cos, sin, pi

# COMPATIBILITY SHIMS
ease_in_out_sine = smooth
ease_in_sine = smooth
ease_out_sine = smooth
def ShowCreationThenFadeOut(mob):
    return Succession(Create(mob), FadeOut(mob))

config.pixel_width = 740
config.pixel_height = 740
config.frame_width = 8.0
config.frame_height = 8.0
config.background_color = "#000000"

# (Using universal get_footer_and_title from manim_compat)



# Configure canvas exactly as required

def setup_scene(scene, category_text):
    # Bottom Title Placement (y = -2.95)
    title = Text("THE AI OBSERVES THE TOKEN CONGESTION", font="Arial", weight=BOLD, font_size=18, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.4)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene10_01(Scene):
    def construct(self):
        setup_scene(self, "INTERNAL AI OBSERVATION")
        
        # Literal figurative visual: AI Eye observing a narrow channel/pipe with tokens stuck
        eye_outer = Circle(radius=1.2, color="#FFFFFF", stroke_width=3).move_to([0, -0.5, 0])
        eye_inner = Circle(radius=0.4, color="#FFFFFF", stroke_width=2).move_to([0, -0.5, 0])
        eye_pupil = Dot([0, -0.5, 0], color="#FFFFFF", radius=0.15)
        
        # Scanlines
        scan_line = Line(LEFT * 1.5, RIGHT * 1.5, color="#FFFFFF", stroke_width=1).set_opacity(0.4).move_to([0, 0.2, 0])
        
        # Pipe representing token pathway
        pipe_top = Line([-3.2, 1.2, 0], [3.2, 1.2, 0], color="#FFFFFF", stroke_width=2)
        pipe_bottom = Line([-3.2, -2.0, 0], [3.2, -2.0, 0], color="#FFFFFF", stroke_width=2)
        
        tokens = VGroup(*[
            Square(side_length=0.3, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.3).move_to([x, -0.4, 0])
            for x in [-1.5, -0.8, -0.3, 0.1, 0.4]
        ])
        
        group = VGroup(eye_outer, eye_inner, eye_pupil, scan_line, pipe_top, pipe_bottom, tokens)
        
        self.play(FadeIn(group, shift=UP*0.2), run_time=1.0)
        self.play(
            scan_line.animate.shift(DOWN * 1.0),
            tokens.animate.shift(RIGHT * 0.2),
            run_time=2.5, rate_func=there_and_back
        )
        self.wait(3.4)

class Scene10_02(Scene):
    def construct(self):
        setup_scene(self, "TOKEN CONGESTION METER")
        
        # Literal figurative visual: Power meter / gauge packed to the maximum with tokens
        gauge_bg = Arc(radius=1.8, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=3).move_to([0, -1.0, 0])
        needle = Line([0, -1.0, 0], [1.2, 0.2, 0], color="#FFFFFF", stroke_width=3)
        pivot = Dot([0, -1.0, 0], color="#FFFFFF", radius=0.15)
        
        # Jammed warning zone indicator
        max_zone = Arc(radius=1.8, start_angle=0.1*PI, angle=0.4*PI, color="#FFFFFF", stroke_width=8).set_opacity(0.8).move_to([0, -1.0, 0])
        
        # Overloaded token blocks spilling out
        spill_tokens = VGroup(*[
            RoundedRectangle(corner_radius=0.05, width=0.4, height=0.4, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.5).move_to([x, y, 0])
            for x, y in [(-1.2, 0.8), (-0.5, 1.1), (0.2, 1.0), (0.9, 0.7), (0.0, 1.5)]
        ])
        
        group = VGroup(gauge_bg, max_zone, needle, pivot, spill_tokens)
        
        self.play(FadeIn(group), run_time=1.0)
        self.play(Rotate(needle, angle=0.5, about_point=[0, -1.0, 0]), run_time=1.5, rate_func=there_and_back)
        self.play(spill_tokens.animate.scale(1.1), run_time=1.5, rate_func=there_and_back)
        self.wait(3.3)

class Scene10_03(Scene):
    def construct(self):
        setup_scene(self, "BOTTLENECK PIPELINE")
        
        # Literal figurative visual: Wide intake funnel narrowing down sharply into a congested bottleneck
        funnel_top = Line([-2.5, 1.2, 0], [2.5, 1.2, 0], color="#FFFFFF", stroke_width=2)
        funnel_left = Line([-2.5, 1.2, 0], [-0.5, -0.5, 0], color="#FFFFFF", stroke_width=2)
        funnel_right = Line([2.5, 1.2, 0], [0.5, -0.5, 0], color="#FFFFFF", stroke_width=2)
        
        narrow_ch_left = Line([-0.5, -0.5, 0], [-0.5, -2.2, 0], color="#FFFFFF", stroke_width=2)
        narrow_ch_right = Line([0.5, -0.5, 0], [0.5, -2.2, 0], color="#FFFFFF", stroke_width=2)
        
        # Stacked squares representing tokens clogging the bottleneck
        tokens = VGroup(*[
            Square(side_length=0.35, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.4).move_to([0, y, 0])
            for y in [-0.3, 0.1, 0.5, 0.9, -0.8, -1.2, -1.6]
        ])
        
        group = VGroup(funnel_top, funnel_left, funnel_right, narrow_ch_left, narrow_ch_right, tokens)
        
        self.play(Create(group), run_time=1.5)
        self.play(tokens.animate.shift(UP * 0.2), run_time=2.0, rate_func=there_and_back)
        self.wait(3.8)

class Scene10_04(Scene):
    def construct(self):
        setup_scene(self, "INTERNAL SENSOR SCAN")
        
        # Literal figurative visual: Grid of server nodes/memory blocks with an active scanning laser grid
        grid = VGroup(*[
            Rectangle(width=0.8, height=0.8, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.15).move_to([x, y, 0])
            for x in [-2.0, -1.0, 0.0, 1.0, 2.0]
            for y in [-1.5, -0.5, 0.5, 1.2]
        ])
        
        laser = Line([-3.0, 1.5, 0], [3.0, 1.5, 0], color="#FFFFFF", stroke_width=3).set_opacity(0.9)
        
        group = VGroup(grid, laser)
        
        self.play(FadeIn(grid), run_time=1.0)
        self.play(laser.animate.shift(DOWN * 3.2), run_time=3.0, rate_func=there_and_back)
        self.wait(3.3)

class Scene10_05(Scene):
    def construct(self):
        setup_scene(self, "QUEUE OVERFLOW")
        
        # Literal figurative visual: Stack of token blocks reaching past a critical overflow line with warning arrows
        base_line = Line([-2.0, -2.0, 0], [2.0, -2.0, 0], color="#FFFFFF", stroke_width=3)
        limit_line = Line([-2.5, 1.0, 0], [2.5, 1.0, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.5)
        
        limit_label = Text("LIMIT", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").move_to([0, 1.2, 0])
        
        stack = VGroup(*[
            Rectangle(width=2.5, height=0.3, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.4).move_to([0, y, 0])
            for y in [-1.8, -1.4, -1.0, -0.6, -0.2, 0.2, 0.6, 1.0, 1.4, 1.8]
        ])
        
        overflow_arrow = Arrow([0, 1.5, 0], [0, 2.3, 0], color="#FFFFFF", stroke_width=3, buff=0)
        
        group = VGroup(base_line, limit_line, limit_label, stack, overflow_arrow)
        
        self.play(FadeIn(base_line), Create(stack), run_time=1.5)
        self.play(FadeIn(limit_line), FadeIn(limit_label), GrowArrow(overflow_arrow), run_time=1.5)
        self.play(stack.animate.shift(UP * 0.2), run_time=2.0, rate_func=there_and_back)
        self.wait(2.3)

class Scene10_06(Scene):
    def construct(self):
        setup_scene(self, "DIAGNOSTIC RADAR")
        
        # Literal figurative visual: Circular radar sweep detecting token cluster anomalies
        outer_ring = Circle(radius=1.8, color="#FFFFFF", stroke_width=2).move_to([0, -0.5, 0])
        inner_ring = Circle(radius=0.9, color="#FFFFFF", stroke_width=1).set_opacity(0.5).move_to([0, -0.5, 0])
        cross_h = Line([-1.8, -0.5, 0], [1.8, -0.5, 0], color="#FFFFFF", stroke_width=1).set_opacity(0.3)
        cross_v = Line([0, -2.3, 0], [0, 1.3, 0], color="#FFFFFF", stroke_width=1).set_opacity(0.3)
        
        sweep_line = Line([0, -0.5, 0], [1.2, 0.7, 0], color="#FFFFFF", stroke_width=2)
        
        cluster_dots = VGroup(*[
            Dot([x, y, 0], color="#FFFFFF", radius=0.08)
            for x, y in [(0.4, 0.2), (0.5, 0.0), (0.3, -0.2), (-0.4, 0.6), (-0.6, 0.4)]
        ])
        
        group = VGroup(outer_ring, inner_ring, cross_h, cross_v, sweep_line, cluster_dots)
        
        self.play(FadeIn(group), run_time=1.0)
        self.play(Rotate(sweep_line, angle=2*PI, about_point=[0, -0.5, 0]), run_time=4.0, rate_func=linear)
        self.wait(2.3)

class Scene10_07(Scene):
    def construct(self):
        setup_scene(self, "SYSTEM SELF-MONITORING")
        
        # Literal figurative visual: AI Central processing core displaying real-time congestion status
        core_box = RoundedRectangle(corner_radius=0.3, width=3.0, height=2.0, color="#FFFFFF", stroke_width=3).move_to([0, -0.5, 0])
        core_inner = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.4, color="#FFFFFF", stroke_width=1).set_opacity(0.3).move_to([0, -0.5, 0])
        
        pulse_ring = RoundedRectangle(corner_radius=0.4, width=3.4, height=2.4, color="#FFFFFF", stroke_width=2).set_opacity(0.6).move_to([0, -0.5, 0])
        
        status_bars = VGroup(*[
            Line([-0.8, y, 0], [0.8, y, 0], color="#FFFFFF", stroke_width=4)
            for y in [-0.2, -0.5, -0.8]
        ])
        
        group = VGroup(core_box, core_inner, pulse_ring, status_bars)
        
        self.play(FadeIn(group), run_time=1.0)
        self.play(pulse_ring.animate.scale(1.15).set_opacity(0.1), run_time=1.5, rate_func=there_and_back)
        self.play(status_bars.animate.stretch_to_fit_width(1.6), run_time=1.5, rate_func=there_and_back)
        self.wait(3.3)


def add_footer_and_title(scene, title_text):
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.4)
    
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("AI TOKEN CONGESTION", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)


class Scene10_08(Scene):
    def construct(self):
        add_footer_and_title(self, "THE AI OBSERVES TOKEN CONGESTION")
        
        # Literal figurative visual: AI Eye observing a clogged data pipe (token congestion)
        eye_outline = Circle(radius=1.2, color="#FFFFFF", stroke_width=2.5).move_to([0, -0.8, 0])
        pupil = Circle(radius=0.4, color="#FFFFFF", fill_opacity=0.8, stroke_width=2).move_to([0, -0.8, 0])
        
        # Congested tokens inside a horizontal pipe intersecting the eye
        pipe = RoundedRectangle(corner_radius=0.1, width=6.0, height=1.0, color="#FFFFFF", stroke_width=2).move_to([0, -0.8, 0])
        
        tokens = VGroup(*[
            Square(side_length=0.4, color="#FFFFFF", fill_opacity=0.3, stroke_width=1.5).move_to([x, -0.8, 0])
            for x in [-2.0, -1.2, -0.4, 0.4, 1.2, 2.0]
        ])
        
        scan_lines = VGroup(*[
            Line(UP * 1.5, DOWN * 3.0, color="#FFFFFF", stroke_width=1).set_opacity(0.2).shift(RIGHT * x)
            for x in [-2.5, -1.2, 0, 1.2, 2.5]
        ])
        
        self.play(FadeIn(pipe), FadeIn(tokens), run_time=1.0)
        self.play(Create(eye_outline), GrowFromCenter(pupil), FadeIn(scan_lines), run_time=2.0)
        
        # Pulsing congestion
        self.play(tokens.animate.scale(1.1), run_time=1.5)
        self.play(tokens.animate.scale(0.9), run_time=1.5)
        self.wait(1.3)


class Scene10_09(Scene):
    def construct(self):
        add_footer_and_title(self, "INTERNAL BOTTLENECK ANALYSIS")
        
        # Literal figurative visual: Funnel/Bottleneck with jammed blocks
        funnel_top = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=2).move_to([0, 0.5, 0])
        left_slope = Line([-2.5, 0.5, 0], [-0.5, -1.5, 0], color="#FFFFFF", stroke_width=2)
        right_slope = Line([2.5, 0.5, 0], [0.5, -1.5, 0], color="#FFFFFF", stroke_width=2)
        pipe_bottom = VGroup(
            Line([-0.5, -1.5, 0], [-0.5, -2.2, 0], color="#FFFFFF", stroke_width=2),
            Line([0.5, -1.5, 0], [0.5, -2.2, 0], color="#FFFFFF", stroke_width=2)
        )
        
        funnel = VGroup(funnel_top, left_slope, right_slope, pipe_bottom).move_to([0, -0.5, 0])
        
        jammed_tokens = VGroup(*[
            Square(side_length=0.6, color="#FFFFFF", fill_opacity=0.5, stroke_width=2).move_to([x, y, 0])
            for x, y in [(-1.0, 0.0), (1.0, 0.0), (0.0, -0.3), (-0.5, -0.8), (0.5, -0.8), (0.0, -1.3)]
        ])
        
        warning_arrow = Arrow(UP * 1.5, UP * 0.8, color="#FFFFFF", stroke_width=3, tip_length=0.2).move_to([0, 1.2, 0])
        
        self.play(Create(funnel), run_time=1.5)
        self.play(FadeIn(jammed_tokens, shift=DOWN*0.5), run_time=2.0)
        self.play(GrowArrow(warning_arrow), run_time=1.0)
        self.play(Wiggle(jammed_tokens, scale_value=1.05, run_time=2.0))
        self.wait(0.8)


class Scene10_10(Scene):
    def construct(self):
        add_footer_and_title(self, "MEASURING QUEUE DEPTH")
        
        # Literal figurative visual: Vertical Bar Meter measuring token overflow
        meter_outline = RoundedRectangle(corner_radius=0.2, width=1.5, height=4.0, color="#FFFFFF", stroke_width=2).move_to([0, -0.6, 0])
        
        # Fill bars representing queue levels
        bars = VGroup(*[
            Rectangle(width=1.3, height=0.35, color="#FFFFFF", fill_opacity=0.7, stroke_width=1).move_to([0, y, 0])
            for y in [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0]
        ])
        
        limit_line = Line(LEFT * 1.2, RIGHT * 1.2, color="#FFFFFF", stroke_width=3).move_to([0, 0.8, 0])
        overflow_text = Text("OVERFLOW", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, 1.5, 0])
        
        self.play(Create(meter_outline), run_time=1.0)
        self.play(FadeIn(bars, lag_ratio=0.1), run_time=2.5)
        self.play(Create(limit_line), FadeIn(overflow_text), run_time=1.5)
        self.play(bars.animate.set_fill(opacity=0.9), run_time=1.5)
        self.wait(0.8)


class Scene10_11(Scene):
    def construct(self):
        add_footer_and_title(self, "ROUTING TRAFFIC STREAMS")
        
        # Literal figurative visual: Diverter node splitting token streams into multiple pathways
        center_node = Circle(radius=0.8, color="#FFFFFF", fill_opacity=0.2, stroke_width=2.5).move_to([0, -0.6, 0])
        node_core = Dot(point=[0, -0.6, 0], color="#FFFFFF", radius=0.15)
        
        inbound_arrow = Arrow(LEFT * 3.5, LEFT * 1.0, color="#FFFFFF", stroke_width=2, tip_length=0.2).move_to([-2.25, -0.6, 0])
        out_up = Arrow(UP * 0.2, UP * 2.0, color="#FFFFFF", stroke_width=2, tip_length=0.2).move_to([1.0, 0.7, 0])
        out_down = Arrow(DOWN * 0.2, DOWN * 2.0, color="#FFFFFF", stroke_width=2, tip_length=0.2).move_to([1.0, -1.9, 0])
        
        path_box_up = RoundedRectangle(corner_radius=0.1, width=1.5, height=0.6, color="#FFFFFF", fill_opacity=0.3, stroke_width=1.5).move_to([2.2, 1.2, 0])
        path_box_down = RoundedRectangle(corner_radius=0.1, width=1.5, height=0.6, color="#FFFFFF", fill_opacity=0.3, stroke_width=1.5).move_to([2.2, -2.4, 0])
        
        self.play(GrowArrow(inbound_arrow), Create(center_node), FadeIn(node_core), run_time=1.5)
        self.play(GrowArrow(out_up), GrowArrow(out_down), run_time=1.5)
        self.play(FadeIn(path_box_up), FadeIn(path_box_down), run_time=1.5)
        self.play(Indicate(center_node, scale_factor=1.1, color="#FFFFFF"), run_time=1.8)
        self.wait(1.0)


class Scene10_12(Scene):
    def construct(self):
        add_footer_and_title(self, "MEMORY BUFFER THRESHOLDS")
        
        # Literal figurative visual: Server racks with flashing overload lights (buffers)
        racks = VGroup(*[
            RoundedRectangle(corner_radius=0.15, width=5.0, height=0.9, color="#FFFFFF", stroke_width=2, fill_opacity=0.1)
            .move_to([0, y, 0])
            for y in [0.8, -0.3, -1.4]
        ])
        
        lights = VGroup()
        for rack in racks:
            for x in [-2.0, -1.4, -0.8]:
                light = Circle(radius=0.1, color="#FFFFFF", fill_opacity=0.8, stroke_width=1).move_to(rack.get_center() + np.array([x, 0, 0]))
                lights.add(light)
                
        gauge_line = Line(LEFT * 1.5, RIGHT * 2.2, color="#FFFFFF", stroke_width=2).move_to([0.5, 1.8, 0])
        cursor_triangle = Polygon([0, 2.1, 0], [-0.2, 1.8, 0], [0.2, 1.8, 0], color="#FFFFFF", fill_opacity=1.0).move_to([1.5, 1.95, 0])
        
        self.play(FadeIn(racks, lag_ratio=0.2), FadeIn(lights, lag_ratio=0.1), run_time=2.0)
        self.play(Create(gauge_line), FadeIn(cursor_triangle), run_time=1.5)
        self.play(cursor_triangle.animate.shift(RIGHT * 0.8), run_time=2.0)
        self.play(cursor_triangle.animate.shift(LEFT * 1.2), run_time=1.0)
        self.wait(0.8)


class Scene10_13(Scene):
    def construct(self):
        add_footer_and_title(self, "PROCESSOR STALL DETECTION")
        
        # Literal figurative visual: CPU gear jammed by excessive tokens (cogwheels locked)
        outer_gear = Circle(radius=1.5, color="#FFFFFF", stroke_width=2.5, fill_opacity=0.1).move_to([0, -0.6, 0])
        inner_core = Circle(radius=0.6, color="#FFFFFF", stroke_width=2).move_to([0, -0.6, 0])
        
        spokes = VGroup(*[
            Line([0, -0.6, 0], [0, -0.6, 0] + np.array(np.array([np.cos(a), np.sin(a), 0])), color="#FFFFFF", stroke_width=2)
            for a in np.linspace(0, 2*np.pi, 6, endpoint=False)
        ])
        
        jamming_token = Square(side_length=0.8, color="#FFFFFF", fill_opacity=0.7, stroke_width=2).move_to([1.2, 0.1, 0])
        halt_sign = Text("HALT", font="Arial", weight=BOLD, font_size=18, color="#FFFFFF").move_to([0, 1.6, 0])
        
        gear_group = VGroup(outer_gear, inner_core, spokes)
        
        self.play(Create(gear_group), run_time=1.5)
        self.play(FadeIn(jamming_token, shift=LEFT*0.5), run_time=1.5)
        self.play(gear_group.animate.rotate(0.2), run_time=0.5)
        self.play(gear_group.animate.rotate(-0.1), run_time=0.5)
        self.play(FadeIn(halt_sign, scale=1.5), run_time=1.5)
        self.wait(1.3)


class Scene10_14(Scene):
    def construct(self):
        add_footer_and_title(self, "SYSTEM EQUILIBRIUM RESTORED")
        
        # Literal figurative visual: Balance scales perfectly leveling out after congestion clears
        fulcrum = Polygon([0, -1.8, 0], [-0.5, -2.6, 0], [0.5, -2.6, 0], color="#FFFFFF", fill_opacity=0.5, stroke_width=2)
        beam = Line(LEFT * 2.8, RIGHT * 2.8, color="#FFFFFF", stroke_width=3).move_to([0, -0.8, 0])
        
        left_pan_strings = VGroup(
            Line([-2.8, -0.8, 0], [-3.3, -1.8, 0], color="#FFFFFF", stroke_width=1.5),
            Line([-2.8, -0.8, 0], [-2.3, -1.8, 0], color="#FFFFFF", stroke_width=1.5)
        )
        left_pan = Arc(radius=1.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2).move_to([-2.8, -1.8, 0])
        
        right_pan_strings = VGroup(
            Line([2.8, -0.8, 0], [2.3, -1.8, 0], color="#FFFFFF", stroke_width=1.5),
            Line([2.8, -0.8, 0], [3.3, -1.8, 0], color="#FFFFFF", stroke_width=1.5)
        )
        right_pan = Arc(radius=1.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2).move_to([2.8, -1.8, 0])
        
        scale = VGroup(fulcrum, beam, left_pan_strings, left_pan, right_pan_strings, right_pan)
        
        tokens_left = VGroup(*[Square(side_length=0.3, color="#FFFFFF", fill_opacity=0.6, stroke_width=1).move_to([-2.8, -1.5 + i*0.35, 0]) for i in range(2)])
        tokens_right = VGroup(*[Square(side_length=0.3, color="#FFFFFF", fill_opacity=0.6, stroke_width=1).move_to([2.8, -1.5 + i*0.35, 0]) for i in range(2)])
        
        check_mark = Text("OPTIMIZED", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([0, 1.2, 0])
        
        self.play(Create(fulcrum), Create(beam), run_time=1.0)
        self.play(FadeIn(left_pan_strings), Create(left_pan), FadeIn(right_pan_strings), Create(right_pan), run_time=1.5)
        self.play(FadeIn(tokens_left), FadeIn(tokens_right), run_time=1.0)
        self.play(scale.animate.rotate(0.0), run_time=1.0) # stays balanced
        self.play(FadeIn(check_mark, scale=1.2), run_time=1.0)
        self.wait(0.8)

# Configure canvas

def setup_scene(scene, category_text):
    # Title at bottom
    title = Text("THE AI OBSERVES THE TOKEN CONGESTION", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.4)
    
    # Footer and meta labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene10_15(Scene):
    def construct(self):
        setup_scene(self, "INTERNAL OBSERVATION")
        
        # Literal illustration: An AI eye observing token blocks jammed in a funnel
        eye_outline = Circle(radius=1.2, color="#FFFFFF", stroke_width=2).move_to([0, -0.5, 0])
        pupil = Circle(radius=0.4, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to([0, -0.5, 0])
        
        # Funnel / bottleneck for token congestion
        funnel_left = Line([-2.0, 1.2, 0], [-0.5, -0.2, 0], color="#FFFFFF", stroke_width=2)
        funnel_right = Line([2.0, 1.2, 0], [0.5, -0.2, 0], color="#FFFFFF", stroke_width=2)
        
        # Congested tokens (squares jammed at top of funnel)
        tokens = VGroup(*[
            Square(side_length=0.3, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.5).move_to([x, y, 0])
            for x, y in [(-0.8, 1.0), (-0.3, 1.2), (0.2, 1.0), (0.7, 1.3), (-0.5, 1.5), (0.4, 1.6)]
        ])
        
        scan_beam = VGroup(
            Line([0, -0.5, 0], [-2.5, 1.8, 0], color="#FFFFFF", stroke_width=1).set_opacity(0.4),
            Line([0, -0.5, 0], [2.5, 1.8, 0], color="#FFFFFF", stroke_width=1).set_opacity(0.4)
        )
        
        self.play(
            Create(eye_outline),
            FadeIn(pupil, scale=0.5),
            Create(funnel_left),
            Create(funnel_right),
            run_time=1.5
        )
        self.play(FadeIn(tokens, shift=DOWN*0.2), run_time=1.5)
        self.play(FadeIn(scan_beam), run_time=1.0)
        
        # Pulsing observation
        self.play(pupil.animate.scale(1.2), run_time=1.0)
        self.play(pupil.animate.scale(1/1.2), run_time=1.0)
        self.wait(1.3)

class Scene10_16(Scene):
    def construct(self):
        setup_scene(self, "TOKEN BOTTLENECK")
        
        # Literal illustration: Server pipeline with traffic jam of glowing token rectangles
        pipeline_top = Line([-3.0, 0.8, 0], [3.0, 0.8, 0], color="#FFFFFF", stroke_width=2)
        pipeline_bottom = Line([-3.0, -1.2, 0], [3.0, -1.2, 0], color="#FFFFFF", stroke_width=2)
        
        # Chokepoint in the middle
        choke_top = Line([-0.5, 0.8, 0], [-0.2, -0.2, 0], color="#FFFFFF", stroke_width=2)
        choke_bottom = Line([-0.5, -1.2, 0], [-0.2, -0.2, 0], color="#FFFFFF", stroke_width=2)
        
        # A massive pileup of token rectangles
        pileup = VGroup(*[
            RoundedRectangle(corner_radius=0.05, width=0.5, height=0.3, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.7)
            .move_to([-1.8 + i*0.25, -0.2 + (j*0.35), 0])
            for i in range(5) for j in range(4)
        ])
        
        warning_icon = VGroup(
            Polygon([-0.3, 1.8, 0], [0.3, 1.8, 0], [0, 1.2, 0], color="#FFFFFF", stroke_width=2, fill_opacity=0.2),
            Text("!", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([0, 1.5, 0])
        )
        
        self.play(
            Create(pipeline_top),
            Create(pipeline_bottom),
            FadeIn(pileup),
            run_time=2.0
        )
        self.play(FadeIn(warning_icon, shift=DOWN*0.2), run_time=1.0)
        
        # Shaking the pileup to show congestion stress
        self.play(pileup.animate.shift(RIGHT * 0.1), run_time=0.3)
        self.play(pileup.animate.shift(LEFT * 0.2), run_time=0.3)
        self.play(pileup.animate.shift(RIGHT * 0.1), run_time=0.3)
        self.wait(3.4)

class Scene10_17(Scene):
    def construct(self):
        setup_scene(self, "INTERNAL DIAGNOSTIC")
        
        # Literal illustration: Internal AI processor grid scanning tokens
        grid = VGroup(*[
            Rectangle(width=0.8, height=0.8, color="#FFFFFF", stroke_width=1, fill_opacity=0.1)
            .move_to([-2.2 + x*1.1, 0.8 - y*1.1, 0])
            for x in range(5) for y in range(2)
        ])
        
        # Highlight overloaded central nodes
        overload_box1 = Rectangle(width=0.8, height=0.8, color="#FFFFFF", stroke_width=2.5, fill_opacity=0.6).move_to([-0.0, 0.8, 0])
        overload_box2 = Rectangle(width=0.8, height=0.8, color="#FFFFFF", stroke_width=2.5, fill_opacity=0.6).move_to([1.1, 0.8, 0])
        
        # Data streams backing up
        arrows = VGroup(*[
            Arrow(start=[-3.0, -1.0 + i*0.6, 0], end=[-2.5, -1.0 + i*0.6, 0], color="#FFFFFF", stroke_width=2, tip_length=0.15)
            for i in range(3)
        ])
        
        diagnostic_line = DashedLine(start=[0, 2.0, 0], end=[0, -2.0, 0], color="#FFFFFF", stroke_width=2, dash_length=0.1)
        
        self.play(Create(grid), run_time=1.5)
        self.play(
            Transform(grid[5], overload_box1),
            Transform(grid[6], overload_box2),
            run_time=1.5
        )
        self.play(Create(diagnostic_line), run_time=1.0)
        self.play(FadeIn(arrows), run_time=1.0)
        self.wait(1.3)

class Scene10_18(Scene):
    def construct(self):
        setup_scene(self, "QUEUE MONITORING")
        
        # Literal illustration: Bar gauges showing skyrocketing token counts in queue
        bar_bg_1 = RoundedRectangle(corner_radius=0.1, width=1.0, height=3.0, color="#FFFFFF", stroke_width=1.5).move_to([-1.5, -0.3, 0])
        bar_fill_1 = RoundedRectangle(corner_radius=0.1, width=0.8, height=2.4, color="#FFFFFF", stroke_width=1, fill_opacity=0.8).move_to([-1.5, -0.6, 0])
        
        bar_bg_2 = RoundedRectangle(corner_radius=0.1, width=1.0, height=3.0, color="#FFFFFF", stroke_width=1.5).move_to([0.0, -0.3, 0])
        bar_fill_2 = RoundedRectangle(corner_radius=0.1, width=0.8, height=2.8, color="#FFFFFF", stroke_width=1, fill_opacity=0.9).move_to([0.0, -0.4, 0])
        
        bar_bg_3 = RoundedRectangle(corner_radius=0.1, width=1.0, height=3.0, color="#FFFFFF", stroke_width=1.5).move_to([1.5, -0.3, 0])
        bar_fill_3 = RoundedRectangle(corner_radius=0.1, width=0.8, height=1.2, color="#FFFFFF", stroke_width=1, fill_opacity=0.4).move_to([1.5, -1.2, 0])
        
        labels = VGroup(
            Text("Q1", font="Arial", font_size=12, color="#FFFFFF").move_to([-1.5, 1.4, 0]),
            Text("Q2", font="Arial", font_size=12, color="#FFFFFF").move_to([0.0, 1.4, 0]),
            Text("Q3", font="Arial", font_size=12, color="#FFFFFF").move_to([1.5, 1.4, 0]),
        )
        
        threshold_line = Line([-2.5, 1.0, 0], [2.5, 1.0, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.8)
        
        self.play(
            Create(bar_bg_1), Create(bar_bg_2), Create(bar_bg_3),
            FadeIn(labels),
            run_time=1.5
        )
        self.play(
            FadeIn(bar_fill_1, shift=UP),
            FadeIn(bar_fill_2, shift=UP),
            FadeIn(bar_fill_3, shift=UP),
            run_time=2.0
        )
        self.play(Create(threshold_line), run_time=1.0)
        
        # Pulse threshold
        self.play(threshold_line.animate.set_opacity(0.3), run_time=0.5)
        self.play(threshold_line.animate.set_opacity(1.0), run_time=0.5)
        self.wait(1.8)

class Scene10_19(Scene):
    def construct(self):
        setup_scene(self, "SYSTEM OVERVIEW")
        
        # Literal illustration: Central AI core monitoring incoming/outgoing token congestion flows
        core = Circle(radius=1.0, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to([0, -0.5, 0])
        core_inner = Circle(radius=0.5, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.5).move_to([0, -0.5, 0])
        
        # Incoming congested paths (dotted lines with tokens)
        path_left = Arrow([-3.5, 0.5, 0], [-1.2, -0.2, 0], color="#FFFFFF", stroke_width=2, tip_length=0.2)
        path_right = Arrow([3.5, 0.5, 0], [1.2, -0.2, 0], color="#FFFFFF", stroke_width=2, tip_length=0.2)
        
        tokens_in = VGroup(
            Square(side_length=0.25, color="#FFFFFF", fill_opacity=0.8).move_to([-2.2, 0.2, 0]),
            Square(side_length=0.25, color="#FFFFFF", fill_opacity=0.8).move_to([-1.8, 0.05, 0]),
            Square(side_length=0.25, color="#FFFFFF", fill_opacity=0.8).move_to([2.2, 0.2, 0]),
            Square(side_length=0.25, color="#FFFFFF", fill_opacity=0.8).move_to([1.8, 0.05, 0])
        )
        
        radar_arc1 = Arc(radius=1.5, start_angle=-0.5, angle=1.0, color="#FFFFFF", stroke_width=1.5).move_to([0, -0.5, 0])
        radar_arc2 = Arc(radius=2.0, start_angle=-0.5, angle=1.0, color="#FFFFFF", stroke_width=1.0).move_to([0, -0.5, 0])
        
        self.play(
            Create(core),
            FadeIn(core_inner),
            Create(path_left),
            Create(path_right),
            run_time=2.0
        )
        self.play(FadeIn(tokens_in), run_time=1.0)
        self.play(Create(radar_arc1), Create(radar_arc2), run_time=1.5)
        
        # Final systemic pulse
        self.play(
            core.animate.scale(1.15),
            core_inner.animate.scale(0.85),
            run_time=1.0
        )
        self.play(
            core.animate.scale(1/1.15),
            core_inner.animate.scale(1/0.85),
            run_time=0.8
        )
        self.wait(1.0)