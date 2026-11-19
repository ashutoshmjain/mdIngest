import os
import sys
import re
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_ROOT = os.path.dirname(SCRIPT_DIR)
ARCHETYPES_DIR = os.path.join(GITHUB_ROOT, "ddma", "archetypes")

def get_scene_classes(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    classes = re.findall(r"class\s+(Scene\w+)\s*\(", text)
    return classes

def compile_clip_scenes(clip_num):
    file_name = f"clip_{clip_num:02d}_gemini_scenes.py"
    file_path = os.path.join(ARCHETYPES_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"Clip {clip_num:02d}: File not found ({file_name})")
        return clip_num, 0, 0

    scene_classes = get_scene_classes(file_path)
    if not scene_classes:
        print(f"Clip {clip_num:02d}: No Scene classes found!")
        return clip_num, 0, 0

    video_dir = os.path.join(GITHUB_ROOT, "media", "videos", f"clip_{clip_num:02d}_gemini_scenes", "740p15")
    existing = set()
    if os.path.exists(video_dir):
        existing = {f[:-4] for f in os.listdir(video_dir) if f.endswith(".mp4") and not f.startswith("partial")}

    missing = [c for c in scene_classes if c not in existing]
    if not missing:
        print(f"[Clip {clip_num:02d}] ALREADY COMPLETE ({len(scene_classes)}/{len(scene_classes)} scenes).")
        return clip_num, len(scene_classes), len(scene_classes)

    print(f"\n[Clip {clip_num:02d}] Compiling {len(missing)} missing scenes (out of {len(scene_classes)}) sequentially with Manim...")
    t0 = time.time()

    # Run all missing scenes for this clip in a single Manim invocation
    cmd = [
        "manim", "-ql",
        "--format=mp4",
        "-r", "740,740",
        "--media_dir", os.path.join(GITHUB_ROOT, "media"),
        file_path
    ] + missing

    p = subprocess.run(cmd, cwd=ARCHETYPES_DIR, capture_output=True, text=True)

    # Check again how many were rendered; if batch stopped early due to one bad scene, compile remaining one by one!
    if os.path.exists(video_dir):
        existing = {f[:-4] for f in os.listdir(video_dir) if f.endswith(".mp4") and not f.startswith("partial")}
    still_missing = [c for c in scene_classes if c not in existing]

    if still_missing:
        print(f"  [Clip {clip_num:02d}] Batch stopped early ({len(still_missing)} left). Compiling remaining scenes individually...")
        for sc in still_missing:
            cmd_single = [
                "manim", "-ql",
                "--format=mp4",
                "-r", "740,740",
                "--media_dir", os.path.join(GITHUB_ROOT, "media"),
                file_path,
                sc
            ]
            res = subprocess.run(cmd_single, cwd=ARCHETYPES_DIR, capture_output=True, text=True)
            if res.returncode != 0:
                err_lines = [line for line in (res.stderr or "").splitlines() if "Error" in line or "Exception" in line]
                err_msg = err_lines[-1] if err_lines else "Unknown error"
                print(f"    [!] {sc} failed: {err_msg}")

    dur = time.time() - t0
    rendered_count = 0
    if os.path.exists(video_dir):
        rendered_count = len([f for f in os.listdir(video_dir) if f.endswith(".mp4") and not f.startswith("partial")])

    print(f"[Clip {clip_num:02d}] DONE: {rendered_count}/{len(scene_classes)} scenes ready ({dur:.1f}s)", flush=True)
    return clip_num, rendered_count, len(scene_classes)

def main():
    print("==================================================")
    print("   Sequential Manim Archetype Compiler (23 Clips) ")
    print("==================================================")
    
    t_start = time.time()
    clips_to_run = list(range(1, 24))
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if "-" in arg:
            s, e = map(int, arg.split("-"))
            clips_to_run = list(range(s, e + 1))
        elif "," in arg:
            clips_to_run = [int(x.strip()) for x in arg.split(",")]
        else:
            clips_to_run = [int(arg)]

    print(f"Running sequentially (1 worker, zero Windows file locking) for clips {clips_to_run}...", flush=True)

    results = []
    for c in clips_to_run:
        results.append(compile_clip_scenes(c))

    total_rendered = sum(r[1] for r in results)
    total_scenes = sum(r[2] for r in results)
    total_dur = time.time() - t_start

    print("\n==================================================")
    print(f"Sequential Compilation Complete!")
    print(f"Total Scenes Rendered: {total_rendered}/{total_scenes}")
    print(f"Total Elapsed Time: {total_dur:.1f}s ({total_dur/60:.2f} mins)")
    print("==================================================")

if __name__ == "__main__":
    main()
