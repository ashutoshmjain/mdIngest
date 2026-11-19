"""Beats Studio — the longform video workflow as its own app (Phase 5, Item 2).

Separate server process (port 8001) living in ddma/, alongside the engine it
wraps (archetype_studio, render_longform_parallel). Linked from the landing
page; the Beat Studio UI moved here OUT of the cockpit podcast tab.

Hub-first: plan + assets resolve via DD_HUB_ROOT (env DD_HUB_ROOT wins, then
the vault/local settings.json dd_hub_root, then the Windows default with a
LOUD warning). Outputs (patched masters) land where the engine writes them;
the longform master resolves from dd_hub/video/ first.

NOTE — intentional duplicate: the DD_HUB_ROOT resolver below mirrors the one
in scratch/run_curator.py and ingest/server.py on purpose (each server file
stays standalone; same convention as the canonical-audio resolver copy).

Mosaic HARD RULE: this app never starts a Mosaic run on its own. The only
Mosaic trigger here is the explicit double-confirmed Retrigger button, which
forwards to the curator's manual /export-to-mosaic endpoint (the same manual
path as the curator's Mosaic button). No auto-resume, no restore branch.
"""
import http.server
import json
import os
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

DDMA_DIR = Path(__file__).resolve().parent
if str(DDMA_DIR) not in sys.path:
    sys.path.insert(0, str(DDMA_DIR))

PORT = 8001
CURATOR_BASE = "http://127.0.0.1:8000"


def resolve_dd_hub_root():
    """env DD_HUB_ROOT -> settings dd_hub_root -> Windows default + LOUD warning."""
    env = os.environ.get("DD_HUB_ROOT", "").strip()
    if env and Path(env).exists():
        return Path(env)
    for settings_name in ("settings.json",):
        sp = DDMA_DIR / settings_name
        if sp.exists():
            try:
                dd = json.loads(sp.read_text(encoding="utf-8")).get("dd_hub_root", "")
                if dd and Path(dd).exists():
                    return Path(dd)
            except Exception:
                pass
    # Vault copy (private, never in git) as a last structured resort.
    for v in (Path("G:/My Drive/dd_hub/vault/settings.json"),):
        if v.exists():
            try:
                dd = json.loads(v.read_text(encoding="utf-8")).get("dd_hub_root", "")
                if dd and Path(dd).exists():
                    return Path(dd)
            except Exception:
                pass
    fallback = Path(r"G:\My Drive\dd_hub")
    print(f"WARNING: DD_HUB_ROOT unresolved — falling back to {fallback} (may not exist).",
          flush=True)
    return fallback


DD_HUB_ROOT = resolve_dd_hub_root()


def rewrite_beat_urls(ch_data):
    """Point per-beat preview URLs at this server (engine emits cockpit paths)."""
    try:
        for b in ch_data.get("beats", []):
            u = b.get("beat_video_url", "")
            if "/api/podcast/beat_video" in u:
                b["beat_video_url"] = u.replace("/api/podcast/beat_video",
                                                "/api/beats/beat_video")
    except Exception:
        pass
    return ch_data


def find_master_video(clean_id):
    """Locate the longform master MP4, hub-first. Returns Path or None."""
    candidates = [
        DD_HUB_ROOT / "video" / f"podcast_{clean_id}.mp4",
        DDMA_DIR / "clips" / f"{clean_id}-longform-master.mp4",
    ]
    for c in candidates:
        try:
            if c.exists():
                return c
        except Exception:
            pass
    return None


def clean_ep(raw, default="248"):
    return str(raw or default).replace(".md", "").lstrip("_") or default


