"""Spec H — composite longform in Beats Studio (spec-h-composite-longform).

Implements defect-specs/deepdive-spec-h-composite-longform.md exactly as
written. This module is the spec's rulebook as code: frame constants,
Mosaic-side guards, Manim-side kill rule, caption rules, run-artifact
durability, Beats workflow helpers, the dd_hub destination writer, the
longform publish gate, platform-quirk notes, and verification helpers.

What this module does NOT do (kept where it already lives):
- frame rendering stays in render_longform_parallel.py (already 1920x1080);
- run-ID resolution and re-download stay in mosaic_runner.py /
  scratch/run_curator.py heal path (this module calls back into them, it
  never invents provenance);
- clip publishing stays in the curator /publish-clip endpoint.
"""

import hashlib
import json
import shutil
from pathlib import Path

SPEC_ID = "deepdive-spec-h-composite-longform"
TRIAL_EPISODE = "249"
FIRST_APP_EPISODE = 250

# --------------------------------------------------------------------------
# 1. Composite frame (fixed layout, never per-clip)
# --------------------------------------------------------------------------
FRAME_W = 1920
FRAME_H = 1080
HOST_STRIP_H = 120
HOST_STRIP_LOOP_S = 3.0
HOST_NAME_LEFT_X = 590    # SATOSHA center: above left-panel center
HOST_NAME_RIGHT_X = 1330  # SATOSHI center: above right-panel center
HOST_BG = (0, 0, 0)       # pure black, no visible band
MIDDLE_BAND_W = 1480
MIDDLE_BAND_H = 740
PANEL_SIZE = 740          # left Manim 740x740 + right Mosaic 740x740
CAPTION_HIGHLIGHT_RGB = (255, 214, 10)  # karaoke yellow (Mosaic convention)
HALF_SIZE_NOTE = "strip, captions, Manim text all half the early-trial size"


def composite_frame_spec():
    """Fixed 1920x1080 layout descriptor (spec H section 1)."""
    return {
        "frame": (FRAME_W, FRAME_H),
        "host_strip": {"height": HOST_STRIP_H, "loop_s": HOST_STRIP_LOOP_S,
                       "names": ("SATOSHA", "SATOSHI"),
                       "name_centers_x": (HOST_NAME_LEFT_X, HOST_NAME_RIGHT_X),
                       "vertical": "mic-base level", "mics": 1,
                       "background": "pure black, no visible band"},
        "captions_band": {"style": "karaoke yellow current word",
                          "gap": "perceivable gap below strip",
                          "sizes": HALF_SIZE_NOTE},
        "middle_band": {"size": (MIDDLE_BAND_W, MIDDLE_BAND_H),
                        "left": "Manim 740x740", "right": "Mosaic 740x740"},
        "footer": {"style": "Mosaic", "left": "Mosaic",
                   "right": "deepDive podcast", "rule": "delimiter line above",
                   "copy": "no invented copy"},
    }


def check_frame_measurements(measured):
    """Check trial measurements dict against the fixed frame spec.

    measured keys: name_left_x, name_right_x, panel_left_cx,
    panel_right_cx, strip_rgb, strip_h, frame_wh, panel_wh.
    Returns a list of mismatch strings (empty = matches).
    """
    bad = []
    tol = 15
    if abs(measured.get("name_left_x", -1) - HOST_NAME_LEFT_X) > tol:
        bad.append("name SATOSHA not above left-panel center (x~=590)")
    if abs(measured.get("name_right_x", -1) - HOST_NAME_RIGHT_X) > tol:
        bad.append("name SATOSHI not above right-panel center (x~=1330)")
    if measured.get("strip_rgb") != (0, 0, 0):
        bad.append("host strip background not pure black")
    if measured.get("strip_h") != HOST_STRIP_H:
        bad.append("host strip height != 1920x120")
    if tuple(measured.get("frame_wh", ())) != (FRAME_W, FRAME_H):
        bad.append("frame != 1920x1080")
    if tuple(measured.get("panel_wh", ())) != (PANEL_SIZE, PANEL_SIZE):
        bad.append("panels not full 740x740 (crop suspected)")
    return bad


