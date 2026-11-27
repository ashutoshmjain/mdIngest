"""Unit tests for the V2 final Manim footer (Spec H2 footer V2).

Pins: plan title above the divider (shrink-to-fit, never truncated);
below-left the clip-constant ARCHETYPE (ANCHOR / FORMULA / DIAGRAM);
below-right exactly ``deepDive podcast · Ep {ep}``; every stage shows
its sentence text on the pane; display text stays at the V1 sizes
(42/34/20 title/anchor/hook... see test).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import manim_fresh_design as F


def stage(kind, text="Some sentence here.", visual=None, **hints):
    s = {"kind": kind, "title": "Clip T", "text": text,
         "labels": ["CLIP T"], "visual": visual or {},
         "_render_ep": "249"}
    s.update(hints)
    return s


class TestV2Footer(unittest.TestCase):
    def test_archetype_below_left_always(self):
        for arch, want in (("anchor", "ANCHOR"), ("formula", "FORMULA"),
                           ("diagram", "DIAGRAM"), ("", "ANCHOR"),
                           ("bogus", "ANCHOR")):
            code = F._chrome_bottom("Clip T", archetype=arch, ep="249")
            self.assertIn('"%s"' % want, code)
            self.assertIn("_arch_l", code)
        self.assertIn("Ep 249", code)

    def test_strict_right_side(self):
        code = F._chrome_bottom("Clip T", archetype="formula", ep="249")
        self.assertIn("deepDive podcast", code)
        self.assertIn("Ep 249", code)
        # Never truncated, never derived from clip data.
        self.assertIn("deepDive podcast", code)
        self.assertNotIn("...", code)

    def test_title_shrink_to_fit(self):
        code = F._chrome_bottom("What Exactly Is Reality?", archetype="anchor",
                                ep="249")
        self.assertIn("WHAT EXACTLY IS REALITY?", code)
        self.assertIn("if _btw > 6.8:", code)
        self.assertIn("bottom.scale_to_fit_width(6.8)", code)

    def test_render_uses_plan_title_and_arch_hint(self):
        s = stage("anchor",
                  visual={"type": "anchor", "label": "ULTIMATE ANCHOR",
                          "hook": "h"},
                  _render_title="8D Totality", _render_archetype="anchor")
        code = F.render_stage_manim_code(s, "ProbeT", 10.0)
        compile(code, "probe", "exec")
        self.assertIn("8D TOTALITY", code)
        self.assertIn('"ANCHOR"', code)
        self.assertIn("Ep 249", code)

    def test_arch_fallback_from_stage_kind(self):
        s = stage("formula",
                  visual={"type": "formula", "full": "a b",
                          "section": "S"})
        code = F.render_stage_manim_code(s, "ProbeF", 10.0)
        self.assertIn('"FORMULA"', code)
        s2 = stage("title", text="Clip T")
        code2 = F.render_stage_manim_code(s2, "ProbeTi", 10.0)
        self.assertIn('"ANCHOR"', code2)

    def test_sentence_on_pane_all_kinds(self):
        cases = [
            ("anchor", {"type": "anchor", "label": "L", "hook": "h"}),
            ("formula", {"type": "formula", "full": "a b",
                         "section": "S"}),
            ("diagram", {"type": "diagram", "diagram": "groundzero"}),
            ("title", {"type": "title"}),
        ]
        for kind, vis in cases:
            s = stage(kind, text="A visible sentence for %s." % kind,
                      visual=vis, _render_archetype=kind)
            code = F.render_stage_manim_code(s, "ProbeS", 10.0)
            compile(code, "probe", "exec")
            self.assertIn("_sent", code)
            self.assertIn("A visible sentence for", code)
            self.assertIn("FadeIn(_sent)", code)

    def test_sentence_fit_bounded(self):
        s = stage("title", text="Clip T " * 60)
        code = F.render_stage_manim_code(s, "ProbeL", 10.0)
        self.assertIn("6.2 / _ssw", code)
        self.assertIn("1.5 / _ssh", code)

    def test_font_sizes_unchanged(self):
        s = stage("anchor", visual={"type": "anchor", "label": "L",
                                    "hook": "h"},
                  _render_archetype="anchor")
        code = F.render_stage_manim_code(s, "ProbeF", 10.0)
        for new in ("font_size=34", "font_size=14"):
            self.assertIn(new, code)
        title_code = F.render_stage_manim_code(
            stage("title", _render_archetype="anchor"), "ProbeT", 10.0)
        self.assertIn("font_size=42", title_code)
        for old in ("font_size=52", "font_size=44", "font_size=30",
                    "font_size=24"):
            self.assertNotIn(old, code)
            self.assertNotIn(old, title_code)
        feq = F.render_stage_manim_code(
            stage("formula",
                  visual={"type": "formula", "full": "a b",
                          "section": "S"},
                  _render_archetype="formula"), "ProbeQ", 10.0)
        self.assertIn("font_size=20", feq)
        self.assertNotIn("font_size=30", feq)

    def test_format_focus_util_still_works(self):
        self.assertEqual(F._format_focus("ULTIMATE ANCHOR"),
                         "ULTIMATE ANCHOR")
        long_name = ("4. Dimensional Loss, Associative Bracketing, "
                     "and the Origin of Time")
        self.assertTrue(F._format_focus(long_name).endswith("\u2026"))


if __name__ == "__main__":
    unittest.main()
