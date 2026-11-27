"""Spec H2 — composite assembler (defect-specs/deepdive-spec-h2-composite-assembler.md).

Ports the proven 249 trial build scripts into app code — it does NOT invent
a new assembler. Reference implementation ported verbatim in behavior:

- v6 frame scripts in 249-composite-test-v6/:
  gen_v6.py      -> build_caption_ass (karaoke ASS writer)
  build_v6.py    -> SEGMENT_FILTER + build_segment_cmd (ffmpeg per-clip build)
  strip_v6.py    -> host-strip constants (1920x120, 3.0 s loop, mic geometry)
  mkconcat6.py   -> write_concat_list (ffmpeg concat demuxer list)
  measure_v6.py  -> frame-measurement expectations (trial geometry evidence)
  abtest.py      -> caption line-spacing finding (hard-placed lines, ASS
                    LineSpacing field ignored by the renderer)
- full-build script in 249-composite-test-full/:
  gen_full.py        -> same caption builder over clips 3..20 (its
                      title_band_ass static-band fallback for caption-less
                      clips 3/4 is prototype-only and is NOT ported: a clip
                      with no caption data is a reported exception per H2 s2)
  build_full.py    -> same segment builder with run IDs from the plan
                      (mosaic_run_id) instead of the v6 hardcoded table
  mkconcat_full.py -> concat list over v6 segs 0-2 + full segs 3-20
  gen_art.py       -> Manim artifact stage-time rule (stages at sentence
                      boundaries of the clip transcript, title first) —
                      recorded here as plan_artifact_timings descriptors
  full_artifacts.py -> the sustained-artifact shape (one continuous scene
                      per clip): ambient + title Write + staged FadeIns
  inv.py / ffall.py -> run-artifact inventory + duration probe pattern
                      (delegated to spec_h.health_check_run_artifacts)
  redownload_missing.py -> heal path (re-download by run ID, hub write
                      only; delegated, never a fresh run without the word)
  hooks.py / offset.py / plan_struct.py -> diagnosis scripts: caption
                      chunks carry a +1.5 s offset and must NOT be used;
                      body-relative _caption_words are the caption source

What this module does NOT do (guardrails):
- never triggers Mosaic: build_segment_cmd only DESCRIBES the ffmpeg argv;
  execution happens solely through the manual UI retrigger path;
- never substitutes: no compiled clip, no generically-named body file
  without run-ID provenance, no fresh run without the user's word;
- never invents a left pane: a clip with no Manim artifact is reported
  not-ready, never a silent Mosaic-only segment;
- captions required per clip: missing data is a reported exception, and
  the kill rule stands (imported from spec_h, not redefined).
"""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

SPEC_ID = "deepdive-spec-h2-composite-assembler"
TRIAL_EPISODE = "249"

# --------------------------------------------------------------------------
# 1. Frame contract (hard-coded style elements — a recode, never a retrigger)
# --------------------------------------------------------------------------
FRAME_W = 1920
FRAME_H = 1080
CHROME_W = 1920
CHROME_H = 1080
HOST_STRIP_W = 1920
HOST_STRIP_H = 120
HOST_STRIP_LOOP_S = 3.0
HOST_NAME_LEFT_X = 590    # SATOSHA center: above left-panel center
HOST_NAME_RIGHT_X = 1330  # SATOSHI center: above right-panel center
HOST_BG = (0, 0, 0)       # pure black, same as the rest of the screen
PANEL_SIZE = 740          # left Manim 740x740 + right Mosaic 740x740
ART_POS = (220, 230)      # left pane overlay origin in the 1920x1080 frame
MOS_POS = (960, 230)      # right pane overlay origin
MOSAIC_SRC_SIZE = 1080    # run artifact body render, scaled exact, NEVER cropped
CHROME_FRAMERATE = 30
SEGMENT_CODEC = ("libx264", "veryfast", 20)  # codec, preset, crf (trial)

