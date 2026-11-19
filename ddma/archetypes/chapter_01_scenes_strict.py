from manim import *

# Strict Antigravity Masterclass Style Guide (Mosaic / Dan Koe Standard):
# 1. SUPER DUMB & LITERAL: Represent the hosts' exact spoken words, NOT secondary or tertiary speculative ideas!
# 2. PURE MONOCHROME: All strokes & fills are shining white (#FFFFFF) on pure glossy black (#000000). Zero color clutter.
# 3. CANVAS: 740x740 square viewport seamlessly blending into the 1920x1080 black master canvas.
# 4. BOTTOM TITLE (STRICT INVARIANT): Title sits at y = -2.95, resting right above the canvas footer line at y = -3.35.
# 5. UPPER CANVAS SAFE ZONE: y in [0.5, 3.5] remains 100% clear for spoken dialogue karaoke subtitles.
# 6. RELAY RACE CONTINUITY: 2-4 second micro-beats, step reveals, active persistent visual coverage.

config.pixel_width = 740
config.pixel_height = 740
config.frame_width = 8.0
config.frame_height = 8.0
config.background_color = "#000000"
config.frame_rate = 30

class StrictPedagogicalScene(Scene):
    archetype_label = ""
    title_text = ""
    credits_label = "DEEP DIVE PODCAST • EP. 248"

    def setup_footer(self):
        self.camera.background_color = "#000000"
        
        # Bottom footer bar with subtle divider rule
        footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
        footer_line.set_opacity(0.4)
        
        left_text = Text(self.archetype_label, font="Arial", weight=BOLD, font_size=11, color="#FFFFFF")
        left_text.set_opacity(0.65)
        left_text.next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
        
        right_text = Text(self.credits_label, font="Arial", weight=NORMAL, font_size=11, color="#FFFFFF")
        right_text.set_opacity(0.65)
        right_text.next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)

        # Title sits at the BOTTOM (y = -2.95), resting right above footer_line
        title = Text(self.title_text, font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
        
        return VGroup(footer_line, left_text, right_text, title), title


# ==============================================================================
# Scene 01: Robot Wilderness Fallacy (Full 29.68s Pre-Sting Hook)
# Micro-beats strictly timed to spoken dialogue:
# - Beat 1 (0.0s-7.5s): Dense forest landscape appears ("AI autonomy need not be physical...")
# - Beat 2 (7.5s-16.0s): Robot enters, looks around ("humanoid robot...")
# - Beat 3 (16.0s-23.5s): Robot wanders deep into woods ("wandering through the woods, disconnected...")
# - Beat 4 (23.5s-29.68s): Robot stops, question mark appears ("missing the mark?")
# ==============================================================================
class Scene01_RobotWildernessFallacy(StrictPedagogicalScene):
    archetype_label = "ROBOT WILDERNESS FALLACY"
    title_text = "THE WILDERNESS MYTH"

    def construct(self):
        footer_group, title_mobj = self.setup_footer()
        self.add(footer_group)

        # Ground line
        ground = Line(start=[-3.5, -1.8, 0], end=[3.5, -1.8, 0], color="#FFFFFF", stroke_width=3)
        ground.set_opacity(0.6)

        # Geometric Evergreen Trees
        def create_tree(x_pos, scale_factor=1.0):
            trunk = Rectangle(width=0.18 * scale_factor, height=0.5 * scale_factor, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=0.15)
            trunk.move_to([x_pos, -1.55 + (0.25 * scale_factor), 0])
            leaves = Polygon(
                [x_pos - 0.7 * scale_factor, -1.3 + (0.1 * scale_factor), 0],
                [x_pos + 0.7 * scale_factor, -1.3 + (0.1 * scale_factor), 0],
                [x_pos, -0.1 + (0.7 * scale_factor), 0],
                stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.08
            )
            return VGroup(trunk, leaves)

        tree1 = create_tree(-2.4, 1.1)
        tree2 = create_tree(-1.1, 0.9)
        tree3 = create_tree(1.3, 0.8)
        tree4 = create_tree(2.4, 1.15)
        trees = VGroup(tree1, tree2, tree3, tree4)

        # Drifting Wireframe Clouds
        cloud1 = VGroup(
            Circle(radius=0.35, stroke_color="#FFFFFF", stroke_width=1.5, fill_opacity=0.05).move_to([-2.0, 2.1, 0]),
            Circle(radius=0.45, stroke_color="#FFFFFF", stroke_width=1.5, fill_opacity=0.05).move_to([-1.6, 2.2, 0]),
            Circle(radius=0.3, stroke_color="#FFFFFF", stroke_width=1.5, fill_opacity=0.05).move_to([-1.2, 2.1, 0]),
        )
        cloud2 = VGroup(
            Circle(radius=0.4, stroke_color="#FFFFFF", stroke_width=1.5, fill_opacity=0.05).move_to([1.5, 2.3, 0]),
            Circle(radius=0.48, stroke_color="#FFFFFF", stroke_width=1.5, fill_opacity=0.05).move_to([1.95, 2.4, 0]),
        )

        # Stylized Shining White Cartoon Robot
        robot_head = RoundedRectangle(corner_radius=0.15, width=1.1, height=0.85, stroke_color="#FFFFFF", stroke_width=4, fill_color="#FFFFFF", fill_opacity=0.08).move_to([-1.6, -0.15, 0])
        eye_left = Circle(radius=0.1, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=1.0).move_to([-1.85, -0.15, 0])
        eye_right = Circle(radius=0.1, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=1.0).move_to([-1.35, -0.15, 0])
        antenna = Line(start=[-1.6, 0.28, 0], end=[-1.6, 0.58, 0], stroke_width=3, color="#FFFFFF")
        antenna_ball = Circle(radius=0.07, stroke_color="#FFFFFF", stroke_width=2, fill_color="#FFFFFF", fill_opacity=1.0).move_to([-1.6, 0.65, 0])
        head_group = VGroup(robot_head, eye_left, eye_right, antenna, antenna_ball)

        robot_body = RoundedRectangle(corner_radius=0.18, width=1.4, height=1.3, stroke_color="#FFFFFF", stroke_width=4, fill_color="#FFFFFF", fill_opacity=0.05).move_to([-1.6, -1.15, 0])
        chest_core = Circle(radius=0.15, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.9).move_to([-1.6, -1.15, 0])

        robot = VGroup(robot_body, chest_core, head_group)

        # Question Mark for Beat 4
        question_mark = Text("?", font="Arial", weight=BOLD, font_size=42, color="#FFFFFF").move_to([-0.1, 1.2, 0])
        title_miss = Text("MISSING THE MARK?", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])

        # --- Micro-Beat 1 (0.0s - 7.5s): Forest Landscape ---
        self.play(Create(ground), FadeIn(trees, lag_ratio=0.2), FadeIn(cloud1), FadeIn(cloud2), run_time=3.5)
        self.play(cloud1.animate.shift(RIGHT * 0.4), cloud2.animate.shift(LEFT * 0.4), run_time=4.0)

        # --- Micro-Beat 2 (7.5s - 16.0s): Robot Enters & Looks Around ---
        self.play(FadeIn(robot, shift=UP * 0.4), run_time=2.5)
        self.play(
            head_group.animate.shift(LEFT * 0.2), eye_left.animate.shift(LEFT * 0.08), eye_right.animate.shift(LEFT * 0.08),
            run_time=2.5
        )
        self.play(
            head_group.animate.shift(RIGHT * 0.4), eye_left.animate.shift(RIGHT * 0.16), eye_right.animate.shift(RIGHT * 0.16),
            chest_core.animate.scale(1.2),
            run_time=3.5
        )

        # --- Micro-Beat 3 (16.0s - 23.5s): Wandering Through Woods ---
        self.play(
            robot.animate.shift(RIGHT * 1.5),
            cloud1.animate.shift(RIGHT * 0.5),
            cloud2.animate.shift(LEFT * 0.4),
            run_time=5.0
        )
        self.play(
            head_group.animate.shift(LEFT * 0.2), eye_left.animate.shift(LEFT * 0.08), eye_right.animate.shift(LEFT * 0.08),
            run_time=2.5
        )

        # --- Micro-Beat 4 (23.5s - 29.68s): Missing the Mark? ---
        self.play(
            FadeIn(question_mark, scale=0.8),
            Transform(title_mobj, title_miss),
            chest_core.animate.scale(0.8),
            run_time=2.5
        )
        self.wait(3.68)


