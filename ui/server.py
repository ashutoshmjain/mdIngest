#!/usr/bin/env python3
"""
md² Ingest Cockpit Backend Server (Pillar 2 Publishing Bridge)
Provides local HTTP API for lossless .py payload extraction, KaTeX sanitization,
Mempool draft management, Block Template auto-numbering, and mdBook integration.
"""

import http.server
import socketserver
import webbrowser
import threading
import json
import os
import sys
import re
import base64
import gzip
import glob
import shutil
import subprocess
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from datetime import datetime
import ast
import socket

# Working directories
INGEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = INGEST_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
IMG_DIR = SRC_DIR / "img"
VID_DIR = SRC_DIR / "vid"
SUMMARY_FILE = SRC_DIR / "SUMMARY.md"
SETTINGS_FILE = INGEST_DIR / "settings.json"

IMG_DIR.mkdir(parents=True, exist_ok=True)
VID_DIR.mkdir(parents=True, exist_ok=True)

# Global tracker for mdbook serve background process
mdserve_process = None
ddma_curator_process = None

def is_ddma_curator_running() -> bool:
    """Checks if DDMA Curator server is running on port 8000."""
    global ddma_curator_process
    if ddma_curator_process and ddma_curator_process.poll() is None:
        return True
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            return s.connect_ex(('127.0.0.1', 8000)) == 0
    except Exception:
        return False

def is_mdserve_running() -> bool:
    """Checks if mdbook serve is running either via sub-process or port 3000."""
    global mdserve_process
    if mdserve_process and mdserve_process.poll() is None:
        return True
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            return s.connect_ex(('127.0.0.1', 3000)) == 0
    except Exception:
        return False

def kill_mdserve():
    """Terminates mdbook serve process cleanly."""
    global mdserve_process
    if mdserve_process:
        try:
            mdserve_process.terminate()
            mdserve_process.wait(timeout=1)
        except Exception:
            try:
                mdserve_process.kill()
            except Exception:
                pass
        mdserve_process = None

    # Kill any orphan mdbook processes on port 3000
    if sys.platform == "win32":
        try:
            subprocess.run(["taskkill", "/F", "/IM", "mdbook.exe"], capture_output=True)
        except Exception:
            pass
    else:
        try:
            subprocess.run(["pkill", "-f", "mdbook serve"], capture_output=True)
        except Exception:
            pass

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "spotify_url": "https://open.spotify.com/show/7doWf0GON9JsG6r8igc7RE",
        "apple_podcasts_url": "https://podcasts.apple.com/us/podcast/deep-dive-with-gemini/id1844532251",
        "youtube_music_url": "https://music.youtube.com/playlist?list=PLIX4sFsmu37qtJMlv-VzMYWM26M1QyXTe",
        "fountain_url": "https://fountain.fm/show/7LBvZT6ffpGyubvk8aSF",
        "tiktok_handle": "@shutosha@bot",
        "instagram_handle": "@shutosha@bot",
        "lightning_address": "shutosha@primal.net",
        "downloads_path": "C:/Users/ashut/Downloads",
        "title_word_limit": 5,
        "port": 8088
    }

def save_settings(settings_data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings_data, f, indent=2)

def sanitize_katex_markdown(text: str, title_override: str = None, word_limit: int = 5) -> tuple[str, str, int]:
    r"""
    Sanitizes markdown content for mdbook-katex:
    1. Fixes math delimiters: $...$ and $$...$$ without whitespace touching $
    2. Escapes unescaped financial currency ($100M -> \$100M)
    3. Re-indexes and hyper-links footnotes [^N]
    4. Extracts and limits H1 title to word_limit words
    """
    content = text.strip()

    # Strip Rust or Python string literals or variable assignments if present
    content = re.sub(r'^(?:Rust)?r#+"\s*', '', content)
    content = re.sub(r'"#+\s*$', '', content)
    content = re.sub(r'^(?:raw_markdown|markdown_text|content|payload_text|research_content)\s*=\s*(?:r?[\'"]{3}|r?[\'"])\s*', '', content)
    content = re.sub(r'[\'"]{3}\s*$', '', content)
    content = re.sub(r'(?m)^```(?:markdown|text|rust|python)?\s*$', '', content)
    content = content.strip()

    # Extract H1 Title
    h1_match = re.search(r'(?m)^#\s+(?:(?:\d+)\s*[:\s]*)?\s*(.*)$', content)
    extracted_title = "Untitled"
    if h1_match:
        extracted_title = h1_match.group(1).strip().strip('*')
        content = re.sub(r'(?m)^#\s+.*$', '', content, count=1).strip()

    if title_override and title_override.strip():
        final_title = title_override.strip()
    else:
        final_title = extracted_title

    # Word limit on title
    title_words = final_title.split()
    if len(title_words) > word_limit:
        clean_title = " ".join(title_words[:word_limit])
    else:
        clean_title = final_title

    # KaTeX delimiter hardening:
    # Protect block math $$...$$
    blocks = []
    def save_block(m):
        idx = len(blocks)
        inner = m.group(1).strip()
        blocks.append(f"\n\n$${inner}$$\n\n")
        return f"__KATEX_BLOCK_{idx}__"

    content = re.sub(r'\$\$(.*?)\$\$', save_block, content, flags=re.DOTALL)

    # Protect inline math $...$
    inlines = []
    def save_inline(m):
        idx = len(inlines)
        inner = m.group(1).strip()
        inlines.append(f"${inner}$")
        return f"__KATEX_INLINE_{idx}__"

    # Match inline math where dollar signs have no space touching them
    content = re.sub(r'(?<!\\)\$([^\$\n]+?)(?<!\\)\$', save_inline, content)

    # Escape standalone financial currency dollars e.g. $100, $50M, $1.5B
    content = re.sub(r'(?<!\\)\$(\d+(?:,\d+)*(?:\.\d+)?(?:[kKmMbBtT]|(?:\s*(?:million|billion|trillion|USD|usd)))?)', r'\\$\1', content)

    # Restore inlines and blocks
    for idx, inl in enumerate(inlines):
        content = content.replace(f"__KATEX_INLINE_{idx}__", inl)
    for idx, blk in enumerate(blocks):
        content = content.replace(f"__KATEX_BLOCK_{idx}__", blk)

    # Normalize excessive newlines
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Count citations
    citation_count = len(re.findall(r'\[\^\d+\]', content))

    return content, clean_title, citation_count

def ensure_syndication_and_wallet_blocks(content: str, settings: dict = None) -> str:
    """
    Guarantees that the article contains the Twentyuno Sats Lightning Widget
    and Audio platform links (Spotify, Apple Podcasts, Fountain.fm) situated
    directly above the Works Cited / Citations section.
    """
    settings = settings or load_settings()
    lightning_addr = settings.get("lightning_address", "shutosha@primal.net")
    spotify_url = settings.get("spotify_url", "https://open.spotify.com/show/7doWf0GON9JsG6r8igc7RE")
    apple_url = settings.get("apple_podcasts_url", "https://podcasts.apple.com/us/podcast/deep-dive-with-gemini/id1844532251")
    fountain_url = settings.get("fountain_url", "https://fountain.fm/show/7LBvZT6ffpGyubvk8aSF")

    social_block = f"""---

### Tips and Donations

If you enjoyed this research, consider supporting the project with a tip in **Sats**. It's a simple, global way to support independent research.

<!-- SOCIALS_START -->

<center>
<lightning-widget
  name="Thanks for supporting the publication"
  accent="#f9ce00"
  to="{lightning_addr}"
  image="https://nostrcheck.me/media/5af0794606a15b5641e25aa23d04af4cb0d7d5e68b11cacb47e56a4698fca8c4/49ff6d00cb5bc819cd19f77783d4815fbd46a5b99b6fbdead1eaecfab798187b.webp"
/>
</center>
<script src="https://embed.twentyuno.net/js/app.js"></script>

<center><a href="{spotify_url}" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">Spotify</a><a href="{apple_url}" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">Apple Podcasts</a><a href="{fountain_url}" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px;">Fountain.fm</a></center>

<!-- SOCIALS_END -->

To send Sats, you'll need a [lightning wallet](https://lightningaddress.com/).

---"""

    # If the widget and donation section are already present, do not duplicate
    if "lightning-widget" in content and "Tips and Donations" in content:
        return content

    # Clean out orphan SOCIALS tags
    cleaned = re.sub(r'<!-- SOCIALS_START -->[\s\S]*?<!-- SOCIALS_END -->', '', content).strip()

    # Locate Works Cited / Citations header
    cited_match = re.search(r'(?mi)^(?:\#\#+|\*{2}|_{2})?\s*(?:Works Cited|References|Sources|Bibliography)', cleaned)
    if cited_match:
        idx = cited_match.start()
        return cleaned[:idx].rstrip() + "\n\n" + social_block.strip() + "\n\n" + cleaned[idx:].lstrip()
    else:
        return cleaned.rstrip() + "\n\n" + social_block.strip() + "\n"

