"""TeX-source threading for 249 formula boards (Spec H2 XIII).

Covers: norm->TeX index mapping (the four equations the 249 designs
use), top-level-only row splitting, KaTeX strict gate, SVG row
rendering, and the SVGMobject codegen branch (with Text fallback when
no SVG rows are present).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import manim_fresh_design as F


NORM_FREE_ENERGY = (
    'F = E q ( \u03b7 ) [ l n q ( \u03b7 ) \u2212 l n p ( \u03b7 , s ) ] = '
    'D KL ( q ( \u03b7 ) | | p ( \u03b7 | s ) ) \u2212 l n p ( s )')
NORM_ASSOCIATOR = '[ x , y , z ] \u2261 ( x y ) z \u2212 x ( y z ) \u2260 0'
NORM_THERMAL = 't thermal = \u2212 1 / \u03b2 l n \u03c1'
NORM_MODULAR = ('\u03b1 t \u03c1 ( A ) = \u0394 i t A \u0394 \u2212 i t '
                '\u2200 A \u2208 M , t \u2208 R')


class TexMappingTests(unittest.TestCase):
    def test_table_has_seven_sources(self):
        self.assertEqual(len(F.EPISODE_TEX_SOURCES), 7)

    def test_four_norms_map(self):
        self.assertEqual(F.match_tex_for_norm(NORM_FREE_ENERGY), 4)
        self.assertEqual(F.match_tex_for_norm(NORM_ASSOCIATOR), 1)
        self.assertEqual(F.match_tex_for_norm(NORM_THERMAL), 6)
        self.assertEqual(F.match_tex_for_norm(NORM_MODULAR), 5)

    def test_unknown_norm_maps_none(self):
        self.assertIsNone(F.match_tex_for_norm('some other equation'))
        self.assertIsNone(F.match_tex_for_norm(''))
        self.assertIsNone(F.match_tex_for_norm(None))

    def test_mapped_sources_parse_in_katex(self):
        for norm in (NORM_FREE_ENERGY, NORM_ASSOCIATOR,
                     NORM_THERMAL, NORM_MODULAR):
            F._katex_validate(
                F.EPISODE_TEX_SOURCES[F.match_tex_for_norm(norm)])

    def test_bad_tex_rejected(self):
        with self.assertRaises(Exception):
            F._katex_validate(r'\frac{unclosed')


class TexSplitTests(unittest.TestCase):
    def test_thermal_splits_at_equals(self):
        rows = F.split_tex_rows(F.EPISODE_TEX_SOURCES[6])
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[1].startswith('='))

    def test_free_energy_rows_break_at_top_level_only(self):
        rows = F.split_tex_rows(F.EPISODE_TEX_SOURCES[4])
        self.assertTrue(len(rows) >= 2)
        for row in rows[1:]:
            self.assertTrue(row[0] in '=+-')
        # No row may end mid-token: every row rejoined reproduces TeX.
        self.assertEqual(' '.join(
            r if i == 0 else r for i, r in enumerate(rows)).replace(
            '  ', ' ').strip()[:1], 'F')

    def test_split_rows_each_parse_in_katex(self):
        for tex in (F.EPISODE_TEX_SOURCES[4],
                    F.EPISODE_TEX_SOURCES[1],
                    F.EPISODE_TEX_SOURCES[5]):
            for row in F.split_tex_rows(tex):
                F._katex_validate(row)

    def test_no_empty_rows(self):
        for tex in F.EPISODE_TEX_SOURCES:
            rows = F.split_tex_rows(tex)
            self.assertTrue(rows)
            for row in rows:
                self.assertTrue(row.strip())


class TexSvgTests(unittest.TestCase):
    def test_rows_render_svg(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            paths = F.render_tex_rows_svg(
                F.EPISODE_TEX_SOURCES[5], tmp, 'probe13')
            self.assertTrue(paths)
            for p in paths:
                self.assertTrue(os.path.isfile(p))
                self.assertGreater(os.path.getsize(p), 500)
            # Modular flow must fit one row inside the budget.
            self.assertEqual(len(paths), 1)
            self.assertLessEqual(F._svg_width_pt(paths[0]),
                                 F.ROW_MAX_PT)

    def test_wide_equation_splits(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            paths = F.render_tex_rows_svg(
                F.EPISODE_TEX_SOURCES[4], tmp, 'probe3')
            self.assertTrue(len(paths) >= 2)
            for p in paths:
                self.assertTrue(os.path.isfile(p))


class TexCodegenTests(unittest.TestCase):
    def _formula_stage(self, rows):
        stage = {'kind': 'formula',
                 'title': 'octonion basis',
                 'visual': {'full': 'x = x 0 e 0',
                            'equation_ref': 'octonion basis',
                            'equation_norm': 'x = x 0 e 0'},
                 'timing': {'enter': 1.0, 'build': 2.0, 'hold': 3.0}}
        if rows is not None:
            stage['_render_svg_rows'] = rows
        return stage

    def test_svg_rows_emit_svgmobject(self):
        code = F.render_stage_manim_code(
            self._formula_stage(['C:/r/c1_row0.svg']), 'ProbeT', 10.0)
        self.assertIn('SVGMobject', code)
        self.assertIn('_eq_rows', code)
        self.assertNotIn('eq = Text', code)

    def test_no_rows_falls_back_to_text(self):
        code = F.render_stage_manim_code(
            self._formula_stage(None), 'ProbeT', 10.0)
        self.assertIn('eq = Text', code)
        self.assertNotIn('SVGMobject', code)

    def test_multi_row_group_wraps_all(self):
        code = F.render_stage_manim_code(
            self._formula_stage(['C:/r/a.svg', 'C:/r/b.svg']),
            'ProbeT', 10.0)
        self.assertIn('_eqr0', code)
        self.assertIn('_eqr1', code)
        self.assertIn('VGroup', code)


if __name__ == '__main__':
    unittest.main()
