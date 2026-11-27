"""Unit tests for the publish-time carousel sync (Spec auto-sync V1).

Fixture: a fake repo root with ddma/projects/episode_999/plan.json,
src/999.md (carousel container + 2 cards), and
src/ddma/docs/episodes/999/clips/ mp4s. Covers: add, already-present
no-op, mp4-missing refusal, unpublished refusal, numeric order
insertion. Asserts CRLF purity is preserved.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import carousel_sync as C

CARD_TMPL = None  # built per fixture from C.render_card


def make_repo(cards=(0, 2), published=(0, 1, 2), mp4s=(0, 1, 2)):
    root = tempfile.mkdtemp(prefix='carouselsync_')
    os.makedirs(os.path.join(root, 'ddma', 'projects', 'episode_999'))
    os.makedirs(os.path.join(root, 'src', 'ddma', 'docs', 'episodes',
                             '999', 'clips'))
    plan = [{'num': n, 'title': 'Clip %d' % n,
             'published': (n in published),
             'published_url': 'http://x/%d.mp4' % n if n in published
             else None}
            for n in (0, 1, 2)]
    with io.open(os.path.join(root, 'ddma', 'projects', 'episode_999',
                              'plan.json'),
                 'w', encoding='utf-8', newline='') as fh:
        json.dump(plan, fh)
    for n in mp4s:
        with io.open(os.path.join(root, 'src', 'ddma', 'docs',
                                  'episodes', '999', 'clips',
                                  '999-%d.mp4' % n),
                     'wb') as fh:
            fh.write(b'\x00' * 16)
    body = '\r\n'.join(C.render_card('999', n, 'Clip %d' % n)
                       for n in cards)
    page = ('# 999 : Fixture\r\n\r\n<!-- VIDEO_STRIP_START -->\r\n'
            '<div class="video-carousel-container" style="x">\r\n'
            + body + '\r\n</div>\r\n\r\n<center>social</center>\r\n')
    with io.open(os.path.join(root, 'src', '999.md'),
                 'w', encoding='utf-8', newline='') as fh:
        fh.write(page)
    return root


def read_page(root):
    with io.open(os.path.join(root, 'src', '999.md'), encoding='utf-8',
                 newline='') as fh:
        return fh.read()


def card_nums(text):
    import re
    return [int(n) for n in re.findall(
        r'999-(\d+)\.mp4', text)]


class CarouselSyncTests(unittest.TestCase):
    def setUp(self):
        self.roots = []

    def tearDown(self):
        for r in self.roots:
            shutil.rmtree(r, ignore_errors=True)

    def repo(self, **kw):
        r = make_repo(**kw)
        self.roots.append(r)
        return r

    def test_add_inserts_in_order(self):
        # clip 1 published + mp4 present; cards hold 0 and 2.
        r = self.repo()
        status, detail = C.sync_carousel_card(r, 999, 1)
        self.assertEqual(status, 'card added')
        nums = card_nums(read_page(r))
        self.assertEqual(nums, [0, 1, 2])

    def test_already_present_no_duplicate(self):
        r = self.repo()
        status, _ = C.sync_carousel_card(r, 999, 0)
        self.assertEqual(status, 'already present')
        text = read_page(r)
        self.assertEqual(text.count('999-0.mp4'), 1)
        self.assertEqual(card_nums(text), [0, 2])

    def test_refuses_missing_mp4(self):
        # clip 1 published but its mp4 is absent.
        r = self.repo(mp4s=(0, 2))
        status, detail = C.sync_carousel_card(r, 999, 1)
        self.assertTrue(status.startswith('not added'))
        self.assertIn('mp4', detail)
        self.assertEqual(card_nums(read_page(r)), [0, 2])

    def test_refuses_unpublished(self):
        # clip 1 has an mp4 but the plan does not flag it.
        r = self.repo(published=(0, 2), mp4s=(0, 1, 2))
        status, detail = C.sync_carousel_card(r, 999, 1)
        self.assertTrue(status.startswith('not added'))
        self.assertIn('published', detail)
        self.assertEqual(card_nums(read_page(r)), [0, 2])

    def test_append_after_last(self):
        r = self.repo(cards=(0, 1), published=(0, 1, 2), mp4s=(0, 1, 2))
        status, _ = C.sync_carousel_card(r, 999, 2)
        self.assertEqual(status, 'card added')
        self.assertEqual(card_nums(read_page(r)), [0, 1, 2])

    def test_crlf_preserved(self):
        r = self.repo()
        C.sync_carousel_card(r, 999, 1)
        raw = io.open(os.path.join(r, 'src', '999.md'),
                      'rb').read()
        self.assertGreater(raw.count(b'\r\n'), 0)
        self.assertEqual(raw.count(b'\n'), raw.count(b'\r\n'))

    def test_format_matches_existing(self):
        r = self.repo()
        C.sync_carousel_card(r, 999, 1)
        text = read_page(r)
        self.assertIn(C.render_card('999', 1, 'Clip 1'), text)


if __name__ == '__main__':
    unittest.main()
