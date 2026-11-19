import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Configure canvas strictly for vertical video layout

def setup_footer_and_title(self, scene_title_text):
    # Strict Bottom Title Placement at y = -2.95
    title = Text(scene_title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    self.play(FadeIn(title), run_time=0.6)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("OPERATING SYSTEM ACCESS", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    self.add(footer_line, left_text, right_text)

class Scene19_01(Scene):
    def construct(self):
        setup_footer_and_title(self, "LEVEL RUDE: SYSTEM ACCESS")
        
        # Literal figurative visual: A large server rack representing an Operating System
        server_box = RoundedRectangle(corner_radius=0.15, width=4.0, height=5.0, color="#FFFFFF", stroke_width=2.5)
        server_box.move_to([0, -1.0, 0])
        
        # Server slots / hard drives inside
        slots = VGroup()
        for i in range(4):
            slot = RoundedRectangle(corner_radius=0.08, width=3.5, height=0.9, color="#FFFFFF", stroke_width=2.0)
            slot.move_to([0, 1.0 - i * 1.2, 0])
            # Add status lights
            light1 = Circle(radius=0.06, color="#FFFFFF", fill_opacity=1).move_to([slot.get_left() + [0.3, 0, 0]])
            light2 = Circle(radius=0.06, color="#FFFFFF", fill_opacity=0.3).move_to([slot.get_left() + [0.6, 0, 0]])
            slots.add(VGroup(slot, light1, light2))
            
        server_group = VGroup(server_box, slots).scale(0.85).move_to([0, -0.6, 0])
        
        self.play(DrawBorderThenFill(server_group), run_time=3.0)
        
        # A warning symbol or barrier representing "Rude" / restricted access
        barrier_line1 = Line(LEFT * 1.5, RIGHT * 1.5, color="#FFFFFF", stroke_width=6).move_to([0, -0.6, 0])
        barrier_line2 = Line(LEFT * 1.0, RIGHT * 1.0, color="#FFFFFF", stroke_width=4).move_to([0, -1.2, 0])
        
        self.play(FadeIn(barrier_line1, shift=UP), FadeIn(barrier_line2, shift=DOWN), run_time=2.0)
        self.wait(1.8)

class Scene19_02(Scene):
    def construct(self):
        setup_footer_and_title(self, "LEVEL RUDE: SYSTEM ACCESS")
        
        # Literal figurative visual: A giant master lock and core processor chip
        chip = RoundedRectangle(corner_radius=0.2, width=3.0, height=3.0, color="#FFFFFF", stroke_width=2.5)
        chip.move_to([0, -0.6, 0])
        
        # Pins around the chip
        pins = VGroup()
        for i in range(3):
            # Top pins
            pins.add(Line(UP * 0.4, UP * 0.8, color="#FFFFFF", stroke_width=2).move_to([-0.8 + i * 0.8, 1.1, 0]))
            # Bottom pins
            pins.add(Line(DOWN * 0.4, DOWN * 0.8, color="#FFFFFF", stroke_width=2).move_to([-0.8 + i * 0.8, -2.3, 0]))
            
        # Core icon inside chip (Gear / Kernel)
        core_circle = Circle(radius=0.8, color="#FFFFFF", stroke_width=2).move_to([0, -0.6, 0])
        core_dot = Circle(radius=0.25, color="#FFFFFF", fill_opacity=1).move_to([0, -0.6, 0])
        
        chip_group = VGroup(chip, pins, core_circle, core_dot)
        
        self.play(Create(chip_group), run_time=3.5)
        
        # Key approaching the system
        key = VGroup(
            Circle(radius=0.3, color="#FFFFFF", stroke_width=2),
            Line(RIGHT * 0.3, RIGHT * 1.5, color="#FFFFFF", stroke_width=3),
            Line(RIGHT * 1.0, RIGHT * 1.0 + UP * 0.3, color="#FFFFFF", stroke_width=2),
            Line(RIGHT * 1.3, RIGHT * 1.3 + UP * 0.3, color="#FFFFFF", stroke_width=2)
        ).rotate(3.14159 / 4).move_to([-2.2, 1.2, 0])
        
        self.play(key.animate.move_to([0, -0.6, 0]), run_time=2.5)
        self.wait(1.4)

class Scene19_03(Scene):
    def construct(self):
        setup_footer_and_title(self, "LEVEL RUDE: SYSTEM ACCESS")
        
        # Literal figurative visual: A terminal/command-line prompt box breaking barriers
        term_box = RoundedRectangle(corner_radius=0.15, width=5.5, height=3.5, color="#FFFFFF", stroke_width=2.5)
        term_box.move_to([0, -0.6, 0])
        
        # Prompt text inside
        prompt = Text("> root/system/access --force", font="Courier", weight=BOLD, font_size=18, color="#FFFFFF")
        prompt.move_to([-1.1, 0.5, 0])
        
        cursor = Rectangle(width=0.15, height=0.3, color="#FFFFFF", fill_opacity=1)
        cursor.next_to(prompt, RIGHT, buff=0.1)
        
        term_content = VGroup(prompt, cursor)
        
        self.play(Create(term_box), Write(term_content), run_time=4.0)
        
        # Bold warning exclamation mark bursting through
        exclamation = VGroup(
            Line(UP * 0.8, DOWN * 0.2, color="#FFFFFF", stroke_width=8),
            Circle(radius=0.12, color="#FFFFFF", fill_opacity=1).move_to([0, -0.7, 0])
        ).move_to([0, -0.8, 0])
        
        self.play(FadeIn(exclamation, scale=1.5), run_time=2.0)
        self.wait(1.4)

class Scene19_04(Scene):
    def construct(self):
        setup_footer_and_title(self, "LEVEL RUDE: SYSTEM ACCESS")
        
        # Literal figurative visual: Dual layers - User space vs Kernel space (Rude access bridging them)
        user_box = RoundedRectangle(corner_radius=0.1, width=5.0, height=1.2, color="#FFFFFF", stroke_width=2).move_to([0, 0.8, 0])
        user_text = Text("USER SPACE", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, 0.8, 0])
        
        kernel_box = RoundedRectangle(corner_radius=0.1, width=5.0, height=1.2, color="#FFFFFF", stroke_width=2).move_to([0, -1.8, 0])
        kernel_text = Text("KERNEL SPACE (RUDE ACCESS)", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, -1.8, 0])
        
        layers = VGroup(user_box, user_text, kernel_box, kernel_text)
        self.play(FadeIn(layers, shift=DOWN), run_time=3.0)
        
        # Piercing heavy-duty arrow going straight from user to kernel
        pierce_arrow = Arrow(start=[0, 0.2, 0], end=[0, -1.2, color_or_point:=0], color="#FFFFFF", stroke_width=4, buff=0)
        pierce_arrow.set_color("#FFFFFF")
        
        self.play(GrowArrow(pierce_arrow), run_time=2.5)
        self.wait(1.9)

