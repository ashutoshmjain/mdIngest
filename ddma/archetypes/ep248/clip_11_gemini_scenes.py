import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Global Canvas and Style Configuration

def add_standard_footer_and_title(scene, title_text):
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("MECHANICS OF WATERFALL", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene11_01(Scene):
    def construct(self):
        add_standard_footer_and_title(self, "WATERFALL STRUCTURE OVERVIEW")
        
        # Literal figurative waterfall structure: cascading stepped rectangles
        steps = VGroup()
        for i in range(4):
            rect = RoundedRectangle(corner_radius=0.1, width=2.0 - i*0.2, height=0.6, stroke_width=2, color="#FFFFFF")
            rect.set_fill("#FFFFFF", opacity=0.15 + i*0.1)
            rect.shift(RIGHT * (i * 1.0 - 1.5) + UP * (1.2 - i * 0.9))
            steps.add(rect)
            
        # Water flow arrows connecting the steps
        arrows = VGroup()
        for i in range(3):
            arr = Arrow(steps[i].get_bottom(), steps[i+1].get_top(), buff=0.1, stroke_width=2, color="#FFFFFF")
            arrows.add(arr)
            
        structure = VGroup(steps, arrows).move_to([0, -0.8, 0])
        
        self.play(FadeIn(structure, shift=DOWN), run_time=2.0)
        self.play(structure.animate.scale(1.05), run_time=2.5, rate_func=there_and_back)
        self.wait(2.4)

class Scene11_02(Scene):
    def construct(self):
        add_standard_footer_and_title(self, "PHASED CASCADING TIERS")
        
        # 3 Vertical tiers representing strict sequential waterfall phases
        tiers = VGroup()
        labels = ["PHASE 1", "PHASE 2", "PHASE 3"]
        for i in range(3):
            box = RoundedRectangle(corner_radius=0.15, width=4.5, height=1.0, stroke_width=2, color="#FFFFFF")
            box.set_fill("#FFFFFF", opacity=0.2)
            lbl = Text(labels[i], font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(box.get_center())
            tier = VGroup(box, lbl)
            tier.shift(UP * (1.2 - i * 1.3))
            tiers.add(tier)
            
        down_arrows = VGroup(
            Arrow(tiers[0].get_bottom(), tiers[1].get_top(), buff=0.08, stroke_width=2, color="#FFFFFF"),
            Arrow(tiers[1].get_bottom(), tiers[2].get_top(), buff=0.08, stroke_width=2, color="#FFFFFF")
        )
        
        full_obj = VGroup(tiers, down_arrows).move_to([0, -0.6, 0])
        
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN) for t in tiers], lag_ratio=0.3), run_time=2.5)
        self.play(FadeIn(down_arrows), run_time=1.0)
        self.play(full_obj.animate.shift(UP * 0.2), run_time=2.0, rate_func=there_and_back)
        self.wait(1.0)

class Scene11_03(Scene):
    def construct(self):
        add_standard_footer_and_title(self, "SEQUENTIAL FLOW MECHANICS")
        
        # Pipeline/Chute structure with flow particles
        chute = Rectangle(width=6.0, height=1.2, stroke_width=2, color="#FFFFFF")
        chute.set_fill("#FFFFFF", opacity=0.1)
        chute.move_to([0, -0.6, 0])
        
        dividers = VGroup()
        for x in [-1.5, 0.0, 1.5]:
            d = Line(UP * 0.6, DOWN * 0.6, stroke_width=2, color="#FFFFFF").shift(x * RIGHT)
            dividers.add(d)
        dividers.move_to(chute.get_center())
        
        flow_dots = VGroup(*[Circle(radius=0.15, color="#FFFFFF", fill_opacity=0.8).move_to(chute.get_left() + RIGHT * (0.8 + i*1.5)) for i in range(4)])
        
        mechanics_group = VGroup(chute, dividers, flow_dots)
        
        self.play(Create(chute), Create(dividers), run_time=2.0)
        self.play(FadeIn(flow_dots), run_time=1.0)
        self.play(flow_dots.animate.shift(RIGHT * 0.5), run_time=2.5, rate_func=there_and_back)
        self.wait(1.0)

