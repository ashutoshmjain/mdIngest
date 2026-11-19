import os
import sys
import re
import json
import time
import math
import shutil
import subprocess
import av
from multiprocessing import Pool, cpu_count
from PIL import Image, ImageDraw, ImageFont

# Set up paths relative to github root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from longform_video_engine import map_timeline_with_stings_and_cuts

EP_NUM = "248"
AUDIO_PATH = os.path.join(GITHUB_ROOT, "src", "ddma", "docs", "episodes", EP_NUM, f"podcast_{EP_NUM}.mp3")
TRANS_PATH = os.path.join(GITHUB_ROOT, "src", "ddma", "docs", "episodes", EP_NUM, "transcription.json")
EDIT_PATH = os.path.join(GITHUB_ROOT, "src", "ddma", "docs", "episodes", EP_NUM, "podcast_edit.json")
PLAN_PATH = os.path.join(GITHUB_ROOT, "ddma", "projects", f"episode_{EP_NUM}", "plan.json")
ARCHETYPES_DIR = os.path.join(GITHUB_ROOT, "ddma", "archetypes")
MEDIA_VIDEOS_DIR = os.path.join(GITHUB_ROOT, "media", "videos")

CLIPS_DIR = os.path.join(GITHUB_ROOT, "ddma", "clips")
TEMP_CHUNKS_DIR = os.path.join(CLIPS_DIR, "temp_chunks")
FINAL_MASTER_MP4 = os.path.join(CLIPS_DIR, f"{EP_NUM}-longform-master.mp4")

def get_bezier_curve(p0, p1, p2, p3, steps=10):
    points = []
    for i in range(steps + 1):
        u = i / steps
        uu = 1 - u
        x = uu**3 * p0[0] + 3 * uu**2 * u * p1[0] + 3 * uu * u**2 * p2[0] + u**3 * p3[0]
        y = uu**3 * p0[1] + 3 * uu**2 * u * p1[1] + 3 * uu * u**2 * p2[1] + u**3 * p3[1]
        points.append((x, y))
    return points

def draw_vector_clip_mic(draw, cx, cy, scale=0.65, fill=(255, 255, 255)):
    capsule_pts = []
    capsule_pts.append((-10, -24))
    capsule_pts.extend(get_bezier_curve((-10, -24), (-10, -32), (10, -32), (10, -24))[1:])
    capsule_pts.append((10, 0))
    capsule_pts.extend(get_bezier_curve((10, 0), (10, 7), (-10, 7), (-10, 0))[1:])
    capsule_pts.append((-10, -24))

    cradle_pts = []
    cradle_pts.append((-14, -5))
    cradle_pts.extend(get_bezier_curve((-14, -5), (-14, 13), (14, 13), (14, -5))[1:])
    cradle_pts.append((16, -5))
    cradle_pts.extend(get_bezier_curve((16, -5), (16, 17), (-16, 17), (-16, -5))[1:])
    cradle_pts.append((-14, -5))

    stand_pts = [
        (-2, 15), (2, 15), (2, 23), (11, 23), (11, 26),
        (-11, 26), (-11, 23), (-2, 23)
    ]

    y_shift = 3
    for pts in [capsule_pts, cradle_pts, stand_pts]:
        scaled_pts = [(cx + x * scale, cy + (y + y_shift) * scale) for x, y in pts]
        draw.polygon(scaled_pts, fill=fill)