class BeatsHandler(http.server.BaseHTTPRequestHandler):
    server_version = "BeatsStudio/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[beats] {self.address_string()} {fmt % args}\n")

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, path, mime="text/html"):
        try:
            data = Path(path).read_bytes()
        except Exception:
            self.send_error(404, "Not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", mime + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def serve_media_file(self, file_path: Path):
        """Streams media files with HTTP Range support (ported from ingest server)."""
        try:
            file_size = file_path.stat().st_size
            ext = file_path.suffix.lower()
            mime_type = ("video/mp4" if ext == ".mp4" else "audio/mpeg" if ext == ".mp3"
                         else "application/octet-stream")
            range_header = self.headers.get("Range")
            if range_header and range_header.startswith("bytes="):
                bytes_range = range_header[6:].split("-")
                start = int(bytes_range[0]) if bytes_range[0] else 0
                end = int(bytes_range[1]) if len(bytes_range) > 1 and bytes_range[1] else file_size - 1
                end = min(end, file_size - 1)
                length = end - start + 1
                self.send_response(206)
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                self.send_header("Content-Length", str(length))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                with open(file_path, "rb") as f:
                    f.seek(start)
                    self.wfile.write(f.read(length))
            else:
                self.send_response(200)
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Length", str(file_size))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                with open(file_path, "rb") as f:
                    while True:
                        chunk = f.read(1024 * 256)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            self.send_error(500, str(e))

    # ---------- GET ----------
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        params = urllib.parse.parse_qs(url.query)

        if path in ("/", "/beats.html"):
            self.serve_file(DDMA_DIR / "beats.html")
            return

        if path == "/api/beats/index":
            ep = clean_ep(params.get("ep", ["248"])[0])
            try:
                import importlib
                import archetype_studio
                importlib.reload(archetype_studio)
                idx = archetype_studio.get_longform_timeline_index(ep)
                master = find_master_video(ep)
                idx["has_video"] = bool(master)
                idx["video_url"] = f"/api/beats/video?ep={ep}" if master else ""
                self.send_json(idx)
            except Exception as e:
                self.send_json({"error": str(e)}, status=500)
            return

        if path == "/api/beats/video":
            ep = clean_ep(params.get("ep", ["248"])[0])
            master = find_master_video(ep)
            if master:
                self.serve_media_file(master)
            else:
                self.send_error(404, f"Longform master MP4 not found for episode {ep}")
            return

        if path == "/api/beats/beats":
            ep = clean_ep(params.get("ep", ["248"])[0])
            try:
                clip_num = int(params.get("clip_num", ["1"])[0])
            except ValueError:
                self.send_json({"error": "bad clip_num"}, status=400)
                return
            try:
                import importlib
                import archetype_studio
                importlib.reload(archetype_studio)
                self.send_json(rewrite_beat_urls(
                    archetype_studio.get_longform_chapter_beats(ep, clip_num)))
            except Exception as e:
                self.send_json({"error": str(e)}, status=500)
            return

        if path == "/api/beats/beat_video":
            try:
                clip_num = int(params.get("clip_num", ["1"])[0])
            except ValueError:
                self.send_error(400, "bad clip_num")
                return
            cls_name = params.get("class_name", [""])[0].strip().replace("/", "")
            media_root = (DDMA_DIR.parent / "media" / "videos"
                          / f"clip_{clip_num:02d}_gemini_scenes" / "740p15" / f"{cls_name}.mp4")
            if media_root.exists():
                self.serve_media_file(media_root)
            else:
                self.send_error(404, f"Beat preview not found: {cls_name}")
            return

        if path == "/api/beats/mosaic_status":
            # PURE READ — never starts a pipeline. Reports curator-side state only.
            ep = clean_ep(params.get("ep", ["248"])[0])
            try:
                clip_num = int(params.get("clip_num", ["1"])[0])
            except ValueError:
                self.send_json({"error": "bad clip_num"}, status=400)
                return
            project_id = f"episode_{ep}"
            try:
                with urllib.request.urlopen(
                        f"{CURATOR_BASE}/get-mosaic-status?id={project_id}&num={clip_num}",
                        timeout=10) as r:
                    self.send_json(json.loads(r.read().decode("utf-8")))
            except Exception as e:
                self.send_json({"status": "unknown", "error": f"curator unreachable: {e}"},
                               status=502)
            return

        self.send_error(404, "Endpoint not found")

    # ---------- POST ----------
    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = 0
        data = {}
        if length > 0:
            try:
                data = json.loads(self.rfile.read(length).decode("utf-8"))
            except Exception:
                data = {}

        if path == "/api/beats/update_beat":
            ep = clean_ep(data.get("ep", "248"))
            try:
                clip_num = int(data.get("clip_num", 1))
                beat_index = int(data.get("beat_index", 1))
            except ValueError:
                self.send_json({"success": False, "error": "bad clip_num/beat_index"},
                               status=400)
                return
            try:
                import importlib
                import archetype_studio
                importlib.reload(archetype_studio)
                res = archetype_studio.update_single_scene_with_ai(
                    clip_num=clip_num,
                    beat_index=beat_index,
                    class_name=str(data.get("class_name", "")).strip(),
                    user_directive=str(data.get("user_directive", "")).strip(),
                    spoken_text=str(data.get("spoken_text", "")).strip(),
                    custom_code=data.get("custom_code"),
                    duration=float(data.get("duration", 7.5)),
                )
                ch = archetype_studio.get_longform_chapter_beats(ep, clip_num)
                res["chapter_data"] = rewrite_beat_urls(ch)
                res["beat_video_url"] = (
                    f"/api/beats/beat_video?clip_num={clip_num}"
                    f"&class_name={urllib.parse.quote(str(data.get('class_name', '')))}"
                    f"&t={int(time.time())}")
                self.send_json(res)
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        if path == "/api/beats/patch":
            ep = clean_ep(data.get("ep", "248"))
            try:
                clip_num = int(data.get("clip_num", 1))
            except ValueError:
                self.send_json({"success": False, "error": "bad clip_num"}, status=400)
                return
            try:
                cmd = [sys.executable, "render_longform_parallel.py", "--patch", str(clip_num)]
                res = subprocess.run(cmd, cwd=str(DDMA_DIR), capture_output=True,
                                     text=True, timeout=180)
                if res.returncode == 0:
                    self.send_json({"success": True,
                                    "message": f"Part {clip_num} patched into ep {ep} master."})
                else:
                    err = (res.stderr[-500:] if res.stderr else res.stdout[-500:])
                    self.send_json({"success": False, "error": f"Patch failed: {err}"},
                                   status=500)
            except Exception as ex:
                self.send_json({"success": False, "error": str(ex)}, status=500)
            return

        if path == "/api/beats/mosaic_retry":
            # EXPLICIT-ONLY manual trigger: the page double-confirms before
            # calling this; the server only forwards to the curator's manual
            # /export-to-mosaic endpoint and never spawns a pipeline itself.
            ep = clean_ep(data.get("ep", "248"))
            try:
                clip_num = int(data.get("clip_num", 1))
            except ValueError:
                self.send_json({"success": False, "error": "bad clip_num"}, status=400)
                return
            project_id = f"episode_{ep}"
            body = json.dumps({"directive": str(data.get("directive", "")),
                               "prompt": str(data.get("prompt", ""))}).encode("utf-8")
            req = urllib.request.Request(
                f"{CURATOR_BASE}/export-to-mosaic?id={project_id}&num={clip_num}",
                data=body, headers={"Content-Type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    self.send_json(json.loads(r.read().decode("utf-8")))
            except urllib.error.HTTPError as he:
                try:
                    detail = he.read().decode("utf-8")[:500]
                except Exception:
                    detail = str(he)
                self.send_json({"success": False, "error": f"curator refused: {detail}"},
                               status=he.code)
            except Exception as e:
                self.send_json(
                    {"success": False,
                     "error": f"curator unreachable on :8000 — open DDMA first: {e}"},
                    status=502)
            return

        self.send_error(404, "Endpoint not found")


class DualStackThreadingHTTPServer(http.server.ThreadingHTTPServer):
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


if __name__ == "__main__":
    print(f"[beats] DD_HUB_ROOT = {DD_HUB_ROOT}", flush=True)
    srv = DualStackThreadingHTTPServer(("127.0.0.1", PORT), BeatsHandler)
    print(f"[beats] Beats Studio on http://127.0.0.1:{PORT}/beats.html", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