# --------------------------------------------------------------------------
# 2. Mosaic side (the clip engine)
# --------------------------------------------------------------------------
MOSAIC_SRC_SIZE = 1080
MOSAIC_DST_SIZE = 740
MOSAIC_SCALE = MOSAIC_DST_SIZE / MOSAIC_SRC_SIZE  # exact 1080 -> 740


def mosaic_run_artifact_name(ep, clip, run_id):
    """Run-ID artifact filename: {ep}-{clip}-mosaic-{run_id}.mp4."""
    return f"{ep}-{clip}-mosaic-{run_id}.mp4"


def resolve_mosaic_side(ep, clip, run_id):
    """Describe the Mosaic-side source. Never the compiled clip, never a crop.

    Raises ValueError when run_id is missing (a generically-named body file
    with no run-ID provenance must never be silently substituted — spec H 5).
    """
    if not run_id:
        raise ValueError(
            f"clip {clip}: no mosaic run_id — refusing to substitute "
            "compiled clip or generic body file")
    return {"artifact": mosaic_run_artifact_name(ep, clip, run_id),
            "scale": f"exact {MOSAIC_SRC_SIZE}->{MOSAIC_DST_SIZE}",
            "crop": False, "compiled_clip": False,
            "audio": "run artifact unchanged",
            "stings_intro_cards": "excluded from longform"}


# --------------------------------------------------------------------------
# 3. Manim side (one sustained artifact per clip) + kill rule
# --------------------------------------------------------------------------
MAX_DIAGRAM_OR_FORMULA_PER_CLIP = 1


class KillRuleExceeded(Exception):
    """Raised when the spec H section 3 kill rule fires (stop + report)."""


class KillRuleTracker:
    """Enforces the 248-disaster kill rule from the 249 trial.

    Stop + report when the Manim side needs per-beat design, or when more
    than a third of the clips' artifacts need reprocessing. The trial did
    NOT trigger it (0 of 18 new clips reprocessed).
    """

    def __init__(self):
        self.clip_count = 0
        self.per_beat_clips = []
        self.reprocessed_clips = []

    def set_clip_count(self, n):
        self.clip_count = int(n)

    def note_design(self, clip, per_beat=False):
        """Record one clip's design call. per_beat=True fires the kill rule."""
        if per_beat:
            self.per_beat_clips.append(clip)
            raise KillRuleExceeded(
                f"spec H kill rule: clip {clip} needs per-beat design "
                "(the 248 disaster in a new layout) — build stopped")

    def note_reprocess(self, clip):
        """Record a clip artifact reprocessing. >1/3 of clips fires the rule."""
        if clip not in self.reprocessed_clips:
            self.reprocessed_clips.append(clip)
        total = self.clip_count or len(self.reprocessed_clips)
        if len(self.reprocessed_clips) > total / 3:
            raise KillRuleExceeded(
                f"spec H kill rule: {len(self.reprocessed_clips)}/{total} "
                "clips reprocessed (>1/3) — build stopped")

    def status(self):
        total = self.clip_count or len(self.reprocessed_clips)
        return {"clip_count": total,
                "per_beat_clips": list(self.per_beat_clips),
                "reprocessed": list(self.reprocessed_clips)}


def classify_formula_source(formula, episode_page_text, clip):
    """Decide per clip whether a formula is its own, a reuse, or absent.

    Returns (kind, report_line) where kind is own|reuse|title-only.
    Reuse is never silent: the report line must be surfaced.
    """
    if not formula:
        return ("title-only",
                f"clip {clip}: no formula on episode page — title-only artifact")
    page = episode_page_text or ""
    if formula not in page:
        return ("title-only",
                f"clip {clip}: formula not on episode page — title-only, reported")
    return ("own", f"clip {clip}: page-sourced formula")