# Captions band (below the strip, karaoke yellow current word; trial sizes —
# half the too-big early sample — baked in, never per-clip).
CAPTION_FONT_SIZE = 28
CAPTION_LINE_TOP_PX = 42  # hard-placed line tops; the ASS LineSpacing field
CAPTION_Y_SINGLE = 162    # is ignored by the renderer (trial abtest.py)
CAPTION_Y_FIRST = 141
CAPTION_Y_SECOND = 183
CAPTION_MAX_LINE_CHARS = 40
CAPTION_LINE_BREAK_GAP_S = 0.9
CAPTION_FILL_FROM_ZERO_S = 0.5  # first event starts here -> hold first line at 0.0

# Concat joints: the trial's 1-tick DTS overlaps at the joints are a known
# cosmetic artifact — accepted and reported, not silently re-timed.
CONCAT_JOINT_NOTE = "1-tick DTS overlaps at concat joints (trial-known cosmetic)"


def composite_frame_spec():
    """Fixed 1920x1080 layout descriptor (spec H2 section 1)."""
    return {
        "frame": (FRAME_W, FRAME_H),
        "chrome": {"size": (CHROME_W, CHROME_H), "framerate": CHROME_FRAMERATE},
        "host_strip": {"size": (HOST_STRIP_W, HOST_STRIP_H),
                       "loop_s": HOST_STRIP_LOOP_S,
                       "names": ("SATOSHA", "SATOSHI"),
                       "name_centers_x": (HOST_NAME_LEFT_X, HOST_NAME_RIGHT_X),
                       "vertical": "mic-base level", "mics": 1,
                       "background": "pure black, no visible band"},
        "captions_band": {"style": "karaoke yellow current word",
                          "gap": "perceivable gap below strip",
                          "font_size": CAPTION_FONT_SIZE,
                          "line_tops_px": (CAPTION_Y_FIRST, CAPTION_Y_SECOND,
                                           CAPTION_Y_SINGLE)},
        "middle_band": {"left": f"Manim {PANEL_SIZE}x{PANEL_SIZE}",
                        "right": f"Mosaic {PANEL_SIZE}x{PANEL_SIZE}",
                        "origins": {"art": ART_POS, "mosaic": MOS_POS}},
        "footer": {"style": "Mosaic", "left": "Manim",
                   "center": "N/total (per-clip drawtext; blank on clip 0)",
                   "right": "Mosaic", "rule": "delimiter line above",
                   "copy": "no invented copy"},
    }


# --------------------------------------------------------------------------
# Segments ground zero for CONTENT (spec H2 s2: the clip's `segments` list
# decides which audio/stings/order — start/end/duration/audio_duration/
# rendered_duration are derived bookkeeping and may be stale, never read them
# for timing). DURATION comes from the clip's Mosaic run file via ffprobe
# (clip_composite_duration); segments-minus-crossfades is fallback only.
# --------------------------------------------------------------------------
def segments_hash(segments):
    """Audio signature of a clip's segments list (md5 of canonical JSON).

    Same construction as the compile path (_audio_sig in ddma.py): the
    Mosaic run path records this alongside the run ID when a run completes,
    and the assembler compares it against the clip's current segments.
    """
    return hashlib.md5(json.dumps(segments or [], sort_keys=True
                                  ).encode("utf-8")).hexdigest()


def clip_ground_zero_duration(clip):
    """Segments-minus-crossfades fallback (content ground zero, NOT timing).

    Sums audio/music segment durations minus crossfades, mirroring the
    Cutroom display (sum of segments minus crossfades). Segments still decide
    CONTENT (which audio/stings/order — golden rule stands); they no longer
    decide DURATION. Used only when no run file exists for the clip.
    """
    total = sum(float(s.get("duration", 0) or 0)
                for s in (clip.get("segments") or []))
    xfades = sum(float(s.get("crossfade", 0) or 0)
                 for s in (clip.get("segments") or []))
    return total - xfades


def probe_run_duration(run_path, probe=None):
    """ffprobe the run artifact's duration (Spec H heal-pattern probe).

    probe: optional callable(path_str) -> float (test seam, same role as the
    probe param of spec_h.verify_run_artifact / health_check_run_artifacts).
    Without it, runs ffprobe format=duration. Returns a float or None —
    never raises, never substitutes another file: the caller passes the real
    run-ID artifact path only.
    """
    try:
        if probe is not None:
            return float(probe(str(run_path)))
        if shutil.which("ffprobe") is None:
            return None
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(run_path)],
            capture_output=True, text=True, timeout=15)
        if p.returncode == 0 and p.stdout.strip():
            return float(p.stdout.strip())
    except Exception:
        pass
    return None


