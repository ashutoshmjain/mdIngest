import os
import sys
import re
import json
import glob
import time
import shutil
import subprocess
import urllib.request
from typing import Dict, Any, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_ROOT = os.path.dirname(SCRIPT_DIR)
ARCHETYPES_DIR = os.path.join(SCRIPT_DIR, "archetypes")
MEDIA_VIDEOS_DIR = os.path.join(GITHUB_ROOT, "media", "videos")
SETTINGS_PATH = os.path.join(SCRIPT_DIR, "settings.json")
GENERATED_ARCHETYPES_JSON = os.path.join(SCRIPT_DIR, "generated_archetypes.json")

PRIMARY_MODELS = [
    "models/gemini-3.5-flash-lite",
    "models/gemini-flash-lite-latest",
    "models/gemini-3.5-flash",
]


def _load_api_key() -> Optional[str]:
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                key = json.load(f).get("gemini_api_key")
                if key:
                    return str(key).strip()
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY")


def extract_scene_classes_from_py(py_path: str) -> List[Dict[str, Any]]:
    """
    Parses a clip_XX_gemini_scenes.py file and returns ordered scene class blocks
    with their class name, source code, extracted title/category, and visual comments.
    """
    if not os.path.exists(py_path):
        return []
    with open(py_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"(^class\s+(Scene\w+)\s*\([^\)]*\):)", re.MULTILINE)
    matches = list(pattern.finditer(content))
    results = []
    for i, m in enumerate(matches):
        start_idx = m.start()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        cls_name = m.group(2)
        cls_code = content[start_idx:end_idx].strip()

        # Extract human-readable summary / metaphor from comments or title call
        comments = []
        for line in cls_code.splitlines():
            s = line.strip()
            if s.startswith("#") and "Title and Footer" not in s and "Using universal" not in s:
                comments.append(s.lstrip("# ").strip())

        title_match = re.search(r'get_footer_and_title\([^\"]*\"([^\"]+)\"(?:,\s*\"([^\"]+)\")?', cls_code)
        if not title_match:
            title_match = re.search(r'Text\(\s*\"([^\"]+)\"', cls_code)

        scene_title = title_match.group(1) if title_match else cls_name
        cat_match = re.search(r'get_footer(?:_and_title)?\([^\)]*\"([^\"]+)\"\s*\)', cls_code)
        category = cat_match.group(1) if cat_match else "AI AUTONOMY"

        results.append({
            "class_name": cls_name,
            "title": scene_title,
            "category": category,
            "visual_summary": " • ".join(comments[:3]) if comments else "Bespoke monochrome vector animation",
            "code": cls_code,
        })
    return results