class Scene11_04(Scene):
    def construct(self):
        add_standard_footer_and_title(self, "RIGID STRUCTURAL BOUNDARIES")
        
        # Box container with locked structural grid
        outer_box = RoundedRectangle(corner_radius=0.2, width=5.5, height=3.0, stroke_width=2.5, color="#FFFFFF")
        outer_box.set_fill("#FFFFFF", opacity=0.08)
        outer_box.move_to([0, -0.6, 0])
        
        grid_lines = VGroup(
            Line(outer_box.get_top(), outer_box.get_bottom(), stroke_width=1.5, color="#FFFFFF").set_opacity(0.5),
            Line(outer_box.get_left(), outer_box.get_right(), stroke_width=1.5, color="#FFFFFF").set_opacity(0.5)
        )
        grid_lines.move_to(outer_box.get_center())
        
        lock_icon = Rectangle(width=0.8, height=0.6, stroke_width=2, color="#FFFFFF").set_fill("#FFFFFF", opacity=0.3).move_to(outer_box.get_center())
        
        struct_group = VGroup(outer_box, grid_lines, lock_icon)
        
        self.play(DrawBorderThenFill(outer_box), run_time=2.0)
        self.play(Create(grid_lines), FadeIn(lock_icon), run_time=1.5)
        self.play(struct_group.animate.scale(1.05), run_time=2.0, rate_func=there_and_back)
        self.wait(1.0)

class Scene11_05(Scene):
    def construct(self):
        add_standard_footer_and_title(self, "GRAVITY-DRIVEN PROGRESSION")
        
        # Vertical drop pipe with directional arrows pointing downward
        pipe = Rectangle(width=1.5, height=4.5, stroke_width=2, color="#FFFFFF")
        pipe.set_fill("#FFFFFF", opacity=0.12)
        pipe.move_to([0, -0.6, 0])
        
        arrows = VGroup(*[
            Arrow(UP * 1.5, UP * 0.8, stroke_width=2, color="#FFFFFF").shift(DOWN * i * 1.2)
            for i in range(3)
        ]).move_to(pipe.get_center())
        
        gravity_group = VGroup(pipe, arrows)
        
        self.play(Create(pipe), run_time=2.0)
        self.play(FadeIn(arrows, shift=DOWN), run_time=2.0)
        self.play(arrows.animate.shift(DOWN * 0.3), run_time=1.5, rate_func=there_and_back)
        self.wait(1.0)

class Scene11_06(Scene):
    def construct(self):
        add_standard_footer_and_title(self, "DOWNWARD UNIDIRECTIONAL FLOW")
        
        # One-way valve / funnel shape
        funnel = Polygon(
            [-2.5, 0.8, 0], [2.5, 0.8, 0],
            [0.8, -1.8, 0], [-0.8, -1.8, 0],
            stroke_width=2, color="#FFFFFF"
        )
        funnel.set_fill("#FFFFFF", opacity=0.15)
        funnel.move_to([0, -0.5, 0])
        
        exit_arrow = Arrow(DOWN * 1.2, DOWN * 2.2, stroke_width=2, color="#FFFFFF").move_to([0, -2.1, 0])
        
        flow_group = VGroup(funnel, exit_arrow)
        
        self.play(DrawBorderThenFill(funnel), run_time=2.5)
        self.play(GrowArrow(exit_arrow), run_time=1.5)
        self.play(flow_group.animate.shift(DOWN * 0.2), run_time=2.0, rate_func=there_and_back)
        self.wait(1.0)

