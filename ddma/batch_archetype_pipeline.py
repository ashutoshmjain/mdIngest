import os
import sys
import json
import time
import math
import subprocess
import urllib.request
import re
from concurrent.futures import ThreadPoolExecutor

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_ROOT = os.path.dirname(SCRIPT_DIR)
def get_ep_num():
    for i, arg in enumerate(sys.argv):
        if arg in ("--ep", "-e") and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return "249"

EP_NUM = get_ep_num()

def _repo_ddma_dir():
    """Clone-agnostic ddma dir: a deepDive checkout keeps code in <root>/ddma,
    a standalone ddma checkout IS the ddma dir (no <root>/ddma inside)."""
    d = os.path.join(GITHUB_ROOT, "ddma")
    return d if os.path.isdir(d) else GITHUB_ROOT

DDMA_DIR = _repo_ddma_dir()

SETTINGS_PATH = os.path.join(DDMA_DIR, "settings.json")

settings = {}
if os.path.exists(SETTINGS_PATH):
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except Exception as e:
        print(f"[WARNING] Failed reading settings.json: {e}", file=sys.stderr)
else:
    print(
        f"[NOTICE] settings.json not found at {SETTINGS_PATH}. "
        "Required keys (or env vars): gemini_api_key (GEMINI_API_KEY).",
        file=sys.stderr
    )

def _resolve_hub_root():
    """Workspace root, same semantics as the Curator resolver: env DD_HUB_ROOT
    -> settings.json dd_hub_root -> plain local <repo>/dd_hub default (loud)."""
    e = os.environ.get("DD_HUB_ROOT")
    if e and os.path.exists(e):
        return e
    cfg = settings.get("dd_hub_root") if isinstance(settings, dict) else None
    if cfg and os.path.exists(cfg):
        return cfg
    local_default = os.path.join(GITHUB_ROOT, "dd_hub")
    print(f"WARNING: DD_HUB_ROOT is unset and no dd_hub directory exists at any known location -- defaulting to plain local folder {local_default} (set DD_HUB_ROOT to your workspace to override).")
    return local_default

def _find_episodes_dir():
    """Plan/data live in the workspace (<hub>/episodes/); the repo's published
    copy (<repo>/src/ddma/docs/episodes/) is the read fallback."""
    hub = _resolve_hub_root()
    cands = [os.path.join(hub, "episodes"),
             os.path.join(GITHUB_ROOT, "src", "ddma", "docs", "episodes")]
    for c in cands:
        if os.path.isdir(c):
            return c
    return cands[0]

EPISODES_DIR = _find_episodes_dir()

PLAN_PATH = os.path.join(EPISODES_DIR, EP_NUM, "plan.json")
if not os.path.exists(PLAN_PATH):
    PLAN_PATH = os.path.join(DDMA_DIR, "projects", f"episode_{EP_NUM}", "plan.json")

TRANS_PATH = os.path.join(EPISODES_DIR, EP_NUM, "transcription.json")
EDIT_PATH = os.path.join(EPISODES_DIR, EP_NUM, "podcast_edit.json")
AUDIO_PATH = os.path.join(EPISODES_DIR, EP_NUM, f"podcast_{EP_NUM}.mp3")
ARCHETYPES_DIR = os.path.join(DDMA_DIR, "archetypes")
CLIPS_DIR = os.path.join(DDMA_DIR, "clips")
TEMP_CHUNKS_DIR = os.path.join(CLIPS_DIR, "temp_chunks")

os.makedirs(ARCHETYPES_DIR, exist_ok=True)
os.makedirs(TEMP_CHUNKS_DIR, exist_ok=True)

API_KEY = settings.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")

PRIMARY_MODELS = [
    "models/gemini-3.5-flash-lite",
    "models/gemini-flash-lite-latest",
    "models/gemini-3.5-flash"
]

def call_gemini_with_fallback(payload):
    headers = {"Content-Type": "application/json"}
    for m in PRIMARY_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/{m}:generateContent?key={API_KEY}"
        for attempt in range(2):
            try:
                t0 = time.time()
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=45) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                t_gen = time.time() - t0
                return res_data, m, t_gen
            except Exception as e:
                print(f"    [{m}] Attempt {attempt+1} error: {e}. Backing off 4s...")
                time.sleep(4)
    return None, None, 0

