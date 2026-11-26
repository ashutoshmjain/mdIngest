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
import shutil
import socket
import threading
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


# ---------- Spec H2 sections 3+4: composite wiring (episode 249 ONLY) ----------
# Design-artifacts fan-out, composite timeline, and retrigger scope live
# here. The push endpoint and gate (Spec H sections 8/9) are UNCHANGED.
# Guardrails: serves episode 249 only (never 250); never starts a Mosaic
# run — no mosaic_retry call exists anywhere in this block; never writes
# plan.json (read-only) or docs/plan.json.
H2_EPISODE = "249"
H2_DESIGN_GROUPS = {}
H2_DESIGN_LOCK = threading.Lock()
H2_DESIGN_SEQ = [0]


def _h2_refused(ep):
    if str(ep) != H2_EPISODE:
        return {"success": False,
                "error": f"H2 wiring serves episode {H2_EPISODE} only "
                         f"(refused ep {ep}; never 250)"}
    return None


def _h2_load_plan_clips():
    """Read-only load of the episode plan (never written by H2 wiring)."""
    return json.loads((DDMA_DIR / "plan.json").read_text(encoding="utf-8"))


def _h2_clip_transcript(clip):
    """The Cutroom clip's transcript: audio as cut (segment texts)."""
    parts = []
    for s in clip.get("segments") or []:
        t = str(s.get("text") or "").strip()
        if t:
            parts.append(t)
    return " ".join(parts)


def _h2_probe_duration(path):
    try:
        if shutil.which("ffprobe") is None:
            return None
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=15)
        if p.returncode == 0 and p.stdout.strip():
            return float(p.stdout.strip())
    except Exception:
        pass
    return None


def _h2_composite_master(ep):
    """The assembled master that feeds the push endpoint and gate (H ss8/9).

    Same resolution as the push path: hub-first master, then the episode
    longform slot. Returns a Path or None — never a fabricated duration."""
    m = find_master_video(ep)
    if m:
        return m
    try:
        import spec_h_composite_longform as spec_h
        dest = spec_h.longform_destination(DD_HUB_ROOT, ep)
        if dest.exists():
            return dest
    except Exception:
        pass
    return None


def _h2_run_design_group(group_id):
    """Background worker: one design call per clip, sequential queue.

    Forwards each clip to the curator's manual Manim path (the same path as
    the existing manim_retrigger button). Never touches Mosaic."""
    import spec_h_composite_longform as spec_h
    grp = H2_DESIGN_GROUPS.get(group_id)
    if not grp:
        return
    try:
        _clips = _h2_load_plan_clips()
    except Exception:
        _clips = []
    _by_num = {}
    for _c in _clips:
        try:
            _by_num[int(_c.get("num"))] = _c
        except Exception:
            pass
    for job in grp["jobs"]:
        with H2_DESIGN_LOCK:
            if grp.get("cancelled"):
                break
            job["status"] = "running"
        try:
            cap = spec_h.validate_clip_captions(
                job["clip"], job.get("body_words") or [], False)
            if not cap["ok"]:
                raise RuntimeError(cap["exception"])
            _pc = _by_num.get(int(job["clip"]), {})
            body = json.dumps(
                {"ep": grp["ep"], "clip_num": job["clip"],
                 "force_regen": True,
                 "transcript": _h2_clip_transcript(_pc) or "",
                 "title": str(_pc.get("title") or ""),
                 "directive": str(job.get("directive") or "")}).encode("utf-8")
            req = urllib.request.Request(
                f"{CURATOR_BASE}/generate-manim-infographic"
                f"?id=episode_{grp['ep']}&num={job['clip']}",
                data=body, headers={"Content-Type": "application/json"},
                method="POST")
            with urllib.request.urlopen(req, timeout=120) as r:
                detail = json.loads(r.read().decode("utf-8"))
            if isinstance(detail, dict) and detail.get("success") is False:
                raise RuntimeError(
                    str(detail.get("error", "curator refused"))[:500])
            with H2_DESIGN_LOCK:
                job["status"] = "done"
                job["detail"] = detail
        except Exception as e:
            with H2_DESIGN_LOCK:
                job["status"] = "failed"
                job["error"] = str(e)[:500]
    with H2_DESIGN_LOCK:
        grp["finished"] = True




