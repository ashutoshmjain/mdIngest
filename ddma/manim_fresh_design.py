"""H2 fresh-cast Manim design (new rules, Spec H s3 + Severity-1 stale-Manim fix).

Every design request means a FRESH cast: this module never reads a cached
storyboard file and never reuses a plan clip's existing infographic_scenes.
It generates a new design from the clip's transcript text + title + the
episode-page equation catalog, implements the new rules (one sustained
artifact per clip: title first, one equation OR one diagram OR one anchor
label+arrow, stages at sentence boundaries, no archetype list, no reuse
without a report), and renders deterministic Manim code (white-on-black Text
plus vector-path math (KaTeX-validated TeX via SVGMobject) for formula stages).
"""

import json
import os
import re
import urllib.request
from html.parser import HTMLParser

EPISODE_PAGE_URL = "https://deepdive.shutri.com/{ep}.html"

FRESH_KINDS = ("title", "formula", "diagram", "anchor")
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


def _src_markdown_display_blocks(ep_num):
    """Extract display math $$...$$ blocks in page order from src/<ep>.md."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "src", f"{ep_num}.md"),
        os.path.join(here, "src", f"{ep_num}.md"),
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    txt = f.read()
                return [b.strip() for b in re.findall(r"\$\$([\s\S]*?)\$\$", txt)
                        if b.strip()]
            except Exception:
                pass
    return []


def resolve_catalog_tex(entry, idx=None, ep_num=None):
    """Resolve TeX source for a catalog entry (explicit tex, norm match, or src/<ep>.md index)."""
    if isinstance(entry, dict) and entry.get("tex"):
        return str(entry["tex"]).strip()
    norm = entry.get("norm", "") if isinstance(entry, dict) else str(entry or "")
    m_idx = match_tex_for_norm(norm)
    if m_idx is not None and 0 <= m_idx < len(EPISODE_TEX_SOURCES):
        return EPISODE_TEX_SOURCES[m_idx]
    if ep_num is not None and idx is not None:
        blocks = _src_markdown_display_blocks(ep_num)
        if 0 <= int(idx) < len(blocks):
            return blocks[int(idx)]
    return None


def fetch_episode_equations(ep_num, cache_path=None, refresh=False):
    """Episode-page equation catalog: [{section, text, norm, tex?}]. Cached JSON."""
    if cache_path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        cache_path = os.path.join(here, "scratch", f"ep{ep_num}_equations_v2.json")
    catalog = None
    if os.path.exists(cache_path) and not refresh:
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                catalog = json.load(f)
        except Exception:
            catalog = None
    if catalog is None:
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
    for idx, entry in enumerate(catalog):
        if isinstance(entry, dict) and not entry.get("tex"):
            tex = resolve_catalog_tex(entry, idx=idx, ep_num=ep_num)
            if tex:
                entry["tex"] = tex
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
2. Equation ONLY if it is that clip's own (it must match the transcript topic). If none fits, choose diagram or anchor. If the clip has no suitable artifact at all, choose anchor with the title words as the label (title-only is retired; never emit it).
3. Hook sentence (first sentence, for the anchor fallback): {hook}
4. Formula reuse across clips is allowed only when the equation genuinely belongs to both clips; it is reported, never silent.

Return ONLY a JSON object, no other text:
{{"kind": "equation|diagram|anchor",
  "equation_ref": <catalog index or null>,
  "equation_display": "<short display form, <=140 chars, plain unicode, no TeX commands>",
  "anchor_label": "<1-4 WORD LABEL or null>",
  "diagram": "tunnel|numberline|groundzero|null",
  "reason": "<one line: why this artifact is this clip's own>"}}"""