SYSTEM_PROMPT = """You are an elite Manim Community Edition (ManimCE) Python developer following strict pedagogical and visual rules:
1. PURE MONOCHROME NOIR WITH FUNCTIONAL ACCENT:
   Every stroke, line, and figure is pure shining white (#FFFFFF) on pure glossy black (#000000). Fill opacities between 0.05 and 1.0. Functional spoken highlight accents may use Gold (#FFD700). ZERO other colors (no blue, green, brown, red, or orange).
2. CANVAS CONFIGURATION:
   config.pixel_width = 740
   config.pixel_height = 740
   config.frame_width = 8.0
   config.frame_height = 8.0
   config.background_color = "#000000"
3. STRICT INVARIANT: NO ARCHETYPE TITLES EVER:
   Do NOT create a scene title or chapter heading at the top or bottom of the canvas. The upper canvas y in [0.5, 3.5] must remain 100% clear for spoken karaoke captions, and the bottom area above the footer line must remain uncluttered.
4. BOTTOM FOOTER BAR & META LABELS:
   footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#334155", stroke_width=1.5).move_to(DOWN * 3.35)
   footer_line.set_opacity(0.6)
   left_text = Text(ARCHETYPE_NAME, font="Arial", weight=NORMAL, font_size=10, color="#64748b").next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
   right_text = Text("deepDive podcast", font="Arial", weight=NORMAL, font_size=10, color="#64748b").next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
   self.add(footer_line, left_text, right_text)
   Never display titles, episode numbers, or scene names in the footer bar. Only Archetype Name on left and 'deepDive podcast' on right in #64748b.
5. "SUPER DUMB & LITERAL" FIGURATIVE PEDAGOGY:
   Directly and figuratively illustrate the primary spoken words. No secondary/tertiary abstract speculation.
   Draw bold figurative objects: robots, balance scales, dollar signs, checkbooks, electric plugs, power meters, servers, cellular walls, arrows, intake pipes.
6. SAFE AREA:
   All visual illustrations MUST be centered vertically and horizontally within x in [-3.2, 3.2] and y in [-2.5, 0.4].
7. TIMING:
   Each scene must be constructed to take EXACTLY the requested run_time (e.g. 7-8s) using smooth, snappy animations.
8. Use only Line, Circle, Rectangle, RoundedRectangle, Polygon, Arc, Arrow, Text, VGroup, DashedLine, DoubleArrow.
Return ONLY valid Python code inside a ```python ... ``` block.
"""

SHIMS_HEADER = """from manim import *
import numpy as np

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

def get_footer_and_title(scene, title_str, category_str):
    title = VGroup()
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#334155", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.6)
    left_text = Text(category_str, font="Arial", weight=NORMAL, font_size=10, color="#64748b").next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("deepDive podcast", font="Arial", weight=NORMAL, font_size=10, color="#64748b").next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    return title, footer_line, left_text, right_text
"""

def extract_clip_transcript_beats(clip_data, target_beat_duration=7.5):
    """
    Slices a clip's speech segments into discrete ~7.5s micro-beats for prompting Gemini.
    """
    words = clip_data.get("_caption_words", [])
    if not words:
        try:
            import ddma
            words = ddma.extract_clip_words(clip_data, plan_file=PLAN_PATH)
        except Exception:
            pass
    if not words:
        seg_texts = [s.get("text", "") for s in clip_data.get("segments", []) if s.get("type") == "audio"]
        full_text = " ".join(seg_texts)
        words = [{"word": w, "start": i*0.4, "end": (i+1)*0.4} for i, w in enumerate(full_text.split())]

    if not words:
        return []

    c_start = float(clip_data.get("start", 0.0))
    c_end = float(clip_data.get("end", c_start + 120.0))
    total_dur = c_end - c_start

    num_beats = max(1, int(round(total_dur / target_beat_duration)))
    beat_dur = total_dur / num_beats

    is_relative_words = bool(words and float(words[0].get("start", 0)) < (c_start / 2) if c_start > 10 else False)

    beats = []
    for b_idx in range(num_beats):
        b_st = c_start + b_idx * beat_dur
        b_en = c_start + (b_idx + 1) * beat_dur
        if is_relative_words:
            w_st, w_en = b_idx * beat_dur, (b_idx + 1) * beat_dur
            b_words = [w["word"] for w in words if w_st <= float(w.get("start", 0)) < w_en]
        else:
            b_words = [w["word"] for w in words if b_st <= float(w.get("start", 0)) < b_en]
        b_text = " ".join(b_words).strip()
        if not b_text:
            b_text = f"Discussion on {clip_data.get('title', 'AI Autonomy')}"
        beats.append({
            "index": b_idx + 1,
            "start": round(b_st, 2),
            "end": round(b_en, 2),
            "duration": round(beat_dur, 1),
            "text": b_text
        })
    return beats

