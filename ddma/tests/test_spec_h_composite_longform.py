"""Tests for spec H composite longform (defect-specs/deepdive-spec-h-composite-longform.md).

Covers: kill rule (per-beat design stop, >1/3 reprocess stop), caption-data
exception rule, Mosaic-side naming/scale guards, run-artifact health check
(re-download by run ID + report, never substitute), retrigger duration lock,
longform publish gate, oracle regression helper.
"""
import sys
import unittest
from pathlib import Path

DDMA_DIR = Path(__file__).resolve().parent.parent
if str(DDMA_DIR) not in sys.path:
    sys.path.insert(0, str(DDMA_DIR))

import spec_h_composite_longform as H


class TestKillRule(unittest.TestCase):
    def test_per_beat_design_stops(self):
        t = H.KillRuleTracker()
        t.set_clip_count(18)
        with self.assertRaises(H.KillRuleExceeded):
            t.note_design(3, per_beat=True)

    def test_over_third_reprocessed_stops(self):
        t = H.KillRuleTracker()
        t.set_clip_count(9)
        t.note_reprocess(0)
        t.note_reprocess(1)
        t.note_reprocess(2)
        with self.assertRaises(H.KillRuleExceeded):
            t.note_reprocess(3)  # 4/9 > 1/3

    def test_trial_shape_does_not_trigger(self):
        t = H.KillRuleTracker()
        t.set_clip_count(18)
        # trial: 0 of 18 new clips reprocessed
        self.assertEqual(t.status()["reprocessed"], [])


class TestMosaicSide(unittest.TestCase):
    def test_run_artifact_naming(self):
        self.assertEqual(H.mosaic_run_artifact_name("249", 3, "abc123"),
                         "249-3-mosaic-abc123.mp4")

    def test_scale_exact_no_crop(self):
        side = H.resolve_mosaic_side("249", 3, "abc123")
        self.assertFalse(side["crop"])
        self.assertFalse(side["compiled_clip"])
        self.assertIn("1080->740", side["scale"])

    def test_missing_run_id_refuses_substitution(self):
        with self.assertRaises(ValueError):
            H.resolve_mosaic_side("249", 3, "")


class TestCaptions(unittest.TestCase):
    def test_missing_caption_data_is_reported_exception(self):
        r = H.validate_clip_captions(3, [])
        self.assertFalse(r["ok"])
        self.assertIn("exception", r["exception"])
        self.assertFalse(r["fallback_static_band"])

    def test_compiled_chunks_refused(self):
        r = H.validate_clip_captions(3, [{"w": "hi", "t": 0.0}],
                                     from_compiled_chunks=True)
        self.assertFalse(r["ok"])
        self.assertIn("+1.5", r["exception"])

    def test_body_timings_pass(self):
        r = H.validate_clip_captions(3, [{"w": "hi", "t": 0.0}])
        self.assertTrue(r["ok"])
        self.assertTrue(r["renderer"]["explicit_fontsize"])


class TestDurability(unittest.TestCase):
    def test_canonical_path(self):
        p = H.canonical_run_artifact_path("HUB", "249", 3, "abc123")
        self.assertEqual(p.name, "249-3-mosaic-abc123.mp4")
        self.assertEqual(p.parent.name, "249")

    def test_health_check_recovers_by_run_id(self, tmp_path=None):
        import tempfile
        with tempfile.TemporaryDirectory() as hub:
            dest = H.canonical_run_artifact_path(hub, "249", 3, "r1")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b"x" * 64)

            def fake_redownload(run_id, d):
                d.parent.mkdir(parents=True, exist_ok=True)
                d.write_bytes(b"y" * 64)

            clips = [{"ep": "249", "clip": 3, "run_id": "r1"},
                     {"ep": "249", "clip": 4, "run_id": "r2"}]
            res = H.health_check_run_artifacts(clips, hub, redownload_fn=fake_redownload)
            self.assertEqual(res["healthy"], [3])
            self.assertEqual(len(res["recovered"]), 1)
            self.assertIn("re-downloaded by run ID", res["recovered"][0]["report"])
            self.assertEqual(res["unrecoverable"], [])

    def test_purge_never_touches_hub_copy(self):
        import tempfile
        with tempfile.TemporaryDirectory() as cache, tempfile.TemporaryDirectory() as hub:
            (Path(cache) / "249-3-mosaic-r1.mp4").write_bytes(b"x")
            hub_copy = Path(hub) / "249-3-mosaic-r1.mp4"
            hub_copy.write_bytes(b"x")
            removed = H.purge_local_cache_only(cache)
            self.assertEqual(removed, ["249-3-mosaic-r1.mp4"])
            self.assertTrue(hub_copy.exists())


class TestWorkflow(unittest.TestCase):
    def test_retrigger_duration_lock(self):
        self.assertTrue(H.retrigger_preserves_duration(76.82, 76.82))
        with self.assertRaises(ValueError):
            H.retrigger_preserves_duration(76.82, 77.5)

    def test_exceptions_only(self):
        out = H.exceptions_only_report({1: {"status": "ok"}, 2: {"status": "FAILED", "reason": "x"}})
        self.assertEqual(list(out), [2])

    def test_formula_reuse_reported(self):
        line = H.report_formula_reuse("8 - 5 = 3", [2, 15])
        self.assertIn("reuse", line)
        self.assertIsNone(H.report_formula_reuse("x", [2]))


class TestGateAndDestination(unittest.TestCase):
    def test_gate_refuses_draft_in_substance(self, tmp_path=None):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            m = Path(d) / "movie.mp4"
            m.write_bytes(b"movie-bytes-1234567890")
            res = H.longform_publish_gate(
                m, m, baseline_structure="sig",
                structure_sampler=lambda p: "sig")
            self.assertFalse(res["ok"])
            self.assertIn("draft-in-substance", res["reason"])

    def test_gate_stops_on_master_mismatch(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            m = Path(d) / "movie.mp4"
            m.write_bytes(b"movie-bytes")
            good = Path(d) / "good.mp4"
            good.write_bytes(b"different-bytes!!")
            res = H.longform_publish_gate(m, good)
            self.assertFalse(res["ok"])
            self.assertIn("master mismatch", res["reason"])

    def test_meta_ready_signal(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "250-longform.mp4"
            dest.write_bytes(b"z")
            meta = H.write_longform_meta(dest, "ab12", 100.0, 100.0, gate_ok=True)
            self.assertTrue(meta["ready_for_distribution"])
            meta2 = H.write_longform_meta(dest, "ab12", 100.0, 100.0, gate_ok=False)
            self.assertFalse(meta2["ready_for_distribution"])
            meta3 = H.write_longform_meta(dest, "ab12", 100.0, 100.5, gate_ok=True)
            self.assertTrue(any("disagreement" in w for w in meta3["warnings"]))

    def test_oracle_helper(self):
        r = H.verify_against_oracle(list(range(21)), 1883.689, (1920, 1080))
        self.assertTrue(r["ok"])
        r2 = H.verify_against_oracle(list(range(21)), 1900.0, (1920, 1080))
        self.assertFalse(r2["ok"])


if __name__ == "__main__":
    unittest.main()
