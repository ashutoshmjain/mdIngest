"""Unit tests for per-clip Manim design directives (Spec H2 X, Part A5).

Pins: "anchor" forces kind anchor (reported); an equation name matching a
catalog entry picks that catalog member (never invented); an equation name
matching nothing degrades to anchor WITH a directive-unmatched report;
empty directive behaves exactly as today (no directive keys stored).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import manim_fresh_design as F


CATALOG = [
    {"section": "4.",
     "text": "modular flow of the observer algebra",
     "norm": F.normalize_eq("modular flow of the observer algebra")},
    {"section": "4.",
     "text": "thermal time arrow and entropy growth",
     "norm": F.normalize_eq("thermal time arrow and entropy growth")},
]

TR = "First hook sentence here. Second sentence follows it. Third ends it."


class TestDirective(unittest.TestCase):
    def test_anchor_forces_anchor(self):
        art, reports = F.design_clip_artifact(
            TR, "Clip T", 60.0, CATALOG, genai_mod=None, clip_num=5,
            directive="make this an anchor")
        d = art["design"]
        self.assertEqual(d["kind"], "anchor")
        self.assertEqual(d["directive"], "make this an anchor")
        self.assertEqual(d["directive_report"],
                         "directive-honored: forced anchor")
        self.assertTrue(any("directive-honored: forced anchor" in r
                            for r in reports))

    def test_negated_anchor_does_not_force(self):
        self.assertFalse(F._directive_forces_anchor("no anchor here"))
        self.assertFalse(F._directive_forces_anchor("without anchor"))
        self.assertTrue(F._directive_forces_anchor("anchor only"))

    def test_equation_name_picks_catalog_member(self):
        art, reports = F.design_clip_artifact(
            TR, "Clip T", 60.0, CATALOG, genai_mod=None, clip_num=5,
            directive="use the thermal-time equation")
        d = art["design"]
        self.assertEqual(d["kind"], "formula")
        self.assertEqual(d["equation_norm"], CATALOG[1]["norm"])
        self.assertEqual(d["directive"], "use the thermal-time equation")
        self.assertTrue(d["directive_report"].startswith(
            "directive-honored: equation "))
        # The picked equation is a catalog member, never invented.
        self.assertIn(d["equation_norm"], [c["norm"] for c in CATALOG])

    def test_unmatched_equation_degrades_reported(self):
        art, reports = F.design_clip_artifact(
            TR, "Clip T", 60.0, CATALOG, genai_mod=None, clip_num=5,
            directive="use the blorpt equation")
        d = art["design"]
        self.assertEqual(d["kind"], "anchor")
        self.assertIsNone(d["equation_norm"])
        self.assertEqual(d["directive"], "use the blorpt equation")
        self.assertTrue(d["directive_report"].startswith(
            "directive-unmatched:"))
        self.assertTrue(any("directive-unmatched:" in r for r in reports))

    def test_topic_hint_keeps_valid_design(self):
        art, reports = F.design_clip_artifact(
            TR, "Clip T", 60.0, CATALOG, genai_mod=None, clip_num=5,
            directive="lean into the mirror idea")
        d = art["design"]
        self.assertIn(d["kind"], ("anchor", "formula", "diagram",
                                  "title-only"))
        self.assertEqual(d["directive"], "lean into the mirror idea")
        if d["kind"] == "formula":
            self.assertIn(d["equation_norm"],
                          [c["norm"] for c in CATALOG])

    def test_empty_directive_is_historical(self):
        art, reports = F.design_clip_artifact(
            TR, "Clip T", 60.0, CATALOG, genai_mod=None, clip_num=5,
            directive="")
        d = art["design"]
        self.assertNotIn("directive", d)
        self.assertNotIn("directive_report", d)
        art2, _ = F.design_clip_artifact(
            TR, "Clip T", 60.0, CATALOG, genai_mod=None, clip_num=5)
        d2 = art2["design"]
        self.assertEqual(d["kind"], d2["kind"])
        self.assertEqual(d.get("equation_norm"), d2.get("equation_norm"))


if __name__ == "__main__":
    unittest.main()
