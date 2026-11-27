"""Carousel sync for the episode-page clip carousel (publish time).

When a Cutroom clip publish succeeds, ``sync_carousel_card`` adds the
clip's card to ``src/<ep>.md`` inside the ``video-carousel-container``
div -- in clip-number order, in the EXACT existing card format -- or
reports why it did nothing. Called from the publish handler in
``scratch/run_curator.py`` after the plan is flagged published and
before the scoped publish commit, so the ``.md`` change rides the
same commit as the clip.

Rules (per deepdive-spec-carousel-auto-sync.md):
- preconditions: the compiled mp4 exists at
  ``src/ddma/docs/episodes/<ep>/clips/<ep>-<n>.mp4`` AND the plan
  marks the clip ``published:true``. Otherwise no card is added and
  the reason is reported (a card with a dead video is never allowed).
- idempotent: an existing card (same ``<video src>``) is reported
  "already present", never duplicated.
- add-only: never removes a card, never reorders existing cards,
  never touches other episodes, the Reels tab, or the Research tab.
"""
import io
import json
import os
import re

CARD_OPEN = ('  <div style="flex: 0 0 60%; scroll-snap-align: center; '
             'position: relative; border-radius: 12px; overflow: hidden; '
             'background: #000; aspect-ratio: 1/1; display: flex; '
             'flex-direction: column; '
             'box-shadow: 0 4px 15px rgba(0,0,0,0.3);">')
VIDEO = ('    <video src="ddma/docs/episodes/{ep}/clips/{ep}-{n}.mp4" '
         'style="width: 100%; height: 85%; object-fit: contain;" '
         'playsinline loop preload="auto" muted autoplay></video>')
LABEL = ('    <div style="height: 15%; background: #1a1a1a; color: #ccc; '
         'display: flex; align-items: center; justify-content: center; '
         'font-family: monospace; font-size: 12px; '
         'border-top: 1px solid #333;">{ep}-{n} {title}</div>')
BUTTON = ('    <button class="vid-toggle" '
          'onclick="window.oph_play_toggle(this)" style="position: absolute; '
          'top: 10px; right: 10px; background: rgba(0,0,0,0.8); '
          'color: white; border: 2px solid white; border-radius: 50%; '
          'width: 45px; height: 45px; cursor: pointer; font-size: 22px; '
          'z-index: 100;">\U0001f507</button>')
CARD_CLOSE = '  </div>'
NL = '\r\n'
CARD_SRC_RE = r'<video src="ddma/docs/episodes/%s/clips/%s-%s\.mp4"'


def render_card(ep_num, clip_num, title):
    return NL.join([CARD_OPEN,
                    VIDEO.format(ep=ep_num, n=clip_num),
                    LABEL.format(ep=ep_num, n=clip_num, title=title),
                    BUTTON, CARD_CLOSE])


def _read(path):
    with io.open(path, 'r', encoding='utf-8', newline='') as fh:
        return fh.read()


def _write(path, text):
    assert text.count('\n') == text.count('\r\n'), \
        'bare LF would corrupt %s' % path
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


def _plan_clip(repo_root, ep_num, clip_num):
    plan_path = os.path.join(repo_root, 'ddma', 'projects',
                             'episode_%s' % ep_num, 'plan.json')
    if not os.path.isfile(plan_path):
        return None, 'plan not found: %s' % plan_path
    with io.open(plan_path, encoding='utf-8-sig') as fh:
        plan = json.load(fh)
    for c in plan:
        if str(c.get('num')) == str(clip_num):
            return c, ''
    return None, 'clip %s not in %s' % (clip_num, plan_path)


def sync_carousel_card(repo_root, ep_num, clip_num):
    """Add one carousel card; return (status, detail).

    status is one of "card added" / "already present" /
    "not added (reason)". Never raises for carousel-level problems
    (missing page, missing container); raises only on unreadable
    plan JSON or an unparseable write so the caller notices.
    """
    ep_num, clip_num = str(ep_num), str(clip_num)
    clip, err = _plan_clip(repo_root, ep_num, clip_num)
    if clip is None:
        return 'not added (%s)' % err, err
    if not clip.get('published'):
        reason = 'plan does not mark clip %s-%s published' % (
            ep_num, clip_num)
        return 'not added (%s)' % reason, reason
    title = clip.get('title') or ''
    if not title:
        reason = 'plan clip %s-%s has no title' % (ep_num, clip_num)
        return 'not added (%s)' % reason, reason
    mp4 = os.path.join(repo_root, 'src', 'ddma', 'docs', 'episodes',
                       ep_num, 'clips', '%s-%s.mp4' % (ep_num, clip_num))
    if not (os.path.isfile(mp4) and os.path.getsize(mp4) > 0):
        reason = 'mp4 missing: %s' % os.path.relpath(mp4, repo_root)
        return 'not added (%s)' % reason, reason
    page = os.path.join(repo_root, 'src', '%s.md' % ep_num)
    if not os.path.isfile(page):
        reason = 'no episode page: src/%s.md' % ep_num
        return 'not added (%s)' % reason, reason
    text = _read(page)
    src_re = CARD_SRC_RE % (ep_num, ep_num, re.escape(clip_num))
    if re.search(src_re, text):
        return 'already present', '%s-%s card present' % (
            ep_num, clip_num)
    m = re.search(r'(<div class="video-carousel-container"[^>]*>'
                  r'\r\n)(.*?)(\r\n</div>\r\n\r\n<center>)',
                  text, re.DOTALL)
    if not m:
        reason = 'no video-carousel-container in src/%s.md' % ep_num
        return 'not added (%s)' % reason, reason
    head, body, tail = m.group(1), m.group(2), m.group(3)
    # The template must match the page's own cards byte-for-byte.
    existing = re.findall(
        r'<video src="ddma/docs/episodes/%s/clips/%s-(\d+)\.mp4"'
        % (ep_num, ep_num), body)
    if existing:
        first = existing[0]
        lab = re.search(r'>%s-%s (.*?)</div>' % (ep_num, first), body)
        probe = render_card(ep_num, first,
                            lab.group(1) if lab else '')
        if not body.lstrip('\r\n').startswith(probe):
            reason = 'card format drift in src/%s.md' % ep_num
            return 'not added (%s)' % reason, reason
    nums = sorted(int(n) for n in existing)
    new_card = render_card(ep_num, clip_num, title)
    if not nums or int(clip_num) > nums[-1]:
        # body ends with the last card; tail starts with the
        # container close. Existing order is kept as-is.
        new_body = body + NL + new_card if body else new_card
        anchor_old = body + tail
        anchor_new = new_body + tail
    else:
        nxt = next(n for n in nums if n > int(clip_num))
        nxt_open = CARD_OPEN + NL + ' ' * 4 + '<video src="ddma/docs/episodes/%s/clips/%s-%d.mp4"' % (ep_num, ep_num, nxt)
        idx = body.find(nxt_open)
        if idx < 0:
            reason = 'anchor card %s-%d not found' % (ep_num, nxt)
            return 'not added (%s)' % reason, reason
        new_body = body[:idx] + new_card + NL + body[idx:]
        anchor_old = head + body + tail
        anchor_new = head + new_body + tail
    if anchor_old not in text:
        reason = 'carousel anchor mismatch in src/%s.md' % ep_num
        return 'not added (%s)' % reason, reason
    if not nums or int(clip_num) > nums[-1]:
        new_text = text.replace(body + tail, new_body + tail, 1)
    else:
        new_text = text.replace(anchor_old, anchor_new, 1)
    _write(page, new_text)
    return 'card added', '%s-%s %s' % (ep_num, clip_num, title)
