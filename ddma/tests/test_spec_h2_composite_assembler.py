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
        self.assertIn("source=manim", html)
        self.assertNotIn("disabled>⚡ Patch", html)

    def test_manim_only_clip_media_ignores_hub_mosaic_short(self):
        import tempfile
        import beats_server as BS
        with tempfile.TemporaryDirectory() as td:
            old_hub = BS.DD_HUB_ROOT
            old_ddma = BS.DDMA_DIR
            try:
                hub_dir = Path(td) / "hub"
                ddma_dir = Path(td) / "ddma"
                hub_ep = hub_dir / "episodes" / "250"
                local_clips = ddma_dir / "clips"
                hub_ep.mkdir(parents=True, exist_ok=True)
                local_clips.mkdir(parents=True, exist_ok=True)
                BS.DD_HUB_ROOT = hub_dir
                BS.DDMA_DIR = ddma_dir
                # Hub holds the compiled Mosaic short (candidate 4 in find_clip_media)
                mosaic_short = hub_ep / "250-1.mp4"
                mosaic_short.write_bytes(b"mosaic-short-140s")
                # When no Manim files exist, Manim-only lookup returns None (404),
                # never falling back to the hub Mosaic short; general lookup returns mosaic_short.
                self.assertIsNone(BS.find_manim_clip_media("250", 1))
                self.assertEqual(BS.find_clip_media("250", 1), mosaic_short)
                # When local 250-1-manim.mp4 exists, Manim-only lookup returns it
                # instead of being shadowed by hub 250-1.mp4.
                local_manim = local_clips / "250-1-manim.mp4"
                local_infographic = local_clips / "250-1-infographic.mp4"
                local_infographic.write_bytes(b"manim-infographic-134s")
                self.assertEqual(BS.find_manim_clip_media("250", 1), local_infographic)
                local_manim.write_bytes(b"manim-compiled-134s")
                self.assertEqual(BS.find_manim_clip_media("250", 1), local_manim)
                # Top-player general lookup remains unchanged (hub 250-1.mp4 still candidate 4).
                self.assertEqual(BS.find_clip_media("250", 1), mosaic_short)
            finally:
                BS.DD_HUB_ROOT = old_hub
                BS.DDMA_DIR = old_ddma