def resolve_clip_run_path(ep, clip, dd_hub_root=None, run_path=None):
    """Resolve the clip's real run-ID artifact path (never a substitute).

    Returns a Path or None. Only the canonical
    {ep}-{clip}-mosaic-{run_id}.mp4 (via spec_h.canonical_run_artifact_path)
    or an explicitly passed run_path is ever returned — never the compiled
    clip, never a generically-named body file.
    """
    if run_path is not None:
        return Path(run_path)
    run_id = (clip.get("mosaic_run_id") or clip.get("run_id") or "").strip() \
        if isinstance(clip, dict) else ""
    if not run_id or dd_hub_root is None:
        return None
    import spec_h_composite_longform as spec_h
    return spec_h.canonical_run_artifact_path(
        dd_hub_root, ep, clip.get("num"), run_id)


def clip_composite_duration(clip, ep=None, dd_hub_root=None, run_path=None,
                            probe=None):
    """Clip composite duration: the RUN FILE decides duration.

    Probes the clip's Mosaic run file via ffprobe (heal-pattern probe) and
    returns that duration. Falls back to segments-minus-crossfades ONLY when
    no run file exists (missing run_id or file absent) or the probe yields
    nothing. Segments still decide CONTENT (golden rule); this decides
    DURATION so both panes render to the same length. Read-only: never
    triggers Mosaic, never substitutes another file.
    """
    candidate = resolve_clip_run_path(ep, clip, dd_hub_root, run_path) \
        if (run_path is not None or (ep is not None
                                     and dd_hub_root is not None)) else None
    if candidate is not None and Path(candidate).exists():
        probed = probe_run_duration(candidate, probe=probe)
        if probed is not None:
            return probed
    return clip_ground_zero_duration(clip)


def clip_composite_duration_explained(clip, ep=None, dd_hub_root=None,
                                      run_path=None, probe=None):
    """Same as clip_composite_duration plus the source of the number.

    Returns (duration, source) where source is "run-file-probe" or
    "segments-fallback (no run file)". The Manim side renders to the same
    duration so both panes stay in sync.
    """
    candidate = resolve_clip_run_path(ep, clip, dd_hub_root, run_path) \
        if (run_path is not None or (ep is not None
                                     and dd_hub_root is not None)) else None
    if candidate is not None and Path(candidate).exists():
        probed = probe_run_duration(candidate, probe=probe)
        if probed is not None:
            return probed, "run-file-probe"
    return clip_ground_zero_duration(clip), "segments-fallback (no run file)"


class StaleRun(Exception):
    """The clip's run is stale: segments edited after the Mosaic run finished."""


class CaptionDataMissing(Exception):
    """The clip has no body-relative caption data — reported, never silent."""


class ManimPaneMissing(Exception):
    """The clip has no Manim artifact yet — not-ready, never a Mosaic-only
    segment and never an invented left pane."""


def check_run_freshness(clip, recorded_audio_sig):
    """Cutroom-edit rule (spec H2 s2): the run file still holds the OLD audio
    after a transcript-pane edit, and nothing in the app can tell except this
    comparison. A mismatch is a reported exception — never a silent reuse.
    """
    current = segments_hash(clip.get("segments"))
    if recorded_audio_sig != current:
        raise StaleRun(
            f"clip {clip.get('num')}: run audio signature stale "
            f"(recorded {recorded_audio_sig} != current {current}) — "
            "manual Mosaic retrigger required")
    return True


# --------------------------------------------------------------------------
# Captions: karaoke ASS from BODY-RELATIVE word timings (gen_v6.py /
# gen_full.py build_ass, ported verbatim in behavior). The compiled caption
# chunks carry a +1.5 s offset and must NOT be used. Clips with no words
# raise CaptionDataMissing — gen_full.title_band_ass (static band for
# caption-less clips 3/4) is prototype-only behavior and is NOT ported.
# --------------------------------------------------------------------------
YEL = r"{\c&H00FFFF&}"
WHT = r"{\c&HFFFFFF&}"


def ass_time(t):
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    return f"{h}:{m:02d}:{t:05.2f}"