class Scene19_05(Scene):
    def construct(self):
        setup_footer_and_title(self, "LEVEL RUDE: SYSTEM ACCESS")
        
        # Literal figurative visual: An open vault door representing raw system core access
        vault_frame = Circle(radius=2.2, color="#FFFFFF", stroke_width=3).move_to([0, -0.6, 0])
        
        # Vault wheel handles
        handles = VGroup()
        for i in range(6):
            angle = i * (3.14159 / 3)
            h = Line(ORIGIN, [1.8 * np.cos(angle), 1.8 * np.sin(angle), 0], color="#FFFFFF", stroke_width=2.5)
            handles.add(h)
            
        center_hub = Circle(radius=0.5, color="#FFFFFF", fill_opacity=0.2, stroke_width=2.5).move_to([0, -0.6, 0])
        
        vault_group = VGroup(vault_frame, handles, center_hub).move_to([0, -0.6, 0])
        
        self.play(Create(vault_group), run_time=4.0)
        
        # Rotating/unlocking action represented by glowing spark lines radiating outward
        sparks = VGroup()
        for i in range(8):
            ang = i * (3.14159 / 4)
            s = Line([2.3 * np.cos(ang), 2.3 * np.sin(ang) - 0.6, 0], [2.8 * np.cos(ang), 2.8 * np.sin(ang) - 0.6, 0], color="#FFFFFF", stroke_width=2)
            sparks.add(s)
            
        self.play(FadeIn(sparks, scale=1.2), run_time=2.0)
        self.wait(1.4)

