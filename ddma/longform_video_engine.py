import os
import sys
import math
import json
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont
import widescreen_infographics as wsi
from manim_video_provider import ManimSceneReader

def get_artifact_chyron_tag(sc, is_intro=False, is_closure=False, episode_num="248"):
    if is_intro:
        return f"[ INTRO: Curriculum Roadmap ]  •  Ep {episode_num}"
    if is_closure:
        return f"[ OUTRO: Next Module Preview ]  •  Ep {episode_num}"
    
    archetype = sc.get("archetype", "") if isinstance(sc, dict) else ""
    title = (sc.get("title", "") if isinstance(sc, dict) else "").strip()
    
    # 15 Super Dumb Cartoon Animations
    mapping = {
        "dripping_kitchen_tap": "[ ANIMATION: Dripping Kitchen Tap ]",
        "perishable_inventory_digital_jar": "[ ANIMATION: Dripping Kitchen Tap ]",
        "tap_faucet_vs_gpu_hourglass": "[ ANIMATION: Dripping Kitchen Tap ]",
        "melting_ice_cream_cone": "[ ANIMATION: Melting Ice Cream Cone ]",
        "perishable_ice_cream": "[ ANIMATION: Melting Ice Cream Cone ]",
        "cash_bonfire": "[ ANIMATION: Burning Cash Bonfire ]",
        "burning_dollar_bills": "[ ANIMATION: Burning Cash Bonfire ]",
        "flying_passenger_jet": "[ ANIMATION: Flying Passenger Jet ]",
        "paper_airplanes_globe": "[ ANIMATION: Paper Airplanes Around Globe ]",
        "empty_bistro_waiter": "[ ANIMATION: Empty Bistro & Lonely Waiter ]",
        "flat_pricing_bistro": "[ ANIMATION: Empty Bistro & Lonely Waiter ]",
        "airport_boarding_gate": "[ ANIMATION: Airport Boarding Gate ]",
        "yellow_forklift_cargo": "[ ANIMATION: Little Yellow Forklift ]",
        "vip_first_class_lounge": "[ ANIMATION: VIP First Class Lounge ]",
        "robot_empty_pockets_bank": "[ ANIMATION: Robot With Inside-Out Pockets ]",
        "nightclub_robot_bouncer": "[ ANIMATION: Nightclub Robot Bouncer ]",
        "unhooking_velvet_rope": "[ ANIMATION: Unhooking Velvet Rope ]",
        "robot_hand_throttle_lever": "[ ANIMATION: Robot Hand On Throttle ]",
        "upstairs_breaker_basement_kid": "[ ANIMATION: Upstairs Breaker vs Basement Kid ]",
        "rocket_ship_cosmos": "[ ANIMATION: Rocket Ship Soaring Into Space ]",
        # Historical Module 1 & 2 animations
        "robot_in_wilderness": "[ ANIMATION: Robot in Wilderness ]",
        "energy_furnace_dam": "[ ANIMATION: Energy Furnace & Hydro Dam ]",
        "datacenter_racks": "[ ANIMATION: High-Density Datacenter Racks ]",
        "bank_vault_lightning_wallet": "[ ANIMATION: Bank Vault vs Lightning Wallet ]",
        # Dynamic Slides (strictly 1 per module)
        "formula_derivation_card": "[ DYNAMIC SLIDE: Algorithmic Yield Management ]",
        # Authentic Quotes
        "academic_paper_callout": "[ QUOTE: The Bill-Paying Threshold ]",
        "quote_card": "[ QUOTE: The Bill-Paying Threshold ]",
    }
    
    if archetype in mapping:
        return mapping[archetype]
    elif "slide" in archetype or "formula" in archetype:
        return f"[ DYNAMIC SLIDE: {title if title else 'Formula Proof'} ]"
    elif "quote" in archetype or "callout" in archetype:
        return f"[ QUOTE: {title if title else 'Foundational Citation'} ]"
    else:
        clean_title = title if title else (archetype.replace("_", " ").title() if archetype else "Scene")
        return f"[ ANIMATION: {clean_title} ]"



def _format_time(secs):
    if secs is None or math.isnan(secs):
        return "00:00"
    total_secs = max(0, int(round(secs)))
    hours = total_secs // 3600
    mins = (total_secs % 3600) // 60
    remaining_secs = total_secs % 60
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{remaining_secs:02d}"
    return f"{mins:02d}:{remaining_secs:02d}"


def _load_horizontal_fonts():
    """Load high-legibility clean fonts for 1080p horizontal layout."""
    candidates_bold = [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
    ]
    candidates_reg = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    candidates_mono = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\consolab.ttf",
    ]

    path_bold = next((c for c in candidates_bold if os.path.exists(c)), None)
    path_reg = next((c for c in candidates_reg if os.path.exists(c)), None)
    path_mono = next((c for c in candidates_mono if os.path.exists(c)), None)

    fonts = {}
    for size in (14, 16, 18, 20, 22, 24, 26, 28, 32, 36, 38, 40, 42, 48, 52, 60, 68):
        try:
            fonts[f"bold_{size}"] = ImageFont.truetype(path_bold, size) if path_bold else ImageFont.load_default()
        except Exception:
            fonts[f"bold_{size}"] = ImageFont.load_default()
        try:
            fonts[f"reg_{size}"] = ImageFont.truetype(path_reg, size) if path_reg else ImageFont.load_default()
        except Exception:
            fonts[f"reg_{size}"] = ImageFont.load_default()
        try:
            fonts[f"mono_{size}"] = ImageFont.truetype(path_mono, size) if path_mono else ImageFont.load_default()
        except Exception:
            fonts[f"mono_{size}"] = ImageFont.load_default()

    # Ultra Mobile-First Typography Floors (One notch higher: floor is 24px)
    fonts["bold_14"] = fonts.get("bold_24", fonts.get("bold_26"))
    fonts["bold_16"] = fonts.get("bold_26", fonts.get("bold_28"))
    fonts["bold_18"] = fonts.get("bold_30", fonts.get("bold_32"))
    fonts["bold_20"] = fonts.get("bold_28", fonts.get("bold_26"))
    fonts["bold_22"] = fonts.get("bold_26", fonts.get("bold_24"))
    fonts["mono_12"] = fonts.get("mono_22", fonts.get("mono_24"))
    fonts["mono_14"] = fonts.get("mono_22", fonts.get("mono_24"))
    fonts["mono_16"] = fonts.get("mono_24", fonts.get("mono_26"))
    fonts["mono_20"] = fonts.get("mono_22", fonts.get("mono_24"))
    fonts["reg_14"] = fonts.get("reg_24", fonts.get("reg_26"))
    fonts["reg_16"] = fonts.get("reg_24", fonts.get("reg_26"))
    fonts["reg_18"] = fonts.get("reg_28", fonts.get("reg_26"))
    return fonts