def _h2_design_stale_report(grp):
    """Master-stale report for a finished design group (read-only).

    The master is NEVER re-assembled here: design completion only reports
    that the master is stale and a manual re-assemble (Patch / re-assemble
    path) plus re-gate is needed before any push. The push stays manual.
    """
    out = {"design_reports": [], "changed_clips": [], "master_stale": False,
           "reassemble_note": ""}
    try:
        if not grp or not grp.get("finished"):
            return out
        ep = str(grp.get("ep", H2_EPISODE))
        master = _h2_composite_master(ep)
        master_mtime = None
        if master is not None:
            try:
                master_mtime = master.stat().st_mtime
            except Exception:
                master_mtime = None
        for job in grp.get("jobs", []):
            det = job.get("detail") or {}
            for rep in det.get("reports") or (det.get("design") or {}).get("reports") or []:
                out["design_reports"].append({"clip": job.get("clip"), "report": rep})
            if job.get("status") != "done":
                continue
            _local_art = DDMA_DIR / "clips" / ((str(ep) + "-") + (str(job.get("clip")) + "-manim.mp4"))
            try:
                _local_ok = _local_art.exists()
            except Exception:
                _local_ok = False
            art = _local_art if _local_ok else find_clip_media(ep, job.get("clip"))
            try:
                art_mtime = art.stat().st_mtime if art is not None else None
            except Exception:
                art_mtime = None
            if art_mtime is not None and (master_mtime is None or art_mtime > master_mtime):
                out["changed_clips"].append(job.get("clip"))
        if out["changed_clips"] or (grp.get("jobs") and all(
                j.get("status") == "done" for j in grp.get("jobs", [])) and master_mtime is None):
            out["master_stale"] = True
            out["reassemble_note"] = ("Master is stale: clips " + ",".join(
                str(c) for c in out["changed_clips"]) + " have fresh Manim. Re-assemble manually "
                "(Patch / re-assemble path), re-gate, then push manually. Nothing was auto-assembled or pushed.")
    except Exception:
        pass
    return out