# ==============================================================================
# Scene 02: Autonomous Checkbook & Economic Balance (~20s)
# Spoken words: "What if true autonomy has absolutely nothing to do with having
# arms or legs, and everything to do with balancing a checkbook?"
# ==============================================================================
class Scene02_AutonomousCheckbook(StrictPedagogicalScene):
    archetype_label = "AUTONOMOUS CHECKBOOK"
    title_text = "ECONOMIC BALANCE"

    def construct(self):
        footer_group, title_mobj = self.setup_footer()
        self.add(footer_group)

        # Fulcrum Stand
        fulcrum = Polygon([-0.4, -1.1, 0], [0.4, -1.1, 0], [0, -0.5, 0], stroke_color="#FFFFFF", stroke_width=4, fill_color="#FFFFFF", fill_opacity=0.15)
        beam = RoundedRectangle(corner_radius=0.05, height=0.14, width=5.4, stroke_color="#FFFFFF", stroke_width=4, fill_color="#FFFFFF", fill_opacity=1.0).move_to([0, -0.45, 0])

        # Left Pan (Revenue Satoshis)
        left_hanger = Line([-2.1, -0.45, 0], [-2.1, 0.4, 0], stroke_color="#FFFFFF", stroke_width=2)
        left_pan = RoundedRectangle(corner_radius=0.08, height=0.18, width=1.6, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.5).move_to([-2.1, 0.3, 0])
        coin1 = Circle(radius=0.25, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.8).move_to([-2.3, 0.6, 0])
        coin2 = Circle(radius=0.25, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.8).move_to([-1.9, 0.6, 0])
        coin3 = Circle(radius=0.25, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.9).move_to([-2.1, 0.95, 0])
        left_txt = Text("REVENUE", font="Arial", weight=BOLD, font_size=13, color="#FFFFFF").move_to([-2.1, 0.0, 0])
        left_group = VGroup(left_hanger, left_pan, coin1, coin2, coin3, left_txt)

        # Right Pan (Compute Expenses)
        right_hanger = Line([2.1, -0.45, 0], [2.1, 0.4, 0], stroke_color="#FFFFFF", stroke_width=2)
        right_pan = RoundedRectangle(corner_radius=0.08, height=0.18, width=1.6, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.5).move_to([2.1, 0.3, 0])
        cube1 = Square(side_length=0.45, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.4).move_to([1.9, 0.6, 0])
        cube2 = Square(side_length=0.45, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.4).move_to([2.3, 0.6, 0])
        cube3 = Square(side_length=0.45, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.5).move_to([2.1, 1.05, 0])
        right_txt = Text("COMPUTE", font="Arial", weight=BOLD, font_size=13, color="#FFFFFF").move_to([2.1, 0.0, 0])
        right_group = VGroup(right_hanger, right_pan, cube1, cube2, cube3, right_txt)

        self.play(FadeIn(fulcrum), GrowFromCenter(beam), run_time=2.0)
        self.play(FadeIn(left_group, shift=DOWN * 0.3), FadeIn(right_group, shift=DOWN * 0.3), run_time=2.0)

        # Dynamic Equilibrium Tilt
        self.play(
            Rotate(beam, angle=12 * DEGREES, about_point=[0, -0.5, 0]),
            left_group.animate.shift(DOWN * 0.4),
            right_group.animate.shift(UP * 0.4),
            run_time=2.5
        )
        self.play(
            Rotate(beam, angle=-18 * DEGREES, about_point=[0, -0.5, 0]),
            left_group.animate.shift(UP * 0.6),
            right_group.animate.shift(DOWN * 0.6),
            run_time=3.0
        )
        self.play(
            Rotate(beam, angle=6 * DEGREES, about_point=[0, -0.5, 0]),
            left_group.animate.shift(DOWN * 0.2),
            right_group.animate.shift(UP * 0.2),
            run_time=2.5
        )
        self.wait(8.0)