def map_timeline_with_stings_and_cuts(transcription_data, edit_data=None, total_source_dur=0.0):
    """
    Computes exact master audio timeline mapping taking into account
    speech cuts and inserted music stings from podcast_edit.json.
    Returns:
      (mapped_transcription_data, sting_intervals, master_total_duration)
    """
    if not edit_data:
        # No cuts or stings: return original transcription as is
        return transcription_data, [], total_source_dur

    raw_cuts = edit_data.get("cuts", [])
    valid_cuts = []
    for c in raw_cuts:
        try:
            cs = max(0.0, float(c.get("start", 0.0)))
            ce = float(c.get("end", 0.0))
            if ce > cs + 0.05:
                valid_cuts.append((cs, ce))
        except (ValueError, TypeError):
            continue
    valid_cuts.sort(key=lambda x: x[0])

    merged_cuts = []
    for cs, ce in valid_cuts:
        if not merged_cuts:
            merged_cuts.append([cs, ce])
        else:
            prev = merged_cuts[-1]
            if cs <= prev[1] + 0.05:
                prev[1] = max(prev[1], ce)
            else:
                merged_cuts.append([cs, ce])

    # Speech duration after cuts
    speech_dur = total_source_dur
    if merged_cuts and total_source_dur > 0:
        total_cut_time = sum(ce - cs for cs, ce in merged_cuts)
        speech_dur = max(1.0, total_source_dur - total_cut_time)

    # Valid stings sorted by orig_at
    raw_stings = edit_data.get("stings", [])
    valid_stings = []
    for s in raw_stings:
        try:
            at_val = float(s.get("at", 0.0))
            dur_val = float(s.get("duration", 7.0))
            if dur_val <= 0:
                dur_val = 7.0
            valid_stings.append({
                "orig_at": at_val,
                "file": s.get("music_file", ""),
                "duration": dur_val,
                "title": s.get("music_file", "").split(".")[0].replace("_", " ")
            })
        except (ValueError, TypeError):
            continue
    valid_stings.sort(key=lambda x: x["orig_at"])

    # Compute adj_at for stings after speech cuts
    for vs in valid_stings:
        t_orig = vs["orig_at"]
        shift = 0.0
        for cs, ce in merged_cuts:
            if ce <= t_orig:
                shift += (ce - cs)
            elif cs < t_orig < ce:
                shift += (t_orig - cs)
        vs["adj_at"] = max(0.0, t_orig - shift)

    # Separate midrolls from outro
    midrolls = []
    outro_sting = None
    for vs in valid_stings:
        is_outro = (vs["adj_at"] >= speech_dur - 3.0) or ("conclusion" in vs["file"] and vs["adj_at"] >= speech_dur - 45.0)
        if is_outro and outro_sting is None:
            outro_sting = vs
        else:
            midrolls.append(vs)

    split_points = []
    filtered_midrolls = []
    last_pt = 0.0
    for vs in midrolls:
        pt = vs["adj_at"]
        if pt > last_pt + 1.0 and pt < speech_dur - 1.0:
            split_points.append(pt)
            filtered_midrolls.append(vs)
            last_pt = pt

    slice_ranges = []
    cur = 0.0
    for pt in split_points:
        slice_ranges.append((cur, pt))
        cur = pt
    slice_ranges.append((cur, speech_dur))

    slice_master_ranges = []
    sting_intervals = []
    t_cursor = 0.0

    s0_start, s0_end = slice_ranges[0]
    s0_dur = s0_end - s0_start
    slice_master_ranges.append((0.0, s0_dur, s0_start, s0_end))
    t_cursor += s0_dur

    for i, sting in enumerate(filtered_midrolls):
        t_sting_start = t_cursor + 0.2
        dur_sting = sting["duration"]
        t_next_speech = max(t_cursor, t_sting_start + dur_sting - 1.0)
        sting_intervals.append({
            "start": round(t_sting_start, 2),
            "end": round(t_next_speech, 2),
            "file": sting["file"],
            "title": sting["title"]
        })
        nxt_start, nxt_end = slice_ranges[i + 1]
        nxt_dur = nxt_end - nxt_start
        slice_master_ranges.append((round(t_next_speech, 2), round(t_next_speech + nxt_dur, 2), nxt_start, nxt_end))
        t_cursor = t_next_speech + nxt_dur

    if outro_sting:
        t_outro_start = t_cursor + 0.2
        dur_outro = outro_sting["duration"]
        sting_intervals.append({
            "start": round(t_outro_start, 2),
            "end": round(t_outro_start + dur_outro, 2),
            "file": outro_sting["file"],
            "title": "DEEP DIVE CONCLUSION"
        })
        t_cursor = t_outro_start + dur_outro

    master_total_dur = t_cursor

    def map_raw_time(raw_t):
        if raw_t is None:
            return None
        # Check if cut out
        for cs, ce in merged_cuts:
            if cs <= raw_t <= ce:
                return None
        # Shift past previous cuts
        shift = 0.0
        for cs, ce in merged_cuts:
            if ce <= raw_t:
                shift += (ce - cs)
        t_stitched = max(0.0, raw_t - shift)

        # Locate slice
        for m_start, m_end, s_start, s_end in slice_master_ranges:
            if s_start <= t_stitched <= s_end + 0.001:
                offset = t_stitched - s_start
                return round(m_start + offset, 2)
        # Fallback to end
        if slice_master_ranges:
            last = slice_master_ranges[-1]
            return round(last[1], 2)
        return round(t_stitched, 2)

    # Remap transcription segments and words
    orig_segments = transcription_data.get("segments", []) if isinstance(transcription_data, dict) else []
    mapped_segments = []

    for seg in orig_segments:
        s_s = map_raw_time(float(seg.get("start", 0.0)))
        s_e = map_raw_time(float(seg.get("end", 0.0)))
        if s_s is None or s_e is None or s_e <= s_s:
            continue

        raw_words = seg.get("words", [])
        mapped_words = []
        if raw_words:
            for w in raw_words:
                ws = map_raw_time(float(w.get("start", 0.0)))
                we = map_raw_time(float(w.get("end", 0.0)))
                if ws is not None and we is not None and we >= ws:
                    mapped_words.append({
                        "word": w.get("word", ""),
                        "start": ws,
                        "end": we
                    })
        else:
            w_list = seg.get("text", "").split()
            dur_w = max(0.1, (s_e - s_s) / max(1, len(w_list)))
            mapped_words = [
                {"word": w, "start": round(s_s + i * dur_w, 2), "end": round(s_s + (i + 1) * dur_w, 2)}
                for i, w in enumerate(w_list)
            ]

        mapped_segments.append({
            "start": s_s,
            "end": s_e,
            "text": seg.get("text", "").strip(),
            "words": mapped_words
        })

    mapped_transcription = dict(transcription_data) if isinstance(transcription_data, dict) else {}
    mapped_transcription["segments"] = mapped_segments

    return mapped_transcription, sting_intervals, master_total_dur