def _h2_patch_clip_249(clip_num):
    """Manual-trigger H2 segment re-stitch for one ep-249 clip.

    Rebuilds ONLY that clip composite segment (fresh Manim
    infographic + Mosaic run + strip + karaoke, per the H2
    assembler) and splices it into the 249 master behind a
    duration gate. No auto-assemble: runs only on the manual
    Patch trigger. Returns (ok, message_or_error). Missing
    inputs are a reported refusal, never a substitution.
    """
    try:
        n = int(clip_num)
    except (TypeError, ValueError):
        return False, "bad clip_num"
    try:
        import spec_h2_composite_assembler as _h2a
        plan = json.loads((DDMA_DIR / "projects" / "episode_249" / "plan.json").read_text(encoding="utf-8"))
        clips = plan if isinstance(plan, list) else plan.get("clips", [])
        t_clip = next((c for c in clips if str(c.get("num")) == str(n)), None)
        if t_clip is None:
            return False, "clip " + str(n) + " not in episode_249 plan (refused, never substituted)"
        chrome = DDMA_DIR / "assets" / "chrome_249.png"
        strip = DDMA_DIR / "assets" / "strip_249.mp4"
        if not chrome.exists() or not strip.exists():
            return False, "249 frame assets missing (refused, never substituted)"
        art = DDMA_DIR / "clips" / ("249-" + str(n) + "-infographic.mp4")
        if not art.exists() or art.stat().st_size <= 0:
            return False, "clip " + str(n) + " has no Manim infographic yet (design it first; refused, never substituted)"
        rid = t_clip.get("mosaic_run_id")
        inputs = _h2a.resolve_segment_inputs("249", n, rid, str(art), str(DD_HUB_ROOT), str(chrome), str(strip))
        dur = _h2a.clip_composite_duration(t_clip, "249", str(DD_HUB_ROOT))
        words = [(float(w.get("start", 0)), float(w.get("end", 0)), str(w.get("word", ""))) for w in (t_clip.get("_caption_words") or [])]
        if not words:
            return False, "clip " + str(n) + " has no caption words (refused, never a silent fallback)"
        work = DDMA_DIR / "scratch" / "249-patch"
        work.mkdir(parents=True, exist_ok=True)
        _h2a.write_caption_ass(str(work), n, words, dur)
        seg = work / ("seg_" + str(n) + ".mp4")
        cmd = _h2a.build_segment_cmd("249", n, inputs, dur, str(seg), str(work / ("vf_" + str(n) + ".txt")), total_clips=len(clips))
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(work))
        if r.returncode != 0 or not seg.exists():
            return False, "segment render failed: " + (r.stderr or r.stdout)[-500:]
        master = _h2_composite_master("249")
        if master is None or not master.exists():
            return False, "249 master missing (refused)"
        m_dur = _h2_probe_duration(master)
        t0 = 0.0
        for c in clips:
            if int(c.get("num")) < n:
                t0 += _h2a.clip_composite_duration(c, "249", str(DD_HUB_ROOT))
        seg_dur = _h2_probe_duration(seg) or dur
        t1 = t0 + seg_dur
        parts = []
        if t0 > 0.05:
            head = work / ("head_" + str(n) + ".mp4")
            rh = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(master), "-t", ("%.3f" % t0), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", str(head)], capture_output=True, text=True)
            if rh.returncode != 0:
                return False, "head cut failed"
            parts.append(str(head))
        parts.append(str(seg))
        if m_dur is not None and t1 < m_dur - 0.05:
            tail = work / ("tail_" + str(n) + ".mp4")
            rt = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", ("%.3f" % t1), "-i", str(master), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", str(tail)], capture_output=True, text=True)
            if rt.returncode != 0:
                return False, "tail cut failed"
            parts.append(str(tail))
        lst = work / ("splice_" + str(n) + ".txt")
        _h2a.write_concat_list(parts, str(lst))
        new_master = work / "249-longform-master-new.mp4"
        rc = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(new_master)], capture_output=True, text=True, cwd=str(work))
        if rc.returncode != 0:
            return False, "concat failed: " + (rc.stderr or rc.stdout)[-500:]
        new_dur = _h2_probe_duration(new_master)
        if new_dur is None or m_dur is None or abs(new_dur - m_dur) > 0.10:
            return False, "duration gate failed (master %.3f, rebuilt %.3f; refused)" % (m_dur or -1, new_dur or -1)
        new_master.replace(master)
        return True, "Part " + str(n) + " patched into ep 249 master."
    except Exception as e:
        return False, "patch failed: " + str(e)[:300]
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


