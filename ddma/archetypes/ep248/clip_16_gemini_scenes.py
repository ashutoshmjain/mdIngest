import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Canvas Configuration

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

    # Bottom Title Placement (y = -2.95)
    title = Text("WHY NOT ACCUMULATE STABLECOINS?", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    self.play(FadeIn(title), run_time=0.6)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_name, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    self.add(footer_line, left_text, right_text)

class Scene16_01(Scene):
    def construct(self):
        setup_scene_base(self, "CRYPTO ACCUMULATION")
        
        # Literal visual: Giant Vault / Safe with dollar signs (Stablecoin Vault)
        safe_box = RoundedRectangle(corner_radius=0.2, width=3.5, height=2.8, color="#FFFFFF", stroke_width=2.5)
        safe_box.move_to([0, -1.0, 0])
        safe_dial = Circle(radius=0.5, color="#FFFFFF", stroke_width=2).move_to([0, -1.0, 0])
        safe_handle = Line([0, -0.5, 0], [0, -1.0, 0], color="#FFFFFF", stroke_width=2)
        
        coin_1 = Circle(radius=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to([-1.8, 1.0, 0])
        coin_2 = Circle(radius=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to([0, 1.3, 0])
        coin_3 = Circle(radius=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.2).move_to([1.8, 1.0, 0])
        
        t1 = Text("USDT", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(coin_1.get_center())
        t2 = Text("USDC", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(coin_2.get_center())
        t3 = Text("DAI", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(coin_3.get_center())
        
        coins_group = VGroup(coin_1, coin_2, coin_3, t1, t2, t3)
        safe_group = VGroup(safe_box, safe_dial, safe_handle)
        
        self.play(DrawBorderThenFill(safe_group), run_time=3.0)
        self.play(FadeIn(coins_group, shift=DOWN), run_time=3.5)
        self.wait(1.1)

class Scene16_02(Scene):
    def construct(self):
        setup_scene_base(self, "STABLECOIN RESERVES")
        
        # Literal visual: Server stacks representing stablecoin issuers/reserves
        servers = VGroup()
        for i in range(3):
            box = RoundedRectangle(corner_radius=0.1, width=3.0, height=0.8, color="#FFFFFF", stroke_width=2, fill_opacity=0.15)
            box.move_to([0, 0.8 - i*1.0, 0])
            light1 = Circle(radius=0.06, color="#FFFFFF", fill_opacity=1.0).move_to([-1.1, 0.8 - i*1.0, 0])
            light2 = Circle(radius=0.06, color="#FFFFFF", fill_opacity=1.0).move_to([-0.9, 0.8 - i*1.0, 0])
            servers.add(VGroup(box, light1, light2))
            
        label = Text("RESERVE VAULT", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, -1.8, 0])
        
        self.play(LaggedStart(*[Create(s) for s in servers], lag_ratio=0.3), run_time=4.5)
        self.play(FadeIn(label), run_time=2.0)
        self.wait(1.1)

class Scene16_03(Scene):
    def construct(self):
        setup_scene_base(self, "VALUE COMPARISON")
        
        # Literal visual: Balance scale comparing stablecoins to fiat
        beam = Line([-2.0, 0.5, 0], [2.0, 0.5, 0], color="#FFFFFF", stroke_width=2)
        fulcrum = Polygon([-0.3, -1.5, 0], [0.3, -1.5, 0], [0, 0.5, 0], color="#FFFFFF", stroke_width=2, fill_opacity=0.2)
        
        pan_left = VGroup(
            Line([-2.0, 0.5, 0], [-2.5, -0.5, 0], color="#FFFFFF", stroke_width=1.5),
            Line([-2.0, 0.5, 0], [-1.5, -0.5, 0], color="#FFFFFF", stroke_width=1.5),
            Arc(radius=1.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=1.5).move_to([-2.0, -0.5, 0])
        ).shift(DOWN*0.5)
        
        pan_right = VGroup(
            Line([2.0, 0.5, 0], [1.5, -0.5, 0], color="#FFFFFF", stroke_width=1.5),
            Line([2.0, 0.5, 0], [2.5, -0.5, 0], color="#FFFFFF", stroke_width=1.5),
            Arc(radius=1.0, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=1.5).move_to([2.0, -0.5, 0])
        ).shift(DOWN*0.5)
        
        weight_l = Circle(radius=0.6, color="#FFFFFF", fill_opacity=0.3, stroke_width=2).move_to([-2.0, -0.7, 0])
        text_l = Text("$1", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to(weight_l.get_center())
        
        weight_r = Circle(radius=0.6, color="#FFFFFF", fill_opacity=0.3, stroke_width=2).move_to([2.0, -0.7, 0])
        text_r = Text("USDT", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(weight_r.get_center())
        
        scale = VGroup(beam, fulcrum, pan_left, pan_right, weight_l, text_l, weight_r, text_r).move_to([0, -0.5, 0])
        
        self.play(Create(fulcrum), Create(beam), run_time=2.5)
        self.play(Create(pan_left), Create(pan_right), run_time=2.5)
        self.play(FadeIn(weight_l), FadeIn(text_l), FadeIn(weight_r), FadeIn(text_r), run_time=1.5)
        self.wait(1.1)

class Scene16_04(Scene):
    def construct(self):
        setup_scene_base(self, "INFLATION DRAIN")
        
        # Literal visual: Coin with a downward leaking arrow (purchasing power loss)
        coin = Circle(radius=1.2, color="#FFFFFF", stroke_width=2.5, fill_opacity=0.1).move_to([0, 0.5, 0])
        dollar = Text("$", font="Arial", weight=BOLD, font_size=40, color="#FFFFFF").move_to(coin.get_center())
        
        leak_arrow = Arrow([0, -0.9, 0], [0, -2.2, 0], color="#FFFFFF", stroke_width=3, tip_length=0.25)
        leak_text = Text("INFLATION", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").next_to(leak_arrow, RIGHT, buff=0.2)
        
        self.play(Create(coin), FadeIn(dollar), run_time=3.0)
        self.play(GrowArrow(leak_arrow), FadeIn(leak_text), run_time=3.5)
        self.wait(1.1)

class Scene16_05(Scene):
    def construct(self):
        setup_scene_base(self, "COUNTERPARTY RISK")
        
        # Literal visual: A cracked shield representing counterparty risk
        shield = Polygon([0, 1.8, 0], [-1.8, 0.8, 0], [-1.8, -1.0, 0], [0, -2.0, 0], [1.8, -1.0, 0], [1.8, 0.8, 0], color="#FFFFFF", stroke_width=2.5, fill_opacity=0.1).move_to([0, -0.2, 0])
        
        crack = Line([0, 1.8, 0], [0.3, 0.5, 0], color="#FFFFFF", stroke_width=3)
        crack2 = Line([0.3, 0.5, 0], [-0.2, -0.5, 0], color="#FFFFFF", stroke_width=3)
        crack3 = Line([-0.2, -0.5, 0], [0.4, -1.5, 0], color="#FFFFFF", stroke_width=3)
        
        cracks = VGroup(crack, crack2, crack3)
        
        self.play(Create(shield), run_time=3.5)
        self.play(Create(cracks), run_time=3.0)
        self.wait(1.1)

class Scene16_06(Scene):
    def construct(self):
        setup_scene_base(self, "YIELD VS HOLDING")
        
        # Literal visual: Upward growth line blocked or flatlining
        axes_line = Line([-2.5, -1.5, 0], [2.5, -1.5, 0], color="#FFFFFF", stroke_width=2)
        axes_vert = Line([-2.5, -1.5, 0], [-2.5, 1.5, 0], color="#FFFFFF", stroke_width=2)
        
        flat_line = Line([-2.5, -0.5, 0], [2.5, -0.5, 0], color="#FFFFFF", stroke_width=3)
        flat_label = Text("FLAT YIELD", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").next_to(flat_line, UP, buff=0.2)
        
        self.play(Create(axes_line), Create(axes_vert), run_time=2.5)
        self.play(Create(flat_line), FadeIn(flat_label), run_time=4.0)
        self.wait(1.1)

class Scene16_07(Scene):
    def construct(self):
        setup_scene_base(self, "FINAL ALTERNATIVE")
        
        # Literal visual: Crossroads or question mark pointing to true accumulation
        q_mark = Text("?", font="Arial", weight=BOLD, font_size=70, color="#FFFFFF").move_to([0, 0.0, 0])
        
        arrow_left = Arrow([-1.0, -1.5, 0], [-2.5, -0.5, 0], color="#FFFFFF", stroke_width=2, tip_length=0.2)
        arrow_right = Arrow([1.0, -1.5, 0], [2.5, -0.5, 0], color="#FFFFFF", stroke_width=2, tip_length=0.2)
        
        t_left = Text("HOLD", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").next_to(arrow_left, UP, buff=0.1)
        t_right = Text("GROW", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").next_to(arrow_right, UP, buff=0.1)
        
        group = VGroup(q_mark, arrow_left, arrow_right, t_left, t_right)
        
        self.play(FadeIn(q_mark, scale=0.5), run_time=3.0)
        self.play(GrowArrow(arrow_left), GrowArrow(arrow_right), FadeIn(t_left), FadeIn(t_right), run_time=3.5)
        self.wait(1.1)


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

    title = Text("WHY NOT ACCUMULATE STABLECOINS?", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)
    scene.play(FadeIn(title), run_time=0.6)

class Scene16_08(Scene):
    def construct(self):
        setup_base_scene(self, "STABLECOIN STORAGE")
        
        # Draw a literal vault / checkbook / database server box for stablecoins (USDT/USDC)
        vault = RoundedRectangle(corner_radius=0.2, width=3.0, height=2.4, stroke_color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.15)
        vault.move_to([0, -0.5, 0])
        
        door_handle = Circle(radius=0.15, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.5).move_to(vault.get_center() + RIGHT * 0.9)
        hinges = VGroup(
            Rectangle(width=0.15, height=0.4, stroke_color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.5).move_to(vault.get_left() + RIGHT * 0.08 + UP * 0.6),
            Rectangle(width=0.15, height=0.4, stroke_color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.5).move_to(vault.get_left() + RIGHT * 0.08 + DOWN * 0.6)
        )
        
        usdt_text = Text("USDT", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to(vault.get_center() + UP * 0.4)
        usdc_text = Text("USDC", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to(vault.get_center() + DOWN * 0.4)
        
        vault_group = VGroup(vault, door_handle, hinges, usdt_text, usdc_text)
        
        self.play(DrawBorderThenFill(vault_group), run_time=2.0)
        
        # Add pulsing inquiry marks or question bounds
        q1 = Text("?", font="Arial", weight=BOLD, font_size=36, color="#FFFFFF").move_to([-2.2, 1.2, 0])
        q2 = Text("?", font="Arial", weight=BOLD, font_size=36, color="#FFFFFF").move_to([2.2, 1.2, 0])
        
        self.play(FadeIn(q1, shift=DOWN*0.2), FadeIn(q2, shift=DOWN*0.2), run_time=1.5)
        self.play(vault_group.animate.scale(1.05), run_time=1.5)
        self.play(vault_group.animate.scale(1/1.05), run_time=1.5)
        self.wait(0.5)

class Scene16_09(Scene):
    def construct(self):
        setup_base_scene(self, "INFLATION EROSION")
        
        # Draw a stack of dollar bills and a fire / erosion meter
        stack = VGroup()
        for i in range(5):
            rect = RoundedRectangle(corner_radius=0.1, width=3.0, height=0.4, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2)
            rect.shift(DOWN * (1.0 - i * 0.45))
            stack.add(rect)
            
        label = Text("STABLE VALUE", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to(stack.get_center())
        stack.add(label)
        
        self.play(Create(stack), run_time=2.0)
        
        # Show purchasing power slipping away via down arrows and erosion lines
        down_arrows = VGroup(
            Arrow(start=UP*1.5, end=UP*0.5, color="#FFFFFF", stroke_width=3).move_to([-2.2, 0, 0]),
            Arrow(start=UP*1.5, end=UP*0.5, color="#FFFFFF", stroke_width=3).move_to([2.2, 0, 0])
        )
        
        erode_text = Text("PURCHASING POWER", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, 1.8, 0])
        
        self.play(FadeIn(erode_text), GrowArrow(down_arrows[0]), GrowArrow(down_arrows[1]), run_time=2.0)
        
        # Shrink the stack slightly to show loss
        self.play(stack.animate.scale(0.85).set_opacity(0.6), run_time=2.6)
        self.wait(0.5)

class Scene16_10(Scene):
    def construct(self):
        setup_base_scene(self, "OPCOST ANALYSIS")
        
        # Balance scale comparing Stablecoin vs Productive Assets
        base_line = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=3).move_to([0, -0.5, 0])
        fulcrum = Polygon([-0.3, -2.0, 0], [0.3, -2.0, 0], [0, -0.5, 0], stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.3)
        
        beam = Line(LEFT * 2.8, RIGHT * 2.8, color="#FFFFFF", stroke_width=3).move_to([0, 0.5, 0])
        
        pan_left = VGroup(
            Line([-2.8, 0.5, 0], [-2.8, -0.5, 0], color="#FFFFFF", stroke_width=2),
            Circle(radius=0.8, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).move_to([-2.8, -0.6, 0])
        )
        pan_right = VGroup(
            Line([2.8, 0.5, 0], [2.8, 0.5, 0], color="#FFFFFF", stroke_width=2),
            Circle(radius=0.8, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).move_to([2.8, 0.5, 0])
        )
        # Adjust right pan down to tilt scale
        pan_right.move_to([2.8, -1.2, 0], coor_mask=[0,1,0])
        beam.rotate(-0.2, about_point=[0, 0.5, 0])
        
        t_left = Text("USDT/USDC", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([-2.8, -0.6, 0])
        t_right = Text("GROWTH", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([2.8, 0.5, 0])
        
        scale_group = VGroup(base_line, fulcrum, beam, pan_left, pan_right, t_left, t_right)
        
        self.play(Create(fulcrum), Create(base_line), Create(beam), run_time=2.0)
        self.play(FadeIn(pan_left), FadeIn(pan_right), FadeIn(t_left), FadeIn(t_right), run_time=2.0)
        self.play(scale_group.animate.rotate(0.1, about_point=[0,-0.5,0]), run_time=2.0)
        self.wait(0.6)

class Scene16_11(Scene):
    def construct(self):
        setup_base_scene(self, "YIELD COMPARISON")
        
        # Bar chart showing 0% vs Growth Assets
        bar_base = Line(LEFT * 3.0, RIGHT * 3.0, color="#FFFFFF", stroke_width=2).move_to([0, -1.5, 0])
        
        bar1 = Rectangle(width=0.8, height=0.5, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.2).align_to(bar_base, DOWN).shift(LEFT * 1.5)
        bar2 = Rectangle(width=0.8, height=2.8, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.6).align_to(bar_base, DOWN).shift(RIGHT * 1.5)
        
        label1 = Text("STABLE", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").next_to(bar1, DOWN, buff=0.1)
        label2 = Text("PRODUCTIVE", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").next_to(bar2, DOWN, buff=0.1)
        
        val1 = Text("0-5%", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").next_to(bar1, UP, buff=0.1)
        val2 = Text("15%+", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").next_to(bar2, UP, buff=0.1)
        
        chart = VGroup(bar_base, bar1, bar2, label1, label2, val1, val2)
        
        self.play(Create(bar_base), run_time=1.0)
        self.play(GrowFromBottom(bar1), GrowFromBottom(bar2), run_time=2.0)
        self.play(FadeIn(label1), FadeIn(label2), FadeIn(val1), FadeIn(val2), run_time=2.0)
        self.play(bar2.animate.stretch_to_fit_height(3.2), run_time=2.0)
        self.wait(0.6)

class Scene16_12(Scene):
    def construct(self):
        setup_base_scene(self, "COUNTERPARTY RISK")
        
        # Central node with warning chains / shields breaking
        shield = Polygon([0, 1.5, 0], [1.5, 0.5, 0], [1.0, -1.5, 0], [-1.0, -1.5, 0], [-1.5, 0.5, 0], stroke_color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.1)
        shield.move_to([0, -0.3, 0])
        
        exclamation = Text("!", font="Arial", weight=BOLD, font_size=48, color="#FFFFFF").move_to(shield.get_center())
        
        crack = Line([-0.3, 0.5, 0], [0.2, -0.2, 0], color="#FFFFFF", stroke_width=3)
        crack2 = Line([0.2, -0.2, 0], [-0.1, -1.0, 0], color="#FFFFFF", stroke_width=3)
        
        risk_text = Text("CENTRALIZED ISSUER RISK", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([0, 1.8, 0])
        
        self.play(Create(shield), FadeIn(risk_text), run_time=2.0)
        self.play(FadeIn(exclamation), run_time=1.0)
        self.play(Create(crack), Create(crack2), run_time=2.0)
        
        # Shake effect
        self.play(shield.animate.shift(LEFT * 0.1), run_time=0.2)
        self.play(shield.animate.shift(RIGHT * 0.2), run_time=0.2)
        self.play(shield.animate.shift(LEFT * 0.1), run_time=0.2)
        self.wait(0.8)

class Scene16_13(Scene):
    def construct(self):
        setup_base_scene(self, "OPPORTUNITY COST")
        
        # Two paths diverging: One flat line, one exponential curve upwards
        path_flat = Line(LEFT * 3.0, RIGHT * 3.0, color="#FFFFFF", stroke_width=2).move_to([0, -1.0, 0])
        
        # Exponential curve approximation using Arc or VGroup of lines
        curve_points = [np.array([-3.0 + i*0.5, -1.0 + 0.05*(i**1.8), 0]) for i in range(13)]
        curve = VGroup()
        for i in range(len(curve_points)-1):
            curve.add(Line(curve_points[i], curve_points[i+1], color="#FFFFFF", stroke_width=3))
            
        label_flat = Text("HOLDING STABLE", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([-1.5, -1.5, 0])
        label_growth = Text("PRODUCTIVE CAPITAL", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([1.5, 1.5, 0])
        
        self.play(Create(path_flat), FadeIn(label_flat), run_time=2.0)
        self.play(Create(curve), FadeIn(label_growth), run_time=3.0)
        
        # Highlight gap
        gap_arrow = DoubleArrow(start=[-1.0, -0.9, 0], end=[-1.0, 1.2, 0], color="#FFFFFF", stroke_width=2)
        gap_text = Text("GAP", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").next_to(gap_arrow, LEFT, buff=0.1)
        
        self.play(GrowArrow(gap_arrow), FadeIn(gap_text), run_time=2.0)
        self.wait(0.6)

class Scene16_14(Scene):
    def construct(self):
        setup_base_scene(self, "CONCLUSION SUMMARY")
        
        # Summary check list box with bold cross out / warning icons
        box = RoundedRectangle(corner_radius=0.2, width=6.0, height=3.5, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.05)
        box.move_to([0, -0.4, 0])
        
        item1 = Text("• NO INFLATION HEDGE", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([-1.2, 0.8, 0], coor_mask=[1,0,0])
        item2 = Text("• ZERO NATIVE YIELD", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([-1.2, 0.1, 0], coor_mask=[1,0,0])
        item3 = Text("• ISSUER / REGULATORY RISK", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([-1.2, -0.6, 0], coor_mask=[1,0,0])
        
        cross1 = Line([-2.5, 0.8, 0], [-2.3, 0.8, 0], color="#FFFFFF", stroke_width=3) # Simplified bullet replacement
        cross2 = Line([-2.5, 0.1, 0], [-2.3, 0.1, 0], color="#FFFFFF", stroke_width=3)
        cross3 = Line([-2.5, -0.6, 0], [-2.3, -0.6, 0], color="#FFFFFF", stroke_width=3)
        
        conclusion = Text("DON'T OVER-ACCUMULATE", font="Arial", weight=BOLD, font_size=18, color="#FFFFFF").move_to([0, 1.4, 0])
        
        self.play(Create(box), FadeIn(conclusion), run_time=2.0)
        self.play(FadeIn(item1), FadeIn(cross1), run_time=1.5)
        self.play(FadeIn(item2), FadeIn(cross2), run_time=1.5)
        self.play(FadeIn(item3), FadeIn(cross3), run_time=1.5)
        
        self.play(box.animate.scale(1.02), run_time=1.0)
        self.play(box.animate.scale(1/1.02), run_time=1.0)
        self.wait(0.5)

# Canvas Configuration

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

    # Title at bottom
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Footer and meta labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene16_15(Scene):
    def construct(self):
        setup_base_scene(self, "WHY NOT ACCUMULATE STABLECOINS?", "STABLECOIN ANALYSIS")
        
        # Literal figurative visual: Dollar coins / Stablecoins stacked in a vault/balance
        coin_group = VGroup()
        for i in range(3):
            c = Circle(radius=0.6, color="#FFFFFF", stroke_width=2.5).shift(UP * (i * 0.8 - 0.8))
            t = Text("$", font="Arial", weight=BOLD, font_size=28, color="#FFFFFF").move_to(c.get_center())
            coin_group.add(VGroup(c, t))
        coin_group.move_to([0, -0.8, 0])
        
        question_mark = Text("?", font="Arial", weight=BOLD, font_size=72, color="#FFFFFF").move_to([0, 1.5, 0])
        
        self.play(FadeIn(coin_group, shift=UP*0.5), Write(question_mark), run_time=1.5)
        self.play(coin_group.animate.rotate(0.2), run_time=1.0)
        self.play(coin_group.animate.rotate(-0.4), run_time=1.0)
        self.play(coin_group.animate.rotate(0.2), run_time=1.0)
        self.wait(2.5)

class Scene16_16(Scene):
    def construct(self):
        setup_base_scene(self, "INFLATION ERODING VALUE", "PURCHASING POWER")
        
        # Literal figurative visual: Dollar bill shrinking under heat/inflation waves
        box = RoundedRectangle(corner_radius=0.2, width=3.0, height=1.8, color="#FFFFFF", stroke_width=2.5).move_to([0, -0.5, 0])
        text_inside = Text("USDT / USDC", font="Arial", weight=BOLD, font_size=18, color="#FFFFFF").move_to(box.get_center())
        bill = VGroup(box, text_inside)
        
        # Downward pressure arrows / Inflation waves
        waves = VGroup(*[
            DashedLine(start=[-2.5, y, 0], end=[2.5, y, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.4)
            for y in np.linspace(1.8, 0.8, 3)
        ])
        down_arrow = Arrow(start=[0, 0.8, 0], end=[0, -0.5, 0], color="#FFFFFF", stroke_width=3)
        
        self.play(FadeIn(bill), FadeIn(waves), run_time=1.5)
        self.play(GrowArrow(down_arrow), bill.animate.scale(0.85), run_time=2.0)
        self.wait(3.1)

class Scene16_17(Scene):
    def construct(self):
        setup_base_scene(self, "SMART CONTRACT RISK", "PLATFORM VULNERABILITY")
        
        # Literal figurative visual: Server box with warning/bug icon
        server = RoundedRectangle(corner_radius=0.15, width=3.2, height=2.2, color="#FFFFFF", stroke_width=2.5).move_to([0, -0.6, 0])
        lines = VGroup(*[Line([-1.2, y, 0], [1.2, y, 0], color="#FFFFFF", stroke_width=1.5) for y in [-1.0, -0.6, -0.2]])
        lights = VGroup(*[Circle(radius=0.08, color="#FFFFFF", fill_opacity=1).move_to([1.2, y, 0]) for y in [-1.0, -0.6, -0.2]])
        server_group = VGroup(server, lines, lights)
        
        alert_box = Polygon([-0.8, 1.5, 0], [0.8, 1.5, 0], [0, 2.3, 0], color="#FFFFFF", stroke_width=2.5)
        exclamation = Text("!", font="Arial", weight=BOLD, font_size=28, color="#FFFFFF").move_to([0, 1.8, 0])
        warning = VGroup(alert_box, exclamation)
        
        self.play(FadeIn(server_group), FadeIn(warning, shift=DOWN*0.3), run_time=1.5)
        self.play(server_group.animate.set_opacity(0.5), run_time=1.0)
        self.play(server_group.animate.set_opacity(1.0), run_time=1.0)
        self.wait(3.1)

class Scene16_18(Scene):
    def construct(self):
        setup_base_scene(self, "YIELD VS. OPPORTUNITY COST", "CAPITAL ALLOCATION")
        
        # Literal figurative visual: Balance scale comparing stablecoins to productive assets
        beam = Line(LEFT * 2.5, RIGHT * 2.5, color="#FFFFFF", stroke_width=3).move_to([0, 0.5, 0])
        fulcrum = Polygon([-0.4, -1.5, 0], [0.4, -1.5, 0], [0, 0.5, 0], color="#FFFFFF", stroke_width=2)
        
        left_pan = Circle(radius=0.6, color="#FFFFFF", stroke_width=2).move_to([-2.5, -0.8, 0])
        left_text = Text("USDT", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(left_pan.get_center())
        
        right_pan = Circle(radius=0.6, color="#FFFFFF", stroke_width=2).move_to([2.5, 0.2, 0])
        right_text = Text("GROWTH", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(right_pan.get_center())
        
        scale = VGroup(beam, fulcrum, left_pan, left_text, right_pan, right_text).move_to([0, -0.3, 0])
        
        self.play(FadeIn(scale), run_time=1.5)
        self.play(scale.animate.rotate(0.25, about_point=fulcrum.get_top()), run_time=1.5)
        self.play(scale.animate.rotate(-0.5, about_point=fulcrum.get_top()), run_time=1.5)
        self.wait(3.1)

class Scene16_19(Scene):
    def construct(self):
        setup_base_scene(self, "CENTRALIZATION & FREEZING", "REGULATORY RISK")
        
        # Literal figurative visual: Bank lock / Shield with a keyhole
        shield = Polygon([0, 1.8, 0], [1.8, 0.8, 0], [1.8, -0.8, 0], [0, -1.8, 0], [-1.8, -0.8, 0], [-1.8, 0.8, 0], color="#FFFFFF", stroke_width=2.5)
        shield.move_to([0, -0.3, 0])
        
        keyhole_circle = Circle(radius=0.3, color="#FFFFFF", stroke_width=2).move_to([0, 0, 0])
        keyhole_rect = Rectangle(width=0.2, height=0.6, color="#FFFFFF", stroke_width=2).move_to([0, -0.4, 0])
        keyhole = VGroup(keyhole_circle, keyhole_rect).move_to([0, -0.2, 0])
        
        lock_group = VGroup(shield, keyhole)
        
        self.play(DrawBorderThenFill(lock_group), run_time=2.0)
        self.play(lock_group.animate.scale(1.1), run_time=1.0)
        self.play(lock_group.animate.scale(1.0), run_time=1.0)
        self.wait(3.6)

class Scene16_20(Scene):
    def construct(self):
        setup_base_scene(self, "COUNTERPARTY DEPENDENCY", "ISSUER RISK")
        
        # Literal figurative visual: Two entities shaking hands or a chain breaking
        box1 = RoundedRectangle(corner_radius=0.1, width=1.5, height=1.2, color="#FFFFFF", stroke_width=2).move_to([-1.8, -0.5, 0])
        t1 = Text("ISSUER", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(box1.get_center())
        
        box2 = RoundedRectangle(corner_radius=0.1, width=1.5, height=1.2, color="#FFFFFF", stroke_width=2).move_to([1.8, -0.5, 0])
        t2 = Text("HOLDER", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(box2.get_center())
        
        bridge = DashedLine(start=[-1.0, -0.5, 0], end=[1.0, -0.5, 0], color="#FFFFFF", stroke_width=3)
        break_mark = VGroup(
            Line([-0.2, 0.2, 0], [0.2, -0.2, 0], color="#FFFFFF", stroke_width=3),
            Line([-0.2, -0.2, 0], [0.2, 0.2, 0], color="#FFFFFF", stroke_width=3)
        ).move_to([0, -0.5, 0])
        
        self.play(FadeIn(box1), FadeIn(box2), Create(bridge), run_time=2.0)
        self.play(FadeIn(break_mark, scale=1.5), run_time=1.5)
        self.wait(4.1)

class Scene16_21(Scene):
    def construct(self):
        setup_base_scene(self, "BALANCING RISK AND REWARD", "STRATEGIC CONCLUSION")
        
        # Literal figurative visual: Target / Bullseye with directional arrows
        circle1 = Circle(radius=1.8, color="#FFFFFF", stroke_width=1.5).move_to([0, -0.5, 0])
        circle2 = Circle(radius=1.1, color="#FFFFFF", stroke_width=2).move_to([0, -0.5, 0])
        circle3 = Circle(radius=0.4, color="#FFFFFF", fill_opacity=1).move_to([0, -0.5, 0])
        
        arrow = Arrow(start=[-2.5, -2.0, 0], end=[-0.4, -0.9, 0], color="#FFFFFF", stroke_width=3)
        
        target = VGroup(circle1, circle2, circle3)
        
        self.play(FadeIn(target), GrowArrow(arrow), run_time=2.0)
        self.play(target.animate.scale(1.05), run_time=1.0)
        self.play(target.animate.scale(0.95), run_time=1.0)
        self.wait(3.6)