def find_system_fonts():
    candidates = [
        (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf"),
        ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
    ]
    for reg, bold in candidates:
        if os.path.exists(reg) and os.path.exists(bold):
            return reg, bold
    return None, None

def build_manim_scene_timeline(plan_data, total_duration):
    """
    Maps all compiled Manim MP4 scenes across the 23 clips onto the Longform Master timeline
    using exact audio-timestamp alignment (archetype_studio.get_longform_scene_intervals):
    every visual lands on the same spoken words as in the DDMA Short. Gaps are closed so the
    last visual persists (screen-never-empty), except for the welcome sting window.
    """
    if SCRIPT_DIR not in sys.path:
        sys.path.insert(0, SCRIPT_DIR)
    from archetype_studio import get_longform_scene_intervals
    return get_longform_scene_intervals(EP_NUM, total_duration)

def render_chunk_worker(args):
    chunk_idx, start_t, end_t, out_path, trans_segments, scene_intervals, fps = args
    t_start_chunk = time.time()
    num_frames = int(round((end_t - start_t) * fps))
    print(f"[{chunk_idx+1}] Starting chunk {start_t:.1f}s -> {end_t:.1f}s ({num_frames} frames)...", flush=True)

    f_reg, f_bold = find_system_fonts()
    font_host = ImageFont.truetype(f_bold or "arial.ttf", 20)
    font_caption = ImageFont.truetype(f_bold or "arial.ttf", 36)
    font_fine = ImageFont.truetype(f_reg or "arial.ttf", 15)
    font_badge = ImageFont.truetype(f_bold or "arial.ttf", 22)
    font_title_lg = ImageFont.truetype(f_bold or "arial.ttf", 60)
    font_sub_md = ImageFont.truetype(f_reg or "arial.ttf", 24)

    cmd_ffmpeg = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1920x1080",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "pipe:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-an",
        out_path
    ]

    proc = subprocess.Popen(cmd_ffmpeg, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    # Single-scene LRU cache in worker so only 1 Manim MP4 is decoded in RAM at a time
    cached_mp4_path = None
    cached_frames = []

    box_x = 590
    box_y = 260

    for i in range(num_frames):
        t = start_t + (i / fps)

        frame_img = Image.new("RGB", (1920, 1080), (0, 0, 0))
        draw = ImageDraw.Draw(frame_img)

        # 1. Centerpiece Display (drawn first so upper-canvas host strip & subtitles overlay cleanly)
        if 29.68 <= t <= 39.68:
            # Welcome Sting: Borderless Podcast Title Artwork Card
            cy = 560
            draw.text((960, cy - 170), "D E E P   D I V E   P O D C A S T", font=font_badge, fill=(180, 190, 205), anchor="mm")
            draw.text((960, cy - 110), f"E P I S O D E   {EP_NUM}", font=font_fine, fill=(140, 150, 165), anchor="mm")
            draw.text((960, cy - 35), "WHAT EXACTLY IS AI AUTONOMY?", font=font_title_lg, fill=(255, 255, 255), anchor="mm")
            draw.text((960, cy + 55), "The Architecture of Sovereign Intelligence • Research to Reality", font=font_sub_md, fill=(200, 210, 225), anchor="mm")
            draw.text((960, cy + 145), "HOSTED BY SATOSHA & SATOSHI", font=font_badge, fill=(160, 170, 185), anchor="mm")
            draw.text((960, cy + 200), f"deepdive.shutri.com/{EP_NUM}.html", font=font_fine, fill=(110, 120, 135), anchor="mm")
        else:
            # Pre-sting scene01 uses full 740x740 height (box_y=220); post-sting scenes keep top half blank for captions so shift up to box_y=110
            cur_box_y = 220 if t < 29.68 else 110
            cur_sc = next((s for s in scene_intervals if s["start"] <= t < s["end"]), None)
            if not cur_sc and scene_intervals:
                cur_sc = scene_intervals[-1] if t >= scene_intervals[-1]["end"] else scene_intervals[0]

            if cur_sc:
                is_mosaic = cur_sc.get("visual_source") == "mosaic"
                mp4_path = cur_sc["mp4"]
                cache_key = f"{mp4_path}:{cur_sc.get('src_offset', 0)}:{cur_sc.get('src_hold', 0)}" if is_mosaic else mp4_path
                if cache_key != cached_mp4_path:
                    cached_frames = []
                    if os.path.exists(mp4_path):
                        if is_mosaic:
                            src_st = max(0.0, float(cur_sc.get("src_offset", 0.0)))
                            src_hold = float(cur_sc.get("src_hold", src_st + 7.5))
                            src_dur = max(0.2, src_hold - src_st)
                            target_w = 416 if cur_sc.get("src_kind") == "vertical" else 740
                            target_h = 740
                            cmd = [
                                "ffmpeg", "-y", "-ss", f"{src_st:.3f}", "-i", mp4_path,
                                "-t", f"{src_dur:.3f}",
                                "-vf", f"scale={target_w}:{target_h}",
                                "-pix_fmt", "rgb24", "-f", "rawvideo",
                                "-v", "error", "pipe:1"
                            ]
                            try:
                                res = subprocess.run(cmd, capture_output=True, timeout=20)
                                raw = res.stdout
                                sz = target_w * target_h * 3
                                n = len(raw) // sz
                                cached_frames = [Image.frombytes("RGB", (target_w, target_h), raw[j*sz : (j+1)*sz]) for j in range(n)]
                            except Exception:
                                cached_frames = []
                        else:
                            try:
                                container = av.open(mp4_path)
                                for f_av in container.decode(video=0):
                                    img = f_av.to_image().convert("RGB")
                                    # Mask out the bold Archetype Title at y = -2.95 (pixel rows 622..672)
                                    # while keeping the thin footer line (y=679..680) and tiny metadata labels (y=691..701)
                                    ImageDraw.Draw(img).rectangle([(0, 622), (740, 672)], fill=(0, 0, 0))
                                    cached_frames.append(img)
                                container.close()
                            except Exception:
                                cached_frames = []
                    cached_mp4_path = cache_key

                if cached_frames:
                    sc_offset = max(0.0, t - cur_sc["start"])
                    sc_fps = cur_sc.get("fps", 25 if is_mosaic else 15)
                    f_idx = min(len(cached_frames) - 1, int(sc_offset * sc_fps))
                    if is_mosaic:
                        img = cached_frames[f_idx]
                        paste_x = (1920 - img.width) // 2
                        frame_img.paste(img, (paste_x, cur_box_y))
                        # Subtle footer line and labels: Left = Mosaic, Right = deepDive podcast
                        draw.line([(590, cur_box_y + 680), (1330, cur_box_y + 680)], fill=(51, 65, 85), width=1)
                        draw.text((600, cur_box_y + 700), "Mosaic", font=font_fine, fill=(100, 116, 139), anchor="lm")
                        draw.text((1320, cur_box_y + 700), "deepDive podcast", font=font_fine, fill=(100, 116, 139), anchor="rm")
                    else:
                        frame_img.paste(cached_frames[f_idx], (box_x, cur_box_y))

        # 2. Top Host Strip: SATOSHA — 🎙️ — SATOSHI (y=60)
        y_host = 60
        draw.text((860, y_host), "SATOSHA", font=font_host, fill=(226, 232, 240), anchor="ra")
        draw.text((1060, y_host), "SATOSHI", font=font_host, fill=(226, 232, 240), anchor="la")
        draw.line([(875, y_host), (935, y_host)], fill=(71, 85, 105), width=2)
        draw.line([(985, y_host), (1045, y_host)], fill=(71, 85, 105), width=2)

        is_mic_on = (t % 0.8) < 0.48
        mic_color = (255, 255, 255) if is_mic_on else (51, 65, 85)
        draw_vector_clip_mic(draw, 960, y_host, scale=0.65, fill=mic_color)

        # 3. Subtitles Karaoke (y=115..175)
        active_seg = next((s for s in trans_segments if s.get("start", 0) <= t <= s.get("end", 0) + 0.15), None)
        if active_seg and active_seg.get("words"):
            cur_words = active_seg["words"]
            w_lens = [font_caption.getbbox(w.get("word", "").strip() + " ")[2] - font_caption.getbbox(w.get("word", "").strip() + " ")[0] for w in cur_words]
            total_w = sum(w_lens)

            if total_w <= 1700:
                cx = (1920 - total_w) // 2
                cy = 115
                for w, wl in zip(cur_words, w_lens):
                    wt = w.get("word", "").strip() + " "
                    ws = float(w.get("start", 0))
                    we = float(w.get("end", ws + 0.3))
                    col = (255, 214, 10) if ws <= t <= we else (255, 255, 255) if t > we else (115, 115, 115)
                    draw.text((cx, cy), wt, font=font_caption, fill=col)
                    cx += wl
            else:
                half = len(cur_words) // 2
                w1 = sum(w_lens[:half])
                cx1 = (1920 - w1) // 2
                for w, wl in zip(cur_words[:half], w_lens[:half]):
                    wt = w.get("word", "").strip() + " "
                    ws = float(w.get("start", 0))
                    we = float(w.get("end", ws + 0.3))
                    col = (255, 214, 10) if ws <= t <= we else (255, 255, 255) if t > we else (115, 115, 115)
                    draw.text((cx1, 105), wt, font=font_caption, fill=col)
                    cx1 += wl
                w2 = sum(w_lens[half:])
                cx2 = (1920 - w2) // 2
                for w, wl in zip(cur_words[half:], w_lens[half:]):
                    wt = w.get("word", "").strip() + " "
                    ws = float(w.get("start", 0))
                    we = float(w.get("end", ws + 0.3))
                    col = (255, 214, 10) if ws <= t <= we else (255, 255, 255) if t > we else (115, 115, 115)
                    draw.text((cx2, 150), wt, font=font_caption, fill=col)
                    cx2 += wl

        proc.stdin.write(frame_img.tobytes())

    proc.stdin.close()
    proc.wait()
    dur_render = time.time() - t_start_chunk
    print(f"[{chunk_idx+1}] Finished in {dur_render:.1f}s ({num_frames/max(0.1, dur_render):.1f} fps)", flush=True)
    return out_path

WELCOME_SEGMENTS = [
    {"start": 29.80, "end": 31.50, "text": "Welcome to the Deep Dive.", "words": [
        {"word": "Welcome", "start": 29.80, "end": 30.22}, {"word": "to", "start": 30.22, "end": 30.50},
        {"word": "the", "start": 30.50, "end": 30.64}, {"word": "Deep", "start": 30.64, "end": 30.86},
        {"word": "Dive.", "start": 30.86, "end": 31.40}]},
    {"start": 31.60, "end": 33.50, "text": "I am Satosha and I am Satoshi.", "words": [
        {"word": "I", "start": 31.60, "end": 31.75}, {"word": "am", "start": 31.75, "end": 31.90},
        {"word": "Satosha", "start": 31.90, "end": 32.35}, {"word": "and", "start": 32.35, "end": 32.55},
        {"word": "I", "start": 32.55, "end": 32.70}, {"word": "am", "start": 32.70, "end": 32.85},
        {"word": "Satoshi.", "start": 32.85, "end": 33.35}]},
]


def _probe_duration(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    return float(p.stdout.strip()) if p.returncode == 0 and p.stdout.strip() else 0.0


def _keyframes_near(path, t, before=20.0, after=20.0):
    """Video keyframe (packet flag K) timestamps within [t-before, t+after]."""
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-read_intervals", f"{max(0.0, t - before)}%{t + after}",
                        "-show_entries", "packet=pts_time,flags", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    kfs = []
    for line in p.stdout.splitlines():
        parts = line.strip().split(",")
        if len(parts) >= 2 and "K" in parts[1]:
            try:
                kfs.append(float(parts[0]))
            except ValueError:
                pass
    return sorted(set(kfs))


def patch_longform_chapter(clip_num, ep_num=EP_NUM, log=print):
    """
    Fast chapter hot-patch: re-renders ONLY one chapter's window of the Longform Master
    (snapped outward to existing keyframes) and splices it in with stream copy:
        [0, k0) master  +  patch [k0, k1)  +  [k1, end) master   (+ original audio stream copy)
    Then replaces ddma/clips/<ep>-longform-master.mp4 and deepDive .../podcast_<ep>.mp4.
    Returns dict(success, start, end, elapsed, path | error).
    """
    t_all = time.time()
    if SCRIPT_DIR not in sys.path:
        sys.path.insert(0, SCRIPT_DIR)
    import archetype_studio
    canonical = os.path.join(GITHUB_ROOT, "src", "ddma", "docs", "episodes", ep_num, f"podcast_{ep_num}.mp4")
    master = canonical if os.path.exists(canonical) else FINAL_MASTER_MP4
    if not os.path.exists(master):
        return {"success": False, "error": "No Longform Master MP4 found - run a full render first."}
    total_duration = _probe_duration(master) or 3254.21

    data = archetype_studio.get_longform_all_chapter_mappings(ep_num, total_duration)
    ch = data["chapters"].get(int(clip_num))
    if not ch:
        return {"success": False, "error": f"Chapter {clip_num} not found in plan."}
    t0, t1 = float(ch["start"]), min(float(ch["end"]), total_duration)

    kf0 = [k for k in _keyframes_near(master, t0) if k <= t0 + 0.001]
    kf1 = [k for k in _keyframes_near(master, t1) if k >= t1 - 0.001]
    k0 = kf0[-1] if kf0 else 0.0
    k1 = kf1[0] if kf1 else total_duration
    if t1 >= total_duration - 0.5:
        k1 = total_duration
    log(f"[patch] Part {clip_num}: chapter {t0:.2f}-{t1:.2f}s -> keyframe window {k0:.2f}-{k1:.2f}s")

    fps = 25
    with open(TRANS_PATH, "r", encoding="utf-8") as f:
        trans_data = json.load(f)
    with open(EDIT_PATH, "r", encoding="utf-8") as f:
        edit_data = json.load(f)
    mapped_trans, _, _ = map_timeline_with_stings_and_cuts(trans_data, edit_data, total_duration)
    trans_segments = mapped_trans.get("segments", []) + [dict(s) for s in WELCOME_SEGMENTS]
    trans_segments.sort(key=lambda x: x.get("start", 0))

    scene_intervals = archetype_studio.get_longform_scene_intervals(ep_num, total_duration)
    c_scenes = [s for s in scene_intervals if s["end"] >= k0 - 5.0 and s["start"] <= k1 + 5.0]

    work = os.path.join(TEMP_CHUNKS_DIR, f"patch_{ep_num}_{int(clip_num):02d}")
    os.makedirs(work, exist_ok=True)
    patch_mp4 = os.path.join(work, "patch.mp4")
    head_mp4 = os.path.join(work, "head.mp4")
    tail_mp4 = os.path.join(work, "tail.mp4")
    out_mp4 = os.path.join(work, "spliced.mp4")

    t_r = time.time()
    # Render in 4 parallel sub-chunks, then concat (keeps the patch ~4x faster on long chapters)
    n_sub = 4 if (k1 - k0) > 40 else 1
    bounds = [k0 + (k1 - k0) * i / n_sub for i in range(n_sub + 1)]
    bounds = [round(round(b * fps) / fps, 4) for b in bounds]
    tasks = [(i, bounds[i], bounds[i + 1], os.path.join(work, f"sub_{i:02d}.mp4"), trans_segments, c_scenes, fps)
             for i in range(n_sub)]
    if n_sub > 1:
        with Pool(processes=min(n_sub, cpu_count())) as pool:
            subs = pool.map(render_chunk_worker, tasks)
    else:
        subs = [render_chunk_worker(tasks[0])]
    log(f"[patch] rendered {k1 - k0:.1f}s of video in {time.time() - t_r:.1f}s")

    def _ff(args):
        r = subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr[-600:])

    try:
        sub_list = os.path.join(work, "sub_list.txt")
        with open(sub_list, "w", encoding="utf-8") as f:
            for s in subs:
                f.write(f"file '{s.replace(chr(92), '/')}'\n")
        _ff(["-f", "concat", "-safe", "0", "-i", sub_list, "-c", "copy", patch_mp4])

        pieces = []
        if k0 > 0.01:
            _ff(["-i", master, "-map", "0:v:0", "-t", f"{k0:.4f}", "-c", "copy", head_mp4])
            pieces.append(head_mp4)
        pieces.append(patch_mp4)
        if k1 < total_duration - 0.05:
            _ff(["-ss", f"{k1:.4f}", "-i", master, "-map", "0:v:0", "-c", "copy", tail_mp4])
            pieces.append(tail_mp4)
        lst = os.path.join(work, "splice_list.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for pth in pieces:
                f.write(f"file '{pth.replace(chr(92), '/')}'\n")
        _ff(["-f", "concat", "-safe", "0", "-i", lst, "-i", master,
             "-map", "0:v:0", "-map", "1:a:0?", "-c", "copy", "-movflags", "+faststart", out_mp4])
    except Exception as e:
        return {"success": False, "error": f"Splice failed: {e}"}

    new_dur = _probe_duration(out_mp4)
    if abs(new_dur - total_duration) > 1.0:
        return {"success": False, "error": f"Spliced duration {new_dur:.2f}s differs from master {total_duration:.2f}s - aborted."}

    replaced = []
    for dst in {os.path.normcase(os.path.abspath(p)): p for p in [canonical, FINAL_MASTER_MP4]}.values():
        if not os.path.exists(os.path.dirname(dst)):
            continue
        try:
            shutil.copyfile(out_mp4, dst + ".tmp")
            os.replace(dst + ".tmp", dst)
            replaced.append(dst)
        except Exception as e:
            log(f"[patch] could not replace {dst}: {e}")
    elapsed = time.time() - t_all
    log(f"[patch] Part {clip_num} spliced into master in {elapsed:.1f}s ({len(replaced)} file(s) updated)")
    return {"success": bool(replaced), "clip_num": int(clip_num), "start": round(t0, 2), "end": round(t1, 2),
            "window": [round(k0, 2), round(k1, 2)], "elapsed": round(elapsed, 1), "paths": replaced,
            **({} if replaced else {"error": "Master file locked; could not replace."})}


def main():
    print(f"==================================================")
    print(f"  Longform Video Master Parallel Render & Concat  ")
    print(f"  Episode {EP_NUM} • 389 Manim Bespoke Scenes     ")
    print(f"==================================================")

    # 1. Load audio duration
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", AUDIO_PATH],
        capture_output=True, text=True
    )
    total_duration = float(p.stdout.strip()) if p.returncode == 0 and p.stdout.strip() else 3254.21
    print(f"Master Audio Duration: {total_duration:.2f}s ({total_duration/60:.2f} mins)")

    # 2. Load data
    with open(TRANS_PATH, "r", encoding="utf-8") as f:
        trans_data = json.load(f)
    with open(EDIT_PATH, "r", encoding="utf-8") as f:
        edit_data = json.load(f)
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    # 3. Build 389-scene Manim timeline
    scene_intervals = build_manim_scene_timeline(plan_data, total_duration)
    print(f"Mapped {len(scene_intervals)} rendered Manim MP4 scenes across {total_duration:.1f}s timeline")

    # 4. Map transcription with cuts & stings
    fps = 25
    mapped_trans, sting_intervals, _ = map_timeline_with_stings_and_cuts(trans_data, edit_data, total_duration)
    trans_segments = mapped_trans.get("segments", [])

    # Insert welcome sting speech segments (29.80s - 33.50s)
    welcome_segments = [
        {
            "start": 29.80,
            "end": 31.50,
            "text": "Welcome to the Deep Dive.",
            "words": [
                {"word": "Welcome", "start": 29.80, "end": 30.22},
                {"word": "to", "start": 30.22, "end": 30.50},
                {"word": "the", "start": 30.50, "end": 30.64},
                {"word": "Deep", "start": 30.64, "end": 30.86},
                {"word": "Dive.", "start": 30.86, "end": 31.40},
            ]
        },
        {
            "start": 31.60,
            "end": 33.50,
            "text": "I am Satosha and I am Satoshi.",
            "words": [
                {"word": "I", "start": 31.60, "end": 31.75},
                {"word": "am", "start": 31.75, "end": 31.90},
                {"word": "Satosha", "start": 31.90, "end": 32.35},
                {"word": "and", "start": 32.35, "end": 32.55},
                {"word": "I", "start": 32.55, "end": 32.70},
                {"word": "am", "start": 32.70, "end": 32.85},
                {"word": "Satoshi.", "start": 32.85, "end": 33.35},
            ]
        }
    ]
    trans_segments.extend(welcome_segments)
    trans_segments.sort(key=lambda x: x.get("start", 0))

    # 5. Partition timeline into chunks (8 chunks ~6.7 mins each)
    os.makedirs(TEMP_CHUNKS_DIR, exist_ok=True)
    num_chunks = 8
    chunk_dur = total_duration / num_chunks
    tasks = []

    for i in range(num_chunks):
        s_t = i * chunk_dur
        e_t = total_duration if i == num_chunks - 1 else (i + 1) * chunk_dur
        chunk_mp4 = os.path.join(TEMP_CHUNKS_DIR, f"chunk_{i:02d}.mp4")
        # Filter scenes overlapping this chunk with a small margin
        c_scenes = [s for s in scene_intervals if s["end"] >= s_t - 5.0 and s["start"] <= e_t + 5.0]
        tasks.append((i, s_t, e_t, chunk_mp4, trans_segments, c_scenes, fps))

    workers = min(4, cpu_count())
    print(f"Rendering {num_chunks} chunks in parallel across {workers} CPU workers...", flush=True)
    t0 = time.time()

    with Pool(processes=workers) as pool:
        chunk_outputs = pool.map(render_chunk_worker, tasks)

    t_render = time.time() - t0
    print(f"\nAll {num_chunks} chunks rendered in {t_render:.1f}s ({t_render/60:.2f} mins)!")

    # 6. Concatenate chunks and mux original master audio
    print("\nConcatenating chunks with FFmpeg concat demuxer & muxing master audio...")
    concat_list_path = os.path.join(TEMP_CHUNKS_DIR, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for ch_path in chunk_outputs:
            safe_p = ch_path.replace("\\", "/")
            f.write(f"file '{safe_p}'\n")

    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-i", AUDIO_PATH,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        FINAL_MASTER_MP4
    ]

    res = subprocess.run(cmd_concat, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error during concat: {res.stderr}")
        return

    total_time = time.time() - t0
    fsize_mb = os.path.getsize(FINAL_MASTER_MP4) / (1024 * 1024)

    print("\n==================================================")
    print(f"SUCCESS: Longform Master Video Rendered!")
    print(f"Path: {FINAL_MASTER_MP4}")
    print(f"Total Duration: {total_duration/60:.2f} mins")
    print(f"Total Wall Time: {total_time:.1f}s ({total_time/60:.2f} mins)")
    print(f"File Size: {fsize_mb:.2f} MB")
    print(f"Scenes Composited: {len(scene_intervals)} Bespoke Manim MP4s")
    print("==================================================")

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--patch":
        res = patch_longform_chapter(int(sys.argv[2]))
        print(json.dumps({k: v for k, v in res.items() if k != "paths"}))
    else:
        main()
