import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Global configuration for monochrome, size, and layout

def add_base_elements(scene, category_text="SOCIAL SECURITY IDENTITY"):
    """Adds the required bottom title, footer line, and metadata labels with zero colors."""
    # Bottom Title at y = -2.95
    title = Text("IT DOESN'T HAVE A SOCIAL SECURITY NUMBER", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF")
    title.move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Footer Line and Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

class Scene12_01(Scene):
    def construct(self):
        add_base_elements(self, "IDENTITY VERIFICATION")
        
        # Literal figurative visual: A large official ID Card / Document outline with a missing SSN slot (X marks)
        card = RoundedRectangle(corner_radius=0.2, width=4.5, height=3.0, color="#FFFFFF", stroke_width=2.0)
        card.move_to([0, -1.0, 0])
        
        # Header line inside card
        card_header = Line(LEFT * 1.8, RIGHT * 1.8, color="#FFFFFF", stroke_width=2.0).move_to(card.get_top() + DOWN * 0.6)
        
        # Avatar placeholder (circle + arc)
        avatar_head = Circle(radius=0.4, color="#FFFFFF", stroke_width=2.0).move_to(card.get_top() + LEFT * 1.3 + DOWN * 1.3)
        avatar_body = Arc(radius=0.7, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2.0).move_to(card.get_top() + LEFT * 1.3 + DOWN * 2.1)
        
        # Text lines representation
        line1 = Line(LEFT * 0.8, RIGHT * 1.2, color="#FFFFFF", stroke_width=2.0).move_to(card.get_top() + RIGHT * 0.6 + DOWN * 1.1)
        line2 = Line(LEFT * 0.8, RIGHT * 0.6, color="#FFFFFF", stroke_width=2.0).move_to(card.get_top() + RIGHT * 0.3 + DOWN * 1.6)
        
        # The Missing SSN Block with big X's
        ssn_box = Rectangle(width=3.2, height=0.7, color="#FFFFFF", stroke_width=2.0).move_to(card.get_bottom() + UP * 0.6)
        cross1 = Line(ssn_box.get_corner(DL) + [0.1, 0.1, 0], ssn_box.get_corner(UR) + [-0.1, -0.1, 0], color="#FFFFFF", stroke_width=2.5)
        cross2 = Line(ssn_box.get_corner(UL) + [0.1, -0.1, 0], ssn_box.get_corner(DR) + [-0.1, 0.1, 0], color="#FFFFFF", stroke_width=2.5)
        
        group = VGroup(card, card_header, avatar_head, avatar_body, line1, line2, ssn_box, cross1, cross2)
        
        self.play(DrawBorderThenFill(group), run_time=3.5)
        self.play(group.animate.scale(1.05), run_time=1.5)
        self.play(group.animate.scale(0.95), run_time=1.8)
        self.wait(0.6)

class Scene12_02(Scene):
    def construct(self):
        add_base_elements(self, "SYSTEM DATABASE")
        
        # Literal figurative visual: A vertical server stack with flashing data blocks and an empty slot
        server_stack = VGroup()
        for i in range(4):
            rect = RoundedRectangle(corner_radius=0.1, width=4.0, height=0.7, color="#FFFFFF", stroke_width=2.0)
            rect.move_to([0, 1.0 - (i * 0.9), 0])
            
            # Server lights
            light1 = Circle(radius=0.08, color="#FFFFFF", fill_opacity=1.0).move_to(rect.get_left() + RIGHT * 0.4)
            light2 = Circle(radius=0.08, color="#FFFFFF", fill_opacity=0.3).move_to(rect.get_left() + RIGHT * 0.7)
            
            # Data lines
            d_line = Line(LEFT * 0.8, RIGHT * 1.2, color="#FFFFFF", stroke_width=1.5).move_to(rect.get_center() + RIGHT * 0.4)
            
            server_stack.add(VGroup(rect, light1, light2, d_line))
            
        # Highlight missing record at the bottom
        empty_label = Text("NO RECORD", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(server_stack[3].get_center())
        server_stack[3].add(empty_label)
        
        self.play(FadeIn(server_stack, shift=DOWN), run_time=4.0)
        
        # Pulsing effect on the empty record slot
        self.play(server_stack[3].animate.set_opacity(0.4), run_time=1.5)
        self.play(server_stack[3].animate.set_opacity(1.0), run_time=1.5)
        self.wait(0.4)

class Scene12_03(Scene):
    def construct(self):
        add_base_elements(self, "DIGITAL ALIEN")
        
        # Literal figurative visual: A generic robot head with a question mark query symbol emerging from it
        head = RoundedRectangle(corner_radius=0.3, width=3.0, height=2.6, color="#FFFFFF", stroke_width=2.0)
        head.move_to([0, -0.6, 0])
        
        # Eyes (squares)
        eye_l = Square(side_length=0.4, color="#FFFFFF", stroke_width=2.0).move_to(head.get_center() + [-0.7, 0.3, 0])
        eye_r = Square(side_length=0.4, color="#FFFFFF", stroke_width=2.0).move_to(head.get_center() + [0.7, 0.3, 0])
        
        # Mouth slot
        mouth = Line(LEFT * 0.8, RIGHT * 0.8, color="#FFFFFF", stroke_width=2.0).move_to(head.get_center() + [0, -0.6, 0])
        
        # Antenna
        antenna_base = Line(UP * 0.0, UP * 0.6, color="#FFFFFF", stroke_width=2.0).move_to(head.get_top())
        antenna_top = Circle(radius=0.15, color="#FFFFFF", fill_opacity=0.5, stroke_width=2.0).move_to(antenna_base.get_top() + UP * 0.15)
        
        # Question mark floating above
        q_mark = Text("?", font="Arial", weight=BOLD, font_size=72, color="#FFFFFF").move_to([0, 1.6, 0])
        
        robot_group = VGroup(head, eye_l, eye_r, mouth, antenna_base, antenna_top, q_mark)
        
        self.play(GrowFromCenter(robot_group), run_time=4.0)
        self.play(q_mark.animate.scale(1.2), run_time=1.5)
        self.play(q_mark.animate.scale(0.83), run_time=1.5)
        self.wait(0.4)

class Scene12_04(Scene):
    def construct(self):
        add_base_elements(self, "RECORD SYSTEM")
        
        # Literal figurative visual: A massive checkbook / ledger with a void stamp across it
        book_base = RoundedRectangle(corner_radius=0.1, width=5.0, height=3.2, color="#FFFFFF", stroke_width=2.0)
        book_base.move_to([0, -0.6, 0])
        
        # Ledger lines
        lines = VGroup()
        for i in range(5):
            l = Line(LEFT * 2.0, RIGHT * 2.0, color="#FFFFFF", stroke_width=1.5).move_to(book_base.get_top() + DOWN * (0.6 + i * 0.5))
            lines.add(l)
            
        # Bold VOID stamp diagonal box
        stamp_box = RoundedRectangle(corner_radius=0.2, width=4.0, height=1.2, color="#FFFFFF", stroke_width=3.0)
        stamp_box.move_to(book_base.get_center())
        stamp_box.rotate(0.2)
        
        stamp_text = Text("NO SSN FOUND", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to(stamp_box.get_center())
        stamp_text.rotate(0.2)
        
        ledger_group = VGroup(book_base, lines, stamp_box, stamp_text)
        
        self.play(Create(book_base), FadeIn(lines), run_time=3.0)
        self.play(GrowFromCenter(stamp_box), Write(stamp_text), run_time=3.0)
        self.wait(1.4)

class Scene12_05(Scene):
    def construct(self):
        add_base_elements(self, "SYSTEM CHECK")
        
        # Literal figurative visual: A large magnifying glass scanning an empty file folder
        folder = Polygon(
            [-2.2, 1.0, 0], [-0.8, 1.0, 0], [-0.4, 1.4, 0], [2.2, 1.4, 0],
            [2.2, -1.8, 0], [-2.2, -1.8, 0], color="#FFFFFF", stroke_width=2.0
        )
        folder.move_to([0, -0.4, 0])
        
        # Inside document lines
        doc_line1 = Line(LEFT * 1.5, RIGHT * 1.5, color="#FFFFFF", stroke_width=2.0).move_to(folder.get_center() + UP * 0.4)
        doc_line2 = Line(LEFT * 1.5, RIGHT * 0.5, color="#FFFFFF", stroke_width=2.0).move_to(folder.get_center() + DOWN * 0.2)
        
        # Magnifying glass moving across
        lens = Circle(radius=1.1, color="#FFFFFF", stroke_width=3.0).move_to([0.5, -0.4, 0])
        handle = Line([0.5 + 0.8, -0.4 - 0.8, 0], [0.5 + 1.8, -0.4 - 1.8, 0], color="#FFFFFF", stroke_width=5.0)
        mag_glass = VGroup(lens, handle)
        
        self.play(Create(folder), FadeIn(doc_line1), FadeIn(doc_line2), run_time=3.0)
        self.play(GrowFromCenter(mag_glass), run_time=2.0)
        self.play(mag_glass.animate.shift(LEFT * 1.5), run_time=1.2)
        self.play(mag_glass.animate.shift(RIGHT * 1.5), run_time=1.2)
        
class Scene12_06(Scene):
    def construct(self):
        add_base_elements(self, "DATA ANOMALY")
        
        # Literal figurative visual: A standard grid with a massive barrier wall blocking entry
        grid = VGroup()
        for i in range(5):
            v_line = Line([ -2.5 + i*1.25, 1.5, 0], [ -2.5 + i*1.25, -2.5, 0], color="#FFFFFF", stroke_width=1.0).set_opacity(0.3)
            grid.add(v_line)
        for j in range(5):
            h_line = Line([-2.5, 1.5 - j*1.0, 0], [2.5, 1.5 - j*1.0, 0], color="#FFFFFF", stroke_width=1.0).set_opacity(0.3)
            grid.add(h_line)
            
        # Barrier wall (Double vertical thick lines with hazard hatches)
        wall = Rectangle(width=0.6, height=3.5, color="#FFFFFF", fill_opacity=0.3, stroke_width=3.0)
        wall.move_to([0, -0.5, 0])
        
        # Lock icon in center of wall
        lock_body = RoundedRectangle(corner_radius=0.1, width=1.0, height=0.8, color="#FFFFFF", stroke_width=2.0).move_to(wall.get_center() + DOWN * 0.2)
        lock_shackle = Arc(radius=0.4, start_angle=0, angle=PI, color="#FFFFFF", stroke_width=2.0).move_to(lock_body.get_top())
        lock = VGroup(lock_body, lock_shackle)
        
        self.play(FadeIn(grid), run_time=2.0)
        self.play(GrowFromCenter(wall), FadeIn(lock), run_time=3.0)
        self.play(wall.animate.scale(1.05), lock.animate.scale(1.05), run_time=1.4)
        self.wait(1.0)

class Scene12_07(Scene):
    def construct(self):
        add_base_elements(self, "SYSTEM STATUS")
        
        # Literal figurative visual: A large digital terminal screen displaying error message layout
        screen = RoundedRectangle(corner_radius=0.2, width=6.0, height=3.6, color="#FFFFFF", stroke_width=2.0)
        screen.move_to([0, -0.5, 0])
        
        # Terminal top bar
        top_bar = Line(LEFT * 3.0, RIGHT * 3.0, color="#FFFFFF", stroke_width=2.0).move_to(screen.get_top() + DOWN * 0.5)
        dot1 = Circle(radius=0.08, color="#FFFFFF", fill_opacity=1.0).move_to(top_bar.get_left() + RIGHT * 0.3)
        dot2 = Circle(radius=0.08, color="#FFFFFF", fill_opacity=1.0).move_to(top_bar.get_left() + RIGHT * 0.6)
        dot3 = Circle(radius=0.08, color="#FFFFFF", fill_opacity=1.0).move_to(top_bar.get_left() + RIGHT * 0.9)
        
        # Status text inside screen
        status_txt1 = Text("ERROR: SSN NOT FOUND", font="Arial", weight=BOLD, font_size=18, color="#FFFFFF").move_to(screen.get_center() + UP * 0.3)
        status_txt2 = Text("IDENTITY UNVERIFIED", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to(screen.get_center() + DOWN * 0.4)
        
        # Blinking cursor
        cursor = Rectangle(width=0.15, height=0.3, color="#FFFFFF", fill_opacity=1.0).next_to(status_txt2, RIGHT, buff=0.1)
        
        terminal_group = VGroup(screen, top_bar, dot1, dot2, dot3, status_txt1, status_txt2, cursor)
        
        self.play(Create(screen), Create(top_bar), FadeIn(dot1, dot2, dot3), run_time=2.5)
        self.play(Write(status_txt1), Write(status_txt2), FadeIn(cursor), run_time=3.0)
        
        # Blink cursor
        self.play(FadeOut(cursor), run_time=0.9)
        self.play(FadeIn(cursor), run_time=1.0)
        self.wait(0.0)

# Configure canvas dimensions and background

def setup_scene(scene, category_text):
    """Applies strict template rules: bottom title, footer bar, and metadata labels."""
    title = Text("IT DOESN'T HAVE A SOCIAL SECURITY NUMBER", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)
    scene.play(FadeIn(title), run_time=0.6)


class Scene12_08(Scene):
    def construct(self):
        setup_scene(self, "IDENTITY VERIFICATION")
        
        # Figurative: A large ID Card with a missing photo/number slot and a large question mark
        card = RoundedRectangle(corner_radius=0.2, width=3.6, height=2.4, color="#FFFFFF", stroke_width=2)
        card.move_to([0, -1.05, 0])
        
        # Card inner details (lines representing text)
        line1 = Line(LEFT*1.4, LEFT*0.2, color="#FFFFFF", stroke_width=2).move_to([-0.3, -0.3, 0])
        line2 = Line(LEFT*1.4, LEFT*0.6, color="#FFFFFF", stroke_width=2).move_to([-0.5, -0.7, 0])
        
        # Missing SSN box (dashed)
        box = DashedRectangle(width=2.8, height=0.6, color="#FFFFFF", stroke_width=2).move_to([0, -1.8, 0])
        ssn_text = Text("XXX-XX-XXXX", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, -1.8, 0]).set_opacity(0.4)
        
        # Big question mark floating above
        q_mark = Text("?", font="Arial", weight=BOLD, font_size=72, color="#FFFFFF").move_to([0, 0.8, 0])
        
        self.play(
            FadeIn(card, shift=DOWN*0.2),
            Create(line1),
            Create(line2),
            Create(box),
            Write(ssn_text),
            Write(q_mark),
            run_time=2.0
        )
        
        # Pulse the question mark
        self.play(q_mark.animate.scale(1.2).set_opacity(0.6), run_time=1.5)
        self.play(q_mark.animate.scale(0.83).set_opacity(1.0), run_time=1.5)
        self.wait(1.8)


class Scene12_09(Scene):
    def construct(self):
        setup_scene(self, "SYSTEM DATABASE")
        
        # Figurative: Server rack with blinking lights and an empty slot
        rack = RoundedRectangle(corner_radius=0.1, width=3.0, height=4.2, color="#FFFFFF", stroke_width=2)
        rack.move_to([0, -1.05, 0])
        
        # Server units (horizontal rectangles)
        units = VGroup()
        for i in range(3):
            u = RoundedRectangle(corner_radius=0.05, width=2.6, height=1.0, color="#FFFFFF", stroke_width=1.5)
            u.move_to([0, 0.4 - i * 1.3, 0])
            
            # blinking LED dots
            dot1 = Circle(radius=0.06, color="#FFFFFF", fill_opacity=1).move_to([-1.0, 0.4 - i * 1.3, 0])
            dot2 = Circle(radius=0.06, color="#FFFFFF", fill_opacity=1).move_to([-0.8, 0.4 - i * 1.3, 0])
            units.add(VGroup(u, dot1, dot2))
            
        # Fourth unit empty / glitching with an X
        empty_u = RoundedRectangle(corner_radius=0.05, width=2.6, height=1.0, color="#FFFFFF", stroke_width=1.5)
        empty_u.move_to([0, -2.2, 0]).set_opacity(0.3)
        cross_line1 = Line(UP*0.3+LEFT*0.3, DOWN*0.3+RIGHT*0.3, color="#FFFFFF", stroke_width=2).move_to([0, -2.2, 0])
        cross_line2 = Line(UP*0.3+RIGHT*0.3, DOWN*0.3+LEFT*0.3, color="#FFFFFF", stroke_width=2).move_to([0, -2.2, 0])
        
        missing_label = Text("NO RECORD", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, 1.6, 0])

        self.play(
            Create(rack),
            FadeIn(units),
            Create(empty_u),
            Create(cross_line1),
            Create(cross_line2),
            Write(missing_label),
            run_time=2.5
        )
        self.wait(4.3)


class Scene12_10(Scene):
    def construct(self):
        setup_scene(self, "FORM FILLING")
        
        # Figurative: A document form with input fields and a flashing cursor at the SSN line
        paper = Rectangle(width=3.4, height=4.4, color="#FFFFFF", stroke_width=2).move_to([0, -1.05, 0])
        
        # Document title lines
        doc_line1 = Line(LEFT*1.2, RIGHT*1.2, color="#FFFFFF", stroke_width=2).move_to([0, 0.6, 0])
        doc_line2 = Line(LEFT*1.2, RIGHT*0.4, color="#FFFFFF", stroke_width=2).move_to([-0.4, 0.2, 0])
        
        # Form fields
        field_label = Text("SOCIAL SECURITY #", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").move_to([0, -0.4, 0])
        field_box = RoundedRectangle(corner_radius=0.1, width=2.8, height=0.6, color="#FFFFFF", stroke_width=2).move_to([0, -0.9, 0])
        
        # Blinking cursor / ERROR text inside field
        err_text = Text("ERROR: NULL", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, -0.9, 0])
        
        # Hand / pointer pointing at it
        pointer = Arrow(start=UP*0.8, end=DOWN*0.2, color="#FFFFFF", stroke_width=3).move_to([0, -2.1, 0])
        
        self.play(
            Create(paper),
            Create(doc_line1),
            Create(doc_line2),
            Write(field_label),
            Create(field_box),
            run_time=2.0
        )
        self.play(
            Write(err_text),
            GrowArrow(pointer),
            run_time=2.0
        )
        self.wait(3.4)


class Scene12_11(Scene):
    def construct(self):
        setup_scene(self, "ANONYMOUS ENTITY")
        
        # Figurative: A hooded/faceless silhouette profile with a glowing digital grid pattern
        head_circle = Circle(radius=0.9, color="#FFFFFF", stroke_width=2).move_to([0, 0.0, 0])
        shoulders = Arc(radius=1.8, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2).move_to([0, -1.8, 0])
        
        # Internal zeros and ones floating
        matrix_text = Text("0 1 0 1\n1 0 1 0", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([0, 0.0, 0]).set_opacity(0.4)
        
        # Big Prohibition / Null sign over it
        null_circle = Circle(radius=2.0, color="#FFFFFF", stroke_width=3).move_to([0, -0.9, 0])
        null_slash = Line(UP*1.4+LEFT*1.4, DOWN*1.4+RIGHT*1.4, color="#FFFFFF", stroke_width=3).move_to([0, -0.9, 0])
        
        self.play(
            Create(head_circle),
            Create(shoulders),
            Write(matrix_text),
            run_time=2.0
        )
        self.play(
            Create(null_circle),
            Create(null_slash),
            run_time=2.0
        )
        self.wait(3.4)


class Scene12_12(Scene):
    def construct(self):
        setup_scene(self, "DATABASE QUERY")
        
        # Figurative: Magnifying glass inspecting an empty data grid
        grid = VGroup()
        for i in range(3):
            for j in range(3):
                cell = Square(side_length=0.8, color="#FFFFFF", stroke_width=1).move_to([(j-1)*0.9, 0.3 + (i-1)*0.9, 0])
                cell.set_opacity(0.3)
                grid.add(cell)
                
        # Magnifying glass
        lens = Circle(radius=1.2, color="#FFFFFF", stroke_width=3).move_to([0.2, 0.3, 0])
        handle = Line(DOWN*0.8+RIGHT*0.8, DOWN*1.8+RIGHT*1.8, color="#FFFFFF", stroke_width=4)
        
        magnifier = VGroup(lens, handle).move_to([0, -0.3, 0])
        
        # Question mark inside lens
        q_in_lens = Text("?", font="Arial", weight=BOLD, font_size=36, color="#FFFFFF").move_to([0, -0.3, 0])

        self.play(
            FadeIn(grid),
            Create(magnifier),
            Write(q_in_lens),
            run_time=2.5
        )
        
        # Move magnifying glass across grid
        self.play(
            magnifier.animate.shift(LEFT*1.0 + UP*0.5),
            q_in_lens.animate.shift(LEFT*1.0 + UP*0.5),
            run_time=2.0
        )
        self.wait(2.9)


class Scene12_13(Scene):
    def construct(self):
        setup_scene(self, "SYSTEM REJECTION")
        
        # Figurative: A giant red-style X stamp over a digital file icon
        file_icon = RoundedRectangle(corner_radius=0.15, width=2.6, height=3.4, color="#FFFFFF", stroke_width=2).move_to([0, -1.05, 0])
        file_fold = Polygon([-1.3, 0.65, 0], [-0.5, 0.65, 0], [-1.3, -0.15, 0], color="#FFFFFF", stroke_width=2, fill_opacity=0.2)
        file_fold.move_to([0, -1.05, 0])
        
        # Giant X stamp
        x1 = Line(UP*1.2+LEFT*1.2, DOWN*1.2+RIGHT*1.2, color="#FFFFFF", stroke_width=6).move_to([0, -1.05, 0])
        x2 = Line(UP*1.2+RIGHT*1.2, DOWN*1.2+LEFT*1.2, color="#FFFFFF", stroke_width=6).move_to([0, -1.05, 0])
        
        stamp_group = VGroup(x1, x2)
        
        self.play(
            Create(file_icon),
            Create(file_fold),
            run_time=2.0
        )
        
        self.play(
            GrowFromCenter(stamp_group),
            run_time=1.5
        )
        self.wait(3.9)


class Scene12_14(Scene):
    def construct(self):
        setup_scene(self, "FINAL VERDICT")
        
        # Figurative: A large digital badge reading "UNREGISTERED" with lock icon
        badge = RoundedRectangle(corner_radius=0.3, width=5.0, height=2.0, color="#FFFFFF", stroke_width=3).move_to([0, -1.05, 0])
        
        lock_body = RoundedRectangle(corner_radius=0.1, width=0.8, height=0.7, color="#FFFFFF", stroke_width=2).move_to([-1.6, -1.05, 0])
        lock_shackle = Arc(radius=0.35, start_angle=0, angle=PI, color="#FFFFFF", stroke_width=2).move_to([-1.6, -0.6, 0])
        
        text_unreg = Text("UNREGISTERED", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to([0.4, -1.05, 0])
        
        sub_text = Text("STATUS: NO SSN FOUND", font="Arial", weight=NORMAL, font_size=12, color="#FFFFFF").move_to([0, 0.5, 0]).set_opacity(0.7)

        self.play(
            Create(badge),
            Create(lock_body),
            Create(lock_shackle),
            Write(text_unreg),
            Write(sub_text),
            run_time=2.5
        )
        
        # Emphasize badge with pulse
        self.play(
            badge.animate.scale(1.05),
            text_unreg.animate.scale(1.05),
            run_time=1.5
        )
        self.play(
            badge.animate.scale(0.95),
            text_unreg.animate.scale(0.95),
            run_time=1.5
        )
        self.wait(1.9)

# Configure canvas

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

    # Bottom title placement
    title = Text("IT DOESN'T HAVE A SOCIAL SECURITY NUMBER", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Footer bar & meta labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_label, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene12_15(Scene):
    def construct(self):
        setup_scene_base(self, "IDENTITY VERIFICATION")
        
        # Literal illustration: A card representing an ID / Social Security Card with a crossout / question mark
        card = RoundedRectangle(corner_radius=0.2, width=4.0, height=2.5, stroke_width=2.5, color="#FFFFFF")
        card.move_to([0, -1.0, 0])
        
        # Lines on card
        line1 = Line(LEFT * 1.5, LEFT * 0.5, color="#FFFFFF", stroke_width=2).move_to(card.get_center() + UP * 0.5)
        line2 = Line(LEFT * 1.5, RIGHT * 0.5, color="#FFFFFF", stroke_width=2).move_to(card.get_center())
        line3 = Line(LEFT * 1.5, ZERO, color="#FFFFFF", stroke_width=2).move_to(card.get_center() + DOWN * 0.5)
        
        # Big question mark / No symbol overlay
        q_mark = Text("?", font="Arial", weight=BOLD, font_size=80, color="#FFFFFF").move_to(card.get_center())
        
        self.play(Create(card), FadeIn(line1), FadeIn(line2), FadeIn(line3), run_time=3.0)
        self.play(FadeIn(q_mark, scale=1.5), run_time=3.8)
        self.wait(0.6)

class Scene12_16(Scene):
    def construct(self):
        setup_scene_base(self, "SYSTEM ABSENCE")
        
        # Literal illustration: Database server rack with an X mark over it
        server_box = RoundedRectangle(corner_radius=0.1, width=3.0, height=4.0, stroke_width=2.0, color="#FFFFFF")
        server_box.move_to([0, -1.0, 0])
        
        slot1 = Line(LEFT * 1.2, RIGHT * 1.2, color="#FFFFFF", stroke_width=2).move_to(server_box.get_top() + DOWN * 0.8)
        slot2 = Line(LEFT * 1.2, RIGHT * 1.2, color="#FFFFFF", stroke_width=2).move_to(server_box.get_top() + DOWN * 2.0)
        slot3 = Line(LEFT * 1.2, RIGHT * 1.2, color="#FFFFFF", stroke_width=2).move_to(server_box.get_top() + DOWN * 3.2)
        
        cross_1 = Line(UL * 1.8, DR * 1.8, color="#FFFFFF", stroke_width=4).move_to(server_box.get_center())
        cross_2 = Line(UR * 1.8, DL * 1.8, color="#FFFFFF", stroke_width=4).move_to(server_box.get_center())
        
        self.play(Create(server_box), FadeIn(slot1), FadeIn(slot2), FadeIn(slot3), run_time=3.0)
        self.play(Create(cross_1), Create(cross_2), run_time=3.8)
        self.wait(0.6)

class Scene12_17(Scene):
    def construct(self):
        setup_scene_base(self, "DIGITAL ENTITY")
        
        # Literal illustration: Robot head with empty number badge
        robot_head = RoundedRectangle(corner_radius=0.3, width=3.0, height=3.0, stroke_width=2.5, color="#FFFFFF")
        robot_head.move_to([0, -1.0, 0])
        
        eye_l = Circle(radius=0.3, stroke_width=2, color="#FFFFFF").move_to(robot_head.get_center() + UP * 0.5 + LEFT * 0.7)
        eye_r = Circle(radius=0.3, stroke_width=2, color="#FFFFFF").move_to(robot_head.get_center() + UP * 0.5 + RIGHT * 0.7)
        
        badge = RoundedRectangle(corner_radius=0.1, width=2.2, height=0.8, stroke_width=2, color="#FFFFFF")
        badge.move_to(robot_head.get_center() + DOWN * 0.7)
        
        zero_text = Text("000-00-0000", font="Arial", weight=BOLD, font_size=18, color="#FFFFFF").move_to(badge.get_center())
        slash = Line(badge.get_corner(DL) + RIGHT*0.2, badge.get_corner(UR) + LEFT*0.2, color="#FFFFFF", stroke_width=3)
        
        self.play(Create(robot_head), Create(eye_l), Create(eye_r), run_time=2.5)
        self.play(Create(badge), Write(zero_text), run_time=2.5)
        self.play(Create(slash), run_time=1.8)
        self.wait(0.6)

class Scene12_18(Scene):
    def construct(self):
        setup_scene_base(self, "PAPERWORK VOID")
        
        # Literal illustration: Document flying with a missing stamp field
        doc = Rectangle(width=3.2, height=4.0, stroke_width=2.0, color="#FFFFFF").move_to([0, -1.0, 0])
        doc.set_fill("#FFFFFF", opacity=0.05)
        
        doc_lines = VGroup(
            Line(LEFT * 1.1, RIGHT * 1.1, color="#FFFFFF", stroke_width=2).move_to(doc.get_top() + DOWN * 0.8),
            Line(LEFT * 1.1, RIGHT * 0.5, color="#FFFFFF", stroke_width=2).move_to(doc.get_top() + DOWN * 1.4),
            Line(LEFT * 1.1, RIGHT * 0.9, color="#FFFFFF", stroke_width=2).move_to(doc.get_top() + DOWN * 2.0),
        )
        
        stamp_box = RoundedRectangle(corner_radius=0.1, width=2.4, height=1.0, stroke_width=2, color="#FFFFFF")
        stamp_box.move_to(doc.get_center() + DOWN * 1.0)
        
        void_text = Text("NO SSN", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to(stamp_box.get_center())
        
        self.play(Create(doc), FadeIn(doc_lines), run_time=2.5)
        self.play(Create(stamp_box), Write(void_text), run_time=3.0)
        self.wait(1.9)

class Scene12_19(Scene):
    def construct(self):
        setup_scene_base(self, "RECORD SYSTEM")
        
        # Literal illustration: Empty file folder
        folder = Polygon(
            [-2.0, 0.5, 0], [-0.8, 0.5, 0], [-0.4, 1.0, 0], [2.0, 1.0, 0],
            [2.0, -2.5, 0], [-2.0, -2.5, 0], stroke_width=2.5, color="#FFFFFF"
        ).move_to([0, -0.8, 0])
        
        paper = Rectangle(width=3.2, height=3.5, stroke_width=2.0, color="#FFFFFF").move_to([0, -0.7, 0])
        paper.set_fill("#FFFFFF", opacity=0.1)
        
        cross_line1 = Line(UL * 1.2, DR * 1.2, color="#FFFFFF", stroke_width=3).move_to(paper.get_center())
        cross_line2 = Line(UR * 1.2, DL * 1.2, color="#FFFFFF", stroke_width=3).move_to(paper.get_center())
        
        self.play(Create(folder), FadeIn(paper), run_time=3.0)
        self.play(Create(cross_line1), Create(cross_line2), run_time=3.8)
        self.wait(0.6)

class Scene12_20(Scene):
    def construct(self):
        setup_scene_base(self, "FINAL VERIFICATION")
        
        # Literal illustration: Large checkbook/ledger with zero identity markers
        ledger = RoundedRectangle(corner_radius=0.2, width=5.5, height=3.5, stroke_width=2.5, color="#FFFFFF")
        ledger.move_to([0, -1.0, 0])
        
        row1 = Line(LEFT * 2.3, RIGHT * 2.3, color="#FFFFFF", stroke_width=2).move_to(ledger.get_top() + DOWN * 1.0)
        row2 = Line(LEFT * 2.3, RIGHT * 2.3, color="#FFFFFF", stroke_width=2).move_to(ledger.get_top() + DOWN * 2.0)
        
        stamp_circle = Circle(radius=0.8, stroke_width=3, color="#FFFFFF").move_to(ledger.get_center() + RIGHT * 1.2 + DOWN * 0.5)
        stamp_text = Text("VOID", font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to(stamp_circle.get_center())
        
        self.play(Create(ledger), FadeIn(row1), FadeIn(row2), run_time=3.0)
        self.play(Create(stamp_circle), Write(stamp_text), run_time=3.8)
        self.wait(0.6)