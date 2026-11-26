"""H2 fresh-cast Manim design (new rules, Spec H s3 + Severity-1 stale-Manim fix).

Every design request means a FRESH cast: this module never reads a cached
storyboard file and never reuses a plan clip's existing infographic_scenes.
It generates a new design from the clip's transcript text + title + the
episode-page equation catalog, implements the new rules (one sustained
artifact per clip: title first, one equation OR one diagram OR one anchor
label+arrow, stages at sentence boundaries, no archetype list, no reuse
without a report), and renders deterministic Manim code (white-on-black
Text only -- no LaTeX/Tex in this environment).
"""

import json
import os
import re
import urllib.request
from html.parser import HTMLParser

EPISODE_PAGE_URL = "https://deepdive.shutri.com/{ep}.html"

FRESH_KINDS = ("title", "formula", "diagram", "anchor", "title-only")
DIAGRAM_KINDS = ("tunnel", "numberline", "groundzero")

_ZW = "\u200b\ue020\uf000\uf001"


def normalize_eq(text):
    """Canonical form for equation comparison (catalog membership, reuse)."""
    t = str(text or "")
    for ch in _ZW:
        t = t.replace(ch, "")
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"(\s\d+)+$", "", t).strip()
    return t


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", str(text or "").strip())
    return [p.strip() for p in parts if p.strip()]


def hook_sentence(transcript):
    sents = split_sentences(transcript)
    for s in sents:
        words = re.sub(r"[^a-z ]", "", s.lower()).split()
        if len(words) >= 4 and not (words and words[0] in ('okay', 'ok', 'so', 'um', 'uh', 'well', 'right', 'yeah', 'yes', 'hi', 'hey', 'alright') and len(words) <= 6):
            return s
    return sents[0] if sents else ""


class _DisplayMathParser(HTMLParser):
    """Collect text strictly inside span.katex-display blocks + section head."""

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.buf = []
        self.blocks = []
        self.section = ""
        self._in_head = False
        self._head = ""

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3"):
            self._in_head = True
            self._head = ""
            return
        if tag == "span":
            cls = ""
            for k, v in attrs:
                if k == "class":
                    cls = v
            if "katex-display" in cls:
                if self.depth == 0:
                    self.buf = []
                self.depth += 1
                self.buf.append(' ')
            elif self.depth > 0:
                self.depth += 1
                self.buf.append(' ')

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3"):
            if self._head.strip():
                self.section = re.sub(r"\s+", " ", self._head).strip()[:100]
            self._in_head = False
            return
        if tag == "span" and self.depth > 0:
            self.depth -= 1
            self.buf.append(' ')
            if self.depth == 0:
                txt = re.sub(r"\s+", " ", "".join(self.buf)).strip()
                if len(txt) > 4:
                    self.blocks.append({"section": self.section, "text": txt})
                self.buf = []

    def handle_data(self, data):
        if self._in_head:
            self._head += data
        elif self.depth > 0:
            self.buf.append(data)