class Scene11_07(Scene):
    def construct(self):
        add_standard_footer_and_title(self, "COMPLETE WATERFALL MECHANICS")
        
        # Full integrated waterfall architecture summary (3 cascading blocks linked)
        block1 = RoundedRectangle(corner_radius=0.1, width=2.2, height=0.8, stroke_width=2, color="#FFFFFF").set_fill("#FFFFFF", opacity=0.2).move_to([-2.0, 0.8, 0])
        block2 = RoundedRectangle(corner_radius=0.1, width=2.2, height=0.8, stroke_width=2, color="#FFFFFF").set_fill("#FFFFFF", opacity=0.2).move_to([0.0, -0.2, 0])
        block3 = RoundedRectangle(corner_radius=0.1, width=2.2, height=0.8, stroke_width=2, color="#FFFFFF").set_fill("#FFFFFF", opacity=0.2).move_to([2.0, -1.2, 0])
        
        conn1 = Arrow(block1.get_bottom(), block2.get_top(), buff=0.1, stroke_width=2, color="#FFFFFF")
        conn2 = Arrow(block2.get_bottom(), block3.get_top(), buff=0.1, stroke_width=2, color="#FFFFFF")
        
        complete_system = VGroup(block1, block2, block3, conn1, conn2).move_to([0, -0.5, 0])
        
        self.play(FadeIn(block1, shift=RIGHT), FadeIn(block2, shift=RIGHT), FadeIn(block3, shift=RIGHT), run_time=2.5)
        self.play(Create(conn1), Create(conn2), run_time=1.5)
        self.play(complete_system.animate.scale(1.05), run_time=2.0, rate_func=there_and_back)
        self.wait(1.0)

# Configure canvas and dimensions strictly

def setup_scene_base(*args, **kwargs):
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

    """Adds the mandatory bottom title, footer, and branding for strict compliance."""
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.4)
    
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)


class Scene11_08(Scene):
    def construct(self):
        setup_scene_base(self, "WATERFALL STRUCTURE: SOURCE & PEAK", "MECHANICS")
        
        # Literal figurative visual: Mountain peak with a reservoir/source at the top
        peak_polygon = Polygon([-2, 1.5, 0], [0, 2.5, 0], [2, 1.5, 0], color="#FFFFFF", stroke_width=2.5)
        peak_polygon.set_fill("#FFFFFF", opacity=0.15)
        
        reservoir = RoundedRectangle(corner_radius=0.2, width=1.5, height=0.6, color="#FFFFFF", stroke_width=2)
        reservoir.set_fill("#FFFFFF", opacity=0.3)
        reservoir.move_to([0, 2.3, 0])
        
        water_line = Line(LEFT * 0.5, RIGHT * 0.5, color="#FFFFFF", stroke_width=2).move_to([0, 2.3, 0])
        
        # Droplets ready to fall
        drop1 = Circle(radius=0.1, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.8).move_to([0, 1.7, 0])
        drop2 = Circle(radius=0.08, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.6).move_to([-0.5, 1.4, 0])
        drop3 = Circle(radius=0.08, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.6).move_to([0.5, 1.4, 0])

        group = VGroup(peak_polygon, reservoir, water_line, drop1, drop2, drop3)
        
        self.play(FadeIn(group, shift=DOWN*0.3), run_time=1.5)
        self.play(Indicate(reservoir, scale_factor=1.1), run_time=2.0)
        self.wait(4.0)


class Scene11_09(Scene):
    def construct(self):
        setup_scene_base(self, "WATERFALL STRUCTURE: THE DROP", "MECHANICS")
        
        # Literal figurative visual: Vertical parallel streaming lines (the water fall)
        stream_lines = VGroup()
        for i in range(7):
            x_pos = -1.8 + i * 0.6
            line = Line([x_pos, 2.0, 0], [x_pos, -1.5, 0], color="#FFFFFF", stroke_width=3.5)
            line.set_opacity(0.7 + (i % 3) * 0.1)
            stream_lines.add(line)
            
        # Directional downward flow arrows
        arrows = VGroup(
            Arrow(start=[0, 1.0, 0], end=[0, -0.5, 0], color="#FFFFFF", stroke_width=3, buff=0),
            Arrow(start=[-1.2, 0.5, 0], end=[-1.2, -1.0, 0], color="#FFFFFF", stroke_width=3, buff=0),
            Arrow(start=[1.2, 0.5, 0], end=[1.2, -1.0, 0], color="#FFFFFF", stroke_width=3, buff=0)
        )
        
        self.play(FadeIn(stream_lines), run_time=1.0)
        self.play(GrowArrow(arrows[0]), GrowArrow(arrows[1]), GrowArrow(arrows[2]), run_time=2.5)
        self.play(stream_lines.animate.shift(DOWN * 0.2), run_time=4.0)