def find_clip_media(clean_id, clip_num):
    """Locate clip-level MP4 or audio segment for middle-pane Clip playback (D3)."""
    c = int(clip_num)
    candidates = [
        DD_HUB_ROOT / "episodes" / clean_id / f"{clean_id}-{c}-manim.mp4",
        DD_HUB_ROOT / "episodes" / clean_id / f"{clean_id}-{c}-mosaic.mp4",
        DD_HUB_ROOT / "episodes" / clean_id / f"{clean_id}-{c}.mp4",
        DDMA_DIR / "clips" / f"{clean_id}-{c}-manim.mp4",
        DDMA_DIR / "clips" / f"{clean_id}-{c}-mosaic.mp4",
        DDMA_DIR / "clips" / f"{clean_id}-{c}.mp4",
        DD_HUB_ROOT / "episodes" / clean_id / f"clip_{c}.mp3",
        DDMA_DIR / "clips" / f"clip_{c}.mp3",
    ]
    for p in candidates:
        try:
            if p.exists():
                return p
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
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                with open(file_path, "rb") as f:
                    f.seek(start)
                    self.wfile.write(f.read(length))
            else:
                self.send_response(200)
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Length", str(file_size))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Cache-Control", "no-cache")
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
    STATIC_WHITELIST = {
        "/workspace-link.js": ("workspace-link.js", "application/javascript"),
        "/shared-settings.js": ("shared-settings.js", "application/javascript"),
    }

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        params = urllib.parse.parse_qs(url.query)

        if path in ("/", "/beats.html"):
            self.serve_file(DDMA_DIR / "beats.html")
            return

        if path in self.STATIC_WHITELIST:
            fname, mime = self.STATIC_WHITELIST[path]
            self.serve_file(DDMA_DIR / fname, mime=mime)
            return

        if path == "/api/settings":
            hub_root = resolve_dd_hub_root()
            vault_file = hub_root / "vault" / "settings.json"
            local_file = DDMA_DIR / "settings.json"
            settings_data = {}
            for p in (local_file, vault_file):
                if p.exists():
                    try:
                        settings_data.update(json.loads(p.read_text(encoding="utf-8")))
                    except Exception:
                        pass
            self.send_json(settings_data)
            return

        if path == "/api/beats/episodes":
            try:
                import importlib
                import archetype_studio
                importlib.reload(archetype_studio)
                self.send_json({"episodes": archetype_studio.list_workspace_episodes()})
            except Exception as e:
                self.send_json({"episodes": [], "error": str(e)}, status=500)
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

        if path == "/api/beats/clip_media":
            ep = clean_ep(params.get("ep", ["248"])[0])
            try:
                clip_num = int(params.get("clip_num", ["1"])[0])
            except ValueError:
                self.send_error(400, "bad clip_num")
                return
            clip_p = find_clip_media(ep, clip_num)
            if clip_p:
                self.serve_media_file(clip_p)
            else:
                self.send_error(404, f"Clip media not found for ep {ep} clip {clip_num}")
            return

        if path == "/api/beats/personal/list":
            q = params.get("q", [""])[0]
            try:
                import importlib
                import archetype_studio
                importlib.reload(archetype_studio)
                self.send_json({"beats": archetype_studio.list_personal_beats(q)})
            except Exception as e:
                self.send_json({"beats": [], "error": str(e)}, status=500)
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

        if path == "/api/beats/storyboard":
            # Read-only: H2 clip storyboard for the Manim panel (design
            # source of truth: title / equation-or-anchor / scenes).
            # No runs, no writes, no substitutions. Episode 249 only.
            ep = clean_ep(params.get("ep", ["248"])[0])
            if ep != "249":
                self.send_json({"success": False,
                                "error": "storyboard serves episode 249 only"},
                               status=400)
                return
            try:
                clip_num = int(params.get("clip_num", ["1"])[0])
            except ValueError:
                self.send_json({"success": False, "error": "bad clip_num"},
                               status=400)
                return
            sb_path = (DDMA_DIR / "projects" / "episode_249" / "storyboards"
                       / f"clip_{clip_num}_storyboard.json")
            try:
                storyboard = json.loads(sb_path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                self.send_json({"success": False, "error": (
                    f"no storyboard for clip {clip_num} "
                    "(reported exception, never a silent fallback)")},
                    status=404)
                return
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
                return
            # Patch-gate inputs (read-only file times for the stored-state
            # gate: designed-but-unpatched <=> artifact newer than master).
            art_mtime = None
            master_mtime = None
            try:
                _art = (DDMA_DIR / "clips" / f"{ep}-{clip_num}-infographic.mp4")
                if _art.exists():
                    art_mtime = _art.stat().st_mtime
                _master = _h2_composite_master(ep)
                if _master is not None and _master.exists():
                    master_mtime = _master.stat().st_mtime
            except Exception:
                pass
            self.send_json({"success": True, "ep": ep, "clip_num": clip_num,
                            "storyboard": storyboard,
                            "manim_artifact_mtime": art_mtime,
                            "master_mtime": master_mtime})
            return

        if path == "/api/beats/beat_video":
            ep = clean_ep(params.get("ep", ["248"])[0])
            try:
                clip_num = int(params.get("clip_num", ["1"])[0])
            except ValueError:
                self.send_error(400, "bad clip_num")
                return
            cls_name = params.get("class_name", [""])[0].strip().replace("/", "")
            import importlib
            import archetype_studio
            importlib.reload(archetype_studio)
            media_root = Path(archetype_studio._resolve_beat_mp4_path(clip_num, cls_name, ep_num=ep))
            if media_root.exists():
                self.serve_media_file(media_root)
            else:
                self.send_error(404, f"Beat preview not found: {cls_name}")
            return

        if path == "/api/beats/spec_h":
            # Spec H status snapshot: fixed frame, workflow, platform quirks.
            try:
                import spec_h_composite_longform as spec_h
                self.send_json({"spec": spec_h.SPEC_ID,
                                "frame": spec_h.composite_frame_spec(),
                                "workflow": spec_h.WORKFLOW,
                                "platform_quirks": spec_h.PLATFORM_QUIRKS,
                                "oracle": {"size": spec_h.ORACLE_SIZE,
                                           "duration_s": spec_h.ORACLE_DURATION_S}})
            except Exception as e:
                self.send_json({"error": str(e)}, status=500)
            return

        if path == "/api/beats/composite_timeline":
            # Spec H2 s4: the longform preview timeline comes from the
            # composite master itself — probed, never the hardcoded 54:14.
            ep = clean_ep(params.get("ep", ["248"])[0])
            if _h2_refused(ep):
                self.send_json({"success": False, "ep": ep,
                                "error": _h2_refused(ep)["error"]}, status=400)
                return
            master = _h2_composite_master(ep)
            if not master:
                self.send_json({"success": True, "ep": ep, "has_video": False,
                                "video_url": "", "total_duration": None,
                                "fallback_used": False,
                                "note": "No composite master yet — assemble first "
                                        "(never the old hardcoded 54:14 index).",
                                "chapters": []})
                return
            total = _h2_probe_duration(master)
            try:
                clips = _h2_load_plan_clips()
            except Exception as e:
                self.send_json({"success": False,
                                "error": f"plan unreadable: {e}"}, status=500)
                return
            import spec_h2_composite_assembler as spec_h2
            chapters, cursor = [], 0.0
            for c in clips:
                dur, src = spec_h2.clip_composite_duration_explained(
                    c, ep, DD_HUB_ROOT)
                chapters.append({"clip_num": c.get("num"),
                                 "title": c.get("title", f"Part {c.get('num')}"),
                                 "start": round(cursor, 3),
                                 "end": round(cursor + dur, 3),
                                 "duration": round(dur, 3),
                                 "source": src})
                cursor += dur
            self.send_json({"success": True, "ep": ep, "has_video": True,
                            "video_url": f"/api/beats/video?ep={ep}",
                            "total_duration": total,
                            "master": str(master),
                            "fallback_used": False,
                            "chapters": chapters})
            return

        if path == "/api/beats/design_status":
            # Spec H2 s3: per-clip progress; only exceptions are reported.
            group_id = params.get("group", [""])[0]
            with H2_DESIGN_LOCK:
                grp = H2_DESIGN_GROUPS.get(group_id)
                def _job_snap(j):
                    out = {k: j[k] for k in ("clip", "status", "error")
                           if k in j}
                    out["directive"] = str(j.get("directive") or "")
                    try:
                        _det = j.get("detail") or {}
                        _des = _det.get("design") or {}
                        out["directive_report"] = str(
                            _des.get("directive_report") or "")
                    except Exception:
                        out["directive_report"] = ""
                    return out
                snap = ({"ep": grp["ep"], "finished": grp["finished"],
                         "jobs": [_job_snap(j) for j in grp["jobs"]]}
                        if grp else None)
            if not snap:
                self.send_json({"success": False,
                                "error": "unknown design group"}, status=404)
                return
            stale_info = _h2_design_stale_report(grp)
            self.send_json({"success": True, "group": group_id, **snap,
                            "exceptions": [x for x in snap["jobs"]
                                           if x["status"] == "failed"],
                            "design_reports": stale_info["design_reports"],
                            "changed_clips": stale_info["changed_clips"],
                            "master_stale": stale_info["master_stale"],
                            "reassemble_note": stale_info["reassemble_note"]})
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

        if path == "/api/settings":
            hub_root = resolve_dd_hub_root()
            vault_file = hub_root / "vault" / "settings.json"
            local_file = DDMA_DIR / "settings.json"
            merged = {}
            for p in (local_file, vault_file):
                if p.exists():
                    try:
                        merged.update(json.loads(p.read_text(encoding="utf-8")))
                    except Exception:
                        pass
            merged.update(data or {})
            local_file.write_text(json.dumps(merged, indent=2), encoding="utf-8")
            if hub_root.exists():
                vault_file.parent.mkdir(parents=True, exist_ok=True)
                vault_file.write_text(json.dumps(merged, indent=2), encoding="utf-8")
            self.send_json({"success": True, "settings": merged})
            return

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
                    ep_num=ep,
                )
                ch = archetype_studio.get_longform_chapter_beats(ep, clip_num)
                res["chapter_data"] = rewrite_beat_urls(ch)
                res["beat_video_url"] = (
                    f"/api/beats/beat_video?ep={ep}&clip_num={clip_num}"
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
            if str(ep) == "249":
                _ok, _msg = _h2_patch_clip_249(clip_num)
                if _ok:
                    self.send_json({"success": True, "message": _msg})
                else:
                    self.send_json({"success": False, "error": _msg}, status=500)
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
                     "error": f"curator unreachable on :8000 — open Cutroom first: {e}"},
                    status=502)
            return

        if path == "/api/beats/set_engine":
            ep = clean_ep(data.get("ep", "248"))
            try:
                clip_num = int(data.get("clip_num", 1))
            except ValueError:
                self.send_json({"success": False, "error": "bad clip_num"}, status=400)
                return
            vs = str(data.get("visual_source", "")).strip().lower()
            try:
                import importlib
                import archetype_studio
                importlib.reload(archetype_studio)
                res = archetype_studio.set_clip_visual_source(ep, clip_num, vs)
                self.send_json(res)
            except ValueError as ve:
                self.send_json({"success": False, "error": str(ve)}, status=400)
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        if path == "/api/beats/manim_retrigger":
            # Production action only — never writes visual_source (Spec C §7).
            ep = clean_ep(data.get("ep", "248"))
            try:
                clip_num = int(data.get("clip_num", 1))
            except ValueError:
                self.send_json({"success": False, "error": "bad clip_num"}, status=400)
                return
            project_id = f"episode_{ep}"
            _re_body = {}
            if str(ep) == H2_EPISODE:
                try:
                    _rc = next((c for c in _h2_load_plan_clips() if int(c.get("num")) == int(clip_num)), {})
                except Exception:
                    _rc = {}
                _re_body = {"force_regen": True,
                              "transcript": _h2_clip_transcript(_rc) or "",
                              "title": str(_rc.get("title") or ""),
                              "directive": str(data.get("directive") or "")}
            req = urllib.request.Request(
                f"{CURATOR_BASE}/generate-manim-infographic?id={project_id}&num={clip_num}",
                data=json.dumps(_re_body).encode("utf-8"),
                headers={"Content-Type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    self.send_json(json.loads(r.read().decode("utf-8")))
            except urllib.error.HTTPError as he:
                try:
                    detail = he.read().decode("utf-8")[:500]
                except Exception:
                    detail = str(he)
                self.send_json({"success": False, "error": f"curator refused: {detail}"}, status=he.code)
            except Exception as e:
                self.send_json(
                    {"success": False, "error": f"curator unreachable on :8000 — open Cutroom first: {e}"},
                    status=502)
            return

        if path == "/api/beats/design_artifacts":
            # Spec H2 s3: ONE deliberate start; fans out one design call per
            # clip; queued background renders with per-clip progress;
            # exceptions-only reporting. Serves 249 only; never starts Mosaic.
            ep = clean_ep(data.get("ep", "248"))
            refused = _h2_refused(ep)
            if refused:
                self.send_json(refused, status=400)
                return
            try:
                import spec_h2_composite_assembler as spec_h2
                clips = _h2_load_plan_clips()
            except Exception as e:
                self.send_json({"success": False,
                                "error": f"plan unreadable: {e}"}, status=500)
                return
            try:
                only = data.get("clip_num", None)
                targets = ([c for c in clips if c.get("num") == int(only)]
                           if only is not None and str(only) != ""
                           else list(clips))
            except ValueError:
                self.send_json({"success": False, "error": "bad clip_num"},
                               status=400)
                return
            _clip_directive = (str(data.get("directive") or "") if (only is not None and str(only) != "") else "")
            if not targets:
                self.send_json({"success": False,
                                "error": "no such clip in plan"}, status=404)
                return
            plan = spec_h2.plan_design_artifacts(
                [{"clip": c.get("num")} for c in targets])
            with H2_DESIGN_LOCK:
                H2_DESIGN_SEQ[0] += 1
                group_id = f"h2-{ep}-{H2_DESIGN_SEQ[0]}"
                jobs = []
                for c, desc in zip(targets, plan["jobs"]):
                    words = [(float(w.get("start", 0)), float(w.get("end", 0)),
                              str(w.get("word", "")))
                             for w in (c.get("_caption_words") or [])]
                    jobs.append({"clip": c.get("num"), "status": "queued",
                                 "transcript_chars": len(_h2_clip_transcript(c)),
                                 "body_words": words, "shape": desc["shape"], "directive": _clip_directive})
                H2_DESIGN_GROUPS[group_id] = {"ep": ep, "finished": False,
                                              "jobs": jobs}
            threading.Thread(target=_h2_run_design_group,
                             args=(group_id,), daemon=True).start()
            self.send_json({"success": True, "group": group_id, "ep": ep,
                            "planned": len(jobs),
                            "kill_status": plan["kill_status"],
                            "note": "One design call per clip, queued in the "
                                    "background; poll design_status. Only "
                                    "exceptions are reported."})
            return

        if path == "/api/beats/composite_retrigger":
            # Spec H2 s4: pause the preview (client-side), retrigger ONE side
            # for ONE clip. Planner only: validates the duration lock and
            # returns the restitch scope. Never starts a Mosaic run; never
            # touches duration or the hard-coded frame.
            ep = clean_ep(data.get("ep", "248"))
            refused = _h2_refused(ep)
            if refused:
                self.send_json(refused, status=400)
                return
            try:
                clip_num = int(data.get("clip_num", 1))
            except ValueError:
                self.send_json({"success": False, "error": "bad clip_num"},
                               status=400)
                return
            side = str(data.get("side", "")).strip().lower()
            try:
                import spec_h2_composite_assembler as spec_h2
                clips = _h2_load_plan_clips()
                clip = next((c for c in clips if c.get("num") == clip_num),
                            None)
                if clip is None:
                    self.send_json({"success": False,
                                    "error": f"clip {clip_num} not in plan"},
                                   status=404)
                    return
                dur = spec_h2.clip_composite_duration(
                    clip, ep, DD_HUB_ROOT)
                scope = spec_h2.plan_retrigger(ep, clip_num, side, dur, dur)
            except ValueError as ve:
                self.send_json({"success": False, "error": str(ve)}, status=400)
                return
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
                return
            note = ("Manim re-render runs via the existing manim_retrigger "
                    "path; this scope re-stitches only this clip's segment."
                    if side == "manim" else
                    "Mosaic re-render runs ONLY via the double-confirmed "
                    "Mosaic retrigger button or your explicit instruction — "
                    "this endpoint never starts a run.")
            self.send_json({"success": True, "ep": ep, "clip": clip_num,
                            "scope": scope, "note": note})
            return

        if path == "/api/beats/longform_push":
            # Spec H section 6/8/9: "Push the movie to dd_hub" button backend.
            # Gate first, then copy to the episode longform slot + meta.
            ep = clean_ep(data.get("ep", "248"))
            try:
                import spec_h_composite_longform as spec_h
                master = find_master_video(ep)
                if not master:
                    self.send_json({"success": False,
                                    "error": f"no longform master for ep {ep}"},
                                   status=404)
                    return
                local_master = DDMA_DIR / "clips" / f"{ep}-longform-master.mp4"
                gate = spec_h.longform_publish_gate(
                    master, local_master if local_master.exists() else None)
                if not gate["ok"]:
                    self.send_json({"success": False, "gate": gate}, status=409)
                    return
                dest = spec_h.longform_destination(DD_HUB_ROOT, ep)
                dest.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(master, dest)
                container_d, stream_d = None, None
                if shutil.which("ffprobe") is not None:
                    try:
                        _fp = subprocess.run(
                            ["ffprobe", "-v", "error", "-show_entries",
                             "format=duration:stream=codec_type,duration",
                             "-of", "json", str(dest)],
                            capture_output=True, text=True, timeout=60)
                        _info = json.loads(_fp.stdout or "{}")
                        container_d = float(_info.get("format", {}).get("duration"))
                        stream_d = container_d
                        for _s in _info.get("streams", []):
                            if _s.get("codec_type") == "video" and _s.get("duration"):
                                stream_d = float(_s["duration"])
                                break
                    except Exception:
                        container_d, stream_d = None, None
                meta = spec_h.write_longform_meta(
                    dest, spec_h.sha256_of(dest), container_d, stream_d,
                    gate_ok=True)
                self.send_json({"success": True, "dest": str(dest),
                                "meta": meta, "gate": gate})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        if path == "/api/beats/personal/save":
            ep = clean_ep(data.get("ep", "248"))
            try:
                clip_num = int(data.get("clip_num", 1))
                beat_index = int(data.get("beat_index", 1))
            except ValueError:
                self.send_json({"success": False, "error": "bad clip_num/beat_index"}, status=400)
                return
            try:
                import importlib
                import archetype_studio
                importlib.reload(archetype_studio)
                tags_raw = data.get("tags", [])
                if isinstance(tags_raw, str):
                    tags_raw = [t.strip() for t in tags_raw.split(",") if t.strip()]
                saved = archetype_studio.save_personal_beat(
                    ep_num=ep,
                    clip_num=clip_num,
                    beat_index=beat_index,
                    class_name=str(data.get("class_name", "")).strip(),
                    title=str(data.get("title", "")).strip(),
                    tags=tags_raw,
                )
                self.send_json({"success": True, "beat": saved})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
            return

        if path == "/api/beats/personal/copy":
            ep = clean_ep(data.get("ep", "248"))
            try:
                clip_num = int(data.get("clip_num", 1))
                beat_index = int(data.get("beat_index", 1))
            except ValueError:
                self.send_json({"success": False, "error": "bad clip_num/beat_index"}, status=400)
                return
            try:
                import importlib
                import archetype_studio
                importlib.reload(archetype_studio)
                res = archetype_studio.copy_personal_beat_visual(
                    personal_beat_id=str(data.get("id", "")).strip(),
                    ep_num=ep,
                    clip_num=clip_num,
                    beat_index=beat_index,
                    target_class_name=str(data.get("class_name", "")).strip(),
                    compile_preview=bool(data.get("compile_preview", True)),
                )
                ch = archetype_studio.get_longform_chapter_beats(ep, clip_num)
                res["chapter_data"] = rewrite_beat_urls(ch)
                self.send_json(res)
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
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