def fix_proper_names(text):
    """Trial ASR fix (gen scripts): Conravelli -> Connes-Rovelli."""
    return text.replace("Conravelli", "Connes-Rovelli")


def build_caption_ass(clip_num, body_words, duration_s):
    """Build the karaoke ASS text for one clip from body-relative words.

    body_words: list of (start, end, word) from the clip's _caption_words.
    Returns (ass_text, event_count, first_start, last_end).
    Raises CaptionDataMissing when there are no words.
    """
    if not body_words:
        raise CaptionDataMissing(
            f"clip {clip_num}: no caption data — reported exception "
            "per spec H2 section 2 (never a silent static band)")
    words = [(float(s), float(e), fix_proper_names(str(t)))
             for (s, e, t) in body_words]
    lines, cur = [], []
    for i, (s, e, txt) in enumerate(words):
        cur.append((s, e, txt))
        curlen = sum(len(t) + 1 for _, _, t in cur)
        gap = (words[i + 1][0] - e) if i + 1 < len(words) else 99
        sent = txt.rstrip().endswith((".", "?", "!"))
        if gap > CAPTION_LINE_BREAK_GAP_S or curlen > CAPTION_MAX_LINE_CHARS \
                or (sent and len(cur) >= 4):
            lines.append(cur)
            cur = []
    if cur:
        lines.append(cur)
    blocks, cur_b = [], []
    for li, line in enumerate(lines):
        cur_b.append(line)
        last_txt = line[-1][2]
        gap = (lines[li + 1][0][0] - line[-1][1]) if li + 1 < len(lines) else 99
        if len(cur_b) == 2 or last_txt.rstrip().endswith(
                (".", "?", "!")) or gap > CAPTION_LINE_BREAK_GAP_S:
            blocks.append(cur_b)
            cur_b = []
    if cur_b:
        blocks.append(cur_b)
    evs = []
    for bi, block in enumerate(blocks):
        flat = [(wi, li, s, e, t)
                for li, line in enumerate(block)
                for wi, (s, e, t) in enumerate(line)]
        b_end = (blocks[bi + 1][0][0][0] if bi + 1 < len(blocks) else duration_s)
        nlines = len(block)
        ys = [CAPTION_Y_SINGLE] if nlines == 1 else [
            CAPTION_Y_FIRST, CAPTION_Y_SECOND][:nlines]
        for k, (wi, li, s, e, txt) in enumerate(flat):
            en = flat[k + 1][2] if k + 1 < len(flat) else b_end
            for li2, line in enumerate(block):
                parts = []
                for wj, (ss, ee, tt) in enumerate(line):
                    if li2 == li and wj == wi:
                        parts.append(YEL + tt + WHT)
                    else:
                        parts.append(tt)
                evs.append((s, en, ys[li2], " ".join(parts)))
    if evs and evs[0][0] > CAPTION_FILL_FROM_ZERO_S:
        first = " ".join(t for _, _, t in blocks[0][0])
        evs.insert(0, (0.0, evs[0][0], CAPTION_Y_SINGLE, WHT + first))
    evs.sort(key=lambda x: (x[0], x[2]))
    head = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920",
            "PlayResY: 1080", "ScaledBorderAndShadow: yes", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, "
            "Bold, Alignment, MarginV",
            "Style: Cap,Arial,28,&H00FFFFFF,&H80000000,0,8,160", "",
            "[Events]",
            "Format: Layer, Start, End, Style, Text"]
    body = [f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Cap,"
            f"{{\\pos(960,{y})}}{t}"
            for (s, e, y, t) in evs]
    return ("\n".join(head + body) + "\n", len(evs), evs[0][0], evs[-1][1])


def write_caption_ass(out_dir, clip_num, body_words, duration_s):
    """Write caps_{n}.ass beside the segment build (trial naming)."""
    text, nev, first, last = build_caption_ass(clip_num, body_words,
                                               duration_s)
    path = Path(out_dir) / f"caps_{clip_num}.ass"
    path.write_text(text, encoding="utf-8")
    return {"path": str(path), "events": nev,
            "first_start": first, "last_end": last}


