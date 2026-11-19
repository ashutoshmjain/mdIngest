from manim import *

config.pixel_width = 1080
config.pixel_height = 1080
config.frame_width = 8.0
config.frame_height = 8.0
config.background_color = "#0A0F1D"
config.frame_rate = 30

class TestSquareScene(Scene):
    def construct(self):
        # Title
        title = Text("THE BALANCE OF AUTONOMY", font="Arial", weight=BOLD, font_size=28, color="#F8FAFC")
        title.to_edge(UP, buff=0.6)
        
        # Subtitle
        sub = Text("Feynman Fulcrum Principle", font="Arial", font_size=18, color="#94A3B8")
        sub.next_to(title, DOWN, buff=0.15)
        
        self.play(FadeIn(title), FadeIn(sub), run_time=0.8)
        
        # Fulcrum
        fulcrum = Polygon([-0.4, -1.2, 0], [0.4, -1.2, 0], [0, -0.6, 0], color="#64748B", fill_opacity=1.0)
        beam = RoundedRectangle(corner_radius=0.08, height=0.18, width=5.2, color="#00E5FF", fill_color="#00E5FF", fill_opacity=1.0)
        beam.move_to([0, -0.5, 0])
        
        self.play(FadeIn(fulcrum), GrowFromCenter(beam), run_time=1.0)
        
        # Left Weight (Agent Wrappers)
        left_box = RoundedRectangle(corner_radius=0.1, height=1.0, width=1.5, color="#EF4444", fill_color="#1E1015", fill_opacity=0.9, stroke_width=4)
        left_box.move_to([-1.8, 0.1, 0])
        left_label = Text("WRAPPERS", font="Arial", weight=BOLD, font_size=16, color="#FCA5A5")
        left_label.move_to(left_box.get_center())
        left_grp = VGroup(left_box, left_label)
        
        # Right Weight (Physical Constraints)
        right_box = RoundedRectangle(corner_radius=0.1, height=1.0, width=1.5, color="#10B981", fill_color="#0C1E14", fill_opacity=0.9, stroke_width=4)
        right_box.move_to([1.8, 0.1, 0])
        right_label = Text("PHYSICS", font="Arial", weight=BOLD, font_size=16, color="#86EFAC")
        right_label.move_to(right_box.get_center())
        right_grp = VGroup(right_box, right_label)
        
        self.play(FadeIn(left_grp, shift=DOWN*0.5), FadeIn(right_grp, shift=DOWN*0.5), run_time=1.0)
        
        # Tilt state change (Micro-beat)
        self.play(
            Rotate(beam, angle=12 * DEGREES, about_point=[0, -0.6, 0]),
            left_grp.animate.shift(DOWN * 0.45 + RIGHT * 0.05),
            right_grp.animate.shift(UP * 0.45 + LEFT * 0.05),
            run_time=1.2
        )
        self.wait(1.0)