def compose_design_prompt(transcript, title, body_duration, catalog,
                          prior_equations=None, hook=None, directive=None,
                          kind=None, equation_ref=None, diagram=None,
                          anchor_label=None, anchor_hook=None):
    """Compose the full effective prompt the design system uses for a clip."""
    transcript = str(transcript or "").strip()
    title = str(title or "Deep Dive").strip()
    body_duration = float(body_duration or 120.0)
    catalog = list(catalog or [])
    prior = prior_equations or {}
    if hook is None:
        hook = hook_sentence(transcript)
    cat_lines = [f"[{i}] ({c.get('section', '')[:60]}) {c.get('norm', '')[:200]}"
                 for i, c in enumerate(catalog)]
    sents = split_sentences(transcript)
    prompt = _FRESH_PROMPT.format(
        transcript=transcript[:6000], title=title,
        body_duration=body_duration, n_sent=len(sents),
        sent_list=json.dumps(sents[:12], ensure_ascii=False)[:1500],
        catalog="\n".join(cat_lines) if cat_lines else "(none)",
        prior=json.dumps(prior, ensure_ascii=False)[:800] or "(none)",
        hook=str(hook)[:300])
    struct_parts = []
    k_clean = str(kind or "").strip().lower()
    if k_clean in ("formula", "equation", "anchor", "diagram"):
        k_norm = "formula" if k_clean == "equation" else k_clean
        struct_parts.append(f"kind={k_norm.upper()}")
        if k_norm == "formula" and equation_ref is not None and str(equation_ref) != "":
            struct_parts.append(f"equation_ref={equation_ref}")
        elif k_norm == "diagram" and diagram:
            struct_parts.append(f"diagram={str(diagram).strip().lower()}")
        elif k_norm == "anchor":
            if anchor_label:
                struct_parts.append(f"anchor_label={str(anchor_label).strip().upper()[:32]!r}")
            if anchor_hook:
                struct_parts.append(f"anchor_hook={str(anchor_hook).strip()[:220]!r}")
    if struct_parts:
        prompt += "\nStructured design parameters: " + ", ".join(struct_parts)
    if directive and str(directive).strip():
        prompt += ("\nUser design instruction for this clip (honor it; the "
                   "catalog-membership rule still applies): "
                   + str(directive).strip()[:300])
    return prompt


def _gemini_fresh_choice(transcript, title, body_duration, catalog, prior,
                         genai_mod, hook, instruction=None,
                         prompt_override=None):
    if genai_mod is None:
        return None
    if prompt_override and str(prompt_override).strip():
        prompt = str(prompt_override).strip()
    else:
        prompt = compose_design_prompt(
            transcript, title, body_duration, catalog,
            prior_equations=prior, hook=hook, directive=instruction)
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
                    "equation", "diagram", "anchor"):
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


def _normalize_anchor_label(raw_label, fallback_title):
    words = [w for w in str(raw_label or "").strip().split() if w][:4]
    if words:
        return " ".join(words).upper()[:32]
    twords = [w for w in re.sub(r"[^A-Za-z0-9 ]", "", str(fallback_title or "")).split() if w][:4]
    return (" ".join(twords).upper() or str(fallback_title or "DEEP DIVE").upper())[:24]