class Scene11_10(Scene):
    def construct(self):
        setup_scene_base(self, "WATERFALL STRUCTURE: TIER ONE", "MECHANICS")
        
        # Literal figurative visual: First ledge catching water (horizontal barrier)
        ledge = Rectangle(width=6.0, height=0.4, color="#FFFFFF", stroke_width=2.5)
        ledge.set_fill("#FFFFFF", opacity=0.3)
        ledge.move_to([0, 0.5, 0])
        
        # Pool accumulating on the ledge
        pool = RoundedRectangle(corner_radius=0.1, width=5.6, height=0.80, color="#FFFFFF", stroke_width=2)
        pool.set_fill("#FFFFFF", opacity=0.4)
        pool.move_to([0, 1.0, 0])
        
        # Overflow stream dropping down further
        overflow = VGroup(
            Line([-1.5, 0.6, 0], [-1.5, -1.5, 0], color="#FFFFFF", stroke_width=2.5),
            Line([1.5, 0.6, 0], [1.5, -1.5, 0], color="#FFFFFF", stroke_width=2.5)
        )
        
        group = VGroup(ledge, pool, overflow)
        self.play(DrawBorderThenFill(ledge), run_time=1.5)
        self.play(FadeIn(pool, shift=UP*0.2), run_time=2.0)
        self.play(FadeIn(overflow), run_time=4.0)


class Scene11_11(Scene):
    def construct(self):
        setup_scene_base(self, "WATERFALL STRUCTURE: TIER TWO", "MECHANICS")
        
        # Literal figurative visual: Multi-tiered staircase of water basins
        tier1 = Rectangle(width=5.0, height=0.3, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.3).move_to([0, 1.5, 0])
        tier2 = Rectangle(width=6.0, height=0.3, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.3).move_to([0, 0.0, 0])
        tier3 = Rectangle(width=7.0, height=0.3, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.3).move_to([0, -1.5, 0])
        
        conn_left = VGroup(
            Line([-2.0, 1.35, 0], [-2.5, 0.15, 0], color="#FFFFFF", stroke_width=2),
            Line([-2.5, -0.15, 0], [-3.0, -1.35, 0], color="#FFFFFF", stroke_width=2)
        )
        conn_right = VGroup(
            Line([2.0, 1.35, 0], [2.5, 0.15, 0], color="#FFFFFF", stroke_width=2),
            Line([2.5, -0.15, 0], [3.0, -1.35, 0], color="#FFFFFF", stroke_width=2)
        )
        
        tiers = VGroup(tier1, tier2, tier3, conn_left, conn_right)
        
        self.play(FadeIn(tier1, shift=DOWN*0.2), run_time=1.5)
        self.play(FadeIn(tier2, shift=DOWN*0.2), run_time=1.5)
        self.play(FadeIn(tier3, shift=DOWN*0.2), run_time=1.5)
        self.play(FadeIn(conn_left, conn_right), run_time=3.0)


class Scene11_12(Scene):
    def construct(self):
        setup_scene_base(self, "WATERFALL STRUCTURE: BASIN COLLECTION", "MECHANICS")
        
        # Literal figurative visual: Large deep basin catching all streams at the bottom
        basin_outer = Arc(radius=2.5, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=3)
        basin_outer.move_to([0, -0.5, 0])
        
        basin_fill = Arc(radius=2.4, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=1.5)
        basin_fill.set_fill("#FFFFFF", opacity=0.25)
        basin_fill.move_to([0, -0.5, 0])
        
        # Incoming flow lines into the basin
        inflows = VGroup(
            Line([-1.0, 2.0, 0], [-1.0, 0.0, 0], color="#FFFFFF", stroke_width=2.5),
            Line([0, 2.0, 0], [0, -0.2, 0], color="#FFFFFF", stroke_width=3),
            Line([1.0, 2.0, 0], [1.0, 0.0, 0], color="#FFFFFF", stroke_width=2.5)
        )
        
        ripple = Circle(radius=1.2, color="#FFFFFF", stroke_width=1.5).move_to([0, -0.8, 0])
        ripple.set_opacity(0.6)
        
        group = VGroup(basin_outer, basin_fill, inflows, ripple)
        
        self.play(Create(basin_outer), FadeIn(basin_fill), run_time=2.0)
        self.play(FadeIn(inflows), run_time=2.0)
        self.play(Transform(ripple, Circle(radius=2.0, color="#FFFFFF", stroke_width=1).move_to([0, -0.8, 0]).set_opacity(0.1)), run_time=3.5)


