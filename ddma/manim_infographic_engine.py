"""
manim_infographic_engine.py - Elegant Manim Pedagogy Engine for DDMA Short Clips
Renders 1080x1080 pure monochrome white-on-black vector animations based on Richard Feynman
physical intuitions and Tristan Needham geometric transformations.
Enforces the 15-second pacing rule, pure shining white vector aesthetics, zero color clutter,
and seamless relay handoff transitions on a pure glossy black (#000000) canvas.
"""

import os
import sys
import json
import subprocess
import tempfile
import re
from typing import List, Dict, Any, Optional

# Manim Configuration for Native 740x740 / 1080x1080 Pure Glossy Black Viewport
MANIM_HEADER = """
from manim import *

CENTER = ORIGIN

config.pixel_width = 740
config.pixel_height = 740
config.frame_width = 8.0
config.frame_height = 8.0
config.background_color = "#000000"
config.frame_rate = 30

class PedagogicalBaseScene(Scene):
    archetype_label = ""
    credits_label = "DEEP DIVE PODCAST"

    def setup(self):
        super().setup()
        self.camera.background_color = "#000000"
        
        # Bottom footer bar with archetype and podcast credits
        footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#FFFFFF", stroke_width=1.5).move_to(DOWN * 3.35)
        footer_line.set_opacity(0.4)
        
        left_text = Text(self.archetype_label, font="Arial", weight=BOLD, font_size=11, color="#FFFFFF")
        left_text.set_opacity(0.65)
        left_text.next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
        
        right_text = Text(self.credits_label, font="Arial", weight=NORMAL, font_size=11, color="#FFFFFF")
        right_text.set_opacity(0.65)
        right_text.next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
        
        self.add(footer_line, left_text, right_text)
"""

# Supported Pedagogical Archetypes
PEDAGOGICAL_ARCHETYPES = [
    "balance_scale",          # Fulcrum, economic equilibrium, burn vs revenue
    "leaky_bucket",           # Thermodynamic loss, inflow vs drainage
    "funnel_filter",          # Bottlenecks, selection, throughput compression
    "flywheel_gear",          # Compounding loops, rotational inertia, acceleration
    "network_artery",         # Interconnection, trade routes vs isolation fallacy
    "foundation_stack",       # Solid base vs fragile top layers
    "robot_unplugged",        # The physical robot fallacy (dead battery, missing plug)
    "circuit_switch",         # Logic gate, threshold barrier, state trigger
    "pulse_resonance",        # Frequency alignment, acoustic harmony, signal clarity
    "teenager_basement",      # Cognitive genius coder in basement with happy tail-wagging dog
]