def design_clip_artifact(transcript, title, body_duration, catalog,
                         genai_mod=None, prior_equations=None, clip_num=None,
                         directive=None, kind=None, equation_ref=None,
                         diagram=None, anchor_label=None, anchor_hook=None,
                         prompt_override=None):
    """Fresh-cast ONE artifact. Returns (storyboard_design_dict, reports).

    Never reads caches or plan scenes. The returned equation (if any) is
    always a catalog member; anything else degrades to anchor
    and is reported. A non-empty directive (per-clip design instruction)
    is honored deterministically: unnegated "anchor" forces kind anchor;
    an equation name picks the best-matching catalog member (never
    invented); anything else acts as a topic hint. Structured parameters
    (kind, equation_ref, diagram, anchor_label, anchor_hook, prompt_override)
    from the Manim configurator are resolved deterministically with full
    catalog-guard enforcement. Empty directive + no structured params means
    exactly the historical behavior (no extra keys are stored).
    """
    reports = []
    transcript = str(transcript or "").strip()
    title = str(title or "Deep Dive").strip()
    default_hook = hook_sentence(transcript)
    hook = str(anchor_hook).strip()[:220] if (anchor_hook is not None and str(anchor_hook).strip()) else default_hook
    prior = prior_equations or {}
    directive = str(directive or "").strip()
    p_override = str(prompt_override or "").strip()
    req_kind = str(kind or "").strip().lower()
    if req_kind == "equation":
        req_kind = "formula"
    has_structured = bool(
        req_kind in ("formula", "anchor", "diagram")
        or (equation_ref is not None and str(equation_ref).strip() != "")
        or (diagram is not None and str(diagram).strip() != "")
        or (anchor_label is not None and str(anchor_label).strip() != "")
        or (anchor_hook is not None and str(anchor_hook).strip() != "")
        or p_override
    )
    outcome_parts = []
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

    choice = None
    used_gemini_override = False
    if p_override and genai_mod is not None:
        g_choice = _gemini_fresh_choice(
            transcript, title, body_duration, catalog, prior, genai_mod, hook,
            instruction=directive or None, prompt_override=p_override)
        if g_choice is not None:
            choice = g_choice
            used_gemini_override = True
            outcome_parts.append("prompt-override: gemini")
            reports.append("prompt-override: gemini")

    if p_override and not used_gemini_override:
        outcome_parts.append("prompt-override: fallback-deterministic")
        reports.append("prompt-override: fallback-deterministic")

    if forced is not None:
        kind_name, ref = forced[0], forced[1]
        outcome_parts.append(forced[2])
        if kind_name == "anchor":
            choice = {"kind": "anchor",
                      "anchor_label": _normalize_anchor_label(anchor_label, title) if anchor_label else None,
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
        reports.append(forced[2])
    elif req_kind in ("formula", "anchor", "diagram") and not used_gemini_override:
        if directive:
            reports.append("directive: " + directive[:200])
        if req_kind == "anchor":
            outcome_parts.append("kind-forced: anchor")
            reports.append("kind-forced: anchor")
            lab_val = _normalize_anchor_label(anchor_label, title)
            if anchor_label and str(anchor_label).strip():
                outcome_parts.append("anchor-label: " + lab_val)
                reports.append("anchor-label: " + lab_val)
            choice = {"kind": "anchor",
                      "anchor_label": lab_val,
                      "equation_ref": None, "equation_display": "",
                      "diagram": None,
                      "reason": "kind-forced: anchor"}
        elif req_kind == "diagram":
            d_val = str(diagram or "").strip().lower()
            if d_val not in DIAGRAM_KINDS:
                d_val = "groundzero"
            outcome_parts.append("kind-forced: diagram")
            outcome_parts.append("diagram-picked: " + d_val)
            reports.append("kind-forced: diagram")
            reports.append("diagram-picked: " + d_val)
            choice = {"kind": "diagram", "diagram": d_val,
                      "equation_ref": None, "equation_display": "",
                      "anchor_label": None,
                      "reason": "kind-forced: diagram (" + d_val + ")"}
        elif req_kind == "formula":
            outcome_parts.append("kind-forced: formula")
            reports.append("kind-forced: formula")
            ref_idx = None
            if equation_ref is not None and str(equation_ref).strip() != "":
                try:
                    cand_idx = int(equation_ref)
                    if 0 <= cand_idx < len(catalog):
                        ref_idx = cand_idx
                except Exception:
                    ref_idx = None
            if ref_idx is not None:
                entry = catalog[ref_idx]
                outcome_parts.append(f"equation-picked: catalog {ref_idx}")
                reports.append(f"equation-picked: catalog {ref_idx}")
                choice = {"kind": "equation", "equation_ref": ref_idx,
                          "equation_display": entry.get("norm", ""),
                          "anchor_label": None, "diagram": None,
                          "reason": f"equation-picked: catalog {ref_idx}"}
            else:
                bad_msg = (f"equation-rejected-not-on-page: invalid equation_ref "
                           f"{equation_ref!r}; degraded to anchor")
                outcome_parts.append(bad_msg)
                reports.append(bad_msg)
                choice = {"kind": "anchor",
                          "anchor_label": _normalize_anchor_label(anchor_label, title),
                          "equation_ref": None, "equation_display": "",
                          "diagram": None,
                          "reason": "invalid equation_ref degraded to anchor"}
    elif choice is None:
        if equation_ref is not None and str(equation_ref).strip() != "":
            try:
                cand_idx = int(equation_ref)
                if not (0 <= cand_idx < len(catalog)):
                    raise ValueError("out of range")
                entry = catalog[cand_idx]
                outcome_parts.append(f"equation-picked: catalog {cand_idx}")
                reports.append(f"equation-picked: catalog {cand_idx}")
                choice = {"kind": "equation", "equation_ref": cand_idx,
                          "equation_display": entry.get("norm", ""),
                          "anchor_label": None, "diagram": None,
                          "reason": f"equation-picked: catalog {cand_idx}"}
            except Exception:
                bad_msg = (f"equation-rejected-not-on-page: invalid equation_ref "
                           f"{equation_ref!r}; degraded to anchor")
                outcome_parts.append(bad_msg)
                reports.append(bad_msg)
                choice = {"kind": "anchor",
                          "anchor_label": _normalize_anchor_label(anchor_label, title),
                          "equation_ref": None, "equation_display": "",
                          "diagram": None,
                          "reason": "invalid equation_ref degraded to anchor"}
        else:
            choice = _gemini_fresh_choice(transcript, title, body_duration,
                                          catalog, prior, genai_mod, hook,
                                          instruction=directive or None,
                                          prompt_override=p_override or None)
            if directive:
                reports.append("directive: " + directive[:200])

    kind_out, visual = "anchor", {"type": "anchor",
                                  "label": _normalize_anchor_label(anchor_label, title),
                                  "hook": hook[:220]}
    equation_norm, equation_section = None, ""
    resolved_eq_ref = None
    reuse_of = None
    if choice is None:
        choice = _deterministic_choice(transcript, title, hook, catalog,
                                       prior, directive=directive or None)
        reports.append("deterministic-design-call: " + str(choice.get("reason", "")))
    want = choice.get("kind")
    if want == "equation":
        try:
            ref = int(choice.get("equation_ref"))
            if ref < 0 or ref >= len(catalog):
                raise IndexError("negative or out-of-range catalog ref")
            entry = catalog[ref]
            resolved_eq_ref = ref
            equation_norm = entry["norm"]
            equation_section = entry.get("section", "")
        except Exception:
            entry = None
        if entry is None:
            text_norm = normalize_eq(choice.get("equation_display") or "")
            for c_idx, c in enumerate(catalog):
                if c["norm"] == text_norm:
                    entry = c
                    resolved_eq_ref = c_idx
                    equation_norm = entry["norm"]
                    equation_section = entry.get("section", "")
                    break
        if entry is None:
            rej = ("equation-rejected-not-on-page: "
                   "design call returned an equation outside the "
                   "episode catalog; degraded to anchor")
            reports.append(rej)
            if has_structured:
                outcome_parts.append(rej)
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
            kind_out = "formula"
            visual = {"type": "formula", "full": disp[:280],
                      "section": equation_section}
    if want == "diagram":
        d = str(choice.get("diagram") or diagram or "").strip().lower()
        if d not in DIAGRAM_KINDS:
            d = "groundzero"
        kind_out = "diagram"
        visual = {"type": "diagram", "diagram": d}
    elif want == "anchor":
        raw_lab = anchor_label if (anchor_label is not None and str(anchor_label).strip()) else choice.get("anchor_label")
        lab = _normalize_anchor_label(raw_lab, title)
        kind_out = "anchor"
        visual = {"type": "anchor", "label": lab[:32],
                  "hook": hook[:220]}
    stages, _ = _build_stages(title, kind_out, visual, transcript, body_duration)
    design = {"kind": kind_out, "title": title,
              "equation_text": visual.get("full") if kind_out == "formula"
              else None,
              "equation_norm": equation_norm,
              "equation_section": equation_section,
              "reuse_of": reuse_of,
              "anchor": {"label": visual.get("label"),
                         "hook": visual.get("hook")}
              if kind_out == "anchor" else None,
              "diagram": visual.get("diagram") if kind_out == "diagram" else None,
              "reports": reports,
              "reason": str((choice or {}).get("reason") or "")[:300]}
    if resolved_eq_ref is not None and has_structured:
        design["equation_ref"] = resolved_eq_ref
    if p_override:
        design["prompt_override"] = p_override
    directive_outcome = "; ".join(p for p in outcome_parts if p)
    if directive:
        design["directive"] = directive
        design["directive_report"] = directive_outcome
    elif has_structured and directive_outcome:
        design["directive_report"] = directive_outcome
    return {"design": design, "stages": stages}, reports


def apply_configurator_overrides_to_storyboard(
        storyboard, transcript, title, body_duration, catalog,
        prior_equations=None, clip_num=None, kind=None, equation_ref=None,
        diagram=None, anchor_label=None, anchor_hook=None, directive=None,
        prompt_override=None, ep_num=None):
    """Update a stored storyboard in-place with explicit configurator overrides
    for Re-render (layers 2+3). If no fields changed from the stored design,
    leaves the storyboard dict untouched (pure redraw, byte-identical)."""
    if not isinstance(storyboard, dict):
        raise ValueError("storyboard must be a dict")
    stored = storyboard.get("design") or {}
    catalog = list(catalog or [])
    prior = prior_equations or {}
    stored_kind = str(stored.get("kind") or "anchor").lower()
    req_kind = str(kind or stored_kind).strip().lower()
    if req_kind == "equation":
        req_kind = "formula"
    if req_kind not in ("formula", "anchor", "diagram"):
        req_kind = stored_kind if stored_kind in ("formula", "anchor", "diagram") else "anchor"

    # Determine stored equation_ref
    stored_eq_ref = stored.get("equation_ref")
    if stored_eq_ref is None and stored.get("equation_norm"):
        for idx, c in enumerate(catalog):
            if c.get("norm") == stored.get("equation_norm"):
                stored_eq_ref = idx
                break
    stored_diag = stored.get("diagram")
    stored_anc = stored.get("anchor") or {}
    stored_lab = stored_anc.get("label") or ""
    stored_hook = stored_anc.get("hook") or ""
    stored_dir = str(stored.get("directive") or "")
    stored_po = str(stored.get("prompt_override") or "")

    eff_eq_ref = stored_eq_ref if (equation_ref is None or str(equation_ref).strip() == "") else equation_ref
    eff_diag = (str(diagram).strip().lower() if (diagram is not None and str(diagram).strip() != "")
                else (stored_diag or "groundzero"))
    eff_lab = (str(anchor_label).strip() if (anchor_label is not None and str(anchor_label).strip() != "")
               else stored_lab)
    eff_hook = (str(anchor_hook).strip() if (anchor_hook is not None and str(anchor_hook).strip() != "")
                else (stored_hook or hook_sentence(transcript)))
    eff_dir = str(directive).strip() if directive is not None else stored_dir
    eff_po = str(prompt_override).strip() if prompt_override is not None else stored_po

    # Check if anything actually changed from the stored design
    same_kind = (req_kind == stored_kind)
    same_dir = (eff_dir == stored_dir)
    same_po = (eff_po == stored_po)
    same_slot = False
    if req_kind == "anchor":
        same_slot = (_normalize_anchor_label(eff_lab, title) == stored_lab and eff_hook == stored_hook)
    elif req_kind == "diagram":
        same_slot = (eff_diag == stored_diag)
    elif req_kind == "formula":
        try:
            same_slot = (int(eff_eq_ref) == int(stored_eq_ref))
        except Exception:
            same_slot = False

    if same_kind and same_slot and same_dir and same_po and storyboard.get("stages"):
        return storyboard, False

    art, reports = design_clip_artifact(
        transcript, title, body_duration, catalog,
        genai_mod=None, prior_equations=prior, clip_num=clip_num,
        directive=eff_dir or None, kind=req_kind, equation_ref=eff_eq_ref,
        diagram=eff_diag, anchor_label=eff_lab, anchor_hook=eff_hook,
        prompt_override=eff_po or None)
    new_design = art["design"]
    if new_design.get("kind") == "formula" and new_design.get("equation_norm"):
        eq_idx = new_design.get("equation_ref")
        tex = resolve_catalog_tex(
            catalog[eq_idx] if (eq_idx is not None and 0 <= eq_idx < len(catalog)) else {"norm": new_design["equation_norm"]},
            idx=eq_idx, ep_num=ep_num)
        if tex:
            new_design["equation_tex"] = tex
    stages = art["stages"]
    for st in stages:
        st.setdefault("labels", [str(title).upper()[:24]])
        st.setdefault("archetype", "fresh-" + str(st.get("kind", "title")))
    updated = dict(storyboard)
    updated["design"] = new_design
    updated["scenes"] = stages
    updated["stages"] = stages
    updated["total_duration"] = round(float(body_duration), 2)
    return updated, True




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


FOCUS_MAX_CHARS = 36
SUB_ROW_FONT_SIZE = 14

# Equation TeX sources, verbatim from the author's page markdown
# (deepDive src/249.md display blocks, in page order). The stored
# plain-text norms are lossy renderings of these same equations.
EPISODE_TEX_SOURCES = [
    r'x = x_0 e_0 + \sum_{i=1}^7 x_i e_i',
    r'[x, y, z] \equiv (xy)z - x(yz) \neq 0',
    r'(ux)(yu) = u(xy)u',
    r'L_x y \equiv xy \quad \text{for } x, y \in \mathbb{O}',
    (r'F = \mathbb{E}_{q(\eta)} \left[ \ln q(\eta) - \ln p(\eta, s) '
     r'\right] = D_{\mathrm{KL}}\left(q(\eta) \,||\, p(\eta | s)'
     r'\right) - \ln p(s)'),
    (r'\alpha_t^\rho(A) = \Delta^{it} A \Delta^{-it} \quad \forall A '
     r'\in \mathcal{M}, \; t \in \mathbb{R}'),
    r't_{\mathrm{thermal}} = -\frac{1}{\beta} \ln \rho',
]


def match_tex_for_norm(norm):
    """Map a stored plain-text equation norm to its TeX source index.

    Returns the index into EPISODE_TEX_SOURCES, or None when the norm
    is not one of the four equations the 249 designs use (the caller
    must refuse to render math in that case, never invent TeX).
    """
    t = str(norm or '')
    if 'D KL (' in t and t.startswith('F = E q'):
        return 4
    if t.startswith('[ x , y , z ]'):
        return 1
    if t.startswith('t thermal'):
        return 6
    if t.startswith('\u03b1 t \u03c1'):
        return 5
    return None


def split_tex_rows(tex):
    """Split TeX into rows at top-level operators only.

    Breaks before depth-0 ``=`` (always binary) and depth-0 ``+``/``-``
    that follow an operand (never unary, never mid-number, never inside
    any ``{}``/``()``/``[]``/``\\left…\\right`` group). Returns the
    list of row strings; a single row when nothing qualifies.
    """
    ops = []
    depth = 0
    i, n = 0, len(tex)
    while i < n:
        ch = tex[i]
        if ch == '\\':
            j = i + 1
            if j < n and tex[j] == '\\':
                i += 2
                continue
            if j < n and tex[j] == ' ':
                i += 2
                continue
            k = j
            while k < n and tex[k].isalpha():
                k += 1
            word = tex[j:k]
            if word in ('left', 'right'):
                depth += 1 if word == 'left' else -1
                i = k
                if k < n and tex[k] in '([{':
                    i = k + 1
                elif k < n and tex[k] == '.':
                    i = k + 1
                continue
            i = k if k > j else j + 1
            continue
        if ch in '{([':
            depth += 1
        elif ch in '})]':
            depth -= 1
        elif depth == 0 and ch == '=':
            ops.append(i)
        elif depth == 0 and ch in '+-':
            j = i - 1
            while j >= 0 and tex[j] in ' \t':
                j -= 1
            if j >= 0 and (tex[j].isalnum() or tex[j] in ')}]'):
                ops.append(i)
        i += 1
    if not ops:
        return [tex.strip()]
    rows, start = [], 0
    for o in ops:
        rows.append(tex[start:o].strip())
        start = o
    rows.append(tex[start:].strip())
    return [r for r in rows if r]


ROW_MAX_PT = 440.0


def _katex_validate(tex):
    """Strict-parse gate: the TeX must be valid KaTeX (npm global).

    Raises on any failure (missing node/katex or a parse error) so the
    caller refuses instead of rendering something unvalidated.
    """
    import os
    import shutil
    import subprocess
    node = shutil.which('node')
    if not node:
        raise RuntimeError('katex gate: node not found')
    npm = shutil.which('npm')
    node_path = os.environ.get('NODE_PATH') or ''
    if not node_path and npm:
        try:
            p = subprocess.run(
                [npm, 'root', '-g'], capture_output=True, text=True,
                timeout=30)
            if p.returncode == 0 and p.stdout.strip():
                node_path = p.stdout.strip()
        except Exception:
            pass
    js = ('const k=require("katex");'
          'k.renderToString(%s,{throwOnError:true});'
          'console.log("TEX-OK");' % __import__('json').dumps(tex))
    env = dict(os.environ)
    if node_path:
        env['NODE_PATH'] = (node_path + os.pathsep +
                            env.get('NODE_PATH', ''))
    r = subprocess.run([node, '-e', js], capture_output=True, text=True,
                       timeout=60, env=env)
    if r.returncode != 0 or 'TEX-OK' not in (r.stdout or ''):
        raise RuntimeError('katex gate rejected TeX: ' +
                           ((r.stderr or r.stdout)[:300] if r else '?'))


def _svg_width_pt(path):
    import re as _re2
    with open(path, 'rb') as fh:
        raw = fh.read()[:2000].decode('utf-8', 'replace')
    m = _re2.search(r'width="([\d.]+)pt"', raw)
    return float(m.group(1)) if m else 0.0


def _render_one_tex_svg(tex, path, fontsize=22):
    import matplotlib
    matplotlib.use('SVG')
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 2))
    fig.patch.set_alpha(0.0)
    fig.text(0.01, 0.4, '$%s$' % tex, fontsize=fontsize, color='white')
    fig.savefig(path, format='svg', transparent=True,
                bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)