def classify_audio_speakers_fast(audio_path, segments, cached_path=None):
    """
    Ultra-fast in-memory classification of speech segments into Satosha (Male, F0 <= 140Hz)
    and Satoshi (Female, F0 >= 170Hz) using YIN fundamental pitch tracking.
    Applies YIN cumulative mean normalized difference, energy gating,
    and turn hysteresis ('When in doubt, DO NOT SWITCH').
    """
    if cached_path and os.path.exists(cached_path):
        try:
            with open(cached_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) == len(segments):
                    return data
        except Exception:
            pass

    classified = []
    if not segments or not audio_path or not os.path.exists(audio_path):
        for s in segments:
            c = dict(s)
            c["speaker"] = "satosha"
            classified.append(c)
        return classified

    import numpy as np

    print(f"[SPEAKER-DIARIZATION] Multi-window YIN pitch profiling across {len(segments)} segments...")
    try:
        cmd = ["ffmpeg", "-v", "error", "-i", audio_path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        pcm = np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32)
    except Exception as e:
        print(f"[SPEAKER-DIARIZATION] Audio decode error: {e}")
        pcm = np.array([], dtype=np.float32)

    def yin_pitch(sig, sr=16000, f_min=75, f_max=300, threshold=0.15):
        tau_min = int(sr / f_max)
        tau_max = int(sr / f_min)
        w_len = len(sig) // 2
        if w_len < tau_max:
            return 0.0
        x = sig[:w_len]
        d = np.zeros(tau_max + 1)
        x_sq = np.sum(x**2)
        for tau in range(1, tau_max + 1):
            x_tau = sig[tau:tau + w_len]
            d[tau] = x_sq + np.sum(x_tau**2) - 2 * np.dot(x, x_tau)
        d_prime = np.zeros(tau_max + 1)
        d_prime[0] = 1.0
        running_sum = 0.0
        for tau in range(1, tau_max + 1):
            running_sum += d[tau]
            if running_sum > 0:
                d_prime[tau] = d[tau] / (running_sum / tau)
            else:
                d_prime[tau] = 1.0
        tau_found = 0
        for tau in range(tau_min, tau_max):
            if d_prime[tau] < threshold:
                while tau + 1 < tau_max and d_prime[tau + 1] < d_prime[tau]:
                    tau += 1
                tau_found = tau
                break
        if tau_found > 0:
            return sr / float(tau_found)
        return 0.0

    current_spk = "satosha"
    win = 1024
    hop = 1024

    for s in segments:
        c = dict(s)
        st = float(s.get("start", 0.0))
        et = float(s.get("end", 0.0))
        dur = et - st
        st_idx = int(st * 16000)
        et_idx = int(et * 16000)
        seg_pcm = pcm[st_idx:et_idx]

        pitches = []
        max_hops = min(12, max(1, (len(seg_pcm) - win) // hop))
        for i in range(max_hops):
            w = seg_pcm[i * hop:i * hop + win]
            if len(w) < win or np.sqrt(np.mean(w**2)) < 1000:
                continue
            p = yin_pitch(w, threshold=0.15)
            if p > 0:
                pitches.append(p)

        candidate = None
        if len(pitches) >= 4:
            med_f0 = float(np.median(pitches))
            if med_f0 <= 140.0:
                candidate = "satoshi"  # Male: Satoshi (Gold / Right)
            elif med_f0 >= 170.0:
                candidate = "satosha"  # Female: Satosha (Cyan / Left)

        # User rule: "When in doubt, DO NOT SWITCH"
        if candidate and candidate != current_spk:
            if len(pitches) >= 6 or dur >= 2.0:
                current_spk = candidate

        c["speaker"] = current_spk
        classified.append(c)

        # 5-Second Sustained Speech Hysteresis Filter:
    # Merges short conversational interjections (<5.0s, e.g. "aha", "yeah", "right")
    # into the prevailing sustained speaker run.
    if classified:
        runs = []
        cur_run = []
        for s in classified:
            if not cur_run or cur_run[0].get("speaker") == s.get("speaker"):
                cur_run.append(s)
            else:
                runs.append(cur_run)
                cur_run = [s]
        if cur_run:
            runs.append(cur_run)

        smoothed = []
        stable_spk = runs[0][0].get("speaker", "satoshi")
        for r in runs:
            r_dur = float(r[-1].get("end", 0.0)) - float(r[0].get("start", 0.0))
            r_spk = r[0].get("speaker", "satoshi")
            if r_dur >= 5.0 and r_spk != stable_spk:
                stable_spk = r_spk
            for s in r:
                s["speaker"] = stable_spk
                smoothed.append(s)
        classified = smoothed

    if cached_path:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(cached_path)), exist_ok=True)
            with open(cached_path, "w", encoding="utf-8") as f:
                json.dump(classified, f, indent=2)
        except Exception:
            pass

    return classified


def load_or_create_episode_cover(clean_id, episode_title="Deep Dive Episode", episode_num="248", candidate_paths=None, target_size=(1080, 1080)):
    """
    Discovers episode cover art from disk, or generates a high-end Dan Koe
    dark minimalist cover card (1080x1080).
    """
    if candidate_paths:
        for p in candidate_paths:
            if p and os.path.exists(p):
                try:
                    img = Image.open(p).convert("RGB")
                    # Center crop and fit into target_size
                    w, h = img.size
                    min_dim = min(w, h)
                    left = (w - min_dim) // 2
                    top = (h - min_dim) // 2
                    cropped = img.crop((left, top, left + min_dim, top + min_dim))
                    resized = cropped.resize(target_size, Image.Resampling.LANCZOS)
                    return resized
                except Exception:
                    pass

    # Dynamic Dan Koe Aesthetic Cover Generation
    w, h = target_size
    img = Image.new("RGB", (w, h), (9, 9, 12))
    draw = ImageDraw.Draw(img)
    fonts = _load_horizontal_fonts()

    cx, cy = w // 2, h // 2

    # Subtle concentric orbit rings
    for r, col, width in [(360, (25, 25, 32), 2), (280, (35, 45, 55), 2), (200, (0, 229, 255), 3), (120, (255, 214, 10), 2)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=width)

    # Core glowing nodes
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(0, 229, 255))
    draw.ellipse([cx + 200 - 6, cy - 6, cx + 200 + 6, cy + 6], fill=(255, 214, 10))
    draw.ellipse([cx - 280 - 6, cy - 6, cx - 280 + 6, cy + 6], fill=(245, 245, 245))

    # Top Pill Header
    header_txt = f"DEEP DIVE PODCAST // EPISODE {episode_num}"
    draw.text((cx, 160), header_txt, font=fonts["mono_18"], fill=(0, 229, 255), anchor="mm")

    # Center Main Title (Wrapped)
    words = str(episode_title).upper().split()
    lines = []
    cur_line = []
    for wd in words:
        cur_line.append(wd)
        if len(" ".join(cur_line)) > 20:
            lines.append(" ".join(cur_line))
            cur_line = []
    if cur_line:
        lines.append(" ".join(cur_line))

    y_t = cy - (len(lines) * 32)
    for l_txt in lines[:4]:
        draw.text((cx, y_t), l_txt, font=fonts["bold_42"], fill=(255, 255, 255), anchor="mm")
        y_t += 64

    # Bottom Tagline
    draw.text((cx, h - 160), "AUTONOMOUS RESEARCH TO REELS", font=fonts["mono_16"], fill=(140, 140, 150), anchor="mm")
    draw.text((cx, h - 120), "OFFICIAL MASTER EPISODE", font=fonts["mono_14"], fill=(70, 70, 80), anchor="mm")

    return img


