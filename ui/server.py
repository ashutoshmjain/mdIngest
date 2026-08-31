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
                SRC_DIR / "ddma" / "docs" / "episodes" / clean_path,
                PROJECT_ROOT / "ddma" / "docs" / "episodes" / clean_path,
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
                    if p1.exists(): target_file = p1
                    elif p2.exists(): target_file = p2

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

                if not slug:
                    slug = re.sub(r'[^a-zA-Z0-9_-]', '_', clean_title.lower()).strip('_') or "draft"

                slug = slug.lstrip('_')
                filename = f"_{slug}.md"
                file_path = SRC_DIR / filename
                full_content = f"# {clean_title}\n\n{sanitized_md}\n"

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
            formatted_title = f"{target_number} : {clean_title}"
            full_content = f"# {formatted_title}\n\n{sanitized_md}\n"

            # Write to new episode file
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(full_content)

            # Remove old draft file
            if src_path != dest_path:
                src_path.unlink()

            # Migrate cover images if exist
            old_slug = src_filename.replace(".md", "").lstrip("_")
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
