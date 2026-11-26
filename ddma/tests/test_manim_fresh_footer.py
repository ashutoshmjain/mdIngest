"""Unit tests for the redesigned two-row Manim footer (Spec H2 XI).

Pins: title above the line; focus left + podcast credit right below the
line (the sub-row always renders, even when the focus is blank);
display text dropped two notches (52/44/30/24 -> 42/34/20/14).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import manim_fresh_design as F


class TestFreshFooter(unittest.TestCase):
    def test_two_row_chrome(self):
        code = F._chrome_bottom("Clip T", focus_left="ULTIMATE ANCHOR",
                                ep="249")
        self.assertIn("ULTIMATE ANCHOR", code)
        self.assertIn("deepDive podcast", code)
        self.assertIn("Ep 249", code)
        self.assertIn("_focus_l", code)
        self.assertIn("_focus_r", code)
        self.assertIn("self.add(_cover, bottom, foot, _focus_l, _focus_r)",
                      code)

    def test_blank_focus_still_has_sub_row(self):
        # Title-only clips leave below-left blank, but the sub-row
        # (cover + line + right credit) still renders.
        code = F._chrome_bottom("Clip T", focus_left="", ep="249")
        self.assertNotIn("_focus_l", code)
        self.assertIn("_focus_r", code)
        self.assertIn("Ep 249", code)

    def test_long_focus_truncates_with_ellipsis(self):
        long_name = ("4. Dimensional Loss, Associative Bracketing, "
                     "and the Origin of Time")
        got = F._format_focus(long_name)
        self.assertTrue(got.endswith("\u2026"))
        self.assertLessEqual(len(got), F.FOCUS_MAX_CHARS + 1)
        self.assertNotIn("  ", got)
        # Short names pass through untouched.
        self.assertEqual(F._format_focus("ULTIMATE ANCHOR"),
                         "ULTIMATE ANCHOR")

    def test_chrome_title_uses_plan_title_hint(self):
        stage = {"kind": "anchor", "title": "Ultimate Anchor",
                 "visual": {"type": "anchor", "label": "ULTIMATE ANCHOR",
                            "hook": "h"},
                 "_render_ep": "249", "_render_title": "8D Totality"}
        code = F.render_stage_manim_code(stage, "ProbeT", 10.0)
        compile(code, "probe", "exec")
        self.assertIn("8D TOTALITY", code)
        # The design label stays below-left as the focus.
        self.assertIn("_focus_l", code)

    def test_stage_code_carries_focus_and_ep(self):
        stage = {"kind": "anchor", "title": "Ultimate Anchor",
                 "visual": {"type": "anchor", "label": "ULTIMATE ANCHOR",
                            "hook": "hook."},
                 "_render_focus": "ULTIMATE ANCHOR", "_render_ep": "249"}
        code = F.render_stage_manim_code(stage, "ProbeF", 10.0)
        compile(code, "probe", "exec")
        self.assertIn("ULTIMATE ANCHOR", code)
        self.assertIn("Ep 249", code)

    def test_font_drop_two_notches(self):
        stage = {"kind": "anchor", "title": "T",
                 "visual": {"type": "anchor", "label": "L", "hook": "h"},
                 "_render_ep": "249"}
        code = F.render_stage_manim_code(stage, "ProbeF", 10.0)
        for new in ("font_size=34", "font_size=14"):
            self.assertIn(new, code)
        title_code = F.render_stage_manim_code(
            {"kind": "title", "title": "T",
             "visual": {"type": "title"}, "_render_ep": "249"},
            "ProbeT", 10.0)
        self.assertIn("font_size=42", title_code)
        for old in ("font_size=52", "font_size=44", "font_size=30",
                     "font_size=24"):
            self.assertNotIn(old, code)
            self.assertNotIn(old, title_code)
        feq = F.render_stage_manim_code(
            {"kind": "formula", "title": "T",
             "visual": {"type": "formula", "full": "a b",
                        "section": "S"},
             "_render_ep": "249"}, "ProbeQ", 10.0)
        self.assertIn("font_size=20", feq)
        self.assertNotIn("font_size=30", feq)


if __name__ == "__main__":
    unittest.main()