def render_tex_rows_svg(tex, out_dir, tag, fontsize=22):
    """Validate (KaTeX gate), split if needed, render TeX rows to SVG.

    Returns row SVG paths (absolute, forward slashes). Single row when
    the whole equation fits ROW_MAX_PT; otherwise split at top-level
    operators only. The Manim side additionally scales the row group
    to the pane, so fit is guaranteed twice over.
    """
    import os as _os
    _katex_validate(tex)
    _os.makedirs(out_dir, exist_ok=True)
    whole = _os.path.join(out_dir, '%s_row0.svg' % tag)
    _render_one_tex_svg(tex, whole, fontsize=fontsize)
    if _svg_width_pt(whole) <= ROW_MAX_PT:
        return [whole.replace('\\', '/')]
    rows = split_tex_rows(tex)
    if len(rows) <= 1:
        return [whole.replace('\\', '/')]
    try:
        _os.remove(whole)
    except OSError:
        pass
    out = []
    for idx, row in enumerate(rows):
        path = _os.path.join(out_dir, '%s_row%d.svg' % (tag, idx))
        _render_one_tex_svg(row, path, fontsize=fontsize)
        out.append(path.replace('\\', '/'))
    return out


def _format_focus(text, limit=FOCUS_MAX_CHARS):
    """Uppercase footer focus label, numeric section prefix stripped,
    truncated at a word boundary (with ellipsis) so the sub-row never
    collides. The single-line budget (~36 caps at sub-row size) was
    measured from rendered frames; longer section names cannot fit."""
    t = re.sub(r'^\d+\.\s*', '', str(text or '')).strip().upper()
    if len(t) <= limit:
        return t
    cut = t[:limit]
    if ' ' in cut:
        cut = cut.rsplit(' ', 1)[0]
    return cut + "\u2026"


