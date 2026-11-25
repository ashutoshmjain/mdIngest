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
        f = H2.segment_filter(0)
        self.assertIn("[1:v]setsar=1[art]", f)
        self.assertIn("[2:v]scale=740:740,setsar=1[mos]", f)
        self.assertIn("[base][art]overlay=220:230[tl]", f)
        self.assertIn("[tl][mos]overlay=960:230,subtitles=caps_0.ass,"
                      "format=yuv420p[v]", f)
        self.assertNotIn("crop", f)

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


if __name__ == "__main__":
    unittest.main()