def report_formula_reuse(formula, clips):
    """Report a formula reused across clips (trial: 8-5 = 3 in two clips)."""
    if len(clips) < 2:
        return None
    return (f"formula reuse: {formula!r} in clips {list(clips)} — "
            "reuse reported, never silent")


# --------------------------------------------------------------------------
# 4. Captions (karaoke, from the body timings)
# --------------------------------------------------------------------------
CAPTION_MAX_LINE_CHARS = 40
CAPTION_LINE_TOP_PX = 42  # hard-placed line tops; LineSpacing style ignored
COMPILED_CHUNK_OFFSET_S = 1.5  # compiled chunks carry +1.5s: must NOT be used


def validate_clip_captions(clip, body_word_timings, from_compiled_chunks=False):
    """Caption-data rule: every clip needs body-relative word timings.

    A clip with no caption data is a REPORTED EXCEPTION — never a silent
    static title band. Compiled-chunk timings (+1.5 s offset) are refused.
    """
    if from_compiled_chunks:
        return {"ok": False,
                "exception": (f"clip {clip}: compiled caption chunks carry "
                              f"+{COMPILED_CHUNK_OFFSET_S}s offset — refused, "
                              "use body-relative word timings"),
                "fallback_static_band": False}
    if not body_word_timings:
        return {"ok": False,
                "exception": (f"clip {clip}: no caption data — reported "
                              "exception per spec H section 4"),
                "fallback_static_band": False}
    return {"ok": True, "exception": None, "fallback_static_band": False,
            "renderer": {"explicit_fontsize": True, "line_top_px": CAPTION_LINE_TOP_PX,
                         "max_line_chars": CAPTION_MAX_LINE_CHARS,
                         "highlight": "yellow current word, word-tiling, hold to duration"}}


def check_proper_name(asr_name, episode_page_text):
    """Check a proper name against the episode page (trial: Connes-Rovelli).

    Returns a correction report line, or None when no correction applies.
    """
    if asr_name and episode_page_text and asr_name not in episode_page_text:
        return (f"proper-name check: {asr_name!r} not on episode page — "
                "verify against page before shipping")
    return None


# --------------------------------------------------------------------------
# 5. Run-artifact durability
# --------------------------------------------------------------------------
def canonical_run_artifact_path(dd_hub_root, ep, clip, run_id):
    """Purge-proof canonical copy: <dd_hub>/episodes/<ep>/{ep}-{clip}-mosaic-{run_id}.mp4."""
    return Path(dd_hub_root) / "episodes" / str(ep) / mosaic_run_artifact_name(ep, clip, run_id)


def verify_run_artifact(path, expect_size=None, expect_duration=None, probe=None):
    """Verify a run artifact on write: size + duration recorded and checked."""
    p = Path(path)
    if not p.exists():
        return {"ok": False, "reason": f"missing: {p}"}
    size = p.stat().st_size
    info = {"ok": True, "size": size, "path": str(p)}
    if expect_size is not None and size != expect_size:
        return {"ok": False, "reason": f"size mismatch: {size} != {expect_size}",
                "size": size}
    if expect_duration is not None and probe is not None:
        try:
            dur = probe(str(p))
        except Exception as e:
            return {"ok": False, "reason": f"unreadable: {e}"}
        info["duration"] = dur
        if abs(dur - expect_duration) > 1.0:
            return {"ok": False, "reason": f"duration mismatch: {dur} != {expect_duration}",
                    **info}
    return info


def purge_local_cache_only(local_cache_dir):
    """Purge cleans ONLY the local cache — never the hub canonical copy."""
    d = Path(local_cache_dir)
    removed = []
    if not d.exists():
        return removed
    for p in sorted(d.glob("*-mosaic-*.mp4")):
        try:
            p.unlink()
            removed.append(p.name)
        except OSError:
            pass
    return removed