def _chrome_bottom(title, archetype="", ep=None):
    """Two-row footer: clip PLAN title above the divider line; below the
    line the archetype type (left) and the fixed credit (right).

    Below-left is the clip's archetype (ANCHOR / FORMULA / DIAGRAM),
    constant through the clip -- never the focus. Below-right is
    always ``deepDive podcast \u00b7 Ep {ep}`` (mixed case,
    middle-dot, episode number always present). The footer title
    shrink-fits long titles (clip 0) instead of truncating.

    The untouched render engine's base scene draws its own duplicate
    rule + sub-row at y ~-3.35/-3.6; this module may not touch the
    engine file, so the chrome first paints a black cover strip over
    that region, then draws the single canonical footer on top.
    """
    arch = str(archetype or "ANCHOR").upper()
    if arch not in ("ANCHOR", "FORMULA", "DIAGRAM"):
        arch = "ANCHOR"
    right = ("deepDive podcast \u00b7 Ep " + str(ep) if ep
             else "deepDive podcast")
    parts = [
        f'    _cover = Rectangle(width=8.0, height=0.8, '
        f'fill_color="#000000", fill_opacity=1, '
        f'stroke_width=0).move_to([0, -3.66, 0])\n',
        f'    bottom = Text({_lit(title.upper())}, font="DejaVu Sans", '
        f'font_size=22, color="#FFFFFF")\n',
        f'    _btw = bottom.width\n',
        f'    if _btw > 6.8:\n',
        f'        bottom.scale_to_fit_width(6.8)\n',
        f'    bottom.move_to([0, -2.70, 0])\n',
        f'    foot = Line([-3.4, -3.45, 0], [3.4, -3.45, 0], '
        f'color="#FFFFFF", stroke_width=2, stroke_opacity=0.35)\n',
        f'    _arch_l = Text({_lit(arch)}, font="DejaVu Sans", '
        f'font_size={SUB_ROW_FONT_SIZE}, color="#FFFFFF")\n'
        f'    _arch_l.move_to('
        f'[-3.4 + _arch_l.width / 2, -3.72, 0])\n',
    ]
    adds = ['_cover', 'bottom', 'foot', '_arch_l']
    parts.append(
        f'    _focus_r = Text({_lit(right)}, font="DejaVu Sans", '
        f'font_size={SUB_ROW_FONT_SIZE}, color="#FFFFFF")\n'
        f'    _focus_r.move_to('
        f'[3.4 - _focus_r.width / 2, -3.72, 0])\n')
    adds.append('_focus_r')
    parts.append(f'    self.add({", ".join(adds)})\n')
    return "".join(parts)