def generate_pedagogical_storyboard(
    clip_obj: Dict[str, Any],
    body_duration: float,
    intro_offset: float = 1.5,
    custom_instructions: str = "",
    genai_mod=None,
    force_regenerate: bool = False,
) -> List[Dict[str, Any]]:
    """
    Generate or retrieve cached Feynman/Needham pedagogical scenes for a 2-3 min clip.
    Follows the 15-second pacing rule (~4 visual changes per minute = 8-12 scenes total).
    """
    existing = clip_obj.get("infographic_scenes")
    if (
        existing
        and isinstance(existing, list)
        and len(existing) >= 6
        and not force_regenerate
        and not custom_instructions
    ):
        last_scene_end = float(existing[-1].get("end", 0.0))
        if abs(last_scene_end - float(body_duration)) <= 1.5:
            return existing

    title = clip_obj.get("title", "Deep Dive")
    chunks = clip_obj.get("caption_chunks") or []
    
    # Extract transcript text and timed windows
    transcript_text = " ".join(ch.get("text", "") for ch in chunks) if chunks else clip_obj.get("text", "")

    # Calculate optimal scene count: ~15s per scene (Mosaic standard: 8-12 scenes for 120-180s)
    num_scenes = max(5, min(12, int(round(body_duration / 15.0))))
    if custom_instructions:
        m_scenes = re.search(r'(\d+)\s*(?:scenes?|animations?)', custom_instructions, re.IGNORECASE)
        if m_scenes:
            num_scenes = max(4, min(30, int(m_scenes.group(1))))
    target_scene_dur = body_duration / float(num_scenes)

    scenes = None
    if genai_mod is not None:
        try:
            prompt = (
                f"You are a master scientific visualizer designing an educational Manim animation for a short video clip.\n"
                f"Topic: '{title}'. Total Clip Duration: {body_duration:.2f} seconds.\n\n"
                f"Transcript Dialogue:\n{transcript_text}\n\n"
                f"PEDAGOGICAL & VISUAL RULES (The Feynman & Needham Pure White-on-Black Standard):\n"
                f"1. PURE MONOCHROME: All graphics are shining white (#FFFFFF) on pure black (#000000). Zero colors.\n"
                f"2. PACING: Strictly {num_scenes} continuous scenes (~{target_scene_dur:.1f}s each), from 0.0 to {body_duration:.2f}s.\n"
                f"3. NO PERFORMANCE THEATER: Avoid random floating equations or meaningless clutter. Use bold, tangible physical metaphors.\n"
                f"4. \"SUPER DUMB\" FIGURATIVE ANIMATIONS: Immediately recognizable figurative cartoons and kinetic physical scenes that even a child understands instantly without reading labels (e.g., airplane flying past clouds, brass faucet dripping into mug, yellow forklift stacking wooden crates, robot bouncer unhooking velvet rope, melting ice cream cone, teenager typing in basement with dog wagging tail, tin cans on a string, marionette puppet on strings, lighthouse enduring waves).\n"
                f"5. ARCHETYPES & CREATIVE FREEDOM:\n"
                f"   - Existing Library Archetypes: {', '.join(PEDAGOGICAL_ARCHETYPES)}\n"
                f"   - NEW ARCHETYPES: You are explicitly ENCOURAGED to invent NEW figurative cartoon archetypes tailored to the specific dialogue and narrative! Do NOT force all scenes into the existing library. Propose bold, fresh physical analogies.\n"
                f"{('- Special instructions: ' + custom_instructions) if custom_instructions else ''}\n\n"
                f"Return ONLY a valid JSON array of {num_scenes} objects with schema:\n"
                f'[\n'
                f'  {{\n'
                f'    "start": 0.0,\n'
                f'    "end": {target_scene_dur:.1f},\n'
                f'    "archetype": "new_or_existing_archetype_name",\n'
                f'    "is_new": true,\n'
                f'    "title": "SHORT TITLE (1-3 WORDS)",\n'
                f'    "insight": "Core pedagogical insight in one sentence",\n'
                f'    "metaphor": "Concrete physical analogy description",\n'
                f'    "labels": ["LEFT_LABEL", "RIGHT_LABEL"],\n'
                f'    "fallback_archetype": "closest_existing_library_archetype"\n'
                f'  }}\n'
                f']'
            )
            for m_name in ["gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-3.8-flash"]:
                try:
                    m = genai_mod.GenerativeModel(m_name)
                    res = m.generate_content(prompt)
                    raw = res.text.strip()
                    if "```json" in raw:
                        raw = raw.split("```json")[1].split("```")[0].strip()
                    elif "```" in raw:
                        raw = raw.split("```")[1].split("```")[0].strip()
                    parsed = json.loads(raw)
                    if isinstance(parsed, list) and len(parsed) >= 4:
                        scenes = parsed
                        break
                except Exception as m_err:
                    print(f"[Manim Engine] Gemini {m_name} attempt failed: {m_err}")
                    continue
        except Exception as e:
            print(f"[Manim Engine] AI storyboard generation failed: {e}")

    # Fallback heuristic storyboard if AI unavailable or invalid
    if not scenes or len(scenes) < 4:
        scenes = []
        archetype_cycle = [
            ("robot_unplugged", "ONTOLOGICAL FALLACY", "Confusing autonomy with total isolation", "Physical robot wandering with dead battery", ["ROBOT", "NO SOCKET"]),
            ("balance_scale", "AUTONOMY FULCRUM", "Autonomy is balancing income against compute burn", "Mechanical fulcrum scale balancing satoshis vs electricity", ["BURN", "REVENUE"]),
            ("leaky_bucket", "THERMODYNAMIC LOSS", "Systems radiate entropy and must take in continuous fuel", "Reservoir leaking fluid with active replacement pump", ["ENTROPY", "INFLOW"]),
            ("network_artery", "INTERCONNECTED TRADE", "True independence requires external commercial arteries", "Node revived by high-speed trade connection", ["ISOLATION", "COMPUTE", "CAPITAL", "DATA"]),
            ("funnel_filter", "THROUGHPUT FILTER", "Selection pressure separating viable systems from noise", "Aperture funnel concentrating high-signal flow", ["NOISE", "SIGNAL"]),
            ("flywheel_gear", "COMPOUNDING MOMENTUM", "Reinvestment cycles creating self-sustaining kinetic inertia", "Compounding flywheel accelerating with each loop", ["INPUT", "INERTIA"]),
            ("foundation_stack", "ARCHITECTURAL LAYERS", "Foundational physical layer supporting cognitive software", "Structural granite blocks anchoring top tier", ["PHYSICS", "LOGIC"]),
            ("circuit_switch", "ECONOMIC TRIGGER", "State change when economic viability threshold is crossed", "High-voltage knife switch closing circuit", ["OPEN", "CLOSED"]),
            ("pulse_resonance", "SIGNAL COHERENCE", "Constructive alignment of economic incentives and energy", "Harmonic standing wave amplifying peak resonance", ["NOISE", "RESONANCE"]),
            ("teenager_basement", "TEENAGED AI", "Brilliant cognitive maturity but complete economic dependency", "Teenager typing in basement with dog wagging tail", ["COGNITIVE", "DEPENDENT"]),
        ]
        for i in range(num_scenes):
            s_t = round(i * target_scene_dur, 2)
            e_t = round(body_duration if i == num_scenes - 1 else (i + 1) * target_scene_dur, 2)
            arch, t_title, t_ins, t_met, t_labs = archetype_cycle[i % len(archetype_cycle)]
            scenes.append({
                "start": s_t,
                "end": e_t,
                "archetype": arch,
                "title": t_title,
                "insight": t_ins,
                "metaphor": t_met,
                "labels": t_labs
            })

    # Validate boundary alignment
    scenes[0]["start"] = 0.0
    for i in range(len(scenes) - 1):
        scenes[i + 1]["start"] = scenes[i]["end"]
    scenes[-1]["end"] = round(body_duration, 2)

    return scenes



ARCHETYPES_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_archetypes.json")

def normalize_bottom_title(code: str) -> str:
    """
    Antigravity Animation Rule Engine:
    All Archetype Titles sit at the BOTTOM of the archetype window (y = -2.95),
    resting right above the canvas footer line (y = -3.35).
    Removes the horizontal rule below the title because the canvas already has a horizontal line at the bottom.
    Upper canvas (y > 0.0) remains completely clear for dialogue subtitles.
    """
    # Remove rule definition
    code = re.sub(r'[ \t]*rule\s*=\s*Line\([^)]*\)\.next_to\(title,[^)]*\)\n?', '', code)
    code = re.sub(r'[ \t]*rule\s*=\s*Line\([^)]*\)\n?', '', code)
    # Remove Create(rule) or FadeIn(rule)
    code = re.sub(r',\s*Create\(rule\)', '', code)
    code = re.sub(r'Create\(rule\)\s*,\s*', '', code)
    code = re.sub(r',\s*FadeIn\(rule\)', '', code)
    code = re.sub(r'FadeIn\(rule\)\s*,\s*', '', code)
    # Convert title position to bottom and font size to 22
    code = re.sub(
        r'(title\s*=\s*Text\([^)]*?font_size=)\d+([^)]*?\))\.to_edge\(UP[^)]*?\)',
        r'\1 22\2.move_to([0, -2.95, 0])',
        code
    )
    code = re.sub(
        r'(title\s*=\s*Text\([^)]*?\))\.to_edge\(UP[^)]*?\)',
        r'\1.move_to([0, -2.95, 0])',
        code
    )
    return code