class TestManimConfiguratorAndMosaicRemoval(unittest.TestCase):
    """Pin the Spec H2 Manim configurator (V1-V9) and Mosaic retrigger removal."""

    CATALOG = [
        {"section": "1. Octonionic Substrate",
         "text": "x = x_0 e_0 + sum x_i e_i",
         "norm": "x = x 0 e 0 + i = 1 sum 7 x i e i",
         "tex": r"x = x_0 e_0 + \sum_{i=1}^7 x_i e_i"},
        {"section": "1. Associator",
         "text": "[x, y, z] = (xy)z - x(yz) != 0",
         "norm": "[ x , y , z ] = ( x y ) z - x ( yz ) != 0",
         "tex": r"[x, y, z] \equiv (xy)z - x(yz) \neq 0"},
    ]
    TR = "Clip one, the ultimate anchor. Is infinity a boundless horizon or a terminal wall? That is the big question."

    def test_v2_kind_forces_anchor_formula_diagram(self):
        import manim_fresh_design as F
        # Kind=ANCHOR + label
        art_a, rep_a = F.design_clip_artifact(
            self.TR, "Ultimate Anchor", 90.0, self.CATALOG,
            genai_mod=None, clip_num=1, kind="anchor",
            anchor_label="BOUNDLESS HORIZON",
            anchor_hook="Is infinity a boundless horizon?")
        da = art_a["design"]
        self.assertEqual(da["kind"], "anchor")
        self.assertEqual(da["anchor"]["label"], "BOUNDLESS HORIZON")
        self.assertEqual(da["anchor"]["hook"], "Is infinity a boundless horizon?")
        self.assertIn("kind-forced: anchor", da["directive_report"])
        self.assertTrue(any("kind-forced: anchor" in r for r in rep_a))

        # Kind=FORMULA + catalog index
        art_f, rep_f = F.design_clip_artifact(
            self.TR, "Ultimate Anchor", 90.0, self.CATALOG,
            genai_mod=None, clip_num=1, kind="formula", equation_ref=1)
        df = art_f["design"]
        self.assertEqual(df["kind"], "formula")
        self.assertEqual(df["equation_ref"], 1)
        self.assertEqual(df["equation_norm"], self.CATALOG[1]["norm"])
        self.assertIn("kind-forced: formula", df["directive_report"])
        self.assertIn("equation-picked: catalog 1", df["directive_report"])

        # Kind=DIAGRAM + tunnel
        art_d, rep_d = F.design_clip_artifact(
            self.TR, "Ultimate Anchor", 90.0, self.CATALOG,
            genai_mod=None, clip_num=1, kind="diagram", diagram="tunnel")
        dd = art_d["design"]
        self.assertEqual(dd["kind"], "diagram")
        self.assertEqual(dd["diagram"], "tunnel")
        self.assertIn("kind-forced: diagram", dd["directive_report"])
        self.assertIn("diagram-picked: tunnel", dd["directive_report"])

    def test_v3_guard_out_of_range_equation_ref_degrades_to_anchor(self):
        import manim_fresh_design as F
        art, rep = F.design_clip_artifact(
            self.TR, "Ultimate Anchor", 90.0, self.CATALOG,
            genai_mod=None, clip_num=1, kind="formula", equation_ref=99)
        d = art["design"]
        self.assertEqual(d["kind"], "anchor")
        self.assertIsNone(d["equation_norm"])
        self.assertIn("equation-rejected-not-on-page", d["directive_report"])
        self.assertTrue(any("equation-rejected-not-on-page" in r for r in rep))

    def test_v4_prompt_override_records_fallback_deterministic_and_gemini(self):
        import json
        import manim_fresh_design as F
        # With Gemini unavailable (None / 401), deterministic fallback runs from structured params
        art_fb, rep_fb = F.design_clip_artifact(
            self.TR, "Ultimate Anchor", 90.0, self.CATALOG,
            genai_mod=None, clip_num=1, kind="diagram", diagram="numberline",
            prompt_override="Custom edited prompt text")
        dfb = art_fb["design"]
        self.assertEqual(dfb["kind"], "diagram")
        self.assertEqual(dfb["diagram"], "numberline")
        self.assertEqual(dfb["prompt_override"], "Custom edited prompt text")
        self.assertIn("prompt-override: fallback-deterministic", dfb["directive_report"])
        self.assertTrue(any("prompt-override: fallback-deterministic" in r for r in rep_fb))

        # With Gemini available, prompt_override is passed verbatim and reported as prompt-override: gemini
        seen_prompts = []
        class _FakeModel:
            def generate_content(self, p):
                seen_prompts.append(p)
                class _R:
                    text = json.dumps({"kind": "diagram", "diagram": "groundzero",
                                       "equation_ref": None, "equation_display": "",
                                       "anchor_label": None, "reason": "gemini override"})
                return _R()
        class _FakeGen:
            def GenerativeModel(self, name):
                return _FakeModel()

        art_g, rep_g = F.design_clip_artifact(
            self.TR, "Ultimate Anchor", 90.0, self.CATALOG,
            genai_mod=_FakeGen(), clip_num=1,
            prompt_override="VERBATIM OVERRIDE PROMPT")
        dg = art_g["design"]
        self.assertEqual(seen_prompts[0], "VERBATIM OVERRIDE PROMPT")
        self.assertEqual(dg["kind"], "diagram")
        self.assertEqual(dg["diagram"], "groundzero")
        self.assertIn("prompt-override: gemini", dg["directive_report"])

    def test_v5_rerender_unchanged_storyboard_vs_changed_override(self):
        import json
        import manim_fresh_design as F
        art, _ = F.design_clip_artifact(
            self.TR, "Ultimate Anchor", 90.0, self.CATALOG,
            genai_mod=None, clip_num=1, kind="anchor",
            anchor_label="ULTIMATE ANCHOR",
            anchor_hook="Clip one, the ultimate anchor.")
        sb = {
            "clip_num": 1, "clip_title": "Ultimate Anchor",
            "total_duration": 90.0,
            "design": art["design"],
            "scenes": art["stages"],
            "stages": art["stages"],
        }
        orig_bytes = json.dumps(sb, sort_keys=True)
        # Re-render with identical configurator values: pure redraw, changed=False, bytes identical
        sb_same, changed_same = F.apply_configurator_overrides_to_storyboard(
            sb, self.TR, "Ultimate Anchor", 90.0, self.CATALOG,
            clip_num=1, kind="anchor", anchor_label="ULTIMATE ANCHOR",
            anchor_hook="Clip one, the ultimate anchor.")
        self.assertFalse(changed_same)
        self.assertEqual(json.dumps(sb_same, sort_keys=True), orig_bytes)

        # Re-render with modified Kind (FORMULA + catalog 0): updates storyboard deterministically
        sb_mod, changed_mod = F.apply_configurator_overrides_to_storyboard(
            sb, self.TR, "Ultimate Anchor", 90.0, self.CATALOG,
            clip_num=1, kind="formula", equation_ref=0, ep_num="249")
        self.assertTrue(changed_mod)
        self.assertEqual(sb_mod["design"]["kind"], "formula")
        self.assertEqual(sb_mod["design"]["equation_ref"], 0)
        self.assertEqual(sb_mod["design"]["equation_tex"], self.CATALOG[0]["tex"])

    def test_v6_mosaic_retrigger_removed_from_page_and_refused_by_server(self):
        import io
        import json
        import beats_server as BS
        beats_html = (DDMA_DIR / "beats.html").read_text(encoding="utf-8")
        self.assertNotIn("btn-retrigger-mosaic", beats_html)
        self.assertNotIn("Retrigger Mosaic-only", beats_html)
        self.assertNotIn("beatsMosaicRetrigger", beats_html)
        self.assertIn("btn-retrigger-manim", beats_html)
        self.assertIn("Retrigger Manim-only", beats_html)

        # Exercise BeatsHandler POST /api/beats/composite_retrigger with side="mosaic"
        # and POST /api/beats/mosaic_retry: both must refuse with HTTP 400 and
        # "Mosaic runs happen in Cutroom" without touching the curator.
        for path, payload in (
            ("/api/beats/composite_retrigger", {"ep": "249", "clip_num": 1, "side": "mosaic"}),
            ("/api/beats/mosaic_retry", {"ep": "249", "clip_num": 1}),
        ):
            raw_body = json.dumps(payload).encode("utf-8")
            sent = {}
            handler = BS.BeatsHandler.__new__(BS.BeatsHandler)
            handler.path = path
            handler.headers = {"Content-Length": str(len(raw_body))}
            handler.rfile = io.BytesIO(raw_body)
            handler.send_json = lambda data, status=200, _s=sent: _s.update({"status": status, "data": data})
            handler.do_POST()
            self.assertEqual(sent.get("status"), 400)
            self.assertFalse(sent["data"].get("success", True))
            self.assertIn("Mosaic runs happen in Cutroom", sent["data"].get("error", ""))

    def test_v1_v9_configurator_dom_prefill_reset_and_clip_switch(self):
        import json
        import shutil
        import subprocess
        node = shutil.which("node")
        if not node:
            self.skipTest("node not available")
        beats_html = (DDMA_DIR / "beats.html").read_text(encoding="utf-8")
        js_harness = f"""
const htmlSrc = {json.dumps(beats_html)};
function extractFn(src, name) {{
    const marker = name.includes('function ') ? name : ('function ' + name);
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
let lfConfigState = null;
let lfActiveClipNum = 3;
const elements = {{}};
function getEl(id) {{
    if (!elements[id]) elements[id] = {{ id, innerHTML: '', innerText: '', value: '', style: {{}} }};
    return elements[id];
}}
const document = {{ getElementById: getEl }};
const katex = {{ renderToString: (t) => '<span class="katex">' + t + '</span>' }};
function beatsEpisode() {{ return '249'; }}
const clipPayloads = {{
    3: {{
        success: true, ep: '249', clip_num: 3,
        title: 'Division Algebras', transcript: 'Clip three, division algebras.',
        body_duration: 87.17, hook: 'Clip three, division algebras.',
        catalog: [
            {{ section: '1. Octonions', norm: 'x = x0 e0', tex: 'x = x_0 e_0' }},
            {{ section: '1. Associator', norm: '[x,y,z] != 0', tex: '[x,y,z] \\\\neq 0' }}
        ],
        prior_equations: {{}},
        has_storyboard: true,
        stored_design: {{
            kind: 'formula', equation_norm: '[x,y,z] != 0',
            directive: 'use the associator equation',
            directive_report: 'directive-honored: equation 1',
            prompt_override: 'STORED OVERRIDE CLIP 3'
        }},
        defaults: {{
            kind: 'formula', equation_ref: 1, diagram: 'numberline',
            anchor_label: 'DIVISION ALGEBRAS', anchor_hook: 'Clip three, division algebras.',
            directive: 'use the associator equation', prompt_override: 'STORED OVERRIDE CLIP 3'
        }},
        composed_prompt: 'COMPOSED DEFAULT CLIP 3'
    }},
    1: {{
        success: true, ep: '250', clip_num: 1,
        title: 'Ultimate Anchor', transcript: 'Clip one, the ultimate anchor.',
        body_duration: 134.65, hook: 'Clip one, the ultimate anchor.',
        catalog: [{{ section: '2.1 Cancellation Law', norm: 'a(x-y)=0', tex: 'a(x-y)=0' }}],
        prior_equations: {{}},
        has_storyboard: false,
        stored_design: null,
        defaults: {{
            kind: 'anchor', equation_ref: 0, diagram: 'numberline',
            anchor_label: 'ULTIMATE ANCHOR', anchor_hook: 'Clip one, the ultimate anchor.',
            directive: '', prompt_override: ''
        }},
        composed_prompt: 'COMPOSED DEFAULT CLIP 1'
    }}
}};
async function fetch(url) {{
    const m = url.match(/clip_num=(\\d+)/);
    const c = m ? Number(m[1]) : 3;
    return {{ ok: true, status: 200, json: async () => clipPayloads[c] }};
}}
for (const fn of [
    'escapeHtml', 'renderKatexMathHtml', 'composeClientEffectivePrompt',
    'syncConfiguratorFromDom', 'updateConfiguratorPromptIfClean',
    'onConfiguratorKindChange', 'toggleEquationDropdown', 'selectCatalogEquation',
    'onConfiguratorPromptInput', 'resetConfiguratorPrompt', 'renderConfiguratorSlot',
    'async function renderManimConfigurator', 'collectConfiguratorPayload'
]) {{
    eval(extractFn(htmlSrc, fn));
}}
(async () => {{
    // 1. Load clip 3 (stored FORMULA design with prompt override)
    await renderManimConfigurator(3, {{ design: clipPayloads[3].stored_design }}, 'Last outcome: directive-honored: equation 1');
    const html3 = getEl('lf-manim-configurator').innerHTML;
    const slot3 = getEl('lf-cfg-slot-container').innerHTML;
    const state3 = Object.assign({{}}, lfConfigState);
    // Simulate unsubmitted typing on clip 3
    getEl('lf-manim-directive').value = 'UNSUBMITTED TYPING';
    getEl('lf-cfg-effective-prompt').value = 'UNSUBMITTED PROMPT EDIT';
    onConfiguratorPromptInput();
    // Reset prompt on clip 3 restores composed default
    resetConfiguratorPrompt();
    const afterResetPrompt = getEl('lf-cfg-effective-prompt').value;
    // 2. Switch to clip 1 (no stored storyboard): unsubmitted typing must not carry over, Re-render disabled
    getEl('lf-manim-directive').value = 'UNSUBMITTED TYPING';
    await renderManimConfigurator(1, null, '');
    const html1 = getEl('lf-manim-configurator').innerHTML;
    const slot1 = getEl('lf-cfg-slot-container').innerHTML;
    const state1 = Object.assign({{}}, lfConfigState);
    console.log(JSON.stringify({{
        html3, slot3, state3, afterResetPrompt, html1, slot1, state1
    }}));
}})();
"""
        proc = subprocess.run([node, "-e", js_harness],
                              capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        res = json.loads(proc.stdout.strip())
        # V1: clip 3 prefilled with formula, catalog equation 1, directive, stored prompt override, Re-render enabled
        self.assertEqual(res["state3"]["kind"], "formula")
        self.assertEqual(res["state3"]["equation_ref"], 1)
        self.assertIn("STORED OVERRIDE CLIP 3", res["html3"])
        self.assertIn("katex", res["slot3"])
        self.assertIn("1. Associator", res["slot3"])
        self.assertNotIn("disabled>Re-render", res["html3"])
        # V4: Reset to default restores composed prompt
        self.assertIn("You design ONE sustained Manim artifact", res["afterResetPrompt"])
        # V9: Switching to clip 1 drops unsubmitted typing, prefills clip 1 anchor defaults, disables Re-render (no stored design)
        self.assertEqual(res["state1"]["kind"], "anchor")
        self.assertEqual(res["state1"]["directive"], "")
        self.assertNotIn("UNSUBMITTED TYPING", res["html1"])
        self.assertIn("ULTIMATE ANCHOR", res["slot1"])
        self.assertIn("disabled>Re-render", res["html1"])


if __name__ == "__main__":
    unittest.main()