def _timings(duration):
    dur = max(3.0, float(duration))
    t_enter = round(min(1.0, dur * 0.15), 2)
    t_build = round(min(2.5, dur * 0.30), 2)
    t_hold = round(max(1.0, dur - t_enter - t_build), 2)
    return t_enter, t_build, t_hold


def _render_stage_body(stage, cls_name, duration):
    """Deterministic white-on-black Manim code for one fresh stage.

    Formula stages embed KaTeX-validated TeX as vector paths;
    every stage also shows its sentence text on the pane. Every
    template keeps the clip title chrome at the bottom, fills the
    canvas (never left-empty), and ends with slow ambient motion
    so the frame is visibly alive.
    """
    kind = str(stage.get("kind") or "title").lower()
    title = str(stage.get("title") or "DEEP DIVE")
    visual = stage.get("visual") or {}
    t_enter, t_build, t_hold = _timings(duration)
    arch = str((stage or {}).get("_render_archetype") or "").upper()
    if arch not in ("ANCHOR", "FORMULA", "DIAGRAM"):
        _ak = str(stage.get("kind") or "").lower()
        arch = {"formula": "FORMULA",
                "diagram": "DIAGRAM"}.get(_ak, "ANCHOR")
    ep = (stage or {}).get("_render_ep")
    # Above-line chrome title is the clip's PLAN title (transient
    # in-memory ``_render_title`` hint from the render driver; falls
    # back to the stage title when no hint is present). Below-left is
    # the clip-constant archetype (transient ``_render_archetype``
    # hint from the driver, taken from the board design kind).
    chrome_title = str((stage or {}).get("_render_title") or title)
    sent_txt = _wrap_lines(str((stage or {}).get("text") or " ").strip()
                           or " ", 36)
    head = (f"class {cls_name}(Scene):\n    def construct(self):\n"
            + _chrome_bottom(chrome_title, archetype=arch, ep=ep)
            + f'    _sent = Text({_lit(sent_txt)}, font="DejaVu Sans", '
            f'font_size=16, color="#FFFFFF")\n'
            f'    _ssw = _sent.width\n'
            f'    _ssh = _sent.height\n'
            f'    _sent.scale(min(1.0, 6.2 / _ssw if _ssw > 0 else 1.0, '
            f'1.5 / _ssh if _ssh > 0 else 1.0))\n'
            f'    _sent.move_to([0, 3.05, 0])\n')
    if kind == "formula":
        svg_rows = (stage or {}).get("_render_svg_rows") or []
        if svg_rows:
            # Real math: KaTeX-validated TeX rendered to SVG rows by
            # the driver, embedded as vector paths. The row group is
            # scaled to the pane (width 5.8u ~= 536px, height-capped),
            # so fit is guaranteed regardless of equation width.
            parts = []
            for i, p in enumerate(svg_rows):
                parts.append(
                    f'    _eqr{i} = SVGMobject({_lit(p)})\n')
            group = ('    _eq_rows = VGroup(%s).arrange(DOWN, buff=0.35, '
                     'aligned_edge=ORIGIN)\n'
                     % ", ".join("_eqr%d" % i
                                 for i in range(len(svg_rows))))
            return (head + "".join(parts) + group +
                    '    _eq_rows.scale(min(1.6, 5.8 / _eq_rows.width))\n'
                    '    _eq_rows.scale(min(1.0, 4.2 / _eq_rows.height))\n'
                    '    _eq_rows.move_to([0, 0.5, 0])\n'
                    f'    self.play(FadeIn(_eq_rows), FadeIn(_sent), run_time={t_enter})\n'
                    '    self.play(_eq_rows.animate.shift(UP * 0.25).scale('
                    '1.02), '
                    f'run_time={t_build})\n'
                    '    self.play(_eq_rows.animate.shift(DOWN * 0.25).scale('
                    '1 / 1.02), '
                    f'run_time={t_hold})\n')
        full = str(visual.get("full") or title)
        toks = full.split()
        prog = float(visual.get("progress") or 1.0)
        cut = max(1, int(len(toks) * min(1.0, max(0.15, prog))))
        shown = _wrap_lines(" ".join(toks[:cut]))
        return (head +
                f'    eq = Text({_lit(shown)}, font="DejaVu Sans", '
                f'font_size=20, color="#FFFFFF")\n'
                f'    eq.scale_to_fit_width(6.4).move_to([0, 0.5, 0])\n'
                f'    self.play(FadeIn(eq), FadeIn(_sent), run_time={t_enter})\n'
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
                    f'    self.play(FadeIn(tunnel), FadeIn(_sent), run_time={t_enter})\n'
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
                    f'    self.play(FadeIn(line), FadeIn(_sent), run_time={t_enter})\n'
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
                f'    self.play(FadeIn(gz), FadeIn(_sent), run_time={t_enter})\n'
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
                f'weight=BOLD, font_size=34, color="#FFFFFF").move_to([0, 0.9, 0])\n'
                f'    arr = Arrow([0, 0.25, 0], [0, -0.55, 0], '
                f'color="#FFFFFF", stroke_width=6)\n'
                f'    hook = Text({_lit(hook_txt)}, font="DejaVu Sans", '
                f'font_size=14, color="#FFFFFF").move_to([0, -1.5, 0])\n'
                f'    hook.scale_to_fit_width(6.2)\n'
                f'    self.play(FadeIn(lab), FadeIn(_sent), run_time={t_enter})\n'
                f'    self.play(GrowArrow(arr), FadeIn(hook), '
                f'run_time={t_build})\n'
                f'    self.play(lab.animate.shift(UP * 0.15), '
                f'hook.animate.shift(DOWN * 0.15), run_time={t_hold})\n')
    big = _wrap_lines(title.upper(), 20)
    return (head +
            f'    big = Text({_lit(big)}, font="DejaVu Sans", weight=BOLD, '
            f'font_size=42, color="#FFFFFF").move_to([0, 0.5, 0])\n'
            f'    big.scale_to_fit_width(6.4)\n'
            f'    self.play(FadeIn(big), FadeIn(_sent), run_time={t_enter})\n'
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