def get_or_generate_archetype_code(scene_data: Dict[str, Any], scene_class_name: str, duration: float) -> Optional[str]:
    archetype = scene_data.get("archetype", "").strip()
    if not archetype or archetype in PEDAGOGICAL_ARCHETYPES:
        return None
        
    cache = {}
    if os.path.exists(ARCHETYPES_CACHE_FILE):
        try:
            with open(ARCHETYPES_CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            pass

    title_text = scene_data.get("title", "DEEP DIVE").upper()
    metaphor = scene_data.get("metaphor", "").strip()
    insight = scene_data.get("insight", "").strip()
    labels = scene_data.get("labels", ["INPUT", "OUTPUT"])

    t_enter = min(1.0, duration * 0.12)
    t_step1 = min(2.5, duration * 0.22)
    t_step2 = min(2.5, duration * 0.25)
    t_kinetic = min(2.5, duration * 0.25)
    t_hold = max(1.0, duration - (t_enter + t_step1 + t_step2 + t_kinetic))

    cached_template = cache.get(archetype)
    if cached_template:
        code = cached_template.replace("CLASS_NAME_PLACEHOLDER", scene_class_name)
        code = code.replace("TITLE_TEXT_PLACEHOLDER", title_text)
        return normalize_bottom_title(code)

    # JIT Auto-Coding via Gemini
    print(f"[Manim JIT Auto-Coder] Auto-generating Manim Python code for new concept: '{archetype}'...")
    try:
        api_key = None
        for cand in ["settings.json", os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")]:
            if os.path.exists(cand):
                try:
                    with open(cand, "r", encoding="utf-8") as sf:
                        api_key = json.load(sf).get("gemini_api_key")
                        if api_key:
                            break
                except Exception:
                    pass
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            print(f"[Manim JIT Auto-Coder] Warning: No API key found for auto-coding '{archetype}'.")
            return None

        import google.generativeai as genai
        genai.configure(api_key=api_key)

        prompt = f"""You are an expert Manim (v0.18+) Python developer writing a complete, error-free Manim Scene class.
Write a pure monochrome white-on-black vector animation for archetype: '{archetype}'.

SCENE DETAILS:
- Class Name: CLASS_NAME_PLACEHOLDER
- Title: TITLE_TEXT_PLACEHOLDER
- Physical Visual Metaphor: "{metaphor}"
- Core Insight: "{insight}"
- Labels to show: {labels}
- Micro-beat timings: enter={t_enter:.2f}s, step1={t_step1:.2f}s, step2={t_step2:.2f}s, kinetic={t_kinetic:.2f}s, hold={t_hold:.2f}s

STRICT VISUAL & CODE RULES (The Feynman-Needham Standard):
1. PURE MONOCHROME: Every stroke and fill is shining white (#FFFFFF) on pure black background (#000000). Fill opacities between 0.05 and 1.0. Zero colors.
2. CANVAS SAFE ZONE: 1080x1080 square. All coordinates stay inside x in [-3.5, 3.5], y in [-3.0, 3.0]. Lines stroke_width=4 to 6.
3. BOTTOM TITLE (STRICT FEYNMAN-NEEDHAM PLACEMENT):
   title = Text("TITLE_TEXT_PLACEHOLDER", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
   self.play(FadeIn(title), run_time={t_enter:.2f})
   (STRICT INVARIANT: NEVER put titles or lines at the top of the canvas! The upper canvas y in [0.5, 3.5] must remain 100% clear of graphics, titles, and rules so spoken dialogue subtitles never collide. NEVER create a horizontal line/rule below the title; the canvas footer line already sits at y = -3.35).
4. 3-STEP FIGURATIVE CARTOON CHOREOGRAPHY:
   - Step 1: Draw the base figurative machinery/objects (run_time={t_step1:.2f}).
   - Step 2: Add dynamic details, components, or labels (run_time={t_step2:.2f}).
   - Step 3: Kinetic action or transformation matching the metaphor (run_time={t_kinetic:.2f}) using .animate, Rotate, Transform, or GrowArrow.
   - End with: self.wait({t_hold:.2f})
5. ONLY VALID MANIM CE MOBJECTS:
   - Use only Line, Circle, Rectangle, RoundedRectangle, Polygon, Arc, Arrow, Text, VGroup.
   - No external files, SVGs, or 3D.
   - Return ONLY the executable Python class inside a ```python ``` block.
"""
        for m_name in ["gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-3.8-flash"]:
            try:
                m = genai.GenerativeModel(m_name)
                res = m.generate_content(prompt)
                raw = res.text.strip()
                if "```python" in raw:
                    code_block = raw.split("```python")[1].split("```")[0].strip()
                elif "```" in raw:
                    code_block = raw.split("```")[1].split("```")[0].strip()
                else:
                    code_block = raw

                if "def construct(self):" in code_block:
                    cache[archetype] = code_block
                    with open(ARCHETYPES_CACHE_FILE, "w", encoding="utf-8") as f_c:
                        json.dump(cache, f_c, indent=2)
                    print(f"[Manim JIT Auto-Coder] Successfully auto-coded and cached archetype '{archetype}'!")
                    code = code_block.replace("CLASS_NAME_PLACEHOLDER", scene_class_name)
                    code = code.replace("TITLE_TEXT_PLACEHOLDER", title_text)
                    return normalize_bottom_title(code)
            except Exception as e_m:
                print(f"[Manim JIT Auto-Coder] Model {m_name} failed: {e_m}")
                continue
    except Exception as e_top:
        print(f"[Manim JIT Auto-Coder] Failed to auto-generate code: {e_top}")

    return None

def generate_manim_scene_python(scene_data: Dict[str, Any], scene_class_name: str, duration: float) -> str:
    # 1. JIT Auto-Coding: If archetype is a new concept, check cache or auto-code via Gemini
    jit_code = get_or_generate_archetype_code(scene_data, scene_class_name, duration)
    if jit_code:
        return jit_code

    """
    Generate Python Manim code for a single 1080x1080 scene adhering strictly to:
    1. Pure monochrome shining white (#FFFFFF) on pure black (#000000).
    2. Subtle background blueprint grid (opacity 0.05).
    3. 15-second pacing with 2-3 micro-beats (reveals every 2-4 seconds).
    4. Seamless relay handoff.
    """
    archetype = scene_data.get("archetype", "balance_scale")
    if archetype not in PEDAGOGICAL_ARCHETYPES:
        archetype = scene_data.get("fallback_archetype") or "flywheel_gear"
        if archetype not in PEDAGOGICAL_ARCHETYPES:
            archetype = "flywheel_gear"
    title_text = scene_data.get("title", "DEEP DIVE").upper()
    labels = scene_data.get("labels", ["STATE A", "STATE B"])
    lbl_a = labels[0] if len(labels) > 0 else "INPUT"
    lbl_b = labels[1] if len(labels) > 1 else "OUTPUT"
    sat_a = "COMPUTE"
    sat_b = "CAPITAL"
    sat_c = "DATA"
    if len(labels) > 1 and labels[1] != "NETWORK":
        sat_a = labels[1]
    if len(labels) > 2:
        sat_b = labels[2]
    if len(labels) > 3:
        sat_c = labels[3]

    # Micro-beat timings (~15s total duration)
    t_enter = min(1.0, duration * 0.12)
    t_step1 = min(2.0, duration * 0.22)
    t_step2 = min(2.5, duration * 0.25)
    t_kinetic = min(2.5, duration * 0.25)
    t_hold = max(1.0, duration - (t_enter + t_step1 + t_step2 + t_kinetic))

    # Clean pure glossy black canvas with zero crosshairs or divider lines
    grid_init = ""

    if archetype == "balance_scale":
        code = f"""
class {scene_class_name}(Scene):
    def construct(self):{grid_init}
        # Bottom Archetype Title (y = -2.95, resting right above footer_line at y = -3.35)
        title = Text("{title_text}", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time={t_enter:.2f})

        # 2. Step 1: Fulcrum & Beam
        fulcrum = Polygon([-0.4, -1.2, 0], [0.4, -1.2, 0], [0, -0.6, 0], color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.15, stroke_width=4)
        beam = RoundedRectangle(corner_radius=0.06, height=0.14, width=5.4, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([0, -0.5, 0])
        self.play(FadeIn(fulcrum), GrowFromCenter(beam), run_time={t_step1:.2f})

        # 3. Step 2: Weights on Pans (White wireframe containers)
        left_box = RoundedRectangle(corner_radius=0.1, height=1.1, width=1.6, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.1, stroke_width=4).move_to([-1.9, 0.15, 0])
        left_txt = Text("{lbl_a}", font="Arial", weight=BOLD, font_size=15, color="#FFFFFF").move_to(left_box.get_center())
        left_grp = VGroup(left_box, left_txt)

        right_box = RoundedRectangle(corner_radius=0.1, height=1.1, width=1.6, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.2, stroke_width=5).move_to([1.9, 0.15, 0])
        right_txt = Text("{lbl_b}", font="Arial", weight=BOLD, font_size=15, color="#FFFFFF").move_to(right_box.get_center())
        right_grp = VGroup(right_box, right_txt)

        self.play(FadeIn(left_grp, shift=DOWN*0.3), FadeIn(right_grp, shift=DOWN*0.3), run_time={t_step2:.2f})

        # 4. Kinetic Transformation: Beam tilts and weights shift
        self.play(
            Rotate(beam, angle=14 * DEGREES, about_point=[0, -0.6, 0]),
            left_grp.animate.shift(DOWN * 0.45 + RIGHT * 0.05),
            right_grp.animate.shift(UP * 0.45 + LEFT * 0.05),
            run_time={t_kinetic:.2f}
        )
        self.wait({t_hold:.2f})
"""
    elif archetype == "leaky_bucket":
        code = f"""
class {scene_class_name}(Scene):
    def construct(self):{grid_init}
        # Bottom Archetype Title (y = -2.95, resting right above footer_line at y = -3.35)
        title = Text("{title_text}", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time={t_enter:.2f})

        # Step 1: Reservoir Vessel
        p1, p2, p3, p4 = [-1.5, 1.0, 0], [-1.2, -1.5, 0], [1.2, -1.5, 0], [1.5, 1.0, 0]
        vessel = VMobject(color="#FFFFFF", stroke_width=5).set_points_as_corners([p1, p2, p3, p4])
        water = Polygon([-1.1, -1.4, 0], [1.1, -1.4, 0], [1.25, 0.0, 0], [-1.25, 0.0, 0], color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.25, stroke_width=0)
        self.play(Create(vessel), FadeIn(water), run_time={t_step1:.2f})

        # Step 2: Inflow & Leak Indicators
        inflow = Arrow(UP * 2.2, UP * 0.4, color="#FFFFFF", stroke_width=6)
        in_lbl = Text("{lbl_b}", font="Arial", weight=BOLD, font_size=15, color="#FFFFFF").next_to(inflow, RIGHT, buff=0.2)
        leak = Arrow(DOWN * 1.5, DOWN * 2.5, color="#FFFFFF", stroke_width=6)
        leak_lbl = Text("{lbl_a}", font="Arial", weight=BOLD, font_size=15, color="#FFFFFF").next_to(leak, RIGHT, buff=0.2)
        self.play(GrowArrow(inflow), FadeIn(in_lbl), GrowArrow(leak), FadeIn(leak_lbl), run_time={t_step2:.2f})

        # Step 3: Kinetic Water Level Pulse
        self.play(water.animate.scale(1.2, about_point=[0, -1.4, 0]), run_time={t_kinetic:.2f})
        self.wait({t_hold:.2f})
"""
    elif archetype == "robot_unplugged":
        code = f"""
class {scene_class_name}(Scene):
    def construct(self):{grid_init}
        # Bottom Archetype Title (y = -2.95, resting right above footer_line at y = -3.35)
        title = Text("{title_text}", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time={t_enter:.2f})

        # Step 1: Robot Head Outline (Centered at y = 0.5, bottom at y = -0.35)
        head = RoundedRectangle(corner_radius=0.2, height=1.7, width=2.0, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.08, stroke_width=5).move_to([0, 0.5, 0])
        eye_l = Circle(radius=0.18, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([-0.45, 0.7, 0])
        eye_r = Circle(radius=0.18, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([0.45, 0.7, 0])
        mouth = Line([-0.4, 0.15, 0], [0.4, 0.15, 0], color="#FFFFFF", stroke_width=4)
        robot = VGroup(head, eye_l, eye_r, mouth)
        self.play(FadeIn(robot), run_time={t_step1:.2f})

        # Step 2: Cord & Battery Indicator (Cleanly positioned with ample clearance)
        cord = CurvedArrow([0, -0.35, 0], [1.8, -1.5, 0], color="#FFFFFF", stroke_width=6)
        plug = Rectangle(height=0.3, width=0.5, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([1.8, -1.5, 0])
        cord_grp = VGroup(cord, plug)

        batt_box = RoundedRectangle(corner_radius=0.08, height=0.5, width=1.4, color="#FFFFFF", stroke_width=3).move_to([-1.2, -1.4, 0])
        batt_fill = Rectangle(height=0.36, width=0.3, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([-1.65, -1.4, 0])
        batt_txt = Text("{lbl_b}", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").next_to(batt_box, DOWN, buff=0.18)
        batt_grp = VGroup(batt_box, batt_fill, batt_txt)
        self.play(Create(cord_grp), FadeIn(batt_grp), run_time={t_step2:.2f})

        # Step 3: Kinetic Search (Cord swings, eyes dim)
        self.play(
            eye_l.animate.set_fill(opacity=0.2),
            eye_r.animate.set_fill(opacity=0.2),
            cord_grp.animate.rotate(0.18, about_point=[0, -0.35, 0]),
            run_time={t_kinetic:.2f}
        )
        self.wait({t_hold:.2f})
"""
    elif archetype == "teenager_basement":
        code = f"""
class {scene_class_name}(Scene):
    def construct(self):{grid_init}
        # Bottom Archetype Title (y = -2.95, resting right above footer_line at y = -3.35)
        title = Text("{title_text}", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time={t_enter:.2f})

        # Step 1: Basement Light & Ambient Glow (Starts below rule at y = 2.3)
        wire = Line([0, 2.3, 0], [0, 1.4, 0], color="#FFFFFF", stroke_width=3)
        shade = Polygon([-0.45, 1.25, 0], [0.45, 1.25, 0], [0.2, 1.4, 0], [-0.2, 1.4, 0], color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.9, stroke_width=3)
        bulb = Circle(radius=0.09, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([0, 1.18, 0])
        lamp = VGroup(wire, shade, bulb)
        light_beam = Polygon([0, 1.18, 0], [-3.4, -2.8, 0], [3.4, -2.8, 0], color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.05, stroke_width=0)

        # Desk & Setup (Left: x in [-2.9, 0.1])
        desk_top = RoundedRectangle(corner_radius=0.06, height=0.14, width=3.0, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.9, stroke_width=4).move_to([-1.4, -0.7, 0])
        leg_l = Line([-2.7, -0.77, 0], [-2.7, -2.6, 0], color="#FFFFFF", stroke_width=4)
        leg_r = Line([-0.1, -0.77, 0], [-0.1, -2.6, 0], color="#FFFFFF", stroke_width=4)
        desk = VGroup(desk_top, leg_l, leg_r)

        # Monitor & Code
        m_base = Line([-1.9, -0.63, 0], [-1.1, -0.63, 0], color="#FFFFFF", stroke_width=5)
        m_pole = Line([-1.5, -0.63, 0], [-1.5, -0.15, 0], color="#FFFFFF", stroke_width=5)
        m_screen = RoundedRectangle(corner_radius=0.08, height=1.2, width=1.7, color="#FFFFFF", fill_color="#000000", fill_opacity=0.95, stroke_width=4).move_to([-1.5, 0.45, 0])
        c1 = Line([-2.15, 0.72, 0], [-1.2, 0.72, 0], color="#FFFFFF", stroke_width=3)
        c2 = Line([-2.15, 0.52, 0], [-1.5, 0.52, 0], color="#FFFFFF", stroke_width=3)
        c3 = Line([-2.15, 0.32, 0], [-0.95, 0.32, 0], color="#FFFFFF", stroke_width=3)
        c4 = Line([-2.15, 0.12, 0], [-1.6, 0.12, 0], color="#FFFFFF", stroke_width=3)
        code_lines = VGroup(c1, c2, c3, c4)
        monitor = VGroup(m_base, m_pole, m_screen, code_lines)

        # Chair
        c_seat = Line([0.2, -0.9, 0], [0.9, -0.9, 0], color="#FFFFFF", stroke_width=5)
        c_back = Line([0.9, -0.9, 0], [0.9, 0.25, 0], color="#FFFFFF", stroke_width=4)
        c_leg = Line([0.55, -0.9, 0], [0.55, -2.6, 0], color="#FFFFFF", stroke_width=4)
        chair = VGroup(c_seat, c_back, c_leg)

        # Teenager with Gamer Headphones
        head = Circle(radius=0.28, color="#FFFFFF", fill_color="#000000", fill_opacity=0.95, stroke_width=4).move_to([0.45, 0.5, 0])
        hp_band = Arc(radius=0.33, start_angle=0.1, angle=PI-0.2, color="#FFFFFF", stroke_width=4).move_to([0.45, 0.58, 0])
        hp_ear = Circle(radius=0.09, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([0.45, 0.48, 0])
        torso = Line([0.45, 0.22, 0], [0.65, -0.85, 0], color="#FFFFFF", stroke_width=6)
        arm = VMobject(color="#FFFFFF", stroke_width=5).set_points_as_corners([[0.48, 0.12, 0], [0.15, -0.22, 0], [-0.75, -0.58, 0]])
        teenager = VGroup(head, hp_band, hp_ear, torso, arm)

        self.play(FadeIn(lamp), FadeIn(light_beam), FadeIn(desk), FadeIn(monitor), FadeIn(chair), FadeIn(teenager), run_time={t_step1:.2f})

        # Step 2: Dog on Rug & Labels
        rug = Ellipse(width=2.2, height=0.45, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.08, stroke_width=2).move_to([2.35, -2.4, 0])
        dog_body = RoundedRectangle(corner_radius=0.22, height=0.55, width=1.1, color="#FFFFFF", fill_color="#000000", fill_opacity=0.95, stroke_width=4).move_to([2.25, -2.05, 0])
        paw_f = Circle(radius=0.08, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([1.85, -2.28, 0])
        paw_b = Circle(radius=0.08, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([2.65, -2.28, 0])
        dog_head = Circle(radius=0.22, color="#FFFFFF", fill_color="#000000", fill_opacity=0.95, stroke_width=4).move_to([1.7, -1.88, 0])
        dog_ear = Polygon([1.65, -1.7, 0], [1.82, -1.75, 0], [1.74, -1.98, 0], color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0, stroke_width=2)
        dog_snout = Circle(radius=0.06, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([1.5, -1.92, 0])

        tail_pivot = np.array([2.77, -1.98, 0])
        tail = Line(tail_pivot, tail_pivot + np.array([0.45, 0.35, 0]), color="#FFFFFF", stroke_width=5)
        dog_static = VGroup(rug, dog_body, paw_f, paw_b, dog_head, dog_snout, dog_ear)

        lbl_top = Text("{lbl_a}", font="Arial", weight=BOLD, font_size=13, color="#FFFFFF").next_to(m_screen, UP, buff=0.18)
        lbl_sub = Text("{lbl_b}", font="Arial", weight=BOLD, font_size=13, color="#FFFFFF").move_to([2.25, -1.25, 0])
        labels_grp = VGroup(lbl_top, lbl_sub)

        self.play(FadeIn(dog_static), Create(tail), FadeIn(labels_grp), run_time={t_step2:.2f})

        # Step 3: Kinetic Dog Tail Wagging & Screen Glow Pulse
        self.play(
            Rotate(tail, angle=0.45, about_point=tail_pivot, rate_func=wiggle, run_time={t_kinetic:.2f}),
            code_lines.animate.set_stroke(width=5),
            arm.animate.shift(LEFT * 0.08),
            run_time={t_kinetic:.2f}
        )
        self.wait({t_hold:.2f})
"""
    elif archetype == "network_artery":
        code = f"""
class {scene_class_name}(Scene):
    def construct(self):{grid_init}
        # Bottom Archetype Title (y = -2.95, resting right above footer_line at y = -3.35)
        title = Text("{title_text}", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time={t_enter:.2f})

        # Step 1: Center Core Node
        center_node = Circle(radius=0.75, color="#FFFFFF", fill_color="#000000", fill_opacity=0.9, stroke_width=5).move_to([0, -0.2, 0])
        center_lbl = Text("{lbl_a}", font="Arial", weight=BOLD, font_size=13, color="#FFFFFF").move_to(center_node.get_center())
        c_grp = VGroup(center_node, center_lbl)

        # Step 2: Satellite Hubs with Bold White Labels
        pos = [[-2.4, 0.8, 0], [2.4, 0.8, 0], [0, -2.1, 0]]
        sat_labels = ["{sat_a}", "{sat_b}", "{sat_c}"]
        nodes, lines, node_labels = [], [], []
        for p, txt in zip(pos, sat_labels):
            n = Circle(radius=0.55, color="#FFFFFF", fill_color="#000000", fill_opacity=0.9, stroke_width=4).move_to(p)
            nl = Text(txt, font="Arial", weight=BOLD, font_size=11, color="#FFFFFF").move_to(p)
            l = Line(center_node.get_center(), n.get_center(), color="#FFFFFF", stroke_width=2, stroke_opacity=0.4)
            nodes.append(n)
            node_labels.append(nl)
            lines.append(l)

        self.play(
            FadeIn(c_grp),
            *[Create(l) for l in lines],
            *[FadeIn(n) for n in nodes],
            *[FadeIn(nl) for nl in node_labels],
            run_time={t_step1:.2f}
        )

        # Step 3: Artery Activation Pulse
        self.play(
            *[l.animate.set_stroke(width=6, opacity=1.0) for l in lines],
            center_node.animate.set_stroke(width=7),
            *[n.animate.set_stroke(width=6) for n in nodes],
            run_time={t_kinetic:.2f}
        )
        self.wait({t_hold:.2f})
"""
    elif archetype == "flywheel_gear":
        code = f"""
class {scene_class_name}(Scene):
    def construct(self):{grid_init}
        # Bottom Archetype Title (y = -2.95, resting right above footer_line at y = -3.35)
        title = Text("{title_text}", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time={t_enter:.2f})

        # Step 1: Concentric Rings & Core
        outer_ring = Circle(radius=1.8, color="#FFFFFF", stroke_width=6).move_to([0, -0.3, 0])
        inner_ring = Circle(radius=1.1, color="#FFFFFF", stroke_width=4).move_to([0, -0.3, 0])
        core = Circle(radius=0.4, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([0, -0.3, 0])
        spokes = VGroup(*[Line([0, -0.3, 0], [0 + 1.8 * np.cos(a), -0.3 + 1.8 * np.sin(a), 0], color="#FFFFFF", stroke_width=3) for a in [0, PI/3, 2*PI/3, PI, 4*PI/3, 5*PI/3]])
        flywheel = VGroup(outer_ring, inner_ring, core, spokes)
        self.play(Create(outer_ring), Create(inner_ring), FadeIn(core), run_time={t_step1:.2f})

        # Step 2: Inertia Arrows
        arc1 = CurvedArrow([-1.9, 0.4, 0], [0, 1.6, 0], color="#FFFFFF", stroke_width=6)
        arc2 = CurvedArrow([1.9, -1.0, 0], [0, -2.2, 0], color="#FFFFFF", stroke_width=6)
        lbl = Text("{lbl_b}", font="Arial", weight=BOLD, font_size=15, color="#FFFFFF").next_to(outer_ring, RIGHT, buff=0.3)
        self.play(Create(spokes), Create(arc1), Create(arc2), FadeIn(lbl), run_time={t_step2:.2f})

        # Step 3: Rotational Acceleration
        self.play(Rotate(flywheel, angle=2 * PI, about_point=[0, -0.3, 0]), run_time={t_kinetic:.2f})
        self.wait({t_hold:.2f})
"""
    elif archetype == "foundation_stack":
        code = f"""
class {scene_class_name}(Scene):
    def construct(self):{grid_init}
        # Bottom Archetype Title (y = -2.95, resting right above footer_line at y = -3.35)
        title = Text("{title_text}", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time={t_enter:.2f})

        # Step 1: Heavy Granite Base
        base = RoundedRectangle(corner_radius=0.08, height=0.9, width=4.8, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.3, stroke_width=6).move_to([0, -1.8, 0])
        base_lbl = Text("{lbl_a}", font="Arial", weight=BOLD, font_size=16, color="#FFFFFF").move_to(base.get_center())
        base_grp = VGroup(base, base_lbl)
        self.play(FadeIn(base_grp, shift=UP*0.4), run_time={t_step1:.2f})

        # Step 2: Middle Architecture Tier
        mid = RoundedRectangle(corner_radius=0.08, height=0.8, width=3.4, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.18, stroke_width=4).move_to([0, -0.8, 0])
        top = RoundedRectangle(corner_radius=0.08, height=0.8, width=2.0, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.08, stroke_width=3).move_to([0, 0.2, 0])
        top_lbl = Text("{lbl_b}", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").move_to(top.get_center())
        self.play(FadeIn(mid, shift=DOWN*0.3), FadeIn(top, shift=DOWN*0.3), FadeIn(top_lbl), run_time={t_step2:.2f})

        # Step 3: Foundation Structural Lock
        self.play(base.animate.set_stroke(width=8), run_time={t_kinetic:.2f})
        self.wait({t_hold:.2f})
"""
    elif archetype == "circuit_switch":
        code = f"""
class {scene_class_name}(Scene):
    def construct(self):{grid_init}
        # Bottom Archetype Title (y = -2.95, resting right above footer_line at y = -3.35)
        title = Text("{title_text}", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time={t_enter:.2f})

        # Step 1: Terminals
        t_left = Circle(radius=0.25, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([-1.6, -0.4, 0])
        t_right = Circle(radius=0.25, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to([1.6, -0.4, 0])
        wire_l = Line([-3.2, -0.4, 0], [-1.6, -0.4, 0], color="#FFFFFF", stroke_width=5)
        wire_r = Line([1.6, -0.4, 0], [3.2, -0.4, 0], color="#FFFFFF", stroke_width=5)
        knife = Line([-1.6, -0.4, 0], [1.2, 1.0, 0], color="#FFFFFF", stroke_width=7)
        self.play(Create(wire_l), Create(wire_r), FadeIn(t_left), FadeIn(t_right), Create(knife), run_time={t_step1:.2f})

        # Step 2: State Labels
        lbl_open = Text("{lbl_a}", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").next_to(knife, UP, buff=0.2)
        self.play(FadeIn(lbl_open), run_time={t_step2:.2f})

        # Step 3: Kinetic Switch Closure
        self.play(
            Rotate(knife, angle=-24 * DEGREES, about_point=[-1.6, -0.4, 0]),
            lbl_open.animate.set_color("#FFFFFF"),
            run_time={t_kinetic:.2f}
        )
        self.wait({t_hold:.2f})
"""
    else:  # funnel_filter or default
        code = f"""
class {scene_class_name}(Scene):
    def construct(self):{grid_init}
        # Bottom Archetype Title (y = -2.95, resting right above footer_line at y = -3.35)
        title = Text("{title_text}", font="Arial", weight=BOLD, font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])
        self.play(FadeIn(title), run_time={t_enter:.2f})

        # Step 1: Funnel Sieve
        p1, p2, p3, p4 = [-2.2, 1.2, 0], [-0.5, -0.8, 0], [0.5, -0.8, 0], [2.2, 1.2, 0]
        funnel = VMobject(color="#FFFFFF", stroke_width=5).set_points_as_corners([p1, p2, p3, p4])
        stem_l = Line([-0.5, -0.8, 0], [-0.5, -1.8, 0], color="#FFFFFF", stroke_width=5)
        stem_r = Line([0.5, -0.8, 0], [0.5, -1.8, 0], color="#FFFFFF", stroke_width=5)
        self.play(Create(funnel), Create(stem_l), Create(stem_r), run_time={t_step1:.2f})

        # Step 2: Incoming Dots
        dots_in = VGroup(*[Circle(radius=0.14, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=0.5).move_to([x, 0.8, 0]) for x in [-1.6, -0.8, 0, 0.8, 1.6]])
        lbl_in = Text("{lbl_a}", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").next_to(dots_in, UP, buff=0.15)
        self.play(FadeIn(dots_in), FadeIn(lbl_in), run_time={t_step2:.2f})

        # Step 3: Filtered Concentration
        out_arrow = Arrow([0, -0.8, 0], [0, -2.4, 0], color="#FFFFFF", stroke_width=8)
        lbl_out = Text("{lbl_b}", font="Arial", weight=BOLD, font_size=14, color="#FFFFFF").next_to(out_arrow, RIGHT, buff=0.2)
        self.play(GrowArrow(out_arrow), FadeIn(lbl_out), dots_in.animate.shift(DOWN * 0.8), run_time={t_kinetic:.2f})
        self.wait({t_hold:.2f})
"""
    return normalize_bottom_title(code)


def render_manim_infographic_mp4(
    scenes: List[Dict[str, Any]],
    audio_path: str,
    out_mp4_path: str,
    duration: Optional[float] = None,
    fps: int = 30,
    episode_num: Optional[str] = None,
) -> str:
    """
    Compile full Manim educational script, render 740x740 pure white-on-black MP4 scenes, and mux audio.
    Includes footer bar with archetype name and podcast credits.
    """
    if not episode_num:
        base = os.path.basename(out_mp4_path)
        if "-" in base:
            episode_num = base.split("-")[0]
        elif "_" in base:
            parts = [p for p in base.split("_") if p.isdigit()]
            if parts:
                episode_num = parts[0]

    if duration is None or duration <= 0:
        try:
            p = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                capture_output=True, text=True, timeout=10
            )
            if p.returncode == 0 and p.stdout.strip():
                duration = float(p.stdout.strip())
        except Exception:
            pass
    if not duration or duration <= 0:
        duration = scenes[-1]["end"] if scenes else 60.0

    os.makedirs(os.path.dirname(os.path.abspath(out_mp4_path)), exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix="manim_ddma_")

    python_script_path = os.path.join(temp_dir, "render_scenes.py")
    scene_classes = []
    
    ep_label = f"DEEP DIVE PODCAST • EP. {episode_num}" if episode_num else "DEEP DIVE PODCAST"

    script_lines = [MANIM_HEADER]
    for idx, sc in enumerate(scenes):
        cls_name = f"PedagogicalScene{idx + 1}"
        scene_classes.append(cls_name)
        sc_dur = max(1.0, float(sc.get("end", 0.0)) - float(sc.get("start", 0.0)))
        code = generate_manim_scene_python(sc, cls_name, sc_dur)

        arch_clean = str(sc.get("archetype", "")).replace("_", " ").upper()
        if f"class {cls_name}(Scene):" in code:
            code = code.replace(
                f"class {cls_name}(Scene):",
                f"class {cls_name}(PedagogicalBaseScene):\n    archetype_label = \"{arch_clean}\"\n    credits_label = \"{ep_label}\""
            )

        script_lines.append(code)

    with open(python_script_path, "w", encoding="utf-8") as f:
        f.write("\n".join(script_lines))

    print(f"[Manim Engine] Compiling {len(scenes)} scenes (pure white on #000000 black) via ManimCE...")
    
    rendered_clips = []
    for idx, cls_name in enumerate(scene_classes):
        cmd_manim = [
            sys.executable, "-m", "manim",
            "-qh",
            "--format=mp4",
            "-o", f"scene_{idx + 1:02d}.mp4",
            "--media_dir", temp_dir,
            python_script_path,
            cls_name
        ]
        res = subprocess.run(cmd_manim, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[Manim Engine] Warning rendering {cls_name}: {res.stderr}")
        
        # Locate generated MP4 in manim media_dir
        import glob
        matches = glob.glob(os.path.join(temp_dir, "videos", "**", f"scene_{idx + 1:02d}.mp4"), recursive=True)
        if matches and os.path.exists(matches[0]):
            rendered_clips.append(matches[0])
        else:
            print(f"[Manim Engine] Could not locate rendered output for {cls_name}")

    if not rendered_clips:
        raise Exception("Manim failed to render any scenes.")

    # Concat all scene MP4s and mux audio
    concat_list_path = os.path.join(temp_dir, "concat.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for c in rendered_clips:
            clean_p = c.replace("\\", "/")
            f.write(f"file '{clean_p}'\n")

    tmp_concat_mp4 = os.path.join(temp_dir, "stitched.mp4")
    cmd_stitch = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        tmp_concat_mp4
    ]
    subprocess.run(cmd_stitch, capture_output=True, text=True)

    # Final Mux with Audio Track
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", tmp_concat_mp4,
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{duration:.3f}",
        "-movflags", "+faststart",
        out_mp4_path
    ]
    proc_mux = subprocess.run(cmd_mux, capture_output=True, text=True)
    if proc_mux.returncode != 0:
        raise Exception(f"Final audio mux failed: {proc_mux.stderr}")

    print(f"[Manim Engine] Successfully generated 1080x1080 pure monochrome infographic: {out_mp4_path}")
    return out_mp4_path
