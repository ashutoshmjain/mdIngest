import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import manim_fresh_design as F


OCTO_TR = ("Clip one, the eight-dimensional totality. It starts in eight-dimensional "
           "mathematical space known as the octonians. The whole substrate identity.")
ASSOC_TR = ("Clip three, the division algebras. The 8d octonians are too chaotic. "
            "They are not associative. The brackets keep shifting. Hurwitz and Frobenius.")


class TestDeterministicChoice(unittest.TestCase):
    def setUp(self):
        self.cat = F.fetch_episode_equations("249")
        self.assertGreaterEqual(len(self.cat), 3)

    def test_octonion_clip_gets_basis_equation(self):
        art, _ = F.design_clip_artifact(OCTO_TR, "8D Totality", 60.0, self.cat, genai_mod=None, clip_num=1)
        d = art["design"]
        self.assertEqual(d["kind"], "formula")
        self.assertEqual(d["equation_norm"], self.cat[0]["norm"])
        self.assertEqual(art["stages"][0]["kind"], "title")
        self.assertAlmostEqual(art["stages"][-1]["end"], 60.0)

    def test_title_gate_blocks_transcript_only_match(self):
        art, _ = F.design_clip_artifact(OCTO_TR, "Unrelated Title Here", 60.0, self.cat, genai_mod=None, clip_num=9)
        self.assertEqual(art["design"]["kind"], "anchor")

    def test_deterministic_reuse_reported(self):
        art1, _ = F.design_clip_artifact(ASSOC_TR, "Division Algebras", 60.0, self.cat, genai_mod=None, clip_num=3)
        norm = art1["design"]["equation_norm"]
        self.assertIsNotNone(norm)
        art2, _ = F.design_clip_artifact(ASSOC_TR, "Division Algebras", 60.0, self.cat, genai_mod=None,
                                         prior_equations={"3": norm}, clip_num=8)
        d2 = art2["design"]
        self.assertEqual(d2["reuse_of"], "3")
        self.assertTrue(any("reuse" in r for r in d2["reports"]))

    def test_hook_skips_filler(self):
        self.assertEqual(F.hook_sentence("Okay. So um. Reality is not what it seems today. Next."),
                         "Reality is not what it seems today.")

    def test_equation_display_short_and_plain(self):
        art, _ = F.design_clip_artifact(OCTO_TR, "8D Totality", 60.0, self.cat, genai_mod=None, clip_num=1)
        disp = art["design"]["equation_text"] or ""
        self.assertLessEqual(len(disp), 280)
        self.assertNotIn("katex", disp)


if __name__ == "__main__":
    unittest.main()