# --------------------------------------------------------------------------
# Per-clip composite segment (build_v6.py / build_full.py, ported in
# behavior). Inputs: chrome base (looped), Manim art, run-ID Mosaic artifact,
# host-strip loop. Audio is the run artifact's, unchanged; duration is the
# Cutroom clip's duration (run artifact carries it).
#
# NOTE on the trial scripts' invocation: build_v6.py/build_full.py pass
# "-/filter_complex" with the filter text held in vf_{n}.txt — that flag
# spelling is not a working ffmpeg invocation (the filter belongs to
# -filter_complex_script). The filter GRAPH is the proven part and is ported
# exactly; this module emits the correct -filter_complex_script form and
# writes the same vf_{n}.txt sidecar the trial used for inspection.
# --------------------------------------------------------------------------
CHROME_LABEL_FONTFILE = "C\\:/Windows/Fonts/verdana.ttf"
CHROME_LABEL_FONTSIZE = 14
CHROME_LABEL_COLOR = "0x888888"
# Baseline-matched top for the footer labels (PIL Verdana-14 baseline
# y=1028, ascent 15 -> top 1013; verified against the chrome rule/labels).
CHROME_LABEL_Y = 1013


def segment_filter(clip_num, total_clips):
    """Exact trial filter graph for clip n (caps_{n}.ass burned in).

    The chrome image carries the static footer (Manim left, Mosaic
    right, delimiter rule); the center "N/total" is drawn per clip
    here since it varies (clip 0, the intro, shows no center text).
    total_clips comes from the episode plan via the caller
    -- never hardcoded.
    """
    total = int(total_clips)
    if total <= 0:
        raise ValueError("segment_filter: total_clips must be positive "
                         "(derived from the episode plan, never hardcoded)")
    # V2 ruling: center is N/total with N = the clip number; clip 0
    # (the intro) shows no center text. Beats Studio numbers the
    # parts 0-based, so clip 1 reads "1/21" on its segment.
    n = int(clip_num)
    center = "" if n == 0 else f"{n}/{total}"
    return ("[1:v]setsar=1[art];"
            "[2:v]scale=740:740,setsar=1[mos];"
            "[0:v][3:v]overlay=0:0[base];"
            "[base][art]overlay=220:230[tl];"
            f"[tl][mos]overlay=960:230,subtitles=caps_{clip_num}.ass,"
            f"drawtext=fontfile='{CHROME_LABEL_FONTFILE}':"
            f"fontsize={CHROME_LABEL_FONTSIZE}:"
            f"fontcolor={CHROME_LABEL_COLOR}:"
            f"text='{center}':x=(w-text_w)/2:y={CHROME_LABEL_Y},"
            "format=yuv420p[v]")


def resolve_segment_inputs(ep, clip_num, run_id, manim_artifact_path,
                           dd_hub_root, chrome_path, strip_path):
    """Resolve a clip's segment inputs with H2 guards (no execution).

    Raises ValueError when run_id is missing (never substitute the compiled
    clip or a generically-named body file); raises ManimPaneMissing when the
    Manim artifact is absent (never invent a left pane, never Mosaic-only).
    Missing run files are a reported exception for the by-run-ID heal path
    (spec_h.health_check_run_artifacts) — never a substitution.
    """
    import spec_h_composite_longform as spec_h
    if not run_id:
        raise ValueError(
            f"clip {clip_num}: no mosaic run_id — refusing to substitute "
            "compiled clip or generic body file (spec H2 s2)")
    run_path = spec_h.canonical_run_artifact_path(dd_hub_root, ep, clip_num,
                                                  run_id)
    if not Path(manim_artifact_path).exists():
        raise ManimPaneMissing(
            f"clip {clip_num}: no Manim artifact at {manim_artifact_path} — "
            "clip not-ready (spec H2 s2)")
    if not Path(run_path).exists():
        raise FileNotFoundError(
            f"clip {clip_num}: run artifact missing: {run_path} — "
            "re-download by run ID and report (spec H s5, never substitute)")
    return {"chrome": str(chrome_path), "art": str(manim_artifact_path),
            "run": str(run_path), "strip": str(strip_path),
            "artifact": run_path.name}