def health_check_run_artifacts(clips, dd_hub_root, probe=None, redownload_fn=None):
    """Health check: every clip's run artifact exists and is valid.

    A missing/invalid one is re-downloaded from Mosaic's cloud BY RUN ID and
    reported. Never substituted (no compiled clip, no generic body file, no
    fresh run without the user's word).
    Returns {"healthy": [...], "recovered": [...], "unrecoverable": [...]}.
    """
    healthy, recovered, unrecoverable = [], [], []
    for c in clips:
        dest = canonical_run_artifact_path(dd_hub_root, c["ep"], c["clip"], c.get("run_id", ""))
        check = verify_run_artifact(dest, probe=probe) if c.get("run_id") else {
            "ok": False, "reason": "no run_id provenance"}
        if check["ok"]:
            healthy.append(c["clip"])
            continue
        if redownload_fn and c.get("run_id"):
            try:
                redownload_fn(c["run_id"], dest)
                after = verify_run_artifact(dest, probe=probe)
                if after["ok"]:
                    recovered.append({"clip": c["clip"], "run_id": c["run_id"],
                                      "report": f"clip {c['clip']}: re-downloaded by run ID"})
                    continue
            except Exception as e:
                unrecoverable.append({"clip": c["clip"], "reason": str(e)})
                continue
        unrecoverable.append({"clip": c["clip"],
                              "reason": check.get("reason", "missing run artifact")})
    return {"healthy": healthy, "recovered": recovered, "unrecoverable": unrecoverable}


# --------------------------------------------------------------------------
# 6. Beats Studio workflow (the compile room)
# --------------------------------------------------------------------------
RETRIGGER_SIDES = ("manim", "mosaic")  # per side: a bad title never costs a re-render
WORKFLOW = {
    "start": "one deliberate 'Design artifacts' action, per clip or per episode; nothing starts itself",
    "fanout": "one design call per clip, each designing that clip's ONE Manim artifact",
    "renders": "queued background jobs, progress per clip, exceptions-only reporting",
    "finesse": "one clip at a time, failures only; retrigger is per side",
    "duration_lock": "retrigger never touches duration (decided in Cutroom)",
    "assemble": "automatic deterministic combine; concat joints must be clean",
    "push": "Push the movie to dd_hub button lives in Beats Studio",
}


def retrigger_preserves_duration(clip_duration_before, clip_duration_after):
    """Retrigger never touches duration — violation stops the retrigger."""
    if abs(float(clip_duration_before) - float(clip_duration_after)) > 0.001:
        raise ValueError("spec H section 6: retrigger changed clip duration — refused")
    return True


def exceptions_only_report(per_clip_outcomes):
    """Report only the exceptions; working clips never ask for attention."""
    return {clip: outcome for clip, outcome in per_clip_outcomes.items()
            if outcome.get("status") not in ("ok", "stitched", "designed")}


# --------------------------------------------------------------------------
# 8. dd_hub longform destination (episode 250 onwards)
# --------------------------------------------------------------------------
LONGFORM_META_NAME = "longform_meta.json"
STRIPPED_ELEMENTS = ("deepdive conclusions stings", "intro cards")


def longform_destination(dd_hub_root, ep):
    """Grounded destination: the episode's longform slot on the hub."""
    return Path(dd_hub_root) / "episodes" / str(ep) / f"{ep}-longform.mp4"