class Scene11_13(Scene):
    def construct(self):
        setup_scene_base(self, "WATERFALL STRUCTURE: FLUID DYNAMICS", "MECHANICS")
        
        # Literal figurative visual: Interlocking mechanical gears powered by water flow path
        gear_center = [0, 0, 0]
        circle_gear = Circle(radius=1.2, color="#FFFFFF", stroke_width=2.5).move_to(gear_center)
        circle_gear.set_fill("#FFFFFF", opacity=0.1)
        
        inner_core = Circle(radius=0.4, color="#FFFFFF", stroke_width=2).move_to(gear_center)
        
        # Gear teeth representation (simple radial lines)
        teeth = VGroup()
        for i in range(8):
            angle = i * (TAU / 8)
            p1 = np.array([0, 0, 0]) + 1.1 * np.array([np.cos(angle), np.sin(angle), 0])
            p2 = np.array([0, 0, 0]) + 1.4 * np.array([np.cos(angle), np.sin(angle), 0])
            teeth.add(Line(p1, p2, color="#FFFFFF", stroke_width=3))
            
        gear = VGroup(circle_gear, inner_core, teeth)
        
        # Surrounding flow curve
        flow_arc = Arc(radius=2.0, start_angle=PI/2, angle=3*PI/2, color="#FFFFFF", stroke_width=2)
        flow_arrow = Arrow(start=[-2, 2, 0], end=[-2, 0, 0], color="#FFFFFF", stroke_width=2, buff=0)
        
        self.play(Create(gear), run_time=2.5)
        self.play(Rotate(gear, angle=PI/4, about_point=gear_center), run_time=1.5)
        self.play(FadeIn(flow_arc), GrowArrow(flow_arrow), run_time=3.5)