def ensure_clip_meta(clip_num: int, plan_clip: Optional[Dict[str, Any]] = None, body_duration: Optional[float] = None) -> Dict[str, Any]:
    """
    Loads or synthesizes clip_XX_meta.json aligned with clip_XX_gemini_scenes.py and media/videos/clip_XX_gemini_scenes/740p15/*.mp4.
    Returns both absolute episode timestamps and clip-relative timestamps (rel_start, rel_end, video_start, video_end).
    """
    c_num = int(clip_num)
    py_path = os.path.join(ARCHETYPES_DIR, f"clip_{c_num:02d}_gemini_scenes.py")
    meta_path = os.path.join(ARCHETYPES_DIR, f"clip_{c_num:02d}_meta.json")
    video_dir = os.path.join(MEDIA_VIDEOS_DIR, f"clip_{c_num:02d}_gemini_scenes", "740p15")

    parsed_classes = extract_scene_classes_from_py(py_path)

    meta_data = {}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)
        except Exception:
            meta_data = {}

    raw_beats = meta_data.get("beats", [])

    # Determine clip start/end and spoken words from plan_clip if available
    if plan_clip is None:
        # Auto-discover plan_clip from projects/episode_248/plan.json or root plan.json so we NEVER lose caption_chunks or audio_duration!
        for cand_plan in [
            os.path.join(SCRIPT_DIR, "projects", "episode_248", "plan.json"),
            os.path.join(SCRIPT_DIR, "plan.json"),
        ]:
            if os.path.exists(cand_plan):
                try:
                    with open(cand_plan, "r", encoding="utf-8") as pf:
                        p_list = json.load(pf)
                    if isinstance(p_list, list):
                        plan_clip = next((c for c in p_list if str(c.get("num")) == str(c_num)), None)
                        if plan_clip:
                            break
                except Exception:
                    pass

    c_start = float(plan_clip.get("start", 0.0)) if plan_clip else (float(raw_beats[0]["start"]) if raw_beats else 0.0)
    c_end = float(plan_clip.get("end", c_start + 120.0)) if plan_clip else (float(raw_beats[-1]["end"]) if raw_beats else c_start + 120.0)
    plan_audio_dur = float(plan_clip.get("audio_duration") or 0.0) if plan_clip else 0.0
    eff_body_dur = (
        float(body_duration)
        if body_duration and body_duration > 0
        else (plan_audio_dur if plan_audio_dur > 0 else max(10.0, c_end - c_start))
    )

    n_scenes = len(parsed_classes)
    if n_scenes == 0:
        return {"clip_num": c_num, "title": plan_clip.get("title", f"Part {c_num}") if plan_clip else f"Part {c_num}", "beats": []}

    # Extract caption words or chunks from plan_clip to populate exact spoken transcript per beat
    caption_chunks = (plan_clip.get("caption_chunks") or []) if plan_clip else []
    full_clip_text = (plan_clip.get("text") or "") if plan_clip else ""

    intro_offset = 1.5  # DDMA compiled short has a 1.5s intro title card before body starts
    beat_dur = eff_body_dur / n_scenes

    enriched_beats = []
    for idx, cls_info in enumerate(parsed_classes):
        cls_name = cls_info["class_name"]
        mp4_path = os.path.join(video_dir, f"{cls_name}.mp4")
        raw_b = raw_beats[idx] if idx < len(raw_beats) else {}

        rel_start = round(idx * beat_dur, 2)
        rel_end = round(eff_body_dur if idx == n_scenes - 1 else (idx + 1) * beat_dur, 2)
        vid_start = round(intro_offset + rel_start, 2)
        vid_end = round(intro_offset + rel_end, 2)

        abs_start = float(raw_b.get("start", c_start + rel_start))
        abs_end = float(raw_b.get("end", c_start + rel_end))

        # ALWAYS compute spoken text from exact word-timed caption_chunks in [vid_start, vid_end] when available
        # so the right-hand "SPOKEN DIALOGUE IN THIS BEAT" matches the burned-in ASS captions 100%!
        b_text = ""
        if caption_chunks:
            beat_words = []
            for ch in caption_chunks:
                w_list = ch.get("words") or []
                if w_list:
                    for w_obj in w_list:
                        w_mid = 0.5 * (float(w_obj.get("start", 0.0)) + float(w_obj.get("end", 0.0)))
                        if vid_start <= w_mid < vid_end:
                            beat_words.append(str(w_obj.get("word", "")).strip())
                else:
                    ch_mid = 0.5 * (float(ch.get("start", 0.0)) + float(ch.get("end", 0.0)))
                    if vid_start <= ch_mid < vid_end:
                        beat_words.append(str(ch.get("text", "")).strip())
            if beat_words:
                b_text = " ".join(w for w in beat_words if w)

        if not b_text:
            b_text = str(raw_b.get("text", "")).strip()
        if (not b_text or b_text.startswith("Discussion on ")) and full_clip_text:
            words = full_clip_text.split()
            w_per_beat = max(1, len(words) // n_scenes)
            b_text = " ".join(words[idx * w_per_beat : (idx + 1) * w_per_beat])

        # Always prefer the latest visual_summary extracted from the live Python class comments
        live_summary = cls_info.get("visual_summary") or raw_b.get("visual_summary") or "Bespoke monochrome vector animation"

        enriched_beats.append({
            "index": idx + 1,
            "class_name": cls_name,
            "title": raw_b.get("title") or cls_info["title"],
            "category": raw_b.get("category") or cls_info["category"],
            "visual_summary": live_summary,
            "user_notes": raw_b.get("user_notes", ""),
            "start": round(abs_start, 2),
            "end": round(abs_end, 2),
            "rel_start": rel_start,
            "rel_end": rel_end,
            "video_start": vid_start,
            "video_end": vid_end,
            "duration": round(rel_end - rel_start, 2),
            "text": b_text,
            "mp4_exists": os.path.exists(mp4_path),
            "mp4_url": f"/media/videos/clip_{c_num:02d}_gemini_scenes/740p15/{cls_name}.mp4",
            "py_file": f"archetypes/clip_{c_num:02d}_gemini_scenes.py",
            "code": cls_info["code"],
        })

    out_meta = {
        "clip_num": c_num,
        "title": (plan_clip.get("title") if plan_clip else None) or meta_data.get("title", f"Part {c_num}"),
        "py_file": f"archetypes/clip_{c_num:02d}_gemini_scenes.py",
        "video_dir": f"media/videos/clip_{c_num:02d}_gemini_scenes/740p15",
        "intro_offset": intro_offset,
        "body_duration": round(eff_body_dur, 2),
        "beats": enriched_beats,
    }

    # Save enriched metadata back to clip_XX_meta.json (without duplicating full code in JSON)
    disk_beats = []
    for b in enriched_beats:
        b_copy = dict(b)
        b_copy.pop("code", None)
        disk_beats.append(b_copy)
    disk_meta = dict(out_meta)
    disk_meta["beats"] = disk_beats
    try:
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(disk_meta, f, indent=2)
    except Exception:
        pass

    return out_meta


def stitch_precompiled_archetypes_for_clip(
    clip_num: int,
    audio_path: str,
    out_mp4_path: str,
    body_duration: float,
    plan_clip: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Super-fast (< 3 seconds) assembler for a DDMA short clip body video (740x740 with masked bottom title
    and centered graphic alignment between the captions line and bottom footer line)
    using the pre-compiled Manim MP4s in media/videos/clip_XX_gemini_scenes/740p15/*.mp4!
    Automatically compiles any missing single scene if needed.
    """
    c_num = int(clip_num)
    meta = ensure_clip_meta(c_num, plan_clip=plan_clip, body_duration=body_duration)
    beats = meta.get("beats", [])
    if not beats:
        return False

    video_dir = os.path.join(MEDIA_VIDEOS_DIR, f"clip_{c_num:02d}_gemini_scenes", "740p15")
    os.makedirs(video_dir, exist_ok=True)

    mp4_paths = []
    for b in beats:
        cls_name = b["class_name"]
        mp4_p = os.path.join(video_dir, f"{cls_name}.mp4")
        if not os.path.exists(mp4_p):
            compile_single_scene(c_num, cls_name)
        if os.path.exists(mp4_p):
            mp4_paths.append((mp4_p, float(b["duration"])))

    if not mp4_paths:
        return False

    os.makedirs(os.path.dirname(os.path.abspath(out_mp4_path)), exist_ok=True)

    # Build a single FFmpeg filtergraph that:
    # 1. Masks out y=622..672 (removing any legacy bottom archetype title while preserving footer at y=672..740),
    # 2. Shifts the illustration zone (y=110..622) upward by 110px to y=0..512 (padded with black down to y=672)
    #    so the graphic is centered midway between the upper captions line and the bottom footer line!
    # 3. Normalizes each scene to its beat duration, concatenates them seamlessly, and muxes the clip audio!
    inputs = []
    filter_parts = []
    concat_inputs = []

    for i, (mp4_p, t_dur) in enumerate(mp4_paths):
        inputs.extend(["-i", mp4_p])
        sc_dur = t_dur
        try:
            p = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", mp4_p],
                capture_output=True, text=True, timeout=5
            )
            if p.returncode == 0 and p.stdout.strip():
                sc_dur = float(p.stdout.strip())
        except Exception:
            pass

        pad_dur = max(0.0, t_dur - sc_dur + 0.5)
        filter_parts.append(
            f"[{i}:v]scale=740:740,fps=25,drawbox=x=0:y=622:w=740:h=50:color=black:t=fill,split=2[g{i}][f{i}];"
            f"[g{i}]crop=740:512:0:110,pad=740:672:0:0:black[gp{i}];"
            f"[f{i}]crop=740:68:0:672[fp{i}];"
            f"[gp{i}][fp{i}]vstack=inputs=2,"
            f"tpad=stop_mode=clone:stop_duration={pad_dur:.2f},trim=duration={t_dur:.3f},setpts=PTS-STARTPTS[v{i}];"
        )
        concat_inputs.append(f"[v{i}]")

    audio_idx = len(mp4_paths)
    inputs.extend(["-i", audio_path])

    filter_complex = (
        "".join(filter_parts)
        + "".join(concat_inputs)
        + f"concat=n={len(mp4_paths)}:v=1:a=0,setsar=1[vout]"
    )

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", f"{audio_idx}:a:0",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{body_duration:.3f}",
        "-movflags", "+faststart",
        out_mp4_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ArchetypeStudio] Warning stitching clip {c_num}: {res.stderr[-400:]}")
        return False

    print(f"[ArchetypeStudio] Superfast stitched {len(mp4_paths)} pre-compiled archetypes -> {out_mp4_path}")
    return True


def compile_single_scene(clip_num: int, class_name: str) -> Tuple[bool, str]:
    """
    Compiles a single Manim Scene class inside ddma/archetypes/clip_XX_gemini_scenes.py
    and places the resulting 740x740 MP4 into media/videos/clip_XX_gemini_scenes/740p15/<class_name>.mp4.
    """
    c_num = int(clip_num)
    py_path = os.path.join(ARCHETYPES_DIR, f"clip_{c_num:02d}_gemini_scenes.py")
    if not os.path.exists(py_path):
        return False, f"Scene file {py_path} not found."

    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{ARCHETYPES_DIR}{os.pathsep}{existing_pp}" if existing_pp else ARCHETYPES_DIR

    cmd = [
        sys.executable, "-m", "manim", "render",
        "-r", "740,740",
        "--fps", "15",
        "--format", "mp4",
        "--media_dir", os.path.join(GITHUB_ROOT, "media"),
        py_path,
        class_name,
    ]
    res = subprocess.run(cmd, cwd=GITHUB_ROOT, env=env, capture_output=True, text=True)
    out_mp4 = os.path.join(MEDIA_VIDEOS_DIR, f"clip_{c_num:02d}_gemini_scenes", "740p15", f"{class_name}.mp4")

    # Purge partial_movie_files immediately so disk stays clean
    partial_dir = os.path.join(MEDIA_VIDEOS_DIR, f"clip_{c_num:02d}_gemini_scenes", "740p15", "partial_movie_files", class_name)
    if os.path.exists(partial_dir):
        shutil.rmtree(partial_dir, ignore_errors=True)

    if res.returncode == 0 and os.path.exists(out_mp4):
        return True, out_mp4
    return False, (res.stderr or res.stdout)[-600:]


def synthesize_figurative_manim_class(
    class_name: str,
    user_directive: str,
    spoken_text: str = "",
    duration: float = 7.5,
) -> str:
    """
    Synthesizes bespoke, error-free pure monochrome ManimCE Python code locally
    when the Gemini REST API is unavailable or returns HTTP 401/429.
    Supports literal figurative animations (commercial airplane flying with empty seats,
    faucet dripping, forklift, server rack + clock, balance scale, battery/plug, etc.)
    centered cleanly in the middle of the viewport.
    """
    match_text = f"{user_directive} {spoken_text}".lower()
    d_clean = user_directive.strip().replace('"', "'") if user_directive.strip() else "Figurative concept animation"
    dur = max(4.0, float(duration))

    # 1. Commercial Airplane Flying (with empty cabin windows & passing clouds)
    if any(k in match_text for k in ["airplane", "plane", "flight", "flying", "jet", "airline", "aircraft", "empty seat"]):
        t_build = round(min(1.6, dur * 0.16), 2)
        t_fly = round(max(2.0, dur - t_build - 0.8), 2)
        t_out = round(max(0.5, dur - t_build - t_fly), 2)
        return f'''class {class_name}(Scene):
    def construct(self):
        get_footer(self)
        # Visual: Commercial airplane flying past clouds with empty cabin seats ({d_clean})
        fuselage = RoundedRectangle(width=3.6, height=0.82, corner_radius=0.41, color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0).move_to([0, -0.35, 0])
        nose_cockpit = Arc(radius=0.38, start_angle=-PI/3, angle=2*PI/3, color="#FFFFFF", stroke_width=3).move_to([1.52, -0.32, 0])
        tail_fin = Polygon([-1.65, 0.0, 0], [-2.25, 1.05, 0], [-1.15, 0.0, 0], color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0)
        wing_bottom = Polygon([-0.55, -0.45, 0], [-1.35, -1.55, 0], [-0.25, -1.55, 0], [0.55, -0.45, 0], color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0)
        wing_top = Polygon([-0.35, 0.05, 0], [-0.95, 0.78, 0], [-0.15, 0.78, 0], [0.35, 0.05, 0], color="#FFFFFF", stroke_width=3, fill_color="#000000", fill_opacity=1.0)
        engine = RoundedRectangle(width=0.65, height=0.30, corner_radius=0.12, color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=0.18).move_to([-0.5, -1.12, 0])

        # Illuminated empty passenger windows along the cabin
        windows = VGroup(*[
            RoundedRectangle(width=0.22, height=0.26, corner_radius=0.06, color="#FFFFFF", stroke_width=2.5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([-1.05 + i * 0.44, -0.32, 0])
            for i in range(6)
        ])
        tag = Text("EMPTY SEATS • PERISHABLE CAPACITY", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, -2.05, 0]).set_opacity(0.85)

        plane = VGroup(wing_top, tail_fin, fuselage, nose_cockpit, windows, wing_bottom, engine).shift(LEFT * 0.4 + DOWN * 0.15)

        # Fluffy clouds & slipstream lines rushing past
        cloud1 = VGroup(
            Circle(radius=0.28, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.1, 0.85, 0]),
            Circle(radius=0.36, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.45, 0.92, 0]),
            Circle(radius=0.26, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.8, 0.82, 0]),
        ).set_opacity(0.75)
        cloud2 = VGroup(
            Circle(radius=0.24, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.5, -1.55, 0]),
            Circle(radius=0.32, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.85, -1.48, 0]),
        ).set_opacity(0.65)
        wind_lines = VGroup(
            DashedLine([3.2, 0.35, 0], [-3.2, 0.35, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.45),
            DashedLine([3.2, -0.95, 0], [-3.2, -0.95, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.45),
        )

        self.play(FadeIn(plane, shift=RIGHT * 0.4 + UP * 0.15), FadeIn(cloud1), FadeIn(cloud2), Create(wind_lines), FadeIn(tag), run_time={t_build})
        self.play(
            plane.animate.shift(RIGHT * 0.85 + UP * 0.32).rotate(0.06),
            cloud1.animate.shift(LEFT * 4.4),
            cloud2.animate.shift(LEFT * 4.8),
            windows.animate.set_fill(opacity=0.45),
            run_time={t_fly},
            rate_func=linear
        )
        self.wait({t_out})'''

        # 2. 100 Meter Sprint / Race Against Time (Sprinter on track racing a giant stopwatch to finish line)
    if any(k in match_text for k in ["100 meter", "race", "sprint", "runner", "running", "track", "marathon", "finish line"]):
        t_build = round(min(1.6, dur * 0.16), 2)
        t_run = round(max(2.0, dur - t_build - 0.8), 2)
        t_out = round(max(0.5, dur - t_build - t_run), 2)
        return f'''class {class_name}(Scene):
    def construct(self):
        get_footer(self)
        # Visual: 100-meter sprinter racing against a ticking stopwatch toward the finish line ({d_clean})
        track_top = Line([-3.1, -0.85, 0], [3.1, -0.85, 0], color="#FFFFFF", stroke_width=3).set_opacity(0.6)
        track_mid = DashedLine([-3.1, -1.35, 0], [3.1, -1.35, 0], color="#FFFFFF", stroke_width=2).set_opacity(0.45)
        track_bot = Line([-3.1, -1.85, 0], [3.1, -1.85, 0], color="#FFFFFF", stroke_width=4)
        finish_pole = Line([2.55, 0.25, 0], [2.55, -1.85, 0], color="#FFFFFF", stroke_width=4)
        finish_banner = RoundedRectangle(width=1.05, height=0.34, corner_radius=0.05, color="#FFFFFF", stroke_width=2.5, fill_color="#000000", fill_opacity=1.0).move_to([2.55, 0.45, 0])
        finish_txt = Text("100M", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to(finish_banner.get_center())

        # Ticking Stopwatch above the track
        clock_ring = Circle(radius=0.58, color="#FFFFFF", stroke_width=3.5).move_to([0.0, 0.45, 0])
        clock_btn = Rectangle(width=0.22, height=0.12, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).next_to(clock_ring, UP, buff=0.02)
        clock_hand = Line(clock_ring.get_center(), clock_ring.get_center() + UP * 0.44, color="#FFFFFF", stroke_width=4)

        # Dynamic Sprinter Figure (Head, Torso, Pumping Arms & Striding Legs)
        r_head = Circle(radius=0.18, color="#FFFFFF", stroke_width=3.5, fill_color="#FFFFFF", fill_opacity=0.2).move_to([-2.0, -0.15, 0])
        r_torso = Line([-2.05, -0.33, 0], [-2.25, -0.95, 0], color="#FFFFFF", stroke_width=5)
        r_arm_f = Line([-2.12, -0.52, 0], [-1.72, -0.38, 0], color="#FFFFFF", stroke_width=3.5)
        r_arm_b = Line([-2.12, -0.52, 0], [-2.52, -0.68, 0], color="#FFFFFF", stroke_width=3.5)
        r_leg_f = Line([-2.25, -0.95, 0], [-1.82, -1.55, 0], color="#FFFFFF", stroke_width=4)
        r_leg_b = Line([-2.25, -0.95, 0], [-2.65, -1.52, 0], color="#FFFFFF", stroke_width=4)
        speed_lines = VGroup(
            Line([-3.0, -0.35, 0], [-2.45, -0.35, 0], color="#FFFFFF", stroke_width=2.5).set_opacity(0.6),
            Line([-3.1, -0.75, 0], [-2.55, -0.75, 0], color="#FFFFFF", stroke_width=2.5).set_opacity(0.6),
        )
        sprinter = VGroup(r_head, r_torso, r_arm_f, r_arm_b, r_leg_f, r_leg_b, speed_lines)
        tag = Text("100M SPRINT • RACE AGAINST TIME", font="Arial", weight=BOLD, font_size=12, color="#FFFFFF").move_to([0, -2.25, 0]).set_opacity(0.85)

        self.play(
            Create(track_top), Create(track_mid), Create(track_bot),
            Create(finish_pole), FadeIn(finish_banner), FadeIn(finish_txt),
            Create(clock_ring), FadeIn(clock_btn), Create(clock_hand),
            FadeIn(sprinter, shift=RIGHT * 0.3), FadeIn(tag),
            run_time={t_build}
        )
        self.play(
            sprinter.animate.shift(RIGHT * 4.15),
            Rotate(clock_hand, angle=-6 * PI, about_point=clock_ring.get_center()),
            finish_banner.animate.set_fill(color="#FFFFFF", opacity=0.25),
            run_time={t_run},
            rate_func=linear
        )
        self.wait({t_out})'''

    # 3. Check if directive matches any of our 22 cached figurative archetypes in generated_archetypes.json
    if os.path.exists(GENERATED_ARCHETYPES_JSON):
        try:
            with open(GENERATED_ARCHETYPES_JSON, "r", encoding="utf-8") as f:
                arch_cache = json.load(f)
            keyword_map = {
                "faucet": "leaky_faucet_meter",
                "drip": "leaky_faucet_meter",
                "ice cream": "melting_ice_cream_cone",
                "melt": "melting_ice_cream_cone",
                "forklift": "warehouse_forklift_stacker",
                "crate": "warehouse_forklift_stacker",
                "bouncer": "velvet_rope_bouncer",
                "velvet": "velvet_rope_bouncer",
                "puppet": "ornate_puppet_theater",
                "marionette": "ornate_puppet_theater",
                "locomotive": "coal_locomotive_burner",
                "train": "coal_locomotive_burner",
                "coal": "coal_locomotive_burner",
                "boiler": "steam_boiler_piston",
                "piston": "steam_boiler_piston",
                "tin can": "tin_can_intercom",
                "vault": "open_library_vault",
                "library": "open_library_vault",
                "bubble": "mayfly_bubble_blower",
                "parrot": "parrot_megaphone",
                "megaphone": "parrot_megaphone",
                "lighthouse": "lighthouse_storm_waves",
            }
            chosen_key = None
            for kw, ak in keyword_map.items():
                if kw in match_text and ak in arch_cache:
                    chosen_key = ak
                    break
            if chosen_key:
                raw_cls = arch_cache[chosen_key]
                idx = raw_cls.find("class CLASS_NAME_PLACEHOLDER")
                if idx != -1:
                    cls_body = raw_cls[idx:].replace("CLASS_NAME_PLACEHOLDER", class_name).replace("TITLE_TEXT_PLACEHOLDER", "")
                    cls_body = re.sub(r'title\s*=\s*Text\([^\)]*\)[^\n]*\n', 'title = VGroup()\n', cls_body)
                    return cls_body
        except Exception:
            pass

    # 3. General Kinetic Figurative Scene Builder for any custom producer directive
    t_build = round(min(1.6, dur * 0.2), 2)
    t_act = round(max(2.0, dur - t_build - 0.8), 2)
    t_out = round(max(0.5, dur - t_build - t_act), 2)
    short_label = " ".join(user_directive.upper().split()[:4]) if user_directive.strip() else "CONCEPT MODEL"
    short_label = re.sub(r'[^A-Z0-9 •\-]', '', short_label)[:28]

    return f'''class {class_name}(Scene):
    def construct(self):
        get_footer(self)
        # Visual: {d_clean}
        outer_frame = RoundedRectangle(width=4.4, height=2.6, corner_radius=0.18, color="#FFFFFF", stroke_width=4, fill_color="#000000", fill_opacity=1.0).move_to([0, -0.35, 0])
        core_hub = Circle(radius=0.72, color="#FFFFFF", stroke_width=5, fill_color="#FFFFFF", fill_opacity=0.15).move_to([-1.05, -0.35, 0])
        target_node = RoundedRectangle(width=1.3, height=1.3, corner_radius=0.15, color="#FFFFFF", stroke_width=4, fill_color="#FFFFFF", fill_opacity=0.12).move_to([1.15, -0.35, 0])
        flow_arrow = Arrow(core_hub.get_right(), target_node.get_left(), buff=0.15, color="#FFFFFF", stroke_width=6)
        orbit_dot = Circle(radius=0.14, color="#FFFFFF", fill_color="#FFFFFF", fill_opacity=1.0).move_to(core_hub.get_top())
        caption_lbl = Text("{short_label}", font="Arial", weight=BOLD, font_size=13, color="#FFFFFF").move_to([0, -2.05, 0]).set_opacity(0.85)

        scene_grp = VGroup(outer_frame, core_hub, target_node, flow_arrow, orbit_dot, caption_lbl)
        self.play(Create(outer_frame), FadeIn(core_hub), FadeIn(target_node), GrowArrow(flow_arrow), FadeIn(orbit_dot), FadeIn(caption_lbl), run_time={t_build})
        self.play(
            Rotate(orbit_dot, angle=4*PI, about_point=core_hub.get_center()),
            target_node.animate.set_fill(opacity=0.45).scale(1.08),
            run_time={t_act},
            rate_func=linear
        )
        self.wait({t_out})'''


def update_single_scene_with_ai(
    clip_num: int,
    beat_index: int,
    class_name: str,
    user_directive: str,
    spoken_text: str = "",
    duration: float = 7.5,
    custom_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Either saves direct custom Manim code or prompts Gemini Flash Lite (with automatic
    local figurative synthesizer fallback if the API key is an expired OAuth token)
    to rewrite ONLY the specified Scene class (`class_name`) inside
    `ddma/archetypes/clip_XX_gemini_scenes.py` based on `user_directive` and `spoken_text`,
    compiles just that single scene (~3s), and updates `clip_XX_meta.json`!
    Because it updates `ddma/archetypes/clip_XX_gemini_scenes.py` and `media/videos/clip_XX_gemini_scenes/740p15/`,
    both the Short Clip and the next Longform Master Video render automatically inherit the improvement!
    """
    c_num = int(clip_num)
    py_path = os.path.join(ARCHETYPES_DIR, f"clip_{c_num:02d}_gemini_scenes.py")
    meta_path = os.path.join(ARCHETYPES_DIR, f"clip_{c_num:02d}_meta.json")
    if not os.path.exists(py_path):
        raise Exception(f"Archetype file not found: {py_path}")

    with open(py_path, "r", encoding="utf-8") as f:
        full_py = f.read()

    # Locate the target class block in clip_XX_gemini_scenes.py
    pattern = re.compile(r"(^class\s+(Scene\w+)\s*\([^\)]*\):)", re.MULTILINE)
    matches = list(pattern.finditer(full_py))
    target_match_idx = next((i for i, m in enumerate(matches) if m.group(2) == class_name), None)
    if target_match_idx is None:
        raise Exception(f"Class {class_name} not found in {py_path}")

    start_pos = matches[target_match_idx].start()
    end_pos = matches[target_match_idx + 1].start() if target_match_idx + 1 < len(matches) else len(full_py)
    current_cls_code = full_py[start_pos:end_pos].strip()

    new_cls_code = custom_code.strip() if custom_code and custom_code.strip() else ""

    if not new_cls_code:
        api_key = _load_api_key()
        gen_text = ""

        # Only call generativelanguage.googleapis.com if api_key is a valid AIza... API key
        if api_key and not api_key.startswith("AQ."):
            prompt = f"""You are an elite Manim Community Edition (ManimCE) Python developer.
Rewrite ONLY the single Manim Scene class `{class_name}` below according to the Producer's Creative Change Request.

STRICT VISUAL & TECHNICAL RULES:
1. Class definition MUST remain exact: `class {class_name}(Scene):`
2. PURE MONOCHROME NOIR WITH FUNCTIONAL ACCENT: Every stroke, line, and fill is pure shining white ("#FFFFFF") on pure black ("#000000"). Functional accents may use gold ("#FFD700"). ZERO other colors.
3. STRICT INVARIANT: NO ARCHETYPE TITLES EVER: Do NOT draw a title at the top or bottom of the scene. Call `get_footer(self)` at the start of `construct(self)`. The footer renders Archetype Name on the left and 'deepDive podcast' on the right in #64748b.
4. SAFE ILLUSTRATION ZONE: Keep all geometry centered within x in [-3.0, 3.0] and y in [-1.8, 0.8] so it sits cleanly in the middle of the viewport.
5. "SUPER DUMB & LITERAL" FIGURATIVE CARTOON STORYTELLING: Draw clear, bold figurative objects (4px-12px strokes) that immediately illustrate the Producer's request and spoken words (e.g. faucet dripping into mug, forklift, airplane, prism, balance scale). Never stuff animations with number tables, tiny telemetry cards, or dense academic text. Include a `# Visual: <description>` comment at the top of `construct(self)`.
6. TIMING & PERSISTENCE INVARIANT: Total `run_time` + `self.wait()` must equal approximately {duration:.1f} seconds. NEVER call `FadeOut` on the main illustration at the end of the scene! The final visual state MUST persist on screen (`self.wait(...)`) until the next beat takes over so the screen is NEVER empty!
7. Use only standard ManimCE primitives: Line, DashedLine, Circle, Rectangle, RoundedRectangle, Polygon, Triangle, Arc, Arrow, DoubleArrow, Text, VGroup, Create, Write, FadeIn, GrowFromCenter, Transform, Rotate.

SPOKEN TRANSCRIPT DURING THIS {duration:.1f}s BEAT:
"{spoken_text}"

CURRENT MANIM CLASS CODE:
```python
{current_cls_code}
```

PRODUCER'S CREATIVE CHANGE REQUEST / FEEDBACK:
"{user_directive}"

Return ONLY the valid Python code for `class {class_name}(Scene):` inside a ```python ... ``` block. Do not include imports or other classes."""

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.35},
            }
            headers = {"Content-Type": "application/json"}
            for model_name in PRIMARY_MODELS:
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
                try:
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                    with urllib.request.urlopen(req, timeout=35) as resp:
                        res_data = json.loads(resp.read().decode("utf-8"))
                    gen_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    if gen_text:
                        break
                except Exception as e:
                    print(f"[ArchetypeStudio] [{model_name}] error: {e}")
                    time.sleep(0.5)

        if gen_text:
            code_match = re.search(r"```(?:python)?\s*(class\s+" + re.escape(class_name) + r"[\s\S]*?)```", gen_text)
            if code_match:
                new_cls_code = code_match.group(1).strip()
            else:
                idx_c = gen_text.find(f"class {class_name}")
                if idx_c != -1:
                    new_cls_code = gen_text[idx_c:].replace("```", "").strip()

        # Automatic Local Figurative Manim Synthesizer fallback if REST API key is an OAuth token or unavailable
        if not new_cls_code:
            print(f"[ArchetypeStudio] Synthesizing bespoke figurative Manim class locally for {class_name}: '{user_directive}'")
            new_cls_code = synthesize_figurative_manim_class(
                class_name=class_name,
                user_directive=user_directive,
                spoken_text=spoken_text,
                duration=duration,
            )

    # Backup original code in memory so we can rollback if Manim fails to compile
    updated_full_py = full_py[:start_pos] + new_cls_code + "\n\n" + full_py[end_pos:]
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(updated_full_py)

    ok, msg = compile_single_scene(c_num, class_name)
    if not ok:
        # If Gemini returned code with a syntax/Manim error, try our guaranteed local figurative synthesizer before rolling back!
        if not custom_code:
            fallback_code = synthesize_figurative_manim_class(
                class_name=class_name,
                user_directive=user_directive,
                spoken_text=spoken_text,
                duration=duration,
            )
            updated_full_py = full_py[:start_pos] + fallback_code + "\n\n" + full_py[end_pos:]
            with open(py_path, "w", encoding="utf-8") as f:
                f.write(updated_full_py)
            ok2, msg2 = compile_single_scene(c_num, class_name)
            if ok2:
                new_cls_code = fallback_code
                ok = True

    if not ok:
        # Rollback so we never leave broken code in the library
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(full_py)
        raise Exception(f"Manim compilation failed for updated {class_name} (rolled back safely):\n{msg}")

    # Persist user_notes / visual_summary in clip_XX_meta.json
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                m_data = json.load(f)
            for b in m_data.get("beats", []):
                if b.get("class_name") == class_name or b.get("index") == beat_index:
                    if user_directive:
                        b["user_notes"] = user_directive
                        b["visual_summary"] = f"Visual: {user_directive}"
                    b["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(m_data, f, indent=2)
        except Exception:
            pass

    return {
        "success": True,
        "clip_num": c_num,
        "class_name": class_name,
        "code": new_cls_code,
        "mp4_url": f"/media/videos/clip_{c_num:02d}_gemini_scenes/740p15/{class_name}.mp4?t={int(time.time())}",
    }


def _load_episode_plan(ep_num: str = "248") -> List[Dict[str, Any]]:
    clean_ep = str(ep_num).replace(".md", "").lstrip("_")
    for cand in [
        os.path.join(SCRIPT_DIR, "projects", f"episode_{clean_ep}", "plan.json"),
        os.path.join(SCRIPT_DIR, "plan.json"),
    ]:
        if os.path.exists(cand):
            try:
                with open(cand, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and data:
                    return data
            except Exception:
                pass
    return []


def _load_mapped_longform_words(ep_num: str = "248", total_duration: float = 3254.21) -> List[Dict[str, Any]]:
    """
    Loads the exact word-level timeline mapped with podcast_edit.json cuts & stings
    so that each Longform beat displays the exact words spoken during [longform_start, longform_end].
    """
    clean_ep = str(ep_num).replace(".md", "").lstrip("_")
    ep_dir = os.path.join(GITHUB_ROOT, "deepDive", "src", "ddma", "docs", "episodes", clean_ep)
    trans_path = os.path.join(ep_dir, "transcription.json")
    edit_path = os.path.join(ep_dir, "podcast_edit.json")

    if not os.path.exists(trans_path):
        return []

    try:
        with open(trans_path, "r", encoding="utf-8") as f:
            trans_data = json.load(f)
        edit_data = {}
        if os.path.exists(edit_path):
            with open(edit_path, "r", encoding="utf-8") as f:
                edit_data = json.load(f)

        from longform_video_engine import map_timeline_with_stings_and_cuts
        mapped_trans, _, _ = map_timeline_with_stings_and_cuts(trans_data, edit_data, total_duration)
        segs = mapped_trans.get("segments", [])
        words = []
        for s in segs:
            for w in s.get("words", []):
                w_text = str(w.get("word", "")).strip()
                if w_text:
                    words.append({
                        "word": w_text,
                        "start": float(w.get("start", s.get("start", 0.0))),
                        "end": float(w.get("end", s.get("end", 0.0))),
                    })
        return words
    except Exception:
        return []


WELCOME_STING_START = 29.68
WELCOME_STING_END = 39.68
_LF_INTERVALS_CACHE: Dict[str, Any] = {}


def _episode_dir(clean_ep: str) -> str:
    return os.path.join(GITHUB_ROOT, "deepDive", "src", "ddma", "docs", "episodes", clean_ep)


def _load_podcast_edit(ep_num: str = "248") -> Dict[str, Any]:
    clean_ep = str(ep_num).replace(".md", "").lstrip("_")
    p = os.path.join(_episode_dir(clean_ep), "podcast_edit.json")
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f) or {}
        except Exception:
            pass
    return {}


def _raw_source_duration(clean_ep: str, edit_data: Dict[str, Any]) -> float:
    """Raw (pre-edit) source speech duration: last transcribed word end, bounded by the outro sting position."""
    dur = 0.0
    tp = os.path.join(_episode_dir(clean_ep), "transcription.json")
    if os.path.exists(tp):
        try:
            with open(tp, "r", encoding="utf-8") as f:
                segs = json.load(f).get("segments", [])
            if segs:
                dur = float(segs[-1].get("end", 0.0))
        except Exception:
            pass
    sting_ats = [float(s.get("at", 0.0)) for s in edit_data.get("stings", [])]
    if sting_ats:
        dur = max(dur, max(sting_ats))
    return dur or 3215.34


def build_raw_to_lf_mapper(edit_data: Dict[str, Any], total_source_dur: float = 3215.34):
    """
    Returns map_t(raw_t) -> Longform Master time, mirroring longform_video_engine's
    cut removal + midroll sting slicing (+0.2s gap, sting_dur - 0.5s crossfade per midroll).
    """
    raw_cuts = edit_data.get("cuts", [])
    valid_cuts = sorted([
        (max(0.0, float(c.get("start", 0.0))), float(c.get("end", 0.0)))
        for c in raw_cuts if float(c.get("end", 0.0)) > float(c.get("start", 0.0)) + 0.05
    ])
    merged_cuts: List[List[float]] = []
    for cs, ce in valid_cuts:
        if not merged_cuts or cs > merged_cuts[-1][1] + 0.05:
            merged_cuts.append([cs, ce])
        else:
            merged_cuts[-1][1] = max(merged_cuts[-1][1], ce)

    def _cut_shift(t: float) -> float:
        return sum((ce - cs) if ce <= t else (t - cs if cs < t < ce else 0.0) for cs, ce in merged_cuts)

    speech_dur = total_source_dur - sum(ce - cs for cs, ce in merged_cuts)
    midrolls = []
    for s in sorted(edit_data.get("stings", []), key=lambda x: float(x.get("at", 0.0))):
        at_v = float(s.get("at", 0.0))
        dur_v = float(s.get("duration", 7.0)) or 7.0
        adj_at = max(0.0, at_v - _cut_shift(at_v))
        is_outro = (adj_at >= speech_dur - 3.0) or ("conclusion" in s.get("music_file", "") and adj_at >= speech_dur - 45.0)
        if not is_outro:
            midrolls.append({"adj_at": adj_at, "duration": dur_v})

    split_pts, filt_mid, last_pt = [], [], 0.0
    for vs in midrolls:
        if last_pt + 1.0 < vs["adj_at"] < speech_dur - 1.0:
            split_pts.append(vs["adj_at"])
            filt_mid.append(vs)
            last_pt = vs["adj_at"]
    slice_ranges, cur = [], 0.0
    for pt in split_pts:
        slice_ranges.append((cur, pt))
        cur = pt
    slice_ranges.append((cur, speech_dur))

    slice_master = []
    s0, e0 = slice_ranges[0]
    slice_master.append((0.0, e0 - s0, s0, e0))
    t_cur = e0 - s0
    for i, st in enumerate(filt_mid):
        t_nxt = max(t_cur, t_cur + 0.2 + st["duration"] - 0.5)
        ns, ne = slice_ranges[i + 1]
        slice_master.append((round(t_nxt, 2), round(t_nxt + (ne - ns), 2), ns, ne))
        t_cur = t_nxt + (ne - ns)

    def map_t(raw_t: float) -> float:
        ts = max(0.0, raw_t - _cut_shift(raw_t))
        for ms, me, ss, se in slice_master:
            if ss <= ts <= se + 0.05:
                return round(ms + (ts - ss), 2)
        return round(ts, 2)

    return map_t


def _norm_tok(w: str) -> str:
    return re.sub(r"[^a-z0-9']", "", str(w).lower().replace("\u2019", "'"))


def _anchor_beats_to_spoken_words(beats: List[Dict[str, Any]], mapped_words: List[Dict[str, Any]],
                                  window: float = 30.0, probe: int = 6) -> None:
    """
    Text-anchored alignment: the raw times in plan.json (DDMA transcript) and the Longform caption
    words (transcription.json) can drift by several seconds. For every kept beat, search the caption
    words near the time-mapped estimate for the beat's opening words and snap longform_start there,
    so each visual lands exactly on the words it illustrates. Falls back to the estimate.
    """
    toks = [_norm_tok(w["word"]) for w in mapped_words]
    starts = [w["start"] for w in mapped_words]
    prev_anchor = -1.0
    for b in beats:
        if b["omitted"] or b["longform_start"] is None:
            continue
        bt = [t for t in (_norm_tok(x) for x in str(b["beat"].get("text", "")).split()) if t][:probe]
        if len(bt) < 2:
            continue
        est = b["longform_start"]
        best = None
        for j, st in enumerate(starts):
            if st < est - window:
                continue
            if st > est + window:
                break
            if st < prev_anchor:
                continue
            score = sum(1 for k, t in enumerate(bt) if j + k < len(toks) and toks[j + k] == t)
            if score < min(3, len(bt)):
                continue
            key = (score, -abs(st - est))
            if best is None or key > best[0]:
                best = (key, st)
        if best is not None:
            delta = best[1] - b["longform_start"]
            b["longform_start"] = round(best[1], 2)
            b["longform_end"] = round(b["longform_end"] + delta, 2)
            prev_anchor = best[1]


def map_clip_beats_to_longform(clip_num: int, plan_clip: Dict[str, Any], map_t_fn,
                               mapped_words: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Exact audio-timestamp alignment: maps each Short beat [rel_start, rel_end] (Short body time)
    -> raw source audio time (removing the Short-only hook/sting structure) -> Longform Master time.
    Beats that exist only inside an out-of-order teaser hook (excerpt / flash-forward) are omitted,
    because the Longform plays that sentence linearly inside the main discussion.
    Returns [{"beat": short_beat, "longform_start", "longform_end"}] (+ omitted list via "omitted" flag).
    """
    meta = ensure_clip_meta(clip_num, plan_clip=plan_clip)
    short_beats = meta.get("beats", [])
    segs = plan_clip.get("segments", []) if plan_clip else []

    body_cursor = 0.0
    spans = []
    for s in segs:
        if s.get("type") == "audio":
            dur = float(s.get("duration", float(s["end"]) - float(s["start"])))
            spans.append({"body_start": body_cursor, "body_end": body_cursor + dur,
                          "raw_start": float(s["start"]), "raw_end": float(s["end"])})
            body_cursor += dur
        elif s.get("type") == "music":
            body_cursor += float(s.get("duration", 5.5)) + float(s.get("silence_before", 0.2)) - float(s.get("crossfade", 0.0))

    is_excerpt = len(spans) >= 2 and spans[0]["raw_start"] > spans[-1]["raw_start"]
    out: List[Dict[str, Any]] = []

    if not spans:
        c_st = float(plan_clip.get("start", 0.0)) if plan_clip else 0.0
        c_en = float(plan_clip.get("end", c_st + 120.0)) if plan_clip else c_st + 120.0
        n = max(1, len(short_beats))
        for i, sb in enumerate(short_beats):
            out.append({"beat": sb, "longform_start": map_t_fn(c_st + i * (c_en - c_st) / n),
                        "longform_end": map_t_fn(c_st + (i + 1) * (c_en - c_st) / n), "omitted": False})
    elif is_excerpt:
        disc = spans[-1]
        for sb in short_beats:
            r_st, r_en = float(sb["rel_start"]), float(sb["rel_end"])
            if r_en <= disc["body_start"] + 1.0:
                out.append({"beat": sb, "longform_start": None, "longform_end": None, "omitted": True})
                continue
            eff_st = max(0.0, r_st - disc["body_start"])
            eff_en = max(eff_st + 1.0, r_en - disc["body_start"])
            raw_st = min(disc["raw_end"] - 0.5, disc["raw_start"] + eff_st)
            raw_en = min(disc["raw_end"], disc["raw_start"] + eff_en)
            out.append({"beat": sb, "longform_start": map_t_fn(raw_st), "longform_end": map_t_fn(raw_en), "omitted": False})
    else:
        raw_chap_end = spans[-1]["raw_end"]

        def body_to_raw(b_t: float) -> float:
            if b_t <= spans[0]["body_end"]:
                return min(spans[0]["raw_end"], spans[0]["raw_start"] + max(0.0, b_t - spans[0]["body_start"]))
            if len(spans) >= 2 and b_t < spans[1]["body_start"]:
                return spans[0]["raw_end"]  # inside the Short-only sting
            sp = spans[-1]
            return min(sp["raw_end"], sp["raw_start"] + max(0.0, b_t - sp["body_start"]))

        for sb in short_beats:
            raw_st = body_to_raw(float(sb["rel_start"]))
            raw_en = body_to_raw(float(sb["rel_end"]))
            if raw_en <= raw_st + 0.5:
                raw_en = min(raw_chap_end, raw_st + 2.0)
            out.append({"beat": sb, "longform_start": map_t_fn(raw_st), "longform_end": map_t_fn(raw_en), "omitted": False})

    # Snap each beat onto the exact words it speaks in the Longform caption timeline
    if mapped_words:
        _anchor_beats_to_spoken_words(out, mapped_words)

    # Clip 1: Longform 0 -> 29.68 is the strict intro scene, 29.68 -> 39.68 the welcome sting card
    if int(clip_num) == 1:
        for b in out:
            if b["omitted"]:
                continue
            if b["longform_end"] <= WELCOME_STING_END + 1.0:
                b["omitted"] = True
            elif b["longform_start"] < WELCOME_STING_END:
                b["longform_start"] = WELCOME_STING_END

    # Contiguous, non-overlapping intervals within the chapter (screen never empty)
    kept = [b for b in out if not b["omitted"]]
    for i, b in enumerate(kept):
        if i > 0 and b["longform_start"] < kept[i - 1]["longform_end"]:
            b["longform_start"] = kept[i - 1]["longform_end"]
        if i < len(kept) - 1 and b["longform_end"] < kept[i + 1]["longform_start"]:
            b["longform_end"] = kept[i + 1]["longform_start"]
        if b["longform_end"] <= b["longform_start"] + 0.5:
            b["longform_end"] = round(b["longform_start"] + 3.0, 2)
        b["longform_start"] = round(b["longform_start"], 2)
        b["longform_end"] = round(b["longform_end"], 2)
    return out


def _lf_cache_key(clean_ep: str) -> str:
    parts = [clean_ep]
    for p in [os.path.join(SCRIPT_DIR, "projects", f"episode_{clean_ep}", "plan.json"),
              os.path.join(_episode_dir(clean_ep), "podcast_edit.json")]:
        parts.append(str(os.path.getmtime(p)) if os.path.exists(p) else "0")
    for p in sorted(glob.glob(os.path.join(ARCHETYPES_DIR, "clip_*_gemini_scenes.py")) +
                    glob.glob(os.path.join(ARCHETYPES_DIR, "clip_*_meta.json"))):
        parts.append(f"{os.path.basename(p)}:{os.path.getmtime(p)}")
    for p in sorted(glob.glob(os.path.join(SCRIPT_DIR, "clips", f"{clean_ep}-*-mosaic*.mp4"))):
        parts.append(f"{os.path.basename(p)}:{os.path.getmtime(p)}")
    return "|".join(parts)


_MOSAIC_PROBE_CACHE: Dict[str, Dict[str, Any]] = {}


def _probe_video_geometry(path: str) -> Dict[str, Any]:
    """ffprobe width/height/fps/duration of a video (cached by path + mtime)."""
    key = f"{path}|{os.path.getmtime(path)}"
    if key in _MOSAIC_PROBE_CACHE:
        return _MOSAIC_PROBE_CACHE[key]
    info = {"width": 0, "height": 0, "fps": 30.0, "duration": 0.0}
    try:
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height,r_frame_rate:format=duration",
             "-of", "json", path], capture_output=True, text=True, timeout=10)
        j = json.loads(p.stdout or "{}")
        st = (j.get("streams") or [{}])[0]
        num, _, den = str(st.get("r_frame_rate", "30/1")).partition("/")
        info["width"] = int(st.get("width") or 0)
        info["height"] = int(st.get("height") or 0)
        info["fps"] = float(num) / float(den or 1) if float(den or 1) else 30.0
        info["duration"] = float((j.get("format") or {}).get("duration") or 0.0)
    except Exception:
        pass
    _MOSAIC_PROBE_CACHE[key] = info
    return info


def resolve_mosaic_body(clean_ep: str, clip_num: int, plan_clip: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Locates the Mosaic body video for a chapter whose Active Master is Mosaic.
    Preference: the raw Mosaic run body clips/<ep>-<n>-mosaic-<run_id>.mp4 (square, caption-free,
    t=0 == Short body t=0); fallback: the compiled clips/<ep>-<n>-mosaic.mp4 (1080x1920 with the
    Intro title card, so body t=0 sits at intro_offset seconds).
    Returns {"path","offset","kind": "square"|"vertical","fps","duration","width","height"} or None.
    """
    clips_dir = os.path.join(SCRIPT_DIR, "clips")
    cands = []
    run_id = (plan_clip or {}).get("mosaic_run_id")
    if run_id:
        cands.append((os.path.join(clips_dir, f"{clean_ep}-{int(clip_num)}-mosaic-{run_id}.mp4"), 0.0))
    intro = float((plan_clip or {}).get("intro_offset") or 1.5)
    cands.append((os.path.join(clips_dir, f"{clean_ep}-{int(clip_num)}-mosaic.mp4"), intro))
    for path, offset in cands:
        if os.path.exists(path) and os.path.getsize(path) > 10000:
            g = _probe_video_geometry(path)
            if not g["width"] or not g["height"]:
                continue
            kind = "vertical" if g["height"] > g["width"] * 1.2 else "square"
            # Compiled 9:16 file: the body (excluding outro) ends at offset + audio_duration
            body_end = offset + float((plan_clip or {}).get("audio_duration") or max(0.0, g["duration"] - offset))
            return {"path": path, "offset": offset, "kind": kind, "fps": g["fps"],
                    "duration": g["duration"], "body_end": min(g["duration"], body_end) if g["duration"] else body_end,
                    "width": g["width"], "height": g["height"]}
    return None


def get_longform_all_chapter_mappings(ep_num: str = "248", total_duration: Optional[float] = None) -> Dict[str, Any]:
    """
    Single source of truth for Longform visual alignment (used by Beat Studio, full render and hot-patch).
    Returns {"chapters": {clip_num: {"start","end","beats":[...]}}, "total_duration"}.
    Chapter windows are contiguous: [first mapped beat start, next chapter first beat start).
    """
    clean_ep = str(ep_num).replace(".md", "").lstrip("_")
    key = _lf_cache_key(clean_ep) + f"|{total_duration}"
    if _LF_INTERVALS_CACHE.get("key") == key:
        return _LF_INTERVALS_CACHE["value"]

    plan_data = _load_episode_plan(clean_ep)
    edit_data = _load_podcast_edit(clean_ep)
    map_t = build_raw_to_lf_mapper(edit_data, _raw_source_duration(clean_ep, edit_data))
    if total_duration is None:
        total_duration = 3254.21
    mapped_words = _load_mapped_longform_words(clean_ep)

    chapters: Dict[int, Dict[str, Any]] = {}
    order: List[int] = []
    for idx, clip in enumerate(plan_data):
        c_num = int(clip.get("num", idx + 1))
        try:
            beats = map_clip_beats_to_longform(c_num, clip, map_t, mapped_words)
        except Exception:
            beats = []
        kept = [b for b in beats if not b["omitted"]]
        if c_num == 1:
            c_start = 0.0
        elif kept:
            c_start = kept[0]["longform_start"]
        else:
            c_start = map_t(float(clip.get("start", 0.0)))
        chapters[c_num] = {"start": round(c_start, 2), "beats": beats, "title": str(clip.get("title", f"Part {c_num}")).strip()}
        # Active Master: plan.json visual_source ("mosaic" | "manim" | None -> manim / existing behaviour)
        mosaic_body = None
        if str(clip.get("visual_source") or "").lower() == "mosaic":
            mosaic_body = resolve_mosaic_body(clean_ep, c_num, clip)
        chapters[c_num]["visual_source"] = "mosaic" if mosaic_body else "manim"
        chapters[c_num]["mosaic_body"] = mosaic_body
        order.append(c_num)

    for i, c_num in enumerate(order):
        ch = chapters[c_num]
        nxt = chapters[order[i + 1]]["start"] if i < len(order) - 1 else total_duration
        ch["end"] = round(max(nxt, ch["start"] + 1.0), 2)
        kept = [b for b in ch["beats"] if not b["omitted"]]
        if kept:
            # Hold the last visual until the next chapter speaks (screen-never-empty rule)
            kept[-1]["longform_end"] = ch["end"]
            # Trim any beat spilling past the chapter end
            prev_end = ch["start"]
            for b in kept:
                b["longform_start"] = max(b["longform_start"], prev_end)
                b["longform_end"] = min(b["longform_end"], ch["end"])
                if b["longform_end"] <= b["longform_start"] + 0.3:
                    b["omitted"] = True  # squeezed out: chapter has no room left for this visual
                    continue
                prev_end = b["longform_end"]
            kept = [b for b in kept if not b["omitted"]]
            if kept:
                kept[-1]["longform_end"] = ch["end"]

    value = {"ep_num": clean_ep, "total_duration": total_duration, "order": order, "chapters": chapters}
    _LF_INTERVALS_CACHE["key"] = key
    _LF_INTERVALS_CACHE["value"] = value
    return value


def get_longform_scene_intervals(ep_num: str = "248", total_duration: Optional[float] = None) -> List[Dict[str, Any]]:
    """All mapped Manim MP4 intervals across the Longform Master (for the compositor)."""
    data = get_longform_all_chapter_mappings(ep_num, total_duration)
    intervals: List[Dict[str, Any]] = []
    intro_mp4 = os.path.join(MEDIA_VIDEOS_DIR, "chapter_01_scenes_strict", "740p30", "Scene01_RobotWildernessFallacy.mp4")
    if os.path.exists(intro_mp4):
        intervals.append({"start": 0.0, "end": WELCOME_STING_START, "mp4": intro_mp4, "fps": 30, "clip_num": 1, "class_name": "Scene01_RobotWildernessFallacy"})
    for c_num in data["order"]:
        ch = data["chapters"][c_num]
        mb = ch.get("mosaic_body") if ch.get("visual_source") == "mosaic" else None
        if mb:
            # Mosaic Active Master: slice the Mosaic body by the SAME short->longform beat windows
            # (src time = body offset + Short body time); omitted teaser beats are skipped.
            src_max = max(mb["offset"], float(mb.get("body_end") or mb["duration"]) - 1.0 / max(1.0, mb["fps"]))
            kept = [b for b in ch["beats"] if not b["omitted"]]
            if not kept:
                kept = [{"beat": {"rel_start": 0.0, "rel_end": ch["end"] - ch["start"]},
                         "longform_start": ch["start"], "longform_end": ch["end"]}]
            for b in kept:
                sb = b["beat"]
                src_st = min(src_max, mb["offset"] + float(sb.get("rel_start", 0.0)))
                src_hold = min(src_max, max(src_st, mb["offset"] + float(sb.get("rel_end", 0.0))))
                intervals.append({"start": b["longform_start"], "end": b["longform_end"], "mp4": mb["path"],
                                  "fps": mb["fps"], "clip_num": c_num, "class_name": "mosaic",
                                  "visual_source": "mosaic", "src_offset": round(src_st, 3),
                                  "src_hold": round(src_hold, 3), "src_kind": mb["kind"]})
            continue
        v_dir = os.path.join(MEDIA_VIDEOS_DIR, f"clip_{c_num:02d}_gemini_scenes", "740p15")
        for b in ch["beats"]:
            if b["omitted"]:
                continue
            cls = b["beat"].get("class_name", "")
            mp4 = os.path.join(v_dir, f"{cls}.mp4")
            if not os.path.exists(mp4):
                continue
            intervals.append({"start": b["longform_start"], "end": b["longform_end"], "mp4": mp4, "fps": 15,
                              "clip_num": c_num, "class_name": cls})
    intervals.sort(key=lambda x: x["start"])
    # Close gaps (except the welcome sting window) so the last visual persists
    for i in range(len(intervals) - 1):
        if abs(intervals[i]["end"] - WELCOME_STING_START) < 0.5:
            continue
        if intervals[i]["end"] < intervals[i + 1]["start"]:
            intervals[i]["end"] = intervals[i + 1]["start"]
    if intervals and intervals[-1]["end"] < data["total_duration"]:
        intervals[-1]["end"] = data["total_duration"] + 1.0
    return intervals


def _probe_longform_duration(clean_ep: str) -> float:
    for v_cand in [
        os.path.join(_episode_dir(clean_ep), f"podcast_{clean_ep}.mp4"),
        os.path.join(SCRIPT_DIR, "clips", f"{clean_ep}-longform-master.mp4"),
        os.path.join(_episode_dir(clean_ep), f"podcast_{clean_ep}.mp3"),
    ]:
        if os.path.exists(v_cand):
            try:
                p = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", v_cand],
                    capture_output=True, text=True, timeout=5
                )
                if p.returncode == 0 and p.stdout.strip():
                    return float(p.stdout.strip())
            except Exception:
                pass
    return 3254.21


def get_longform_timeline_index(ep_num: str = "248") -> Dict[str, Any]:
    """
    Returns a lightweight (< 4 KB) chapter index across the 54-minute Longform Master video
    so the browser can progressively lazy-load individual chapter beats without bloating DOM memory.
    Chapter windows are exact Longform Master times (audio-timestamp aligned).
    """
    clean_ep = str(ep_num).replace(".md", "").lstrip("_")
    total_duration = _probe_longform_duration(clean_ep)
    data = get_longform_all_chapter_mappings(clean_ep, total_duration)

    chapters = []
    total_scenes = 0
    for c_num in data["order"]:
        ch = data["chapters"][c_num]
        n_scenes = len([b for b in ch["beats"] if not b["omitted"]])
        total_scenes += n_scenes
        chapters.append({
            "clip_num": c_num,
            "title": ch["title"],
            "start": ch["start"],
            "end": ch["end"],
            "duration": round(ch["end"] - ch["start"], 2),
            "scenes_count": n_scenes,
            "py_file": f"archetypes/clip_{c_num:02d}_gemini_scenes.py",
            "visual_source": ch.get("visual_source", "manim"),
            "locked": ch.get("visual_source") == "mosaic",
        })

    return {
        "ep_num": clean_ep,
        "total_duration": round(total_duration, 2),
        "total_chapters": len(chapters),
        "total_scenes": total_scenes,
        "welcome_sting": {"start": WELCOME_STING_START, "end": WELCOME_STING_END},
        "chapters": chapters,
    }


def get_longform_chapter_beats(ep_num: str = "248", clip_num: int = 1) -> Dict[str, Any]:
    """
    Progressively loads the ~12-18 Manim beats for a single Chapter (clip_num) mapped to
    their exact Longform Master timestamps [longform_start, longform_end] and spoken words.
    Teaser-only hook beats (out-of-order excerpts) are listed in "omitted_beats".
    """
    clean_ep = str(ep_num).replace(".md", "").lstrip("_")
    c_num = int(clip_num)
    total_duration = _probe_longform_duration(clean_ep)
    data = get_longform_all_chapter_mappings(clean_ep, total_duration)
    ch = data["chapters"].get(c_num, {"start": 0.0, "end": 0.0, "beats": [], "title": f"Part {c_num}"})

    mapped_words = _load_mapped_longform_words(clean_ep)
    lf_beats, omitted = [], []
    for b in ch["beats"]:
        sb = b["beat"]
        cls_name = sb.get("class_name", "")
        if b["omitted"]:
            omitted.append({"class_name": cls_name, "visual_summary": sb.get("visual_summary", ""),
                            "text": sb.get("text", ""), "reason": "Short-only teaser hook (spoken later inside the chapter)"})
            continue
        lf_st, lf_en = b["longform_start"], b["longform_end"]
        spoken = sb.get("text", "")
        if mapped_words:
            bw = [w["word"] for w in mapped_words if lf_st <= 0.5 * (w["start"] + w["end"]) < lf_en]
            if bw:
                spoken = " ".join(bw)
        lf_beats.append({
            "index": len(lf_beats) + 1,
            "short_index": sb.get("index"),
            "clip_num": c_num,
            "class_name": cls_name,
            "title": sb.get("title", cls_name),
            "category": sb.get("category", "AI AUTONOMY"),
            "visual_summary": sb.get("visual_summary", ""),
            "user_notes": sb.get("user_notes", ""),
            "longform_start": lf_st,
            "longform_end": lf_en,
            "duration": round(lf_en - lf_st, 2),
            "short_video_start": sb.get("video_start", 0.0),
            "short_video_end": sb.get("video_end", 0.0),
            "text": spoken,
            "mp4_exists": sb.get("mp4_exists", True),
            "beat_video_url": f"/api/podcast/beat_video?clip_num={c_num}&class_name={cls_name}",
            "code": sb.get("code", ""),
            "visual_source": ch.get("visual_source", "manim"),
        })

    return {
        "ep_num": clean_ep,
        "clip_num": c_num,
        "title": ch.get("title", f"Part {c_num}"),
        "py_file": f"archetypes/clip_{c_num:02d}_gemini_scenes.py",
        "chapter_start": ch["start"],
        "chapter_end": ch["end"],
        "scenes_count": len(lf_beats),
        "beats": lf_beats,
        "omitted_beats": omitted,
        "visual_source": ch.get("visual_source", "manim"),
        "locked": ch.get("visual_source") == "mosaic",
        "mosaic_file": os.path.basename((ch.get("mosaic_body") or {}).get("path", "")) or None,
    }
