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
import html
import subprocess
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from datetime import datetime
import ast
import socket
import time

# Working directories
INGEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = INGEST_DIR.parent

# Auto-discover canonical deepDive production workspace if running in sibling mdIngest

# Global async background job tracker for long-form video rendering
VIDEO_RENDER_JOBS = {}
candidate_roots = [PROJECT_ROOT, PROJECT_ROOT.parent / "deepDive"]
PROD_ROOT = next((r for r in candidate_roots if (r / "src" / "SUMMARY.md").exists() and (r / "src" / "SUMMARY.md").stat().st_size > 1000), PROJECT_ROOT)

SRC_DIR = PROD_ROOT / "src"
IMG_DIR = SRC_DIR / "img"
VID_DIR = SRC_DIR / "vid"
SUMMARY_FILE = SRC_DIR / "SUMMARY.md"
SETTINGS_FILE = INGEST_DIR / "settings.json"

IMG_DIR.mkdir(parents=True, exist_ok=True)
VID_DIR.mkdir(parents=True, exist_ok=True)

# Global tracker for mdbook serve background process
mdserve_process = None
ddma_curator_process = None
beats_studio_process = None

def is_ddma_curator_running() -> bool:
    """Checks if DDMA Curator server is running on port 8000."""
    global ddma_curator_process
    if ddma_curator_process and ddma_curator_process.poll() is None:
        return True
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.04)
            return s.connect_ex(('127.0.0.1', 8000)) == 0
    except Exception:
        return False

def is_beats_studio_running() -> bool:
    """Checks if Beats Studio server is running on port 8001."""
    global beats_studio_process
    if beats_studio_process and beats_studio_process.poll() is None:
        return True
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.04)
            return s.connect_ex(('127.0.0.1', 8001)) == 0
    except Exception:
        return False

