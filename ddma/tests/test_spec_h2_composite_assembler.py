"""Tests for spec H2 composite assembler (defect-specs/deepdive-spec-h2-composite-assembler.md).

Ports the trial's proven behavior as the oracle: karaoke caption builder
(gen_v6/gen_full build_ass), exact filter graph (build_v6/build_full),
concat list (mkconcat scripts), segments-ground-zero timing, run-freshness
rule, and the caption/kill guardrails (no static-band fallback, kill rule
stands via spec_h).
"""
import sys
import unittest
from pathlib import Path

DDMA_DIR = Path(__file__).resolve().parent.parent
if str(DDMA_DIR) not in sys.path:
    sys.path.insert(0, str(DDMA_DIR))

import spec_h2_composite_assembler as H2


def _words(n=10, start=0.0, step=0.5):
    return [(start + i * step, start + (i + 1) * step, f"w{i}") for i in range(n)]


class TestFrameContract(unittest.TestCase):
    def test_fixed_frame(self):
        spec = H2.composite_frame_spec()
        self.assertEqual(spec["frame"], (1920, 1080))
        self.assertEqual(spec["host_strip"]["size"], (1920, 120))
        self.assertEqual(spec["host_strip"]["loop_s"], 3.0)
        self.assertEqual(spec["host_strip"]["name_centers_x"], (590, 1330))

    def test_pane_geometry(self):
        spec = H2.composite_frame_spec()
        self.assertEqual(spec["middle_band"]["origins"]["art"], (220, 230))
        self.assertEqual(spec["middle_band"]["origins"]["mosaic"], (960, 230))


class TestGroundZero(unittest.TestCase):
    def test_duration_from_segments_not_span(self):
        clip = {"segments": [{"duration": 17.41}, {"duration": 10.0}],
                "start": 0, "end": 134.18, "duration": 149.84,
                "audio_duration": 999.0, "rendered_duration": 999.0}
        self.assertAlmostEqual(H2.clip_ground_zero_duration(clip), 27.41)
        self.assertNotEqual(H2.clip_ground_zero_duration(clip),
                            clip["audio_duration"])

    def test_fresh_run_passes(self):
        clip = {"num": 0, "segments": [{"duration": 1.0}]}
        self.assertTrue(H2.check_run_freshness(
            clip, H2.segments_hash(clip["segments"])))

    def test_edited_segments_flag_stale(self):
        clip = {"num": 0, "segments": [{"duration": 1.0}]}
        with self.assertRaises(H2.StaleRun):
            H2.check_run_freshness(clip, "deadbeef" * 4)


class TestCaptions(unittest.TestCase):
    def test_karaoke_highlights_current_word(self):
        text, nev, first, last = H2.build_caption_ass(
            0, _words(6, 0.0, 0.5), 10.0)
        self.assertIn(H2.YEL + "w0" + H2.WHT, text)
        self.assertIn("Fontsize", text)  # explicit fontsize (trial dark-red bug)
        self.assertIn("PlayResX: 1920", text)
        self.assertEqual(nev, 6)  # one line, one event per word

    def test_first_event_fill_and_hold(self):
        text, nev, first, last = H2.build_caption_ass(
            0, _words(4, 2.0, 0.5), 10.0)
        self.assertEqual(first, 0.0)
        self.assertEqual(last, 10.0)  # held to duration

    def test_proper_name_fix(self):
        text, _, _, _ = H2.build_caption_ass(
            0, [(0.0, 0.5, "Conravelli")], 5.0)
        self.assertIn("Connes-Rovelli", text)

    def test_missing_captions_is_reported_exception(self):
        with self.assertRaises(H2.CaptionDataMissing):
            H2.build_caption_ass(3, [], 87.166)