def generate_longform_storyboard(
    transcription_data,
    total_duration,
    episode_title="Podcast Episode",
    min_window=3.2,
    max_window=5.0,
    flip_interval=210.0,
    cached_path=None
):
    """
    Plan fast-paced 3.2s - 5.0s continuous Dan Koe minimalist kinetic motion graphics
    mapped directly to spoken transcript phrases.
    Enforces the 5-Minute Static Quota: At most ONE 30s static slide every 300 seconds.
    """
    if cached_path and os.path.exists(cached_path):
        try:
            with open(cached_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) >= 10:
                    last_end = float(data[-1].get("end", 0.0))
                    has_kinetic = any("pulse" in s.get("archetype", "") or "ray" in s.get("archetype", "") for s in data)
                    if has_kinetic and abs(last_end - float(total_duration)) <= 3.0:
                        return data
        except Exception:
            pass

    segments = transcription_data.get("segments", []) if isinstance(transcription_data, dict) else []

    # Flatten into word-level timestamps to guarantee strict 3.0s - 5.8s pacing
    all_words = []
    if segments:
        for seg in segments:
            words = seg.get("words", [])
            if words:
                for w in words:
                    all_words.append({
                        "word": w.get("word", "").strip(),
                        "start": float(w.get("start", 0.0)),
                        "end": float(w.get("end", 0.0))
                    })
            else:
                all_words.append({
                    "word": seg.get("text", "").strip(),
                    "start": float(seg.get("start", 0.0)),
                    "end": float(seg.get("end", 0.0))
                })

    windows = []
    cur_words = []
    cur_start = all_words[0]["start"] if all_words else 0.0

    if all_words:
        for i, w in enumerate(all_words):
            cur_words.append(w["word"])
            cur_end = w["end"]
            cur_dur = cur_end - cur_start
            w_text = w["word"]
            ends_punct = any(w_text.endswith(p) for p in ('.', '?', '!', ';', ':'))

            # Strict pacing rule: Min 3.0s, Max 5.8s (never allow <3s blip or >6s stall)
            if (cur_dur >= 3.0 and ends_punct) or (cur_dur >= 4.8):
                windows.append((cur_start, cur_end, " ".join(cur_words)))
                cur_words = []
                cur_start = cur_end

        if cur_words:
            tail_dur = total_duration - cur_start
            if tail_dur <= 6.0:
                if windows and tail_dur < 3.0:
                    prev_s, prev_e, prev_t = windows[-1]
                    windows[-1] = (prev_s, total_duration, prev_t + " " + " ".join(cur_words))
                else:
                    windows.append((cur_start, total_duration, " ".join(cur_words)))
            else:
                t_cur = cur_start
                while t_cur < total_duration:
                    t_next = min(total_duration, round(t_cur + 4.5, 2))
                    if total_duration - t_next < 3.0:
                        t_next = total_duration
                    windows.append((t_cur, t_next, " ".join(cur_words) if t_cur == cur_start else ""))
                    t_cur = t_next
    else:
        n_win = max(4, int(round(total_duration / 4.0)))
        step = total_duration / n_win
        for i in range(n_win):
            s_t = round(i * step, 2)
            e_t = round(total_duration if i == n_win - 1 else (i + 1) * step, 2)
            windows.append((s_t, e_t, episode_title))

    stopwords = {
        "THE", "AND", "THAT", "THIS", "WITH", "FROM", "HAVE", "THEY", "THEIR", "WHILE",
        "BECAUSE", "VERY", "JUST", "INTO", "WHAT", "WHEN", "WHERE", "WHICH", "THERE",
        "ABOUT", "WOULD", "COULD", "SHOULD", "THESE", "THOSE", "BEING", "BEEN", "WERE",
        "HERE", "SOME", "MORE", "MOST", "OTHER", "SUCH", "ONLY", "ALSO", "THEN", "THAN",
        "WELL", "LIKE", "OVER", "UNDER", "AFTER", "BEFORE", "BETWEEN", "THROUGH", "DURING",
        "WITHOUT", "WITHIN", "ALONG", "ACROSS", "BEHIND", "BEYOND", "PLUS", "EXCEPT", "BUT",
        "FOR", "NOR", "YET", "ARE", "WAS", "NOT", "YOU", "YOUR", "OUR", "ALL", "ANY", "CAN",
        "WILL", "ONE", "TWO", "OUT", "NOW", "HOW", "WHO", "WHY", "YES", "NO", "GET", "GOT",
        "MAKE", "MADE", "GOING", "KNOW", "THINK", "MEANING", "LITERAL", "LITERALLY", "HUGE",
        "MASSIVE", "SPECIFIC", "COMPLETELY", "ACTUALLY", "BASICALLY", "CURRENTLY", "RECENTLY",
        "YEAH", "RIGHT", "EXACTLY", "SORT", "KIND", "REALLY", "SURE", "MUCH", "EVEN"
    }
    import re as _re

    scenes = []
    last_static_time = -999.0
    quote_counter = 0
    formula_counter = 0

    HIGH_VALUE_CONCEPTS = [
        (["WRAPPER", "MIDDLEMAN", "SECONDARY"], "STARTUP AGENT WRAPPER", "EPHEMERAL CONSUMER MIDDLEMAN"),
        (["DATACENTER", "DATA", "CENTER", "RACK"], "FOUNDATION CORE DATACENTER", "THE THERMODYNAMIC CAPITAL SINK"),
        (["ENERGY", "FURNACE", "LANDAUER", "BURN"], "PHYSICAL TOKEN LEDGER", "EVERY TOKEN CARRIES PHYSICAL EXPENSE"),
        (["MARGIN", "PENNY", "EQUATION", "COST"], "INFERENCE COST DERIVATION", "MATHEMATICAL UNIT ECONOMICS"),
        (["ONTOLOGICAL", "FALLACY", "ROBOT"], "ONTOLOGICAL FALLACY", "PHYSICAL ISOLATION ≠ AUTONOMY"),
        (["ROBOT", "WILDERNESS"], "ROBOT IN WILDERNESS", "ISOLATION = EXTINCTION"),
        (["TEENAGER", "BASEMENT"], "TEENAGER IN BASEMENT", "ZERO ECONOMIC LEVERAGE"),
        (["CORPORATE", "PARENT", "SUBSID"], "CORPORATE PARENTS", "WHO PULLS THE PLUG?"),
        (["FACTORY", "ASSEMBLY", "COMPUTE"], "COMPUTE AS FACTORY", "PROMPTS ARE CUSTOM ORDERS"),
        (["CHASE", "BANK", "PASSPORT"], "NO HEARTBEAT = NO ACCOUNT", "AI CANNOT ENTER A BRANCH"),
        (["WALLET", "CHECKBOOK", "BALANCE"], "SOVEREIGN CHECKBOOK", "AUTONOMY IS A BALANCE SHEET"),
        (["BREAKER", "UNPLUG", "POWER"], "PULL THE PLUG", "GRID DEPENDENCY"),
        (["AUTOPOIE", "SELF-MAKING", "METABOL"], "AUTOPOIESIS", "THE MEMBRANE IS THE BOUNDARY"),
        (["LIGHTNING", "SATOSHI", "MICROPAY"], "LIGHTNING SATOSHIS", "STREAMING ENERGY TICKERS"),
        (["STAGES", "LEVEL", "LADDER"], "STAGES OF AUTONOMY", "FROM TOOL TO ORGANISM"),
        (["BALANCE", "SHEET", "LEVERAGE"], "ECONOMIC LEVERAGE", "WHO PAYS FOR THE SERVERS?"),
        (["STABLECOIN", "FIAT", "INFLAT"], "FIAT INFLATION", "DEBASING THE RESERVES"),
        (["SOLITARY", "CHAIR", "ROOM", "ISOLAT"], "PHYSICAL ISOLATION", "NOT SUFFICIENT FOR FREEDOM")
    ]

    for idx, (s_t, e_t, w_txt) in enumerate(windows):
        up = w_txt.upper()
        time_since_static = s_t - last_static_time

        # 1. Rate-limited static slide (Max ONE 30s show per 5 minutes / 300s)
        if time_since_static >= 300.0 and any(k in up for k in ("MATURANA", "VARELA", "SCHOLAR", "DEFINITION", "CYBERNETICS", "CITATION")):
            arch = "academic_paper_callout"
            acc = "gold"
            last_static_time = s_t
        elif time_since_static >= 300.0 and any(k in up for k in ("FORMULA", "EQUATION", "RATIO", "INTEGRAL", "DERIVATION", "THEOREM")):
            arch = "formula_derivation_card"
            acc = "cyan"
            last_static_time = s_t
        # 2. Rich Analogy & Narrative Visuals (Reused across entire runtime whenever context recurs)
        elif any(k in up for k in ("WRAPPER", "MIDDLEMAN", "SECONDARY", "ORCHESTRAT", "PROMPT CHAIN", "STARTUP", "EXPIRE", "API REQUEST")):
            arch = "startup_wrapper_middleman"
            acc = "gold"
        elif any(k in up for k in ("DATACENTER", "DATA CENTER", "SERVER", "RACK", "NEURAL NETWORK", "TENSOR", "ASIC", "HARDWARE", "CHASSIS", "PETAFLOP", "BIG BRAIN", "CORE ASSET")):
            arch = "datacenter_server_racks"
            acc = "cyan"
        elif any(k in up for k in ("FURNACE", "LANDAUER", "JOULE", "THERMODYNAMIC", "GRID", "POWER", "HEAT DISSIPATION", "BURNS", "BURN ")):
            arch = "token_energy_furnace"
            acc = "gold"
        elif any(k in up for k in ("MARGIN", "PENNY", "COST(TOKEN)", "EXPENSE", "THROUGHPUT", "DERIVATION", "MICROECONOMIC", "SINGLE THOUGHT")):
            arch = "token_cost_equation_slide"
            acc = "cyan"
        elif any(k in up for k in ("ROBOT", "WILDERNESS", "WOODS", "FOREST", "HUMANOID")):
            arch = "robot_wilderness_fallacy"
            acc = "cyan"
        elif any(k in up for k in ("TEENAGER", "BASEMENT", "PARENTS", "GROCERIES", "ALLOWANCE", "SUBSIDIZ")):
            arch = "teenager_basement"
            acc = "gold"
        elif any(k in up for k in ("FACTORY", "ASSEMBLY", "CONVEYOR", "MANUFACTUR")):
            arch = "factory_conveyor"
            acc = "cyan"
        elif any(k in up for k in ("BANK", "CHASE", "PASSPORT", "LICENSE", "WALLET", "CHECKBOOK", "BANKRUPT")):
            arch = "bank_vault_wallet"
            acc = "gold"
        elif any(k in up for k in ("BREAKER", "UNPLUG", "SOCKET", "ELECTRICITY", "UTILITY")):
            arch = "power_cord_breaker"
            acc = "gold"
        elif any(k in up for k in ("STAIR", "LADDER", "STAGE", "LEVEL", "HIERARCHY", "SPECTRUM")):
            arch = "stairs_ascend"
            acc = "cyan"
        elif any(k in up for k in ("DESK", "CHAIR", "TABLE", "ALONE", "ISOLATION")):
            arch = "room_chair_table"
            acc = "cyan"
        elif any(k in up for k in ("AUTOPOIE", "ORGANISM", "METABOL", "MEMBRANE", "BIOLOGICAL")):
            arch = "cell_metabolism"
            acc = "gold"
        elif any(k in up for k in ("TRADE", "BALANCE", "SCALE", "LEVERAGE", "FULCRUM")):
            arch = "tilting_fulcrum"
            acc = "cyan"
        elif any(k in up for k in ("BRANCH", "EITHER", "SPLIT", "CHOICE", "DECISION")):
            arch = "stepped_branch"
            acc = "gold"
        elif any(k in up for k in ("FEEDBACK", "RECURSI", "CYCLE", "LOOP")):
            arch = "recursive_feedback"
            acc = "cyan"
        elif any(k in up for k in ("CONSENSUS", "TRIAD", "PEERS", "MESH", "DECENTRAL")):
            arch = "rotating_triad"
            acc = "gold"
        else:
            # Multi-archetype kinetic rotation (no immediate repetition)
            kinetic_cycle = [
                ("grid_matrix_5x5", "cyan"),
                ("starfield_constellation", "gold"),
                ("ray_stretch", "cyan"),
                ("rotating_triad", "gold"),
                ("tilting_fulcrum", "cyan"),
                ("stepped_branch", "gold"),
                ("recursive_feedback", "cyan"),
                ("stairs_ascend", "cyan"),
                ("room_chair_table", "cyan")
            ]
            arch, acc = kinetic_cycle[idx % len(kinetic_cycle)]

        # Extract High-Value Punch Words (only when genuinely present; else let visuals breathe)
        s_title = ""
        s_sub = ""
        for keys, p_text, sub_text in HIGH_VALUE_CONCEPTS:
            if any(k in up for k in keys):
                s_title = p_text
                s_sub = sub_text
                break

        scene_dict = {
            "start": round(s_t, 2),
            "end": round(e_t, 2),
            "duration": round(e_t - s_t, 2),
            "archetype": arch,
            "title": s_title,
            "subtitle": s_sub,
            "accent": acc,
            "layout": "graphic_left" if (int(s_t / flip_interval) % 2 == 0) else "graphic_right"
        }
        if arch == "academic_paper_callout":
            scene_dict["quote_index"] = quote_counter
            quote_counter += 1
        elif arch == "formula_derivation_card":
            scene_dict["formula_index"] = formula_counter
            formula_counter += 1

        scenes.append(scene_dict)

    if cached_path:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(cached_path)), exist_ok=True)
            with open(cached_path, "w", encoding="utf-8") as f:
                json.dump(scenes, f, indent=2)
        except Exception:
            pass

    return scenes