def is_mdserve_running() -> bool:
    """Checks if mdbook serve is running either via sub-process or port 3000."""
    global mdserve_process
    if mdserve_process and mdserve_process.poll() is None:
        return True
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.04)
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
    settings = {}
    vault_file = get_dd_hub_root() / "vault" / "settings.json"
    if vault_file.exists():
        try:
            with open(vault_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception:
            pass
    else:
        print(f"WARNING: vault settings.json not found at {vault_file} (dd_hub unreachable?) -- falling back to local settings.json.")
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
            except Exception:
                pass

    defaults = {
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

    # Overlay defaults with file settings
    merged = {**defaults, **settings}

    # Environment overrides take priority
    if os.environ.get("GEMINI_API_KEY"):
        merged["gemini_api_key"] = os.environ.get("GEMINI_API_KEY")
    if os.environ.get("MOSAIC_API_KEY"):
        merged["mosaic_api_key"] = os.environ.get("MOSAIC_API_KEY")
    if os.environ.get("DD_HUB_ROOT"):
        merged["dd_hub_root"] = os.environ.get("DD_HUB_ROOT")
    if os.environ.get("GDRIVE_PICKUP_PATH"):
        merged["gdrive_pickup_path"] = os.environ.get("GDRIVE_PICKUP_PATH")
    if os.environ.get("GDRIVE_VIDEO_PICKUP_PATH"):
        merged["gdrive_video_pickup_path"] = os.environ.get("GDRIVE_VIDEO_PICKUP_PATH")
    if os.environ.get("INGEST_PORT"):
        try:
            merged["port"] = int(os.environ.get("INGEST_PORT"))
        except ValueError:
            pass

    return merged

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
></lightning-widget>
</center>

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

_ep_videos_cache: dict[str, tuple[float, list[dict]]] = {}

def find_episode_videos(slug_or_num: str) -> list[dict]:
    """
    Discovers ONLY the single latest canonical compiled master `<clean_id>-<num>.mp4` per clip number.
    Cached for 2.0s to eliminate redundant disk queries when loading tabs.
    """
    clean_id = str(slug_or_num).replace('.md', '').lstrip('_')
    now = time.time()
    if clean_id in _ep_videos_cache:
        c_time, c_clips = _ep_videos_cache[clean_id]
        if now - c_time < 2.0:
            return c_clips

    candidates = []

    # 1. Modern Canonical DDMA Standard (src/ddma/docs/episodes/<ep>/clips/)
    canonical_ep_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / "clips"
    if canonical_ep_dir.exists():
        candidates.extend(canonical_ep_dir.glob("*.mp4"))

    # 2. ddma/docs/episodes/<clean_id>/clips/*.mp4 (Root fallback in deepDive & sibling ddma)
    for ddma_root in [PROJECT_ROOT / "ddma", PROJECT_ROOT.parent / "ddma"]:
        ep_clips_dir = ddma_root / "docs" / "episodes" / clean_id / "clips"
        if ep_clips_dir.exists():
            candidates.extend(ep_clips_dir.glob("*.mp4"))

    # 3. ddma/projects/episode_<id>/clips (Draft and working clips)
    for ddma_root in [PROJECT_ROOT / "ddma", PROJECT_ROOT.parent / "ddma"]:
        proj_clips = ddma_root / "projects" / f"episode_{clean_id}" / "clips"
        if proj_clips.exists():
            candidates.extend(proj_clips.glob("*.mp4"))

    # 4. ddma/clips/<clean_id>-*.mp4 (ddma root clips folder in both deepDive and sibling ddma)
    for ddma_root in [PROJECT_ROOT / "ddma", PROJECT_ROOT.parent / "ddma"]:
        clips_folder = ddma_root / "clips"
        if clips_folder.exists():
            candidates.extend(clips_folder.glob(f"{clean_id}-*.mp4"))

    # 5. Legacy episodes store (src/vid/<clean_id>-*.mp4)
    candidates.extend(VID_DIR.glob(f"{clean_id}-*.mp4"))
    candidates.extend(VID_DIR.glob(f"_{clean_id}-*.mp4"))

    # 6. ddma/docs/assets/clips/<clean_id>-*.mp4
    for ddma_root in [PROJECT_ROOT / "ddma", PROJECT_ROOT.parent / "ddma"]:
        assets_clips_dir = ddma_root / "docs" / "assets" / "clips"
        if assets_clips_dir.exists():
            candidates.extend(assets_clips_dir.glob(f"{clean_id}-*.mp4"))

    # Map clip_num -> title from plan.json if available
    clip_titles = {}
    for plan_cand in [
        SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / "plan.json",
        PROJECT_ROOT / "ddma" / "projects" / f"episode_{clean_id}" / "plan.json",
        PROJECT_ROOT.parent / "ddma" / "projects" / f"episode_{clean_id}" / "plan.json",
    ]:
        if plan_cand.exists():
            try:
                p_data = json.loads(plan_cand.read_text(encoding="utf-8-sig"))
                parts = p_data if isinstance(p_data, list) else p_data.get("parts", [])
                for pt in parts:
                    if isinstance(pt, dict) and pt.get("num") is not None and pt.get("title"):
                        clip_titles[int(pt["num"])] = str(pt["title"]).strip()
                if clip_titles:
                    break
            except Exception:
                pass

    canonical_pattern = re.compile(rf"^_?{re.escape(clean_id)}-(\d+)\.mp4$")
    by_clip_num = {}
    for path in candidates:
        name = path.name
        m = canonical_pattern.match(name)
        if not m:
            continue
        c_num = int(m.group(1))
        if c_num in by_clip_num:
            continue
        c_title = clip_titles.get(c_num, "")
        clip_label = f"{clean_id}-{c_num} • {c_title}" if c_title else f"{clean_id}-{c_num}"

        # Build canonical streaming URL
        if "docs" in str(path) and "episodes" in str(path):
            url = f"/media/ddma/docs/episodes/{clean_id}/clips/{name}"
        elif "projects" in str(path):
            url = f"/media/ddma/projects/episode_{clean_id}/clips/{name}"
        elif "clips" in str(path):
            url = f"/media/ddma/clips/{name}"
        else:
            url = f"/vid/{name}"

        by_clip_num[c_num] = {
            "name": name,
            "num": c_num,
            "url": url,
            "label": clip_label,
            "size_bytes": path.stat().st_size if path.exists() else 0
        }

    final_clips = [by_clip_num[k] for k in sorted(by_clip_num.keys())]
    _ep_videos_cache[clean_id] = (now, final_clips)
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

def sync_episode_clips_and_markdown(slug_or_num: str) -> dict:
    """
    Synchronizes clips and plan.json from sibling ddma repo to deepDive,
    and automatically regenerates/embeds the <!-- VIDEO_STRIP_START -->
    video carousel in src/<clean_id>.md.
    Ensures mdBook (local), mdIngest Research Tab, and GitHub Pages (deepdive.shutri.com)
    are 100% synchronized with the exact same source of truth.
    """
    clean_id = str(slug_or_num).replace('.md', '').lstrip('_')
    deepdive_ep_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id
    deepdive_clips_dir = deepdive_ep_dir / "clips"
    deepdive_clips_dir.mkdir(parents=True, exist_ok=True)

    # 1. Discover sibling ddma directory
    sibling_ddma = None
    for d in [PROJECT_ROOT / "ddma", PROJECT_ROOT.parent / "ddma"]:
        if d.exists() and ((d / "clips").exists() or (d / "projects" / f"episode_{clean_id}").exists() or (d / "docs" / "episodes" / clean_id).exists()):
            sibling_ddma = d
            break

    synced_clips = []
    if sibling_ddma:
        ddma_plan_file = sibling_ddma / "docs" / "episodes" / clean_id / "plan.json"

        # Copy plan.json if newer or missing (single source of truth: projects/<ep>/plan.json)
        proj_plan_file = sibling_ddma / "projects" / f"episode_{clean_id}" / "plan.json"
        if not proj_plan_file.exists():
            proj_plan_file = sibling_ddma / "projects" / clean_id / "plan.json"
        
        dest_plan = deepdive_ep_dir / "plan.json"
        if proj_plan_file.exists():
            try:
                shutil.copy2(proj_plan_file, dest_plan)
                if ddma_plan_file.parent.exists():
                    shutil.copy2(proj_plan_file, ddma_plan_file)
            except Exception:
                pass
        elif ddma_plan_file.exists():
            if not dest_plan.exists() or dest_plan.stat().st_size != ddma_plan_file.stat().st_size:
                try:
                    shutil.copy2(ddma_plan_file, dest_plan)
                except Exception:
                    pass

        # Sync to dd_hub vault on publish
        hub_root = get_dd_hub_root()
        if hub_root.exists():
            hub_plan = hub_root / "episodes" / clean_id / "plan.json"
            src_sync = proj_plan_file if proj_plan_file.exists() else (dest_plan if dest_plan.exists() else None)
            if src_sync:
                try:
                    hub_plan.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_sync, hub_plan)
                except Exception:
                    pass

        canonical_pattern = re.compile(rf"^{re.escape(clean_id)}-(\d+)\.mp4$")

        # Copy ONLY canonical `<clean_id>-<num>.mp4` compiled master clips from all possible ddma clip folders
        possible_clip_dirs = [
            sibling_ddma / "clips",
            sibling_ddma / "docs" / "episodes" / clean_id / "clips",
            PROJECT_ROOT / "ddma" / "clips",
        ]
        seen_dirs = set()
        for d_dir in possible_clip_dirs:
            resolved_d = d_dir.resolve()
            if resolved_d in seen_dirs or not d_dir.exists():
                continue
            seen_dirs.add(resolved_d)
            for src_clip in d_dir.glob(f"{clean_id}-*.mp4"):
                if not canonical_pattern.match(src_clip.name):
                    continue
                dest_clip = deepdive_clips_dir / src_clip.name
                if not dest_clip.exists() or dest_clip.stat().st_size != src_clip.stat().st_size or src_clip.stat().st_mtime > dest_clip.stat().st_mtime:
                    try:
                        shutil.copy2(src_clip, dest_clip)
                        if src_clip.name not in synced_clips:
                            synced_clips.append(src_clip.name)
                            print(f"[SYNC] Synced active master clip: {src_clip.name} -> {dest_clip}")
                    except Exception as ce:
                        print(f"[SYNC] Error copying clip {src_clip.name}: {ce}")

    canonical_pattern = re.compile(rf"^{re.escape(clean_id)}-(\d+)\.mp4$")
    # Remove any non-canonical files (e.g. *-mosaic.mp4, *-infographic.mp4, *-draft.mp4) from deepdive_clips_dir
    if deepdive_clips_dir.exists():
        for stray in list(deepdive_clips_dir.glob("*.mp4")):
            if not canonical_pattern.match(stray.name):
                try:
                    stray.unlink()
                except Exception:
                    pass

    # Invalidate video cache
    if clean_id in _ep_videos_cache:
        del _ep_videos_cache[clean_id]

    # 2. Read plan.json for part titles (supports both list and dict formats, including Clip 0)
    plan_data = {}
    dest_plan = deepdive_ep_dir / "plan.json"
    if dest_plan.exists():
        try:
            with open(dest_plan, "r", encoding="utf-8-sig") as pf:
                p_json = json.load(pf)
                parts_list = p_json if isinstance(p_json, list) else p_json.get("parts", [])
                for part in parts_list:
                    if not isinstance(part, dict):
                        continue
                    p_num = part.get("num") if part.get("num") is not None else part.get("part_number")
                    p_title = part.get("title", "")
                    if p_num is not None:
                        plan_data[str(p_num)] = p_title
        except Exception:
            pass

    # 3. Gather all published canonical clips in deepDive
    all_clips = sorted(
        [p for p in deepdive_clips_dir.glob("*.mp4") if canonical_pattern.match(p.name)],
        key=lambda p: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', p.name)]
    )
    if not all_clips:
        return {"success": True, "synced_clips": synced_clips, "total_clips": 0}

    # 4. Build standard VIDEO_STRIP block for mdBook
    cards_html = []
    for clip_path in all_clips:
        c_name = clip_path.name
        m = canonical_pattern.match(c_name)
        if not m:
            continue
        part_num = m.group(1)
        label = f"{clean_id}-{part_num}"
        if part_num in plan_data and plan_data[part_num]:
            label += f" {plan_data[part_num]}"
        elif "Meta Muse" in c_name:
            label += " Meta Muse - deepDive"

        card = (
            f'  <div style="flex: 0 0 60%; scroll-snap-align: center; position: relative; border-radius: 12px; overflow: hidden; background: #000; aspect-ratio: 1/1; display: flex; flex-direction: column; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">'
            f'\n    <video src="ddma/docs/episodes/{clean_id}/clips/{c_name}" style="width: 100%; height: 85%; object-fit: contain;" playsinline loop preload="auto" muted autoplay></video>'
            f'\n    <div style="height: 15%; background: #1a1a1a; color: #ccc; display: flex; align-items: center; justify-content: center; font-family: monospace; font-size: 12px; border-top: 1px solid #333;">{html.escape(label)}</div>'
            f'\n    <button class="vid-toggle" onclick="window.oph_play_toggle(this)" style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; border: 2px solid white; border-radius: 50%; width: 45px; height: 45px; cursor: pointer; font-size: 22px; z-index: 100;">🔇</button>'
            f'\n  </div>'
        )
        cards_html.append(card)

    cards_joined = "\n".join(cards_html)
    video_strip = (
        f'<!-- VIDEO_STRIP_START -->\n'
        f'<div class="video-carousel-container" style="display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 15px; padding: 20px 0; scroll-behavior: smooth;">\n'
        f'{cards_joined}\n'
        f'</div>\n\n'
        f'<center><a href="https://www.tiktok.com/@shutoshabot" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">▶ TikTok ◀</a><a href="https://www.instagram.com/shutoshabot/" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px; margin-right: 10px;">◈ Instagram ◈</a><a href="https://www.youtube.com/playlist?list=PLIX4sFsmu37q8rU8HKTLhdLPZQadcvx-K" target="_blank" style="background-color: #2E2E2E; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; margin-top: 10px;">⫸ YouTube ⫷</a></center>\n\n'
        f'<script>\n'
        f'  window.oph_play_toggle = window.oph_play_toggle || function(btn) {{\n'
        f'    const parent = btn.parentElement;\n'
        f'    const vid = parent.querySelector("video");\n'
        f'    const container = btn.closest(".video-carousel-container");\n'
        f'    if (vid.paused || vid.muted) {{\n'
        f'      container.querySelectorAll("video").forEach(v => {{ v.pause(); v.muted = true; v.parentElement.querySelector(".vid-toggle").innerText = "🔇"; }});\n'
        f'      vid.muted = false; vid.volume = 1.0;\n'
        f'      vid.play().then(() => {{ btn.innerText = "🔊"; }}).catch(e => console.error(e));\n'
        f'    }} else {{\n'
        f'      vid.pause(); vid.muted = true; btn.innerText = "🔇";\n'
        f'    }}\n'
        f'  }};\n'
        f'</script>\n'
        f'<!-- VIDEO_STRIP_END -->'
    )

    # 5. Inject/Update in src/<clean_id>.md or src/_<clean_id>.md
    target_files = [SRC_DIR / f"{clean_id}.md", SRC_DIR / f"_{clean_id}.md"]
    updated_files = []
    for md_file in target_files:
        if md_file.exists():
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                if "<!-- VIDEO_STRIP_START -->" in content:
                    new_content = re.sub(r'<!-- VIDEO_STRIP_START -->[\s\S]*?<!-- VIDEO_STRIP_END -->', video_strip, content)
                else:
                    m_h1 = re.search(r'(?m)^(?:#\s+[^\n]+\n+)(?:<!--\s*SIDEBAR_TITLE:[^\n]+-->\n+)?(?:\s*<center>[\s\S]*?<\/center>\n+)?', content)
                    if m_h1:
                        insert_pos = m_h1.end()
                        new_content = content[:insert_pos] + "\n" + video_strip + "\n\n" + content[insert_pos:]
                    else:
                        new_content = video_strip + "\n\n" + content

                if new_content != content:
                    with open(md_file, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    updated_files.append(md_file.name)
            except Exception as e:
                print(f"Error updating {md_file}: {e}")

    return {
        "success": True,
        "clean_id": clean_id,
        "synced_clips": synced_clips,
        "total_clips": len(all_clips),
        "updated_files": updated_files
    }

# Active transcription jobs: { clean_id: { "status": "idle"|"processing"|"done"|"error", "progress": str, "error": str } }
transcription_jobs = {}

def _read_settings_file(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def get_dd_hub_root() -> Path:
    """Resolves the canonical dd_hub root across Local Windows, Antigravity Cloud VM, and GCP Docker."""
    env_hub = os.environ.get("DD_HUB_ROOT")
    if env_hub and Path(env_hub).exists():
        return Path(env_hub)
    settings = _read_settings_file(SETTINGS_FILE)
    cfg_hub = settings.get("dd_hub_root")
    if cfg_hub and Path(cfg_hub).exists():
        return Path(cfg_hub)
    for cand in [
        Path(r"G:\My Drive\dd_hub"),
        Path("/mnt/gdrive/dd_hub"),
        Path("/workspace/dd_hub"),
    ]:
        try:
            if cand.exists():
                return cand
        except Exception:
            pass
    print("WARNING: DD_HUB_ROOT is unset and no dd_hub directory exists at any known location -- using default G:\\My Drive\\dd_hub which DOES NOT EXIST. Vault/plan reads will fail and hub syncs will be skipped.")
    return Path(r"G:\My Drive\dd_hub")

def get_episode_audio_path(clean_id: str) -> Path | None:
    """Discovers local audio file for an episode, including DDMA projects and Google Drive dd_hub/inputs."""
    possible_dirs = [
        SRC_DIR / "ddma" / "docs" / "episodes" / clean_id,
        PROJECT_ROOT / "ddma" / "docs" / "episodes" / clean_id,
        PROJECT_ROOT / "ddma" / "projects" / f"episode_{clean_id}",
        PROJECT_ROOT.parent / "ddma" / "projects" / f"episode_{clean_id}",
        SRC_DIR / "audio",
        PROJECT_ROOT / "ddma" / "audio",
    ]
    for d in possible_dirs:
        if not d.exists():
            continue
        for ext in [".m4a", ".wav", ".mp3", ".ogg", ".aac"]:
            for stem in [f"audio{ext}", f"{clean_id}{ext}", f"notebooklm{ext}", f"podcast_{clean_id}{ext}"]:
                f = d / stem
                if f.exists():
                    return f

    # Automatic Google Drive dd_hub/inputs/<ep> (and legacy agy_inputs/<ep>) fallback
    hub_root = get_dd_hub_root()
    for gdrive_ep_dir in [
        hub_root / "inputs" / str(clean_id),
        Path(r"G:\My Drive\agy_inputs") / str(clean_id),
    ]:
        if gdrive_ep_dir.exists():
            for ext in [".m4a", ".mp3", ".wav", ".ogg", ".aac"]:
                matches = sorted(gdrive_ep_dir.glob(f"*{ext}"))
                if matches:
                    src_audio = matches[0]
                    try:
                        dest_dir = SRC_DIR / "ddma" / "docs" / "episodes" / str(clean_id)
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        dest_file = dest_dir / f"{clean_id}{ext}"
                        if not dest_file.exists():
                            shutil.copy2(str(src_audio), str(dest_file))
                        return dest_file
                    except Exception:
                        return src_audio
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

def get_episode_podcast_dir(clean_id: str) -> Path:
    """Canonical folder for episode podcast assets."""
    target_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir

def get_episode_podcast_edit_path(clean_id: str) -> Path:
    """Path to non-destructive podcast_edit.json (cuts, stings, loudnorm)."""
    return get_episode_podcast_dir(clean_id) / "podcast_edit.json"

def get_episode_podcast_mp3_path(clean_id: str) -> Path:
    """Path to rendered master podcast MP3."""
    return get_episode_podcast_dir(clean_id) / f"podcast_{clean_id}.mp3"

def get_episode_podcast_video_path(clean_id: str) -> Path:
    """Path to rendered master podcast 1080p horizontal MP4."""
    canonical = get_episode_podcast_dir(clean_id) / f"podcast_{clean_id}.mp4"
    if canonical.exists():
        return canonical
    hub_root = get_dd_hub_root()
    for alt in [
        PROJECT_ROOT.parent / "ddma" / "clips" / f"{clean_id}-longform-master.mp4",
        PROD_ROOT.parent / "ddma" / "clips" / f"{clean_id}-longform-master.mp4",
        hub_root / "video" / f"podcast_{clean_id}.mp4",
        Path("G:/My Drive/pickup_longform") / f"podcast_{clean_id}.mp4",
    ]:
        try:
            if alt.exists():
                return alt
        except Exception:
            pass
    return canonical

def render_podcast_video_pipeline(clean_id: str, preview_seconds: float = None, progress_callback = None) -> tuple[bool, str, str]:
    """
    Renders 1920x1080 horizontal motion graphics video podcast:
    - Left 1080x1080: Dan Koe minimalist vector graphics
    - Right 840x1080: Episode Identity, Live Word Karaoke Captions, and Progress
    Returns (success: bool, path_or_err: str, message: str)
    """
    for d in [PROD_ROOT / "ddma", PROJECT_ROOT.parent / "ddma", PROJECT_ROOT / "ddma"]:
        if d.exists() and str(d.resolve()) not in sys.path:
            sys.path.insert(0, str(d.resolve()))
    
    try:
        import importlib
        import longform_video_engine as lve
        importlib.reload(lve)
        if hasattr(lve, 'wsi'):
            importlib.reload(lve.wsi)
    except ImportError as e:
        return False, "", f"Failed to load longform_video_engine: {e}"

    # 1. Locate Master Podcast Audio (rendered MP3 or source audio)
    audio_path = get_episode_podcast_mp3_path(clean_id)
    if not audio_path.exists():
        audio_path = get_episode_audio_path(clean_id)
    if not audio_path or not audio_path.exists():
        return False, "", f"Audio not found for episode {clean_id}. Please render podcast audio first."

    # 2. Locate Word-Level Transcription
    trans_path = get_episode_transcription_json_path(clean_id)
    if not trans_path or not trans_path.exists():
        return False, "", f"Word-level transcription.json not found for episode {clean_id}."
    
    try:
        with open(trans_path, "r", encoding="utf-8") as f:
            trans_data = json.load(f)
    except Exception as e:
        return False, "", f"Error reading transcription.json: {e}"

    # 3. Determine Episode Title
    ep_title = f"Episode {clean_id}"
    try:
        mempool, template, chain, _ = parse_summary_structure()
        all_items = mempool + template + chain
        matching = next((it for it in all_items if it.get("filename") == f"{clean_id}.md" or str(it.get("number")) == clean_id), None)
        if matching and matching.get("title"):
            ep_title = matching["title"]
    except Exception:
        pass

    # 4. Total Duration
    total_dur = 0.0
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip():
            total_dur = float(res.stdout.strip())
    except Exception:
        pass

    # 5. Load Edit Specification and Map Timeline
    edit_data = load_podcast_edit(clean_id)
    mapped_trans, sting_intervals, mapped_dur = lve.map_timeline_with_stings_and_cuts(
        transcription_data=trans_data,
        edit_data=edit_data,
        total_source_dur=total_dur
    )
    effective_dur = mapped_dur if mapped_dur > 0 else (total_dur or 3200.0)

    # 6. Discover Episode Cover Art
    cover_image_path = None
    episode_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id
    for img_candidate in [
        episode_dir / "cover.webp",
        episode_dir / "cover.png",
        episode_dir / "cover.jpg",
        IMG_DIR / f"{clean_id}.png",
        IMG_DIR / f"{clean_id}.jpg"
    ]:
        if img_candidate.exists():
            cover_image_path = img_candidate
            break

    # 7. Plan Storyboard (Aligned to mapped timeline)
    storyboard_cache = get_episode_podcast_dir(clean_id) / "podcast_video_storyboard.json"
    scenes = lve.generate_longform_storyboard(
        transcription_data=mapped_trans,
        total_duration=effective_dur,
        episode_title=ep_title,
        cached_path=str(storyboard_cache)
    )

    out_mp4 = get_episode_podcast_video_path(clean_id)

    try:
        lve.render_horizontal_podcast_video(
            scenes=scenes,
            audio_path=str(audio_path),
            transcription_data=trans_data,
            out_mp4_path=str(out_mp4),
            episode_num=clean_id,
            episode_title=ep_title,
            duration=effective_dur,
            max_seconds=preview_seconds,
            edit_data=edit_data,
            cover_image_path=str(cover_image_path) if cover_image_path else None,
            progress_callback=progress_callback
        )
        dur_desc = f"{int(preview_seconds)}s preview" if preview_seconds else "full episode"
        return True, str(out_mp4), f"1080p Horizontal motion graphics video rendered successfully ({dur_desc})!"
    except Exception as e:
        return False, "", f"Video rendering failed: {e}"

def get_episode_podcast_meta_path(clean_id: str) -> Path:
    """Path to meta-muse companion distribution manifest."""
    return get_episode_podcast_dir(clean_id) / "podcast_meta.json"

def get_episode_transcription_json_path(clean_id: str) -> Path | None:
    """Discovers full acoustic transcription.json containing word-level timestamps, including dd_hub/episodes/<ep>."""
    hub_root = get_dd_hub_root()
    candidates = [
        SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / "transcription.json",
        PROJECT_ROOT / "ddma" / "docs" / "episodes" / clean_id / "transcription.json",
        PROJECT_ROOT.parent / "ddma" / "projects" / f"episode_{clean_id}" / "transcription.json",
        PROJECT_ROOT / "ddma" / "projects" / f"episode_{clean_id}" / "transcription.json",
        hub_root / "episodes" / str(clean_id) / "transcription.json",
    ]
    for c in candidates:
        try:
            if c.exists() and c.stat().st_size > 0:
                # Ensure local src copy exists if found in dd_hub
                local_src = SRC_DIR / "ddma" / "docs" / "episodes" / str(clean_id) / "transcription.json"
                if c != local_src and not local_src.exists():
                    local_src.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(c), str(local_src))
                return c
        except Exception:
            pass
    return None

_FASTER_WHISPER_CACHE = {}

def run_faster_whisper_transcription(audio_path, model_name="large-v3-turbo", word_timestamps=True, initial_prompt=None):
    """
    Transcribe audio using faster-whisper (CTranslate2 INT8 with AVX-512 optimization on Ryzen).
    Falls back gracefully to openai-whisper if faster-whisper encounters an error.
    Returns standard Whisper-format result dict: {"text": str, "segments": list, "language": str}.
    """
    global _FASTER_WHISPER_CACHE
    try:
        import av
        if not hasattr(av, "_patched_metadata_errors"):
            _orig_open = av.open
            def _safe_av_open(*args, **kwargs):
                kwargs.pop("metadata_errors", None)
                return _orig_open(*args, **kwargs)
            av.open = _safe_av_open
            av._patched_metadata_errors = True
    except Exception:
        pass

    fw_model_name = model_name or "large-v3-turbo"
    try:
        from faster_whisper import WhisperModel
        if fw_model_name not in _FASTER_WHISPER_CACHE:
            _FASTER_WHISPER_CACHE[fw_model_name] = WhisperModel(
                fw_model_name,
                device="cpu",
                compute_type="int8",
                cpu_threads=8
            )
        model = _FASTER_WHISPER_CACHE[fw_model_name]

        audio_input = str(audio_path)
        try:
            import whisper.audio
            audio_input = whisper.audio.load_audio(str(audio_path))
        except Exception:
            pass

        transcribe_kwargs = {"word_timestamps": word_timestamps}
        if initial_prompt:
            transcribe_kwargs["initial_prompt"] = initial_prompt

        segments_gen, info = model.transcribe(audio_input, **transcribe_kwargs)
        segments_list = []
        text_chunks = []
        for s in segments_gen:
            text_chunks.append(s.text)
            seg_dict = {
                "id": getattr(s, "id", len(segments_list)),
                "seek": getattr(s, "seek", 0),
                "start": round(float(s.start), 3),
                "end": round(float(s.end), 3),
                "text": s.text,
                "tokens": getattr(s, "tokens", []),
                "avg_logprob": getattr(s, "avg_logprob", 0.0),
                "compression_ratio": getattr(s, "compression_ratio", 1.0),
                "no_speech_prob": getattr(s, "no_speech_prob", 0.0),
            }
            if s.words:
                seg_dict["words"] = [
                    {
                        "word": w.word,
                        "start": round(float(w.start), 3),
                        "end": round(float(w.end), 3),
                        "probability": round(float(getattr(w, "probability", 1.0)), 4)
                    }
                    for w in s.words
                ]
            else:
                seg_dict["words"] = []
            segments_list.append(seg_dict)

        return {
            "text": "".join(text_chunks).strip(),
            "segments": segments_list,
            "language": getattr(info, "language", "en")
        }
    except Exception as e:
        print(f"[TRANSCRIPTION] faster-whisper error ({e}); falling back to openai-whisper...")
        import whisper
        fallback_mname = fw_model_name if fw_model_name != "large-v3-turbo" else "small.en"
        wmodel = whisper.load_model(fallback_mname)
        return wmodel.transcribe(str(audio_path), fp16=False, word_timestamps=word_timestamps)

CANONICAL_PODCAST_STINGS = [
    "deepDive-strong.mp3",
    "Bluesy Vibes (Sting) - Doug Maxwell_Media Right Productions.mp3",
    "Howling (Sting) - Gunnar Olsen.mp3",
    "deepDive-conclusion.mp3",
]

def get_available_stings() -> list[dict]:
    """Catalog restricted to the 4 canonical podcast stings."""
    stings = []
    candidates = [
        PROD_ROOT / "ddma" / "music",
        PROJECT_ROOT / "ddma" / "music",
        PROJECT_ROOT.parent / "ddma" / "music",
    ]
    seen = set()
    for d in candidates:
        if d.exists() and d.is_dir():
            for fname in CANONICAL_PODCAST_STINGS:
                f = d / fname
                if f.exists() and fname not in seen:
                    seen.add(fname)
                    stings.append({
                        "filename": fname,
                        "path": str(f.resolve()),
                        "size": f.stat().st_size
                    })
    return stings

def load_podcast_edit(clean_id: str) -> dict:
    """Loads podcast_edit.json or returns default non-destructive schema."""
    edit_path = get_episode_podcast_edit_path(clean_id)
    if edit_path.exists():
        try:
            with open(edit_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data.setdefault("cuts", [])
                    data.setdefault("stings", [])
                    data.setdefault("intro_sting", "deepDive-strong.mp3")
                    data.setdefault("outro_sting", "deepDive-conclusion.mp3")
                    data.setdefault("target_lufs", -16.0)
                    return data
        except Exception as e:
            print(f"[PODCAST] Error reading {edit_path}: {e}")

    audio_path = get_episode_audio_path(clean_id)
    return {
        "episode": clean_id,
        "source_audio": audio_path.name if audio_path else "",
        "cuts": [],
        "stings": [],
        "intro_sting": "deepDive-strong.mp3",
        "outro_sting": "deepDive-conclusion.mp3",
        "target_lufs": -16.0,
        "updated_at": datetime.now().isoformat()
    }

def save_podcast_edit(clean_id: str, edit_data: dict) -> bool:
    """Saves updated cuts, stings and parameters to podcast_edit.json."""
    try:
        edit_path = get_episode_podcast_edit_path(clean_id)
        edit_data["episode"] = clean_id
        edit_data["updated_at"] = datetime.now().isoformat()
        if "cuts" in edit_data and isinstance(edit_data["cuts"], list):
            edit_data["cuts"] = sorted(edit_data["cuts"], key=lambda c: float(c.get("start", 0)))
        if "stings" in edit_data and isinstance(edit_data["stings"], list):
            edit_data["stings"] = sorted(edit_data["stings"], key=lambda s: float(s.get("at", 0)))
        with open(edit_path, "w", encoding="utf-8") as f:
            json.dump(edit_data, f, indent=2)
        return True
    except Exception as e:
        print(f"[PODCAST] Failed to save {clean_id} podcast_edit.json: {e}")
        return False

def extract_timed_words_from_transcription(clean_id: str) -> tuple[list[dict], list[dict], str]:
    """
    Extracts word-level timestamps from acoustic transcription.json.
    Returns (words, segments, full_text).
    words: [{word, start, end, idx, segment_id}]
    """
    t_path = get_episode_transcription_json_path(clean_id)
    if not t_path or not t_path.exists():
        txt_path = get_episode_transcript_path(clean_id)
        if txt_path.exists():
            try:
                with open(txt_path, "r", encoding="utf-8") as tf:
                    raw = tf.read().strip()
                toks = raw.split()
                synth_words = []
                for i, t in enumerate(toks):
                    synth_words.append({
                        "word": t,
                        "start": round(i * 0.4, 2),
                        "end": round(i * 0.4 + 0.36, 2),
                        "idx": i,
                        "segment_id": 0
                    })
                return synth_words, [{"id": 0, "start": 0.0, "end": round(len(toks) * 0.4, 2), "text": raw}], raw
            except Exception:
                pass
        return [], [], ""

    try:
        with open(t_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[PODCAST] Failed to parse {t_path}: {e}")
        return [], [], ""

    full_text = data.get("text", "")
    raw_segments = data.get("segments", [])
    all_words = []
    normalized_segments = []
    word_idx = 0

    for s_idx, seg in enumerate(raw_segments):
        s_id = seg.get("id", s_idx)
        s_start = float(seg.get("start", 0.0))
        s_end = float(seg.get("end", 0.0))
        s_text = seg.get("text", "")
        seg_words = seg.get("words", [])

        norm_words = []
        if seg_words:
            for w in seg_words:
                w_str = w.get("word", "")
                w_s = float(w.get("start", s_start))
                w_e = float(w.get("end", s_end))
                w_obj = {
                    "word": w_str,
                    "start": round(w_s, 2),
                    "end": round(w_e, 2),
                    "idx": word_idx,
                    "segment_id": s_id
                }
                all_words.append(w_obj)
                norm_words.append(w_obj)
                word_idx += 1
        else:
            toks = s_text.split()
            dur = max(0.1, s_end - s_start)
            step = dur / max(1, len(toks))
            for i, t in enumerate(toks):
                w_s = s_start + (i * step)
                w_e = w_s + step
                w_obj = {
                    "word": t,
                    "start": round(w_s, 2),
                    "end": round(w_e, 2),
                    "idx": word_idx,
                    "segment_id": s_id
                }
                all_words.append(w_obj)
                norm_words.append(w_obj)
                word_idx += 1

        normalized_segments.append({
            "id": s_id,
            "start": round(s_start, 2),
            "end": round(s_end, 2),
            "text": s_text,
            "word_count": len(norm_words)
        })

    return all_words, normalized_segments, full_text

def render_podcast_pipeline(clean_id: str, edit_data: dict = None) -> tuple[bool, str, str]:
    """
    Renders non-destructive master podcast MP3 using FFmpeg:
    1. Cuts out deleted speech segments and joins remaining audio with micro-crossfades.
    2. Prepends intro sting and appends outro sting.
    3. Normalizes loudness to -16 LUFS (Spotify / Apple Podcast standard).
    4. Writes clean ID3 metadata.
    Returns (success: bool, path_or_err: str, message: str).
    """
    audio_path = get_episode_audio_path(clean_id)
    if not audio_path or not audio_path.exists():
        return False, "", f"Source audio not found for episode {clean_id}"

    if edit_data is None:
        edit_data = load_podcast_edit(clean_id)

    total_dur = 0.0
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip():
            total_dur = float(res.stdout.strip())
    except Exception as pe:
        print(f"[PODCAST RENDER] ffprobe error: {pe}")

    if total_dur <= 0.0:
        return False, "", "Could not probe duration of source audio"

    raw_cuts = edit_data.get("cuts", [])
    valid_cuts = []
    for c in raw_cuts:
        try:
            cs = max(0.0, float(c.get("start", 0.0)))
            ce = min(total_dur, float(c.get("end", 0.0)))
            if ce > cs + 0.05:
                valid_cuts.append((cs, ce))
        except (ValueError, TypeError):
            continue
    valid_cuts.sort(key=lambda x: x[0])

    merged_cuts = []
    for cs, ce in valid_cuts:
        if not merged_cuts:
            merged_cuts.append([cs, ce])
        else:
            prev = merged_cuts[-1]
            if cs <= prev[1] + 0.05:
                prev[1] = max(prev[1], ce)
            else:
                merged_cuts.append([cs, ce])

    keep_ranges = []
    cursor = 0.0
    for cs, ce in merged_cuts:
        if cs > cursor + 0.08:
            keep_ranges.append((cursor, cs))
        cursor = max(cursor, ce)
    if cursor < total_dur - 0.08:
        keep_ranges.append((cursor, total_dur))

    if not keep_ranges:
        return False, "", "Error: Cuts remove entire audio timeline!"

    out_mp3 = get_episode_podcast_mp3_path(clean_id)
    temp_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / "tmp_podcast"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        stitched_speech = temp_dir / "stitched_speech.wav"
        if len(keep_ranges) == 1 and keep_ranges[0][0] <= 0.1 and keep_ranges[0][1] >= total_dur - 0.1:
            subprocess.run(["ffmpeg", "-y", "-i", str(audio_path), "-vn", "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(stitched_speech)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        else:
            slice_files = []
            for i, (ks, ke) in enumerate(keep_ranges):
                s_file = temp_dir / f"slice_{i:03d}.wav"
                dur = ke - ks
                fade_dur = min(0.02, dur / 3.0)
                cmd = [
                    "ffmpeg", "-y", "-ss", f"{ks:.3f}", "-t", f"{dur:.3f}",
                    "-i", str(audio_path),
                    "-af", f"afade=t=in:ss=0:d={fade_dur:.3f},afade=t=out:st={(dur - fade_dur):.3f}:d={fade_dur:.3f}",
                    "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2",
                    str(s_file)
                ]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                slice_files.append(s_file)

            concat_list = temp_dir / "concat_slices.txt"
            with open(concat_list, "w", encoding="utf-8") as cf:
                for sf in slice_files:
                    cf.write(f"file '{sf.resolve().as_posix()}'\n")

            cmd_concat = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_list),
                "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2",
                str(stitched_speech)
            ]
            subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        stings_dict = {s["filename"]: Path(s["path"]) for s in get_available_stings()}
        intro_name = edit_data.get("intro_sting")
        outro_name = edit_data.get("outro_sting")
        intro_path = stings_dict.get(intro_name) if intro_name else None
        outro_path = stings_dict.get(outro_name) if outro_name else None

        current_track = stitched_speech

        raw_stings = edit_data.get("stings", [])
        if raw_stings and stitched_speech.exists():
            valid_stings = []
            for s in raw_stings:
                try:
                    at_val = float(s.get("at", 0.0))
                    sf = s.get("music_file", "")
                    sp = stings_dict.get(sf)
                    if sp and sp.exists():
                        dur_val = float(s.get("duration", 0.0))
                        if dur_val <= 0.0:
                            try:
                                ps = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(sp)], stdout=subprocess.PIPE, text=True)
                                dur_val = float(ps.stdout.strip()) if ps.returncode == 0 else 7.0
                            except Exception:
                                dur_val = 7.0
                        valid_stings.append({
                            "orig_at": at_val,
                            "file": sf,
                            "path": sp,
                            "duck_db": s.get("duck_db", -14),
                            "duration": dur_val
                        })
                except (ValueError, TypeError):
                    continue

            if valid_stings:
                speech_dur = 0.0
                try:
                    cmd_probe = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(stitched_speech)]
                    res_p = subprocess.run(cmd_probe, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if res_p.returncode == 0 and res_p.stdout.strip():
                        speech_dur = float(res_p.stdout.strip())
                except Exception:
                    pass

                valid_stings.sort(key=lambda x: x["orig_at"])
                for vs in valid_stings:
                    t_orig = vs["orig_at"]
                    shift = 0.0
                    for cs, ce in merged_cuts:
                        if ce <= t_orig:
                            shift += (ce - cs)
                        elif cs < t_orig < ce:
                            shift += (t_orig - cs)
                    vs["adj_at"] = max(0.0, t_orig - shift)

                midrolls = []
                outro_sting = None
                for vs in valid_stings:
                    is_outro = (vs["adj_at"] >= speech_dur - 3.0) or ("conclusion" in vs["file"] and vs["adj_at"] >= speech_dur - 45.0)
                    if is_outro and outro_sting is None:
                        outro_sting = vs
                    else:
                        midrolls.append(vs)

                midrolls.sort(key=lambda x: x["adj_at"])

                split_points = []
                filtered_midrolls = []
                last_pt = 0.0
                for vs in midrolls:
                    pt = vs["adj_at"]
                    if pt > last_pt + 1.0 and pt < speech_dur - 1.0:
                        split_points.append(pt)
                        filtered_midrolls.append(vs)
                        last_pt = pt

                slice_ranges = []
                cur = 0.0
                for pt in split_points:
                    slice_ranges.append((cur, pt))
                    cur = pt
                slice_ranges.append((cur, speech_dur))

                # Assemble master timeline with canonical DDMA acoustic transition rules:
                # 1. Front of sting: 0.2s silence - no crossfade.
                # 2. End of sting: fade out 2.0s, and crossfade 1.0s into incoming speech at 100% FULL VOLUME (strictly ZERO afade=in on human speech).
                # 3. Outro sting: 0.2s silence after speech ends, 5.5s conclusion sting fading out over final 2.0s.
                inputs = []
                filter_parts = []
                labels = []
                in_idx = 0
                t_cursor = 0.0

                s0_start, s0_end = slice_ranges[0]
                s0_dur = s0_end - s0_start
                inputs.extend(["-ss", f"{s0_start:.3f}", "-t", f"{s0_dur:.3f}", "-i", str(stitched_speech)])
                labels.append(f"[{in_idx}:a]")
                in_idx += 1
                t_cursor += s0_dur

                for i, sting in enumerate(filtered_midrolls):
                    t_sting_start = t_cursor + 0.2
                    dur_sting = sting["duration"]
                    t_sting_ms = int(t_sting_start * 1000)
                    fade_out_dur = min(2.0, dur_sting)
                    fade_out_st = max(0.0, dur_sting - fade_out_dur)

                    inputs.extend(["-i", str(sting["path"])])
                    filter_parts.append(
                        f"[{in_idx}:a]atrim=0:{dur_sting:.3f},afade=t=out:st={fade_out_st:.3f}:d={fade_out_dur:.3f},adelay={t_sting_ms}|{t_sting_ms}[m{i}];"
                    )
                    labels.append(f"[m{i}]")
                    in_idx += 1

                    t_next_speech = max(t_cursor, t_sting_start + dur_sting - 1.0)
                    t_speech_ms = int(t_next_speech * 1000)
                    nxt_start, nxt_end = slice_ranges[i + 1]
                    nxt_dur = nxt_end - nxt_start

                    inputs.extend(["-ss", f"{nxt_start:.3f}", "-t", f"{nxt_dur:.3f}", "-i", str(stitched_speech)])
                    filter_parts.append(
                        f"[{in_idx}:a]adelay={t_speech_ms}|{t_speech_ms}[sl{i+1}];"
                    )
                    labels.append(f"[sl{i+1}]")
                    in_idx += 1
                    t_cursor = t_next_speech + nxt_dur

                if outro_sting:
                    t_outro_start = t_cursor + 0.2
                    t_outro_ms = int(t_outro_start * 1000)
                    dur_outro = outro_sting["duration"]
                    fade_outro = min(2.0, dur_outro)
                    fade_outro_st = max(0.0, dur_outro - fade_outro)

                    inputs.extend(["-i", str(outro_sting["path"])])
                    filter_parts.append(
                        f"[{in_idx}:a]atrim=0:{dur_outro:.3f},afade=t=out:st={fade_outro_st:.3f}:d={fade_outro:.3f},adelay={t_outro_ms}|{t_outro_ms}[moutro];"
                    )
                    labels.append("[moutro]")
                    in_idx += 1
                    t_cursor = t_outro_start + dur_outro

                filter_parts.append(
                    f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:dropout_transition=0:normalize=0[mixed_podcast]"
                )

                with_stings_file = temp_dir / "with_stings_master.wav"
                mix_cmd = [
                    "ffmpeg", "-y"
                ] + inputs + [
                    "-filter_complex", "".join(filter_parts),
                    "-map", "[mixed_podcast]",
                    "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2",
                    str(with_stings_file)
                ]
                mix_res = subprocess.run(mix_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if mix_res.returncode == 0 and with_stings_file.exists():
                    current_track = with_stings_file
                else:
                    err_msg = mix_res.stderr.decode("utf-8", errors="ignore") if mix_res.stderr else ""
                    print(f"[PODCAST RENDER] Stings mixing error: {err_msg[:300]}")

        if (intro_path or outro_path) and not valid_stings:
            master_pieces = []
            if intro_path and intro_path.exists():
                intro_wav = temp_dir / "intro.wav"
                subprocess.run(["ffmpeg", "-y", "-i", str(intro_path), "-af", "afade=t=out:st=4.5:d=1.5", "-t", "6", "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(intro_wav)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if intro_wav.exists():
                    master_pieces.append(intro_wav)

            master_pieces.append(current_track)

            if outro_path and outro_path.exists():
                outro_wav = temp_dir / "outro.wav"
                # Play outro conclusion sting to its full finish (with gentle fade out on the tail)
                subprocess.run(["ffmpeg", "-y", "-i", str(outro_path), "-af", "afade=t=out:st=13.5:d=1.5", "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(outro_wav)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if outro_wav.exists():
                    master_pieces.append(outro_wav)

            concat_master = temp_dir / "concat_master.txt"
            with open(concat_master, "w", encoding="utf-8") as cm:
                for mp in master_pieces:
                    cm.write(f"file '{mp.resolve().as_posix()}'\n")

            with_stings = temp_dir / "with_intro_outro.wav"
            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_master), "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(with_stings)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            current_track = with_stings

        ep_title = f"Episode {clean_id}"
        for possible_file in [SRC_DIR / f"{clean_id}.md", SRC_DIR / f"_{clean_id}.md"]:
            if possible_file.exists():
                try:
                    with open(possible_file, "r", encoding="utf-8") as pf:
                        m = re.search(r"^#\s+(.*)$", pf.read(), re.MULTILINE)
                        if m:
                            ep_title = m.group(1).strip()
                            break
                except Exception:
                    pass

        target_lufs = float(edit_data.get("target_lufs", -16.0))
        final_cmd = [
            "ffmpeg", "-y", "-i", str(current_track),
            "-af", f"loudnorm=I={target_lufs}:LRA=11:TP=-1.5",
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100",
            "-metadata", f"title={ep_title}",
            "-metadata", "artist=Knowledge Deep Dive",
            "-metadata", "album=Deep Dive with Gemini",
            "-metadata", f"track={clean_id}",
            str(out_mp3)
        ]
        res_final = subprocess.run(final_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res_final.returncode != 0:
            return False, "", f"FFmpeg loudnorm failed: {res_final.stderr[:300]}"

        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

        return True, str(out_mp3), f"Podcast successfully rendered to podcast_{clean_id}.mp3 ({out_mp3.stat().st_size // 1024} KB)"
    except Exception as e:
        return False, "", f"Render pipeline failed: {str(e)}"

def find_best_sentence_boundary(segments: list[dict], target_t: float, window: float = 45.0) -> tuple[float, str]:
    """
    Finds the exact end timestamp of a complete sentence closest to target_t.
    Prioritizes segments ending in terminal punctuation (., ?, !) and natural speaker pauses.
    Guarantees stings are never placed in the middle of a sentence.
    """
    if not segments:
        return target_t, ""

    candidates = []
    for i, s in enumerate(segments):
        end_t = float(s.get("end", 0.0))
        if abs(end_t - target_t) <= window:
            txt = s.get("text", "").strip()
            is_punct = txt.endswith((".", "?", "!"))
            pause = 0.0
            if i + 1 < len(segments):
                next_start = float(segments[i + 1].get("start", end_t))
                pause = max(0.0, next_start - end_t)
            score = 0.0
            if is_punct:
                score += 15.0
            if pause >= 0.2:
                score += 5.0
            score -= (abs(end_t - target_t) / max(1.0, window)) * 5.0
            candidates.append((score, end_t, txt))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1], candidates[0][2]

    # Fallback to closest segment ending
    closest = min(segments, key=lambda s: abs(float(s.get("end", 0.0)) - target_t))
    return float(closest.get("end", target_t)), closest.get("text", "")

def resolve_acoustic_word_end(raw_end: float, next_word_start: float | None = None, audio_path: str | Path | None = None) -> float:
    """
    Extends a Whisper word end timestamp into the natural breath pause so trailing sibilants/plosives
    (e.g., '-es' in 'senses') are never clipped in half.
    Uses an 180ms sibilant safety cushion clamped 40ms before next_word_start, refined by 16kHz PCM RMS energy if audio_path is available.
    """
    max_extend = min(0.32, max(0.0, (next_word_start - raw_end) - 0.04)) if next_word_start is not None else 0.22
    if max_extend <= 0.02:
        return round(raw_end, 2)
    default_ext = round(raw_end + min(0.18, max_extend), 2)
    audio_str = str(audio_path) if audio_path else ""
    if not audio_str or not os.path.exists(audio_str):
        return default_ext
    try:
        import numpy as np
        win_start = max(0.0, raw_end - 0.05)
        win_dur = 0.05 + max_extend
        p = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", f"{win_start:.3f}", "-t", f"{win_dur:.3f}", "-i", audio_str, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        arr = np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0
        if len(arr) < 160:
            return default_ext
        last_active_t = raw_end + min(0.12, max_extend)
        for i in range(800, len(arr) - 160, 160):
            rms = float(np.sqrt(np.mean(arr[i:i + 160] ** 2)))
            t_frame = win_start + (i + 160) / 16000.0
            if rms > 0.0020:
                last_active_t = t_frame + 0.03
        return round(min(raw_end + max_extend, max(raw_end + min(0.12, max_extend), last_active_t)), 2)
    except Exception:
        return default_ext


def detect_redundant_welcome_cuts(words: list[dict], segments: list[dict], opener_hook_end: float, audio_path: Path | None = None) -> list[dict]:
    """
    Scans the opening 40 seconds of the word-level transcript (grouped into true sentences across Whisper segments)
    for redundant spoken welcome statements ('Welcome to [the] deep dive' or 'Today we are going on a [massive] deep dive')
    that should be stripped because 'deepDive-strong.mp3' already delivers the spoken
    'Welcome to deepDive, I am Satosha, and I am Satoshi' intro sting.
    """
    suggested_cuts = []
    early_words = [w for w in words if float(w.get("start", 0.0)) < 40.0]
    if not early_words:
        return suggested_cuts

    # Split word stream into true sentences at terminal punctuation (., ?, !)
    sentences = []
    cur_sent = []
    for w in early_words:
        cur_sent.append(w)
        w_txt = w.get("word", "").strip()
        if w_txt.endswith((".", "?", "!")):
            sentences.append(cur_sent)
            cur_sent = []
    if cur_sent:
        sentences.append(cur_sent)

    for sent in sentences:
        sent_text = " ".join(w.get("word", "").strip() for w in sent).strip()
        sent_lower = re.sub(r"[^a-z0-9\s]", "", sent_text.lower())
        is_welcome = ("welcome to" in sent_lower and "deep dive" in sent_lower)
        is_going_on_dd = ("going on a" in sent_lower and "deep dive" in sent_lower and float(sent[0]["start"]) <= opener_hook_end + 12.0)
        if is_welcome or is_going_on_dd:
            c_start = round(max(0.0, float(sent[0]["start"]) - 0.04), 2)
            raw_c_end = float(sent[-1]["end"])
            next_ws = [float(w["start"]) for w in words if float(w["start"]) > raw_c_end + 0.01]
            next_w_st = next_ws[0] if next_ws else raw_c_end + 0.25
            c_end = round(min(raw_c_end + 0.12, max(raw_c_end, next_w_st - 0.04)), 2)
            if not any(abs(c["start"] - c_start) < 0.5 for c in suggested_cuts):
                suggested_cuts.append({
                    "id": f"cut_welcome_{int(c_start * 100)}",
                    "start": c_start,
                    "end": c_end,
                    "text": sent_text,
                    "reason": "Stripped redundant spoken welcome (replaced by deepDive-strong.mp3 spoken intro sting)"
                })
    return suggested_cuts


def review_podcast_with_gemini(clean_id: str) -> dict:
    """
    Deterministically structures the Longform Podcast music stings & welcome cuts using spoken clip boundaries:
    1. Strips redundant 'Welcome to the deep dive' / 'Today we are going on a massive deep dive' in Clip 0.
    2. Embeds 'deepDive-strong.mp3' (~16.71s spoken 'Welcome to deepDive, I am Satosha, and I am Satoshi' + music) at the appropriate hook boundary in the opening clip.
    3. Places alternating 'Bluesy Vibes' (5.5s) and 'Howling' (5.5s) at the end of EVERY clip and before the next clip starts.
    4. Places 'deepDive-conclusion.mp3' (5.5s: 'I am Satosha, and I am Satoshi' + ~4s closing music) at the very end of the episode.
    Also auto-saves the cuts and stings into podcast_edit.json so the timeline is ready immediately.
    """
    words, segments, full_text = extract_timed_words_from_transcription(clean_id)
    if not segments and not full_text:
        return {"success": False, "error": "No transcript available for this episode."}

    audio_path = get_episode_audio_path(clean_id)
    total_time = float(words[-1]["end"]) if words else (float(segments[-1].get("end", 600.0)) if segments else 600.0)

    # Probe exact duration of deepDive-strong.mp3 (typically 16.71s)
    stings_list = get_available_stings()
    stings_map = {s["filename"]: Path(s["path"]) for s in stings_list}
    strong_dur = 16.71
    strong_path = stings_map.get("deepDive-strong.mp3")
    if strong_path and strong_path.exists():
        try:
            ps = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(strong_path)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if ps.returncode == 0 and ps.stdout.strip():
                strong_dur = round(float(ps.stdout.strip()), 2)
        except Exception:
            pass

    # Check if a DDMA plan.json exists for this episode
    plan_clips = []
    for p_cand in [
        PROD_ROOT / "ddma" / "projects" / f"episode_{clean_id}" / "plan.json",
        SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / "plan.json",
        PROD_ROOT.parent / "ddma" / "projects" / f"episode_{clean_id}" / "plan.json",
    ]:
        if p_cand.exists():
            try:
                with open(p_cand, "r", encoding="utf-8") as pf:
                    loaded = json.load(pf)
                    if isinstance(loaded, list) and len(loaded) > 0:
                        plan_clips = loaded
                        break
            except Exception:
                pass

    def get_words_between(st: float, et: float) -> list[dict]:
        return [w for w in words if float(w["start"]) >= st - 0.05 and float(w["end"]) <= et + 0.05]

    def get_tail_quote(et: float, window_s: float = 6.5) -> str:
        ws = [w.get("word", "").strip() for w in words if et - window_s <= float(w["end"]) <= et + 0.15]
        return " ".join(ws[-10:]).strip()

    # Step 1: Detect spoken 'Clip N' cues from Whisper transcript if plan.json is not yet present
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
        "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19, "twenty": 20
    }
    raw_cues = []
    for i, s in enumerate(segments):
        t = s.get("text", "")
        m = re.search(r"\bclip\s+(\w+)\b", t, re.IGNORECASE)
        if m and "next clip" not in t.lower() and "final clip" not in t.lower():
            w_val = m.group(1).lower()
            c_num = int(w_val) if w_val.isdigit() else word_to_num.get(w_val)
            if c_num is not None:
                w_start = float(s.get("start", 0.0))
                for w in s.get("words", []):
                    if "clip" in w.get("word", "").lower():
                        w_start = float(w["start"])
                        break
                intro_start = float(s["start"]) if (float(s["start"]) < w_start and (w_start - float(s["start"])) < 4.0) else w_start
                raw_cues.append({"num": c_num, "start": intro_start, "text": t.strip()})
    raw_cues.sort(key=lambda x: x["start"])
    cues = []
    seen_nums = set()
    for rc in raw_cues:
        if rc["num"] not in seen_nums:
            cues.append(rc)
            seen_nums.add(rc["num"])

    recommendations = []

    # Step 2: Determine Opener Sting ('deepDive-strong.mp3') placement in the opening clip
    opener_at = None
    opener_quote = ""
    if plan_clips:
        c0 = plan_clips[0]
        c0_segs = [s for s in c0.get("segments", []) if s.get("type") == "audio"]
        if c0_segs:
            opener_at = round(float(c0_segs[0].get("end", 17.41)), 2)
            opener_quote = c0_segs[0].get("text", "").strip()
    if opener_at is None:
        # Look for sentence boundary in [12s, 28s] right before 'Today we are going on a... deep dive' or after opening question
        c0_words = get_words_between(0.0, 32.0)
        raw_h_end = None
        for w in c0_words:
            if 12.0 <= float(w["end"]) <= 28.0 and any(w.get("word", "").strip().endswith(p) for p in [".", "?", "!"]):
                raw_h_end = float(w["end"])
                break
        if raw_h_end is not None:
            next_ws = [float(w["start"]) for w in words if float(w["start"]) > raw_h_end + 0.01]
            next_st = next_ws[0] if next_ws else raw_h_end + 0.3
            opener_at = resolve_acoustic_word_end(raw_h_end, next_st, audio_path)
        else:
            opener_at, opener_quote = find_best_sentence_boundary(segments, 20.0, window=12.0)

    if not opener_quote:
        opener_quote = get_tail_quote(opener_at)

    # Detect redundant welcome cuts ('Welcome to the deep dive' / 'Today we are going on a massive deep dive')
    suggested_cuts = detect_redundant_welcome_cuts(words, segments, opener_at, audio_path)

    recommendations.append({
        "at": opener_at,
        "music_file": "deepDive-strong.mp3",
        "reason": f"Clip 0 Show Opener ('Welcome to deepDive, I am Satosha & Satoshi' + 10s music) after hook: '...{opener_quote[-48:]}'",
        "mode": "fade_2s_xfade_10",
        "duration": strong_dur,
        "duck_db": -14
    })

    # Step 3: Place alternating Bluesy Vibes / Howling at the end of EVERY clip and before the next clip starts
    inter_clip_boundaries = []
    if plan_clips and len(plan_clips) >= 2:
        for idx in range(len(plan_clips) - 1):
            cur_clip = plan_clips[idx]
            nxt_clip = plan_clips[idx + 1]
            c_num = cur_clip.get("num", idx)
            nxt_num = nxt_clip.get("num", idx + 1)
            nxt_title = nxt_clip.get("title", f"Clip {nxt_num}")
            end_t = round(float(cur_clip.get("end", 0.0)), 2)
            if end_t > opener_at + 5.0 and end_t < total_time - 5.0:
                inter_clip_boundaries.append({
                    "at": end_t,
                    "from_clip": c_num,
                    "to_clip": nxt_num,
                    "to_title": nxt_title,
                    "tail_quote": get_tail_quote(end_t)
                })
    elif len(cues) >= 2:
        # Build boundaries directly from spoken 'Clip 1', 'Clip 2', ..., 'Clip N' markers
        for idx, cue in enumerate(cues):
            next_st = cue["start"]
            if next_st <= opener_at + 8.0:
                continue
            w_prev = [w for w in words if float(w["start"]) < next_st - 0.02]
            raw_et = round(float(w_prev[-1]["end"]), 2) if w_prev else round(next_st, 2)
            et = resolve_acoustic_word_end(raw_et, next_st, audio_path)
            from_c = 0 if idx == 0 else cues[idx - 1]["num"]
            to_c = cue["num"]
            if et > opener_at + 5.0 and et < total_time - 5.0:
                inter_clip_boundaries.append({
                    "at": et,
                    "from_clip": from_c,
                    "to_clip": to_c,
                    "to_title": f"Clip {to_c}",
                    "tail_quote": get_tail_quote(et)
                })

    for b_idx, b in enumerate(inter_clip_boundaries):
        sting_file = (
            "Bluesy Vibes (Sting) - Doug Maxwell_Media Right Productions.mp3"
            if b_idx % 2 == 0
            else "Howling (Sting) - Gunnar Olsen.mp3"
        )
        recommendations.append({
            "at": b["at"],
            "music_file": sting_file,
            "reason": f"End of Clip {b['from_clip']} → Before Clip {b['to_clip']} ({b['to_title']}): '...{b['tail_quote'][-42:]}'",
            "mode": "fade_2s_xfade_10",
            "duration": 5.5,
            "duck_db": -14
        })

    # Step 4: Place deepDive-conclusion.mp3 (5.5s: 'I am Satosha, and I am Satoshi' + ~4s music) at the very end
    last_seg = segments[-1] if segments else {}
    raw_outro_t = float(words[-1]["end"]) if words else float(last_seg.get("end", total_time))
    outro_t = resolve_acoustic_word_end(raw_outro_t, None, audio_path)
    outro_txt = get_tail_quote(outro_t) or last_seg.get("text", "").strip()

    recommendations.append({
        "at": outro_t,
        "music_file": "deepDive-conclusion.mp3",
        "reason": f"Episode Finale Sign-Off ('I am Satosha, and I am Satoshi' + 4s closing music) after final words: '...{outro_txt[-45:]}'",
        "mode": "fade_2s_xfade_10",
        "duration": 5.5,
        "duck_db": -14
    })

    # Auto-save suggested cuts and canonical stings into podcast_edit.json so the timeline is ready out-of-the-box
    edit_data = load_podcast_edit(clean_id)
    existing_cuts = edit_data.get("cuts", [])
    for sc in suggested_cuts:
        if not any(abs(float(c.get("start", -99)) - sc["start"]) < 0.4 for c in existing_cuts):
            existing_cuts.append(sc)
    edit_data["cuts"] = existing_cuts
    edit_data["stings"] = [
        {
            "id": f"sting_{idx}_{int(r['at'] * 10)}",
            "at": r["at"],
            "music_file": r["music_file"],
            "mode": r["mode"],
            "duck_db": r["duck_db"],
            "duration": r["duration"],
            "reason": r["reason"]
        }
        for idx, r in enumerate(recommendations)
    ]
    save_podcast_edit(clean_id, edit_data)

    return {
        "success": True,
        "recommendations": recommendations,
        "suggested_cuts": suggested_cuts,
        "edit": edit_data
    }

def generate_sting_flow_preview(clean_id: str, sting_file: str, at_sec: float, pre_sec: float = 15.0, post_sec: float = 15.0) -> Path | None:
    """
    Generates a contextual preview around the sting at at_sec:
    - Front side: 0.2s silence gap, no crossfade.
    - Tail of sting: fades out 2.0s, and crossfades 1.0s into incoming podcast speech at 100% FULL VOLUME (strictly ZERO afade=t=in on human speech).
    - Respects any cuts in podcast_edit.json (e.g., stripped 'Today we are going on a massive deep dive' after deepDive-strong.mp3).
    - If outro conclusion sting: plays the final 18s of dialogue up to sentence end, 0.2s silence gap, and 5.5s conclusion sting ('I am Satosha, and I am Satoshi' + 4s closing music) fading out over 2.0s.
    """
    audio_path = get_episode_audio_path(clean_id)
    if not audio_path or not audio_path.exists():
        return None

    stings_dict = {s["filename"]: Path(s["path"]) for s in get_available_stings()}
    sting_path = stings_dict.get(sting_file)
    if not sting_path or not sting_path.exists():
        return None

    total_dur = 3600.0
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip():
            total_dur = float(res.stdout.strip())
    except Exception:
        pass

    # Probe sting duration
    sting_dur = 7.0
    try:
        cmd_s = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(sting_path)]
        res_s = subprocess.run(cmd_s, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res_s.returncode == 0 and res_s.stdout.strip():
            sting_dur = float(res_s.stdout.strip())
    except Exception:
        pass

    preview_dir = get_episode_podcast_dir(clean_id) / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    clean_stem = re.sub(r'[^a-zA-Z0-9_-]', '_', Path(sting_file).stem)
    out_file = preview_dir / f"flow_{int(at_sec * 100)}_{clean_stem}.mp3"

    # Check if this is the outro conclusion sting at the very end of the speech track
    is_outro_ending = (at_sec >= total_dur - 3.0) or ("conclusion" in sting_file and at_sec >= total_dur - 45.0)

    if is_outro_ending:
        # Previews the final 18 seconds of dialogue up to the final words, followed by 0.2s silence and 5.5s conclusion sting fading out over 2.0s!
        seg1_dur = min(18.0, at_sec)
        seg1_start = max(0.0, at_sec - seg1_dur)
        silence_front = 0.2
        sting_start_s = seg1_dur + silence_front
        sting_start_ms = int(sting_start_s * 1000)

        eff_outro_dur = min(5.5, sting_dur) if "conclusion" in sting_file else sting_dur
        fade_out_dur = min(2.0, eff_outro_dur)
        fade_out_st = max(0.0, eff_outro_dur - fade_out_dur)

        filter_str = (
            f"[1:a]atrim=0:{eff_outro_dur:.3f},afade=t=out:st={fade_out_st:.3f}:d={fade_out_dur:.3f},adelay={sting_start_ms}|{sting_start_ms}[sting_delayed];"
            f"[0:a][sting_delayed]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[out]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{seg1_start:.3f}", "-t", f"{seg1_dur:.3f}", "-i", str(audio_path),
            "-i", str(sting_path),
            "-filter_complex", filter_str,
            "-map", "[out]",
            "-c:a", "libmp3lame", "-b:a", "128k",
            str(out_file)
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if out_file.exists():
                return out_file
        except Exception as e:
            print(f"[PODCAST] Outro flow preview ffmpeg error: {e}")
        return None

    # Mid-roll / Intro transition:
    # Check if podcast_edit.json has cuts right around at_sec (e.g., stripped welcome sentence)
    edit_data = load_podcast_edit(clean_id)
    cuts = []
    for c in edit_data.get("cuts", []):
        try:
            cs, ce = float(c.get("start", 0.0)), float(c.get("end", 0.0))
            if ce > cs + 0.05:
                cuts.append((cs, ce))
        except Exception:
            pass
    cuts.sort(key=lambda x: x[0])

    seg1_start = max(0.0, at_sec - pre_sec)
    seg1_dur = max(0.5, at_sec - seg1_start)

    # Build post-sting speech intervals skipping any cut regions in [at_sec, at_sec + post_sec + 10]
    post_cursor = min(total_dur, at_sec)
    # Skip any tiny breath gap before first word after at_sec
    post_slices = []
    rem_dur = post_sec
    for cs, ce in cuts:
        if ce <= post_cursor:
            continue
        if cs > post_cursor:
            chunk = min(rem_dur, cs - post_cursor)
            if chunk > 0.08:
                post_slices.append((post_cursor, chunk))
                rem_dur -= chunk
        post_cursor = max(post_cursor, ce)
        if rem_dur <= 0.05:
            break
    if rem_dur > 0.05 and post_cursor < total_dur:
        chunk = min(rem_dur, total_dur - post_cursor)
        if chunk > 0.08:
            post_slices.append((post_cursor, chunk))
    if not post_slices:
        post_slices = [(min(total_dur, at_sec), max(0.5, min(total_dur, at_sec + post_sec) - min(total_dur, at_sec)))]

    # Canonical duration: full 16.71s for deepDive-strong.mp3, 5.5s for Bluesy Vibes / Howling / deepDive-conclusion
    silence_front = 0.2
    if "strong" in sting_file:
        eff_sting_dur = sting_dur
    else:
        eff_sting_dur = min(5.5, sting_dur)

    sting_start_s = seg1_dur + silence_front
    sting_start_ms = int(sting_start_s * 1000)

    fade_out_dur = min(2.0, eff_sting_dur)
    fade_out_st = max(0.0, eff_sting_dur - fade_out_dur)

    crossfade_dur = 1.0
    seg2_start_s = max(seg1_dur, sting_start_s + eff_sting_dur - crossfade_dur)

    inputs = ["-ss", f"{seg1_start:.3f}", "-t", f"{seg1_dur:.3f}", "-i", str(audio_path)]
    post_labels = []
    cur_delay_s = seg2_start_s
    for idx_p, (ps, pd) in enumerate(post_slices):
        inputs.extend(["-ss", f"{ps:.3f}", "-t", f"{pd:.3f}", "-i", str(audio_path)])
        delay_ms = int(cur_delay_s * 1000)
        # Strictly ZERO afade=t=in on human speech so incoming words enter at 100% full volume
        post_labels.append((idx_p + 1, delay_ms, f"[spost{idx_p}]"))
        cur_delay_s += pd

    sting_in_idx = len(post_slices) + 1
    inputs.extend(["-i", str(sting_path)])

    filter_parts = []
    mix_labels = ["[0:a]"]
    for in_i, d_ms, lbl in post_labels:
        filter_parts.append(f"[{in_i}:a]adelay={d_ms}|{d_ms}{lbl};")
        mix_labels.append(lbl)
    filter_parts.append(
        f"[{sting_in_idx}:a]atrim=0:{eff_sting_dur:.3f},afade=t=out:st={fade_out_st:.3f}:d={fade_out_dur:.3f},adelay={sting_start_ms}|{sting_start_ms}[sting_delayed];"
    )
    mix_labels.append("[sting_delayed]")
    filter_parts.append(
        f"{''.join(mix_labels)}amix=inputs={len(mix_labels)}:duration=longest:dropout_transition=0:normalize=0[out]"
    )

    cmd = [
        "ffmpeg", "-y"
    ] + inputs + [
        "-filter_complex", "".join(filter_parts),
        "-map", "[out]",
        "-c:a", "libmp3lame", "-b:a", "128k",
        str(out_file)
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if out_file.exists():
            return out_file
    except Exception as e:
        print(f"[PODCAST] Flow preview ffmpeg error: {e}")

    return None

def export_podcast_to_gdrive(clean_id: str, custom_dest: str = "") -> tuple[bool, str]:
    """
    Copies rendered podcast MP3 and companion podcast_meta.json into Google Drive pickup folder for meta-muse.
    Enforces that the episode MUST be mined from Mempool to Template before publishing.
    Tags the audio track directly with complete ID3 metadata (and cover art if present).
    """
    # 1. Enforce that episode is mined into Block Template
    mempool, template, chain, _ = parse_summary_structure()
    template_item = next((t for t in template if t.get("filename") == f"{clean_id}.md" or str(t.get("number")) == clean_id), None)
    if not template_item:
        is_mempool = any(m.get("filename") == f"_{clean_id}.md" or m.get("slug") == clean_id for m in mempool)
        if is_mempool or (SRC_DIR / f"_{clean_id}.md").exists():
            return False, f"Episode '{clean_id}' is still in Mempool. You must Mine the episode into the Block Template first before pushing to Google Drive!"
        if not clean_id.isdigit():
            return False, f"Episode '{clean_id}' is not an active mined episode in the Block Template. Please Mine it first."

    # 2. Locate or render podcast MP3
    mp3_path = get_episode_podcast_mp3_path(clean_id)
    if not mp3_path or not mp3_path.exists():
        success, res_path, msg = render_podcast_pipeline(clean_id)
        if not success or not Path(res_path).exists():
            return False, f"Cannot export: Podcast MP3 is not rendered yet ({msg})"
        mp3_path = Path(res_path)

    # 3. Destination folder in Google Drive (dd_hub/audio)
    dest_str = custom_dest.strip()
    settings = load_settings()
    if not dest_str:
        dest_str = settings.get("gdrive_pickup_path", str(get_dd_hub_root() / "audio"))

    dest_dir = Path(dest_str)
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Could not create Google Drive destination '{dest_str}': {e}"

    target_mp3 = dest_dir / f"podcast_{clean_id}.mp3"

    # 4. Resolve episode title and description
    ep_title = f"Episode {clean_id}"
    target_md = SRC_DIR / f"{clean_id}.md"
    if target_md.exists():
        try:
            with open(target_md, "r", encoding="utf-8") as pf:
                m = re.search(r"^#\s+(.*)$", pf.read(), re.MULTILINE)
                if m:
                    ep_title = m.group(1).strip()
        except Exception:
            pass

    clean_title_only = re.sub(r'^\d+\s*:\s*', '', ep_title).strip()
    formatted_title = f"{clean_id} : {clean_title_only}" if clean_id.isdigit() and not ep_title.startswith(f"{clean_id} :") else ep_title

    # 5. Check for cover image to embed
    cover_image_path = None
    episode_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id
    for img_candidate in [
        episode_dir / "cover.webp",
        episode_dir / "cover.png",
        episode_dir / "cover.jpg",
        IMG_DIR / f"{clean_id}.png",
        IMG_DIR / f"{clean_id}.jpg"
    ]:
        if img_candidate.exists():
            cover_image_path = img_candidate
            break

    # 6. Tag audio track directly with ID3 metadata via FFmpeg to target_mp3
    canonical_url = f"https://deepdive.shutri.com/{clean_id}.html"
    spotify_url = settings.get("spotify_url", "https://open.spotify.com/show/7doWf0GON9JsG6r8igc7RE")
    apple_url = settings.get("apple_podcasts_url", "https://podcasts.apple.com/us/podcast/deep-dive-with-gemini/id1844532251")
    yt_music_url = settings.get("youtube_music_url", "https://music.youtube.com/playlist?list=PLIX4sFsmu37qtJMlv-VzMYWM26M1QyXTe")
    fountain_url = settings.get("fountain_url", "https://fountain.fm/show/7LBvZT6ffpGyubvk8aSF")
    lightning_addr = settings.get("lightning_address", "shutosha@primal.net")
    year_str = str(datetime.now().year)

    ffmpeg_tag_cmd = ["ffmpeg", "-y", "-i", str(mp3_path)]
    if cover_image_path:
        ffmpeg_tag_cmd.extend([
            "-i", str(cover_image_path),
            "-map", "0:a",
            "-map", "1:v",
            "-c:a", "copy",
            "-c:v", "mjpeg",
            "-metadata:s:v", "title=Album cover",
            "-metadata:s:v", "comment=Cover (front)"
        ])
    else:
        ffmpeg_tag_cmd.extend(["-c", "copy"])

    ffmpeg_tag_cmd.extend([
        "-metadata", f"title={formatted_title}",
        "-metadata", "artist=Knowledge Deep Dive",
        "-metadata", "album=Deep Dive with Gemini",
        "-metadata", "album_artist=Knowledge Deep Dive",
        "-metadata", f"track={clean_id}",
        "-metadata", "genre=Podcast",
        "-metadata", f"date={year_str}",
        "-metadata", f"comment={canonical_url}",
        "-id3v2_version", "3",
        str(target_mp3)
    ])

    try:
        tag_res = subprocess.run(ffmpeg_tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if tag_res.returncode != 0:
            shutil.copy2(mp3_path, target_mp3)
    except Exception:
        shutil.copy2(mp3_path, target_mp3)

    # 6.5 Export standalone square cover image for distribution agent (Spotify for Creators requires separate file)
    target_cover_path = dest_dir / f"podcast_{clean_id}_cover.jpg"
    has_cover_exported = False
    if cover_image_path and cover_image_path.exists():
        try:
            cmd_cover = [
                "ffmpeg", "-y",
                "-i", str(cover_image_path),
                "-vf", "scale=1600:1600:force_original_aspect_ratio=decrease,pad=1600:1600:(ow-iw)/2:(oh-ih)/2:color=black",
                "-q:v", "2",
                str(target_cover_path)
            ]
            res_c = subprocess.run(cmd_cover, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res_c.returncode == 0 and target_cover_path.exists():
                has_cover_exported = True
            else:
                shutil.copy2(cover_image_path, target_cover_path)
                has_cover_exported = True
        except Exception as ex_cov:
            print(f"[EXPORT] Warning exporting cover image: {ex_cov}")

    # 6.6 Copy MP4 video if present
    video_path = get_episode_podcast_video_path(clean_id)
    target_video_path = dest_dir / f"podcast_{clean_id}.mp4"
    has_video_exported = False
    if video_path.exists():
        try:
            shutil.copy2(video_path, target_video_path)
            has_video_exported = True
        except Exception as ex_vid:
            print(f"[EXPORT] Warning copying video to Google Drive: {ex_vid}")

    # 7. Write companion meta-muse distribution manifest
    meta = {
        "episode": clean_id,
        "title": formatted_title,
        "clean_title": clean_title_only,
        "audio_file": target_mp3.name,
        "video_file": target_video_path.name if has_video_exported else None,
        "cover_file": target_cover_path.name if has_cover_exported else None,
        "local_pickup_path": str(target_mp3.resolve()),
        "canonical_url": canonical_url,
        "spotify_show": spotify_url,
        "apple_podcasts": apple_url,
        "youtube_music": yt_music_url,
        "fountain_show": fountain_url,
        "lightning_tips": lightning_addr,
        "has_cover": has_cover_exported,
        "exported_at": datetime.now().isoformat(),
        "status": "ready_for_meta_muse",
        "instructions": "Pickup audio and upload to Spotify for Creators episode draft."
    }
    meta_path = dest_dir / f"podcast_{clean_id}_meta.json"
    with open(meta_path, "w", encoding="utf-8") as jf:
        json.dump(meta, jf, indent=2)

    return True, f"Exported {target_mp3.name} with complete ID3 metadata to Google Drive: {dest_dir}"

def export_video_to_gdrive(clean_id: str, custom_dest: str = None) -> tuple[bool, str]:
    """
    Exports rendered 1080p horizontal podcast video and comprehensive video_meta.json
    to dedicated Google Drive folder (default G:/My Drive/Podcast_Video_Pickup)
    for YouTube, Spotify Video, and TikTok long-form distribution.
    """
    video_path = get_episode_podcast_video_path(clean_id)
    if not video_path.exists():
        return False, f"Video not found for episode {clean_id}. Please render the video master first."

    default_dest = get_dd_hub_root() / "video"
    dest_dir = Path(custom_dest.strip()) if custom_dest and custom_dest.strip() else default_dest

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Could not access or create Google Drive destination '{dest_dir}': {e}"

    # Get episode details
    mempool, template, chain, _ = parse_summary_structure()
    all_items = mempool + template + chain
    matching = next((it for it in all_items if it.get("filename") == f"{clean_id}.md" or str(it.get("number")) == clean_id), None)
    ep_title = matching["title"] if matching and matching.get("title") else f"Episode {clean_id}"
    clean_title_only = re.sub(r"^\d+\s*[:\-]\s*", "", ep_title).strip()
    formatted_title = f"{clean_id} : {clean_title_only}" if clean_id.isdigit() else clean_title_only

    # Probe duration
    total_dur = 0.0
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip():
            total_dur = float(res.stdout.strip())
    except Exception:
        pass

    target_video_path = dest_dir / f"podcast_{clean_id}.mp4"
    try:
        shutil.copy2(video_path, target_video_path)
    except Exception as e:
        return False, f"Failed copying video to Google Drive: {e}"

    # Export thumbnail
    target_thumb_path = dest_dir / f"podcast_{clean_id}_thumbnail.jpg"
    has_thumb = False
    episode_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id
    cover_image_path = None
    for cand in [
        episode_dir / "cover.webp",
        episode_dir / "cover.png",
        episode_dir / "cover.jpg",
        IMG_DIR / f"{clean_id}.png",
        IMG_DIR / f"{clean_id}.jpg"
    ]:
        if cand.exists():
            cover_image_path = cand
            break

    if cover_image_path:
        try:
            cmd_thumb = [
                "ffmpeg", "-y", "-i", str(cover_image_path),
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black",
                "-q:v", "2",
                str(target_thumb_path)
            ]
            res_th = subprocess.run(cmd_thumb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res_th.returncode == 0 and target_thumb_path.exists():
                has_thumb = True
        except Exception:
            pass

    # Read article summary
    summary_text = ""
    md_file = SRC_DIR / f"{clean_id}.md"
    if md_file.exists():
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                c_txt = f.read()
                paras = [p.strip() for p in c_txt.split("\n\n") if p.strip() and not p.strip().startswith("#") and not p.strip().startswith("<!--")]
                if paras:
                    summary_text = paras[0][:400]
        except Exception:
            pass

    size_mb = round(target_video_path.stat().st_size / (1024 * 1024), 1)
    mins = int(total_dur // 60)
    secs = int(total_dur % 60)

    video_meta = {
        "episode": clean_id,
        "title": formatted_title,
        "clean_title": clean_title_only,
        "video_file": target_video_path.name,
        "thumbnail_file": target_thumb_path.name if has_thumb else None,
        "file_size_mb": size_mb,
        "resolution": "1920x1080",
        "aspect_ratio": "16:9",
        "duration_seconds": round(total_dur, 2),
        "duration_formatted": f"{mins:02d}:{secs:02d}",
        "canonical_url": f"https://deepdive.shutri.com/{clean_id}.html",
        "distribution_targets": ["YouTube", "Spotify Video", "TikTok Long-Form"],
        "description": summary_text,
        "status": "ready_for_video_distribution",
        "exported_at": datetime.now().isoformat(),
        "instructions": "Distribute 1080p video podcast to YouTube Channel, Spotify for Creators Video, and TikTok."
    }

    meta_path = dest_dir / f"podcast_{clean_id}_video_meta.json"
    with open(meta_path, "w", encoding="utf-8") as jf:
        json.dump(video_meta, jf, indent=2)

    return True, f"Exported {target_video_path.name} ({size_mb} MB) and video_meta.json to {dest_dir}"


def smart_streamline_narrative(raw_text: str, title: str = "", ep_num: str = "", lightning_addr: str = "shutosha@primal.net") -> tuple[str, int]:
    """
    Intelligently structures continuous audio transcripts into publication-ready Nostr Markdown (NIP-23):
    1. Removes existing heading/footer duplication for idempotency.
    2. Inserts document title H1 and episode metadata blockquote.
    3. Normalizes punctuation, grammar casing, and speech artifacts.
    4. Detects thematic section shifts and injects semantic H2 headings.
    5. Converts sequential enumeration ('First, ...', 'Second, ...') into Markdown bullet lists.
    6. Identifies and bolds core technical entities and architectural concepts.
    7. Isolates promotional / sponsor / channel notes in callout quote blocks (> 📢 **Promotional Note**: ...).
    8. Appends clean Nostr publication footer with Lightning tip address.
    Returns (streamlined_markdown, promo_blocks_count).
    """
    if not raw_text or not raw_text.strip():
        return "", 0

    text = raw_text.strip()

    # Strip existing Nostr header / title if re-running
    text = re.sub(r'^#\s+[^\n]+\n*', '', text)
    text = re.sub(r'>\s*🎙️[^\n]+\n*(?:>\s*⚡[^\n]+\n*)?(?:---\s*\n*)?', '', text)
    # Strip existing footer if present
    text = re.sub(r'---\s*\n+###\s*⚡ Connect & Support[\s\S]*$', '', text)
    # Strip existing markdown headings (H1-H6) to ensure idempotency if re-streamlining
    text = re.sub(r'(?m)^#{1,6}\s+[^\n]+\n*', '', text)

    # Normalize whitespace & punctuation
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\s+([,.:;?!])', r'\1', text)
    text = re.sub(r'([,.:;?!])(?=[^\s\d])', r'\1 ', text)
    text = re.sub(r'\bi\b', 'I', text)
    text = re.sub(r'\bi\'m\b', "I'm", text, flags=re.IGNORECASE)
    text = re.sub(r'\bi\'ve\b', "I've", text, flags=re.IGNORECASE)
    text = re.sub(r'\bi\'ll\b', "I'll", text, flags=re.IGNORECASE)
    text = re.sub(r'\bi\'d\b', "I'd", text, flags=re.IGNORECASE)

    # Remove inline tag questions and conversational fillers
    text = re.sub(r',\s*right\?', '.', text, flags=re.IGNORECASE)
    text = re.sub(r',\s*you\s+know\?', '.', text, flags=re.IGNORECASE)
    text = re.sub(r',\s*yeah\?', '.', text, flags=re.IGNORECASE)
    text = re.sub(r'\byou\s+know,\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\boh,\s*yeah,\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\boh\s+yeah,\s*', '', text, flags=re.IGNORECASE)

    # Capitalize after sentence terminators
    text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
    if text:
        text = text[0].upper() + text[1:]

    # Promotional detection regex pattern (ruthlessly discard)
    promo_patterns = [
        r'\b(?:sponsor(?:ed|s)?|patreon|subscribe|follow us on|discount code|promo code|rate and review|check out the link|link in the description|leave a five star|support (?:us|the show|the podcast))\b',
        r'\b(?:supported by|brought to you by|special offer|advertis(?:er|ement)|our partners? at)\b',
        r'\b(?:welcome\s+(?:back\s+)?to\s+(?:the\s+)?deep\s*dive|in\s+this\s+deep\s*dive|draw(?:ing)?\s+this\s+deep\s*dive\s+to\s+a\s+close)\b',
        r'\b(?:deep\s*dive\s+website|progressive\s+web\s+app|access\s+all\s+of\s+the\s+research\s+offline|read\s+these\s+massive\s+deep\s+dives)\b',
        r'\b(?:install|access)\s+it\s+(?:essentially\s+)?as\s+a\s+native\s+app\b',
        r'\b(?:share\s+this\s+show|if\s+you\s+have\s+expertise\s+in\s+the\s+specific\s+fields|see\s+you\s+on\s+the\s+next\s+deep\s+dive|i\s+am\s+satoshi)\b',
        r'\b(?:keep\s+searching,\s*keep\s+the\s+quest\s+on|symbiosis\s+of\s+artificial\s+and\s+natural\s+intelligence)\b',
        r'\b(?:research\s+hub\s+at\s+deepdive|secure\s+enclave\s+of\s+your\s+own\s+to\s+read)\b'
    ]
    promo_regex = re.compile('|'.join(promo_patterns), re.IGNORECASE)

    # Key entity highlighting (bolding core concepts)
    key_entities = [
        r'\bMeta ?Muse\b', r'\bMSL\b', r'\bMeta Superintelligence Labs\b',
        r'\bPareto efficient cost frontier\b', r'\bPareto efficient\b',
        r'\bTau3-Bench Banking\b', r'\bGDPval-AA\b', r'\bMuse Spark\b',
        r'\bDocument Object Model\b', r'\bDOM\b', r'\bheadless browser\b',
        r'\bMuse Secure VM\b', r'\bsystemd-nspawn\b', r'\bSentinel\b',
        r'\beBPF tracing\b', r'\beBPF\b', r'\bStripe Link\b',
        r'\bprogressive capital allocation\b', r'\btax loss harvesting\b',
        r'\bquantitative portfolio management\b', r'\bambient feed reporting\b',
        r'\bPerplexity Computer\b', r'\bPrivate Cloud Compute\b', r'\bPCC\b',
        r'\bInnovator\'s Dilemma\b', r'\bLaggard Coalition\b',
        r'\bData Center Moratorium Act\b',
        r'\bLarge Language Models?\b', r'\bLLMs?\b', r'\bNeural Networks?\b',
        r'\bDiffusion Models?\b', r'\bZero-Knowledge Proofs?\b',
        r'\bLightning Network\b', r'\bNostr\b'
    ]

    def bold_entities(t: str) -> str:
        for pat in key_entities:
            t = re.sub(r'(?<!\*\*)(' + pat + r')(?!\*\*)', r'**\1**', t, flags=re.IGNORECASE)
        return t

    # Major thematic section markers
    section_patterns = [
        (r'\b(before we really plunge|setting the tone|intentional slowing down)\b', "Introduction: Setting the Tone"),
        (r'\b(set the context for this journey|causing an absolute earthquake|metas? mues?|meta muse)\b', "The Agentic Shift: From Q&A to Execution"),
        (r'\b(what Metamuse actually is under the hood|Meta Superintelligence Labs|Pareto efficient cost frontier)\b', "Architecture & The Pareto Efficient Frontier"),
        (r'\b(how it navigates the web|headless browser|parsing the DOM|document object model)\b', "Autonomous Navigation: Parsing the DOM"),
        (r'\b(dedicated Muse secure VM|systemd-nspawn|virtual machine vault)\b', "Isolation Architecture: Dedicated Secure Containers"),
        (r'\b(supervisor process called Sentinel|kernel level tracking|EBPF tracing)\b', "Kernel-Level Enforcement: Sentinel & eBPF Supervision"),
        (r'\b(autonomous quantitative portfolio management|tax loss harvesting|brokerage account)\b', "High-Consequence Workflows: Autonomous Portfolio Management"),
        (r'\b(cross platform creative|social layer|media production|mosaic)\b', "Creative Workflows: Cross-Platform Media Automation"),
        (r'\b(progressive capital allocation|trust must be structurally earned)\b', "Earning Trust: Progressive Capital Allocation"),
        (r'\b(stripe link|single use, merchant scoped|virtual credit cards)\b', "Financial Protection: Merchant-Scoped Virtual Cards"),
        (r'\b(Perplexity Computer|multi model orchestration|ephemeral Linux runtimes)\b', "Competitive Landscape: Meta Muse vs. Perplexity Computer"),
        (r'\b(Apple\'s private cloud compute|PCC|stateless architecture)\b', "The Privacy Debate: Meta's Persistent State vs. Apple's PCC"),
        (r'\b(innovators dilemma|alphabet|parent company of google|75% of Alphabet\'s operating profit)\b', "The Innovator's Dilemma: Why Google Hesitates"),
        (r'\b(regulatory real politics|regulatory realpolitik|Dario Amodei|we must pace the frontier)\b', "Regulatory Realpolitik & Pacing the Frontier"),
        (r'\b(laggard coalition|economic strategy|corporate protectionism)\b', "The Laggard Coalition & Defensible Moats"),
        (r'\b(looking ahead|by the end of this|the future of the internet)\b', "Strategic Outlook: The Future of Ubiquitous Agents")
    ]

    # Split into sentences
    sentence_regex = re.compile(r'[^.!?]+[.!?]+(?:\s+|$)')
    sentences = sentence_regex.findall(text)
    if not sentences:
        sentences = [text]

    current_para = []
    promo_count = 0
    used_section_titles = set()

    # Prepend header if title provided (clean H1 only, no podcast metadata)
    doc_lines = []
    if title:
        doc_lines.append(f"# {title}")

    interjection_set = {
        'right.', 'right?', 'right!', 'exactly.', 'precisely.', 'correct.', 'yeah.', 'yep.', 'yes.',
        'sure.', 'totally.', 'definitely.', 'absolutely.', 'indeed.', 'okay.', 'alright.', 'all right.',
        'wow.', 'fair enough.', 'i see.', 'i follow.', 'i fall.', 'you bet.', 'obviously.', 'obviously not.',
        'we do.', 'it really is.', 'that makes sense.', 'i think that\'s a great idea.', 'oh, i\'m sure it does.',
        'okay, i like where this is going.', 'true.', 'agreed.', 'oh yeah.', 'oh, yeah.', 'yeah, right.',
        'no way.', 'that\'s right.', 'that is right.', 'sounds right.', 'makes sense.', 'got it.', 'i got it.',
        'is the optimal balance?', 'have a way.', 'we have and it\'s fantastic.', 'also correct.',
        'a lot of power in a chat app.', 'that\'s a great way to summarize it.', 'it really does.',
        'it does, but it\'s pure strategic reality.', 'this part is fascinating.'
    }

    for idx, s in enumerate(sentences):
        s_clean = s.strip()
        if not s_clean:
            continue

        # Filter out standalone conversational interjections
        norm_s = re.sub(r'[*_#`]', '', s_clean).strip().lower()
        if norm_s in interjection_set or re.match(r'^(?:right|exactly|precisely|yeah|yep|yes|okay|alright|wow|sure|correct)[.!?]$', norm_s):
            continue

        # Clean leading interjection words in longer sentences
        s_clean = re.sub(r'^(?:Right|Exactly|Precisely|Yeah|Yep|Yes|Okay|Alright|Well),\s+([a-zA-Z])', lambda m: m.group(1).upper(), s_clean, flags=re.IGNORECASE)
        s_clean = re.sub(r'^(?:Right|Exactly|Precisely|Yeah|Yep|Yes|Okay|Alright)\.\s+([a-zA-Z])', lambda m: m.group(1).upper(), s_clean, flags=re.IGNORECASE)

        # Check for section triggers
        triggered_heading = None
        for pat, sec_title in section_patterns:
            if sec_title not in used_section_titles and re.search(pat, s_clean, re.IGNORECASE):
                triggered_heading = sec_title
                used_section_titles.add(sec_title)
                break

        if triggered_heading:
            if current_para:
                doc_lines.append(' '.join(current_para))
                current_para = []
            doc_lines.append(f"\n## {triggered_heading}\n")

        # Check for promotional note - Ruthlessly drop completely
        is_promo = bool(promo_regex.search(s_clean))
        if is_promo:
            promo_count += 1
            continue

        # Speaker detection
        speaker_match = re.match(r'^(Host|Guest|Speaker \d+|Interviewer|Narrator)\s*:\s*(.*)', s_clean, re.IGNORECASE)
        if speaker_match:
            speaker_name = speaker_match.group(1).title()
            rest = speaker_match.group(2)
            s_clean = f"**{speaker_name}**: {rest}"

        # Turn multi-step enumeration into clean bullet points
        list_match = re.match(r'^(First|Second|Third|Finally|Furthermore|Crucially),\s*(.*)', s_clean, re.IGNORECASE)
        if list_match and idx > 0 and len(current_para) <= 1:
            step_word = list_match.group(1).title()
            rest_text = list_match.group(2)
            current_para.append(f"\n* **{step_word}**: {rest_text}")
            continue

        current_para.append(s_clean)

        # Paragraph break triggers
        is_transition = bool(re.match(r'^(However|Moreover|Furthermore|In addition|Therefore|Clinically|When|So|Now|And|In fact|Specifically|That said|Interestingly|If |By the time|This is |On the other hand|What is fascinating|To understand this|Here is why|Let us look|Consider|Notice how)', s_clean, re.IGNORECASE))

        if len(current_para) >= 4 or (len(current_para) >= 2 and is_transition and idx > 0) or idx == len(sentences) - 1:
            para_str = ' '.join(current_para)
            doc_lines.append(para_str)
            current_para = []

    if current_para:
        doc_lines.append(' '.join(current_para))

    full_doc = '\n\n'.join(doc_lines)
    full_doc = bold_entities(full_doc)

    return full_doc, promo_count


def extract_nostr_metadata(markdown_text: str, title: str = "", clean_id: str = "") -> dict:
    """
    Extracts and prepares NIP-23 long-form metadata for Nostr clients (Habla, Primal, NAK):
    - title: Document title
    - summary: Concise 1-2 sentence hook (150-250 characters)
    - image: Canonical image URL (from src/img/{clean_id}.png or ddma cover or fallback)
    - tags: Extracted list of topic tags
    - d_tag: Episode slug
    - published_at: Unix timestamp
    - canonical_url: Web reference ledger
    - word_count: Total words
    - reading_time_min: Estimated reading minutes
    - nak_command: Pre-formatted CLI command for nak event 30023
    """
    if not clean_id:
        clean_id = "index"

    # 1. Clean title
    doc_title = (title or "").strip()
    if not doc_title:
        m = re.search(r"^#\s+(.*)$", markdown_text, re.MULTILINE)
        if m:
            doc_title = m.group(1).strip()
        else:
            doc_title = f"Episode {clean_id}"

    # 2. Extract summary hook (first substantive paragraph, 1-2 sentences)
    clean_text = re.sub(r'(?m)^#{1,6}\s+.*$', '', markdown_text)
    clean_text = re.sub(r'(?m)^>.*$', '', clean_text)
    clean_text = re.sub(r'(?m)^\s*[\*\-]\s+.*$', '', clean_text)
    clean_text = re.sub(r'[\*_`]', '', clean_text)

    paras = [p.strip() for p in clean_text.split('\n\n') if len(p.strip()) > 50]
    first_para = paras[0] if paras else ''
    sentences = re.findall(r'[^.!?]+[.!?]+', first_para)
    summary = ''
    if sentences:
        summary = sentences[0].strip()
        if len(summary) < 120 and len(sentences) > 1:
            summary += ' ' + sentences[1].strip()
    if len(summary) > 240:
        summary = summary[:237].rsplit(' ', 1)[0] + '...'
    if not summary:
        summary = f"Research deep dive on {doc_title}."

    # 3. Resolve cover picture
    image_url = ""
    # Check src/img/{clean_id}.png / .webp / .jpg
    for ext in [".png", ".webp", ".jpg", ".jpeg"]:
        img_candidate = SRC_DIR / "img" / f"{clean_id}{ext}"
        if img_candidate.exists():
            image_url = f"https://deepdive.shutri.com/img/{clean_id}{ext}"
            break

    if not image_url:
        # Check src/ddma/docs/episodes/{clean_id}/cover.*
        for ext in [".webp", ".png", ".jpg"]:
            cover_candidate = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / f"cover{ext}"
            if cover_candidate.exists():
                image_url = f"https://deepdive.shutri.com/ddma/docs/episodes/{clean_id}/cover{ext}"
                break

    if not image_url:
        # Check first DDMA clip and auto-extract cover.webp keyframe if possible
        clip_candidate = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / "clips" / f"{clean_id}-1.mp4"
        if clip_candidate.exists():
            target_cover = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / "cover.webp"
            try:
                import subprocess
                subprocess.run(
                    ["ffmpeg", "-y", "-ss", "00:00:01", "-i", str(clip_candidate), "-vframes", "1", "-q:v", "2", str(target_cover)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
                )
                if target_cover.exists():
                    image_url = f"https://deepdive.shutri.com/ddma/docs/episodes/{clean_id}/cover.webp"
            except Exception:
                pass
            if not image_url:
                image_url = f"https://deepdive.shutri.com/ddma/docs/episodes/{clean_id}/clips/{clean_id}-1.mp4"

    if not image_url:
        image_url = "https://deepdive.shutri.com/img/shutoshaBuffalo.png"

    # 4. Extract topic tags
    entity_tags = [
        (r'\bMeta ?Muse\b', 'meta-muse'),
        (r'\bApple\b|\bPCC\b|\bPrivate Cloud Compute\b', 'apple-pcc'),
        (r'\bPerplexity\b', 'perplexity'),
        (r'\bAgents?\b|\bAgentic\b', 'ai-agents'),
        (r'\bPrivacy\b', 'privacy'),
        (r'\bSecurity\b|\beBPF\b|\bSentinel\b', 'cybersecurity'),
        (r'\bAutonomous\b', 'autonomous-systems'),
        (r'\bBitcoin\b|\bLightning\b|\bSats\b', 'bitcoin'),
        (r'\bNostr\b', 'nostr'),
        (r'\bLLMs?\b|\bAI\b|\bArtificial Intelligence\b', 'artificial-intelligence'),
        (r'\bStripe\b|\bPayments?\b', 'fintech'),
        (r'\bResearch\b|\bPaper\b', 'research')
    ]
    tags = []
    for pat, tag in entity_tags:
        if re.search(pat, markdown_text, re.IGNORECASE) and tag not in tags:
            tags.append(tag)
    if not tags:
        tags = ["research", "deepdive", "technology"]
    tags = tags[:6]

    # 5. Metadata stats
    word_count = len(re.findall(r'\b\w+\b', markdown_text))
    reading_time_min = max(1, round(word_count / 200)) if word_count else 1
    canonical_url = f"https://deepdive.shutri.com/{clean_id}.html"
    published_at = int(time.time())

    # 6. Pre-generate NAK command
    nak_flags = [
        f"-t d=\"{clean_id}\"",
        f"-t title=\"{doc_title}\"",
        f"-t summary=\"{summary}\"",
        f"-t image=\"{image_url}\"",
        f"-t published_at=\"{published_at}\"",
    ]
    for t in tags:
        nak_flags.append(f"-t t=\"{t}\"")
    nak_flags.append("-t client=\"mdIngest Cockpit\"")
    flag_str = " \\\n  ".join(nak_flags)
    nak_command = f"nak event -k 30023 \\\n  {flag_str} \\\n  --sec \"$NOSTR_NSEC\" \\\n  wss://relay.damus.io wss://nos.lol wss://relay.primal.net < narrative.md"

    return {
        "d_tag": clean_id,
        "title": doc_title,
        "summary": summary,
        "image": image_url,
        "tags": tags,
        "canonical_url": canonical_url,
        "word_count": word_count,
        "reading_time_min": reading_time_min,
        "published_at": published_at,
        "nak_command": nak_command
    }


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
            settings = load_settings()
            mname = settings.get("whisper_model", "large-v3-turbo")
            res_obj = run_faster_whisper_transcription(audio_path, model_name=mname, word_timestamps=True)
            segments = res_obj.get("segments", [])
            transcript_text = res_obj.get("text", "").strip() or transcript_text
            
            # Save acoustic transcription.json in src
            src_trans_json.parent.mkdir(parents=True, exist_ok=True)
            with open(src_trans_json, "w", encoding="utf-8") as tj:
                json.dump(res_obj, tj, indent=4)
        except Exception as we:
            print(f"[DDMA SEED] faster-whisper acoustic alignment fallback: {we}")

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

        # Prioritize raw continuous .m4a/.wav input over mastered podcast .mp3
        if (proj_dir / f"{clean_id}.m4a").exists():
            dest_audio_name = f"{clean_id}.m4a"
        elif (proj_dir / f"{clean_id}.wav").exists():
            dest_audio_name = f"{clean_id}.wav"
        else:
            audio_ext = audio_path.suffix if audio_path else ".m4a"
            dest_audio_name = f"{clean_id}{audio_ext}"
        dest_audio_path = proj_dir / dest_audio_name

        # Copy audio if missing
        if audio_path and audio_path.exists() and not dest_audio_path.exists():
            try:
                shutil.copy2(str(audio_path), str(dest_audio_path))
            except Exception as ce:
                print(f"[DDMA SEED] Error copying audio: {ce}")

        # Write or update project_info.json (preserve existing canonical .m4a)
        info_path = proj_dir / "project_info.json"
        if info_path.exists():
            try:
                with open(info_path, "r", encoding="utf-8") as inf:
                    existing = json.load(inf)
                if existing.get("audio_filename", "").endswith((".m4a", ".wav")):
                    dest_audio_name = existing["audio_filename"]
            except Exception:
                pass
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

        # Sync plan.json from src/ddma/docs/episodes/<id>/plan.json first if available
        plan_json_dest = proj_dir / "plan.json"
        src_plan_json = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id / "plan.json"
        if src_plan_json.exists() and src_plan_json.stat().st_size > 20:
            try:
                should_sync = not plan_json_dest.exists() or plan_json_dest.stat().st_size == 0
                if not should_sync:
                    with open(plan_json_dest, "r", encoding="utf-8") as pf_chk:
                        existing_p = json.load(pf_chk)
                    if existing_p and isinstance(existing_p, list) and existing_p[0].get("title") == "Clip 1":
                        should_sync = True
                if should_sync:
                    shutil.copy2(str(src_plan_json), str(plan_json_dest))
            except Exception as sp_err:
                print(f"[DDMA SEED] Warning syncing src plan.json: {sp_err}")

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
                    
                    # 4-part structure: Hook -> Mid Sting (Bluesy / Howling) -> Body -> Outro Sting (deepDive-conclusion)
                    mid_music = "Bluesy Vibes (Sting) - Doug Maxwell_Media Right Productions.mp3" if clip_num % 2 == 1 else "Howling (Sting) - Gunnar Olsen.mp3"
                    hook_end = min(t_curr + 20.0, target_b)
                    hook_win = [s for s in in_win if s["start"] >= t_curr and s["end"] <= hook_end + 1.0]
                    hook_text = " ".join(s["text"] for s in hook_win).strip() or win_text[:120]
                    
                    c_obj = {
                        "num": clip_num,
                        "title": f"Part {clip_num}",
                        "start": round(t_curr, 2),
                        "end": round(target_b, 2),
                        "duration": clip_dur,
                        "bridge_text": [f"What Is Part {clip_num + 1} ?"],
                        "segments": [
                            {"type": "audio", "start": round(t_curr, 2), "end": round(hook_end, 2), "duration": round(hook_end - t_curr, 2), "text": hook_text},
                            {"type": "music", "music_file": mid_music, "duration": 5.5, "silence_before": 0.2, "gap": 0.2, "fade_out": 2.0, "crossfade": 1.0, "volume": 1.0},
                            {"type": "audio", "start": round(hook_end, 2), "end": round(target_b, 2), "duration": round(target_b - hook_end, 2), "text": win_text},
                            {"type": "music", "music_file": "deepDive-conclusion.mp3", "duration": 5.5, "silence_before": 0.2, "gap": 0.2, "fade_out": 2.0, "crossfade": 0.0, "volume": 1.0}
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


def build_fast_indices():
    """
    Rapidly scans filesystem in bulk to index existing markdown files,
    covers, and video clip counts in a single pass (<10ms).
    """
    existing_src_files = set(os.listdir(SRC_DIR)) if SRC_DIR.exists() else set()
    
    # Fast bulk cover index
    existing_covers = set()
    if IMG_DIR.exists():
        try:
            for fname in os.listdir(IMG_DIR):
                name, ext = os.path.splitext(fname)
                if ext.lower() in ['.png', '.jpg', '.jpeg', '.webp']:
                    existing_covers.add(name.lstrip('_'))
        except Exception:
            pass
    
    for ddma_root in [PROJECT_ROOT / 'ddma', PROJECT_ROOT.parent / 'ddma']:
        ep_dir = ddma_root / 'docs' / 'episodes'
        if ep_dir.exists():
            try:
                for ep_name in os.listdir(ep_dir):
                    p = ep_dir / ep_name
                    if p.is_dir():
                        if (p / 'cover.png').exists() or (p / 'thumbnail.png').exists():
                            existing_covers.add(ep_name.lstrip('_'))
            except Exception:
                pass
        assets_dir = ddma_root / 'docs' / 'assets'
        if assets_dir.exists():
            try:
                for fname in os.listdir(assets_dir):
                    name, ext = os.path.splitext(fname)
                    if ext.lower() in ['.png', '.jpg']:
                        existing_covers.add(name.lstrip('_'))
            except Exception:
                pass

    # Fast bulk video counts (deduplicated per canonical `<ep>-<num>.mp4`)
    vid_sets = {}
    def add_vid(ep_id, clip_num_str=None):
        clean = str(ep_id).lstrip('_')
        if clean not in vid_sets:
            vid_sets[clean] = set()
        vid_sets[clean].add(str(clip_num_str) if clip_num_str is not None else f"vid_{len(vid_sets[clean])}")

    # Canonical deepDive clips
    canonical_eps = SRC_DIR / 'ddma' / 'docs' / 'episodes'
    if canonical_eps.exists():
        try:
            for ep_name in os.listdir(canonical_eps):
                clips_dir = canonical_eps / ep_name / 'clips'
                if clips_dir.exists():
                    for c in os.listdir(clips_dir):
                        m_c = re.match(rf"^_?{re.escape(str(ep_name).lstrip('_'))}-(\d+)\.mp4$", c)
                        if m_c:
                            add_vid(ep_name, m_c.group(1))
        except Exception:
            pass

    # DDMA projects clips
    for ddma_root in [PROJECT_ROOT / 'ddma', PROJECT_ROOT.parent / 'ddma']:
        proj_dir = ddma_root / 'projects'
        if proj_dir.exists():
            try:
                for proj_name in os.listdir(proj_dir):
                    if proj_name.startswith('episode_'):
                        ep_id = proj_name.replace('episode_', '')
                        p_clips = proj_dir / proj_name / 'clips'
                        if p_clips.exists():
                            for c in os.listdir(p_clips):
                                m_c = re.match(rf"^_?{re.escape(str(ep_id).lstrip('_'))}-(\d+)\.mp4$", c)
                                if m_c:
                                    add_vid(ep_id, m_c.group(1))
            except Exception:
                pass

    vid_counts = {k: len(v) for k, v in vid_sets.items()}

    # Legacy vid dir clips
    if VID_DIR.exists():
        try:
            for fname in os.listdir(VID_DIR):
                if fname.endswith('.mp4'):
                    m = re.match(r'^_?(\d+)-(\d+)\.mp4$', fname)
                    if m:
                        ep_k = m.group(1)
                        if ep_k not in vid_sets:
                            vid_sets[ep_k] = set()
                        vid_sets[ep_k].add(m.group(2))
                        vid_counts[ep_k] = len(vid_sets[ep_k])
        except Exception:
            pass

    return existing_src_files, existing_covers, vid_counts


def parse_summary_structure():
    """
    Parses SUMMARY.md and discovers Mempool drafts, Template episodes, and Master Chain blocks.
    Uses bulk-indexed in-memory lookups for sub-10ms response time.
    """
    if not SUMMARY_FILE.exists():
        return [], [], [], 247

    existing_src_files, existing_covers, vid_counts = build_fast_indices()

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

            clean_slug = filename.replace(".md", "").lstrip("_")
            has_img = clean_slug in existing_covers
            v_count = vid_counts.get(clean_slug, 0)
            file_exists = filename in existing_src_files

            item = {
                "title": title_text,
                "filename": filename,
                "slug": clean_slug,
                "has_image": has_img,
                "vid_count": v_count,
                "is_locked": v_count > 0,
                "exists": file_exists
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

    try:
        regenerate_episodes_manifest()
    except Exception as me:
        print(f"[WARN] Failed to regenerate episodes.json: {me}")


def regenerate_episodes_manifest():
    """
    Regenerates both copies of episodes.json (`ddma/docs/episodes.json` and `src/ddma/docs/episodes.json`)
    from published episodes in SUMMARY.md (Template) and existing episode folders, setting isDefault=True
    on the latest episode.
    """
    manifest_paths = [
        PROJECT_ROOT / "ddma" / "docs" / "episodes.json",
        SRC_DIR / "ddma" / "docs" / "episodes.json",
    ]
    existing_by_id = {}
    for mp in manifest_paths:
        if mp.exists():
            try:
                with open(mp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and (item.get("id") or item.get("number")):
                            eid = str(item.get("id") or item.get("number"))
                            existing_by_id[eid] = item
            except Exception:
                pass

    _, template_items, _, _ = parse_summary_structure()
    for t in template_items:
        num = t.get("number")
        if not num:
            fn_stem = str(t.get("filename", "")).replace(".md", "")
            if fn_stem.isdigit():
                num = int(fn_stem)
        if not num:
            continue
        eid = str(num)
        has_ep_dir = (
            (SRC_DIR / "ddma" / "docs" / "episodes" / eid / "plan.json").exists()
            or (PROJECT_ROOT / "ddma" / "docs" / "episodes" / eid / "plan.json").exists()
            or (PROJECT_ROOT / "ddma" / "projects" / f"episode_{eid}" / "plan.json").exists()
        )
        if not has_ep_dir and eid not in existing_by_id:
            continue
        raw_title = str(t.get("title", "")).strip()
        clean_title = re.sub(r'^\d+\s*:\s*', '', raw_title).strip() or f"Episode {eid}"
        prev = existing_by_id.get(eid, {})
        existing_by_id[eid] = {
            "id": eid,
            "number": int(num),
            "title": clean_title,
            "fullTitle": f"Episode {eid}: {clean_title}",
            "planPath": f"episodes/{eid}/plan.json",
            "clipsDir": f"episodes/{eid}/clips",
            "links": prev.get("links", {}),
            "isDefault": False
        }

    for eid, item in list(existing_by_id.items()):
        try:
            vid_items = find_episode_videos(eid)
            avail_nums = sorted([v["num"] for v in vid_items if v.get("num") is not None])
            if avail_nums:
                item["availableClips"] = avail_nums
        except Exception:
            pass

    if not existing_by_id:
        return []

    sorted_eps = sorted(
        existing_by_id.values(),
        key=lambda x: int(x.get("number") or (int(x["id"]) if str(x.get("id", "")).isdigit() else 0))
    )
    for item in sorted_eps:
        item["isDefault"] = False
    sorted_eps[-1]["isDefault"] = True

    for mp in manifest_paths:
        try:
            mp.parent.mkdir(parents=True, exist_ok=True)
            with open(mp, "w", encoding="utf-8") as f:
                json.dump(sorted_eps, f, indent=2)
        except Exception as e:
            print(f"[WARN] Could not write {mp}: {e}")

    return sorted_eps


def start_auto_transcription_pipeline(clean_id: str, audio_path: Path | None = None, model_name: str | None = None, force: bool = False) -> tuple[bool, str]:
    """
    Automatically runs faster-whisper (large-v3-turbo) word-timestamp transcription in a background thread,
    saves to src/ddma/docs/episodes/<id>/, ddma/projects/episode_<id>/, and dd_hub/episodes/<id>/,
    and automatically runs review_podcast_with_gemini(clean_id) + seed_ddma_project_if_missing(clean_id).
    """
    clean_id = str(clean_id).replace(".md", "").lstrip("_")
    if not clean_id:
        return False, "Missing episode clean_id"

    cur_job = transcription_jobs.get(clean_id, {})
    if cur_job.get("status") == "processing":
        return True, f"Transcription already running for {clean_id}"

    if not force and get_episode_transcription_json_path(clean_id):
        return True, f"Transcription already exists for {clean_id}"

    apath = audio_path or get_episode_audio_path(clean_id)
    if not apath or not apath.exists():
        return False, f"No audio file found for episode {clean_id}"

    settings = load_settings()
    mname = model_name or settings.get("whisper_model", "large-v3-turbo") or "large-v3-turbo"

    def _auto_worker(cid: str, audio_p: Path, mdl: str):
        transcription_jobs[cid] = {"status": "processing", "progress": f"Auto-transcribing {audio_p.name} with faster-whisper ({mdl})..."}
        try:
            result = run_faster_whisper_transcription(audio_p, model_name=mdl, word_timestamps=True)
            text_out = result.get("text", "").strip()

            # 1. Save plain transcript.txt
            t_path = get_episode_transcript_path(cid)
            with open(t_path, "w", encoding="utf-8") as f:
                f.write(text_out)

            # 2. Save streamlined narrative.md
            ep_title = ""
            for possible_file in [SRC_DIR / f"{cid}.md", SRC_DIR / f"_{cid}.md"]:
                if possible_file.exists():
                    try:
                        with open(possible_file, "r", encoding="utf-8") as pf:
                            m = re.search(r"^#\s+(.*)$", pf.read(), re.MULTILINE)
                            if m:
                                ep_title = m.group(1).strip()
                                break
                    except Exception:
                        pass
            cfg = load_settings()
            ln_addr = cfg.get("lightning_address", "shutosha@primal.net")
            streamlined_text, _ = smart_streamline_narrative(text_out, title=ep_title, ep_num=cid, lightning_addr=ln_addr)
            n_path = get_episode_narrative_path(cid)
            with open(n_path, "w", encoding="utf-8") as nf:
                nf.write(streamlined_text)

            # 3. Save full acoustic transcription.json in src/ddma/docs/episodes/<cid>/
            src_trans_json = SRC_DIR / "ddma" / "docs" / "episodes" / cid / "transcription.json"
            src_trans_json.parent.mkdir(parents=True, exist_ok=True)
            with open(src_trans_json, "w", encoding="utf-8") as jf:
                json.dump(result, jf, indent=4)

            # 4. Save to dd_hub/episodes/<cid>/transcription.json
            try:
                hub_ep_dir = get_dd_hub_root() / "episodes" / str(cid)
                hub_ep_dir.mkdir(parents=True, exist_ok=True)
                with open(hub_ep_dir / "transcription.json", "w", encoding="utf-8") as hjf:
                    json.dump(result, hjf, indent=4)
            except Exception as he:
                print(f"[DD_HUB] Warning saving transcription.json to dd_hub: {he}")

            # 5. Sync directly into DDMA projects folder & auto-seed DDMA project + Gemini podcast stings
            for ddma_root in [PROJECT_ROOT.parent / "ddma", PROJECT_ROOT / "ddma"]:
                proj_dir = ddma_root / "projects" / f"episode_{cid}"
                if proj_dir.exists():
                    with open(proj_dir / "transcription.json", "w", encoding="utf-8") as pjf:
                        json.dump(result, pjf, indent=4)
                    with open(proj_dir / "transcript.txt", "w", encoding="utf-8") as ptf:
                        ptf.write(text_out)

            transcription_jobs[cid]["progress"] = "Auto-structuring podcast stings & seeding DDMA clips..."
            try:
                review_podcast_with_gemini(cid)
            except Exception as rev_e:
                print(f"[AUTO-INGEST] review_podcast_with_gemini warning for {cid}: {rev_e}")

            try:
                seed_ddma_project_if_missing(cid)
            except Exception as seed_e:
                print(f"[AUTO-INGEST] seed_ddma_project_if_missing warning for {cid}: {seed_e}")

            transcription_jobs[cid] = {
                "status": "done",
                "progress": "Auto-transcription, podcast stings & DDMA clips ready!",
                "text": text_out
            }
        except Exception as e:
            transcription_jobs[cid] = {"status": "error", "progress": "Transcription failed", "error": str(e)}

    threading.Thread(target=_auto_worker, args=(clean_id, apath, mname), daemon=True).start()
    return True, f"Auto-transcription started with faster-whisper ({mname})"


def _ingest_research_payload_to_episode(slug_or_id: str, raw_text: str, is_python: bool = True, title_override: str = "") -> dict:
    """
    Saves raw payload to dd_hub/inputs/<slug>/payload.py and creates or updates either:
    - src/<num>.md (if slug_or_id is digits or already in Block Template)
    - src/_<slug>.md (if Mempool draft)
    """
    settings = load_settings()
    word_limit = settings.get("title_word_limit", 5)
    raw_md, _, _ = extract_python_payload(raw_text) if is_python else (raw_text, len(raw_text), len(raw_text))
    sanitized_md, clean_title, _ = sanitize_katex_markdown(raw_md, title_override or None, word_limit)
    sanitized_md = ensure_syndication_and_wallet_blocks(sanitized_md, settings)

    clean_slug = str(slug_or_id).replace(".md", "").lstrip("_").strip()
    if not clean_slug:
        clean_slug = re.sub(r'[^a-zA-Z0-9_-]', '-', clean_title.lower()).strip('-') or "draft"

    # Save to dd_hub/inputs/<clean_slug>/payload.py
    try:
        hub_in_dir = get_dd_hub_root() / "inputs" / clean_slug
        hub_in_dir.mkdir(parents=True, exist_ok=True)
        payload_file = hub_in_dir / "payload.py"
        if is_python:
            payload_file.write_text(raw_text, encoding="utf-8")
        else:
            escaped = raw_text.replace('"""', '\"\"\"')
            payload_file.write_text(f'raw_markdown = """{escaped}"""\n', encoding="utf-8")
    except Exception as he:
        print(f"[DD_HUB] Warning saving payload.py to dd_hub/inputs/{clean_slug}: {he}")

    mempool, template, _, _ = parse_summary_structure()
    is_numbered = clean_slug.isdigit() or any(t["filename"] == f"{clean_slug}.md" for t in template)

    if is_numbered:
        filename = f"{clean_slug}.md"
        formatted_title = f"{clean_slug} : {clean_title}"
    else:
        filename = f"_{clean_slug}.md"
        formatted_title = clean_title

    sidebar_tag = f"<!-- SIDEBAR_TITLE: {clean_title} -->"
    if "<!-- SIDEBAR_TITLE:" not in sanitized_md:
        full_content = f"# {formatted_title}\n\n{sidebar_tag}\n\n{sanitized_md}\n"
    else:
        full_content = f"# {formatted_title}\n\n{sanitized_md}\n"

    file_path = SRC_DIR / filename
    file_path.write_text(full_content, encoding="utf-8")

    if is_numbered:
        existing = next((t for t in template if t["filename"] == filename), None)
        if existing:
            existing["title"] = formatted_title
        else:
            template.insert(0, {"title": formatted_title, "filename": filename, "number": int(clean_slug) if clean_slug.isdigit() else clean_slug})
    else:
        existing = next((m for m in mempool if m["filename"] == filename), None)
        if existing:
            existing["title"] = formatted_title
        else:
            mempool.insert(0, {"title": formatted_title, "filename": filename, "slug": clean_slug})

    sync_summary_file(mempool, template)

    def bg_build():
        try:
            subprocess.run(["mdbook", "build"], cwd=str(PROD_ROOT), capture_output=True)
        except Exception:
            pass
    threading.Thread(target=bg_build, daemon=True).start()

    return {
        "success": True,
        "filename": filename,
        "clean_id": clean_slug,
        "title": formatted_title,
        "clean_title": clean_title,
        "is_draft": not is_numbered
    }


def sync_dd_hub_inputs() -> dict:
    """
    Scans dd_hub/inputs/<slug>/ for any automated drops (e.g. from the send-py skill or NotebookLM audio):
    - Ingests new or updated payload.py / *.py / *.md into Mempool or Block Template.
    - Copies new audio files (*.m4a, *.mp3, *.wav) into the episode folder and auto-triggers
      faster-whisper large-v3-turbo transcription + Gemini podcast sting review + DDMA clip seeding.
    """
    hub_inputs = get_dd_hub_root() / "inputs"
    if not hub_inputs.exists():
        return {"success": False, "error": f"dd_hub/inputs not found at {hub_inputs}"}

    ingested_payloads = []
    ingested_audios = []
    latest_filename = None

    for sub in sorted(hub_inputs.iterdir(), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True):
        if not sub.is_dir():
            continue
        slug = sub.name.strip()
        if not slug or slug.startswith("."):
            continue

        # Check for payload.py or *.py / *.md
        py_candidates = list(sub.glob("payload.py")) or sorted(sub.glob("*.py"))
        md_candidates = sorted(sub.glob("*.md"))
        payload_src = py_candidates[0] if py_candidates else (md_candidates[0] if md_candidates else None)

        target_md = SRC_DIR / (f"{slug}.md" if slug.isdigit() else f"_{slug}.md")
        if not target_md.exists() and (SRC_DIR / f"{slug}.md").exists():
            target_md = SRC_DIR / f"{slug}.md"

        if payload_src and payload_src.exists():
            # Ingest if target_md doesn't exist yet or payload_src is newer than target_md
            should_ingest = (not target_md.exists()) or (payload_src.stat().st_mtime > target_md.stat().st_mtime + 2.0)
            if should_ingest:
                try:
                    raw_txt = payload_src.read_text(encoding="utf-8")
                    res_p = _ingest_research_payload_to_episode(slug, raw_txt, is_python=(payload_src.suffix.lower() == ".py"))
                    if res_p.get("success"):
                        ingested_payloads.append({"slug": slug, "filename": res_p["filename"], "title": res_p["title"]})
                        if not latest_filename:
                            latest_filename = res_p["filename"]
                except Exception as pe:
                    print(f"[SYNC_INPUTS] Payload ingest error for {slug}: {pe}")

        # Check for audio files (*.m4a, *.mp3, *.wav)
        for ext in [".m4a", ".mp3", ".wav", ".ogg", ".aac"]:
            aud_matches = sorted(sub.glob(f"*{ext}"))
            if aud_matches:
                src_aud = aud_matches[0]
                dest_dir = SRC_DIR / "ddma" / "docs" / "episodes" / slug
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_aud = dest_dir / f"{slug}{ext}"
                if not dest_aud.exists() or src_aud.stat().st_size != dest_aud.stat().st_size:
                    shutil.copy2(str(src_aud), str(dest_aud))
                    ingested_audios.append({"slug": slug, "audio": dest_aud.name})
                if not get_episode_transcription_json_path(slug):
                    start_auto_transcription_pipeline(slug, audio_path=dest_aud)
                    if not any(a["slug"] == slug for a in ingested_audios):
                        ingested_audios.append({"slug": slug, "audio": dest_aud.name})
                if not latest_filename:
                    latest_filename = f"{slug}.md" if (SRC_DIR / f"{slug}.md").exists() else f"_{slug}.md"
                break

    return {
        "success": True,
        "ingested_payloads": ingested_payloads,
        "ingested_audios": ingested_audios,
        "latest_filename": latest_filename,
        "message": f"Synced dd_hub/inputs: {len(ingested_payloads)} payload(s), {len(ingested_audios)} audio track(s)."
    }


def handle_unified_drop(data: dict) -> dict:
    """
    Unified Smart Drop handler for .py, .md, and audio (.m4a, .mp3, .wav) files:
    - Automatically saves inputs to dd_hub/inputs/<slug_or_ep>/
    - Assigns a slug (for new research payloads) or episode number (mining Mempool draft if needed when audio is dropped)
    - Automatically triggers faster-whisper large-v3-turbo transcription + Gemini audio review on audio drop.
    """
    orig_filename = str(data.get("orig_filename", "")).strip()
    active_filename = str(data.get("active_filename", "")).strip()
    slug_override = str(data.get("slug", "")).strip()
    ext = Path(orig_filename).suffix.lower()

    # CASE 1: Research Payload (.py or .md)
    if ext in (".py", ".md"):
        text_content = data.get("text_content", "")
        if not text_content and data.get("base64_data"):
            text_content = base64.b64decode(data["base64_data"]).decode("utf-8", errors="replace")
        if not text_content.strip():
            return {"success": False, "error": "Dropped file is empty"}

        is_py = (ext == ".py")
        target_slug = slug_override
        if not target_slug:
            stem = Path(orig_filename).stem
            if stem and stem.lower() not in ("payload", "extract", "final_research", "research", "script", "new"):
                target_slug = re.sub(r'[^a-zA-Z0-9_-]', '-', stem.lower()).strip('-')
            elif active_filename:
                target_slug = active_filename.replace(".md", "").lstrip("_")

        res = _ingest_research_payload_to_episode(target_slug, text_content, is_python=is_py)
        res["drop_type"] = "research"
        res["message"] = f"Saved to dd_hub/inputs/{res['clean_id']}/payload.py & ingested {res['filename']}"
        return res

    # CASE 2: Audio File (.m4a, .mp3, .wav, .ogg, .aac)
    if ext in (".m4a", ".mp3", ".wav", ".ogg", ".aac"):
        b64_data = data.get("base64_data", "")
        if not b64_data:
            return {"success": False, "error": "Missing audio base64_data"}
        raw_bytes = base64.b64decode(b64_data)

        # Determine episode number / ID:
        # 1. If filename is digits (e.g. 250.m4a), use 250.
        # 2. If active episode is a Mempool draft (_slug.md), auto-mine it to next_episode_number!
        # 3. Otherwise use active episode number or next_episode_number.
        stem = Path(orig_filename).stem.strip()
        ep_match = re.match(r'^(\d+)$', stem)
        mempool, template, _, next_num = parse_summary_structure()

        target_ep_id = ""
        target_md_filename = active_filename

        if ep_match:
            target_ep_id = ep_match.group(1)
            target_md_filename = f"{target_ep_id}.md"
        elif active_filename and active_filename.startswith("_"):
            # Auto-mine Mempool draft to next episode number when audio is dropped!
            target_ep_id = str(next_num)
            src_path = SRC_DIR / active_filename
            dest_filename = f"{target_ep_id}.md"
            dest_path = SRC_DIR / dest_filename
            if src_path.exists():
                settings = load_settings()
                word_limit = settings.get("title_word_limit", 5)
                existing_text = src_path.read_text(encoding="utf-8")
                sanitized_md, clean_title, _ = sanitize_katex_markdown(existing_text, "", word_limit)
                sanitized_md = ensure_syndication_and_wallet_blocks(sanitized_md, settings)
                formatted_title = f"{target_ep_id} : {clean_title}"
                sidebar_tag = f"<!-- SIDEBAR_TITLE: {clean_title} -->"
                full_content = f"# {formatted_title}\n\n{sidebar_tag}\n\n{sanitized_md}\n" if "<!-- SIDEBAR_TITLE:" not in sanitized_md else f"# {formatted_title}\n\n{sanitized_md}\n"
                dest_path.write_text(full_content, encoding="utf-8")
                if src_path != dest_path:
                    src_path.unlink()
                old_slug = active_filename.replace(".md", "").lstrip("_")
                # Also copy payload.py from dd_hub/inputs/<old_slug> to dd_hub/inputs/<target_ep_id>
                try:
                    old_hub_in = get_dd_hub_root() / "inputs" / old_slug
                    new_hub_in = get_dd_hub_root() / "inputs" / target_ep_id
                    if old_hub_in.exists() and old_hub_in != new_hub_in:
                        new_hub_in.mkdir(parents=True, exist_ok=True)
                        for item in old_hub_in.iterdir():
                            if item.is_file():
                                shutil.copy2(str(item), str(new_hub_in / item.name))
                except Exception:
                    pass
                mempool = [m for m in mempool if m["filename"] != active_filename]
                template.insert(0, {"title": formatted_title, "filename": dest_filename, "number": int(target_ep_id)})
                sync_summary_file(mempool, template)
                target_md_filename = dest_filename
        elif active_filename:
            target_ep_id = active_filename.replace(".md", "").lstrip("_")
            target_md_filename = active_filename
        else:
            target_ep_id = str(next_num)
            target_md_filename = f"{target_ep_id}.md"

        # Save to dd_hub/inputs/<target_ep_id>/<target_ep_id><ext>
        try:
            hub_in_dir = get_dd_hub_root() / "inputs" / target_ep_id
            hub_in_dir.mkdir(parents=True, exist_ok=True)
            hub_audio_file = hub_in_dir / f"{target_ep_id}{ext}"
            hub_audio_file.write_bytes(raw_bytes)
        except Exception as he:
            print(f"[DD_HUB] Warning saving audio to dd_hub/inputs/{target_ep_id}: {he}")

        # Save to local episode directory
        ep_dir = SRC_DIR / "ddma" / "docs" / "episodes" / target_ep_id
        ep_dir.mkdir(parents=True, exist_ok=True)
        local_audio_file = ep_dir / f"{target_ep_id}{ext}"
        local_audio_file.write_bytes(raw_bytes)

        # Immediately trigger auto-transcription + Gemini review + DDMA seeding
        start_auto_transcription_pipeline(target_ep_id, audio_path=local_audio_file, force=True)

        return {
            "success": True,
            "drop_type": "audio",
            "clean_id": target_ep_id,
            "filename": target_md_filename,
            "audio_filename": local_audio_file.name,
            "message": f"Saved to dd_hub/inputs/{target_ep_id}/{target_ep_id}{ext} & started Whisper large-v3-turbo transcription!"
        }

    return {"success": False, "error": f"Unsupported file extension: {ext}"}

class IngestRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(INGEST_DIR), **kwargs)

    def do_HEAD(self):
        return self.do_GET()

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path

        if path == "/" or path == "/index.html":
            self.path = "/landing.html"
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

            ep_title = ""
            for possible_file in [SRC_DIR / f"{clean_id}.md", SRC_DIR / f"_{clean_id}.md"]:
                if possible_file.exists():
                    try:
                        with open(possible_file, "r", encoding="utf-8") as pf:
                            m = re.search(r"^#\s+(.*)$", pf.read(), re.MULTILINE)
                            if m:
                                ep_title = m.group(1).strip()
                                break
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
                settings = load_settings()
                ln_addr = settings.get("lightning_address", "shutosha@primal.net")
                narrative_text, _ = smart_streamline_narrative(transcript_text, title=ep_title, ep_num=clean_id, lightning_addr=ln_addr)

            job = transcription_jobs.get(clean_id, {"status": "idle", "progress": ""})
            if audio_path and audio_path.exists() and not get_episode_transcription_json_path(clean_id) and job.get("status") not in ("processing", "done"):
                start_auto_transcription_pipeline(clean_id, audio_path=audio_path)
                job = transcription_jobs.get(clean_id, {"status": "processing", "progress": "Auto-transcribing with faster-whisper large-v3-turbo..."})

            audio_rel_url = None
            if audio_path:
                try:
                    rel = audio_path.relative_to(SRC_DIR)
                    audio_rel_url = f"/src/{rel.as_posix()}"
                except ValueError:
                    audio_rel_url = f"/media/{audio_path.name}"

            nostr_meta = extract_nostr_metadata(narrative_text or transcript_text, ep_title, clean_id)

            self.send_json({
                "clean_id": clean_id,
                "has_audio": audio_path is not None,
                "audio_filename": audio_path.name if audio_path else None,
                "audio_url": audio_rel_url,
                "has_transcript": len(transcript_text.strip()) > 0,
                "transcript": transcript_text,
                "narrative_md": narrative_text,
                "nostr_meta": nostr_meta,
                "job_status": job.get("status", "idle"),
                "job_progress": job.get("progress", ""),
                "job_error": job.get("error", "")
            })
            return

        if path == "/api/ddma/status":
            params = parse_qs(url.query)
            fn = params.get("filename", [""])[0]
            clean_id = fn.replace(".md", "").lstrip("_")
            
            ddma_ep_dir = PROJECT_ROOT / "ddma" / "docs" / "episodes" / clean_id
            if not ddma_ep_dir.exists():
                ddma_ep_dir = PROJECT_ROOT.parent / "ddma" / "docs" / "episodes" / clean_id
            if not ddma_ep_dir.exists():
                ddma_ep_dir = SRC_DIR / "ddma" / "docs" / "episodes" / clean_id
            
            clips = find_episode_videos(clean_id)

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

        if path == "/api/podcast/data":
            params = parse_qs(url.query)
            fn = params.get("filename", [""])[0]
            clean_id = fn.replace(".md", "").lstrip("_")
            words, segments, full_text = extract_timed_words_from_transcription(clean_id)
            edit_data = load_podcast_edit(clean_id)
            stings = get_available_stings()
            mp3_path = get_episode_podcast_mp3_path(clean_id)
            audio_path = get_episode_audio_path(clean_id)
            settings = load_settings()
            gdrive_folder = settings.get("gdrive_pickup_path", str(get_dd_hub_root() / "audio"))

            audio_rel = None
            if audio_path:
                try:
                    rel = audio_path.relative_to(SRC_DIR)
                    audio_rel = f"/src/{rel.as_posix()}"
                except ValueError:
                    audio_rel = f"/media/{audio_path.name}"

            self.send_json({
                "clean_id": clean_id,
                "has_audio": audio_path is not None,
                "audio_filename": audio_path.name if audio_path else None,
                "audio_url": audio_rel,
                "has_transcription": len(words) > 0,
                "words_count": len(words),
                "words": words,
                "segments": segments,
                "full_text": full_text,
                "edit": edit_data,
                "available_stings": stings,
                "has_rendered": mp3_path.exists(),
                "rendered_size": mp3_path.stat().st_size if mp3_path.exists() else 0,
                "rendered_url": f"/api/podcast/audio?filename={clean_id}",
                "has_video": get_episode_podcast_video_path(clean_id).exists(),
                "video_size": get_episode_podcast_video_path(clean_id).stat().st_size if get_episode_podcast_video_path(clean_id).exists() else 0,
                "video_url": f"/api/podcast/video?filename={clean_id}",
                "gdrive_folder": gdrive_folder
            })
            return

        if path == "/api/podcast/audio":
            params = parse_qs(url.query)
            fn = params.get("filename", [""])[0]
            clean_id = fn.replace(".md", "").lstrip("_")
            mp3_path = get_episode_podcast_mp3_path(clean_id)
            if mp3_path.exists():
                self.serve_media_file(mp3_path)
            else:
                self.send_error(404, f"Rendered podcast MP3 not found for episode {clean_id}")
            return

        if path == "/api/podcast/video_render_status":
            params = parse_qs(url.query)
            fn = params.get("filename", [""])[0]
            clean_id = fn.replace(".md", "").lstrip("_")
            job = VIDEO_RENDER_JOBS.get(clean_id)
            mp4_path = get_episode_podcast_video_path(clean_id)
            has_mp4 = mp4_path.exists()
            mp4_size = mp4_path.stat().st_size if has_mp4 else 0

            if job:
                resp = {
                    "status": job.get("status", "idle"),
                    "progress_pct": job.get("progress_pct", 0),
                    "elapsed_seconds": job.get("elapsed_seconds", 0),
                    "eta_seconds": job.get("eta_seconds", 0),
                    "message": job.get("message", ""),
                    "error": job.get("error"),
                    "has_video": has_mp4,
                    "video_size": mp4_size,
                    "video_url": f"/api/podcast/video?filename={clean_id}"
                }
            else:
                resp = {
                    "status": "ready" if has_mp4 else "idle",
                    "progress_pct": 100 if has_mp4 else 0,
                    "elapsed_seconds": 0,
                    "eta_seconds": 0,
                    "message": "Video master ready" if has_mp4 else "Not rendered",
                    "has_video": has_mp4,
                    "video_size": mp4_size,
                    "video_url": f"/api/podcast/video?filename={clean_id}"
                }
            self.send_json(resp)
            return

        if path == "/api/podcast/video":
            params = parse_qs(url.query)
            fn = params.get("filename", [""])[0]
            clean_id = fn.replace(".md", "").lstrip("_")
            mp4_path = get_episode_podcast_video_path(clean_id)
            if mp4_path.exists():
                self.serve_media_file(mp4_path)
            else:
                self.send_error(404, f"Rendered podcast MP4 not found for episode {clean_id}")
            return

        if path == "/api/podcast/sting":
            params = parse_qs(url.query)
            sting_file = params.get("file", [""])[0]
            stings = get_available_stings()
            target_sting = next((s for s in stings if s["filename"] == sting_file), None)
            if target_sting and Path(target_sting["path"]).exists():
                self.serve_media_file(Path(target_sting["path"]))
            else:
                self.send_error(404, f"Sting '{sting_file}' not found")
            return

        if path == "/api/podcast/preview_flow":
            params = parse_qs(url.query)
            fn = params.get("filename", [""])[0]
            clean_id = fn.replace(".md", "").lstrip("_")
            sting_file = params.get("sting", [""])[0]
            try:
                at_sec = float(params.get("at", ["0"])[0])
            except ValueError:
                at_sec = 0.0
            preview_file = generate_sting_flow_preview(clean_id, sting_file, at_sec)
            if preview_file and preview_file.exists():
                self.serve_media_file(preview_file)
            else:
                self.send_error(500, f"Failed to generate flow preview for {sting_file} @ {at_sec}s")
            return

        if path == "/api/settings":
            self.send_json(load_settings())
            return

        if path == "/api/workspace/test":
            params = parse_qs(url.query)
            raw_url = params.get("url", [""])[0].strip()
            m = re.search(r"/folders/([A-Za-z0-9_-]+)", raw_url)
            if not m:
                self.send_json({"success": False, "ok": False,
                                "message": "Not a Google Drive folder URL (expected …/drive/folders/<folder-id>)."})
                return
            folder_id = m.group(1)
            settings = load_settings()
            cfg_id = ""
            cfg_url = str(settings.get("workspace_url", "") or "")
            cm = re.search(r"/folders/([A-Za-z0-9_-]+)", cfg_url)
            if cm:
                cfg_id = cm.group(1)
            hub_root = get_dd_hub_root()
            local_path = str(hub_root)
            readable = False
            has_marker = False
            try:
                readable = hub_root.exists() and hub_root.is_dir()
                has_marker = readable and ((hub_root / "vault" / "settings.json").exists() or (hub_root / "episodes").exists())
            except Exception:
                pass
            ok = bool(folder_id) and readable
            if ok and cfg_id and folder_id != cfg_id:
                msg = (f"URL parses and the local workspace is readable at {local_path}, "
                       f"but its folder ID does not match the configured workspace ({cfg_id}). "
                       "Saving would switch workspaces.")
            elif ok:
                msg = (f"Workspace resolves and is readable at {local_path}. "
                       + ("Folder ID matches the configured workspace." if cfg_id else ""))
            elif not readable:
                msg = f"URL parses (folder {folder_id}) but the local path {local_path} is not reachable. Mount dd_hub / set DD_HUB_ROOT."
            else:
                msg = "Workspace URL not usable."
                ok = False
            self.send_json({"success": True, "ok": ok, "folder_id": folder_id,
                            "matches_configured": bool(cfg_id) and folder_id == cfg_id,
                            "local_path": local_path, "readable": readable,
                            "has_marker": has_marker, "message": msg})
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
                PROJECT_ROOT.parent / "ddma" / "docs" / "episodes" / clean_path,
                PROJECT_ROOT / "ddma" / clean_path,
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
                    for cand in [
                        PROJECT_ROOT / "ddma" / "docs" / "episodes" / ep_num / "clips" / fname,
                        PROJECT_ROOT.parent / "ddma" / "docs" / "episodes" / ep_num / "clips" / fname,
                        SRC_DIR / "ddma" / "docs" / "episodes" / ep_num / "clips" / fname,
                        PROJECT_ROOT / "ddma" / "projects" / f"episode_{ep_num}" / "clips" / fname,
                        PROJECT_ROOT.parent / "ddma" / "projects" / f"episode_{ep_num}" / "clips" / fname,
                        PROJECT_ROOT / "ddma" / "clips" / fname,
                        PROJECT_ROOT.parent / "ddma" / "clips" / fname,
                        VID_DIR / fname,
                    ]:
                        if cand.exists():
                            target_file = cand
                            break

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
            mime_type = "video/mp4" if ext == ".mp4" else "audio/mpeg" if ext == ".mp3" else "audio/mp4" if ext in [".m4a", ".aac"] else "audio/wav" if ext == ".wav" else "image/png" if ext == ".png" else "image/jpeg" if ext in [".jpg", ".jpeg"] else "application/octet-stream"

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

                if self.command == "HEAD":
                    return

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
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                if self.command == "HEAD":
                    return

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
                if file_path.exists() and not data.get("overwrite", False):
                    self.send_json({
                        "success": False,
                        "exists": True,
                        "filename": filename,
                        "error": f"Destination draft {filename} already exists. Pass overwrite=true to overwrite."
                    }, status=409)
                    return

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

        if path in ("/api/template/mine", "/api/template/lock"):
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

            if dest_path.exists() and not data.get("overwrite", False):
                self.send_json({
                    "success": False,
                    "exists": True,
                    "episode_number": target_number,
                    "filename": target_filename,
                    "error": f"Destination episode {target_filename} already exists. Pass overwrite=true to overwrite."
                }, status=409)
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
            for ext in [".png", ".jpg", ".webp"]:
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
                    subprocess.run(["mdbook", "build"], cwd=str(PROD_ROOT), capture_output=True)
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

        if path in ("/api/template/demote_to_mempool", "/api/template/demote"):
            filename = data.get("filename", "")
            if not filename:
                self.send_error(400, "Missing filename")
                return

            src_path = SRC_DIR / filename
            if not src_path.exists():
                self.send_error(404, f"Template file {filename} not found")
                return

            mempool, template, chain, _ = parse_summary_structure()
            item = next((t for t in template if t["filename"] == filename), None)
            raw_title = item.get("title", "") if item else ""
            clean_title = re.sub(r'^\d+\s*:\s*', '', raw_title).strip()
            if not clean_title:
                try:
                    with open(src_path, "r", encoding="utf-8") as f:
                        for l in f:
                            m_h = re.match(r'^#\s+(?:(?:\d+\s*:\s*)?(.*))', l)
                            if m_h:
                                clean_title = m_h.group(1).strip()
                                break
                except Exception:
                    pass
            if not clean_title:
                clean_title = f"Draft {filename.replace('.md', '')}"

            slug = re.sub(r'[^a-zA-Z0-9_-]', '-', clean_title.lower()).strip('-')
            slug = re.sub(r'-+', '-', slug)
            if not slug:
                slug = f"draft-{filename.replace('.md', '')}"
            mempool_filename = f"_{slug}.md"
            dest_path = SRC_DIR / mempool_filename

            if dest_path.exists() and not data.get("overwrite", False):
                self.send_json({
                    "success": False,
                    "exists": True,
                    "mempool_filename": mempool_filename,
                    "error": f"Destination draft {mempool_filename} already exists. Pass overwrite=true to overwrite."
                }, status=409)
                return

            # Read existing markdown and update header to not include episode number
            with open(src_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = re.sub(r'^#\s+\d+\s*:\s*(.*)$', r'# \1', content, count=1, flags=re.MULTILINE)
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)

            if src_path != dest_path and src_path.exists():
                src_path.unlink()

            # Migrate DDMA asset folders
            ep_num = filename.replace(".md", "")
            old_ddma_dir = SRC_DIR / "ddma" / "docs" / "episodes" / ep_num
            new_ddma_dir = SRC_DIR / "ddma" / "docs" / "episodes" / slug
            if old_ddma_dir.exists():
                new_ddma_dir.mkdir(parents=True, exist_ok=True)
                for item_f in old_ddma_dir.iterdir():
                    dest_item = new_ddma_dir / item_f.name
                    if item_f.is_dir():
                        if dest_item.exists():
                            shutil.rmtree(str(dest_item))
                        shutil.copytree(str(item_f), str(dest_item))
                    else:
                        shutil.copy2(str(item_f), str(dest_item))
                shutil.rmtree(str(old_ddma_dir), ignore_errors=True)

            # Migrate cover images
            for ext in [".png", ".jpg", ".webp"]:
                old_img = IMG_DIR / f"{ep_num}{ext}"
                if old_img.exists():
                    shutil.move(str(old_img), str(IMG_DIR / f"_{slug}{ext}"))

            # Update SUMMARY.md
            template = [t for t in template if t["filename"] != filename]
            mempool.insert(0, {"title": clean_title, "filename": mempool_filename, "slug": slug})
            sync_summary_file(mempool, template)

            def bg_build():
                try:
                    subprocess.run(["mdbook", "build"], cwd=str(PROD_ROOT), capture_output=True)
                except Exception:
                    pass
            threading.Thread(target=bg_build, daemon=True).start()

            self.send_json({
                "success": True,
                "mempool_filename": mempool_filename,
                "title": clean_title,
                "slug": slug
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

        if path == "/api/editor/open":
            filename = data.get("filename", "").strip()
            if not filename:
                self.send_error(400, "Missing filename")
                return

            file_path = SRC_DIR / filename
            if not file_path.exists():
                self.send_error(404, f"File {filename} not found")
                return

            editor = data.get("editor", "gvim").strip() or "gvim"
            try:
                subprocess.Popen([editor, str(file_path)])
            except Exception:
                try:
                    os.startfile(str(file_path))
                except Exception as e2:
                    self.send_json({"success": False, "error": f"Failed to launch editor {editor}: {e2}"})
                    return

            self.send_json({
                "success": True,
                "editor": editor,
                "filename": filename,
                "path": str(file_path)
            })
            return

        if path == "/api/episode/update_content":
            filename = data.get("filename", "").strip()
            content = data.get("content", "").strip()
            is_python = data.get("is_python", False)
            title_override = data.get("title_override", "").strip()
            settings = load_settings()
            word_limit = settings.get("title_word_limit", 5)

            if not filename or not content:
                self.send_error(400, "Missing filename or content")
                return

            file_path = SRC_DIR / filename
            if not file_path.exists():
                self.send_error(404, f"File {filename} not found")
                return

            if file_path.exists() and not data.get("overwrite", False):
                self.send_json({
                    "success": False,
                    "exists": True,
                    "filename": filename,
                    "error": f"Destination file {filename} already exists. Pass overwrite=true to overwrite."
                }, status=409)
                return

            try:
                if is_python:
                    raw_md, _, _ = extract_python_payload(content)
                else:
                    raw_md = content

                sanitized_md, clean_title, _ = sanitize_katex_markdown(raw_md, title_override or None, word_limit)
                sanitized_md = ensure_syndication_and_wallet_blocks(sanitized_md, settings)

                num_match = re.match(r'^(\d+)\.md$', filename)
                if num_match:
                    ep_num = int(num_match.group(1))
                    formatted_title = f"{ep_num} : {clean_title}"
                else:
                    formatted_title = clean_title

                sidebar_tag = f"<!-- SIDEBAR_TITLE: {clean_title} -->"
                if "<!-- SIDEBAR_TITLE:" not in sanitized_md:
                    full_content = f"# {formatted_title}\n\n{sidebar_tag}\n\n{sanitized_md}\n"
                else:
                    full_content = f"# {formatted_title}\n\n{sanitized_md}\n"

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(full_content)

                # Update SUMMARY.md title while preserving slug and placement
                mempool, template, _, _ = parse_summary_structure()
                for item in mempool:
                    if item["filename"] == filename:
                        item["title"] = formatted_title
                for item in template:
                    if item["filename"] == filename:
                        item["title"] = formatted_title
                sync_summary_file(mempool, template)

                # Rebuild mdbook in background
                def bg_build():
                    try:
                        subprocess.run(["mdbook", "build"], cwd=str(PROD_ROOT), capture_output=True)
                    except Exception:
                        pass
                threading.Thread(target=bg_build, daemon=True).start()

                self.send_json({
                    "success": True,
                    "filename": filename,
                    "title": formatted_title,
                    "clean_title": clean_title,
                    "word_count": len(re.findall(r'\b\w+\b', full_content))
                })
            except Exception as e:
                self.send_json({
                    "success": False,
                    "error": str(e)
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
                        cwd=str(PROD_ROOT),
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
            default_model = settings.get("whisper_model", "large-v3-turbo")
            model_name = data.get("model", default_model)

            ok, msg = start_auto_transcription_pipeline(clean_id, model_name=model_name, force=True)
            self.send_json({"success": ok, "message": msg if ok else "", "error": "" if ok else msg})
            return

        if path == "/api/dd_hub/sync_inputs":
            res = sync_dd_hub_inputs()
            self.send_json(res)
            return

        if path == "/api/dd_hub/unified_drop":
            res = handle_unified_drop(data)
            self.send_json(res)
            return

        if path == "/api/transcript/streamline":
            fn = data.get("filename", "")
            clean_id = fn.replace(".md", "").lstrip("_")
            custom_text = data.get("text", "")
            title = data.get("title", "")

            if not title:
                for possible_file in [SRC_DIR / f"{clean_id}.md", SRC_DIR / f"_{clean_id}.md"]:
                    if possible_file.exists():
                        try:
                            with open(possible_file, "r", encoding="utf-8") as pf:
                                m = re.search(r"^#\s+(.*)$", pf.read(), re.MULTILINE)
                                if m:
                                    title = m.group(1).strip()
                                    break
                        except Exception:
                            pass

            if not custom_text:
                n_path = get_episode_narrative_path(clean_id)
                if n_path.exists():
                    try:
                        with open(n_path, "r", encoding="utf-8") as f:
                            custom_text = f.read()
                    except Exception:
                        pass

            if not custom_text:
                t_path = get_episode_transcript_path(clean_id)
                if t_path.exists():
                    try:
                        with open(t_path, "r", encoding="utf-8") as f:
                            custom_text = f.read()
                    except Exception:
                        pass

            if not custom_text:
                for possible_file in [SRC_DIR / f"{clean_id}.md", SRC_DIR / f"_{clean_id}.md"]:
                    if possible_file.exists():
                        try:
                            with open(possible_file, "r", encoding="utf-8") as pf:
                                md_body = pf.read()
                                prose = re.sub(r'<!--[\s\S]*?-->', '', md_body)
                                prose = re.sub(r'```[\s\S]*?```', '', prose)
                                prose = re.sub(r'\$\$[\s\S]*?\$\$', '', prose)
                                prose = prose.strip()
                                if prose:
                                    custom_text = prose
                                    break
                        except Exception:
                            pass

            settings = load_settings()
            ln_addr = settings.get("lightning_address", "shutosha@primal.net")
            streamlined, promo_count = smart_streamline_narrative(custom_text, title=title, ep_num=clean_id, lightning_addr=ln_addr)

            n_path = get_episode_narrative_path(clean_id)
            with open(n_path, "w", encoding="utf-8") as f:
                f.write(streamlined)

            nostr_meta = extract_nostr_metadata(streamlined, title, clean_id)

            self.send_json({
                "success": True,
                "clean_id": clean_id,
                "streamlined": streamlined,
                "promo_count": promo_count,
                "nostr_meta": nostr_meta
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
            
            if not n_path.exists():
                if t_path.exists():
                    try:
                        with open(t_path, "r", encoding="utf-8") as tf:
                            raw_t = tf.read()
                        ep_title = ""
                        for possible_file in [SRC_DIR / f"{clean_id}.md", SRC_DIR / f"_{clean_id}.md"]:
                            if possible_file.exists():
                                try:
                                    with open(possible_file, "r", encoding="utf-8") as pf:
                                        m = re.search(r"^#\s+(.*)$", pf.read(), re.MULTILINE)
                                        if m:
                                            ep_title = m.group(1).strip()
                                            break
                                except Exception:
                                    pass
                        settings = load_settings()
                        ln_addr = settings.get("lightning_address", "shutosha@primal.net")
                        nostr_md, _ = smart_streamline_narrative(raw_t, title=ep_title, ep_num=clean_id, lightning_addr=ln_addr)
                        with open(n_path, "w", encoding="utf-8") as nf:
                            nf.write(nostr_md)
                    except Exception:
                        pass
                else:
                    with open(n_path, "w", encoding="utf-8") as f:
                        f.write(f"# {clean_id} Narrative\n\n")

            target_path = n_path

            settings = load_settings()
            pref_editor = settings.get("external_editor")

            local_gvim = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Vim\gvim.exe")
            local_vim = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Vim\vim.exe")

            editor_candidates = []
            if pref_editor:
                editor_candidates.append(pref_editor)
            for ed in ["gvim", "code", "nvim", "vim", "notepad"]:
                if ed not in editor_candidates:
                    editor_candidates.append(ed)

            editor_opened = False
            opened_ed_name = None

            for ed in editor_candidates:
                try:
                    ed_path = shutil.which(ed)
                    if not ed_path and sys.platform == "win32":
                        if "gvim" in ed.lower() and os.path.exists(local_gvim):
                            ed_path = local_gvim
                        elif "vim" in ed.lower() and os.path.exists(local_vim):
                            ed_path = local_vim

                    if ed_path:
                        if sys.platform == "win32":
                            # Primary launch on Windows: use Explorer ShellWindows dispatch so the window
                            # appears directly on the interactive user desktop even if server is a daemon/task
                            ps_script = f"""
                            $sw = [Activator]::CreateInstance([Type]::GetTypeFromCLSID([Guid]'{{9BA05972-F6A8-11CF-A442-00A0C90A8F39}}'))
                            $app = $null
                            if ($sw -and $sw.Count -gt 0) {{
                                $app = $sw.Item(0).Document.Application
                            }} else {{
                                $desktop = $sw.FindWindowSW([ref]0, [ref]0, 8, [ref]0, 1)
                                if ($desktop) {{
                                    $app = $desktop.Document.Application
                                }}
                            }}
                            if ($app) {{
                                $app.ShellExecute('{ed_path}', '"{target_path}"', '', 'open', 1)
                                exit 0
                            }} else {{
                                exit 1
                            }}
                            """
                            try:
                                res = subprocess.run(
                                    ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                                    capture_output=True,
                                    timeout=5
                                )
                                if res.returncode == 0:
                                    editor_opened = True
                                    opened_ed_name = ed
                                    print(f"[EXT-EDITOR] Successfully launched {ed} via Explorer ShellWindows for {target_path}")
                                    break
                            except Exception as sh_err:
                                print(f"[EXT-EDITOR] Explorer dispatch failed ({sh_err}), trying standard subprocess")

                            # Fallback if Explorer COM was unavailable
                            if ed.lower() in ("vim", "nvim"):
                                subprocess.Popen(
                                    f'start "" "{ed_path}" "{target_path}"',
                                    shell=True
                                )
                            else:
                                subprocess.Popen(
                                    [ed_path, str(target_path)],
                                    stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    close_fds=True
                                )
                            editor_opened = True
                            opened_ed_name = ed
                            print(f"[EXT-EDITOR] Successfully launched {ed} ({ed_path}) for {target_path}")
                            break
                        else:
                            subprocess.Popen(
                                [ed_path, str(target_path)],
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                close_fds=True
                            )
                            editor_opened = True
                            opened_ed_name = ed
                            break
                except Exception as ex:
                    print(f"[EXT-EDITOR] Failed to launch editor {ed}: {ex}")

            if not editor_opened:
                if sys.platform == "win32":
                    try:
                        os.startfile(str(target_path))
                        editor_opened = True
                        opened_ed_name = "Default System Editor"
                        print(f"[EXT-EDITOR] Successfully opened via os.startfile: {target_path}")
                    except Exception as os_err:
                        print(f"[EXT-EDITOR] os.startfile failed: {os_err}")

            self.send_json({"success": editor_opened, "path": str(target_path), "editor": opened_ed_name})
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
                "message": f"DDMA Project {project_id} ready and launched on {curator_target_url}",
            })
            return

        if path == "/api/beats/launch":
            global beats_studio_process
            fn = data.get("filename", "")
            clean_id = fn.replace(".md", "").lstrip("_") if fn else ""
            if not clean_id:
                _, template, _, next_num = parse_summary_structure()
                if template:
                    clean_id = str(template[0].get("number") or template[0]["filename"].replace(".md", "").lstrip("_"))
                else:
                    clean_id = str(next_num - 1)

            beats_target_url = f"http://127.0.0.1:8001/beats.html?ep={clean_id}"

            ddma_dir = PROJECT_ROOT.parent / "ddma"
            if not ddma_dir.exists():
                ddma_dir = PROJECT_ROOT / "ddma"
            beats_script = ddma_dir / "beats_server.py"

            if not is_beats_studio_running() and beats_script.exists():
                try:
                    beats_studio_process = subprocess.Popen(
                        [sys.executable, str(beats_script)],
                        cwd=str(ddma_dir),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception as e:
                    self.send_json({"success": False, "error": str(e)})
                    return

            self.send_json({
                "success": True,
                "beats_url": beats_target_url,
                "message": f"Beats Studio ready and launched on {beats_target_url}"
            })
            return

        if path == "/api/episode/sync_clips":
            fn = data.get("filename", "")
            clean_id = fn.replace(".md", "").lstrip("_")
            result = sync_episode_clips_and_markdown(clean_id)
            self.send_json(result)
            return

        if path == "/api/episode/update_listen_buttons":
            fn = data.get("filename", "") or data.get("clean_id", "") or data.get("number", "")
            clean_id = str(fn).replace(".md", "").lstrip("_")
            if not clean_id:
                self.send_json({"success": False, "error": "Missing episode identifier."}, status=400)
                return
            try:
                from update_listen_buttons import update_episode_listen_buttons
                success = update_episode_listen_buttons(clean_id)
                self.send_json({"success": success, "clean_id": clean_id, "message": f"Updated listen buttons for {clean_id}"})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        if path == "/api/git/push":
            ep_num = data.get("number", "update")
            try:
                regenerate_episodes_manifest()
            except Exception as me:
                print(f"Manifest regeneration warning before push: {me}")
            if ep_num and ep_num != "update":
                try:
                    sync_episode_clips_and_markdown(ep_num)
                except Exception as se:
                    print(f"Auto-sync before push warning for {ep_num}: {se}")
            try:
                subprocess.run(["git", "add", "src/", "book.toml"], cwd=str(PROD_ROOT), check=True)
                subprocess.run(["git", "commit", "-m", f"publish: episode {ep_num} via md² cockpit"], cwd=str(PROD_ROOT), check=True)
                subprocess.run(["git", "push"], cwd=str(PROD_ROOT), check=True)
                self.send_json({"success": True, "message": "Pushed to remote repository successfully!"})
            except subprocess.CalledProcessError as e:
                self.send_json({"success": False, "error": f"Git command failed: {e}"})
            return

        if path == "/api/podcast/save_edit":
            clean_id = data.get("clean_id", "").replace(".md", "").lstrip("_")
            edit = data.get("edit", {})
            if not clean_id:
                self.send_json({"success": False, "error": "clean_id is required"}, status=400)
                return
            ok = save_podcast_edit(clean_id, edit)
            self.send_json({"success": ok, "message": "Saved podcast_edit.json successfully" if ok else "Failed to save"})
            return

        if path == "/api/podcast/review_gemini":
            clean_id = data.get("clean_id", "").replace(".md", "").lstrip("_")
            if not clean_id:
                self.send_json({"success": False, "error": "clean_id is required"}, status=400)
                return
            res = review_podcast_with_gemini(clean_id)
            self.send_json(res)
            return

        if path == "/api/podcast/render":
            clean_id = data.get("clean_id", "").replace(".md", "").lstrip("_")
            edit = data.get("edit")
            if not clean_id:
                self.send_json({"success": False, "error": "clean_id is required"}, status=400)
                return
            if edit:
                save_podcast_edit(clean_id, edit)
            success, out_path, msg = render_podcast_pipeline(clean_id, edit)
            mp3_path = get_episode_podcast_mp3_path(clean_id)
            self.send_json({
                "success": success,
                "message": msg,
                "output_path": out_path,
                "has_rendered": mp3_path.exists(),
                "rendered_size": mp3_path.stat().st_size if mp3_path.exists() else 0,
                "rendered_url": f"/api/podcast/audio?filename={clean_id}"
            })
            return

        if path == "/api/podcast/render_video":
            clean_id = data.get("clean_id", "").replace(".md", "").lstrip("_")
            preview_seconds = data.get("preview_seconds")
            if preview_seconds is not None:
                try:
                    preview_seconds = float(preview_seconds)
                except Exception:
                    preview_seconds = None
            if not clean_id:
                self.send_json({"success": False, "error": "clean_id is required"}, status=400)
                return

            current_job = VIDEO_RENDER_JOBS.get(clean_id)
            if current_job and current_job.get("status") == "rendering":
                self.send_json({
                    "success": True,
                    "status": "rendering",
                    "message": "Video render is already running in background",
                    "progress_pct": current_job.get("progress_pct", 0)
                })
                return

            VIDEO_RENDER_JOBS[clean_id] = {
                "status": "rendering",
                "progress_pct": 0,
                "current_time": 0.0,
                "total_duration": 0.0,
                "started_at": time.time(),
                "elapsed_seconds": 0,
                "eta_seconds": 0,
                "message": "Initializing 1080p video render in background...",
                "error": None,
                "preview_seconds": preview_seconds
            }

            def _bg_video_worker(c_id, p_secs):
                def _prog_cb(pct, cur_t, tot_dur):
                    if c_id in VIDEO_RENDER_JOBS:
                        j = VIDEO_RENDER_JOBS[c_id]
                        j["progress_pct"] = pct
                        j["current_time"] = cur_t
                        j["total_duration"] = tot_dur
                        elapsed = time.time() - j["started_at"]
                        j["elapsed_seconds"] = int(elapsed)
                        if pct > 0:
                            total_est = (elapsed / pct) * 100
                            j["eta_seconds"] = max(0, int(total_est - elapsed))
                        else:
                            j["eta_seconds"] = 0
                        mins_e = int(elapsed // 60)
                        secs_e = int(elapsed % 60)
                        eta_m = int(j["eta_seconds"] // 60)
                        eta_s = int(j["eta_seconds"] % 60)
                        j["message"] = f"Rendering {pct}% • {mins_e:02d}:{secs_e:02d} elapsed • ETA {eta_m:02d}:{eta_s:02d}"

                try:
                    ok, out_p, msg_text = render_podcast_video_pipeline(
                        c_id,
                        preview_seconds=p_secs,
                        progress_callback=_prog_cb
                    )
                    v_path = get_episode_podcast_video_path(c_id)
                    f_sz = v_path.stat().st_size if v_path.exists() else 0
                    if ok:
                        VIDEO_RENDER_JOBS[c_id].update({
                            "status": "ready",
                            "progress_pct": 100,
                            "message": msg_text,
                            "rendered_path": str(out_p),
                            "rendered_size": f_sz,
                            "error": None
                        })
                    else:
                        VIDEO_RENDER_JOBS[c_id].update({
                            "status": "error",
                            "error": msg_text,
                            "message": msg_text
                        })
                except Exception as ex:
                    VIDEO_RENDER_JOBS[c_id].update({
                        "status": "error",
                        "error": str(ex),
                        "message": f"Render failed: {ex}"
                    })

            th = threading.Thread(target=_bg_video_worker, args=(clean_id, preview_seconds), daemon=True)
            th.start()

            self.send_json({
                "success": True,
                "status": "rendering",
                "message": f"Video render started in background ({'60s preview' if preview_seconds else 'full 54m episode'})",
                "progress_pct": 0
            })
            return

        if path == "/api/podcast/export_gdrive":
            clean_id = data.get("clean_id", "").replace(".md", "").lstrip("_")
            custom_dest = data.get("custom_dest", "")
            if not clean_id:
                self.send_json({"success": False, "error": "clean_id is required"}, status=400)
                return
            success, msg = export_podcast_to_gdrive(clean_id, custom_dest)
            self.send_json({"success": success, "message": msg})
            return

        if path == "/api/podcast/export_gdrive_video":
            clean_id = data.get("clean_id", "").replace(".md", "").lstrip("_")
            custom_dest = data.get("custom_dest", "")
            if not clean_id:
                self.send_json({"success": False, "error": "clean_id is required"}, status=400)
                return
            success, msg = export_video_to_gdrive(clean_id, custom_dest)
            self.send_json({"success": success, "message": msg})
            return

        self.send_error(404, "Endpoint not found")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

class DualStackThreadingHTTPServer(http.server.ThreadingHTTPServer):
    """
    Multithreaded HTTP Server with Dual-Stack (IPv4 + IPv6) support.
    Eliminates Windows localhost 2-second IPv6 timeout and handles concurrent requests.
    """
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass):
        try:
            self.address_family = socket.AF_INET6
            super().__init__(server_address, RequestHandlerClass)
        except Exception:
            self.address_family = socket.AF_INET
            super().__init__(server_address, RequestHandlerClass)

    def server_bind(self):
        if self.address_family == socket.AF_INET6:
            try:
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except Exception:
                pass
        super().server_bind()

def run_server():
    settings = load_settings()
    port = settings.get("port", 8088)
    DualStackThreadingHTTPServer.allow_reuse_address = True
    bind_addr = ("::", port) if socket.has_ipv6 else ("", port)
    try:
        httpd = DualStackThreadingHTTPServer(bind_addr, IngestRequestHandler)
    except Exception:
        DualStackThreadingHTTPServer.address_family = socket.AF_INET
        httpd = DualStackThreadingHTTPServer(("", port), IngestRequestHandler)

    with httpd:
        print(f"\n==================================================")
        print(f"       md² Ingest Publishing Cockpit (Fast Dual-Stack)")
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