def generate_clip_code(clip_num, force=False):
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)

    if clip_num < 1 or clip_num > len(plan):
        print(f"Error: Invalid clip number {clip_num}")
        return None

    out_file = os.path.join(ARCHETYPES_DIR, f"clip_{clip_num:02d}_gemini_scenes.py")
    if not force and os.path.exists(out_file) and os.path.getsize(out_file) > 5000:
        print(f"Clip {clip_num:02d} already generated ({os.path.getsize(out_file)} bytes). Skipping.")
        return out_file

    clip = plan[clip_num - 1]
    beats = extract_clip_transcript_beats(clip)
    print(f"\n--- Clip {clip_num:02d}: '{clip.get('title')}' ({len(beats)} micro-beats, dur={clip.get('duration'):.1f}s) ---")

    # Sub-batches of 7 beats to stay well within output token budget
    batch_size = 7
    all_clean_scenes = []

    for batch_i in range(0, len(beats), batch_size):
        sub_beats = beats[batch_i:batch_i + batch_size]
        sub_num = (batch_i // batch_size) + 1
        total_sub = (len(beats) + batch_size - 1) // batch_size
        print(f"  [Clip {clip_num:02d}] Calling Gemini for Part {sub_num}/{total_sub} (beats {sub_beats[0]['index']}..{sub_beats[-1]['index']})...")

        prompt_items = []
        for b in sub_beats:
            scene_name = f"Scene{clip_num:02d}_{b['index']:02d}"
            prompt_items.append(
                f"{b['index']}. {scene_name} (Duration {b['duration']}s):\n"
                f"   Spoken Dialogue: \"{b['text']}\"\n"
                f"   Design a literal, bold figurative white vector cartoon illustrating these exact words (pure white #FFFFFF on #000000, footer: Archetype: KineticVector left, deepDive podcast right, strictly NO titles)."
            )

        user_prompt = f"""Generate Manim Community Edition Scene classes for Part {sub_num} of Clip {clip_num:02d} ('{clip.get('title')}'):\n\n""" + "\n\n".join(prompt_items)

        payload = {
            "contents": [{"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\n" + user_prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192}
        }

        res_data, used_model, t_gen = call_gemini_with_fallback(payload)
        if not res_data or "candidates" not in res_data:
            print(f"  [Clip {clip_num:02d}] Failed to get response for Part {sub_num}")
            continue

        print(f"  [Clip {clip_num:02d}] Part {sub_num} generated by {used_model} in {t_gen:.2f}s!")
        time.sleep(2) # brief delay between calls

        text = res_data["candidates"][0]["content"]["parts"][0]["text"]
        for line in text.splitlines():
            line_s = line.strip()
            if line_s.startswith("```") or line_s.startswith("from manim import") or line_s.startswith("import numpy") or line_s.startswith("config."):
                continue
            all_clean_scenes.append(line)

    final_code = SHIMS_HEADER + "\n\n" + "\n".join(all_clean_scenes)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(final_code)

    # Save metadata mapping for chunk renderer
    meta_file = os.path.join(ARCHETYPES_DIR, f"clip_{clip_num:02d}_meta.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({"clip_num": clip_num, "title": clip.get("title"), "beats": beats}, f, indent=2)

    print(f"Saved: {out_file} ({len(final_code)} chars)")
    return out_file

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--generate-code":
            target = sys.argv[2] if len(sys.argv) > 2 else "all"
            clip_list = []
            if target == "all":
                clip_list = list(range(1, 24))
            elif "-" in target:
                start_c, end_c = map(int, target.split("-"))
                clip_list = list(range(start_c, end_c + 1))
            elif "," in target:
                clip_list = [int(x.strip()) for x in target.split(",")]
            else:
                clip_list = [int(target)]

            force_flag = "--force" in sys.argv
            for c_num in clip_list:
                generate_clip_code(c_num, force=force_flag)
            print("Batch generation completed!")
    else:
        print("Usage: python batch_archetype_pipeline.py --generate-code <clip_num|all|3-23>")