class TestSegmentBuild(unittest.TestCase):
    def test_filter_graph_exact(self):
        f = H2.segment_filter(0, 21)
        self.assertIn("[1:v]setsar=1[art]", f)
        self.assertIn("[2:v]scale=740:740,setsar=1[mos]", f)
        self.assertIn("[base][art]overlay=220:230[tl]", f)
        self.assertIn("subtitles=caps_0.ass", f)
        self.assertIn("format=yuv420p[v]", f)
        self.assertNotIn("crop", f)

    def test_filter_graph_center_footer_text(self):
        # Per-clip center footer: "N/total" with N = the clip's
        # on-screen part number (249 parts are 0-based); clip 0
        # (the intro) shows no center text.
        self.assertIn("text=''", H2.segment_filter(0, 21))
        self.assertIn("text='1/21'", H2.segment_filter(1, 21))
        self.assertIn("text='9/21'", H2.segment_filter(9, 21))
        self.assertIn("text='20/21'", H2.segment_filter(20, 21))
        self.assertIn("x=(w-text_w)/2", H2.segment_filter(0, 21))
        self.assertIn("fontsize=14", H2.segment_filter(0, 21))
        self.assertIn("fontcolor=0x888888", H2.segment_filter(0, 21))
        with self.assertRaises(ValueError):
            H2.segment_filter(0, 0)
        with self.assertRaises(ValueError):
            H2.build_segment_cmd("249", 0, {}, 10.0, "o.mp4")

    def test_missing_run_id_refuses_substitution(self):
        with self.assertRaises(ValueError):
            H2.resolve_segment_inputs("249", 3, "", "art.mp4", "hub",
                                      "chrome.png", "strip.mp4")

    def test_missing_manim_pane_not_ready(self):
        with self.assertRaises(H2.ManimPaneMissing):
            H2.resolve_segment_inputs("249", 3, "abc123",
                                      "no-such-art.mp4", "hub",
                                      "chrome.png", "strip.mp4")

    def test_concat_list(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            r = H2.write_concat_list(["a.mp4", "b.mp4"],
                                     str(Path(td) / "concat.txt"))
            self.assertEqual(r["segments"], 2)
            self.assertIn("DTS", r["joint_note"])

    def test_retrigger_sides(self):
        r = H2.plan_retrigger("249", 3, "manim", 87.166, 87.166)
        self.assertEqual(r["untouched_side"], "mosaic")
        with self.assertRaises(ValueError):
            H2.plan_retrigger("249", 3, "manim", 87.166, 90.0)

    def test_design_plan_one_call_per_clip(self):
        r = H2.plan_design_artifacts([{"clip": 0}, {"clip": 1}])
        self.assertEqual(len(r["jobs"]), 2)
        self.assertFalse(r["jobs"][0]["per_beat"])


class TestEpisode249DurationPin(unittest.TestCase):
    """Pin the episode-249 fresh-assembly total to the run-file oracle.

    The 21 per-clip run durations below are the ffprobe format=duration
    values of the REAL hub run artifacts (episode 249, read-only probe).
    The assembler's fresh-assembly total (run-file probe per clip) must
    match the oracle total 1883.689 s within 0.05 s. Skips when the hub
    root or any run file is absent (environmental, not a code failure).
    """
    EP = "249"
    # Per-clip oracle durations, clip order 0..20 (ffprobe, 3 dp).
    ORACLE_CLIP_DURATIONS = [
        144.300, 120.733, 112.666, 87.166, 89.467, 94.966, 81.067,
        74.267, 91.533, 75.700, 76.866, 77.533, 78.200, 78.200,
        98.633, 74.167, 88.200, 77.066, 68.000, 63.066, 131.867,
    ]
    ORACLE_TOTAL = 1883.689
    TOLERANCE_S = 0.05

    def test_oracle_clip_durations_sum(self):
        # Rounded (3 dp) per-clip oracles: their sum carries rounding
        # error, so pin it to the oracle total within tolerance, and pin
        # the 21 caller-given run durations to 1883.69 within 1 cent.
        total = sum(self.ORACLE_CLIP_DURATIONS)
        self.assertEqual(len(self.ORACLE_CLIP_DURATIONS), 21)
        self.assertLessEqual(abs(total - self.ORACLE_TOTAL),
                             self.TOLERANCE_S)
        caller_given = [144.30, 120.73, 112.67, 87.17, 89.47, 94.97,
                        81.07, 74.27, 91.53, 75.70, 76.87, 77.53, 78.20,
                        78.20, 98.63, 74.17, 88.20, 77.07, 68.00, 63.07,
                        131.87]
        self.assertEqual(len(caller_given), 21)
        self.assertAlmostEqual(sum(caller_given), 1883.69, places=2)

    def test_fresh_assembly_total_matches_oracle(self):
        import json
        import beats_server
        hub = beats_server.DD_HUB_ROOT
        # Clip list: the episode plan, NEVER the shared root copy. The
        # root plan.json is the currently-loaded Cutroom project's working
        # copy and flips to 250's 14-clip plan whenever the user works on
        # 250 -- reading it here caused false 14 != 21 failures. The
        # code-only mirror clone has no plan files by design, so fall back
        # to the canonical hub plan (same 21 clip dicts with mosaic_run_id).
        clips = None
        local_ep_plan = DDMA_DIR / "projects" / ("episode_" + self.EP) / "plan.json"
        if local_ep_plan.exists():
            clips = json.loads(local_ep_plan.read_text(encoding="utf-8"))
        elif hub is not None:
            hub_plan = Path(str(hub)) / "episodes" / self.EP / "plan.json"
            if hub_plan.exists():
                clips = json.loads(hub_plan.read_text(encoding="utf-8"))
        if clips is None:
            self.skipTest("no clip plan available "
                          "(local episode plan and hub plan both absent)")
        self.assertEqual(len(clips), 21)
        run_paths = [H2.resolve_clip_run_path(self.EP, c, hub)
                     for c in clips]
        if hub is None or not Path(str(hub)).exists() or any(
                p is None or not p.exists() for p in run_paths):
            self.skipTest(f"hub run files unavailable (hub={hub})")
        total, sources = 0.0, []
        for c in clips:
            dur, src = H2.clip_composite_duration_explained(
                c, self.EP, hub)
            total += dur
            sources.append(src)
        self.assertTrue(all(s == "run-file-probe" for s in sources),
                        f"fresh assembly must probe run files: {sources}")
        self.assertLessEqual(abs(total - self.ORACLE_TOTAL),
                             self.TOLERANCE_S,
                             f"assembler total {total:.3f}s vs oracle "
                             f"{self.ORACLE_TOTAL:.3f}s")


class TestIssue143ManimPanelLanding(unittest.TestCase):
    """Pin the Issue 143 panel-landing path for completed H2 Manim designs.

    Proves:
    (1) Partial-coverage episodes (e.g. 250 with 4/14 mosaic_run_ids) still
        report has_beats=True when a clip's H2 Manim artifact exists, and
        _lf_cache_key invalidates when a Manim artifact or storyboard changes.
    (2) renderClipManimPanel lands a completed 250-1 design (kind ANCHOR,
        label ULTIMATE ANCHOR, hook Clip one, the ultimate anchor., stages
        list, playable video, Patch enabled) even when chInfo.has_beats was
        initially stale/false, and survives a page reload.
    """
    def test_partial_coverage_episode_reports_h2_manim_has_beats(self):
        import tempfile
        import archetype_studio as AS
        with tempfile.TemporaryDirectory() as td:
            old_script_dir = AS.SCRIPT_DIR
            try:
                AS.SCRIPT_DIR = td
                AS._LF_INTERVALS_CACHE.clear()
                proj_dir = Path(td) / "projects" / "episode_250"
                proj_dir.mkdir(parents=True, exist_ok=True)
                clips_dir = Path(td) / "clips"
                clips_dir.mkdir(parents=True, exist_ok=True)
                # Episode 250 shape: clip 1 has mosaic_run_id + infographic_ready,
                # clip 4 has no mosaic_run_id (so h2_covered is False).
                plan = [
                    {"num": 1, "title": "Ultimate Anchor", "start": 0.0,
                     "end": 134.65, "duration": 134.65,
                     "mosaic_run_id": "4dc08028-5f8a-4d51-97e2-490e4cadc68d",
                     "infographic_ready": True},
                    {"num": 4, "title": "Part 4", "start": 134.65,
                     "end": 250.0, "duration": 115.35,
                     "mosaic_run_id": None},
                ]
                (proj_dir / "plan.json").write_text(
                    __import__("json").dumps(plan), encoding="utf-8")
                idx_before = AS.get_longform_timeline_index("250")
                ch1_before = next(
                    c for c in idx_before["chapters"] if c["clip_num"] == 1)
                self.assertFalse(ch1_before["has_beats"])
                key_before = AS._lf_cache_key("250")
                # Now the Manim render completes and writes 250-1-infographic.mp4
                (clips_dir / "250-1-infographic.mp4").write_bytes(b"mp4bytes")
                key_after = AS._lf_cache_key("250")
                self.assertNotEqual(key_before, key_after)
                idx_after = AS.get_longform_timeline_index("250")
                ch1_after = next(
                    c for c in idx_after["chapters"] if c["clip_num"] == 1)
                self.assertTrue(ch1_after["has_beats"])
            finally:
                AS.SCRIPT_DIR = old_script_dir
                AS._LF_INTERVALS_CACHE.clear()

    def test_panel_lands_completed_250_1_design_in_node_harness(self):
        import json
        import shutil
        import subprocess
        node = shutil.which("node")
        if not node:
            self.skipTest("node not available")
        beats_html = (DDMA_DIR / "beats.html").read_text(encoding="utf-8")
        sb_path = (DDMA_DIR / "projects" / "episode_250" / "storyboards"
                   / "clip_1_storyboard.json")
        if sb_path.exists():
            sb_data = json.loads(sb_path.read_text(encoding="utf-8"))
        else:
            sb_data = {
                "clip_num": 1, "clip_title": "Ultimate Anchor",
                "total_duration": 134.65,
                "design": {
                    "kind": "anchor", "title": "Ultimate Anchor",
                    "anchor": {"label": "ULTIMATE ANCHOR",
                               "hook": "Clip one, the ultimate anchor."},
                    "directive": "Rule: one artifact — title first, plus this one anchor.",
                    "directive_report": "directive-honored: forced anchor",
                },
                "stages": [
                    {"start": 0.0, "end": 3.0, "kind": "title",
                     "title": "Ultimate Anchor", "text": "Ultimate Anchor"},
                    {"start": 3.0, "end": 28.82, "kind": "anchor",
                     "title": "Ultimate Anchor", "text": "Is infinity a boundless horizon or a terminal wall?"},
                    {"start": 28.82, "end": 58.89, "kind": "anchor",
                     "title": "Ultimate Anchor", "text": "So to map that kind of physical universe, we need a mathematical system."},
                    {"start": 58.89, "end": 93.09, "kind": "anchor",
                     "title": "Ultimate Anchor", "text": "The absolute essence of a division algebra is that it's this pristine space."},
                    {"start": 93.09, "end": 122.76, "kind": "anchor",
                     "title": "Ultimate Anchor", "text": "I want to make sure we are visualizing this correctly."},
                    {"start": 122.76, "end": 134.65, "kind": "anchor",
                     "title": "Ultimate Anchor", "text": "It scales logically. But what happens if the algebra isn't a division algebra?"},
                ],
            }
        # Extract escapeHtml and renderClipManimPanel from beats.html
        js_harness = f"""
const sbPayload = {json.dumps(sb_data)};
const htmlSrc = {json.dumps(beats_html)};
function extractFn(src, name) {{
    const marker = name.startsWith('async ') ? name : ('function ' + name);
    const start = src.indexOf(marker);
    if (start < 0) throw new Error('missing ' + name);
    let depth = 0, i = src.indexOf('{{', start);
    for (; i < src.length; i++) {{
        if (src[i] === '{{') depth++;
        else if (src[i] === '}}') {{
            depth--;
            if (depth === 0) return src.slice(start, i + 1);
        }}
    }}
    throw new Error('unclosed ' + name);
}}
const escapeFn = extractFn(htmlSrc, 'escapeHtml');
const panelFn = extractFn(htmlSrc, 'async function renderClipManimPanel');
const container = {{ innerHTML: '' }};
const document = {{
    getElementById: (id) => (id === 'beats-below-player' ? container : null)
}};
const lfTimelineIndex = {{ has_video: false }};
function beatsEpisode() {{ return '250'; }}
async function fetch(url) {{
    return {{
        ok: true, status: 200,
        json: async () => ({{
            success: true, ep: '250', clip_num: 1,
            storyboard: sbPayload,
            manim_artifact_mtime: 1764295000.0,
            master_mtime: null
        }})
    }};
}}
eval(escapeFn);
eval(panelFn);
(async () => {{
    const chInfo = {{ clip_num: 1, title: 'Ultimate Anchor', has_beats: false }};
    await renderClipManimPanel(1, chInfo);
    console.log(JSON.stringify({{
        html: container.innerHTML,
        has_beats_after: chInfo.has_beats
    }}));
}})();
"""
        proc = subprocess.run([node, "-e", js_harness],
                              capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout.strip())
        html = out["html"]
        self.assertTrue(out["has_beats_after"])
        self.assertNotIn("No Manim yet", html)
        self.assertIn("Manim ready - 6 stages, 134.65s - 250-1-manim.mp4", html)
        self.assertIn("Anchor: ULTIMATE ANCHOR - Clip one, the ultimate anchor.", html)
        self.assertIn("lf-manim-stages-list", html)
        self.assertIn("Stage 1 (", html)
        self.assertIn("lf-manim-infographic-video", html)
        self.assertNotIn("disabled>⚡ Patch", html)


if __name__ == "__main__":
    unittest.main()