class Scene19_06(Scene):
    def construct(self):
        setup_footer_and_title(self, "LEVEL RUDE: SYSTEM ACCESS")
        
        # Literal figurative visual: CPU core with high-voltage warning bolts
        cpu = RoundedRectangle(corner_radius=0.2, width=3.5, height=3.5, color="#FFFFFF", stroke_width=3).move_to([0, -0.6, 0])
        
        # Inner circuit lines
        c1 = Line([-1.0, 0.5, 0], [1.0, 0.5, 0], color="#FFFFFF", stroke_width=2)
        c2 = Line([-1.0, -0.5, 0], [1.0, -0.5, 0], color="#FFFFFF", stroke_width=2)
        c3 = Line([0, 1.2, 0], [0, -2.4, 0], color="#FFFFFF", stroke_width=2)
        
        circuits = VGroup(c1, c2, c3, cpu)
        self.play(Create(circuits), run_time=3.0)
        
        # Lightning bolt across the OS core
        bolt = Polygon(
            [0, 1.5, 0],
            [-0.8, -0.1, 0],
            [0.3, -0.1, 0],
            [-0.3, -2.1, 0],
            [1.0, 0.2, 0],
            [-0.1, 0.2, 0],
            color="#FFFFFF",
            fill_opacity=0.8,
            stroke_width=2
        ).move_to([0, -0.6, 0])
        
        self.play(FadeIn(bolt, scale=1.3), run_time=2.5)
        self.wait(1.9)