def extract_python_payload(payload_code: str) -> tuple[str, str, int, int]:
    """
    Extracts research markdown from a self-extracting Python script or raw markdown.
    Supports:
    1. Multiline raw markdown literals in Python (raw_markdown = \"\"\"...\"\"\")
    2. Base64 + Gzip encoded payload variables (ENCODED_PAYLOAD, payload_text, etc.)
    3. Direct raw markdown content.
    """
    code_str = payload_code.strip()

    # 1. Check for multiline string assignment e.g. raw_markdown = """..."""
    lit_match = re.search(r'(?:raw_markdown|markdown_text|content|payload_text|research_content)\s*=\s*(?:r?[\'"]{3}([\s\S]*?)[\'"]{3})', code_str)
    if lit_match:
        extracted = lit_match.group(1).strip()
        return extracted, len(code_str), len(extracted)

    # 2. Try Python AST parsing for exact variable extraction
    try:
        clean_ast_code = code_str
        if clean_ast_code.startswith("# ") and "\nimport " in clean_ast_code:
            clean_ast_code = clean_ast_code[clean_ast_code.find("import "):]

        tree = ast.parse(clean_ast_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        if var_name in ["encoded_payload", "payload_text", "payload", "b64_data", "compressed_payload", "raw_markdown", "markdown_text", "content", "data", "research_content", "payload_b64"]:
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                val = node.value.value
                                # If it's raw markdown
                                if val.strip().startswith("#") or "## " in val:
                                    return val.strip(), len(code_str), len(val)
                                # If it looks like base64
                                try:
                                    b64_clean = val.replace('\n', '').replace(' ', '').strip()
                                    raw_bytes = base64.b64decode(b64_clean)
                                    try:
                                        decomp = gzip.decompress(raw_bytes).decode('utf-8')
                                        return decomp, len(b64_clean), len(decomp)
                                    except Exception:
                                        # Raw uncompressed base64
                                        decoded_text = raw_bytes.decode('utf-8')
                                        if decoded_text.strip().startswith("#") or "## " in decoded_text:
                                            return decoded_text, len(b64_clean), len(decoded_text)
                                        raise ValueError("Corrupted Gzip Base64 payload: The LLM hallucinated compressed tokens in chat instead of executing Python compression.")
                                except ValueError:
                                    raise
                                except Exception as be:
                                    raise ValueError(f"Base64 decoding failed: {be}")
    except ValueError:
        raise
    except Exception:
        pass

    # 3. Base64 regex fallback
    b64_match = re.search(r'(?:ENCODED_PAYLOAD|payload_text|PAYLOAD|payload|b64_data|PAYLOAD_B64)\s*=\s*(?:\(\s*([\s\S]*?)\s*\)|[\'"]([A-Za-z0-9+/=\s\n]+)[\'"])', code_str)
    if b64_match:
        raw_block = b64_match.group(1) or b64_match.group(2)
        strings = re.findall(r'[\'"]([A-Za-z0-9+/=]+)[\'"]', raw_block)
        if not strings:
            strings = [raw_block.replace('\n', '').replace(' ', '').strip()]
        b64_str = ''.join(strings)
        try:
            raw_bytes = base64.b64decode(b64_str)
            decomp = gzip.decompress(raw_bytes).decode('utf-8')
            return decomp, len(b64_str), len(decomp)
        except Exception as e:
            raise ValueError("Corrupted Gzip Base64 payload: The LLM hallucinated compressed tokens in chat.")

    # 4. If it's already pure markdown text (not a python script)
    if not ("if __name__" in code_str or "import " in code_str):
        return code_str, len(code_str), len(code_str)

    raise ValueError("Could not extract markdown content from the uploaded payload.")

def find_episode_videos(slug_or_num: str) -> list[dict]:
    """
    Discovers video clips across canonical DDMA episodes store (src/ddma/docs/episodes/)
    and legacy fallback directories per agent.md.
    """
    clean_id = str(slug_or_num).replace('.md', '').lstrip('_')
    candidates = []

    # 1. Modern Canonical DDMA Standard (src/ddma/docs/episodes/<ep>/clips/)
    canonical_ep_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / "clips"
    if canonical_ep_dir.exists():
        candidates.extend(canonical_ep_dir.glob("*.mp4"))

    # 2. ddma/docs/episodes/<clean_id>/clips/*.mp4 (Root fallback)
    ep_clips_dir = PROJECT_ROOT / "ddma" / "docs" / "episodes" / clean_id / "clips"
    if ep_clips_dir.exists():
        candidates.extend(ep_clips_dir.glob("*.mp4"))

    # 3. Legacy episodes store (src/vid/<clean_id>-*.mp4)
    candidates.extend(VID_DIR.glob(f"{clean_id}-*.mp4"))
    candidates.extend(VID_DIR.glob(f"_{clean_id}-*.mp4"))

    # 4. ddma/docs/assets/clips/<clean_id>-*.mp4
    assets_clips_dir = PROJECT_ROOT / "ddma" / "docs" / "assets" / "clips"
    if assets_clips_dir.exists():
        candidates.extend(assets_clips_dir.glob(f"{clean_id}-*.mp4"))

    # 5. ddma/clips/<clean_id>-*.mp4
    ddma_clips_dir = PROJECT_ROOT / "ddma" / "clips"
    if ddma_clips_dir.exists():
        candidates.extend(ddma_clips_dir.glob(f"{clean_id}-*.mp4"))

    seen = set()
    final_clips = []
    for path in candidates:
        name = path.name
        if name in seen or "-original.mp4" in name or "-mosaic-" in name:
            continue
        seen.add(name)
        clip_label = name.replace('.mp4', '').replace('_', ' ')
        final_clips.append({
            "name": name,
            "url": f"/media/ddma/docs/episodes/{clean_id}/clips/{name}" if "ddma" in str(path) else f"/vid/{name}",
            "label": clip_label
        })

    def sort_key(clip):
        nums = re.findall(r'\d+', clip["name"])
        return [int(n) for n in nums] if nums else [clip["name"]]

    final_clips.sort(key=sort_key)
    return final_clips

def find_episode_cover(slug_or_num: str) -> bool:
    """
    Checks for cover art across src/img/ and DDMA asset locations.
    """
    clean_id = str(slug_or_num).replace('.md', '').lstrip('_')
    for ext in ['.png', '.jpg']:
        if (IMG_DIR / f"{clean_id}{ext}").exists() or (IMG_DIR / f"_{clean_id}{ext}").exists():
            return True
    ddma_ep_dir = PROJECT_ROOT / "ddma" / "docs" / "episodes" / clean_id
    if (ddma_ep_dir / "cover.png").exists() or (ddma_ep_dir / "thumbnail.png").exists():
        return True
    if (PROJECT_ROOT / "ddma" / "docs" / "assets" / f"{clean_id}.png").exists():
        return True
    return False

# Active transcription jobs: { clean_id: { "status": "idle"|"processing"|"done"|"error", "progress": str, "error": str } }
transcription_jobs = {}

def get_episode_audio_path(clean_id: str) -> Path | None:
    """Discovers local NotebookLM audio file for an episode."""
    possible_dirs = [
        SRC_DIR / "ddma" / "docs" / "episodes" / clean_id,
        PROJECT_ROOT / "ddma" / "docs" / "episodes" / clean_id,
        SRC_DIR / "audio",
        PROJECT_ROOT / "ddma" / "audio",
    ]
    for d in possible_dirs:
        for ext in [".mp3", ".wav", ".m4a", ".ogg", ".aac"]:
            f = d / f"audio{ext}"
            if f.exists():
                return f
            f_named = d / f"{clean_id}{ext}"
            if f_named.exists():
                return f_named
            f_nb = d / f"notebooklm{ext}"
            if f_nb.exists():
                return f_nb
    return None

def get_episode_transcript_path(clean_id: str) -> Path:
    """Returns canonical path to episode transcript.txt (ensuring directory exists)."""
    target_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / "transcript.txt"

def get_episode_narrative_path(clean_id: str) -> Path:
    """Returns canonical path to episode narrative.md (ensuring directory exists)."""
    target_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / "narrative.md"

def smart_streamline_narrative(raw_text: str) -> tuple[str, int]:
    """
    Intelligently structures continuous audio transcripts into:
    1. Clean, well-spaced editorial paragraphs.
    2. Speaker/dialogue headers (**Host**, **Guest**).
    3. Isolated promotional / sponsor / channel notes in callout quote blocks (> 📢 **Promotional Note**: ...).
    Returns (streamlined_markdown, promo_blocks_count).
    """
    if not raw_text or not raw_text.strip():
        return "", 0

    text = raw_text.strip()

    # Normalize whitespace & punctuation
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\s+([,.:;?!])', r'\1', text)
    text = re.sub(r'([,.:;?!])(?=[^\s\d])', r'\1 ', text)
    text = re.sub(r'\bi\b', 'I', text)
    text = re.sub(r'\bi\'m\b', "I'm", text, flags=re.IGNORECASE)
    text = re.sub(r'\bi\'ve\b', "I've", text, flags=re.IGNORECASE)
    text = re.sub(r'\bi\'ll\b', "I'll", text, flags=re.IGNORECASE)
    text = re.sub(r'\bi\'d\b', "I'd", text, flags=re.IGNORECASE)

    # Capitalize after sentence terminators
    text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
    if text:
        text = text[0].upper() + text[1:]

    # Promotional detection regex pattern
    promo_patterns = [
        r'\b(?:sponsor(?:ed|s)?|patreon|subscribe|follow us on|discount code|promo code|rate and review|check out the link|link in the description|leave a five star|support (?:us|the show|the podcast))\b',
        r'\b(?:supported by|brought to you by|special offer|advertis(?:er|ement)|our partners? at)\b'
    ]
    promo_regex = re.compile('|'.join(promo_patterns), re.IGNORECASE)

    # Split into sentences
    sentence_regex = re.compile(r'[^.!?]+[.!?]+(?:\s+|$)')
    sentences = sentence_regex.findall(text)
    if not sentences:
        sentences = [text]

    paragraphs = []
    current_para = []
    promo_count = 0

    for idx, s in enumerate(sentences):
        s_clean = s.strip()
        if not s_clean:
            continue

        # Check if this sentence is a promotional note
        is_promo = bool(promo_regex.search(s_clean))

        if is_promo:
            if current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
            paragraphs.append(f"> 📢 **Promotional / Channel Note**\n> {s_clean}")
            promo_count += 1
            continue

        current_para.append(s_clean)

        # Natural paragraph boundary transitions
        is_transition = bool(re.match(r'^(However|Moreover|Furthermore|In addition|Therefore|Clinically|When|So|Now|And|In fact|Specifically|That said|Interestingly|If |By the time|This is |On the other hand|What is fascinating|To understand this|Here is why|Let us look|Consider|Notice how)', s_clean, re.IGNORECASE))
        
        # Speaker prefix detection
        speaker_match = re.match(r'^(Host|Guest|Speaker \d+|Interviewer|Narrator)\s*:\s*(.*)', s_clean, re.IGNORECASE)
        if speaker_match:
            speaker_name = speaker_match.group(1).title()
            rest = speaker_match.group(2)
            current_para[-1] = f"**{speaker_name}**: {rest}"

        if len(current_para) >= 4 or (len(current_para) >= 2 and is_transition and idx > 0) or idx == len(sentences) - 1:
            paragraphs.append(' '.join(current_para))
            current_para = []

    if current_para:
        paragraphs.append(' '.join(current_para))

    return '\n\n'.join(paragraphs), promo_count


def seed_ddma_project_if_missing(clean_id: str) -> str:
    """
    Seeds DDMA project folder ddma/projects/episode_<clean_id> if it doesn't already exist.
    Copies audio from src/ddma/docs/episodes/<clean_id>/ or src/
    Copies transcript and generates transcription.json and plan.json with max_duration <= 165s.
    Returns the project_id (e.g. 'episode_247').
    """
    project_id = f"episode_{clean_id}"
    clean_id_digits = re.sub(r'\D', '', clean_id)
    
    # Locate all potential DDMA roots
    ddma_roots = []
    parent_ddma = PROJECT_ROOT.parent / "ddma"
    if parent_ddma.exists():
        ddma_roots.append(parent_ddma)
    local_ddma = PROJECT_ROOT / "ddma"
    if local_ddma.exists() and local_ddma not in ddma_roots:
        ddma_roots.append(local_ddma)
    if not ddma_roots:
        ddma_roots.append(parent_ddma)

    # Locate audio source
    audio_path = get_episode_audio_path(clean_id)
    if not audio_path and clean_id_digits:
        audio_path = get_episode_audio_path(clean_id_digits)
    
    # Locate transcript source
    transcript_path = get_episode_transcript_path(clean_id)
    if not transcript_path.exists() and clean_id_digits:
        transcript_path = get_episode_transcript_path(clean_id_digits)

    # Read transcript text if available
    transcript_text = ""
    if transcript_path.exists():
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript_text = f.read()
        except Exception:
            pass

    # Determine episode title
    episode_title = f"Episode {clean_id}"
    for candidate_fn in [f"{clean_id}.md", f"_{clean_id}.md", f"{clean_id_digits}.md"]:
        md_p = SRC_DIR / candidate_fn
        if md_p.exists():
            try:
                with open(md_p, "r", encoding="utf-8") as mf:
                    h1_match = re.search(r'(?m)^#\s+(.*)$', mf.read())
                    if h1_match:
                        episode_title = h1_match.group(1).strip()
                        break
            except Exception:
                pass

    # Determine audio duration via ffprobe
    audio_duration = 0.0
    if audio_path and audio_path.exists():
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0 and res.stdout.strip():
                audio_duration = float(res.stdout.strip())
        except Exception:
            pass

    # Build or extract Whisper segments for transcription.json
    segments = []
    src_trans_json = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / "transcription.json"
    if src_trans_json.exists():
        try:
            with open(src_trans_json, "r", encoding="utf-8") as tj:
                t_obj = json.load(tj)
                segments = t_obj.get("segments", [])
                if not transcript_text:
                    transcript_text = t_obj.get("text", "")
        except Exception:
            pass

    # If true acoustic segments with words are missing, transcribe with Whisper (word_timestamps=True)
    has_valid_words = bool(segments and any(s.get("words") for s in segments))
    if not has_valid_words and audio_path and audio_path.exists():
        try:
            import whisper
            settings = load_settings()
            mname = settings.get("whisper_model", "small.en")
            try:
                model = whisper.load_model(mname)
            except Exception:
                model = whisper.load_model("base")
            res_obj = model.transcribe(str(audio_path), fp16=False, word_timestamps=True)
            segments = res_obj.get("segments", [])
            transcript_text = res_obj.get("text", "").strip() or transcript_text
            
            # Save acoustic transcription.json in src
            src_trans_json.parent.mkdir(parents=True, exist_ok=True)
            with open(src_trans_json, "w", encoding="utf-8") as tj:
                json.dump(res_obj, tj, indent=4)
        except Exception as we:
            print(f"[DDMA SEED] Whisper acoustic alignment fallback: {we}")

    if not segments and transcript_text:
        # Emergency fallback: Synthesize segments from transcript sentences distributed over audio_duration
        sentences = [s.strip() for s in re.split(r'(?<=[.?!])\s+', transcript_text) if s.strip()]
        if not sentences:
            sentences = [transcript_text]
        
        total_dur = audio_duration if audio_duration > 10.0 else max(len(sentences) * 5.0, 180.0)
        total_chars = sum(len(s) for s in sentences) or 1
        curr_t = 0.0
        for i, s in enumerate(sentences):
            dur = (len(s) / total_chars) * total_dur
            dur = max(1.5, dur)
            end_t = min(curr_t + dur, total_dur) if i < len(sentences) - 1 else total_dur
            
            words = s.split()
            word_list = []
            if words:
                w_dur = (end_t - curr_t) / len(words)
                w_curr = curr_t
                for w in words:
                    w_end = min(w_curr + w_dur, end_t)
                    word_list.append({"word": w, "start": round(w_curr, 2), "end": round(w_end, 2)})
                    w_curr = w_end

            segments.append({
                "id": i,
                "start": round(curr_t, 2),
                "end": round(end_t, 2),
                "text": s,
                "words": word_list
            })
            curr_t = end_t

    transcription_payload = {
        "text": transcript_text,
        "segments": segments
    }

    # Iterate over DDMA roots and create/update project folder
    for root_dir in ddma_roots:
        proj_dir = root_dir / "projects" / project_id
        proj_dir.mkdir(parents=True, exist_ok=True)

        audio_ext = audio_path.suffix if audio_path else ".m4a"
        dest_audio_name = f"{clean_id}{audio_ext}"
        dest_audio_path = proj_dir / dest_audio_name

        # Copy audio if missing
        if audio_path and audio_path.exists() and not dest_audio_path.exists():
            try:
                shutil.copy2(str(audio_path), str(dest_audio_path))
            except Exception as ce:
                print(f"[DDMA SEED] Error copying audio: {ce}")

        # Write project_info.json
        info_path = proj_dir / "project_info.json"
        project_info = {
            "id": project_id,
            "name": f"Episode {clean_id}",
            "title": episode_title,
            "audio_filename": dest_audio_name,
            "audio_file": dest_audio_name,
            "status": "ready"
        }
        with open(info_path, "w", encoding="utf-8") as inf:
            json.dump(project_info, inf, indent=4)

        # Write transcript.txt
        if transcript_text:
            with open(proj_dir / "transcript.txt", "w", encoding="utf-8") as tf:
                tf.write(transcript_text)

        # Write transcription.json if missing
        trans_json_dest = proj_dir / "transcription.json"
        if not trans_json_dest.exists() or trans_json_dest.stat().st_size == 0:
            with open(trans_json_dest, "w", encoding="utf-8") as tj:
                json.dump(transcription_payload, tj, indent=4)

        # Generate plan.json if missing
        plan_json_dest = proj_dir / "plan.json"
        if not plan_json_dest.exists() or plan_json_dest.stat().st_size == 0:
            # Try running ddma.py plan CLI first
            cli_script = root_dir / "ddma.py"
            plan_generated = False
            if cli_script.exists() and dest_audio_path.exists() and trans_json_dest.exists():
                try:
                    cmd = [
                        sys.executable, str(cli_script), "plan",
                        "--audio", str(dest_audio_path),
                        "--transcription", str(trans_json_dest),
                        "--max-duration", "165.0",
                        "--min-duration", "90.0",
                        "--out", str(plan_json_dest)
                    ]
                    res = subprocess.run(cmd, cwd=str(root_dir), capture_output=True, text=True, timeout=30)
                    if res.returncode == 0 and plan_json_dest.exists() and plan_json_dest.stat().st_size > 10:
                        plan_generated = True
                except Exception as pe:
                    print(f"[DDMA SEED] CLI plan failed: {pe}")

            # Fallback Python generator for plan.json under strict <= 165s
            if not plan_generated and segments:
                stings = [
                    "Bluesy Vibes (Sting) - Doug Maxwell_Media Right Productions.mp3",
                    "Howling (Sting) - Gunnar Olsen.mp3",
                    "Demilitarized Zone (Sting) - Ethan Meixsell.mp3",
                    "Double Helix (Sting) - Ethan Meixsell.mp3"
                ]
                total_duration = audio_duration or (segments[-1]["end"] if segments else 180.0)
                clips_plan = []
                t_curr = 0.0
                clip_num = 1
                max_dur = 165.0
                min_dur = 90.0

                while t_curr < total_duration:
                    target_b = min(t_curr + max_dur, total_duration)
                    # Find candidate boundary
                    candidates = [s["end"] for s in segments if s["end"] > t_curr]
                    valid = [c for c in candidates if min_dur <= (c - t_curr) <= max_dur]
                    if valid:
                        target_b = max(valid)
                    elif candidates:
                        if (total_duration - t_curr) <= max_dur:
                            target_b = total_duration
                        else:
                            target_b = min(candidates, key=lambda c: abs((c - t_curr) - max_dur))
                    
                    if total_duration - target_b < 15.0:
                        target_b = total_duration

                    clip_dur = round(target_b - t_curr, 2)
                    in_win = [s for s in segments if s["start"] >= t_curr and s["end"] <= target_b + 0.5]
                    win_text = " ".join(s["text"] for s in in_win).strip()
                    
                    # 5-part structure
                    intro_music = stings[(clip_num - 1) % len(stings)]
                    hook_end = min(t_curr + 22.0, target_b)
                    hook_win = [s for s in in_win if s["start"] >= t_curr and s["end"] <= hook_end + 1.0]
                    hook_text = " ".join(s["text"] for s in hook_win).strip() or win_text[:120]
                    
                    c_obj = {
                        "num": clip_num,
                        "title": f"Clip {clip_num}",
                        "start": round(t_curr, 2),
                        "end": round(target_b, 2),
                        "duration": clip_dur,
                        "bridge_text": [f"What is the deeper secret behind Part {clip_num}?"],
                        "segments": [
                            {"type": "music", "music_file": intro_music, "duration": 5.5, "crossfade": 1.3, "volume": 1.0},
                            {"type": "audio", "start": round(t_curr, 2), "end": round(hook_end, 2), "duration": round(hook_end - t_curr, 2), "text": hook_text},
                            {"type": "music", "music_file": "deepDive-strong.mp3" if clip_num == 1 else "deepDive-soft-ok.mp3", "duration": 7.5, "crossfade": 0.0, "volume": 1.0},
                            {"type": "audio", "start": round(hook_end, 2), "end": round(target_b, 2), "duration": round(target_b - hook_end, 2), "text": win_text},
                            {"type": "music", "music_file": "Howling (Sting) - Gunnar Olsen.mp3", "duration": 4.5, "crossfade": 0.3, "volume": 1.0}
                        ],
                        "locked": False
                    }
                    clips_plan.append(c_obj)

                    if target_b >= total_duration:
                        break
                    t_curr = target_b
                    clip_num += 1

                with open(plan_json_dest, "w", encoding="utf-8") as pf:
                    json.dump(clips_plan, pf, indent=4)

    return project_id


def parse_summary_structure():
    """
    Parses SUMMARY.md and discovers Mempool drafts, Template episodes, and Master Chain blocks.
    """
    if not SUMMARY_FILE.exists():
        return [], [], [], 247

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    mempool_items = []
    template_items = []
    chain_items = []
    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        l_lower = stripped.lower()
        if "- [mempool" in l_lower:
            current_section = "mempool"
            continue
        elif "- [template" in l_lower:
            current_section = "template"
            continue
        elif "- [chain" in l_lower:
            current_section = "chain"
            continue
        elif stripped.startswith("#"):
            continue

        # Match markdown links: - [Title](filename.md)
        link_match = re.search(r'\[(.*?)\]\((.*?)\)', stripped)
        if link_match:
            title_text = link_match.group(1).strip()
            filename = link_match.group(2).strip()

            if filename in ["github.md", "mempool.md", "template.md", "chain.md", "cover.md", "block1.md", "block2.md", "genesis.md"]:
                continue

            file_path = SRC_DIR / filename
            clean_slug = filename.replace(".md", "").lstrip("_")
            has_img = find_episode_cover(clean_slug)
            vid_clips = find_episode_videos(clean_slug)

            item = {
                "title": title_text,
                "filename": filename,
                "slug": clean_slug,
                "has_image": has_img,
                "vid_count": len(vid_clips),
                "is_locked": len(vid_clips) > 0,
                "exists": file_path.exists()
            }

            # Number detection
            num_match = re.match(r'^(\d+)\s*:', title_text)
            if num_match:
                item["number"] = int(num_match.group(1))
            elif filename.replace(".md", "").isdigit():
                item["number"] = int(filename.replace(".md", ""))
            else:
                item["number"] = None

            if current_section == "mempool":
                mempool_items.append(item)
            elif current_section == "template":
                template_items.append(item)
            elif current_section == "chain":
                chain_items.append(item)

    # Calculate next episode number
    template_numbers = [item["number"] for item in template_items if item.get("number")]
    chain_numbers = [item["number"] for item in chain_items if item.get("number")]
    all_numbers = template_numbers + chain_numbers
    next_number = max(all_numbers, default=240) + 1

    return mempool_items, template_items, chain_items, next_number

def sync_summary_file(mempool_items, template_items):
    """
    Safely writes SUMMARY.md with updated Mempool and Template sections,
    preserving header links, Chain, and Genesis pillars intact.
    Automatically creates a timestamped pre-write backup.
    """
    if not SUMMARY_FILE.exists():
        return

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Pre-write safety backup
    try:
        backup_dir = INGEST_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"SUMMARY_{timestamp}.md.bak"
        with open(backup_file, "w", encoding="utf-8") as bf:
            bf.write(content)

        # Retain the last 30 snapshots
        all_backups = sorted(backup_dir.glob("SUMMARY_*.md.bak"))
        if len(all_backups) > 30:
            for old_b in all_backups[:-30]:
                try:
                    old_b.unlink()
                except Exception:
                    pass
    except Exception as be:
        print(f"[WARN] Failed to write pre-write backup: {be}")

    lines = content.splitlines()
    header_lines = []
    chain_lines = []
    in_header = True
    in_chain = False

    for line in lines:
        l = line.strip().lower()
        if "- [mempool" in l or "- [template" in l or "- [chain" in l:
            in_header = False

        if in_header:
            header_lines.append(line)

        if "- [chain" in l:
            in_chain = True

        if in_chain:
            chain_lines.append(line)

    # Build new Summary
    new_lines = []
    # 1. Header (e.g. # Summary \n - [deepDive](./cover.md))
    for h in header_lines:
        new_lines.append(h)

    # 2. Mempool
    new_lines.append("- [mempool](mempool.md)")
    if not mempool_items:
        new_lines.append("    - [None at this moment. Join us on GitHub!](github.md)")
    else:
        for item in mempool_items:
            fn = item["filename"]
            title = item["title"]
            new_lines.append(f"    - [{title}]({fn})")

    new_lines.append("")

    # 3. Template
    new_lines.append("- [template](template.md)")
    for item in template_items:
        fn = item["filename"]
        title = item["title"]
        new_lines.append(f"    - [{title}]({fn})")

    new_lines.append("")

    # 4. Chain & Genesis (Preserved 100%)
    for c in chain_lines:
        new_lines.append(c)

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

class IngestRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(INGEST_DIR), **kwargs)

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path

        if path == "/" or path == "/index.html":
            self.path = "/cockpit.html"
            return super().do_GET()

        if path == "/api/status":
            mempool, template, chain, next_num = parse_summary_structure()
            settings = load_settings()
            resp = {
                "mempool": mempool,
                "template": template,
                "chain": chain,
                "next_episode_number": next_num,
                "active_block_count": len(template),
                "settings": settings,
                "is_serving": is_mdserve_running()
            }
            self.send_json(resp)
            return

        if path == "/api/episode":
            params = parse_qs(url.query)
            fn = params.get("filename", [""])[0]
            if not fn or not (SRC_DIR / fn).exists():
                self.send_error(404, "Episode not found")
                return

            file_path = SRC_DIR / fn
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            h1_m = re.search(r'(?m)^#\s+(.*)$', raw_text)
            title = h1_m.group(1) if h1_m else "Untitled"
            words = len(raw_text.split())

            clean_id = fn.replace(".md", "").lstrip("_")
            has_cover = find_episode_cover(clean_id)
            vids = find_episode_videos(clean_id)

            self.send_json({
                "filename": fn,
                "title": title,
                "content": raw_text,
                "word_count": words,
                "has_cover": has_cover,
                "videos": vids,
                "is_draft": fn.startswith("_")
            })
            return

        if path == "/api/audio/status":
            params = parse_qs(url.query)
            fn = params.get("filename", [""])[0]
            clean_id = fn.replace(".md", "").lstrip("_")
            audio_path = get_episode_audio_path(clean_id)
            transcript_path = get_episode_transcript_path(clean_id)
            narrative_path = get_episode_narrative_path(clean_id)

            transcript_text = ""
            if transcript_path.exists():
                try:
                    with open(transcript_path, "r", encoding="utf-8") as f:
                        transcript_text = f.read()
                except Exception:
                    pass

            narrative_text = ""
            if narrative_path.exists():
                try:
                    with open(narrative_path, "r", encoding="utf-8") as f:
                        narrative_text = f.read()
                except Exception:
                    pass
            elif transcript_text:
                narrative_text, _ = smart_streamline_narrative(transcript_text)

            job = transcription_jobs.get(clean_id, {"status": "idle", "progress": ""})

            audio_rel_url = None
            if audio_path:
                try:
                    rel = audio_path.relative_to(SRC_DIR)
                    audio_rel_url = f"/src/{rel.as_posix()}"
                except ValueError:
                    audio_rel_url = f"/media/{audio_path.name}"

            self.send_json({
                "clean_id": clean_id,
                "has_audio": audio_path is not None,
                "audio_filename": audio_path.name if audio_path else None,
                "audio_url": audio_rel_url,
                "has_transcript": len(transcript_text.strip()) > 0,
                "transcript": transcript_text,
                "narrative_md": narrative_text,
                "job_status": job.get("status", "idle"),
                "job_progress": job.get("progress", ""),
                "job_error": job.get("error", "")
            })
            return

        if path == "/api/ddma/status":
            params = parse_qs(url.query)
            fn = params.get("filename", [""])[0]
            clean_id = fn.replace(".md", "").lstrip("_")
            
            ddma_ep_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id
            clips_dir = ddma_ep_dir / "clips"
            clips = []
            
            # 1. Discover clips in src/ddma/docs/episodes/<id>/clips
            if clips_dir.exists():
                for ext in [".mp4", ".mov", ".webm"]:
                    for cf in sorted(clips_dir.glob(f"*{ext}")):
                        clips.append({
                            "name": cf.name,
                            "label": cf.name.replace(".mp4", "").replace("_", " "),
                            "url": f"/media/ddma/docs/episodes/{clean_id}/clips/{cf.name}",
                            "size_bytes": cf.stat().st_size
                        })
            
            # 2. Discover clips in ddma/projects/episode_<id>/clips
            for ddma_root in [PROJECT_ROOT.parent / "ddma", PROJECT_ROOT / "ddma"]:
                proj_clips = ddma_root / "projects" / f"episode_{clean_id}" / "clips"
                if proj_clips.exists():
                    for ext in [".mp4", ".mov", ".webm"]:
                        for cf in sorted(proj_clips.glob(f"*{ext}")):
                            if not any(c["name"] == cf.name for c in clips):
                                clips.append({
                                    "name": cf.name,
                                    "label": cf.name.replace(".mp4", "").replace("_", " "),
                                    "url": f"/media/ddma/projects/episode_{clean_id}/clips/{cf.name}",
                                    "size_bytes": cf.stat().st_size
                                })

            audio_path = get_episode_audio_path(clean_id)
            transcript_path = get_episode_transcript_path(clean_id)
            
            self.send_json({
                "clean_id": clean_id,
                "ep_dir_exists": ddma_ep_dir.exists(),
                "ep_dir_path": str(ddma_ep_dir),
                "clips_count": len(clips),
                "clips": clips,
                "has_audio": audio_path is not None,
                "has_transcript": transcript_path.exists() and transcript_path.stat().st_size > 0,
                "curator_running": is_ddma_curator_running(),
                "curator_url": f"http://localhost:8000/curator.html?project=episode_{clean_id}"
            })
            return

        if path == "/api/settings":
            self.send_json(load_settings())
            return

        # Media Streaming routes for video clips and cover images
        if path.startswith("/media/") or path.startswith("/vid/") or path.startswith("/img/") or path.startswith("/src/"):
            clean_path = path.lstrip("/")
            if clean_path.startswith("media/"):
                clean_path = clean_path[len("media/"):]

            target_file = None
            possible_paths = [
                SRC_DIR / clean_path,
                PROJECT_ROOT / clean_path,
                PROJECT_ROOT.parent / clean_path,
                SRC_DIR / "ddma" / "docs" / "episodes" / clean_path,
                PROJECT_ROOT / "ddma" / "docs" / "episodes" / clean_path,
                PROJECT_ROOT.parent / "ddma" / clean_path,
                SRC_DIR / "vid" / Path(clean_path).name,
                SRC_DIR / "img" / Path(clean_path).name,
            ]
            for p in possible_paths:
                if p.exists() and p.is_file():
                    target_file = p
                    break

            if not target_file:
                fname = Path(clean_path).name
                ep_match = re.search(r'(\d+)', fname)
                ep_num = ep_match.group(1) if ep_match else ""
                if ep_num:
                    p1 = SRC_DIR / "ddma" / "docs" / "episodes" / ep_num / "clips" / fname
                    p2 = PROJECT_ROOT / "ddma" / "docs" / "episodes" / ep_num / "clips" / fname
                    p3 = PROJECT_ROOT.parent / "ddma" / "projects" / f"episode_{ep_num}" / "clips" / fname
                    if p1.exists(): target_file = p1
                    elif p2.exists(): target_file = p2
                    elif p3.exists(): target_file = p3

            if target_file and target_file.exists():
                self.serve_media_file(target_file)
                return
            else:
                self.send_error(404, "Media file not found")
                return

        # Serve static files from ingest/
        return super().do_GET()

    def serve_media_file(self, file_path: Path):
        """Streams media files (videos, images) with HTTP Range support."""
        try:
            file_size = file_path.stat().st_size
            ext = file_path.suffix.lower()
            mime_type = "video/mp4" if ext == ".mp4" else "image/png" if ext == ".png" else "image/jpeg" if ext in [".jpg", ".jpeg"] else "application/octet-stream"

            range_header = self.headers.get('Range')
            if range_header and range_header.startswith('bytes='):
                bytes_range = range_header[6:].split('-')
                start = int(bytes_range[0]) if bytes_range[0] else 0
                end = int(bytes_range[1]) if len(bytes_range) > 1 and bytes_range[1] else file_size - 1
                end = min(end, file_size - 1)
                length = end - start + 1

                self.send_response(206)
                self.send_header('Content-Type', mime_type)
                self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                self.send_header('Content-Length', str(length))
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                with open(file_path, 'rb') as f:
                    f.seek(start)
                    bytes_remaining = length
                    while bytes_remaining > 0:
                        chunk_size = min(64 * 1024, bytes_remaining)
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        bytes_remaining -= len(chunk)
            else:
                self.send_response(200)
                self.send_header('Content-Type', mime_type)
                self.send_header('Content-Length', str(file_size))
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                with open(file_path, 'rb') as f:
                    shutil.copyfileobj(f, self.wfile)
        except (ConnectionResetError, BrokenPipeError):
            pass
        except Exception:
            pass

    def do_POST(self):
        url = urlparse(self.path)
        path = url.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if path == "/api/payload/extract":
            code = data.get("code", "")
            title_override = data.get("title_override", "")
            settings = load_settings()
            word_limit = settings.get("title_word_limit", 5)

            try:
                raw_md, raw_size, md_size = extract_python_payload(code)
                sanitized_md, clean_title, citations = sanitize_katex_markdown(raw_md, title_override, word_limit)

                self.send_json({
                    "success": True,
                    "extracted_md": sanitized_md,
                    "title": clean_title,
                    "citation_count": citations,
                    "raw_size": raw_size,
                    "md_size": md_size
                })
            except Exception as e:
                self.send_json({
                    "success": False,
                    "error": str(e)
                })
            return

        if path == "/api/mempool/create":
            slug = data.get("slug", "").strip()
            title = data.get("title", "").strip()
            content = data.get("content", "").strip()
            settings = load_settings()
            word_limit = settings.get("title_word_limit", 5)

            try:
                raw_md, _, _ = extract_python_payload(content)
                sanitized_md, clean_title, _ = sanitize_katex_markdown(raw_md, title, word_limit)
                sanitized_md = ensure_syndication_and_wallet_blocks(sanitized_md, settings)

                if not slug:
                    slug = re.sub(r'[^a-zA-Z0-9_-]', '_', clean_title.lower()).strip('_') or "draft"

                slug = slug.lstrip('_')
                filename = f"_{slug}.md"
                file_path = SRC_DIR / filename
                sidebar_tag = f"<!-- SIDEBAR_TITLE: {clean_title} -->"
                full_content = f"# {clean_title}\n\n{sidebar_tag}\n\n{sanitized_md}\n"

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(full_content)

                # Update SUMMARY.md
                mempool, template, _, _ = parse_summary_structure()
                existing = next((item for item in mempool if item["filename"] == filename), None)
                if existing:
                    existing["title"] = clean_title
                else:
                    mempool.insert(0, {"title": clean_title, "filename": filename})

                sync_summary_file(mempool, template)

                self.send_json({
                    "success": True,
                    "filename": filename,
                    "slug": slug,
                    "title": clean_title
                })
            except Exception as e:
                self.send_json({
                    "success": False,
                    "error": str(e)
                })
            return

        if path == "/api/mempool/delete":
            filename = data.get("filename", "").strip()
            if not filename or not filename.startswith("_"):
                self.send_error(400, "Only Mempool drafts can be deleted")
                return

            file_path = SRC_DIR / filename
            if file_path.exists():
                file_path.unlink()

            # Remove from SUMMARY.md
            mempool, template, _, _ = parse_summary_structure()
            mempool = [m for m in mempool if m["filename"] != filename]
            sync_summary_file(mempool, template)

            self.send_json({"success": True, "filename": filename})
            return

        if path == "/api/template/lock":
            src_filename = data.get("filename", "")
            target_number = data.get("number")
            title_override = data.get("title", "")
            settings = load_settings()
            word_limit = settings.get("title_word_limit", 5)

            mempool, template, _, next_num = parse_summary_structure()
            if not target_number:
                target_number = next_num

            target_filename = f"{target_number}.md"
            src_path = SRC_DIR / src_filename
            dest_path = SRC_DIR / target_filename

            if not src_path.exists():
                self.send_error(404, f"Source file {src_filename} not found")
                return

            with open(src_path, "r", encoding="utf-8") as f:
                existing_text = f.read()

            sanitized_md, clean_title, _ = sanitize_katex_markdown(existing_text, title_override, word_limit)
            
            # Guarantee Tips and Donations (Twentyuno Sats Widget) and Audio Platform Links
            sanitized_md = ensure_syndication_and_wallet_blocks(sanitized_md, settings)

            formatted_title = f"{target_number} : {clean_title}"
            
            # Ensure sidebar title tag
            sidebar_tag = f"<!-- SIDEBAR_TITLE: {clean_title} -->"
            if "<!-- SIDEBAR_TITLE:" not in sanitized_md:
                full_content = f"# {formatted_title}\n\n{sidebar_tag}\n\n{sanitized_md}\n"
            else:
                full_content = f"# {formatted_title}\n\n{sanitized_md}\n"

            # Write to new episode file
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(full_content)

            # Remove old draft file
            if src_path != dest_path:
                src_path.unlink()

            # Migrate DDMA asset folders (audio, transcript, clips, plan)
            old_slug = src_filename.replace(".md", "").lstrip("_")
            old_ddma_dir = SRC_DIR / "ddma" / "docs" / "episodes" / old_slug
            new_ddma_dir = SRC_DIR / "ddma" / "docs" / "episodes" / str(target_number)
            new_ddma_dir.mkdir(parents=True, exist_ok=True)

            if old_ddma_dir.exists() and old_ddma_dir != new_ddma_dir:
                for item in old_ddma_dir.iterdir():
                    dest_item = new_ddma_dir / item.name
                    if item.is_dir():
                        if dest_item.exists():
                            shutil.rmtree(str(dest_item))
                        shutil.copytree(str(item), str(dest_item))
                    else:
                        shutil.copy2(str(item), str(dest_item))
                shutil.rmtree(str(old_ddma_dir), ignore_errors=True)

            # Migrate cover images if exist
            for ext in [".png", ".jpg"]:
                old_img = IMG_DIR / f"_{old_slug}{ext}"
                if not old_img.exists():
                    old_img = IMG_DIR / f"{old_slug}{ext}"
                if old_img.exists():
                    shutil.move(str(old_img), str(IMG_DIR / f"{target_number}{ext}"))

            # Update SUMMARY.md: remove from mempool, insert into template
            mempool = [m for m in mempool if m["filename"] != src_filename]
            template.insert(0, {"title": formatted_title, "filename": target_filename, "number": target_number})

            sync_summary_file(mempool, template)

            # Trigger background mdbook build to ensure compiled HTML is instantly fresh
            def bg_build():
                try:
                    subprocess.run(["mdbook", "build"], cwd=str(PROJECT_ROOT), capture_output=True)
                except Exception:
                    pass
            threading.Thread(target=bg_build, daemon=True).start()

            self.send_json({
                "success": True,
                "episode_number": target_number,
                "filename": target_filename,
                "title": formatted_title
            })
            return

        if path == "/api/episode/update_title":
            filename = data.get("filename", "").strip()
            raw_new_title = data.get("title", "").strip()

            if not filename or not raw_new_title:
                self.send_error(400, "Missing filename or title")
                return

            file_path = SRC_DIR / filename
            if not file_path.exists():
                self.send_error(404, f"File {filename} not found")
                return

            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            title_words = raw_new_title.split()
            clean_title_text = " ".join(title_words[:5]) if len(title_words) > 5 else raw_new_title
            clean_title_text = re.sub(r'^\d+\s*:\s*', '', clean_title_text).strip()

            num_match = re.match(r'^(\d+)\.md$', filename)
            if num_match:
                ep_num = int(num_match.group(1))
                formatted_summary_title = f"{ep_num} : {clean_title_text}"
            else:
                formatted_summary_title = clean_title_text

            sidebar_tag_regex = re.compile(r'<!--\s*SIDEBAR_TITLE:\s*.*?\s*-->', re.IGNORECASE)
            new_tag = f"<!-- SIDEBAR_TITLE: {clean_title_text} -->"

            if sidebar_tag_regex.search(file_content):
                file_content = sidebar_tag_regex.sub(new_tag, file_content)
            else:
                lines = file_content.splitlines(keepends=True)
                if lines and lines[0].startswith('#'):
                    lines.insert(1, f"\n{new_tag}\n")
                    file_content = "".join(lines)
                else:
                    file_content = f"{new_tag}\n\n{file_content}"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)

            mempool, template, _, _ = parse_summary_structure()
            for item in mempool:
                if item["filename"] == filename:
                    item["title"] = formatted_summary_title
            for item in template:
                if item["filename"] == filename:
                    item["title"] = formatted_summary_title

            sync_summary_file(mempool, template)

            self.send_json({
                "success": True,
                "filename": filename,
                "new_title": clean_title_text,
                "formatted_title": formatted_summary_title
            })
            return

        if path == "/api/settings":
            save_settings(data)
            self.send_json({"success": True, "settings": data})
            return

        if path == "/api/mdserve":
            global mdserve_process
            action = data.get("action", "toggle")
            running = is_mdserve_running()

            if action == "stop" or (action == "toggle" and running):
                kill_mdserve()
                self.send_json({"success": True, "is_serving": False})
            else:
                try:
                    # Kill any stale instance first
                    kill_mdserve()
                    mdserve_process = subprocess.Popen(
                        ["mdbook", "serve", "--hostname", "0.0.0.0", "-p", "3000"],
                        cwd=str(PROJECT_ROOT),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    self.send_json({"success": True, "is_serving": True, "url": "http://localhost:3000"})
                except Exception as e:
                    self.send_json({"success": False, "error": str(e)})
            return

        if path == "/api/audio/upload":
            fn = data.get("filename", "")
            clean_id = fn.replace(".md", "").lstrip("_")
            b64_data = data.get("audio_base64", "")
            ext = data.get("ext", "mp3").lstrip(".").lower()

            if not clean_id or not b64_data:
                self.send_error(400, "Missing filename or audio_base64")
                return

            try:
                raw_bytes = base64.b64decode(b64_data)
                target_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id
                target_dir.mkdir(parents=True, exist_ok=True)
                target_file = target_dir / f"audio.{ext}"

                with open(target_file, "wb") as f:
                    f.write(raw_bytes)

                self.send_json({
                    "success": True,
                    "clean_id": clean_id,
                    "audio_filename": f"audio.{ext}",
                    "audio_url": f"/src/ddma/docs/episodes/{clean_id}/audio.{ext}",
                    "size_bytes": len(raw_bytes)
                })
            except Exception as e:
                self.send_json({"success": False, "error": str(e)})
            return

        if path == "/api/audio/transcribe":
            fn = data.get("filename", "")
            clean_id = fn.replace(".md", "").lstrip("_")
            settings = load_settings()
            default_model = settings.get("whisper_model", "small.en")
            model_name = data.get("model", default_model)

            audio_path = get_episode_audio_path(clean_id)
            if not audio_path or not audio_path.exists():
                self.send_json({"success": False, "error": "No audio file found for this episode."})
                return

            def transcribe_worker(cid, apath, mname):
                transcription_jobs[cid] = {"status": "processing", "progress": f"Loading Whisper ({mname})..."}
                try:
                    import whisper
                    transcription_jobs[cid]["progress"] = f"Transcribing audio with {mname} (word_timestamps=True)..."
                    model = whisper.load_model(mname)
                    result = model.transcribe(str(apath), fp16=False, word_timestamps=True)
                    text = result.get("text", "").strip()

                    # 1. Save plain transcript.txt
                    t_path = get_episode_transcript_path(cid)
                    with open(t_path, "w", encoding="utf-8") as f:
                        f.write(text)

                    # 2. Save streamlined narrative.md
                    streamlined_text, _ = smart_streamline_narrative(text)
                    n_path = get_episode_narrative_path(cid)
                    with open(n_path, "w", encoding="utf-8") as nf:
                        nf.write(streamlined_text)

                    # 3. Save full acoustic transcription.json in src/ddma/docs/episodes/<cid>/
                    src_trans_json = SRC_DIR / "ddma" / "docs" / "episodes" / cid / "transcription.json"
                    src_trans_json.parent.mkdir(parents=True, exist_ok=True)
                    with open(src_trans_json, "w", encoding="utf-8") as jf:
                        json.dump(result, jf, indent=4)

                    # 4. Sync directly into DDMA projects folder if project exists
                    for ddma_root in [PROJECT_ROOT.parent / "ddma", PROJECT_ROOT / "ddma"]:
                        proj_dir = ddma_root / "projects" / f"episode_{cid}"
                        if proj_dir.exists():
                            with open(proj_dir / "transcription.json", "w", encoding="utf-8") as pjf:
                                json.dump(result, pjf, indent=4)
                            with open(proj_dir / "transcript.txt", "w", encoding="utf-8") as ptf:
                                ptf.write(text)

                    transcription_jobs[cid] = {"status": "done", "progress": "Transcription complete with word timestamps!", "text": text}
                except Exception as e:
                    transcription_jobs[cid] = {"status": "error", "progress": "Transcription failed", "error": str(e)}

            threading.Thread(target=transcribe_worker, args=(clean_id, audio_path, model_name), daemon=True).start()
            self.send_json({"success": True, "message": f"Transcription started with Whisper ({model_name}) with word-level timestamps."})
            return

        if path == "/api/transcript/streamline":
            fn = data.get("filename", "")
            clean_id = fn.replace(".md", "").lstrip("_")
            custom_text = data.get("text", "")

            if not custom_text:
                t_path = get_episode_transcript_path(clean_id)
                if t_path.exists():
                    try:
                        with open(t_path, "r", encoding="utf-8") as f:
                            custom_text = f.read()
                    except Exception:
                        pass

            streamlined, promo_count = smart_streamline_narrative(custom_text)

            n_path = get_episode_narrative_path(clean_id)
            with open(n_path, "w", encoding="utf-8") as f:
                f.write(streamlined)

            t_path = get_episode_transcript_path(clean_id)
            with open(t_path, "w", encoding="utf-8") as f:
                f.write(streamlined)

            self.send_json({
                "success": True,
                "clean_id": clean_id,
                "streamlined": streamlined,
                "promo_count": promo_count
            })
            return

        if path == "/api/transcript/save":
            fn = data.get("filename", "")
            clean_id = fn.replace(".md", "").lstrip("_")
            transcript_text = data.get("transcript", "")

            t_path = get_episode_transcript_path(clean_id)
            with open(t_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)

            n_path = get_episode_narrative_path(clean_id)
            with open(n_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)

            self.send_json({"success": True, "clean_id": clean_id, "length": len(transcript_text)})
            return

        if path == "/api/transcript/open_external" or path == "/api/transcript/open_vim":
            fn = data.get("filename", "")
            clean_id = fn.replace(".md", "").lstrip("_")
            n_path = get_episode_narrative_path(clean_id)
            t_path = get_episode_transcript_path(clean_id)
            
            target_path = n_path if n_path.exists() else t_path
            if not target_path.exists():
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write("# NotebookLM Narrative\n\n")

            editor_opened = False
            for ed in ["nvim", "gvim", "vim", "code", "notepad"]:
                try:
                    if shutil.which(ed):
                        subprocess.Popen([ed, str(target_path)])
                        editor_opened = True
                        break
                except Exception:
                    pass

            if not editor_opened:
                if sys.platform == "win32":
                    os.startfile(str(target_path))
                    editor_opened = True

            self.send_json({"success": editor_opened, "path": str(target_path)})
            return

        if path == "/api/ddma/launch":
            global ddma_curator_process
            fn = data.get("filename", "")
            clean_id = fn.replace(".md", "").lstrip("_") if fn else ""
            
            if not clean_id:
                # Pick latest episode from parse_summary_structure
                _, template, _, next_num = parse_summary_structure()
                if template:
                    clean_id = str(template[0].get("number") or template[0]["filename"].replace(".md", "").lstrip("_"))
                else:
                    clean_id = str(next_num - 1)

            # Auto-seed project in DDMA (zero re-transcription, strict <= 165s clips)
            project_id = seed_ddma_project_if_missing(clean_id)
            curator_target_url = f"http://localhost:8000/curator.html?project={project_id}"

            ddma_dir = PROJECT_ROOT.parent / "ddma"
            if not ddma_dir.exists():
                ddma_dir = PROJECT_ROOT / "ddma"
            curator_script = ddma_dir / "scratch" / "run_curator.py"
            
            if not is_ddma_curator_running() and curator_script.exists():
                try:
                    ddma_curator_process = subprocess.Popen(
                        [sys.executable, str(curator_script)],
                        cwd=str(ddma_dir),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception as e:
                    self.send_json({"success": False, "error": str(e)})
                    return

            self.send_json({
                "success": True,
                "project_id": project_id,
                "curator_url": curator_target_url,
                "message": f"DDMA Project {project_id} ready and launched on {curator_target_url}"
            })
            return

        if path == "/api/git/push":
            ep_num = data.get("number", "update")
            try:
                subprocess.run(["git", "add", "src/", "book.toml", "ingest/settings.json"], cwd=str(PROJECT_ROOT), check=True)
                subprocess.run(["git", "commit", "-m", f"publish: episode {ep_num} via md² cockpit"], cwd=str(PROJECT_ROOT), check=True)
                subprocess.run(["git", "push"], cwd=str(PROJECT_ROOT), check=True)
                self.send_json({"success": True, "message": "Pushed to remote repository successfully!"})
            except subprocess.CalledProcessError as e:
                self.send_json({"success": False, "error": f"Git command failed: {e}"})
            return

        self.send_error(404, "Endpoint not found")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def run_server():
    settings = load_settings()
    port = settings.get("port", 8088)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), IngestRequestHandler) as httpd:
        print(f"\n==================================================")
        print(f"       md² Ingest Publishing Cockpit")
        print(f"==================================================")
        print(f"  URL: http://localhost:{port}")
        print(f"  Root: {PROJECT_ROOT}")
        print(f"==================================================\n")
        webbrowser.open(f"http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down md² Cockpit server.")

if __name__ == "__main__":
    run_server()