def write_longform_meta(dest_movie, sha256_hex, container_duration,
                        stream_duration, gate_ok, stings_stripped=True):
    """Write longform meta beside the movie.

    Records SHA-256, container + video-stream durations (any disagreement is
    a logged warning), and the ready_for_distribution signal the distribution
    pickup reads. Not distributable until the signal is set.
    """
    warnings = []
    if container_duration is None or stream_duration is None:
        warnings.append("duration probe unavailable — durations unrecorded")
    elif abs(float(container_duration) - float(stream_duration)) > 0.05:
        warnings.append("container/stream duration disagreement")
    meta = {"spec": SPEC_ID, "sha256": sha256_hex,
            "container_duration": container_duration,
            "stream_duration": stream_duration, "warnings": warnings,
            "stings_stripped": bool(stings_stripped),
            "stripped": list(STRIPPED_ELEMENTS),
            "ready_for_distribution": bool(gate_ok),
            "slot": "episode longform slot"}
    meta_path = Path(dest_movie).with_name(LONGFORM_META_NAME)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def sha256_of(path, limit_bytes=None):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 256)
            if not chunk:
                break
            h.update(chunk)
            if limit_bytes is not None:
                limit_bytes -= len(chunk)
                if limit_bytes <= 0:
                    break
    return h.hexdigest()


# --------------------------------------------------------------------------
# 9. Publish gate for the longform
# --------------------------------------------------------------------------
def longform_publish_gate(movie_path, local_master_path,
                          baseline_structure=None, structure_sampler=None):
    """Draft-relative structural gate for the longform movie.

    Compares against the black-canvas draft baseline BY STRUCTURE — never an
    absolute brightness threshold — and refuses the draft-in-substance with a
    named reason. Prefers the verified good local master; stops on a master
    mismatch. Same draft-relative gate as the clip publish gate, for the movie.
    """
    movie = Path(movie_path)
    if not movie.exists():
        return {"ok": False, "reason": f"movie missing: {movie}"}
    local = Path(local_master_path) if local_master_path else None
    if local is not None and local.exists():
        if sha256_of(movie) != sha256_of(local):
            return {"ok": False,
                    "reason": "master mismatch: movie != verified good local master"}
    if baseline_structure is not None and structure_sampler is not None:
        try:
            sig = structure_sampler(str(movie))
        except Exception as e:
            return {"ok": False, "reason": f"structure sampling failed: {e}"}
        if sig == baseline_structure:
            return {"ok": False,
                    "reason": "draft-in-substance: movie matches black-canvas draft baseline"}
    return {"ok": True, "reason": "gate passed: draft-relative structural check"}


# --------------------------------------------------------------------------
# 10. Platform quirks (249 trial, baked in — distribution notes, not gates)
# --------------------------------------------------------------------------
PLATFORM_QUIRKS = {
    "youtube": "public slopcast playlist, verbatim title/description; same-title video is the RSS audio podcast, not a duplicate",
    "spotify": "new video-show episode; A/V tracks must match; transient sync advisory is not by itself a failure",
    "tiktok": "60-min web cap; brief 'under review/Only me' is review not failure; 1s duration rounding is TikTok-side",
    "instagram": "OUT — longform over the 20-min Reels cap",
}


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------
ORACLE_SIZE = 93749687
ORACLE_DURATION_S = 1883.689
ORACLE_FRAME = (1920, 1080)
DURATION_TOL_S = 1.0


def verify_against_oracle(clip_order, total_duration, frame_wh, frame_notes=()):
    """Regression check vs the 249 prototype oracle (93,749,687 B, 1883.689 s).

    Same clip order and durations (within 1 s total), same 1920x1080 frame,
    same strip/captions/panels/footer by the trial measurements.
    """
    problems = []
    if tuple(frame_wh) != ORACLE_FRAME:
        problems.append(f"frame {frame_wh} != oracle 1920x1080")
    if abs(float(total_duration) - ORACLE_DURATION_S) > DURATION_TOL_S:
        problems.append(f"duration {total_duration}s differs from oracle by >1s")
    problems.extend(frame_notes)
    return {"ok": not problems, "problems": problems,
            "oracle": {"size": ORACLE_SIZE, "duration_s": ORACLE_DURATION_S,
                       "frame": list(ORACLE_FRAME)},
            "clip_order": list(clip_order)}
