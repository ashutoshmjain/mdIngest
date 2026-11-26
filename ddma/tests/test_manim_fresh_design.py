"""Unit tests for H2 fresh-cast Manim design (manim_fresh_design).

Pins: fresh means fresh (never cache/plan reuse), equation must be an
episode-page catalog member (invented degrades + reported), cap of one
visual, stages cover the clip at sentence boundaries, reuse reported,
templates are valid Manim (Text only, no Tex).
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import manim_fresh_design as F


CATALOG = [
    {"section": "S1", "text": "x = y + 1 where y is late", "norm": F.normalize_eq("x = y + 1 where y is late")},
    {"section": "S2", "text": "A implies B always", "norm": F.normalize_eq("A implies B always")},
]

TR = "First hook sentence here. Second sentence follows it. Third ends it."


class _Resp:
    def __init__(self, text):
        self.text = text


class _Model:
    def __init__(self, payload):
        self._payload = payload

    def generate_content(self, prompt):
        return _Resp(self._payload)


class _FakeGenai:
    def __init__(self, payload):
        self._payload = payload

    def GenerativeModel(self, name):
        return _Model(self._payload)


def _choice(**kw):
    base = {"kind": "anchor", "equation_ref": None, "equation_display": "",
            "anchor_label": "HOOK", "diagram": None, "reason": "test"}
    base.update(kw)
    return json.dumps(base)


class TestFreshDesign(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(F.normalize_eq("  a   b 1 2 "), "a b")
        self.assertEqual(F.normalize_eq("x" + chr(8203) + "y"), "xy")

    def test_sentences_and_hook(self):
        sents = F.split_sentences(TR)
        self.assertEqual(len(sents), 3)
        self.assertEqual(F.hook_sentence(TR), "First hook sentence here.")

    def test_fallback_anchor_reported(self):
        art, reports = F.design_clip_artifact(TR, "Clip T", 60.0, CATALOG, genai_mod=None, clip_num=1)
        d = art["design"]
        self.assertEqual(d["kind"], "anchor")
        self.assertTrue(any("deterministic" in r for r in reports + d["reports"]))
        st = art["stages"]
        self.assertEqual(st[0]["kind"], "title")
        self.assertAlmostEqual(st[0]["start"], 0.0)
        self.assertAlmostEqual(st[-1]["end"], 60.0)
        for a, b in zip(st, st[1:]):
            self.assertAlmostEqual(a["end"], b["start"])

    def test_invented_equation_rejected(self):
        g = _FakeGenai(_choice(kind="equation", equation_ref=99, equation_display="E = mc2 invented"))
        art, _ = F.design_clip_artifact(TR, "Clip T", 60.0, CATALOG, genai_mod=g, clip_num=1)
        d = art["design"]
        self.assertEqual(d["kind"], "anchor")
        self.assertIsNone(d["equation_norm"])
        self.assertTrue(any("not-on-page" in r for r in d["reports"]))

    def test_catalog_equation_accepted(self):
        g = _FakeGenai(_choice(kind="equation", equation_ref=0, equation_display="x = y + 1"))
        art, _ = F.design_clip_artifact(TR, "Clip T", 60.0, CATALOG, genai_mod=g, clip_num=2)
        d = art["design"]
        self.assertEqual(d["kind"], "formula")
        self.assertEqual(d["equation_norm"], CATALOG[0]["norm"])
        self.assertIsNone(d["reuse_of"])

    def test_reuse_reported(self):
        g = _FakeGenai(_choice(kind="equation", equation_ref=1, equation_display="A implies B"))
        prior = {"5": CATALOG[1]["norm"]}
        art, _ = F.design_clip_artifact(TR, "Clip T", 60.0, CATALOG, genai_mod=g, prior_equations=prior, clip_num=2)
        d = art["design"]
        self.assertEqual(d["reuse_of"], "5")
        self.assertTrue(any("reuse" in r for r in d["reports"]))

    def test_cap_one_visual(self):
        g = _FakeGenai(_choice(kind="diagram", diagram="tunnel"))
        art, _ = F.design_clip_artifact(TR, "Clip T", 90.0, CATALOG, genai_mod=g, clip_num=1)
        kinds = {s["kind"] for s in art["stages"]}
        self.assertTrue(kinds <= {"title", "diagram"})

    def test_title_only_reported(self):
        g = _FakeGenai(_choice(kind="title-only"))
        art, _ = F.design_clip_artifact(TR, "Clip T", 30.0, CATALOG, genai_mod=g, clip_num=1)
        self.assertEqual(art["design"]["kind"], "title-only")
        self.assertTrue(any("title-only" in r for r in art["design"]["reports"]))

    def test_templates_compile_no_tex(self):
        vis = {"formula": {"type": "formula", "full": "x = y + 1 over two for all cases here"},
               "tunnel": {"type": "diagram", "diagram": "tunnel"},
               "numberline": {"type": "diagram", "diagram": "numberline"},
               "groundzero": {"type": "diagram", "diagram": "groundzero"},
               "anchor": {"type": "anchor", "label": "HOOK", "hook": "hook words"},
               "title": {"type": "title"}}
        kinds = {"formula": "formula", "tunnel": "diagram", "numberline": "diagram",
                 "groundzero": "diagram", "anchor": "anchor", "title": "title"}
        for name, v in vis.items():
            s = {"kind": kinds[name], "title": "T", "text": "t", "labels": ["T"],
                 "visual": dict(v, progress=0.5)}
            code = F.render_stage_manim_code(s, "ProbeX", 10.0)
            self.assertNotIn("Tex(", code)
            compile(code, "<probe>", "exec")

    def test_display_parser(self):
        html = ('<h2>Sec Alpha</h2><p>words</p>'
                '<span class="katex-display"><span class="base">a = b</span></span>'
                '<h2>Sec Beta</h2>'
                '<span class="katex-display"><span class="base">c = d</span></span>')
        p = F._DisplayMathParser()
        p.feed(html)
        self.assertEqual(len(p.blocks), 2)
        self.assertEqual(p.blocks[0]["section"], "Sec Alpha")
        self.assertIn("a = b", p.blocks[0]["text"])


if __name__ == "__main__":
    unittest.main()