def build_segment_cmd(ep, clip_num, inputs, duration_s, out_path,
                      filter_sidecar_path=None, total_clips=None):
    """Describe the per-clip ffmpeg build (no execution — manual trigger only).

    Writes the vf_{n}.txt sidecar holding the filter graph (trial naming) and
    returns the argv list. Audio: run artifact's, unchanged (-map 2:a?).
    total_clips is the episode's clip count from the plan (threaded through
    from the caller, never hardcoded) for the per-clip center footer text.
    """
    if total_clips is None:
        raise ValueError("build_segment_cmd: total_clips is required "
                         "(episode clip count from the plan, never hardcoded)")
    sidecar = (Path(filter_sidecar_path) if filter_sidecar_path
               else Path(out_path).parent / f"vf_{clip_num}.txt")
    sidecar.write_text(segment_filter(clip_num, total_clips),
                       encoding="utf-8")
    codec, preset, crf = SEGMENT_CODEC
    return ["ffmpeg", "-y",
            "-loop", "1", "-framerate", str(CHROME_FRAMERATE),
            "-i", inputs["chrome"],
            "-i", inputs["art"],
            "-i", inputs["run"],
            "-stream_loop", "-1", "-i", inputs["strip"],
            "-filter_complex_script", str(sidecar),
            "-map", "[v]", "-map", "2:a?",
            "-t", str(duration_s),
            "-c:v", codec, "-preset", preset, "-crf", str(crf),
            "-c:a", "aac", str(out_path)]


def write_concat_list(seg_paths, out_path):
    """Write the ffmpeg concat-demuxer list (mkconcat6/mkconcat_full naming:
    file '<segment path>' per line, in clip order)."""
    lines = [f"file '{p}'" for p in seg_paths]
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"path": str(out_path), "segments": len(lines),
            "joint_note": CONCAT_JOINT_NOTE}


# --------------------------------------------------------------------------
# 3. Design artifacts — initial render of the Manim side (planner only).
# One deliberate start; fans out one design call per clip, each from that
# clip's Cutroom transcript (audio as cut, never the whole transcript in
# one pass, never per beat — per-beat fires the spec H kill rule). Renders
# run as queued background jobs with per-clip progress; only exceptions
# are reported. This function plans the work; it starts nothing by itself.
# --------------------------------------------------------------------------
def plan_design_artifacts(clips):
    """Plan one Manim design call per clip (returns job descriptors)."""
    import spec_h_composite_longform as spec_h
    tracker = spec_h.KillRuleTracker()
    tracker.set_clip_count(len(clips))
    jobs = []
    for c in clips:
        tracker.note_design(c["clip"])  # per_beat=True would fire the rule
        jobs.append({"clip": c["clip"],
                     "source": "cutroom transcript (audio as cut)",
                     "whole_transcript_one_pass": False,
                     "per_beat": False,
                     "shape": "one sustained artifact, title first, stages "
                              "at sentence boundaries, at most one "
                              "diagram/formula (page-sourced, reuse "
                              "reported)",
                     "queue": "background, progress per clip, "
                              "exceptions-only reporting"})
    return {"jobs": jobs, "kill_status": tracker.status()}


# --------------------------------------------------------------------------
# 4. Retrigger — pause the preview, fix one side, re-stitch (planner only).
# Retrigger Manim re-renders only the left pane; retrigger Mosaic only the
# right pane (via the manual UI trigger — this module never starts a run).
# Either path re-stitches only that clip's segment; duration and the
# hard-coded frame never change (spec_h duration lock enforced).
# --------------------------------------------------------------------------
def plan_retrigger(ep, clip_num, side, duration_before, duration_after):
    """Plan a single-side restitch (returns the restitch descriptor)."""
    import spec_h_composite_longform as spec_h
    if side not in spec_h.RETRIGGER_SIDES:
        raise ValueError(f"unknown retrigger side {side!r} "
                         f"(want one of {spec_h.RETRIGGER_SIDES})")
    spec_h.retrigger_preserves_duration(duration_before, duration_after)
    other = "mosaic" if side == "manim" else "manim"
    return {"ep": ep, "clip": clip_num, "side": side,
            "untouched_side": other,
            "scope": "re-stitch only this clip's composite segment, "
                     "then re-gate the master before any push",
            "duration_locked": True, "frame_locked": True}
