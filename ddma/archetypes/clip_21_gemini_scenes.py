import numpy as np
from numpy import cos, sin, pi
from manim_compat import *


# (Using universal get_footer_and_title from manim_compat)



# Configure canvas strictly

def setup_footer():
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("COMMUNITY INTELLIGENCE", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    return VGroup(footer_line, left_text, right_text)

def setup_title(text_str):
    return Text(text_str, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])

class Scene21_01(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("THEY INTRODUCED THE CONCEPT")
        self.play(FadeIn(title), run_time=0.6)
        
        # Literal illustration: A central shining brain node connected to individual nodes (Community Intelligence)
        central_node = Circle(radius=0.6, color="#FFFFFF", stroke_width=2.5).move_to([0, -1.0, 0])
        core_dot = Dot(point=[0, -1.0, 0], color="#FFFFFF")
        
        satellites = VGroup()
        coords = [
            [-2.2, 0.2, 0], [2.2, 0.2, 0],
            [-1.4, 1.2, 0], [1.4, 1.2, 0],
            [0, 1.8, 0]
        ]
        
        connections = VGroup()
        for pt in coords:
            sat = Circle(radius=0.25, color="#FFFFFF", stroke_width=2).move_to(pt)
            satellites.add(sat)
            conn = Line(central_node.get_center(), pt, color="#FFFFFF", stroke_width=1.5).set_opacity(0.5)
            connections.add(conn)
            
        network_group = VGroup(connections, central_node, core_dot, satellites)
        
        self.play(
            FadeIn(central_node, scale=0.5),
            FadeIn(core_dot),
            run_time=1.0
        )
        self.play(
            Create(connections),
            FadeIn(satellites, lag_ratio=0.2),
            run_time=2.0
        )
        
        # Pulsing effect to show intelligence flow
        self.play(
            central_node.animate.set_stroke(width=5).set_opacity(0.8),
            run_time=1.0
        )
        self.play(
            central_node.animate.set_stroke(width=2.5).set_opacity(1.0),
            run_time=1.0
        )
        
        self.wait(2.0)

class Scene21_02(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("INDIVIDUAL MINDS COMBINING")
        self.play(FadeIn(title), run_time=0.6)
        
        # Literal illustration: Multiple distinct user icons / silhouettes merging into one big box (Community)
        left_box = RoundedRectangle(corner_radius=0.2, width=1.2, height=1.6, color="#FFFFFF", stroke_width=2).move_to([-2.2, -0.8, 0])
        mid_box = RoundedRectangle(corner_radius=0.2, width=1.2, height=1.6, color="#FFFFFF", stroke_width=2).move_to([0, -0.8, 0])
        right_box = RoundedRectangle(corner_radius=0.2, width=1.2, height=1.6, color="#FFFFFF", stroke_width=2).move_to([2.2, -0.8, 0])
        
        arr_left = Arrow(start=[-1.4, -0.8, 0], end=[-0.8, -0.8, 0], color="#FFFFFF", stroke_width=2, tip_length=0.15)
        arr_right = Arrow(start=[1.4, -0.8, 0], end=[0.8, -0.8, 0], color="#FFFFFF", stroke_width=2, tip_length=0.15)
        
        big_hub = RoundedRectangle(corner_radius=0.3, width=3.0, height=1.2, color="#FFFFFF", stroke_width=3).move_to([0, 1.2, 0])
        hub_arrow = Arrow(start=[0, -0.0, 0], end=[0, 0.5, 0], color="#FFFFFF", stroke_width=2.5, tip_length=0.2)
        
        self.play(
            Create(left_box), Create(mid_box), Create(right_box),
            run_time=1.5
        )
        self.play(
            GrowArrow(arr_left), GrowArrow(arr_right),
            run_time=1.0
        )
        self.play(
            Create(big_hub),
            GrowArrow(hub_arrow),
            run_time=1.5
        )
        
        self.wait(3.0)

class Scene21_03(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("COMMUNITY INTELLIGENCE FLOW")
        self.play(FadeIn(title), run_time=0.6)
        
        # Literal illustration: Data stream flowing across distributed servers
        server_1 = Rectangle(width=1.4, height=2.2, color="#FFFFFF", stroke_width=2).move_to([-2.2, -0.5, 0])
        server_2 = Rectangle(width=1.4, height=2.2, color="#FFFFFF", stroke_width=2).move_to([0, -0.5, 0])
        server_3 = Rectangle(width=1.4, height=2.2, color="#FFFFFF", stroke_width=2).move_to([2.2, -0.5, 0])
        
        # Server details (blinking lights)
        lights = VGroup()
        for s in [server_1, server_2, server_3]:
            for dy in [0.6, 0.0, -0.6]:
                dot = Dot(point=s.get_center() + UP * dy, color="#FFFFFF", radius=0.06)
                lights.add(dot)
                
        line_connect = Line([-1.5, -0.5, 0], [1.5, -0.5, 0], color="#FFFFFF", stroke_width=2)
        
        self.play(
            Create(server_1), Create(server_2), Create(server_3),
            run_time=1.5
        )
        self.play(
            FadeIn(lights, lag_ratio=0.1),
            Create(line_connect),
            run_time=1.5
        )
        
        # Signal pulse
        pulse = Circle(radius=0.3, color="#FFFFFF", stroke_width=2).move_to(server_1.get_center())
        self.play(FadeIn(pulse), run_time=0.5)
        self.play(pulse.animate.move_to(server_3.get_center()), run_time=1.5)
        self.play(FadeOut(pulse), run_time=0.5)
        
        self.wait(1.0)

class Scene21_04(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("SHARED KNOWLEDGE REPOSITORY")
        self.play(FadeIn(title), run_time=0.6)
        
        # Literal illustration: A vast database cylinder stack
        cylinders = VGroup()
        for i in range(4):
            y_pos = 1.0 - (i * 0.7)
            c = Ellipse(width=3.5, height=0.8, color="#FFFFFF", stroke_width=2).move_to([0, y_pos, 0])
            cylinders.add(c)
            
        # Connective vertical lines for the cylinder sides
        left_side = Line([-1.75, 1.0, 0], [-1.75, -1.1, 0], color="#FFFFFF", stroke_width=2)
        right_side = Line([1.75, 1.0, 0], [1.75, -1.1, 0], color="#FFFFFF", stroke_width=2)
        bottom_arc = Arc(radius=1.75, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=2).move_to([0, -1.1, 0])
        bottom_arc.stretch_to_fit_width(3.5)
        bottom_arc.stretch_to_fit_height(0.8)
        
        db_group = VGroup(cylinders, left_side, right_side, bottom_arc)
        
        upload_arrow = Arrow(start=[0, 2.2, 0], end=[0, 1.5, 0], color="#FFFFFF", stroke_width=3, tip_length=0.2)
        
        self.play(
            GrowArrow(upload_arrow),
            Create(db_group, lag_ratio=0.2),
            run_time=2.5
        )
        
        # Internal glowing wave inside database
        glow_line = Line([-1.2, 0, 0], [1.2, 0, 0], color="#FFFFFF", stroke_width=3).move_to([0, 0, 0])
        self.play(FadeIn(glow_line), run_time=0.8)
        self.play(glow_line.animate.shift(DOWN * 0.7), run_time=1.0)
        self.play(FadeOut(glow_line), run_time=0.5)
        
        self.wait(2.2)

class Scene21_05(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("DISTRIBUTED PROBLEM SOLVING")
        self.play(FadeIn(title), run_time=0.6)
        
        # Literal illustration: A complex maze/puzzle piece being solved collectively
        outer_box = RoundedRectangle(corner_radius=0.3, width=5.0, height=3.0, color="#FFFFFF", stroke_width=2).move_to([0, -0.3, 0])
        
        # Internal paths (Maze lines)
        path1 = Line([-2.0, 0.8, 0], [-0.5, 0.8, 0], color="#FFFFFF", stroke_width=2)
        path2 = Line([-0.5, 0.8, 0], [-0.5, -0.2, 0], color="#FFFFFF", stroke_width=2)
        path3 = Line([-0.5, -0.2, 0], [1.5, -0.2, 0], color="#FFFFFF", stroke_width=2)
        path4 = Line([1.5, -0.2, 0], [1.5, 1.0, 0], color="#FFFFFF", stroke_width=2)
        path5 = Line([0.5, -1.0, 0], [0.5, -0.2, 0], color="#FFFFFF", stroke_width=2)
        
        maze_paths = VGroup(path1, path2, path3, path4, path5)
        
        # Target solved marker at the end
        target_dot = Dot(point=[1.5, 1.0, 0], color="#FFFFFF", radius=0.12)
        start_dot = Dot(point=[-2.0, 0.8, 0], color="#FFFFFF", radius=0.12)
        
        self.play(
            Create(outer_box),
            Create(maze_paths, lag_ratio=0.1),
            FadeIn(target_dot), FadeIn(start_dot),
            run_time=3.0
        )
        
        # Traveling tracer dot
        tracer = Dot(point=[-2.0, 0.8, 0], color="#FFFFFF", radius=0.15)
        self.play(FadeIn(tracer), run_time=0.3)
        
        self.play(tracer.animate.move_to([-0.5, 0.8, 0]), run_time=0.8)
        self.play(tracer.animate.move_to([-0.5, -0.2, 0]), run_time=0.8)
        self.play(tracer.animate.move_to([1.5, -0.2, 0]), run_time=1.0)
        self.play(tracer.animate.move_to([1.5, 1.0, 0]), run_time=0.8)
        
        self.wait(0.5)

class Scene21_06(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("COLLECTIVE FEEDBACK LOOP")
        self.play(FadeIn(title), run_time=0.6)
        
        # Literal illustration: Circular feedback loop arrows
        circle_path = Arc(radius=1.4, start_angle=0, angle=TAU, color="#FFFFFF", stroke_width=2).move_to([0, -0.3, 0])
        
        arrow1 = Arrow(start=[0, 1.1, 0], end=[0.4, 1.4, 0], color="#FFFFFF", stroke_width=2, tip_length=0.2).move_to([1.4, -0.3, 0])
        arrow2 = Arrow(start=[0, -1.1, 0], end=[-0.4, -1.4, 0], color="#FFFFFF", stroke_width=2, tip_length=0.2).move_to([-1.4, -0.3, 0])
        
        node_top = Circle(radius=0.3, color="#FFFFFF", stroke_width=2).move_to([0, 1.1, 0])
        node_bottom = Circle(radius=0.3, color="#FFFFFF", stroke_width=2).move_to([0, -1.7, 0])
        node_right = Circle(radius=0.3, color="#FFFFFF", stroke_width=2).move_to([1.4, -0.3, 0])
        node_left = Circle(radius=0.3, color="#FFFFFF", stroke_width=2).move_to([-1.4, -0.3, 0])
        
        nodes_group = VGroup(node_top, node_bottom, node_right, node_left, circle_path)
        
        self.play(
            Create(circle_path),
            FadeIn(nodes_group, lag_ratio=0.15),
            run_time=2.0
        )
        
        # Rotate loop animation
        self.play(
            nodes_group.animate.rotate(PI),
            run_time=2.5
        )
        self.play(
            nodes_group.animate.rotate(PI),
            run_time=2.5
        )

class Scene21_07(Scene):
    def construct(self):
        footer = setup_footer()
        self.add(footer)
        
        title = setup_title("THE NEW PARADIGM OF INTELLIGENCE")
        self.play(FadeIn(title), run_time=0.6)
        
        # Literal illustration: Expanding horizon / shining sun burst made of vector lines
        center_core = Circle(radius=0.5, color="#FFFFFF", stroke_width=3).move_to([0, -0.2, 0])
        inner_fill = Dot(point=[0, -0.2, 0], color="#FFFFFF", radius=0.2)
        
        rays = VGroup()
        num_rays = 12
        for i in range(num_rays):
            angle = i * (TAU / num_rays)
            start_pt = [0 + 0.7 * np.cos(angle), -0.2 + 0.7 * np.sin(angle), 0]
            end_pt = [0 + 1.8 * np.cos(angle), -0.2 + 1.8 * np.sin(angle), 0]
            ray = Line(start_pt, end_pt, color="#FFFFFF", stroke_width=2.5)
            rays.add(ray)
            
        burst_group = VGroup(center_core, inner_fill, rays)
        
        self.play(
            FadeIn(center_core, scale=0.1),
            FadeIn(inner_fill),
            run_time=1.0
        )
        self.play(
            Create(rays, lag_ratio=0.05),
            run_time=2.5
        )
        
        # Scale up burst for impactful climax
        self.play(
            burst_group.animate.scale(1.2),
            run_time=1.5
        )
        self.play(
            burst_group.animate.scale(0.9),
            run_time=1.0
        )
        
        self.wait(1.0)

# Canvas Configuration

def add_base_elements(scene, scene_title_text):
    # Strict Bottom Title Placement (y = -2.95)
    title = Text(scene_title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("COMMUNITY INTELLIGENCE", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    scene.add(footer_line, left_text, right_text)

class Scene21_08(Scene):
    def construct(self):
        add_base_elements(self, "THEY INTRODUCED COMMUNITY INTELLIGENCE")
        
        # Literal illustration: A central glowing hub (community) connected to multiple nodes (intelligence units)
        center_node = Circle(radius=0.6, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.2).move_to([0, -1.0, 0])
        core_text = Text("CI", font="Arial", weight=BOLD, font_size=24, color="#FFFFFF").move_to(center_node.get_center())
        
        nodes = VGroup()
        lines = VGroup()
        
        angles = [0, PI/3, 2*PI/3, PI, 4*PI/3, 5*PI/3]
        for i, angle in enumerate(angles):
            pos = np.array([np.cos(angle) * 2.2, np.sin(angle) * 1.2 - 1.0, 0])
            node = Circle(radius=0.3, color="#FFFFFF", stroke_width=1.5).set_fill("#FFFFFF", opacity=0.1).move_to(pos)
            line = Line(center_node.get_center(), pos, color="#FFFFFF", stroke_width=1.5).set_opacity(0.6)
            nodes.add(node)
            lines.add(line)
            
        self.play(Create(lines), FadeIn(center_node), Write(core_text), run_time=2.0)
        self.play(FadeIn(nodes, shift=UP*0.1), run_time=2.0)
        
        # Pulsing effect to show intelligence flow
        self.play(center_node.animate.set_fill("#FFFFFF", opacity=0.5), run_time=1.6)
        self.play(center_node.animate.set_fill("#FFFFFF", opacity=0.2), run_time=1.4)
        self.wait(0.6)

class Scene21_09(Scene):
    def construct(self):
        add_base_elements(self, "COLLECTIVE NETWORK NODES")
        
        # Literal illustration: Grid of interconnected servers/nodes passing data
        grid = VGroup()
        for x in [-2, 0, 2]:
            for y in [-0.5, -1.8]:
                rect = RoundedRectangle(corner_radius=0.1, width=1.2, height=0.8, color="#FFFFFF", stroke_width=1.5)
                rect.set_fill("#FFFFFF", opacity=0.15)
                rect.move_to([x, y, 0])
                grid.add(rect)
                
        # Connecting lines forming a network web
        net_lines = VGroup(
            Line(grid[0].get_center(), grid[1].get_center(), color="#FFFFFF", stroke_width=1),
            Line(grid[1].get_center(), grid[2].get_center(), color="#FFFFFF", stroke_width=1),
            Line(grid[3].get_center(), grid[4].get_center(), color="#FFFFFF", stroke_width=1),
            Line(grid[4].get_center(), grid[5].get_center(), color="#FFFFFF", stroke_width=1),
            Line(grid[0].get_center(), grid[3].get_center(), color="#FFFFFF", stroke_width=1),
            Line(grid[1].get_center(), grid[4].get_center(), color="#FFFFFF", stroke_width=1),
            Line(grid[2].get_center(), grid[5].get_center(), color="#FFFFFF", stroke_width=1),
        )
        net_lines.set_opacity(0.5)
        
        self.play(Create(net_lines), run_time=2.0)
        self.play(FadeIn(grid, shift=UP*0.2), run_time=3.0)
        
        # Data pulses
        pulse = Circle(radius=0.2, color="#FFFFFF", stroke_width=2).move_to(grid[0].get_center())
        self.play(FadeIn(pulse), run_time=0.4)
        self.play(pulse.animate.move_to(grid[5].get_center()), run_time=1.2)
        self.play(FadeOut(pulse), run_time=0.4)

class Scene21_10(Scene):
    def construct(self):
        add_base_elements(self, "SYNCHRONIZED COMMUNITY PULSE")
        
        # Literal illustration: Sine waves interacting, representing shared intelligence synchronization
        axes_center = np.array([0, -1.0, 0])
        wave1 = FunctionGraph(lambda x: 0.8 * np.sin(2 * x), color="#FFFFFF", x_range=[-3.0, 3.0], stroke_width=2).move_to(axes_center + UP*0.4)
        wave2 = FunctionGraph(lambda x: 0.8 * np.sin(2 * x + 1.57), color="#FFFFFF", x_range=[-3.0, 3.0], stroke_width=1).set_opacity(0.4).move_to(axes_center + DOWN*0.4)
        
        sync_arrow = DoubleArrow(axes_center + UP*0.8, axes_center + DOWN*0.8, color="#FFFFFF", stroke_width=2, tip_length=0.15)
        
        self.play(Create(wave1), Create(wave2), run_time=2.5)
        self.play(GrowArrow(sync_arrow), run_time=2.0)
        
        # Shift waves together to show synchronization
        self.play(wave2.animate.move_to(axes_center + UP*0.4).set_opacity(1.0), run_time=2.0)
        self.wait(1.1)

class Scene21_11(Scene):
    def construct(self):
        add_base_elements(self, "SCALING COMMUNITY CAPACITY")
        
        # Literal illustration: Step-by-step ascending blocks representing growing intelligence scale
        blocks = VGroup()
        for i in range(4):
            height = 0.5 + i * 0.4
            block = Rectangle(width=1.0, height=height, color="#FFFFFF", stroke_width=2)
            block.set_fill("#FFFFFF", opacity=0.1 + i * 0.15)
            block.move_to([-2.2 + i * 1.5, -1.5 + height/2, 0])
            blocks.add(block)
            
        growth_line = Arrow(start=[-2.8, -1.8, 0], end=[2.8, 0.2, 0], color="#FFFFFF", stroke_width=2, tip_length=0.2)
        
        self.play(FadeIn(blocks, shift=UP*0.2, lag_ratio=0.3), run_time=3.5)
        self.play(GrowArrow(growth_line), run_time=3.0)
        self.wait(1.1)

class Scene21_12(Scene):
    def construct(self):
        add_base_elements(self, "DATA CONVERGENCE PIPELINES")
        
        # Literal illustration: Multiple pipes/arrows feeding into a single processing unit
        pipes = VGroup()
        for y_pos in [0.0, -1.0, -2.0]:
            pipe = Arrow(start=[-3.5, y_pos, 0], end=[-1.2, -1.0, 0], color="#FFFFFF", stroke_width=2, tip_length=0.15)
            pipes.add(pipe)
            
        central_processor = RoundedRectangle(corner_radius=0.2, width=2.0, height=1.6, color="#FFFFFF", stroke_width=2)
        central_processor.set_fill("#FFFFFF", opacity=0.25).move_to([0.5, -1.0, 0])
        
        out_pipe = Arrow(start=[1.5, -1.0, 0], end=[3.5, -1.0, 0], color="#FFFFFF", stroke_width=2, tip_length=0.15)
        
        self.play(Create(pipes, lag_ratio=0.2), run_time=2.5)
        self.play(FadeIn(central_processor, scale=0.8), run_time=2.0)
        self.play(GrowArrow(out_pipe), run_time=2.0)
        self.wait(1.1)

class Scene21_13(Scene):
    def construct(self):
        add_base_elements(self, "DISTRIBUTED BRAIN MESH")
        
        # Literal illustration: A distributed mesh of interconnected brain/node circles
        dots = VGroup()
        coords = [
            [-2.0, 0.0, 0], [-1.0, 0.8, 0], [1.0, 0.8, 0], [2.0, 0.0, 0],
            [-1.5, -1.5, 0], [0.0, -0.8, 0], [1.5, -1.5, 0]
        ]
        
        for coord in coords:
            dot = Circle(radius=0.25, color="#FFFFFF", stroke_width=2).set_fill("#FFFFFF", opacity=0.3).move_to(coord)
            dots.add(dot)
            
        mesh_lines = VGroup(
            Line(coords[0], coords[1]), Line(coords[1], coords[2]), Line(coords[2], coords[3]),
            Line(coords[0], coords[4]), Line(coords[4], coords[5]), Line(coords[5], coords[6]),
            Line(coords[3], coords[6]), Line(coords[1], coords[5]), Line(coords[2], coords[5])
        )
        mesh_lines.set_color("#FFFFFF").set_stroke_width(1.5).set_opacity(0.5)
        
        self.play(Create(mesh_lines), run_time=3.0)
        self.play(FadeIn(dots, scale=0.5, lag_ratio=0.2), run_time=3.0)
        self.wait(1.6)

class Scene21_14(Scene):
    def construct(self):
        add_base_elements(self, "COMMUNITY INTELLIGENCE MANIFESTED")
        
        # Literal illustration: Large central core with radiating output waves representing community realization
        core = Circle(radius=1.0, color="#FFFFFF", stroke_width=2.5).set_fill("#FFFFFF", opacity=0.3).move_to([0, -1.0, 0])
        
        rings = VGroup()
        for r in [1.6, 2.2, 2.8]:
            ring = Circle(radius=r, color="#FFFFFF", stroke_width=1).set_opacity(0.7 - (r*0.2)).move_to([0, -1.0, 0])
            rings.add(ring)
            
        label = Text("COMMUNITY INTELLIGENCE", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to(core.get_center())
        
        self.play(FadeIn(core, scale=0.2), Write(label), run_time=2.5)
        self.play(Create(rings, lag_ratio=0.3), run_time=3.5)
        self.play(core.animate.set_fill("#FFFFFF", opacity=0.6), run_time=1.0)
        self.wait(0.6)

# Configure canvas exactly to specifications

def setup_footer_and_title(scene, title_text):
    # Bottom Title Placement (y = -2.95)
    title = Text(title_text, font="Arial", weight=BOLD, font_size=20, color="#FFFFFF").move_to([0, -2.95, 0])
    scene.play(FadeIn(title), run_time=0.6)
    
    # Bottom Footer Bar & Meta Labels
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.4)
    left_text = Text("COMMUNITY INTELLIGENCE", font="Arial", weight=BOLD, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("DEEP DIVE PODCAST • EP. 248", font="Arial", weight=NORMAL, font_size=10, color="#FFFFFF").set_opacity(0.65).next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    
    scene.add(footer_line, left_text, right_text)

class Scene21_15(Scene):
    def construct(self):
        setup_footer_and_title(self, "THEY INTRODUCED COMMUNITY INTELLIGENCE")
        
        # Literal figurative visual: Central hub connected to multiple nodes (Community network)
        center_node = Circle(radius=0.6, color="#FFFFFF", stroke_width=2).move_to([0, -1.0, 0])
        center_text = Text("AI", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to(center_node.get_center())
        
        nodes = VGroup()
        lines = VGroup()
        
        angles = [0, PI/3, 2*PI/3, PI, 4*PI/3, 5*PI/3]
        for i, angle in enumerate(angles):
            pos = np.array([1.8 * np.cos(angle), -1.0 + 1.8 * np.sin(angle), 0])
            node = Circle(radius=0.3, color="#FFFFFF", stroke_width=2).move_to(pos)
            line = Line(center_node.get_center(), pos, color="#FFFFFF", stroke_width=1.5).set_opacity(0.6)
            nodes.add(node)
            lines.add(line)
            
        network_group = VGroup(lines, center_node, center_text, nodes)
        
        self.play(FadeIn(network_group, shift=UP*0.3), run_time=2.0)
        self.play(Rotate(network_group, angle=2*PI, about_point=[0, -1.0, 0]), run_time=4.4)
        self.wait(0.6)

class Scene21_16(Scene):
    def construct(self):
        setup_footer_and_title(self, "CONNECTING DIVERSE NODES")
        
        # Literal figurative visual: Nodes merging data streams into a central processing unit
        server_box = Rectangle(width=2.0, height=2.8, color="#FFFFFF", stroke_width=2).move_to([0, -1.0, 0])
        server_lines = VGroup(*[Line(server_box.get_left() + [0.2, y, 0], server_box.get_right() - [0.2, y, 0], color="#FFFFFF", stroke_width=1).set_opacity(0.5) for y in [-0.8, 0, 0.8]])
        
        in_arrows = VGroup(
            Arrow(start=[-3.0, 0.2, 0], end=[-1.0, 0.2, 0], color="#FFFFFF", stroke_width=2, buff=0),
            Arrow(start=[-3.0, -1.0, 0], end=[-1.0, -1.0, 0], color="#FFFFFF", stroke_width=2, buff=0),
            Arrow(start=[-3.0, -2.2, 0], end=[-1.0, -2.2, 0], color="#FFFFFF", stroke_width=2, buff=0),
        )
        
        out_arrow = Arrow(start=[1.0, -1.0, 0], end=[3.0, -1.0, 0], color="#FFFFFF", stroke_width=2, buff=0)
        
        group = VGroup(server_box, server_lines, in_arrows, out_arrow)
        
        self.play(Create(group), run_time=2.5)
        self.play(Indicate(server_box, color="#FFFFFF", scale_factor=1.05), run_time=4.5)
        self.wait(0.6)

class Scene21_17(Scene):
    def construct(self):
        setup_footer_and_title(self, "SHARED KNOWLEDGE POOL")
        
        # Literal figurative visual: A large container (pool) with rising liquid level and floating data blocks
        pool = RoundedRectangle(corner_radius=0.2, width=4.0, height=2.2, color="#FFFFFF", stroke_width=2).move_to([0, -1.2, 0])
        liquid = Rectangle(width=3.8, height=0.1, color="#FFFFFF", fill_opacity=0.4, stroke_width=0).align_to(pool, DOWN).shift(UP*0.1)
        
        blocks = VGroup(
            Square(side_length=0.4, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.2).move_to([-1.0, -1.8, 0]),
            Square(side_length=0.4, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.2).move_to([0.0, -1.8, 0]),
            Square(side_length=0.4, color="#FFFFFF", stroke_width=1.5, fill_opacity=0.2).move_to([1.0, -1.8, 0]),
        )
        
        self.play(Create(pool), FadeIn(blocks), run_time=2.0)
        self.play(
            liquid.animate.stretch_to_fit_height(1.6, about_edge=DOWN),
            blocks[0].animate.shift(UP*1.0),
            blocks[1].animate.shift(UP*1.2),
            blocks[2].animate.shift(UP*0.8),
            run_time=4.5
        )
        self.wait(0.1)

class Scene21_18(Scene):
    def construct(self):
        setup_footer_and_title(self, "DISTRIBUTED PROBLEM SOLVING")
        
        # Literal figurative visual: Puzzle pieces coming together from all directions to form a complete square
        center = np.array([0, -1.0, 0])
        p1 = Square(side_length=1.0, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to(center + [-1.5, 1.5, 0])
        p2 = Square(side_length=1.0, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to(center + [1.5, 1.5, 0])
        p3 = Square(side_length=1.0, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to(center + [-1.5, -1.5, 0])
        p4 = Square(side_length=1.0, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to(center + [1.5, -1.5, 0])
        
        puzzle = VGroup(p1, p2, p3, p4)
        
        self.play(FadeIn(puzzle, shift=IN), run_time=2.0)
        self.play(
            p1.animate.move_to(center + [-0.5, 0.5, 0]),
            p2.animate.move_to(center + [0.5, 0.5, 0]),
            p3.animate.move_to(center + [-0.5, -0.5, 0]),
            p4.animate.move_to(center + [0.5, -0.5, 0]),
            run_time=4.5
        )
        self.wait(0.6)

class Scene21_19(Scene):
    def construct(self):
        setup_footer_and_title(self, "COLLECTIVE FEEDBACK LOOPS")
        
        # Literal figurative visual: Circular arrows chasing each other with a central core
        core = Circle(radius=0.5, color="#FFFFFF", stroke_width=2, fill_opacity=0.5).move_to([0, -1.0, 0])
        
        arc1 = Arc(radius=1.5, start_angle=0, angle=PI, color="#FFFFFF", stroke_width=3).move_to([0, -1.0, 0])
        arc2 = Arc(radius=1.5, start_angle=PI, angle=PI, color="#FFFFFF", stroke_width=3).move_to([0, -1.0, 0])
        
        arrow1 = Arrow(start=[1.5, -1.0, 0], end=[1.4, -0.8, 0], color="#FFFFFF", stroke_width=3, buff=0)
        arrow2 = Arrow(start=[-1.5, -1.0, 0], end=[-1.4, -1.2, 0], color="#FFFFFF", stroke_width=3, buff=0)
        
        loop_group = VGroup(core, arc1, arc2, arrow1, arrow2)
        
        self.play(Create(loop_group), run_time=2.5)
        self.play(Rotate(loop_group, angle=-2*PI, about_point=[0, -1.0, 0]), run_time=4.5)
        self.wait(0.6)

class Scene21_20(Scene):
    def construct(self):
        setup_footer_and_title(self, "EMERGENT INTELLIGENCE DYNAMICS")
        
        # Literal figurative visual: Multiple small ascending spark lines merging into one massive vertical beam
        sparks = VGroup()
        for x in [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5]:
            spark = Line(start=[x, -2.3, 0], end=[x, -1.8, 0], color="#FFFFFF", stroke_width=2)
            sparks.add(spark)
            
        beam = Rectangle(width=0.1, height=0.1, color="#FFFFFF", fill_opacity=1.0).move_to([0, -1.0, 0])
        
        self.play(FadeIn(sparks), run_time=2.0)
        self.play(
            sparks.animate.shift(UP*1.0).set_opacity(0.1),
            beam.animate.stretch_to_fit_height(3.0, about_edge=DOWN).stretch_to_fit_width(2.0, about_point=[0,-1,0]),
            run_time=4.5
        )
        self.wait(0.1)

class Scene21_21(Scene):
    def construct(self):
        setup_footer_and_title(self, "THE ECOSYSTEM OF MINDS")
        
        # Literal figurative visual: A robust interconnected grid of nodes symbolizing a thriving ecosystem
        grid = VGroup()
        for x in [-2, 0, 2]:
            for y in [-2, -1, 0]:
                node = Circle(radius=0.25, color="#FFFFFF", stroke_width=2, fill_opacity=0.3).move_to([x, y, 0])
                grid.add(node)
                
        connections = VGroup(
            Line([-2, -2, 0], [0, -2, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            Line([0, -2, 0], [2, -2, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            Line([-2, -1, 0], [0, -1, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            Line([0, -1, 0], [2, -1, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            Line([-2, 0, 0], [0, 0, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            Line([0, 0, 0], [2, 0, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            
            Line([-2, -2, 0], [-2, -1, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            Line([-2, -1, 0], [-2, 0, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            Line([0, -2, 0], [0, -1, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            Line([0, -1, 0], [0, 0, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            Line([2, -2, 0], [2, -1, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
            Line([2, -1, 0], [2, 0, 0], color="#FFFFFF", stroke_width=1.5).set_opacity(0.5),
        )
        
        ecosystem = VGroup(connections, grid).move_to([0, -1.0, 0])
        
        self.play(Create(connections), FadeIn(grid, scale=0.5), run_time=3.0)
        self.play(Indicate(ecosystem, color="#FFFFFF", scale_factor=1.05), run_time=4.0)
        self.wait(0.6)