class Scene11_14(Scene):
    def construct(self):
        setup_scene_base(self, "WATERFALL STRUCTURE: COMPLETE SYSTEM", "MECHANICS")
        
        # Literal figurative visual: Comprehensive structural overview diagram (Top source -> Tiers -> Bottom Basin)
        box_top = RoundedRectangle(corner_radius=0.15, width=3.0, height=0.6, color="#FFFFFF", stroke_width=2).move_to([0, 1.8, 0])
        box_top.set_fill("#FFFFFF", opacity=0.2)
        text_top = Text("SOURCE", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(box_top.get_center())
        
        arrow1 = Arrow(start=[0, 1.4, 0], end=[0, 0.6, 0], color="#FFFFFF", stroke_width=2, buff=0.1)
        
        box_mid = RoundedRectangle(corner_radius=0.15, width=4.5, height=0.6, color="#FFFFFF", stroke_width=2).move_to([0, 0.1, 0])
        box_mid.set_fill("#FFFFFF", opacity=0.2)
        text_mid = Text("CASCADING TIERS", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(box_mid.get_center())
        
        arrow2 = Arrow(start=[0, -0.3, 0], end=[0, -1.1, 0], color="#FFFFFF", stroke_width=2, buff=0.1)
        
        box_bot = RoundedRectangle(corner_radius=0.15, width=6.0, height=0.6, color="#FFFFFF", stroke_width=2).move_to([0, -1.6, 0])
        box_bot.set_fill("#FFFFFF", opacity=0.2)
        text_bot = Text("FINAL COLLECTION BASIN", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(box_bot.get_center())
        
        system_group = VGroup(box_top, text_top, arrow1, box_mid, text_mid, arrow2, box_bot, text_bot)
        
        self.play(FadeIn(box_top, shift=DOWN*0.1), FadeIn(text_top), run_time=1.5)
        self.play(GrowArrow(arrow1), FadeIn(box_mid, shift=DOWN*0.1), FadeIn(text_mid), run_time=2.5)
        self.play(GrowArrow(arrow2), FadeIn(box_bot, shift=DOWN*0.1), FadeIn(text_bot), run_time=3.5)

# Configuration conforming strictly to the rules

def setup_scene_base(*args, **kwargs):
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

    """Sets up the mandatory title, footer line, and footer labels."""
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text("MECHANICS & STRUCTURES", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

class Scene11_15(Scene):
    def construct(self):
        setup_scene_base(self)
        
        # Literal Waterfall: Tiered horizontal ledges cascading water downward
        waterfall_group = VGroup()
        
        ledges = VGroup(
            Line(LEFT * 2.0, RIGHT * 1.0, color="#FFFFFF", stroke_width=4).move_to([0, 0.5, 0]),
            Line(LEFT * 1.0, RIGHT * 2.0, color="#FFFFFF", stroke_width=4).move_to([0, -0.5, 0]),
            Line(LEFT * 2.0, RIGHT * 1.5, color="#FFFFFF", stroke_width=4).move_to([0, -1.5, 0])
        )
        
        streams = VGroup(
            Arrow(start=[1.0, 0.5, 0], end=[1.0, -0.5, 0], color="#FFFFFF", stroke_width=3, buff=0),
            Arrow(start=[-1.0, -0.5, 0], end=[-1.0, -1.5, 0], color="#FFFFFF", stroke_width=3, buff=0)
        )
        
        waterfall_group.add(ledges, streams)
        
        self.play(FadeIn(waterfall_group, shift=DOWN), run_time=2.0)
        self.play(Wiggle(waterfall_group, scale_value=1.05, rotation_angle=0.01), run_time=4.5)
        self.wait(1.0)

class Scene11_16(Scene):
    def construct(self):
        setup_scene_base(self)
        
        # Literal Waterfall structure expanding with mechanical gears
        structure = VGroup(
            Rectangle(width=5.0, height=3.0, color="#FFFFFF", stroke_width=2).move_to([0, -0.8, 0]),
            Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=1.5).move_to([0, 0.2, 0]),
            Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=1.5).move_to([0, -0.8, 0])
        )
        
        gear1 = Circle(radius=0.5, color="#FFFFFF", stroke_width=2).move_to([-1.5, 0.7, 0])
        gear2 = Circle(radius=0.7, color="#FFFFFF", stroke_width=2).move_to([1.2, -0.2, 0])
        
        mech_group = VGroup(structure, gear1, gear2)
        
        self.play(Create(mech_group), run_time=2.5)
        self.play(Rotate(gear1, angle=2*PI, about_point=[-1.5, 0.7, 0]),
                  Rotate(gear2, angle=-2*PI, about_point=[1.2, -0.2, 0]), run_time=4.0)
        self.wait(1.0)

class Scene11_17(Scene):
    def construct(self):
        setup_scene_base(self)
        
        # Literal cascading flow blocks (Steps/Phases of a waterfall model)
        blocks = VGroup()
        for i in range(4):
            block = RoundedRectangle(corner_radius=0.1, width=3.0, height=0.6, color="#FFFFFF", stroke_width=2)
            block.move_to([i * 0.5 - 1.0, 1.0 - i * 0.9, 0])
            blocks.add(block)
            
        flow_arrows = VGroup()
        for i in range(3):
            arr = Arrow(start=blocks[i].get_bottom(), end=blocks[i+1].get_top(), color="#FFFFFF", stroke_width=2, buff=0.05)
            flow_arrows.add(arr)
            
        cascade_system = VGroup(blocks, flow_arrows)
        
        self.play(FadeIn(cascade_system, lag_ratio=0.3), run_time=3.5)
        self.play(Indicate(blocks, color="#FFFFFF", scale_factor=1.05), run_time=3.0)
        self.wait(1.0)

class Scene11_18(Scene):
    def construct(self):
        setup_scene_base(self)
        
        # Literal mechanical drop: weights falling sequentially down strict tiers
        tiers = VGroup(
            Line(LEFT * 3.0, RIGHT * 3.0, color="#FFFFFF", stroke_width=1.5).move_to([0, 1.0, 0]),
            Line(LEFT * 3.0, RIGHT * 3.0, color="#FFFFFF", stroke_width=1.5).move_to([0, -0.5, 0]),
            Line(LEFT * 3.0, RIGHT * 3.0, color="#FFFFFF", stroke_width=1.5).move_to([0, -2.0, 0])
        )
        
        weight = Square(side_length=0.6, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to([-2.0, 1.5, 0])
        
        self.play(Create(tiers), run_time=1.5)
        self.play(FadeIn(weight), run_time=0.5)
        
        self.play(weight.animate.move_to([-2.0, 0.3, 0]), run_time=1.5)
        self.play(weight.animate.move_to([-2.0, -1.2, 0]), run_time=1.5)
        self.play(weight.animate.move_to([2.0, -1.2, 0]), run_time=1.5)
        self.wait(1.0)

class Scene11_19(Scene):
    def construct(self):
        setup_scene_base(self)
        
        # Precision blueprint mechanics of a waterfall drop structure
        axis_v = Line(DOWN * 2.2, UP * 1.5, color="#FFFFFF", stroke_width=2).move_to([-2.0, -0.3, 0])
        axis_h = Line(LEFT * 0.5, RIGHT * 3.0, color="#FFFFFF", stroke_width=2).move_to([0.5, 1.0, 0])
        
        steps = VGroup(
            Rectangle(width=1.2, height=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to([-1.0, 1.0, 0]),
            Rectangle(width=1.2, height=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to([0.0, 0.2, 0]),
            Rectangle(width=1.2, height=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to([1.0, -0.6, 0]),
            Rectangle(width=1.2, height=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to([2.0, -1.4, 0])
        )
        
        blueprint = VGroup(axis_v, axis_h, steps)
        
        self.play(Create(axis_v), Create(axis_h), run_time=2.0)
        self.play(FadeIn(steps, shift=RIGHT, lag_ratio=0.2), run_time=4.0)
        self.wait(1.5)

class Scene11_20(Scene):
    def construct(self):
        setup_scene_base(self)
        
        # Fluid Dynamics: Continuous stream lines curving down a massive vertical cliff
        cliff = Line(UP * 2.2, DOWN * 2.2, color="#FFFFFF", stroke_width=4).move_to([-2.0, -0.2, 0])
        
        streams = VGroup()
        for i in range(5):
            y_offset = 1.5 - i * 0.7
            stream = Arc(radius=1.0, start_angle=PI/2, angle=-PI/2, color="#FFFFFF", stroke_width=2)
            stream.move_to([-1.0, y_offset, 0])
            streams.add(stream)
            
        basin = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=3).move_to([0, -2.2, 0])
        
        waterfall_dynamics = VGroup(cliff, streams, basin)
        
        self.play(Create(cliff), Create(basin), run_time=2.0)
        self.play(FadeIn(streams, shift=DOWN, lag_ratio=0.15), run_time=3.5)
        self.wait(2.0)

class Scene11_21(Scene):
    def construct(self):
        setup_scene_base(self)
        
        # Grand Finale of the Waterfall Structure: Fully locked mechanical cascading framework
        framework = VGroup()
        
        outer_box = RoundedRectangle(corner_radius=0.2, width=6.0, height=4.2, color="#FFFFFF", stroke_width=2).move_to([0, -0.6, 0])
        
        internal_ledges = VGroup(
            Line(LEFT * 2.5, RIGHT * 0.0, color="#FFFFFF", stroke_width=2).move_to([-0.5, 1.0, 0]),
            Line(LEFT * 0.0, RIGHT * 2.5, color="#FFFFFF", stroke_width=2).move_to([0.5, 0.0, 0]),
            Line(LEFT * 2.5, RIGHT * 0.0, color="#FFFFFF", stroke_width=2).move_to([-0.5, -1.0, 0])
        )
        
        core_symbol = Circle(radius=0.6, color="#FFFFFF", stroke_width=2, fill_opacity=0.4).move_to([0, -0.5, 0])
        core_cross = VGroup(
            Line(UP * 0.4, DOWN * 0.4, color="#FFFFFF", stroke_width=2),
            Line(LEFT * 0.4, RIGHT * 0.4, color="#FFFFFF", stroke_width=2)
        ).move_to([0, -0.5, 0])
        
        framework.add(outer_box, internal_ledges, core_symbol, core_cross)
        
        self.play(Create(outer_box), run_time=2.0)
        self.play(FadeIn(internal_ledges, lag_ratio=0.3), run_time=2.5)
        self.play(GrowFromCenter(core_symbol), GrowFromCenter(core_cross), run_time=2.0)
        self.wait(1.0)