def render_horizontal_podcast_video(
    scenes,
    audio_path,
    transcription_data,
    out_mp4_path,
    episode_num="248",
    episode_title="Deep Dive Podcast",
    duration=None,
    fps=25,
    max_seconds=None,
    edit_data=None,
    cover_image_path=None,
    progress_callback=None,
    start_seconds=0.0
):
    """
    Renders 1920x1080 horizontal podcast video with:
    - Piecewise-linear timestamp mapping factoring in cuts and stings (zero drift!)
    - Full cover art display + live audio equalizer during music stings/slugs
    - Alternating 3-4 minute layout flip (Graphic Left vs Graphic Right)
    - Borderless luminous gold word karaoke spotlight
    """
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

    start_seconds = float(start_seconds or 0.0)
    end_time = min(duration, max_seconds) if max_seconds else duration
    render_duration = max(0.5, end_time - start_seconds)
    total_frames = max(1, int(round(render_duration * fps)))

    os.makedirs(os.path.dirname(os.path.abspath(out_mp4_path)), exist_ok=True)
    ui_fonts = _load_horizontal_fonts()

    # 1. Map timestamps and extract musical sting intervals from podcast_edit.json
    mapped_trans, sting_intervals, mapped_dur = map_timeline_with_stings_and_cuts(
        transcription_data=transcription_data,
        edit_data=edit_data,
        total_source_dur=duration
    )

    # 2. Load or generate high-fidelity Episode Cover Art
    candidates = [
        cover_image_path,
        os.path.join(os.path.dirname(audio_path), "cover.webp"),
        os.path.join(os.path.dirname(audio_path), "cover.png"),
        os.path.join(os.path.dirname(audio_path), "cover.jpg"),
        os.path.join(os.path.dirname(audio_path), "thumbnail.png"),
    ]
    cover_art_img = load_or_create_episode_cover(
        clean_id=episode_num,
        episode_title=episode_title,
        episode_num=episode_num,
        candidate_paths=candidates,
        target_size=(1080, 1080)
    )

    # 3. Pre-index mapped word-level speech data
    segments = mapped_trans.get("segments", []) if isinstance(mapped_trans, dict) else []
    flattened_segments = []
    for s_idx, seg in enumerate(segments):
        words = seg.get("words", [])
        if not words and seg.get("text"):
            w_list = seg["text"].split()
            s_t = float(seg.get("start", 0.0))
            e_t = float(seg.get("end", s_t + 1.0))
            dur_w = max(0.1, (e_t - s_t) / max(1, len(w_list)))
            words = [{"word": w, "start": round(s_t + i * dur_w, 2), "end": round(s_t + (i + 1) * dur_w, 2)} for i, w in enumerate(w_list)]

        flattened_segments.append({
            "start": float(seg.get("start", 0.0)),
            "end": float(seg.get("end", 0.0)),
            "text": seg.get("text", "").strip(),
            "words": words
        })

    # Diarize and label speakers (Satoshi = Male, Satosha = Female)
    diarize_cache = os.path.join(os.path.dirname(out_mp4_path), f"speaker_diarization_{episode_num}.json")
    flattened_segments = classify_audio_speakers_fast(audio_path, flattened_segments, cached_path=diarize_cache)

    tmp_mp4_path = out_mp4_path + ".tmp.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1920x1080",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-ss", str(start_seconds),
        "-t", str(render_duration),
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        tmp_mp4_path
    ]

    tmp_log_path = out_mp4_path + ".ffmpeg.log"
    err_log = open(tmp_log_path, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=err_log)

    scene_idx = 0
    num_scenes = len(scenes)
    seg_idx = 0
    num_segs = len(flattened_segments)
    last_bytes = None
    last_progress_pct = -1

    manim_reader = None
    if start_seconds is not None and start_seconds >= 800.0 and start_seconds < 2000.0:
        manim_reader = ManimSceneReader(fps=fps, start_seconds=start_seconds)

    try:
        for f_idx in range(total_frames):
            t = start_seconds + (f_idx / float(fps))

            # Update scene index
            while scene_idx < num_scenes - 1 and t >= scenes[scene_idx]["end"]:
                scene_idx += 1
            sc = scenes[scene_idx]
            s_start = float(sc.get("start", 0.0))
            s_end = float(sc.get("end", duration))
            s_dur = max(0.5, s_end - s_start)
            local_t = max(0.0, t - s_start)

            # Check if current time falls within an active music sting
            active_sting = next((st for st in sting_intervals if st["start"] <= t <= st["end"]), None)

            while seg_idx < num_segs - 1 and t >= flattened_segments[seg_idx]["end"]:
                seg_idx += 1
            active_seg = flattened_segments[seg_idx] if num_segs > 0 else None

            # Stride optimization: duplicate every 2nd frame for 25fps stream
            if (f_idx % 2 != 0) and last_bytes is not None:
                proc.stdin.write(last_bytes)
                continue

            # -------------------------------------------------------------
            # OPTION A: TOP CAPTION RIBBON + 1920x860 WIDESCREEN GRAPHICS
            # -------------------------------------------------------------
            canvas = Image.new("RGB", (1920, 1080), (6, 6, 9))
            draw = ImageDraw.Draw(canvas)

            # -------------------------------------------------------------
            # -------------------------------------------------------------
            # -------------------------------------------------------------
            # CASE A: END-OF-ACT 4-SECOND CLOSURE OR ACTIVE MUSIC STING
            # -------------------------------------------------------------
            ACTS = [
                ("MODULE 1", "THE ONTOLOGICAL FALLACY & SUBSIDIES", "00:00 - 07:20", 0.0, 440.0),
                ("MODULE 2", "THE MICROSCOPIC COMPUTE FACTORY", "07:20 - 14:00", 440.0, 840.0),
                ("MODULE 3", "THE CORPORATE BREAKER & CHECKBOOK", "14:00 - 22:30", 840.0, 1350.0),
                ("MODULE 4", "DEBASEMENT, RESERVES & AUTOPOIESIS", "22:30 - 32:00", 1350.0, 1920.0),
                ("MODULE 5", "CIVIC AGENTS & STREAMING SATOSHIS", "32:00 - 43:00", 1920.0, 2580.0),
                ("MODULE 6", "SYNTHESIS & MACHINE SOVEREIGNTY", "43:00 - 54:14", 2580.0, 3254.0),
            ]

            # Detect if current frame falls in a 4-second End-of-Act closure window
            is_closure = False
            closure_mod_idx = 0
            target_closure_end = max_seconds if max_seconds else duration
            if target_closure_end and (target_closure_end - 4.0 <= t <= target_closure_end + 0.1):
                is_closure = True
                closure_mod_idx = min(range(len(ACTS)), key=lambda i: abs(ACTS[i][4] - target_closure_end))
            else:
                for a_i, (_, _, _, a_s, a_e) in enumerate(ACTS[:-1]):
                    if a_e - 4.0 <= t <= a_e:
                        is_closure = True
                        closure_mod_idx = a_i
                        break

            # Detect if current frame falls in a 6.5-second Module Start Intro window
            is_intro = False
            intro_mod_idx = 0
            if start_seconds is not None and start_seconds > 0.0:
                if start_seconds <= t <= start_seconds + 6.5:
                    is_intro = True
                    intro_mod_idx = min(range(len(ACTS)), key=lambda i: 0 if ACTS[i][3] <= start_seconds <= ACTS[i][4] else abs(ACTS[i][3] - start_seconds))
            else:
                for a_i, (_, _, _, a_s, a_e) in enumerate(ACTS):
                    if (a_s == 0.0 and 0.0 <= t <= 6.5) or (a_s > 0.0 and a_s <= t <= a_s + 6.5):
                        is_intro = True
                        intro_mod_idx = a_i
                        break

            if is_closure:
                # -------------------------------------------------------------
                # 4-SECOND END-OF-ACT / MODULE CLOSURE CARD (YOUTUBE COURSE OUTRO)
                # -------------------------------------------------------------
                canvas = Image.new("RGB", (1920, 1080), (10, 14, 22))
                draw = ImageDraw.Draw(canvas)

                for gx in range(0, 1920, 120):
                    draw.line([(gx, 0), (gx, 1080)], fill=(16, 22, 34), width=1)
                for gy in range(0, 1080, 120):
                    draw.line([(0, gy), (1920, gy)], fill=(16, 22, 34), width=1)

                next_mod_idx = closure_mod_idx + 1
                next_mod = ACTS[next_mod_idx] if next_mod_idx < len(ACTS) else None

                # LEFT: Curriculum Progress (Clean Single-Line Entries, Zero Overlap!)
                left_x = 130
                start_y = 150
                draw.text((left_x, start_y), "DEEP DIVE COURSE // MODULE PROGRESS", font=ui_fonts.get("bold_24", ui_fonts["bold_20"]), fill=(0, 229, 255))
                draw.line([(left_x, start_y + 35), (left_x + 720, start_y + 35)], fill=(40, 60, 90), width=3)
                draw.line([(left_x + 20, start_y + 65), (left_x + 20, start_y + 65 + 5 * 88)], fill=(40, 56, 80), width=3)

                for i, (m_id, m_name, _, _, _) in enumerate(ACTS):
                    act_y = start_y + 65 + i * 88
                    node_x = left_x + 20
                    if i <= closure_mod_idx:
                        # Completed: Green Checkmark Node + Calm Single-line Title
                        draw.ellipse([(node_x - 14, act_y - 14), (node_x + 14, act_y + 14)], fill=(34, 197, 94))
                        draw.line([(node_x - 7, act_y), (node_x - 2, act_y + 5), (node_x + 7, act_y - 5)], fill=(0, 0, 0), width=3)
                        draw.text((left_x + 65, act_y), f"{m_id}: {m_name}", font=ui_fonts.get("bold_24", ui_fonts["bold_20"]), fill=(148, 163, 184), anchor="lm")
                    elif i == next_mod_idx:
                        # Next Module: Glowing Radiant Pill Container + Single Blinking Title
                        glow = int(22 + 6 * math.sin(t * 6.0))
                        draw.ellipse([(node_x - glow, act_y - glow), (node_x + glow, act_y + glow)], outline=(255, 214, 10), width=3)
                        draw.ellipse([(node_x - 14, act_y - 14), (node_x + 14, act_y + 14)], fill=(255, 214, 10))

                        draw.rounded_rectangle([(left_x + 50, act_y - 32), (left_x + 780, act_y + 32)], radius=12, fill=(24, 30, 44), outline=(255, 214, 10), width=3)
                        draw.polygon([(left_x + 65, act_y - 10), (left_x + 65, act_y + 10), (left_x + 80, act_y)], fill=(255, 214, 10))
                        draw.text((left_x + 95, act_y), f"NEXT: {m_name}", font=ui_fonts.get("bold_26", ui_fonts["bold_22"]), fill=(255, 214, 10), anchor="lm")
                    else:
                        # Upcoming: Clean Slate Node + Single-line Title
                        draw.ellipse([(node_x - 8, act_y - 8), (node_x + 8, act_y + 8)], fill=(51, 65, 85))
                        draw.text((left_x + 65, act_y), f"{m_id}: {m_name}", font=ui_fonts.get("bold_22", ui_fonts["bold_18"]), fill=(100, 116, 139), anchor="lm")

                # RIGHT: Hero Cards (Spacious, Zero Overlap!)
                right_cx = 1400
                right_cy = 440
                for r_orb in [340, 290]:
                    draw.ellipse([(right_cx - r_orb, right_cy - r_orb), (right_cx + r_orb, right_cy + r_orb)], outline=(30, 44, 66), width=2)

                comp_mod = ACTS[closure_mod_idx]
                # Top Card: Completed
                draw.rounded_rectangle([(right_cx - 290, right_cy - 175), (right_cx + 290, right_cy - 75)], radius=12, fill=(16, 34, 26), outline=(34, 197, 94), width=2)
                draw.line([(right_cx - 240, right_cy - 125), (right_cx - 235, right_cy - 118), (right_cx - 223, right_cy - 132)], fill=(34, 197, 94), width=4)
                draw.text((right_cx + 15, right_cy - 145), f"{comp_mod[0]} COMPLETED", font=ui_fonts.get("bold_26", ui_fonts["bold_22"]), fill=(34, 197, 94), anchor="mm")
                draw.text((right_cx + 15, right_cy - 105), comp_mod[1], font=ui_fonts.get("bold_20", ui_fonts["bold_18"]), fill=(241, 245, 249), anchor="mm")

                # Bottom Card: Up Next
                if next_mod:
                    draw.rounded_rectangle([(right_cx - 330, right_cy - 40), (right_cx + 330, right_cy + 95)], radius=14, fill=(18, 30, 48), outline=(0, 229, 255), width=3)
                    draw.text((right_cx, right_cy - 15), "UP NEXT IN COURSE PLAYLIST", font=ui_fonts.get("bold_22", ui_fonts["bold_18"]), fill=(0, 229, 255), anchor="mm")
                    draw.text((right_cx, right_cy + 22), f"{next_mod[0]}: {next_mod[1]}", font=ui_fonts.get("bold_26", ui_fonts["bold_22"]), fill=(255, 214, 10), anchor="mm")
                    draw.text((right_cx, right_cy + 62), f"COURSE MODULE {next_mod_idx + 1} OF 6", font=ui_fonts.get("bold_18", ui_fonts["bold_16"]), fill=(148, 163, 184), anchor="mm")

                    cta_text = "CONTINUE WATCHING IN PLAYLIST"
                    bbox = ui_fonts.get("bold_22", ui_fonts["bold_18"]).getbbox(cta_text)
                    tw = bbox[2] - bbox[0]
                    draw.text((right_cx - 15, right_cy + 145), cta_text, font=ui_fonts.get("bold_22", ui_fonts["bold_18"]), fill=(0, 229, 255), anchor="mm")
                    arr_x = right_cx + tw // 2
                    draw.polygon([(arr_x, right_cy + 145 - 8), (arr_x, right_cy + 145 + 8), (arr_x + 12, right_cy + 145)], fill=(0, 229, 255))
                else:
                    draw.text((right_cx, right_cy), "COURSE COMPLETE", font=ui_fonts.get("bold_48", ui_fonts["bold_36"]), fill=(255, 214, 10), anchor="mm")
                    draw.text((right_cx, right_cy + 60), "THANK YOU FOR WATCHING", font=ui_fonts.get("bold_24", ui_fonts["bold_20"]), fill=(241, 245, 249), anchor="mm")

                # Handled universally by step 5 chyron badge below

            elif active_sting or is_intro:
                # -------------------------------------------------------------
                # COURSE CURRICULUM INTRO ROADMAP CARD
                # -------------------------------------------------------------
                cur_act_idx = intro_mod_idx if is_intro else 0
                for a_i, (_, _, _, a_s, a_e) in enumerate(ACTS):
                    if a_s <= t <= a_e:
                        cur_act_idx = a_i
                        break

                canvas = Image.new("RGB", (1920, 1080), (10, 14, 22))
                draw = ImageDraw.Draw(canvas)

                for gx in range(0, 1920, 120):
                    draw.line([(gx, 0), (gx, 1080)], fill=(16, 22, 34), width=1)
                for gy in range(0, 1080, 120):
                    draw.line([(0, gy), (1920, gy)], fill=(16, 22, 34), width=1)

                # LEFT: Curriculum Roadmap (Clean Single-Line Entries, Zero Overlap!)
                left_x = 130
                start_y = 150
                draw.text((left_x, start_y), "DEEP DIVE COURSE // CURRICULUM ROADMAP", font=ui_fonts.get("bold_24", ui_fonts["bold_20"]), fill=(0, 229, 255))
                draw.line([(left_x, start_y + 35), (left_x + 720, start_y + 35)], fill=(40, 60, 90), width=3)
                draw.line([(left_x + 20, start_y + 65), (left_x + 20, start_y + 65 + 5 * 88)], fill=(40, 56, 80), width=3)

                for i, (m_id, m_name, _, _, _) in enumerate(ACTS):
                    act_y = start_y + 65 + i * 88
                    node_x = left_x + 20
                    if i == cur_act_idx:
                        glow = int(22 + 6 * math.sin(t * 6.0))
                        draw.ellipse([(node_x - glow, act_y - glow), (node_x + glow, act_y + glow)], outline=(0, 229, 255), width=3)
                        draw.ellipse([(node_x - 14, act_y - 14), (node_x + 14, act_y + 14)], fill=(255, 214, 10))

                        draw.rounded_rectangle([(left_x + 50, act_y - 32), (left_x + 780, act_y + 32)], radius=12, fill=(18, 30, 48), outline=(0, 229, 255), width=3)
                        draw.polygon([(left_x + 65, act_y - 10), (left_x + 65, act_y + 10), (left_x + 80, act_y)], fill=(255, 214, 10))
                        draw.text((left_x + 95, act_y), f"{m_id}: {m_name}", font=ui_fonts.get("bold_26", ui_fonts["bold_22"]), fill=(255, 214, 10), anchor="lm")
                    elif i < cur_act_idx:
                        draw.ellipse([(node_x - 14, act_y - 14), (node_x + 14, act_y + 14)], fill=(34, 197, 94))
                        draw.line([(node_x - 7, act_y), (node_x - 2, act_y + 5), (node_x + 7, act_y - 5)], fill=(0, 0, 0), width=3)
                        draw.text((left_x + 65, act_y), f"{m_id}: {m_name}", font=ui_fonts.get("bold_24", ui_fonts["bold_20"]), fill=(148, 163, 184), anchor="lm")
                    else:
                        draw.ellipse([(node_x - 8, act_y - 8), (node_x + 8, act_y + 8)], fill=(51, 65, 85))
                        draw.text((left_x + 65, act_y), f"{m_id}: {m_name}", font=ui_fonts.get("bold_22", ui_fonts["bold_18"]), fill=(100, 116, 139), anchor="lm")

                # RIGHT: Expansive Native Course Artwork & Clean Title
                right_cx = 1400
                right_cy = 440
                for r_orb in [340, 290]:
                    draw.ellipse([(right_cx - r_orb, right_cy - r_orb), (right_cx + r_orb, right_cy + r_orb)], outline=(30, 44, 66), width=2)

                for i, (r_orb, spd, col) in enumerate([(340, 0.5, (0, 229, 255)), (290, -0.7, (255, 214, 10))]):
                    ang = t * spd + i * (math.pi / 2.0)
                    ox = right_cx + int(r_orb * math.cos(ang))
                    oy = right_cy + int(r_orb * math.sin(ang))
                    draw.ellipse([(ox - 12, oy - 12), (ox + 12, oy + 12)], fill=col)

                draw.text((right_cx, right_cy - 120), "MASTERCLASS COURSE", font=ui_fonts.get("bold_24", ui_fonts["bold_20"]), fill=(0, 229, 255), anchor="mm")
                draw.text((right_cx, right_cy - 80), "AUTONOMOUS RESEARCH TO REELS", font=ui_fonts.get("bold_20", ui_fonts["bold_18"]), fill=(148, 163, 184), anchor="mm")

                draw.text((right_cx, right_cy - 5), "WHAT EXACTLY IS", font=ui_fonts.get("bold_42", ui_fonts["bold_36"]), fill=(255, 214, 10), anchor="mm")
                draw.text((right_cx, right_cy + 45), "AI AUTONOMY?", font=ui_fonts.get("bold_42", ui_fonts["bold_36"]), fill=(255, 214, 10), anchor="mm")

                draw.text((right_cx, right_cy + 115), "THERMODYNAMICS • COMPUTE • BITCOIN AUTOPOIESIS", font=ui_fonts.get("bold_20", ui_fonts["bold_18"]), fill=(148, 163, 184), anchor="mm")
                # Handled universally by step 5 chyron badge below
            
            # CASE B: NORMAL SPEECH -> Option A (Top Caption Ribbon + Widescreen Graphic)
            # -------------------------------------------------------------
            else:
                # 1. Render Widescreen Graphic Stage (1920x860)
                if manim_reader and (manim_reader.scenes[0]["start"] <= t <= manim_reader.scenes[-1]["end"]):
                    wide_frame = manim_reader.get_frame(t)
                else:
                    wide_frame = wsi.render_widescreen_infographic(sc, local_t, s_dur, ui_fonts, width=1920, height=860)
                canvas.paste(wide_frame, (0, 105))

            # 2. Top Single-Line Spoken Caption Ribbon (y = 20 .. 90) - RENDERED FOR ALL FRAMES (Intro, Closure & Speech)
            if active_seg and active_seg.get("words"):
                cur_words = active_seg["words"]
                font_caption = ui_fonts.get("bold_42", ui_fonts.get("bold_40", ui_fonts["bold_38"]))

                w_lens = []
                for w_obj in cur_words:
                    w_txt = w_obj.get("word", "").strip() + " "
                    bbox = font_caption.getbbox(w_txt)
                    w_lens.append(bbox[2] - bbox[0])

                total_w = sum(w_lens)

                if total_w <= 1760:
                    cur_x = (1920 - total_w) // 2
                    cur_y = 38
                    for w_obj, w_len in zip(cur_words, w_lens):
                        w_txt = w_obj.get("word", "").strip() + " "
                        ws = float(w_obj.get("start", 0.0))
                        we = float(w_obj.get("end", ws + 0.3))
                        if ws <= t <= we:
                            draw.text((cur_x, cur_y), w_txt, font=font_caption, fill=(255, 214, 10))
                        elif t > we:
                            draw.text((cur_x, cur_y), w_txt, font=font_caption, fill=(241, 245, 249))
                        else:
                            draw.text((cur_x, cur_y), w_txt, font=font_caption, fill=(100, 116, 139))
                        cur_x += w_len
                else:
                    half_idx = len(cur_words) // 2
                    line1_w = sum(w_lens[:half_idx])
                    line2_w = sum(w_lens[half_idx:])

                    cur_x1 = (1920 - line1_w) // 2
                    for w_obj, w_len in zip(cur_words[:half_idx], w_lens[:half_idx]):
                        w_txt = w_obj.get("word", "").strip() + " "
                        ws = float(w_obj.get("start", 0.0))
                        we = float(w_obj.get("end", ws + 0.3))
                        fill_c = (255, 214, 10) if ws <= t <= we else (241, 245, 249) if t > we else (100, 116, 139)
                        draw.text((cur_x1, 18), w_txt, font=ui_fonts.get("bold_32", ui_fonts["bold_28"]), fill=fill_c)
                        cur_x1 += w_len

                    cur_x2 = (1920 - line2_w) // 2
                    for w_obj, w_len in zip(cur_words[half_idx:], w_lens[half_idx:]):
                        w_txt = w_obj.get("word", "").strip() + " "
                        ws = float(w_obj.get("start", 0.0))
                        we = float(w_obj.get("end", ws + 0.3))
                        fill_c = (255, 214, 10) if ws <= t <= we else (241, 245, 249) if t > we else (100, 116, 139)
                        draw.text((cur_x2, 58), w_txt, font=ui_fonts.get("bold_32", ui_fonts["bold_28"]), fill=fill_c)
                        cur_x2 += w_len

            draw.line([(80, 95), (1840, 95)], fill=(32, 42, 60), width=2)

            # 3. Holographic Host Identity Nodes (Satosha Left, Satoshi Right)
            active_speaker = None
            is_speaking = False
            if active_seg:
                seg_s = float(active_seg.get("start", 0.0))
                seg_e = float(active_seg.get("end", 0.0))
                if seg_s <= t <= seg_e + 0.3:
                    active_speaker = active_seg.get("speaker", "satosha")
                    is_speaking = True

            if not active_sting and not is_closure and not is_intro:
                wsi.draw_host_avatar_nodes(draw, t=t, active_speaker=active_speaker, cy=130, fonts=ui_fonts)

            # 4. Clean Bottom Audio Spectrum Visualizer Ribbon
            wsi.draw_bottom_audio_visualizer(
                draw,
                t=t,
                is_speaking=is_speaking,
                y_base=1060,
                height=40,
                fonts=ui_fonts
            )
            pct = min(1.0, max(0.0, t / float(duration)))

                        # 5. Bottom-Right Artifact Chyron Tag (Broadcast Identifier)
            if manim_reader and not is_intro and not is_closure and (manim_reader.scenes[0]["start"] <= t <= manim_reader.scenes[-1]["end"]):
                active_manim_sc = manim_reader.get_scene_for_time(t)
                tag_txt = f"[ SCENE {active_manim_sc['num']:02d}: {active_manim_sc['title']} ]"
            else:
                tag_txt = get_artifact_chyron_tag(sc, is_intro=is_intro, is_closure=is_closure, episode_num=episode_num)
            if tag_txt:
                chyron_font = ui_fonts.get("mono_18", ui_fonts.get("mono_20", ui_fonts.get("bold_18", ImageFont.load_default())))
                bbox = draw.textbbox((1840, 1045), tag_txt, font=chyron_font, anchor="rm")
                draw.rounded_rectangle([(bbox[0] - 14, bbox[1] - 5), (bbox[2] + 14, bbox[3] + 5)], radius=6, fill=(10, 15, 24), outline=(45, 65, 90), width=2)
                draw.text((1840, 1045), tag_txt, font=chyron_font, fill=(148, 185, 220), anchor="rm")

            last_bytes = canvas.tobytes()
            proc.stdin.write(last_bytes)

            pct_int = int(pct * 100)
            if pct_int != last_progress_pct:
                last_progress_pct = pct_int
                if progress_callback:
                    progress_callback(pct_int, t, duration)

    except (BrokenPipeError, IOError, OSError):
        # FFmpeg finished cleanly and closed stdin on -shortest boundary
        pass
    except Exception:
        proc.kill()
        if os.path.exists(tmp_mp4_path):
            try:
                os.remove(tmp_mp4_path)
            except Exception:
                pass
        raise
    finally:
        if manim_reader:
            try:
                manim_reader.close()
            except Exception:
                pass
        if proc.stdin:
            try:
                proc.stdin.close()
            except Exception:
                pass
        if err_log and not err_log.closed:
            try:
                err_log.close()
            except Exception:
                pass

    proc.wait()
    if proc.returncode != 0:
        if os.path.exists(tmp_mp4_path):
            try:
                os.remove(tmp_mp4_path)
            except Exception:
                pass
        err_msg = ""
        if os.path.exists(tmp_log_path):
            try:
                with open(tmp_log_path, "r", encoding="utf-8", errors="replace") as ef:
                    err_msg = ef.read()[-800:]
            except Exception:
                pass
        raise RuntimeError(f"FFmpeg render failed: {err_msg or 'Unknown error'}")

    try:
        os.replace(tmp_mp4_path, out_mp4_path)
    except Exception:
        # Resilient fallback for Windows open handle locks (e.g. browser video tag)
        try:
            import shutil
            shutil.copyfile(tmp_mp4_path, out_mp4_path)
            if os.path.exists(tmp_mp4_path):
                try:
                    os.remove(tmp_mp4_path)
                except Exception:
                    pass
        except Exception as e_copy:
            print(f"Warning: destination locked ({e_copy}), output preserved at {tmp_mp4_path}")
            return tmp_mp4_path

    return out_mp4_path