class Scene19_07(Scene):
    def construct(self):
        setup_footer_and_title(self, "LEVEL RUDE: SYSTEM ACCESS")
        
        # Literal figurative visual: Complete OS architecture breakdown with root access granted
        # Top layer: Apps
        box_app = RoundedRectangle(corner_radius=0.1, width=4.0, height=0.9, color="#FFFFFF", stroke_width=2).move_to([0, 1.0, 0])
        t_app = Text("APPLICATIONS", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, 1.0, 0])
        
        # Middle layer: OS Kernel
        box_kernel = RoundedRectangle(corner_radius=0.1, width=4.0, height=0.9, color="#FFFFFF", stroke_width=2).move_to([0, -0.3, 0])
        t_kernel = Text("OS KERNEL", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, -0.3, 0])
        
        # Bottom layer: Hardware / Raw Metal
        box_hw = RoundedRectangle(corner_radius=0.1, width=4.0, height=0.9, color="#FFFFFF", stroke_width=2).move_to([0, -1.6, 0])
        t_hw = Text("HARDWARE (ROOT)", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, -1.6, 0])
        
        architecture = VGroup(box_app, t_app, box_kernel, t_kernel, box_hw, t_hw)
        self.play(FadeIn(architecture, shift=UP), run_time=3.5)
        
        # Direct override bypass arrow looping from apps straight to hardware
        bypass_arrow = CurvedArrow(start_point=[-2.2, 1.0, 0], end_point=[-2.2, -1.6, 0], angle=-2.0, color="#FFFFFF", stroke_width=3)
        bypass_label = Text("RUDE", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").next_to(bypass_arrow, LEFT, buff=0.1)
        
        bypass_group = VGroup(bypass_arrow, bypass_label)
        self.play(Create(bypass_group), run_time=2.5)
        self.wait(1.4)

# Configuration per strict instructions

def setup_footer(scene):
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("OS ROOT ACCESS", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

def setup_title(scene, text_str):
    title = Text(text_str, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)


class Scene19_08(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "LEVEL RUDE ACCESS: KERNEL GATEWAY")
        
        # Literal Operating System Core (Central Box) & Rude Access (Break-in wedge/bolt)
        os_box = RoundedRectangle(corner_radius=0.2, width=3.0, height=2.0, color="#FFFFFF", stroke_width=2.5)
        os_box.move_to([0, -1.0, 0])
        os_text = Text("OPERATING SYSTEM", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(os_box.get_center())
        
        # Giant warning lightning bolt / "Rude" breaker entering from top
        bolt = Polygon([0, 1.8, 0], [-0.5, 0.4, 0], [0.2, 0.4, 0], [-0.3, -0.5, 0], [0.6, 0.4, 0], [0, 0.4, 0], color="#FFFFFF", stroke_width=2.5)
        bolt.set_fill("#FFFFFF", opacity=0.3)
        bolt.scale(0.9).move_to([0, 0.8, 0])
        
        self.play(Create(os_box), FadeIn(os_text), run_time=2.0)
        self.play(GrowFromEdge(bolt, UP), run_time=2.5)
        self.wait(2.3)


class Scene19_09(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "HARDWARE BYPASS MECHANISM")
        
        # Server rack literal boxes
        rack = VGroup()
        for i in range(3):
            box = RoundedRectangle(corner_radius=0.1, width=4.0, height=0.7, color="#FFFFFF", stroke_width=2.0)
            box.move_to([0, 0.6 - i * 0.9, 0])
            rack.add(box)
            
        # Bypass Arrow cutting straight through
        bypass_arrow = Arrow(start=[-3.0, 1.8, 0], end=[3.0, -1.8, 0], color="#FFFFFF", stroke_width=4, buff=0.1)
        bypass_label = Text("BYPASS", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([1.5, 0.3, 0])
        
        self.play(Create(rack), run_time=2.0)
        self.play(GrowArrow(bypass_arrow), FadeIn(bypass_label), run_time=2.5)
        self.wait(2.3)


class Scene19_10(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "ROOT PRIVILEGE ESCALATION")
        
        # Staircase of privileges going UP
        stairs = VGroup()
        for i in range(4):
            step = Rectangle(width=1.2 + i*0.4, height=0.3, color="#FFFFFF", stroke_width=2.0)
            step.move_to([-1.5 + i*0.8, -1.8 + i*0.7, 0])
            stairs.add(step)
            
        # Heavy boots / Rude stomp at the top
        top_platform = stairs[-1]
        rude_spike = Triangle(color="#FFFFFF", stroke_width=2.5).scale(0.5).rotate(PI).next_to(top_platform, UP, buff=0.1)
        
        self.play(Create(stairs), run_time=3.0)
        self.play(GrowFromCenter(rude_spike), run_time=2.0)
        self.wait(2.4)


class Scene19_11(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "MEMORY SEGFAULT BREACH")
        
        # Memory blocks (grid)
        grid = VGroup()
        for x in range(-1, 2):
            for y in range(-1, 2):
                cell = Square(side_length=0.9, color="#FFFFFF", stroke_width=1.5)
                cell.move_to([x * 1.0, y * 1.0 - 0.5, 0])
                grid.add(cell)
                
        # Sledgehammer / Crash symbol across
        line1 = Line([-1.5, 0.5, 0], [1.5, -1.5, 0], color="#FFFFFF", stroke_width=5)
        line2 = Line([-1.5, -1.5, 0], [1.5, 0.5, 0], color="#FFFFFF", stroke_width=5)
        crash_x = VGroup(line1, line2)
        
        self.play(Create(grid), run_time=2.5)
        self.play(FadeIn(crash_x, scale=1.5), run_time=2.5)
        self.wait(2.4)


class Scene19_12(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "UNRESTRICTED SYSTEM CONTROL")
        
        # Central steering wheel / Control interface
        wheel = Circle(radius=1.5, color="#FFFFFF", stroke_width=3.0).move_to([0, -0.5, 0])
        center_hub = Circle(radius=0.4, color="#FFFFFF", stroke_width=2.0).move_to([0, -0.5, 0])
        spokes = VGroup(
            Line([0, -0.5, 0], [0, 1.0, 0], color="#FFFFFF", stroke_width=3.0),
            Line([0, -0.5, 0], [-1.3, -1.2, 0], color="#FFFFFF", stroke_width=3.0),
            Line([0, -0.5, 0], [1.3, -1.2, 0], color="#FFFFFF", stroke_width=3.0)
        )
        
        control_group = VGroup(wheel, center_hub, spokes)
        
        # Rude lock broken open
        lock_body = Rectangle(width=1.0, height=0.8, color="#FFFFFF", stroke_width=2.0).move_to([0, 1.8, 0])
        lock_shackle = Arc(radius=0.5, start_angle=0, angle=PI, color="#FFFFFF", stroke_width=2.0).move_to([0, 2.3, 0])
        lock_shackle.rotate(PI/2) # Break open style
        
        self.play(Create(control_group), run_time=3.0)
        self.play(Create(lock_body), Create(lock_shackle), run_time=2.0)
        self.wait(2.4)


class Scene19_13(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "RAW KERNEL INSTRUCTION EXECUTION")
        
        # Literal processor chip with pins
        chip = RoundedRectangle(corner_radius=0.2, width=3.0, height=3.0, color="#FFFFFF", stroke_width=2.5).move_to([0, -0.5, 0])
        chip_text = Text("CPU KERNEL", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(chip.get_center())
        
        # Direct raw data streams piercing in
        streams = VGroup()
        for i in range(4):
            arrow = Arrow(start=[-3.8 + i*2.5, 1.8, 0], end=[-1.5 + i*1.0, 0.5, 0], color="#FFFFFF", stroke_width=2.0, buff=0.1)
            streams.add(arrow)
            
        self.play(Create(chip), FadeIn(chip_text), run_time=2.5)
        self.play(GrowArrow(streams[0]), GrowArrow(streams[1]), GrowArrow(streams[2]), GrowArrow(streams[3]), run_time=2.5)
        self.wait(2.4)


class Scene19_14(Scene):
    def construct(self):
        setup_footer(self)
        setup_title(self, "DEEP SYSTEM DOMINANCE")
        
        # Giant pyramid / hierarchy base
        base_poly = Polygon([-2.5, -2.0, 0], [2.5, -2.0, 0], [0, 1.5, 0], color="#FFFFFF", stroke_width=3.0)
        base_poly.set_fill("#FFFFFF", opacity=0.15)
        
        # Apex Rude Flag
        flag_pole = Line([0, 1.5, 0], [0, 2.2, 0], color="#FFFFFF", stroke_width=3.0)
        flag = Polygon([0, 2.2, 0], [1.0, 1.9, 0], [0, 1.6, 0], color="#FFFFFF", stroke_width=2.0)
        flag.set_fill("#FFFFFF", opacity=0.8)
        
        dominance_text = Text("ROOT LEVEL", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, -0.5, 0])
        
        self.play(Create(base_poly), run_time=2.5)
        self.play(Create(flag_pole), FadeIn(flag, shift=RIGHT), FadeIn(dominance_text), run_time=2.5)
        self.wait(2.4)

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

    # Title at bottom
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Footer and Meta labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text(category_text, font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene19_15(Scene):
    def construct(self):
        setup_scene_base(self, "LEVEL RUDE: OPERATING SYSTEM ACCESS", "SYSTEM ARCHITECTURE")
        
        # Literal figurative visual: Central OS core block with a bold "ROOT/RUDE" barrier break
        # Safe area: x in [-3.2, 3.2], y in [-2.5, 0.4]
        
        os_box = RoundedRectangle(corner_radius=0.2, width=4.0, height=2.2, color="#FFFFFF", stroke_width=3)
        os_box.move_to([0, -1.0, 0])
        
        os_label = Text("OS KERNEL", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([0, -0.2, 0])
        
        # Inner server lines representing OS layers
        line1 = Line(LEFT * 1.5, RIGHT * 1.5, color="#FFFFFF", stroke_width=1.5).move_to([0, -0.8, 0])
        line2 = Line(LEFT * 1.5, RIGHT * 1.5, color="#FFFFFF", stroke_width=1.5).move_to([0, -1.4, 0])
        
        # A giant breaking key / override arrow entering the OS
        override_arrow = Arrow(start=[-3.0, 1.2, 0], end=[-0.5, -0.5, 0], color="#FFFFFF", stroke_width=6, buff=0)
        override_text = Text("RUDE ACCESS", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([-2.2, 0.6, 0])
        
        self.play(
            Create(os_box),
            FadeIn(os_label),
            Create(line1),
            Create(line2),
            run_time=2.0
        )
        
        self.play(
            GrowArrow(override_arrow),
            FadeIn(override_text),
            run_time=2.5
        )
        
        # Flash effect on the OS box to show rude breach
        flash_rect = RoundedRectangle(corner_radius=0.2, width=4.2, height=2.4, color="#FFFFFF", stroke_width=4).move_to([0, -1.0, 0])
        flash_rect.set_opacity(0.8)
        
        self.play(FadeIn(flash_rect, run_time=0.2), FadeOut(flash_rect, run_time=1.5))
        self.wait(1.2)

class Scene19_16(Scene):
    def construct(self):
        setup_scene_base(self, "LEVEL RUDE: OPERATING SYSTEM ACCESS", "PRIVILEGE ESCALATION")
        
        # Literal figurative visual: Stack of privilege rings breaking through
        # Safe area: x in [-3.2, 3.2], y in [-2.5, 0.4]
        
        ring3 = RoundedRectangle(corner_radius=0.15, width=4.5, height=0.8, color="#FFFFFF", stroke_width=2).move_to([0, 0.0, 0])
        ring2 = RoundedRectangle(corner_radius=0.15, width=3.5, height=0.8, color="#FFFFFF", stroke_width=2).move_to([0, -0.9, 0])
        ring1 = RoundedRectangle(corner_radius=0.15, width=2.5, height=0.8, color="#FFFFFF", stroke_width=3).move_to([0, -1.8, 0])
        
        t3 = Text("USER RING", font="Arial", weight=NORMAL, font_size=12, color="#FFFFFF").move_to([0, 0.0, 0])
        t2 = Text("KERNEL RING", font="Arial", weight=NORMAL, font_size=12, color="#FFFFFF").move_to([0, -0.9, 0])
        t1 = Text("HARDWARE ROOT", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, -1.8, 0])
        
        # Rude access hammer/bolt smashing from top down
        smash_bolt = Arrow(start=[0, 2.0, 0], end=[0, -1.5, 0], color="#FFFFFF", stroke_width=8, buff=0)
        smash_text = Text("BYPASS ALL CHECKS", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, 1.3, 0])
        
        self.play(
            Create(ring3), FadeIn(t3),
            Create(ring2), FadeIn(t2),
            Create(ring1), FadeIn(t1),
            run_time=2.5
        )
        
        self.play(
            GrowArrow(smash_bolt),
            FadeIn(smash_text),
            run_time=2.5
        )
        
        self.play(
            ring1.animate.set_stroke(width=5),
            ring2.animate.set_stroke(width=5),
            run_time=1.4
        )
        self.wait(1.0)

class Scene19_17(Scene):
    def construct(self):
        setup_scene_base(self, "LEVEL RUDE: OPERATING SYSTEM ACCESS", "SYSTEM COMMAND")
        
        # Literal figurative visual: Terminal window with raw execution lines
        # Safe area: x in [-3.2, 3.2], y in [-2.5, 0.4]
        
        term_box = RoundedRectangle(corner_radius=0.2, width=6.0, height=3.0, color="#FFFFFF", stroke_width=2).move_to([0, -0.8, 0])
        term_bar = Line(LEFT * 3.0, RIGHT * 3.0, color="#FFFFFF", stroke_width=2).move_to([0, 0.3, 0])
        
        dot_l = Circle(radius=0.06, color="#FFFFFF", fill_opacity=1).move_to([-2.7, 0.55, 0])
        dot_m = Circle(radius=0.06, color="#FFFFFF", fill_opacity=1).move_to([-2.5, 0.55, 0])
        
        cmd1 = Text("$ sudo rm -rf /kernel/core", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").align_to(term_box, LEFT).shift(LEFT * 2.6, UP * 0.0)
        cmd2 = Text("> WARNING: LEVEL RUDE ENGAGED", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").align_to(term_box, LEFT).shift(LEFT * 2.6, DOWN * 0.6)
        cmd3 = Text("> DIRECT MEMORY MAP OVERWRITTEN", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").align_to(term_box, LEFT).shift(LEFT * 2.6, DOWN * 1.2)
        
        self.play(
            Create(term_box),
            Create(term_bar),
            FadeIn(dot_l), FadeIn(dot_m),
            run_time=1.5
        )
        
        self.play(FadeIn(cmd1, shift=RIGHT*0.2), run_time=1.5)
        self.play(FadeIn(cmd2, shift=RIGHT*0.2), run_time=1.5)
        self.play(FadeIn(cmd3, shift=RIGHT*0.2), run_time=1.5)
        self.wait(1.4)

class Scene19_18(Scene):
    def construct(self):
        setup_scene_base(self, "LEVEL RUDE: OPERATING SYSTEM ACCESS", "FINAL EXECUTION")
        
        # Literal figurative visual: A master control switch flipped entirely to "RUDE / UNRESTRICTED"
        # Safe area: x in [-3.2, 3.2], y in [-2.5, 0.4]
        
        switch_base = RoundedRectangle(corner_radius=0.3, width=3.0, height=1.5, color="#FFFFFF", stroke_width=3).move_to([0, -0.8, 0])
        
        # Switch lever pointing aggressively to the right (ON / RUDE)
        lever_line = Line([0, -0.8, 0], [1.5, 0.6, 0], color="#FFFFFF", stroke_width=6)
        lever_knob = Circle(radius=0.25, color="#FFFFFF", fill_opacity=1).move_to([1.5, 0.6, 0])
        
        label_safe = Text("SAFE", font="Arial", weight=NORMAL, font_size=12, color="#FFFFFF").move_to([-1.5, -1.8, 0])
        label_rude = Text("LEVEL RUDE", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to([1.5, -1.8, 0])
        
        top_warning = Text("UNRESTRICTED OS CONTROL ACTIVE", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to([0, 1.0, 0])
        
        self.play(
            Create(switch_base),
            Create(lever_line),
            FadeIn(lever_knob),
            FadeIn(label_safe),
            FadeIn(label_rude),
            run_time=2.0
        )
        
        self.play(FadeIn(top_warning, shift=UP*0.2), run_time=1.5)
        
        # Pulse effect on lever knob
        for _ in range(3):
            self.play(lever_knob.animate.set_fill(opacity=0.3), run_time=0.4)
            self.play(lever_knob.animate.set_fill(opacity=1.0), run_time=0.4)
            
        self.wait(1.4)