def fetch_episode_equations(ep_num, cache_path=None, refresh=False):
    """Episode-page equation catalog: [{section, text, norm}]. Cached JSON."""
    if cache_path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        cache_path = os.path.join(here, "scratch", f"ep{ep_num}_equations_v2.json")
    if os.path.exists(cache_path) and not refresh:
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    url = EPISODE_PAGE_URL.format(ep=ep_num)
    req = urllib.request.Request(url, headers={"User-Agent": "deepdive-h2/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html_text = r.read().decode("utf-8", "replace")
    parser = _DisplayMathParser()
    parser.feed(html_text)
    catalog = []
    seen = set()
    for b in parser.blocks:
        norm = normalize_eq(b["text"])
        if len(norm) < 6 or norm in seen:
            continue
        seen.add(norm)
        catalog.append({"section": b["section"], "text": b["text"][:400],
                        "norm": norm})
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=1)
    except Exception:
        pass
    return catalog


_FRESH_PROMPT = """You design ONE sustained Manim artifact for a single podcast clip.
Transcript (this clip only):
{transcript}

Clip title: {title}
Clip duration: {body_duration:.1f}s. Sentences ({n_sent}): {sent_list}

Candidate equations from the episode page (use ONLY these; never invent):
{catalog}

Equations already used by other clips (avoid; reuse must be reported, so prefer an unused one):
{prior}

NEW DESIGN RULES (absolute):
1. ONE design call for this clip; output ONE artifact: the clip title first, plus AT MOST ONE of: (a) an equation from the catalog above, (b) one diagram, (c) one anchor (a label + arrow keyed to the hook sentence below). Never a list of per-beat scenes. Never a figurative cartoon, never an archetype.
2. Equation ONLY if it is that clip's own (it must match the transcript topic). If none fits, choose diagram or anchor. If the clip has no suitable artifact at all, choose title-only.
3. Hook sentence (first sentence, for the anchor fallback): {hook}
4. Formula reuse across clips is allowed only when the equation genuinely belongs to both clips; it is reported, never silent.

Return ONLY a JSON object, no other text:
{{"kind": "equation|diagram|anchor|title-only",
  "equation_ref": <catalog index or null>,
  "equation_display": "<short display form, <=140 chars, plain unicode, no TeX commands>",
  "anchor_label": "<1-4 WORD LABEL or null>",
  "diagram": "tunnel|numberline|groundzero|null",
  "reason": "<one line: why this artifact is this clip's own>"}}"""


def _gemini_fresh_choice(transcript, title, body_duration, catalog, prior,
                         genai_mod, hook, instruction=None):
    if genai_mod is None:
        return None
    cat_lines = [f"[{i}] ({c['section'][:60]}) {c['norm'][:200]}"
                 for i, c in enumerate(catalog)]
    sents = split_sentences(transcript)
    prompt = _FRESH_PROMPT.format(
        transcript=transcript[:6000], title=title,
        body_duration=body_duration, n_sent=len(sents),
        sent_list=json.dumps(sents[:12], ensure_ascii=False)[:1500],
        catalog="\n".join(cat_lines) if cat_lines else "(none)",
        prior=json.dumps(prior, ensure_ascii=False)[:800] or "(none)",
        hook=hook[:300])
    if instruction:
        prompt += ("\nUser design instruction for this clip (honor it; the "
                   "catalog-membership rule still applies): "
                   + str(instruction)[:300])
    for m_name in ["gemini-3.5-flash-lite", "gemini-flash-lite-latest",
                   "gemini-3.5-flash", "gemini-3.8-flash"]:
        try:
            m = genai_mod.GenerativeModel(m_name)
            res = m.generate_content(prompt)
            raw = res.text.strip()
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            choice = json.loads(raw)
            if isinstance(choice, dict) and choice.get("kind") in (
                    "equation", "diagram", "anchor", "title-only"):
                return choice
        except Exception as e_m:
            print(f"[FreshDesign] Gemini {m_name} failed: {e_m}")
            continue
    return None


def _wrap_lines(text, width=38):
    words = str(text or "").split()
    lines, cur = [], ""
    for w in words:
        if len((cur + " " + w).strip()) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return chr(10).join(lines) if lines else ""


def _build_stages(title, kind, visual, transcript, body_duration):
    """Stages at sentence boundaries: title stage, then build stages of the
    ONE visual. Returns (stages, reports)."""
    sents = split_sentences(transcript)
    if not sents:
        sents = [title]
    groups = [[sents[0]]]
    rest = sents[1:]
    n_build = min(5, max(1, len(rest)))
    if rest:
        per = max(1, (len(rest) + n_build - 1) // n_build)
        for i in range(0, len(rest), per):
            groups.append(rest[i:i + per])
    lens = [max(1, sum(len(s) for s in g)) for g in groups]
    total = float(sum(lens))
    stages, t = [], 0.0
    for gi, g in enumerate(groups):
        dur = max(3.0, body_duration * lens[gi] / total)
        start = round(t, 2)
        end = round(body_duration if gi == len(groups) - 1 else t + dur, 2)
        t += dur
        if gi == 0:
            skind, text = "title", title
        else:
            skind = kind if kind in ("formula", "diagram", "anchor") else "title"
            text = " ".join(g)[:220]
        frac = (gi) / max(1, len(groups) - 1) if len(groups) > 1 else 1.0
        stages.append({"start": start, "end": end, "kind": skind,
                       "title": title, "text": text,
                       "labels": [title.upper()[:24]],
                       "archetype": f"fresh-{skind}",
                       "footer_label": skind.upper(),
                       "visual": dict(visual, progress=round(frac, 3),
                                      stage_index=gi,
                                      stage_count=len(groups))})
    return stages, []


def design_clip_artifact(transcript, title, body_duration, catalog,
                         genai_mod=None, prior_equations=None, clip_num=None,
                         directive=None):
    """Fresh-cast ONE artifact. Returns (storyboard_design_dict, reports).

    Never reads caches or plan scenes. The returned equation (if any) is
    always a catalog member; anything else degrades to anchor/title-only
    and is reported. A non-empty directive (per-clip design instruction)
    is honored deterministically: unnegated "anchor" forces kind anchor;
    an equation name picks the best-matching catalog member (never
    invented); anything else acts as a topic hint. Empty directive means
    exactly the historical behavior (no directive keys are stored).
    """
    reports = []
    transcript = str(transcript or "").strip()
    title = str(title or "Deep Dive").strip()
    hook = hook_sentence(transcript)
    prior = prior_equations or {}
    directive = str(directive or "").strip()
    directive_outcome = ""
    forced = None
    if directive:
        if _directive_forces_anchor(directive):
            forced = ("anchor", None, "directive-honored: forced anchor")
        else:
            _idx = _directive_equation_match(directive, catalog)
            if _idx is not None:
                forced = ("equation", _idx,
                          "directive-honored: equation " + str(_idx))
            elif _directive_names_equation(directive):
                forced = ("anchor", None,
                          "directive-unmatched: no catalog equation matched '"
                          + directive[:120] + "'; degraded to anchor")
    if forced is not None:
        kind_name, ref = forced[0], forced[1]
        directive_outcome = forced[2]
        if kind_name == "anchor":
            choice = {"kind": "anchor", "anchor_label": None,
                      "equation_ref": None, "equation_display": "",
                      "diagram": None,
                      "reason": "directive forced anchor"}
        else:
            entry = catalog[ref]
            choice = {"kind": "equation", "equation_ref": ref,
                      "equation_display": entry.get("norm", ""),
                      "anchor_label": None, "diagram": None,
                      "reason": "directive picked catalog member"}
        reports.append("directive: " + directive[:200])
        reports.append(directive_outcome)
    else:
        choice = _gemini_fresh_choice(transcript, title, body_duration,
                                     catalog, prior, genai_mod, hook,
                                     instruction=directive or None)
        if directive:
            reports.append("directive: " + directive[:200])
    kind, visual = "anchor", {"type": "anchor",
                              "label": title.upper()[:24],
                              "hook": hook[:220]}
    equation_norm, equation_section = None, ""
    reuse_of = None
    if choice is None:
        choice = _deterministic_choice(transcript, title, hook, catalog,
                                       prior, directive=directive or None)
        reports.append("deterministic-design-call: " + str(choice.get("reason", "")))
    want = choice.get("kind")
    if want == "equation":
        try:
            ref = int(choice.get("equation_ref"))
            entry = catalog[ref]
            equation_norm = entry["norm"]
            equation_section = entry.get("section", "")
        except Exception:
            entry = None
        if entry is None:
            text_norm = normalize_eq(choice.get("equation_display") or "")
            entry = next((c for c in catalog if c["norm"] == text_norm),
                         None)
            if entry is not None:
                equation_norm = entry["norm"]
                equation_section = entry.get("section", "")
        if entry is None:
            reports.append("equation-rejected-not-on-page: "
                           "design call returned an equation outside the "
                           "episode catalog; degraded to anchor")
            want = "anchor"
        else:
            disp = normalize_eq(choice.get("equation_display") or "")
            if not disp:
                disp = equation_norm[:140]
            for other_clip, other_eq in (prior or {}).items():
                if other_eq and other_eq == equation_norm and str(
                        other_clip) != str(clip_num):
                    reuse_of = other_clip
                    break
            if reuse_of is not None:
                reports.append(f"formula-reuse: same equation as clip "
                               f"{reuse_of} (reported, never silent)")
            kind = "formula"
            visual = {"type": "formula", "full": disp[:280],
                      "section": equation_section}
    if want == "diagram":
        d = str(choice.get("diagram") or "").strip().lower()
        if d not in DIAGRAM_KINDS:
            d = "groundzero"
        kind = "diagram"
        visual = {"type": "diagram", "diagram": d}
    elif want == "anchor":
        lab = str(choice.get("anchor_label") or "").strip().upper()
        if not lab:
            lab = title.upper()[:24]
        kind = "anchor"
        visual = {"type": "anchor", "label": lab[:32],
                  "hook": hook[:220]}
    elif want == "title-only":
        kind = "title-only"
        visual = {"type": "title"}
        reports.append("title-only: no suitable equation/diagram/anchor "
                       "for this clip")
    stages, _ = _build_stages(title, kind, visual, transcript, body_duration)
    design = {"kind": kind, "title": title,
              "equation_text": visual.get("full") if kind == "formula"
              else None,
              "equation_norm": equation_norm,
              "equation_section": equation_section,
              "reuse_of": reuse_of,
              "anchor": {"label": visual.get("label"),
                         "hook": visual.get("hook")}
              if kind == "anchor" else None,
              "diagram": visual.get("diagram") if kind == "diagram" else None,
              "reports": reports,
              "reason": str((choice or {}).get("reason") or "")[:300]}
    if directive:
        design["directive"] = directive
        design["directive_report"] = directive_outcome
    return {"design": design, "stages": stages}, reports




ALIASES = {
    '8d': 'eight octonion octonionic dimensional',
    'totality': 'whole substrate',
    'sensory': 'perception interface desktop',
    'division': 'division associator algebra algebras',
    'algebras': 'algebra associator bracket',
    'quaternions': 'quaternion ijk hamilton',
    'volumetric': 'volume knot topology',
    'commutativity': 'artin alternative associator',
    'illusion': 'interface desktop perception',
    'color': 'charge gluon qcd',
    'chiral': 'mirror parity modular',
    'spin': 'fermion half pauli',
    'arrows': 'thermal arrow entropy',
    'time': 'thermal modular arrow entropy',
    'equilibrium': 'balance',
    'imbalance': 'delta asymmetry',
    'creation': 'cosmology infinite',
    'zero': 'ground vacuum origin',
    'state': 'ground vacuum',
    'observer': 'measurement observed wigner',
    'scalar': 'identity higgs',
    'confinement': 'charge gluon qcd',
    'anticolors': 'charge gluon qcd',
    'electric': 'charge maxwell u1',
    'reality': 'real ontology',
    '2d': 'two dimensional flatland',
}


def _expand(toks):
    out = set(toks)
    for t in list(toks):
        hit = ALIASES.get(t)
        if hit:
            out.update(hit.split())
    return out
STOPWORDS = set('the a an and or of to in on for with as at by from is are was were be been it its this that these those we you they he she him her our your their there here what when where which who how why not no yes do does did will would can could should have has had having than then also just into over under more most such only own same so very'.split())


def _tokens(text):
    out = []
    for t in re.findall('[a-z0-9]+', str(text or '').lower()):
        if t in STOPWORDS or len(t) < 2:
            continue
        if len(t) > 5 and t.endswith('ing'):
            t = t[:-3]
        elif len(t) > 4 and t.endswith('es'):
            t = t[:-2]
        elif len(t) > 4 and t.endswith('s') and not t.endswith('ss'):
            t = t[:-1]
        if len(t) > 1 and t not in STOPWORDS:
            out.append(t)
    return out


SECTION_ENTRY_TOPICS = {
    '1.': ['octonion octonian eight totality basis identity substrate division hurwitz',
        'associator associative bracket division hurwitz frobenius alternative artin commutativity',
        'moufang automorphism g2 octonion division',
        'operator multiplication left algebra octonion'],
    '2.': ['free energy inference active perception interface sensory markov surprise bayesian split'],
    '4.': ['modular flow tomita observer ignorance statistical algebra mirror',
        'thermal arrow entropy origin ignorance time observer creation'],
}


def _entry_topics(catalog):
    topics = []
    seen = {}
    for entry in catalog:
        sec = str(entry.get('section', ''))
        key = sec[:2]
        slot = seen.get(key, 0)
        seen[key] = slot + 1
        bank = SECTION_ENTRY_TOPICS.get(key)
        if bank is not None and slot < len(bank):
            topics.append(bank[slot])
        else:
            topics.append(sec)
    return topics


def _directive_forces_anchor(directive):
    """Unnegated 'anchor' word forces kind anchor (e.g. 'make this an
    anchor', 'anchor only'). Never invents; the anchor path is unchanged."""
    toks = set(_tokens(directive or ""))
    if "anchor" not in toks:
        return False
    low = str(directive or "").lower()
    for neg in ("no anchor", "not anchor", "without anchor", "never anchor",
                "don't anchor", "dont anchor", "isn't anchor", "isnt anchor"):
        if neg in low:
            return False
    return True


def _directive_equation_match(directive, catalog):
    """Best catalog member for a directive naming an equation, or None.

    Scores directive words against entry topics + normalized text. The
    pick is always a catalog member (returned as index); None means
    no member matched (caller degrades to anchor and reports it)."""
    dtoks = set(_tokens(directive or ""))
    if not dtoks:
        return None
    topics = _entry_topics(catalog)
    best, best_score = None, 0
    for idx, entry in enumerate(catalog):
        tset = set(_tokens(topics[idx]))
        nset = set(_tokens(entry.get("norm", "")))
        score = 3 * len(dtoks & tset) + len(dtoks & nset)
        if score > best_score:
            best, best_score = idx, score
    if best is not None and best_score >= 4:
        return best
    return None


def _directive_names_equation(directive):
    low = str(directive or "").lower()
    return ("equation" in low or "formula" in low or "theorem" in low
            or "identity" in low or "=" in low)


def _deterministic_choice(transcript, title, hook, catalog, prior,
                         directive=None):
    '''One deterministic design call per clip (no AI key needed).

    Matches the clip title+transcript against the episode-page catalog.
    Returns a choice dict in the Gemini shape. Cannot invent: the equation
    is always a catalog member by construction. A non-empty directive acts
    as a topic hint (score boost); forced outcomes are resolved by the
    caller before this runs.'''
    title_toks = _expand(set(_tokens(title)))
    title_raw = set(_tokens(title))
    text_toks = _expand(set(_tokens(transcript)))
    topics = _entry_topics(catalog)
    hint_toks = _expand(set(_tokens(directive))) if directive else set()
    scored = []
    for idx, entry in enumerate(catalog):
        tset = set(_tokens(topics[idx]))
        overlap_title = title_toks & tset
        score = 4 * len(overlap_title) + len(text_toks & tset)
        if hint_toks:
            score += 2 * len(hint_toks & tset)
        used = any(e == entry.get('norm') for e in (prior or {}).values())
        scored.append((score, bool(overlap_title), used, idx))
    scored.sort(reverse=True)
    gated = [(s, u, x) for (s, g, u, x) in scored if s >= 5 and (title_raw & set(_tokens(topics[x])))]
    if gated:
        gated.sort(reverse=True)
        _, used, idx = gated[0]
        entry = catalog[idx]
        return {'kind': 'equation', 'equation_ref': idx,
                'equation_display': entry.get('norm', '')[:140],
                'anchor_label': None, 'diagram': None,
                'reason': 'deterministic title+transcript overlap'}
    words = [w for w in re.sub('[^A-Za-z0-9 ]', '', title).split() if w][:4]
    return {'kind': 'anchor', 'equation_ref': None,
            'equation_display': '', 'anchor_label': (" ".join(words).upper() or title.upper()[:24]),
            'diagram': None,
            'reason': 'deterministic: no catalog equation clears threshold'}
def check_equation_reuse(equation_norm, prior_equations, clip_num):
    for other_clip, other_eq in (prior_equations or {}).items():
        if other_eq and other_eq == equation_norm and str(other_clip) != str(
                clip_num):
            return other_clip
    return None


def _lit(s):
    return json.dumps(str(s or ""), ensure_ascii=False)


def _chrome_bottom(title):
    return (f'    bottom = Text({_lit(title.upper()[:40])}, font="DejaVu Sans", '
            f'font_size=22, color="#FFFFFF").move_to([0, -2.95, 0])\n'
            f'    foot = Line([-3.4, -3.35, 0], [3.4, -3.35, 0], '
            f'color="#FFFFFF", stroke_width=2, stroke_opacity=0.35)\n'
            f'    self.add(bottom, foot)\n')


def _timings(duration):
    dur = max(3.0, float(duration))
    t_enter = round(min(1.0, dur * 0.15), 2)
    t_build = round(min(2.5, dur * 0.30), 2)
    t_hold = round(max(1.0, dur - t_enter - t_build), 2)
    return t_enter, t_build, t_hold


def _render_stage_body(stage, cls_name, duration):
    """Deterministic white-on-black Manim code for one fresh stage.

    Uses Text only (no LaTeX in this environment). Every template keeps the
    clip title chrome at the bottom, fills the canvas (never left-empty),
    and ends with slow ambient motion so the frame is visibly alive.
    """
    kind = str(stage.get("kind") or "title").lower()
    title = str(stage.get("title") or "DEEP DIVE")
    visual = stage.get("visual") or {}
    t_enter, t_build, t_hold = _timings(duration)
    head = (f"class {cls_name}(Scene):\n    def construct(self):\n"
            + _chrome_bottom(title))
    if kind == "formula":
        full = str(visual.get("full") or title)
        toks = full.split()
        prog = float(visual.get("progress") or 1.0)
        cut = max(1, int(len(toks) * min(1.0, max(0.15, prog))))
        shown = _wrap_lines(" ".join(toks[:cut]))
        return (head +
                f'    eq = Text({_lit(shown)}, font="DejaVu Sans", '
                f'font_size=30, color="#FFFFFF")\n'
                f'    eq.scale_to_fit_width(6.4).move_to([0, 0.5, 0])\n'
                f'    self.play(FadeIn(eq), run_time={t_enter})\n'
                f'    self.play(eq.animate.shift(UP * 0.25).scale(1.02), '
                f'run_time={t_build})\n'
                f'    self.play(eq.animate.shift(DOWN * 0.25).scale(1 / 1.02), '
                f'run_time={t_hold})\n')
    if kind == "diagram":
        which = str(visual.get("diagram") or "groundzero").lower()
        if which not in DIAGRAM_KINDS:
            which = "groundzero"
        prog = float(visual.get("progress") or 1.0)
        if which == "tunnel":
            n = max(2, min(4, 1 + int(round(prog * 3))))
            squares = ", ".join(
                f'Square(side_length={1.2 + i * 0.9:.1f}, color="#FFFFFF", '
                f'stroke_width=5)' for i in range(4))
            return (head +
                    f'    sqs = [{squares}]\n'
                    f'    tunnel = VGroup(*sqs).move_to([0, 0.3, 0])\n'
                    f'    dot = Dot(color="#FFFFFF").move_to([-3, 0.3, 0])\n'
                    f'    self.play(FadeIn(tunnel), run_time={t_enter})\n'
                    f'    self.play(*[FadeIn(sqs[{{i}}]) for i in range({n})], '
                    f'run_time={t_build})\n'
                    f'    self.play(dot.animate.move_to([3, 0.3, 0]), '
                    f'run_time={t_hold})\n')
        if which == "numberline":
            n = max(2, min(6, 2 + int(round(prog * 4))))
            return (head +
                    f'    line = Line([-3.2, 0.3, 0], [3.2, 0.3, 0], '
                    f'color="#FFFFFF", stroke_width=5)\n'
                    f'    ticks = VGroup(*[Line([x, 0.05, 0], [x, 0.55, 0], '
                    f'color="#FFFFFF", stroke_width=4) for x in '
                    f'[-2.4, -1.2, 0.0, 1.2, 2.4][: {n}]])\n'
                    f'    dot = Dot(color="#FFFFFF").move_to([-3.2, 0.3, 0])\n'
                    f'    self.play(FadeIn(line), run_time={t_enter})\n'
                    f'    self.play(FadeIn(ticks), run_time={t_build})\n'
                    f'    self.play(dot.animate.move_to([3.2, 0.3, 0]), '
                    f'run_time={t_hold})\n')
        n = max(1, min(3, 1 + int(round(prog * 2))))
        rings = ", ".join(
            f'Circle(radius={0.7 + i * 0.8:.1f}, color="#FFFFFF", '
            f'stroke_width=5)' for i in range(3))
        return (head +
                f'    rings = [{rings}]\n'
                f'    gz = VGroup(*rings).move_to([0, 0.3, 0])\n'
                f'    core = Dot(color="#FFFFFF").scale(1.4).move_to([0, 0.3, 0])\n'
                f'    self.play(FadeIn(gz), run_time={t_enter})\n'
                f'    self.play(*[FadeIn(rings[{{i}}]) for i in range({n})], '
                f'FadeIn(core), run_time={t_build})\n'
                f'    self.play(core.animate.scale(1.6), run_time={t_hold / 2:.2f})\n'
                f'    self.play(core.animate.scale(1 / 1.6), '
                f'run_time={t_hold / 2:.2f})\n')
    if kind == "anchor":
        label = str(visual.get("label") or title.upper()[:24])
        hook_txt = _wrap_lines(visual.get("hook") or "", 44)
        return (head +
                f'    lab = Text({_lit(label)}, font="DejaVu Sans", '
                f'weight=BOLD, font_size=44, color="#FFFFFF").move_to([0, 0.9, 0])\n'
                f'    arr = Arrow([0, 0.25, 0], [0, -0.55, 0], '
                f'color="#FFFFFF", stroke_width=6)\n'
                f'    hook = Text({_lit(hook_txt)}, font="DejaVu Sans", '
                f'font_size=24, color="#FFFFFF").move_to([0, -1.5, 0])\n'
                f'    hook.scale_to_fit_width(6.2)\n'
                f'    self.play(FadeIn(lab), run_time={t_enter})\n'
                f'    self.play(GrowArrow(arr), FadeIn(hook), '
                f'run_time={t_build})\n'
                f'    self.play(lab.animate.shift(UP * 0.15), '
                f'hook.animate.shift(DOWN * 0.15), run_time={t_hold})\n')
    big = _wrap_lines(title.upper(), 20)
    return (head +
            f'    big = Text({_lit(big)}, font="DejaVu Sans", weight=BOLD, '
            f'font_size=52, color="#FFFFFF").move_to([0, 0.5, 0])\n'
            f'    big.scale_to_fit_width(6.4)\n'
            f'    self.play(FadeIn(big), run_time={t_enter})\n'
            f'    self.play(big.animate.shift(UP * 0.2), run_time={t_build})\n'
            f'    self.play(big.animate.shift(DOWN * 0.2), '
            f'run_time={t_hold})\n')


def render_stage_manim_code(stage, cls_name, duration):
    """Deterministic white-on-black Manim code for one fresh stage.

    Body lines are indented one extra level so they sit inside
    ``def construct`` (the templates are written at class level and get
    shifted here, keeping the template source readable).
    """
    code = _render_stage_body(stage, cls_name, duration)
    lines = code.split("\n")
    fixed = lines[:2] + [("    " + ln) if ln.strip() else ln
                         for ln in lines[2:]]
    return "\n".join(fixed)
