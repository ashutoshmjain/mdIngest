import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DDMA_DIR = SCRIPT_DIR.parent
os.chdir(DDMA_DIR)

os.makedirs("clips", exist_ok=True)
os.makedirs("previews", exist_ok=True)

def smart_format_transcript_py(raw_text):
    if not raw_text:
        return ""
    text = raw_text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([,.:;?!])', r'\1', text)
    text = re.sub(r'([,.:;?!])(?=[^\s\d])', r'\1 ', text)
    text = re.sub(r'\bi\b', 'I', text)
    text = re.sub(r'\bi\'m\b', "I'm", text, flags=re.IGNORECASE)
    text = re.sub(r'\bi\'ve\b', "I've", text, flags=re.IGNORECASE)
    text = re.sub(r'\bi\'ll\b', "I'll", text, flags=re.IGNORECASE)
    text = re.sub(r'\bi\'d\b', "I'd", text, flags=re.IGNORECASE)
    if text:
        text = text[0].upper() + text[1:]
    text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
    
    sentence_regex = re.compile(r'[^.!?]+[.!?]+(?:\s+|$)')
    sentences = sentence_regex.findall(text)
    if not sentences:
        sentences = [text]
    
    paragraphs = []
    current_para = []
    for idx, s in enumerate(sentences):
        s_clean = s.strip()
        current_para.append(s_clean)
        is_transition = bool(re.match(r'^(However|Moreover|Furthermore|In addition|Therefore|Clinically|When|So|Now|And|In fact|Specifically|That said|Interestingly|If |By the time|This is )', s_clean, re.IGNORECASE))
        if len(current_para) >= 3 or (len(current_para) >= 2 and is_transition and idx > 0) or idx == len(sentences) - 1:
            paragraphs.append(' '.join(current_para))
            current_para = []
    if current_para:
        paragraphs.append(' '.join(current_para))
    return '\n\n'.join(paragraphs)

import http.server
import socketserver
import webbrowser
import threading
import time
import sys
import os
from pathlib import Path
import re
import json
import shutil
import shlex
import subprocess
import requests
from urllib.parse import urlparse, parse_qs

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def configure_gemini(api_key=None):
    if not HAS_GENAI:
        return False
    creds_path = "gemini-creds.json"
    if os.path.exists(creds_path):
        try:
            from google.oauth2 import service_account
            creds = service_account.Credentials.from_service_account_file(creds_path)
            genai.configure(credentials=creds)
            print("[Gemini] Configured successfully using service account JSON credentials.")
            return True
        except Exception as e:
            print(f"[Gemini] Warning: Failed to load service account credentials: {e}")
            
    if api_key:
        genai.configure(api_key=api_key)
        return True
plan_file_lock = threading.Lock()

def safe_load_json(file_path, retries=10, delay=0.05):
    if not os.path.exists(file_path):
        return None
    for i in range(retries):
        try:
            with plan_file_lock:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        return json.load(f)
        except (PermissionError, json.JSONDecodeError, OSError):
            time.sleep(delay)
    try:
        with plan_file_lock:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
    except Exception as e:
        print(f"ERROR: safe_load_json: {file_path} unreadable after {retries} retries ({e}) -- raising.")
        raise RuntimeError(f"Unreadable JSON {file_path}: {e}") from e
    return None

def load_settings():
    # Vault first; the local file is only a fallback when the vault is unreachable.
    # Env vars still win over everything (see below).
    vault_path = vault_settings_path()
    if os.path.exists(vault_path):
        try:
            s = safe_load_json(vault_path)
        except Exception as e:
            print(f"ERROR: vault settings.json at {vault_path} is corrupt ({e}) -- refusing to run on empty settings.")
            raise
        settings = s if isinstance(s, dict) else {}
    else:
        print(f"WARNING: vault settings.json not found at {vault_path} (dd_hub unreachable?) -- falling back to local settings.json.")
        try:
            s = safe_load_json("settings.json")
        except Exception as e:
            print(f"ERROR: local settings.json is corrupt ({e}) -- refusing to run on empty settings.")
            raise
        settings = s if isinstance(s, dict) else {}
    if os.environ.get("GEMINI_API_KEY"):
        settings["gemini_api_key"] = os.environ.get("GEMINI_API_KEY")
    if os.environ.get("MOSAIC_API_KEY"):
        settings["mosaic_api_key"] = os.environ.get("MOSAIC_API_KEY")
    return settings


def resolve_dd_hub_root():
    """Single shared resolution: env -> local settings.json dd_hub_root -> candidates -> default with a LOUD warning.
    (Intentional duplicate of the resolver in ddma.py and ingest/server.py; keep the three in sync.)"""
    e = os.environ.get("DD_HUB_ROOT")
    if e and os.path.exists(e):
        return e
    try:
        s = safe_load_json("settings.json")
        if isinstance(s, dict):
            cfg = s.get("dd_hub_root")
            if cfg and os.path.exists(cfg):
                return cfg
    except Exception:
        pass
    for cand in ["/workspace/dd_hub"]:
        try:
            if os.path.exists(cand):
                return cand
        except Exception:
            pass
    local_default = str(DDMA_DIR.parent / "dd_hub")
    print(f"WARNING: DD_HUB_ROOT is unset and no dd_hub directory exists at any known location -- defaulting to plain local folder {local_default} (set DD_HUB_ROOT to your workspace to override). Vault/plan reads may fail and hub syncs will be skipped until the folder exists.")
    return local_default


def vault_settings_path():
    return os.path.join(resolve_dd_hub_root(), "vault", "settings.json")

PORT = 8000

# Global tracker for background Mosaic runs
# Keys: (project_id, clip_num), Values: {"status": ..., "progress": ..., "error": ..., "run_id": ...}
mosaic_runs = {}

def safe_save_json(file_path, data):
    with plan_file_lock:
        temp_path = f"{file_path}.tmp.{os.getpid()}.{threading.get_ident()}"
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        os.replace(temp_path, file_path)

def notify_failure(workflow, step, error):
    """Failure notification for the pipeline workflows (TRIGGER_CONTRACT.md section 4).

    Prints a timestamped NOTIFY line naming workflow/step/error to the server log
    AND appends it to dd_hub/logs/notifications.log (local logs/ fallback when the
    hub is unreachable). This is alongside -- never instead of -- the telemetry log.
    """
    import datetime as _dt2
    line = f"{_dt2.datetime.now().isoformat(timespec='seconds')} NOTIFY {workflow} step={step} error={error}"
    print(line, flush=True)
    try:
        hub = resolve_dd_hub_root()
        logdir = os.path.join(hub, "logs")
        os.makedirs(logdir, exist_ok=True)
        with open(os.path.join(logdir, "notifications.log"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        try:
            os.makedirs("logs", exist_ok=True)
            with open(os.path.join("logs", "notifications.log"), "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e2:
            print(f"WARNING: notify_failure could not persist notification: {e2}")
    return line

# ---- Phase 2: dd_hub as the PRIMARY plan store (local disk is a CACHE only) ----
PLAN_META_FILENAME = "plan.meta.json"

# episode -> hub plan_rev seen by the last load_plan() in this process.
# save_plan() refuses the write when the hub sidecar moved past this revision.
_plan_rev_cache = {}

def _episode_from_project_id(project_id):
    m = re.search(r"\d+", str(project_id))
    return m.group(0) if m else None

def _hub_plan_paths(ep):
    """(hub plan path, hub meta path), or (None, None) when dd_hub is unreachable."""
    if not ep:
        return (None, None)
    hub_root = resolve_dd_hub_root()
    try:
        if not os.path.exists(hub_root):
            return (None, None)
    except Exception:
        return (None, None)
    hub_plan = os.path.join(hub_root, "episodes", str(ep), "plan.json")
    hub_meta = os.path.join(hub_root, "episodes", str(ep), PLAN_META_FILENAME)
    return (hub_plan, hub_meta)

def _read_plan_meta(meta_path):
    try:
        if meta_path and os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                d = json.load(f)
                if isinstance(d, dict):
                    return d
    except Exception:
        pass
    return {}

def load_plan(project_id, writer="curator"):
    """Read the plan from dd_hub FIRST; the local copy is a CACHE only.

    Returns the clip list (possibly []). When dd_hub is unreachable the local
    cache is read with a VISIBLE warning -- never silently treated as current.
    """
    ep = _episode_from_project_id(project_id)
    local_plan = os.path.join("projects", project_id, "plan.json")
    hub_plan, hub_meta = _hub_plan_paths(ep)
    if hub_plan and os.path.exists(hub_plan):
        try:
            data = safe_load_json(hub_plan)
        except Exception as e:
            print(f"WARNING: hub plan at {hub_plan} raised {e} -- falling back to local cache (may be stale).")
            data = None
        if isinstance(data, list):
            meta = _read_plan_meta(hub_meta)
            try:
                _plan_rev_cache[str(ep)] = int(meta.get("plan_rev", 0))
            except Exception:
                _plan_rev_cache[str(ep)] = 0
            try:
                safe_save_json(local_plan, data)
            except Exception as ce:
                print(f"WARNING: could not refresh local plan cache {local_plan}: {ce}")
            return data
        print(f"WARNING: hub plan at {hub_plan} is unreadable -- falling back to local cache (may be stale).")
    else:
        print(f"WARNING: dd_hub plan not reachable for episode {ep} ({hub_plan}) -- reading LOCAL CACHE {local_plan} (may be stale).")
    try:
        data = safe_load_json(local_plan)
    except Exception as e:
        print(f"WARNING: local plan cache at {local_plan} unreadable ({e}) -- returning empty plan.")
        return []
    if isinstance(data, list):
        meta = _read_plan_meta(os.path.join("projects", project_id, PLAN_META_FILENAME))
        try:
            _plan_rev_cache[str(ep)] = int(meta.get("plan_rev", 0))
        except Exception:
            _plan_rev_cache[str(ep)] = 0
        return data
    return []

def save_plan(project_id, plan_data, writer="curator", expected_rev=None):
    """Write the plan to dd_hub FIRST, then the local cache, then Active Master paths.

    A save that cannot reach dd_hub raises RuntimeError (fail loudly -- never
    silently writes locally only). A save whose hub sidecar revision moved past
    the loaded revision also raises (no silent last-writer-wins; reconcile by
    hand). Returns the new plan_rev.

    NOTE (accepted, Phase 2 decision): check-then-write over a network mount is
    NOT atomic. Fine at our concurrency (one user + agents); degrades to
    "usually refuses" under a true simultaneous save. No lock file by design.
    """
    import datetime as _dt
    ep = _episode_from_project_id(project_id)
    hub_plan, hub_meta = _hub_plan_paths(ep)
    if not hub_plan:
        raise RuntimeError(
            f"dd_hub UNREACHABLE -- refusing to save plan for {project_id} locally only. "
            "Set DD_HUB_ROOT or mount dd_hub and retry.")
    if expected_rev is None:
        expected_rev = _plan_rev_cache.get(str(ep))
    current_meta = _read_plan_meta(hub_meta)
    try:
        current_rev = int(current_meta.get("plan_rev", 0))
    except Exception:
        current_rev = 0
    if expected_rev is not None and int(expected_rev) != current_rev:
        raise RuntimeError(
            f"STALE plan write REFUSED for {project_id}: hub plan_rev is {current_rev}, "
            f"you loaded {expected_rev}. Reload the hub plan, re-apply your change, and save again. "
            "No silent last-writer-wins.")
    new_rev = current_rev + 1
    stamp = _dt.datetime.now().astimezone().isoformat()
    os.makedirs(os.path.dirname(hub_plan), exist_ok=True)
    safe_save_json(hub_plan, plan_data)
    safe_save_json(hub_meta, {"plan_rev": new_rev, "last_writer": writer, "updated_at": stamp})
    _plan_rev_cache[str(ep)] = new_rev
    local_plan = os.path.join("projects", project_id, "plan.json")
    safe_save_json(local_plan, plan_data)
    safe_save_json(os.path.join("projects", project_id, PLAN_META_FILENAME),
                    {"plan_rev": new_rev, "last_writer": writer, "updated_at": stamp})
    safe_save_json("plan.json", plan_data)
    if ep:
        for docs_root in ["docs", os.path.join("..", "src", "ddma", "docs")]:
            docs_ep_plan = os.path.join(docs_root, "episodes", ep, "plan.json")
            if os.path.exists(os.path.dirname(docs_ep_plan)):
                try:
                    shutil.copy2(local_plan, docs_ep_plan)
                except Exception as e:
                    print(f"Error syncing {docs_ep_plan}: {e}")
    return new_rev

# ---- Phase 3: working assets read from dd_hub, local clips/ is a CACHE ----
def working_asset_hub_path(ep, filename):
    """PRIMARY location of a working asset on dd_hub, or None when unreachable."""
    hub_root = resolve_dd_hub_root()
    try:
        if not hub_root or not os.path.exists(hub_root):
            return None
    except Exception:
        return None
    return os.path.join(hub_root, "episodes", str(ep), filename)

def working_asset_local_path(filename):
    """Local CACHE location of a working asset (same filename, local clips/ dir)."""
    return os.path.join("clips", filename)

def read_working_asset(ep, filename, quiet=False):
    """Resolve the path to read: the hub PRIMARY copy when present, else the local cache.

    Prints a VISIBLE warning on every cache fallback unless quiet=True (existence
    probes on hot paths pass quiet=True to avoid log spam; content reads stay loud).
    """
    hub_p = working_asset_hub_path(ep, filename)
    if hub_p and os.path.exists(hub_p):
        return hub_p
    local_p = working_asset_local_path(filename)
    if not quiet:
        if hub_p is None:
            print(f"WARNING: dd_hub unreachable -- reading working asset from LOCAL CACHE clips/{filename} (may be stale).")
        else:
            print(f"WARNING: working asset {filename} not on hub -- reading LOCAL CACHE (may be stale).")
    return local_p

def ensure_local_cache(ep, filename):
    """Copy the hub PRIMARY copy down to the local cache when the cache is cold.

    Local-only consumers (ddma CLI subprocesses, ffmpeg) need the file in clips/;
    call this before invoking them. No-op when the cache is warm or hub is missing.
    """
    local_p = working_asset_local_path(filename)
    if os.path.exists(local_p):
        return local_p
    hub_p = working_asset_hub_path(ep, filename)
    if hub_p and os.path.exists(hub_p):
        try:
            os.makedirs(os.path.dirname(local_p) or ".", exist_ok=True)
            shutil.copy2(hub_p, local_p)
            print(f"[{ep}] Warmed local cache from hub: {filename}")
        except Exception as ce:
            print(f"WARNING: could not warm local cache for {filename}: {ce}")
    return local_p

def ensure_audio_slice_cache(ep, c_num):
    """Warm the clip's audio slice ({ep}-{num}-*.mp3) from the hub episode folder.

    There is exactly one audio slice per clip; when the hub has no match, do
    nothing here (the compile fails loudly as it does today -- never invent
    a filename). Same hub-primary/local-cache direction as ensure_local_cache.
    """
    hub_probe = working_asset_hub_path(ep, "x")
    hub_dir = os.path.dirname(hub_probe) if hub_probe else ""
    if not hub_dir or not os.path.isdir(hub_dir):
        return
    prefix = f"{ep}-{c_num}-"
    try:
        names = sorted(os.listdir(hub_dir))
    except Exception:
        return
    for name in names:
        if name.startswith(prefix) and name.lower().endswith(".mp3"):
            ensure_local_cache(ep, name)
            return

def get_mosaic_jobs_file(project_id):
    proj_dir = os.path.join("projects", project_id)
    os.makedirs(proj_dir, exist_ok=True)
    return os.path.join(proj_dir, "mosaic_jobs.json")

def load_mosaic_jobs(project_id):
    jobs_file = get_mosaic_jobs_file(project_id)
    if os.path.exists(jobs_file):
        try:
            with open(jobs_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except Exception as e:
            print(f"Warning loading mosaic_jobs for {project_id}: {e}")
    return {}

def save_mosaic_jobs(project_id, jobs_dict):
    try:
        jobs_file = get_mosaic_jobs_file(project_id)
        serializable = {str(k): v for k, v in jobs_dict.items()}
        with open(jobs_file, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2)
    except Exception as e:
        print(f"Warning saving mosaic_jobs for {project_id}: {e}")

def update_mosaic_job_state(project_id, clip_num, status, progress, error=None, run_id=None):
    # Serialize the read-modify-write: concurrent heal/pipeline threads must not
    # clobber each other's entries (Issue 86 found clip 13's completed entry lost
    # to two simultaneous saves). save_mosaic_jobs takes no lock itself, so no
    # re-entrancy hazard with plan_file_lock here.
    job_key = (project_id, int(clip_num))
    with plan_file_lock:
        existing = mosaic_runs.get(job_key, {})
        new_job = {
            "status": status,
            "progress": progress,
            "error": error,
            "run_id": run_id or existing.get("run_id"),
            "start_time": existing.get("start_time", time.time()),
            "last_update": time.time()
        }
        mosaic_runs[job_key] = new_job

        # Save to disk for persistence across server restarts
        proj_jobs = load_mosaic_jobs(project_id)
        proj_jobs[int(clip_num)] = new_job
        save_mosaic_jobs(project_id, proj_jobs)

def download_mosaic_render(project_id, ep_num, clip_num, run_id, video_url):
    """Download an already-completed Mosaic render hub-first.

    Shared by run_mosaic_pipeline Step 5 and the heal re-download (Issue 86).
    Raises on failure. Never starts a run -- the caller must already hold a
    completed run's video_url (free, 0 API cost for a new run)."""
    mosaic_filename = f"{ep_num}-{clip_num}-mosaic-{run_id}.mp4"
    mosaic_hub_path = working_asset_hub_path(ep_num, mosaic_filename)
    if not mosaic_hub_path:
        raise Exception(f"dd_hub UNREACHABLE -- refusing Mosaic download for Clip {clip_num} (working assets never write locally-only). Set DD_HUB_ROOT or mount dd_hub and retry.")
    mosaic_version_path = working_asset_local_path(mosaic_filename)

    # Download rendered video with robust multi-attempt retry (protects against socket blips/IncompleteRead)
    download_success = False
    last_dl_err = None
    for attempt in range(1, 6):
        try:
            print(f"[{project_id}][Clip {clip_num}] Downloading rendered video from Mosaic S3 (attempt {attempt}/5)...")
            res_download = requests.get(video_url, stream=True, timeout=60)
            if res_download.status_code != 200:
                raise Exception(f"Failed to download rendered video from Mosaic: HTTP {res_download.status_code}")

            os.makedirs(os.path.dirname(mosaic_hub_path), exist_ok=True)
            mosaic_part_path = mosaic_hub_path + ".part"
            with open(mosaic_part_path, "wb") as f_out:
                for chunk in res_download.iter_content(chunk_size=65536):
                    if chunk:
                        f_out.write(chunk)

            if os.path.exists(mosaic_part_path) and os.path.getsize(mosaic_part_path) > 1024:
                # Hub FIRST (atomic rename, no partials on the primary store), then the local cache.
                os.replace(mosaic_part_path, mosaic_hub_path)
                os.makedirs(os.path.dirname(mosaic_version_path) or "clips", exist_ok=True)
                shutil.copy2(mosaic_hub_path, mosaic_version_path)
                download_success = True
                break
            else:
                raise Exception("Downloaded file is empty or corrupted.")
        except Exception as dl_ex:
            last_dl_err = dl_ex
            print(f"[{project_id}][Clip {clip_num}] Download attempt {attempt} failed: {dl_ex}. Retrying in 5s...")
            time.sleep(5)

    if not download_success:
        raise Exception(f"Failed to download rendered video after 5 attempts: {last_dl_err}")
    return mosaic_hub_path

def _clip_master_is_valid(master_clip_path):
    """A master is valid when the file exists, is non-trivial, and ffprobes
    to a real duration. Shared by the heal scan and its workers."""
    if not (os.path.exists(master_clip_path) and os.path.getsize(master_clip_path) > 1024):
        return False
    try:
        chk = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1", master_clip_path],
            capture_output=True, text=True, timeout=5
        )
        return chk.returncode == 0
    except Exception:
        return False

def _heal_compile_and_mark(pid, cn, rid):
    """Compile one clip's master and mark the Mosaic job completed/failed.
    Shared by heal Case 1 (after a re-download) and Case 2 workers."""
    try:
        plan_file = os.path.join("projects", pid, "plan.json")
        subprocess.run([sys.executable, "ddma.py", "compile-clip", "--num", str(cn), "--plan-file", plan_file], check=True)
        update_mosaic_job_state(pid, cn, "completed", 100, run_id=rid)
        print(f"[{pid}][Clip {cn}] Auto-healing compilation complete!")
    except Exception as h_err:
        print(f"[{pid}][Clip {cn}] Auto-healing compilation failed: {h_err}")
        update_mosaic_job_state(pid, cn, "failed", 0, error=str(h_err), run_id=rid)

def auto_recompile_clip(project_id, clip_num):
    try:
        ep_num_match = re.search(r'\d+', str(project_id))
        ep_num = ep_num_match.group(0) if ep_num_match else "244"
        master_clip_path = os.path.join("clips", f"{ep_num}-{clip_num}.mp4")
        orig_clip_path = os.path.join("clips", f"{ep_num}-{clip_num}-original.mp4")
        if os.path.exists(master_clip_path) or os.path.exists(orig_clip_path):
            import sys
            plan_path = os.path.join("projects", project_id, "plan.json")
            print(f"[{project_id}][Clip {clip_num}] Auto re-compiling clip after title/bridge update...")
            subprocess.run([
                sys.executable, "ddma.py", "compile-clip",
                "--num", str(clip_num),
                "--plan-file", plan_path
            ], check=True)
            print(f"[{project_id}][Clip {clip_num}] Auto re-compilation complete!")
    except Exception as e:
        print(f"[{project_id}][Clip {clip_num}] Warning: Auto compile-clip failed: {e}")

def heal_mosaic_project_state(project_id, plan_data=None):
    """
    Scans project state for interrupted or stalled Mosaic runs across server restarts
    or prompt settings changes. Self-heals zombie states:
    1. If the mosaic file is missing but the plan has a run_id: re-download the
       completed render from Mosaic's cloud using the run_id (free, 0 API cost;
       never starts a new run); if the master is missing/invalid, fall through
       to the Case 2 compile, else mark completed. Other run states
       (running/failed/etc.) are left untouched.
    2. If mosaic file downloaded but master compilation incomplete/broken: auto-resumes compile-clip.
    3. If master compilation is already valid on disk: ensures mosaic_jobs.json reflects 100% completed.
    """
    ep_num_match = re.search(r'\d+', str(project_id))
    if not ep_num_match:
        return
    ep_num = ep_num_match.group(0)

    if plan_data is None:
        try:
            plan_data = load_plan(project_id) or []
        except Exception as le:
            print(f"WARNING: hub plan load failed in heal ({le}) -- healing with empty plan.")
            plan_data = []

    for clip in plan_data:
        if not isinstance(clip, dict) or "mosaic_run_id" not in clip:
            continue
        c_num = clip.get("num")
        if c_num is None:
            continue
        run_id = clip["mosaic_run_id"]
        versioned_mosaic_file = read_working_asset(ep_num, f"{ep_num}-{c_num}-mosaic-{run_id}.mp4", quiet=True)
        orig_file = read_working_asset(ep_num, f"{ep_num}-{c_num}-original.mp4", quiet=True)
        ensure_local_cache(ep_num, f"{ep_num}-{c_num}-mosaic-{run_id}.mp4")
        ensure_local_cache(ep_num, f"{ep_num}-{c_num}-original.mp4")
        ensure_audio_slice_cache(ep_num, c_num)
        master_clip_path = os.path.join("clips", f"{ep_num}-{c_num}.mp4")
        job_key = (project_id, int(c_num))

        has_mosaic_source = os.path.exists(versioned_mosaic_file) or os.path.exists(orig_file)

        master_is_valid = _clip_master_is_valid(master_clip_path)

        if not has_mosaic_source:
            # Case 1: Mosaic source file missing locally. Never START a new run:
            # a Mosaic run begins ONLY on the user's explicit trigger (the
            # manual Mosaic button / /export-to-mosaic). But when the plan already
            # holds a mosaic_run_id, the completed render can be fetched again
            # from Mosaic's cloud -- a download, free, 0 API cost for a new run.
            # Runs still in flight (running/starting) wait; failed runs and API
            # errors are left for the user to retry via the button.
            if run_id:
                def _heal_redownload(pid=project_id, cn=c_num, rid=run_id, epn=ep_num):
                    if mosaic_runs.get((pid, int(cn)), {}).get("status") == "auto-downloading":
                        print(f"[{pid}][Clip {cn}] Heal re-download already in progress -- skipping duplicate.")
                        return
                    try:
                        settings = load_settings()
                        api_key = settings.get("mosaic_api_key")
                        if not api_key:
                            print(f"[{pid}][Clip {cn}] Heal re-download skipped: no mosaic_api_key configured (run_id {rid}).")
                            return
                        res_status = requests.get(f"https://api.mosaic.so/agent_run/{rid}",
                                                  headers={"Authorization": f"Bearer {api_key}"},
                                                  timeout=20)
                        if res_status.status_code != 200:
                            print(f"[{pid}][Clip {cn}] Heal re-download skipped: Mosaic API returned HTTP {res_status.status_code} for run_id {rid}. Leaving clip for manual retry.")
                            return
                        run_info = res_status.json() or {}
                        status = run_info.get("status")
                        if status == "completed":
                            outputs = run_info.get("outputs") or []
                            video_url = outputs[0].get("video_url") if outputs else None
                            if not video_url:
                                print(f"[{pid}][Clip {cn}] Heal re-download skipped: run {rid} is completed but has no video_url. Leaving clip for manual retry.")
                                return
                            print(f"[{pid}][Clip {cn}] Heal re-downloading completed render for run_id {rid}...")
                            update_mosaic_job_state(pid, cn, "auto-downloading", 90, run_id=rid)
                            download_mosaic_render(pid, epn, cn, rid, video_url)
                            print(f"[{pid}][Clip {cn}] Heal re-download complete.")
                            if _clip_master_is_valid(os.path.join("clips", f"{epn}-{cn}.mp4")):
                                update_mosaic_job_state(pid, cn, "completed", 100, run_id=rid)
                                print(f"[{pid}][Clip {cn}] Master already valid -- skipping recompile.")
                            else:
                                print(f"[{pid}][Clip {cn}] Master missing/invalid -- compiling master.")
                                _heal_compile_and_mark(pid, cn, rid)
                        elif status in ("running", "starting", "queued", "pending"):
                            print(f"[{pid}][Clip {cn}] Heal: run {rid} is '{status}' on Mosaic -- waiting, no download, no compile.")
                        else:
                            print(f"[{pid}][Clip {cn}] Heal re-download skipped: run {rid} status is '{status}'. Leaving clip for manual retry.")
                    except Exception as he:
                        print(f"[{pid}][Clip {cn}] Heal re-download failed for run {rid}: {he}. Leaving clip for manual retry.")
                t = threading.Thread(target=_heal_redownload, daemon=True)
                t.start()
            # No run_id: nothing to fetch -- leave the job state untouched.
        elif has_mosaic_source and not master_is_valid:
            # Case 2: Mosaic video downloaded, but master clip compilation was interrupted mid-flight (e.g. at 95%)
            if job_key not in mosaic_runs or mosaic_runs[job_key].get("status") not in ("compiling", "completed"):
                print(f"[{project_id}][Clip {c_num}] Auto-healing interrupted compilation for run_id {run_id}...")
                update_mosaic_job_state(project_id, c_num, "auto-compiling", 95, run_id=run_id)
                def _heal_worker(pid=project_id, cn=c_num, rid=run_id):
                    _heal_compile_and_mark(pid, cn, rid)
                t = threading.Thread(target=_heal_worker, daemon=True)
                t.start()
        elif has_mosaic_source and master_is_valid:
            # Case 3: Master clip already valid, ensure mosaic_jobs.json reflects 100% completed
            d_jobs = load_mosaic_jobs(project_id)
            cur_j = d_jobs.get(int(c_num))
            if cur_j and cur_j.get("status") != "completed":
                update_mosaic_job_state(project_id, c_num, "completed", 100, run_id=run_id)

# Background thread helper for executing the Mosaic API pipeline (upload, run, poll, download)
def run_mosaic_pipeline(project_id, clip_num, settings, prompt_content, segments, audio_path, run_id=None):
    job_key = (project_id, int(clip_num))
    update_mosaic_job_state(project_id, clip_num, "starting", 0, run_id=run_id)
    
    try:
        api_key = settings.get("mosaic_api_key")
        agent_id = settings.get("mosaic_agent_id")
        mogr_node_id = settings.get("mosaic_mogr_node_id")
        captions_node_id = settings.get("mosaic_captions_node_id")
        
        if not api_key or not agent_id:
            raise Exception("Mosaic API Key and Agent ID must be configured in System Settings first.")
        
        headers = {"Authorization": f"Bearer {api_key}"}
        base_url = "https://api.mosaic.so"
        
        # 1. Locate local file
        ep_num_match = re.search(r'\d+', project_id)
        if not ep_num_match:
            raise Exception(f"Could not resolve episode number from project ID '{project_id}'")
        ep_num = ep_num_match.group(0)
        
        file_path = os.path.join("clips", f"{ep_num}-{clip_num}.mp4")

        if not run_id:
            # Force recompilation of the black draft video on a fresh Mosaic run so any audio changes are captured!
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as rm_err:
                    print(f"Warning: could not delete old clip file: {rm_err}")
                    
            backup_path = os.path.join("clips", f"{ep_num}-{clip_num}-original.mp4")
            if os.path.exists(backup_path):
                try:
                    os.remove(backup_path)
                except Exception as rm_err:
                    print(f"Warning: could not delete old backup file: {rm_err}")

            import glob
            for old_audio in glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}*.mp3")):
                try:
                    os.remove(old_audio)
                except Exception:
                    pass

            for old_mosaic in glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}-mosaic-*.mp4")):
                # If this is a fresh run (run_id is not the one in the filename), clean it up
                if not run_id or run_id not in old_mosaic:
                    try:
                        os.remove(old_mosaic)
                    except Exception:
                        pass
                    
            # Step 1: Prepare fresh baseline body draft MP4 (audio + black canvas body, NO intro/outro cards)
            update_mosaic_job_state(project_id, clip_num, "muxing draft body", 5, run_id=run_id)
            print(f"[{project_id}][Clip {clip_num}] Muxing baseline body draft before Mosaic upload...")
            
            os.makedirs("clips", exist_ok=True)
            plan_file_path = os.path.join("projects", project_id, "plan.json")
            
            # Always ensure canonical continuous raw audio source (.m4a) is resolved
            canonical_audio = get_project_canonical_audio_path(os.path.join("projects", project_id), project_id)
            if canonical_audio and os.path.exists(canonical_audio):
                audio_path = canonical_audio
                print(f"[{project_id}][Clip {clip_num}] Using canonical raw audio source: {audio_path}")
            elif not os.path.exists(audio_path):
                possible_candidates = [
                    os.path.join("projects", project_id, f"{ep_num}.m4a"),
                    os.path.join("projects", project_id, f"{ep_num}.mp3"),
                    os.path.join("..", "deepDive", "ddma", "projects", project_id, f"{ep_num}.m4a"),
                    os.path.join("..", "deepDive", "ddma", "projects", project_id, f"{ep_num}.mp3")
                ]
                for cand in possible_candidates:
                    if os.path.exists(cand):
                        audio_path = cand
                        print(f"[{project_id}][Clip {clip_num}] Resolved audio source via fallback: {audio_path}")
                        break

            # Slice fresh audio clip for this specific clip
            cut_cmd = [sys.executable, "ddma.py", "cut", "--audio", audio_path, "--plan-file", plan_file_path, "--out-dir", "clips", "--num", str(clip_num)]
            res_cut = subprocess.run(cut_cmd, capture_output=True, text=True, cwd=".")
            if res_cut.returncode != 0:
                raise Exception(f"Audio cut failed for Clip {clip_num}: {res_cut.stderr}")
                
            # Mux clean solid black canvas draft body video (exact audio duration, NO intro/outro cards)
            mux_draft_cmd = [sys.executable, "ddma.py", "mux-clip", "--num", str(clip_num), "--plan-file", plan_file_path, "--out-dir", "clips"]
            res_draft = subprocess.run(mux_draft_cmd, capture_output=True, text=True, cwd=".")
            if res_draft.returncode != 0:
                raise Exception(f"Failed to prepare baseline draft body video for Mosaic: {res_draft.stderr}")
            print(f"[{project_id}][Clip {clip_num}] Fresh baseline draft body video muxed successfully: {file_path}")
            
            # Step 2: Upload S3
            update_mosaic_job_state(project_id, clip_num, "requesting upload URL", 10, run_id=run_id)
            print(f"[{project_id}][Clip {clip_num}] Requesting upload URL from Mosaic...")
            
            # Get upload details
            res = requests.post(f"{base_url}/uploads/video/get_upload_url", headers=headers)
            if res.status_code != 200:
                raise Exception(f"Mosaic get_upload_url failed: {res.text}")
            
            upload_data = res.json()
            upload_url = upload_data.get("upload_url")
            upload_fields = upload_data.get("upload_fields", {})
            video_id = upload_data.get("video_id")
            
            if not upload_url or not video_id:
                raise Exception("Failed to retrieve upload parameters from Mosaic.")
            
            # Post file to S3
            update_mosaic_job_state(project_id, clip_num, "uploading media", 30, run_id=run_id)
            print(f"[{project_id}][Clip {clip_num}] Uploading {file_path} to Mosaic S3 storage...")
            
            with open(file_path, "rb") as f:
                files = {
                    "file": (os.path.basename(file_path), f, "video/mp4")
                }
                res_s3 = requests.post(upload_url, data=upload_fields, files=files)
                
            if res_s3.status_code not in (200, 201, 204):
                raise Exception(f"S3 upload failed: Status code {res_s3.status_code}, response: {res_s3.text}")
            
            # Finalize upload
            update_mosaic_job_state(project_id, clip_num, "finalizing upload", 50, run_id=run_id)
            print(f"[{project_id}][Clip {clip_num}] Finalizing upload on Mosaic...")
            
            res_finalize = requests.post(
                f"{base_url}/uploads/video/finalize_upload",
                headers=headers,
                json={"video_id": video_id}
            )
            if res_finalize.status_code != 200:
                raise Exception(f"Mosaic finalize_upload failed: {res_finalize.text}")
            
            # Step 3: Trigger Agent Run
            update_mosaic_job_state(project_id, clip_num, "triggering run", 60, run_id=run_id)
            print(f"[{project_id}][Clip {clip_num}] Triggering Mosaic agent run...")
            
            update_params = {}
            if mogr_node_id:
                update_params[mogr_node_id] = {
                    "prompt": prompt_content,
                    "model_tier": "pro",
                    "style_video_url": "https://www.youtube.com/shorts/xybpfL1GnEQ",
                    "frequency_per_minute": "auto",
                    "reference_links": "",
                    "only_generate_full_screen_graphics": True
                }
            if captions_node_id and str(captions_node_id).strip():
                default_captions_config = {
                    "font1": "Montserrat",
                    "font2": "Besley",
                    "color_override": None,
                    "text_bg_enabled": False,
                    "text_bg_color": "#000000",
                    "text_bg_opacity": 0.6,
                    "text_bg_roundness": 6,
                    "animation_style": "fade",
                    "stroke_enabled": True,
                    "stroke_color": "#000000",
                    "stroke_width": 2,
                    "uniform_word_size": False,
                    "single_line": False,
                    "caption_position": "auto",
                    "shadow_enabled": False,
                    "shadow_blur": 10,
                    "shadow_color": "#000000",
                    "shadow_opacity": 0.5
                }
                update_params[captions_node_id] = settings.get("mosaic_captions_config") or default_captions_config
            
            run_body = {
                "video_ids": [video_id]
            }
            if update_params:
                run_body["update_params"] = update_params
            
            res_run = requests.post(
                f"{base_url}/agent/{agent_id}/run",
                headers=headers,
                json=run_body
            )
            if res_run.status_code != 200:
                raise Exception(f"Failed to start agent run on Mosaic: {res_run.text}")
            
            run_id = res_run.json().get("run_id")
            if not run_id:
                raise Exception("Failed to retrieve run ID from Mosaic execution response.")

            update_mosaic_job_state(project_id, clip_num, "triggering run", 60, run_id=run_id)

            # Persist mosaic_run_id to the hub plan immediately so interrupt/resumes are 100% recoverable
            try:
                persist_plan = load_plan(project_id)
                for c in persist_plan:
                    if int(c.get("num", -1)) == int(clip_num):
                        c["mosaic_run_id"] = run_id
                        break
                save_plan(project_id, persist_plan)
                print(f"[{project_id}][Clip {clip_num}] Immediately saved mosaic_run_id {run_id} to hub plan.json for interrupt/resume protection!")
            except RuntimeError as pe:
                print(f"[{project_id}][Clip {clip_num}] ERROR: hub plan save FAILED LOUDLY (no local-only write): {pe}")
            except Exception as pe:
                print(f"[{project_id}][Clip {clip_num}] Warning: Failed to save initial mosaic_run_id to plan.json: {pe}")

        # Resume / Start Step 4: Polling
        update_mosaic_job_state(project_id, clip_num, "running", 70, run_id=run_id)
        print(f"[{project_id}][Clip {clip_num}] Polling Mosaic run {run_id} status every 60 seconds (4 hours max)...")
        
        max_attempts = 240  # 4 hours max at 60-second intervals
        attempt = 0
        final_video_url = None
        
        while attempt < max_attempts:
            attempt += 1
            
            try:
                res_status = requests.get(f"{base_url}/agent_run/{run_id}", headers=headers)
                if res_status.status_code != 200:
                    print(f"[{project_id}][Clip {clip_num}] Error checking Mosaic run status: {res_status.text}")
                    time.sleep(60)
                    continue
                run_info = res_status.json()
            except Exception as poll_ex:
                print(f"[{project_id}][Clip {clip_num}] Warning: Connection glitch while polling Mosaic status: {poll_ex}. Retrying in 60 seconds...")
                time.sleep(60)
                continue
            
            status = run_info.get("status")
            
            print(f"[{project_id}][Clip {clip_num}] Polling Mosaic run status: {status}")
            
            if status == "completed":
                outputs = run_info.get("outputs", [])
                if outputs and outputs[0].get("video_url"):
                    final_video_url = outputs[0]["video_url"]
                    break
                else:
                    raise Exception("Mosaic run completed but no output video URL was returned.")
            elif status in ("failed", "cancelled"):
                err_msg = run_info.get("status_message") or "Unknown run error."
                node_errors = run_info.get("errors", [])
                if node_errors:
                    err_msg += f" Detailed errors: {json.dumps(node_errors)}"
                raise Exception(f"Mosaic run ended with status '{status}': {err_msg}")
            
            # Update progress incrementally while running
            new_prog = min(70 + int((attempt / max_attempts) * 25), 90)
            update_mosaic_job_state(project_id, clip_num, f"rendering ({status})", new_prog, run_id=run_id)
            time.sleep(60)
        
        if not final_video_url:
            raise Exception("Mosaic run timed out after 4 hours.")
            
        # Step 5: Download finished video (hub-first via the shared helper)
        update_mosaic_job_state(project_id, clip_num, "downloading output", 95, run_id=run_id)
        print(f"[{project_id}][Clip {clip_num}] Downloading rendered video from Mosaic S3...")

        mosaic_filename = f"{ep_num}-{clip_num}-mosaic-{run_id}.mp4"
        mosaic_hub_path = working_asset_hub_path(ep_num, mosaic_filename)
        if not mosaic_hub_path:
            raise Exception(f"dd_hub UNREACHABLE -- refusing Mosaic download for Clip {clip_num} (working assets never write locally-only). Set DD_HUB_ROOT or mount dd_hub and retry.")
        mosaic_version_path = working_asset_local_path(mosaic_filename)

        # Purge older Mosaic render files for this clip (e.g. clips/245-13-mosaic-*.mp4)
        import glob
        for f_cand in glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}-mosaic-*.mp4")):
            if f_cand != mosaic_version_path:
                try:
                    os.remove(f_cand)
                    print(f"[{project_id}][Clip {clip_num}] Purged older Mosaic render: {f_cand}")
                except Exception as p_err:
                    print(f"Warning: Could not purge older Mosaic render {f_cand}: {p_err}")
        for f_cand in glob.glob(os.path.join(os.path.dirname(mosaic_hub_path), f"{ep_num}-{clip_num}-mosaic-*.mp4")):
            if os.path.abspath(f_cand) != os.path.abspath(mosaic_hub_path):
                try:
                    os.remove(f_cand)
                    print(f"[{project_id}][Clip {clip_num}] Purged older hub Mosaic render: {f_cand}")
                except Exception as p_err:
                    print(f"Warning: Could not purge older hub Mosaic render {f_cand}: {p_err}")

        download_mosaic_render(project_id, ep_num, clip_num, run_id, final_video_url)

        # Persist mosaic_run_id into the hub plan AFTER successful download!
        try:
            dl_plan = load_plan(project_id)
            for c in dl_plan:
                if int(c.get("num", -1)) == int(clip_num):
                    c["mosaic_run_id"] = run_id
                    break
            save_plan(project_id, dl_plan)
            print(f"[{project_id}][Clip {clip_num}] Persisted mosaic_run_id {run_id} to hub plan.json after successful download!")
        except RuntimeError as pe:
            print(f"[{project_id}][Clip {clip_num}] ERROR: hub plan save FAILED LOUDLY (no local-only write): {pe}")
        except Exception as pe:
            print(f"[{project_id}][Clip {clip_num}] Warning: Failed to save mosaic_run_id to plan.json: {pe}")

        # Step 6: Automatically stitch Mosaic render into final Master Clip (Intro 2s + Mosaic Body + Outro 5s) & sync to docs/
        print(f"[{project_id}][Clip {clip_num}] Auto-compiling Master Mosaic video with Intro/Outro cards...")
        try:
            plan_file_path = os.path.join("projects", project_id, "plan.json")
            comp_master_cmd = [sys.executable, "ddma.py", "compile-clip", "--num", str(clip_num), "--plan-file", plan_file_path]
            res_comp = subprocess.run(comp_master_cmd, capture_output=True, text=True, cwd=".")
            if res_comp.returncode == 0:
                print(f"[{project_id}][Clip {clip_num}] Successfully compiled and synced Master Mosaic clip!")
            else:
                print(f"[{project_id}][Clip {clip_num}] Warning auto-compiling master clip: {res_comp.stderr}")
        except Exception as comp_err:
            print(f"[{project_id}][Clip {clip_num}] Warning: Failed auto-compiling master clip: {comp_err}")

        update_mosaic_job_state(project_id, clip_num, "completed", 100, run_id=run_id)
        print(f"[{project_id}][Clip {clip_num}] Mosaic download completed successfully! Status set to completed.")
        
    except Exception as ex:
        import traceback
        tb_str = traceback.format_exc()
        print(f"Error in run_mosaic_pipeline for clip {clip_num}: {ex}\n{tb_str}")
        update_mosaic_job_state(project_id, clip_num, "failed", 0, error=str(ex), run_id=run_id)
        notify_failure("W3", "mosaic-run", f"{project_id} clip {clip_num}: {ex}")
        
        # CRITICAL SEV-1 GUARD: Only delete mosaic_run_id from plan.json if the cloud API explicitly
        # reported the run as permanently cancelled or failed. NEVER delete run_id on local network or disk blips!
        is_cloud_terminal_failure = run_id and any(term in str(ex).lower() for term in ["ended with status 'failed'", "ended with status 'cancelled'", "not found", "404"])
        if is_cloud_terminal_failure:
            try:
                cleanup_plan = load_plan(project_id)
                for c in cleanup_plan:
                    if int(c.get("num", -1)) == int(clip_num) and "mosaic_run_id" in c:
                        del c["mosaic_run_id"]
                        break
                save_plan(project_id, cleanup_plan)
                print(f"[{project_id}][Clip {clip_num}] Cleaned up terminal failed mosaic_run_id from hub plan.json")
            except RuntimeError as pe:
                print(f"[{project_id}][Clip {clip_num}] ERROR: hub plan save FAILED LOUDLY (no local-only write): {pe}")
            except Exception as pe:
                print(f"Warning: Failed to clean up mosaic_run_id from plan.json on error: {pe}")
        

def resolve_deepdive_publication_clips_dir(episode) -> Path:
    """
    Resolves the canonical deepDive publication clips directory:
      <deepDive_root>/src/ddma/docs/episodes/<episode>/clips
    Anchored on __file__ to guarantee reliable resolution across:
      1. deepDive unified workbench (<deepDive>/ddma/scratch/run_curator.py)
      2. Merged mdIngest repo (<mdIngest>/ddma/scratch/run_curator.py)
      3. Any arbitrary invocation directory.
    """
    script_path = Path(__file__).resolve()
    candidates = []
    for parent in script_path.parents:
        cand_direct = parent / "src" / "ddma" / "docs" / "episodes"
        if cand_direct.exists():
            candidates.append(cand_direct)
            break
    if candidates:
        chosen = candidates[0] / str(episode) / "clips"
        return chosen
    attempted = [str(p / "src/ddma/docs/episodes") for p in script_path.parents]
    raise FileNotFoundError(
        f"Could not resolve deepDive publication directory from {script_path}. Attempted candidates: {attempted}"
    )

def get_project_canonical_audio_path(project_dir: str, project_id: str = None, info: dict = None) -> str:
    """
    Resolves the canonical continuous raw audio source for an episode.
    Always prioritizes raw continuous .m4a input over .mp3 because .mp3 may be the
    assembled longform podcast master containing inserted music stings.
    """
    if not project_id:
        project_id = os.path.basename(project_dir)
    ep_num = project_id.replace("episode_", "")

    if info is None:
        info_path = os.path.join(project_dir, "project_info.json")
        if os.path.exists(info_path):
            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
            except Exception:
                info = {}
        else:
            info = {}

    # 1. First priority: Raw continuous .m4a in project directory matching transcript timeline
    for cand_name in [f"{ep_num}.m4a", f"episode_{ep_num}.m4a", "audio.m4a", f"{ep_num}.wav", f"episode_{ep_num}.wav"]:
        cand_path = os.path.join(project_dir, cand_name)
        if os.path.exists(cand_path):
            return cand_path

    # 2. Check info audio_filename if it exists
    f_name = info.get("audio_filename") or info.get("audio_file")
    if f_name:
        cand_path = os.path.join(project_dir, f_name)
        if os.path.exists(cand_path):
            stem = os.path.splitext(f_name)[0]
            for ext in [".m4a", ".wav"]:
                m4a_equiv = os.path.join(project_dir, f"{stem}{ext}")
                if os.path.exists(m4a_equiv):
                    return m4a_equiv
            return cand_path

    # 3. Fallback to any candidate audio file in project dir
    for ext in [".m4a", ".wav", ".mp3"]:
        for cand_name in [f"{ep_num}{ext}", f"episode_{ep_num}{ext}", f"audio{ext}"]:
            cand_path = os.path.join(project_dir, cand_name)
            if os.path.exists(cand_path):
                return cand_path

    return None

def compile_segments_helper(segments, output_path, audio_source_path):
    """
    Compiles clip segments preview using exact sample-accurate timeline mixing:
    - Hook speech: 0 to h_dur
    - Mid Sting: 0.2s silence gap, dur_m, 2.0s fade out
    - Body speech: enters 1.0s into the 2.0s fading sting tail at 100% FULL volume (zero afade=in on human voice!)
    - Outro Sting: 0.2s silence gap after body speech, 2.0s fade out
    - Normalized to -16 LUFS
    """
    if not segments:
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=48000:cl=stereo:d=1.0",
            "-c:a", "libmp3lame", "-b:a", "128k",
            output_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return

    def get_music_path(m_name: str) -> str:
        m_clean = os.path.basename(m_name)
        for cand in [
            os.path.join("music", m_clean),
            os.path.join("ddma", "music", m_clean),
            os.path.join("..", "ddma", "music", m_clean),
            os.path.join("..", "music", m_clean),
            os.path.join("docs", "assets", "music", m_clean)
        ]:
            if os.path.exists(cand):
                return cand
        return os.path.join("music", m_clean)

    inputs = []
    filter_parts = []
    labels = []
    in_idx = 0
    t_cursor = 0.0

    for s_idx, seg in enumerate(segments):
        seg_type = seg.get("type")
        if seg_type == "audio":
            s_start = float(seg.get("start", 0.0))
            s_end = float(seg.get("end", 0.0))
            s_dur = max(0.1, s_end - s_start)

            if s_idx > 0 and segments[s_idx - 1].get("type") == "music":
                cf_dur = float(segments[s_idx - 1].get("crossfade", 1.0))
                t_speech = max(0.0, t_cursor - cf_dur)
                t_speech_ms = int(round(t_speech * 1000))
                inputs.extend(["-ss", f"{s_start:.3f}", "-t", f"{s_dur:.3f}", "-i", audio_source_path])
                filter_parts.append(
                    f"[{in_idx}:a]adelay={t_speech_ms}|{t_speech_ms}[sp{in_idx}];"
                )
                labels.append(f"[sp{in_idx}]")
                t_cursor = t_speech + s_dur
            else:
                t_speech = t_cursor
                t_speech_ms = int(round(t_speech * 1000))
                inputs.extend(["-ss", f"{s_start:.3f}", "-t", f"{s_dur:.3f}", "-i", audio_source_path])
                if t_speech_ms > 0:
                    filter_parts.append(f"[{in_idx}:a]adelay={t_speech_ms}|{t_speech_ms}[sp{in_idx}];")
                    labels.append(f"[sp{in_idx}]")
                else:
                    labels.append(f"[{in_idx}:a]")
                t_cursor = t_speech + s_dur
            in_idx += 1

        elif seg_type == "music":
            m_file = seg.get("music_file", "Howling (Sting) - Gunnar Olsen.mp3")
            m_path = get_music_path(m_file)
            dur_m = float(seg.get("duration", 5.5))
            fade_out = float(seg.get("fade_out", 2.0))
            fade_out_st = max(0.0, dur_m - fade_out)
            silence_front = float(seg.get("silence_before", seg.get("gap", 0.2)))

            t_sting = t_cursor + silence_front
            t_sting_ms = int(round(t_sting * 1000))

            if not os.path.exists(m_path) or m_file == "none":
                inputs.extend(["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={dur_m:.3f}"])
            else:
                inputs.extend(["-i", m_path])

            filter_parts.append(
                f"[{in_idx}:a]atrim=0:{dur_m:.3f},afade=t=out:st={fade_out_st:.3f}:d={fade_out:.3f},adelay={t_sting_ms}|{t_sting_ms}[m{in_idx}];"
            )
            labels.append(f"[m{in_idx}]")
            in_idx += 1
            t_cursor = t_sting + dur_m

    filter_parts.append(
        f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:dropout_transition=0:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    )

    cmd_mix = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", "".join(filter_parts),
        "-map", "[out]",
        "-c:a", "libmp3lame", "-b:a", "128k",
        output_path
    ]
    res_mix = subprocess.run(cmd_mix, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_mix.returncode != 0:
        raise Exception(f"FFmpeg error compiling preview: {res_mix.stderr}")


def run_transcribe(project_id, audio_path, out_json_path, info_path):
    try:
        print(f"[{project_id}] Background Whisper transcription started on {audio_path}")
        python_exe = sys.executable
        cmd = [
            python_exe,
            "ddma.py",
            "transcribe",
            "--audio", audio_path,
            "--out", out_json_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print(f"[{project_id}] Background Whisper transcription completed successfully.")
            
            # Extract episode number if available
            ep_num_match = re.search(r'\d+', project_id)
            if ep_num_match:
                ep_num = int(ep_num_match.group(0))
            else:
                existing_nums = [244]
                if os.path.exists("projects"):
                    for p in os.listdir("projects"):
                        m = re.search(r'\d+', p)
                        if m: existing_nums.append(int(m.group(0)))
                ep_num = max(existing_nums) + 1
            
            # Read project info
            info = {}
            if os.path.exists(info_path):
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
            title = info.get("name", f"Episode {ep_num}")
            
            print(f"[{project_id}] Kicking off automated clip ingestion pipeline...")
            ingest_cmd = [
                python_exe,
                "ddma.py",
                "ingest-episode",
                "--audio", audio_path,
                "--episode", str(ep_num),
                "--title", title
            ]
            subprocess.run(ingest_cmd, check=True)
            print(f"[{project_id}] Background project creation pipeline completed successfully!")

            if os.path.exists(info_path):
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                info["status"] = "ready"
                info["audio_filename"] = info.get("audio_filename") or info.get("audio_file") or os.path.basename(audio_path)
                info["audio_file"] = info["audio_filename"]
                with open(info_path, "w", encoding="utf-8") as f:
                    json.dump(info, f, indent=4)
        else:
            raise Exception(res.stderr or "Whisper exited with non-zero code.")
    except Exception as e:
        print(f"[{project_id}] Background Whisper transcription error: {e}")
        # Update status to error
        try:
            if os.path.exists(info_path):
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                info["status"] = "error"
                info["error_message"] = str(e)
                with open(info_path, "w", encoding="utf-8") as f:
                    json.dump(info, f, indent=4)
        except Exception as e:
            print(f"ERROR: failed writing error status to {info_path}: {e}")


# Migration Helper for Legacy Root files
def migrate_legacy_files():
    # Clean up any leftover trash folders from previous sessions
    try:
        if os.path.exists("projects"):
            for folder in os.listdir("projects"):
                if folder.startswith(".trash_"):
                    trash_path = os.path.join("projects", folder)
                    try:
                        shutil.rmtree(trash_path)
                    except OSError as e:
                        print(f"WARNING: could not remove trash folder {trash_path}: {e}")
    except OSError as e:
        print(f"WARNING: migrate_legacy_files scan failed: {e}")

    # If legacy files exist in root and we don't have episode_244 project, migrate them automatically
    os.makedirs("projects", exist_ok=True)
    legacy_project_dir = os.path.join("projects", "episode_244")
    
    if not os.path.exists(legacy_project_dir):
        has_legacy = os.path.exists("transcription.json") and os.path.exists("plan.json") and os.path.exists("244.m4a")
        if has_legacy:
            print("Detected legacy root files for Episode 244. Auto-migrating to multi-project layout...")
            try:
                os.makedirs(legacy_project_dir, exist_ok=True)
                # Copy files into project folder
                shutil.copy2("transcription.json", os.path.join(legacy_project_dir, "transcription.json"))
                shutil.copy2("plan.json", os.path.join(legacy_project_dir, "plan.json"))
                shutil.copy2("244.m4a", os.path.join(legacy_project_dir, "audio.m4a"))
                
                # Write metadata
                info = {
                    "id": "episode_244",
                    "name": "Episode 244",
                    "audio_filename": "audio.m4a",
                    "status": "ready"
                }
                with open(os.path.join(legacy_project_dir, "project_info.json"), "w", encoding="utf-8") as f:
                    json.dump(info, f, indent=4)
                print("Episode 244 successfully migrated to projects/episode_244/")
            except Exception as e:
                print(f"Warning: Failed to migrate legacy files: {e}")

    # Auto-seed published episodes from docs/episodes/ for fresh git clones
    for ep in ["244", "245", "246"]:
        ep_dir = os.path.join("projects", f"episode_{ep}")
        docs_plan = os.path.join("docs", "episodes", ep, "plan.json")
        if not os.path.exists(ep_dir) and os.path.exists(docs_plan):
            print(f"[AUTO-SEED] Seeding starter project Episode {ep} from docs/episodes/{ep}/...")
            try:
                os.makedirs(ep_dir, exist_ok=True)
                shutil.copy2(docs_plan, os.path.join(ep_dir, "plan.json"))
                shutil.copy2(docs_plan, os.path.join(ep_dir, "plan_snapshot.json"))
                
                audio_name = f"{ep}.m4a"
                info = {
                    "id": f"episode_{ep}",
                    "name": f"Episode {ep}",
                    "title": f"Episode {ep}",
                    "audio_filename": audio_name,
                    "audio_file": audio_name,
                    "status": "ready"
                }
                with open(os.path.join(ep_dir, "project_info.json"), "w", encoding="utf-8") as f:
                    json.dump(info, f, indent=4)
                print(f"[AUTO-SEED] Starter project Episode {ep} successfully seeded!")
            except Exception as seed_err:
                print(f"Warning: Failed to auto-seed Episode {ep}: {seed_err}")


def get_mosaic_default_prompt():
    settings_path = "settings.json"
    if not os.path.exists(settings_path):
        alt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.json")
        if os.path.exists(alt_path):
            settings_path = alt_path
    if os.path.exists(settings_path):
        try:
            s_data = safe_load_json(settings_path)
            if s_data and isinstance(s_data, dict):
                prompt = s_data.get("mosaic_default_prompt")
                if prompt:
                    return prompt
        except Exception as se:
            print(f"Warning: Failed to load settings.json for prompt: {se}")
            
    return (
        "MOTION DESIGN INSTRUCTIONS (YOUTUBE SHORTS - around 150 to 180 seconds long)\n\n"
        "- Cover the entire timeline of the video with Dan Koe-style motion graphics. Visual coverage must be active and persistent from 0:00 to the very last second with ZERO blank frames.\n\n"
        "- Maintain uniform graphic density across all segments.\n\n"
        "- Plan 10 to 12 continuous segments of roughly ~ 15 seconds each, perfectly mapped to the clip length. Each segment renders a dynamic diagrammatic graphic with changing visual steps and text reveals.\n\n"
        "- Assume background video is a blank black glossy screen (#000000). Keep persistent visuals (animations, conceptual geometry, or text) throughout. Segments must hand off to each other seamlessly like a relay race.\n\n"
        "--------------------------------------------------\n"
        "PACING & ANIMATION RULES\n"
        "--------------------------------------------------\n"
        "- No static holds beyond 6 seconds. Introduce visual changes or step reveals every 2-4 seconds.\n"
        "- Use only basic transforms: opacity, position, scale. Keep animations single-property per element.\n"
        "- Prefer step-based reveals over continuous complex motion. Avoid preset/template animations.\n"
        "- No gaps in infographic coverage. Zero external asset dependencies."
    )


def get_factory_mosaic_prompt():
    """Shipped factory fallback for the Mosaic default prompt.

    Reads the tracked canonical copy (ddma/scratch/mosaic_factory_defaults.json,
    linked from GEMINI.md). Returns the stored settings value NEVER -- Reset
    uses this so it can recover even a poisoned stored prompt. If the backup
    file is missing, falls back to the hardcoded gold literal below (same text
    the backup file carries).
    """
    try:
        factory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "mosaic_factory_defaults.json")
        with open(factory_path, "r", encoding="utf-8") as ff:
            return json.load(ff)["mosaic_default_prompt"]
    except Exception:
        pass
    return (
        "MOTION DESIGN INSTRUCTIONS (YOUTUBE SHORTS - around 150 to 180 seconds long)\n"
        "\n"
        "- Cover the entire timeline of the video with Dan Koe-style motion graphics. Visual coverage must be active and persistent from 0:00 to the very last second with ZERO blank frames.\n"
        "\n"
        "- Maintain uniform graphic density across all segments.\n"
        "\n"
        "- Plan 10 to 12 continuous segments of roughly ~ 15 seconds each, perfectly mapped to the clip length. Each segment renders a dynamic diagrammatic graphic with changing visual steps and text reveals.\n"
        "\n"
        "- Assume background video is a blank black glossy screen (#000000). Keep persistent visuals (animations, conceptual geometry, or text) throughout. Segments must hand off to each other seamlessly like a relay race.\n"
        "\n"
        "--------------------------------------------------\n"
        "PACING & ANIMATION RULES\n"
        "--------------------------------------------------\n"
        "- No static holds beyond 6 seconds. Introduce visual changes or step reveals every 2-4 seconds.\n"
        "- Use only basic transforms: opacity, position, scale. Keep animations single-property per element.\n"
        "- Prefer step-based reveals over continuous complex motion. Avoid preset/template animations.\n"
        "- No gaps in infographic coverage. Zero external asset dependencies."
    )


def build_mosaic_prompt_with_context(title, transcript=None, custom_instructions=None):
    mogr_base_rules = get_mosaic_default_prompt()
    prompt_content = (
        f"{mogr_base_rules}\n\n"
        "--------------------------------------------------\n"
        "DYNAMIC CLIP CONTEXT\n"
        "--------------------------------------------------\n"
        f"- Visual Theme / Topic: {title}"
    )
    if transcript:
        clean_transcript = transcript.strip()
        prompt_content += (
            f"\n- Audio Content Context (for visual inspiration and Dan Koe text reveals): {clean_transcript}"
        )
    if custom_instructions:
        prompt_content += f"\n- SPECIAL MOTION GRAPHICS INSTRUCTIONS: {custom_instructions}"
        
    return prompt_content


def get_gemini_default_prompt():
    return (
        "You are the Creative Remix Agent for the DeepDive Media Automator (DDMA).\n"
        "Your task is to recast the segments, title, and bridge transition text of Clip {clip_num} in the plan.\n\n"
        "### Creative & Structural Rules:\n"
        "1. **Total Duration**: The total duration of the clip MUST be strictly under 2 minutes and 55 seconds (175 seconds).\n"
        "   Calculated as: `Total = Sum(segment_durations) - Sum(segment_crossfades)`.\n"
        "2. **Storyboard Structure**:\n"
        "   - Begin with a short welcome hook / high-power speech segment (10-20 seconds) from the transcript.\n"
        "   - Followed by a quick music sting (5.5 seconds long, 0.2s silence_before, 2.0s fade_out, 1.0s crossfade, 1.0 volume).\n"
        "   - Followed by the main audio segment (core deliberation + spoken outro teaser, entering at 100% full volume over the last 1.0s of the fading music sting).\n"
        "   - Followed by ending music (`deepDive-conclusion.mp3`, 5.5s, 0.2s silence_before, 2.0s fade_out, 0.0s crossfade, 1.0 volume).\n"
        "3. **Intro Card Title (STRICTLY MAX 3 WORDS for Clip 1+)**:\n"
        "   - For `Clip 0` (`num == 0`): Use the overarching Episode Title (e.g. \"What Exactly Is Reality?\"), rendered with `EPISODE <number>` and NO Part number.\n"
        "   - For `Clip 1+` (`num >= 1`): Title MUST be **STRICTLY MAXIMUM 3 WORDS** designed to capture attention — typically the scientific concept, scientist name, or core idea (e.g. \"8D Totality\", \"Sensory Split\", \"Division Algebras\", \"Quaternions\").\n"
        "4. **Outro Card Bridge Text (STRICTLY MAX 5 WORDS)**:\n"
        "   - Provide a single ultra-concise curiosity question/exclamation in \"bridge_text\" (a 1-element list of strings) that is **STRICTLY MAXIMUM 5 WORDS** (e.g. \"What is 8D Totality !\", \"Why Four Division Algebras ?\").\n"
        "   - NEVER write \"Coming up in Clip...\" or long story sentences because the hosts already speak that aloud in the audio!\n"
        "5. **Standalone Thought Integrity**: Every clip MUST stand on its own as a complete, coherent, and interesting statement.\n"
        "6. **Deep Dive Music Sting Restrictions**: Under NO circumstances use deepDive-strong in video clips (reserved strictly for the full podcast). Clip structure is always: Hook audio segment -> Mid music sting (alternating Bluesy Vibes and Howling) -> Body audio segment -> Outro music sting (deepDive-conclusion.mp3)."
    )


def get_gemini_episode_default_prompt():
    return (
        "You are the Executive Producer & AI Storyboard Curator for the DeepDive Media Automator (DDMA).\n"
        "Your task is to analyze the full raw episode transcript and structure it into a sequence of high-engagement, standalone podcast/social video clips.\n\n"
        "### 🎬 EPISODE STORYBOARDING & CLIP DYNAMICS RULES:\n"
        "1. **0-Based Clip Numbering (`<ep>-0`, `<ep>-1`, ...)**:\n"
        "   - Number the Prologue / Cold Open clip (before hosts announce \"Clip 1\") as `\"num\": 0` (`<ep>-0`).\n"
        "   - Number all subsequent clips `\"num\": 1`, `\"num\": 2`, etc. (`<ep>-1`, `<ep>-2`, ...) so that clip numbers strictly mirror the spoken word (\"Clip 1\", \"Clip 2\", etc. in the transcript).\n"
        "2. **Strict Duration Limits**: Each clip MUST be between 60 seconds (1 minute) and 165 seconds (2 minutes 45 seconds). No clip may ever exceed 2 minutes 55 seconds (175 seconds).\n"
        "3. **Tripartite Spoken Flow & Music Stings**: Every clip is structured into: (1) Intro Title Card (1.5s), (2) Speech Punchline / Hook (10-20s audio segment), (3) Mid Music Sting (5.5s, alternating `Bluesy Vibes (Sting) - Doug Maxwell_Media Right Productions.mp3` and `Howling (Sting) - Gunnar Olsen.mp3`), (4) Core Deliberation + Spoken Outro Teaser Audio Segment, (5) Outro Music Sting (`deepDive-conclusion.mp3`, 5.5s), and (6) Outro Curiosity Question Card (5.0s).\n"
        "4. **Concise Intro Card Titles (MAX 3 WORDS for Clip 1+)**:\n"
        "   - For `Clip 0` (`num: 0`): Assign the overarching Episode Title (e.g. `\"What Exactly Is Reality?\"`), displayed with `EPISODE <number>` and NO Part number.\n"
        "   - For `Clip 1+` (`num >= 1`): Assign a title of **STRICTLY MAXIMUM 3 WORDS** designed to capture attention — typically the scientific concept, scientist name, or core idea (e.g. `\"8D Totality\"`, `\"Sensory Split\"`, `\"Division Algebras\"`, `\"Quaternions\"`). Drop leading articles like \"The\" if needed to stay ≤ 3 words.\n"
        "5. **Concise Outro Card Bridge Text (MAX 5 WORDS)**:\n"
        "   - Under `\"bridge_text\"` (a 1-element list of strings), provide an ultra-concise punchy question or exclamation of **STRICTLY MAXIMUM 5 WORDS** introducing the next clip's core concept (e.g. `[\"What is 8D Totality !\"]`, `[\"Why Four Division Algebras ?\"]`).\n"
        "   - NEVER write \"Coming up in the next clip...\" or multi-clause sentences because the hosts are already speaking that transition aloud!\n"
        "6. **Verbatim Word-Level Quote Anchors**: For each clip, output exact 3-7 word verbatim transcript quote fragments (`\"start_quote\"` and `\"end_quote\"`) matching the spoken transcript text so DDMA snaps clip boundaries sample-accurately to Whisper word timestamps.\n\n"
        "### 📋 OUTPUT FORMAT (JSON ARRAY ONLY):\n"
        "Return ONLY a valid JSON array of clip objects with no markdown codeblock wrapping or extra conversational text:\n"
        "[\n"
        "  {\n"
        "    \"num\": 0,\n"
        "    \"title\": \"What Exactly Is Reality?\",\n"
        "    \"start_quote\": \"exact 3-7 words from start of prologue\",\n"
        "    \"end_quote\": \"exact 3-7 words from end of prologue\",\n"
        "    \"approx_start\": 0.0,\n"
        "    \"approx_end\": 135.0,\n"
        "    \"music\": \"Bluesy Vibes (Sting) - Doug Maxwell_Media Right Productions.mp3\",\n"
        "    \"music_volume\": 1.0,\n"
        "    \"bridge_text\": [\"What is 8D Totality !\"]\n"
        "  },\n"
        "  {\n"
        "    \"num\": 1,\n"
        "    \"title\": \"8D Totality\",\n"
        "    \"start_quote\": \"exact 3-7 words from start of clip 1\",\n"
        "    \"end_quote\": \"exact 3-7 words from end of clip 1\",\n"
        "    \"approx_start\": 135.0,\n"
        "    \"approx_end\": 275.0,\n"
        "    \"music\": \"Howling (Sting) - Gunnar Olsen.mp3\",\n"
        "    \"music_volume\": 1.0,\n"
        "    \"bridge_text\": [\"What Is Sensory Split ?\"]\n"
        "  }\n"
        "]"
    )




def build_gemini_prompt(project_id, clip_num, directive=None):
    plan_data = load_plan(project_id)
    if not plan_data:
        raise Exception(f"plan.json not found for project {project_id}.")
    
    target_clip = None
    preceding_locked_clips = []
    for c in plan_data:
        c_num = int(c.get("num", -1))
        if c_num == int(clip_num):
            target_clip = c
        elif c_num < int(clip_num) and c.get("locked"):
            preceding_locked_clips.append(c)
            
    # Limit context to the last 5 preceding locked clips and reverse their order
    # (so the penultimate/most recent clip appears first in the prompt)
    preceding_locked_clips = preceding_locked_clips[-5:]
    preceding_locked_clips.reverse()
    
    if not target_clip:
        raise Exception(f"Clip {clip_num} not found in project plan.")
    
    trans_path = os.path.join(project_dir, "transcription.json")
    if not os.path.exists(trans_path):
        raise Exception("transcription.json not found in project directory.")
    
    with open(trans_path, "r", encoding="utf-8") as f:
        trans_data = json.load(f)
    
    orig_start = None
    orig_end = None
    for seg in target_clip.get("segments", []):
        if seg.get("type") == "audio":
            s = float(seg.get("start", 0))
            e = float(seg.get("end", 0))
            if orig_start is None or s < orig_start:
                orig_start = s
            if orig_end is None or e > orig_end:
                orig_end = e
    
    if orig_start is None:
        orig_start = 0.0
        orig_end = 120.0
    
    neigh_start = max(0.0, orig_start - 10.0)
    neigh_end = orig_start + 600.0
    
    all_segments = trans_data.get("segments", [])
    neigh_lines = []
    for s in all_segments:
        s_start = float(s.get("start", 0))
        s_end = float(s.get("end", 0))
        if s_start >= neigh_start and s_end <= neigh_end:
            text = s.get("text", "").strip()
            neigh_lines.append(f"[{s_start:.2f} - {s_end:.2f}] {text}")
    neigh_text = "\n".join(neigh_lines)
    
    music_dir = "music"
    music_files = []
    if os.path.exists(music_dir):
        music_files = [f for f in os.listdir(music_dir) if f.lower().endswith(('.mp3', '.wav'))]
    
    base_instructions = get_gemini_default_prompt()
    if "{clip_num}" in base_instructions:
        base_instructions = base_instructions.replace("{clip_num}", str(clip_num))
        
    prompt = f"{base_instructions}\n"
    if directive:
        prompt += f"\n### IMPORTANT - USER REMIX DIRECTIVE (Follow this instruction strictly!):\n- {directive}\n\n"

    prompt += f"""### Preceding Locked Clips (Context):
{json.dumps(preceding_locked_clips, indent=2)}

### Transcript Segments in the Neighborhood:
# Formatted as: [start_time_seconds - end_time_seconds] Text
{neigh_text}

### Available Music Stings:
{json.dumps(music_files, indent=2)}

You MUST respond with a single JSON object for Clip {clip_num} matching the schema below. Do not include markdown code block formatting or explanations outside the JSON object:
{{
  "num": {clip_num},
  "title": "Recasted Clip Title",
  "bridge_text": [
    "Curiosity question?"
  ],
  "segments": [
    {{
      "type": "audio",
      "start": 0.0,
      "end": 45.5,
      "duration": 45.5,
      "text": "Exact text matching transcription segments"
    }},
    {{
      "type": "music",
      "music_file": "Bluesy Vibes (Sting) - Doug Maxwell_Media Right Productions.mp3",
      "duration": 4.5,
      "crossfade": 0.3,
      "volume": 1.0
    }}
  ],
  "locked": false
}}
"""
    return prompt



def get_storyboard_filepath(project_id: str, clip_num) -> str:
    project_dir = os.path.join("projects", project_id)
    storyboards_dir = os.path.join(project_dir, "storyboards")
    os.makedirs(storyboards_dir, exist_ok=True)
    return os.path.join(storyboards_dir, f"clip_{clip_num}_storyboard.json")


def generate_or_load_storyboard_data(project_id: str, clip_num, force_regen: bool = False, custom_directive: str = "") -> dict:
    filepath = get_storyboard_filepath(project_id, clip_num)
    
    if os.path.exists(filepath) and not force_regen and not custom_directive:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("scenes") and len(data.get("scenes")) >= 2:
                    return data
        except Exception:
            pass

    plan_path = os.path.join("projects", project_id, "plan.json")
    plan_data = load_plan(project_id)
    if not plan_data and os.path.exists("plan.json"):
        print(f"WARNING: hub + cache plans empty for {project_id} -- reading root plan.json fallback (may be stale).")
        try:
            plan_data = safe_load_json("plan.json") or []
        except Exception as e:
            print(f"WARNING: root plan.json fallback unreadable ({e}) -- using empty plan.")
            plan_data = []
    t_clip = next((c for c in plan_data if str(c.get("num")) == str(clip_num)), None)
    if not t_clip:
        raise Exception(f"Clip {clip_num} not found in plan {plan_path}")

    body_dur = float(t_clip.get("audio_duration") or t_clip.get("duration") or 120.0)
    existing_scenes = t_clip.get("infographic_scenes") or []
    
    if existing_scenes and not force_regen and not custom_directive:
        scenes = existing_scenes
    else:
        import manim_infographic_engine
        settings = load_settings()
        api_key = settings.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
        g_mod = genai if (HAS_GENAI and configure_gemini(api_key)) else None
        scenes = manim_infographic_engine.generate_pedagogical_storyboard(
            t_clip, body_duration=body_dur, intro_offset=1.5,
            custom_instructions=custom_directive, genai_mod=g_mod,
            force_regenerate=force_regen
        )
        t_clip["infographic_scenes"] = scenes
        save_plan(project_id, plan_data)

    storyboard_obj = {
        "_rule_engine": {
            "standard": "Feynman-Needham Pedagogical Standard",
            "canvas": "1080x1080 square Manim window, centered at y in [420, 1500] on 1080x1920 vertical canvas",
            "theme": "Pure Monochrome Shining White (#FFFFFF, #E2E8F0) on Black Glossy Background (#000000)",
            "pacing": "Minimum 2-4 visual changes per minute (~15-second pacing, 8-12 scenes for 120-180s clip)",
            "visual_philosophy": "Super-Dumb bold figurative storytelling. Zero small telemetry/data clutter.",
            "line_weights": "Bold 4px-14px lines with luminous glows. No super-thin lines.",
            "safe_zones": "Captions at y≈500..555. Top chrome y in [0, 450] strictly clear.",
            "archetypes_guide": {
                "balance_scale": "Fulcrum, economic equilibrium, burn vs revenue",
                "leaky_bucket": "Thermodynamic loss, inflow vs drainage",
                "funnel_filter": "Bottlenecks, selection, throughput compression",
                "flywheel_gear": "Compounding loops, rotational inertia, acceleration",
                "network_artery": "Interconnection, trade routes vs isolation fallacy",
                "foundation_stack": "Solid base vs fragile top layers",
                "robot_unplugged": "The physical robot fallacy (dead battery, missing plug)",
                "circuit_switch": "Logic gate, threshold barrier, state trigger",
                "pulse_resonance": "Frequency alignment, acoustic harmony, signal clarity",
            "teenager_basement": "Genius teenager coding in basement with happy tail-wagging dog"
            }
        },
        "clip_num": int(clip_num),
        "clip_title": t_clip.get("title", ""),
        "total_duration": round(body_dur, 2),
        "custom_directive": custom_directive,
        "scenes": scenes
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(storyboard_obj, f, indent=2)

    return storyboard_obj


class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def compile_segments(self, segments, output_path, audio_source_path):
        compile_segments_helper(segments, output_path, audio_source_path)

    def do_POST(self):
        import re
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        
        if parsed_url.path == '/api/cockpit/launch':
            # Ensure the Workspace home (cockpit :8088) server answers, starting it
            # on this machine when it is down. Mirrors the /api/beats/launch
            # precedent. The browser host comes from the request Host header so the
            # returned URL stays on the host the user actually opened.
            try:
                host_hdr = (self.headers.get('Host') or '').split(':')[0] or '127.0.0.1'
                cockpit_url = f"http://{host_hdr}:8088/"
                up = False
                try:
                    r = requests.get("http://127.0.0.1:8088/", timeout=2)
                    up = r.status_code < 500
                except Exception:
                    up = False
                if not up:
                    ingest_dir = DDMA_DIR.parent / "ingest"
                    cockpit_script = ingest_dir / "server.py"
                    if not cockpit_script.exists():
                        raise Exception("ingest/server.py not found next to ddma/.")
                    try:
                        prev = globals().get('cockpit_server_process')
                        if not (prev and prev.poll() is None):
                            globals()['cockpit_server_process'] = subprocess.Popen(
                                [sys.executable, str(cockpit_script)],
                                cwd=str(ingest_dir),
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
                    except Exception as pe:
                        raise Exception(f"Could not start the cockpit server: {pe}")
                    for _ in range(30):
                        time.sleep(0.5)
                        try:
                            r = requests.get("http://127.0.0.1:8088/", timeout=2)
                            if r.status_code < 500:
                                up = True
                                break
                        except Exception:
                            pass
                if not up:
                    raise Exception("still not responding after start.")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "cockpit_url": cockpit_url}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Workspace server is not running on :8088 " + str(e)}).encode('utf-8'))
                return

        if parsed_url.path == '/help-bot':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                if not HAS_GENAI:
                    reply = "Help Error: The 'google-generativeai' library is not installed in the python environment. Run 'pip install google-generativeai' to enable the help panel."
                else:
                    api_key = os.environ.get("GEMINI_API_KEY")
                    if not api_key and os.path.exists("settings.json"):
                        try:
                            with open("settings.json", "r", encoding="utf-8") as sf:
                                s_data = json.load(sf)
                                api_key = s_data.get("gemini_api_key")
                        except Exception as se:
                            print(f"Warning: Failed to load settings.json: {se}")
                    
                    if not configure_gemini(api_key):
                        reply = "Help Error: Neither 'gemini-creds.json' credentials nor 'GEMINI_API_KEY' in settings are configured. Please set them up in DDMA first!"
                    else:
                        
                        # Load request body
                        req_json = json.loads(post_data.decode('utf-8'))
                        user_message = req_json.get("message", "")
                        history = req_json.get("history", [])
                        
                        # Load context files (cache/read on the fly)
                        context = ""
                        for doc_file in ["README.md", "CREATIVE_PROCESS.md", os.path.join(".agents", "AGENTS.md"), "settings.json"]:
                            if os.path.exists(doc_file):
                                try:
                                    with open(doc_file, "r", encoding="utf-8") as df:
                                        context += f"\n\n=== FILE: {doc_file} ===\n" + df.read()
                                except Exception as fe:
                                    print(f"Warning: Failed to read {doc_file} for help bot: {fe}")
                        
                        system_instruction = (
                            "You are the DDMA Help Assistant, an expert AI chatbot designed to assist users in understanding "
                            "and using the DeepDive Media Automator (DDMA).\n\n"
                            "### IMPORTANT SYSTEM RULE:\n"
                            "- To change or customize default Mosaic prompts (Motion Design Instructions) or Gemini Remix instructions, "
                            "users DO NOT need to edit Python code files. They can simply click the ⚙️ Settings button in the bottom left "
                            "of the Curator UI and customize the prompts directly inside the textareas. These are saved in settings.json.\n\n"
                            "Your goal is to answer UI workflow, architectural, installation, Whisper, and creative curation questions "
                            "accurately and concisely using the documentation and settings structure provided below. Keep your responses "
                            "user-friendly and formatted in clean, concise markdown.\n\n"
                            f"=== DOCUMENTATION CONTEXT ===\n{context}"
                        )
                        
                        # Convert history format
                        contents = []
                        for h in history:
                            contents.append({
                                "role": "user" if h.get("role") == "user" else "model",
                                "parts": [h.get("text", "")]
                            })
                        contents.append({
                            "role": "user",
                            "parts": [user_message]
                        })
                        
                        # Generate content with fallback list of valid models
                        model_names = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.0-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]
                        reply = None
                        last_err = None
                        for model_name in model_names:
                            try:
                                model = genai.GenerativeModel(
                                    model_name=model_name,
                                    system_instruction=system_instruction
                                )
                                response = model.generate_content(contents)
                                reply = response.text
                                break
                            except Exception as e:
                                print(f"Co-Pilot model {model_name} failed: {e}")
                                last_err = e
                        if not reply:
                            err_str = str(last_err)
                            if "429" in err_str or "quota" in err_str.lower():
                                reply = "⚠️ Gemini API Quota Exceeded (429). Please set your personal Gemini API Key in ⚙️ Settings -> Co-Pilot Integration, or wait a minute for your quota to reset."
                            else:
                                reply = f"Co-Pilot Error: Failed to generate content. Last error: {last_err}"
                        
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))
                return
            except Exception as e:
                print(f"Error in help chatbot: {e}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"reply": f"Co-Pilot Error: {str(e)}"}).encode('utf-8'))
                return
                
        elif parsed_url.path == '/save-project-plan':
            project_id = params.get('id', [None])[0]
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                if not project_id:
                    raise Exception("Missing project id parameter.")
                
                project_dir = os.path.join("projects", project_id)
                if not os.path.exists(project_dir):
                    raise Exception(f"Project directory {project_id} not found.")
                
                # Load the old plan to compare metadata changes
                old_plan = []
                plan_file_path = os.path.join(project_dir, 'plan.json')
                # Capture the revision this server last saw BEFORE reloading: save_plan()
                # must compare against it, not the just-reloaded copy (which would make the
                # stale-write guard vacuous). Empty (e.g. after a restart) = no usable base,
                # so the guard is skipped for this save (fail-open, documented).
                save_expected_rev = _plan_rev_cache.get(str(_episode_from_project_id(project_id)))
                try:
                    old_plan = load_plan(project_id) or []
                except Exception as e:
                    print(f"Warning: Failed to load old plan for comparison: {e}")
                
                json_data = json.loads(post_data.decode('utf-8'))
                if isinstance(json_data, dict) and "clips" in json_data:
                    clips_array = json_data["clips"]
                elif isinstance(json_data, dict) and "plan" in json_data:
                    clips_array = json_data["plan"]
                else:
                    clips_array = json_data
                
                # Save hub FIRST, then local cache, then Active Master paths (fail loudly on hub outage)
                save_plan(project_id, clips_array, expected_rev=save_expected_rev)
                    
                # Sync to docs/episodes/EP_NUM/plan.json and docs/episodes.json (plus ../src/ddma/docs/ mirror)
                ep_match = re.search(r'\d+', project_id)
                ep_str = ep_match.group(0) if ep_match else None
                if ep_str:
                    for docs_root in ["docs", os.path.join("..", "src", "ddma", "docs")]:
                        docs_ep_plan = os.path.join(docs_root, "episodes", ep_str, "plan.json")
                        if os.path.exists(os.path.dirname(docs_ep_plan)):
                            try:
                                shutil.copy2(plan_file_path, docs_ep_plan)
                            except Exception as e:
                                print(f"Error syncing {docs_ep_plan}: {e}")
                    
                    # (hub sync now happens hub-first inside save_plan(); see above)

                    if json_data and len(json_data) > 0 and json_data[0].get("title"):
                        c1_title = json_data[0]["title"]
                        for docs_root in ["docs", os.path.join("..", "src", "ddma", "docs")]:
                            ep_mf_path = os.path.join(docs_root, "episodes.json")
                            if os.path.exists(ep_mf_path):
                                try:
                                    with open(ep_mf_path, "r", encoding="utf-8") as mf:
                                        m_data = json.load(mf)
                                    for item in m_data:
                                        if str(item.get("id")) == ep_str or str(item.get("number")) == ep_str:
                                            item["title"] = c1_title
                                            item["fullTitle"] = f"Episode {ep_str}: {c1_title}"
                                    with open(ep_mf_path, "w", encoding="utf-8") as mf:
                                        json.dump(m_data, mf, indent=2)
                                except Exception as e:
                                    print(f"Error updating {ep_mf_path} title: {e}")
                    
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b"Success")
                return
            except Exception as e:
                print(f"Error saving plan for {project_id}: {e}")
                self.send_error(500, f"Error saving plan: {e}")
                return
                
        elif parsed_url.path == '/remix-clip':
            # [API-ONLY ENDPOINT] Recasts an individual clip with Gemini based on preceding locked clips
            project_id = params.get('id', [None])[0]
            clip_num = int(params.get('num', [-1])[0])
            
            directive = ""
            custom_prompt = ""
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    body_json = json.loads(post_data.decode('utf-8'))
                    directive = body_json.get("directive", "").strip()
                    custom_prompt = body_json.get("prompt", "").strip()
            except Exception as body_ex:
                print(f"Warning: Failed to parse remix body: {body_ex}")
                
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                if clip_num < 0:
                    raise Exception("Invalid clip number.")
                
                # Check for Gemini API key (Env first, then settings.json)
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key and os.path.exists("settings.json"):
                    try:
                        with open("settings.json", "r", encoding="utf-8") as sf:
                            s_data = json.load(sf)
                            api_key = s_data.get("gemini_api_key")
                    except Exception as se:
                        print(f"Warning: Failed to load settings.json: {se}")
                
                if not api_key and not os.path.exists("gemini-creds.json"):
                    raise Exception("GEMINI_API_KEY settings config is not set, and gemini-creds.json was not found.")
                
                project_dir = os.path.join("projects", project_id)
                plan_path = os.path.join(project_dir, "plan.json")
                rmx_plan = load_plan(project_id)
                if not rmx_plan:
                    raise Exception(f"plan.json not found for project {project_id}.")
                target_clip_rmx = next((c for c in rmx_plan if int(c.get("num", -1)) == clip_num), None)
                if not target_clip_rmx:
                    raise Exception(f"Clip {clip_num} not found in plan.")
                if not target_clip_rmx.get("locked"):
                    self.send_response(403)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": f"Clip {clip_num} is unlocked. Lock clip before remixing."}).encode("utf-8"))
                    return
                
                if custom_prompt:
                    prompt = custom_prompt
                else:
                    prompt = build_gemini_prompt(project_id, clip_num, directive=directive)

                # Call Gemini with fallback chain of valid models
                configure_gemini(api_key)
                model_names = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.0-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]
                response = None
                last_err = None
                
                for model_name in model_names:
                    try:
                        print(f"[{project_id}][Clip {clip_num}] Attempting remix with model {model_name}...")
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(
                            prompt,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        if response and response.text:
                            print(f"[{project_id}][Clip {clip_num}] Successful response from model {model_name}!")
                            break
                    except Exception as me:
                        print(f"[{project_id}][Clip {clip_num}] Model {model_name} failed: {me}")
                        last_err = me
                        err_str = str(me)
                        if "401" in err_str or "unauthenticated" in err_str.lower() or "invalid authentication" in err_str.lower() or "access_token_type_unsupported" in err_str.lower():
                            raise Exception(
                                "Gemini Authentication Failed (401): The configured Gemini API key is invalid or expired.\n\n"
                                "To fix this:\n"
                                "1. Obtain an active Gemini API key from Google AI Studio (https://aistudio.google.com/app/apikey).\n"
                                "2. In DDMA Cockpit, click '⚙️ Settings' (top right) -> '🤖 Gemini Co-Pilot Prompts' tab.\n"
                                "3. Paste your new API key into 'GEMINI API CREDENTIALS' and click 'Save Settings'."
                            )
                
                if not response or not response.text:
                    err_str = str(last_err)
                    if "429" in err_str or "quota" in err_str.lower():
                        raise Exception("Gemini API Quota Exceeded (429). Please set your personal Gemini API Key in ⚙️ Settings -> Co-Pilot Integration, or wait a minute for your quota to reset.")
                    if "401" in err_str or "unauthenticated" in err_str.lower() or "invalid authentication" in err_str.lower() or "access_token_type_unsupported" in err_str.lower():
                        raise Exception(
                            "Gemini Authentication Failed (401): The configured Gemini API key is invalid or expired.\n\n"
                            "To fix this:\n"
                            "1. Obtain an active Gemini API key from Google AI Studio (https://aistudio.google.com/app/apikey).\n"
                            "2. In DDMA Cockpit, click '⚙️ Settings' (top right) -> '🤖 Gemini Co-Pilot Prompts' tab.\n"
                            "3. Paste your new API key into 'GEMINI API CREDENTIALS' and click 'Save Settings'."
                        )
                    raise last_err or Exception("All Gemini models failed to generate content.")
                
                def clean_and_parse_json(text):
                    text = text.strip()
                    if text.startswith("```"):
                        lines = text.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].strip() == "```":
                            lines = lines[:-1]
                        text = "\n".join(lines).strip()
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        pass
                    first_brace = text.find("{")
                    if first_brace != -1:
                        brace_count = 0
                        for i in range(first_brace, len(text)):
                            if text[i] == "{":
                                brace_count += 1
                            elif text[i] == "}":
                                brace_count -= 1
                                if brace_count == 0:
                                    candidate = text[first_brace:i+1]
                                    try:
                                        return json.loads(candidate)
                                    except json.JSONDecodeError:
                                        pass
                    temp = text
                    while temp.endswith("}"):
                        try:
                            return json.loads(temp)
                        except json.JSONDecodeError:
                            temp = temp[:-1].strip()
                    return json.loads(text)

                try:
                    recasted_clip = clean_and_parse_json(response.text)
                except Exception as je:
                    raise Exception(f"Failed to parse Gemini response as JSON: {je}\nResponse was:\n{response.text}")
                
                recasted_clip["locked"] = target_clip_rmx.get("locked", True)
                recasted_clip.pop("mosaic_run_id", None)

                # Derive start, end, duration from segments if missing
                audio_segs = [s for s in recasted_clip.get("segments", []) if s.get("type") == "audio" and "start" in s and "end" in s]
                if audio_segs:
                    if "start" not in recasted_clip or recasted_clip["start"] is None:
                        recasted_clip["start"] = audio_segs[0]["start"]
                    if "end" not in recasted_clip or recasted_clip["end"] is None:
                        recasted_clip["end"] = audio_segs[-1]["end"]
                    recasted_clip["duration"] = round(recasted_clip["end"] - recasted_clip["start"], 2)

                if recasted_clip.get("title"):
                    raw_title = recasted_clip["title"]
                    clean_title = re.sub(r'[:\\/*?<>|"]', ' - ', raw_title)
                    clean_title = re.sub(r'\s+-\s+-', ' -', clean_title)
                    recasted_clip["title"] = re.sub(r'\s+', ' ', clean_title).strip(" -")

                # Remove any obsolete cut audio and video files for this clip
                import glob
                for old_f in glob.glob(os.path.join("clips", f"*-{clip_num}*")):
                    try:
                        os.remove(old_f)
                    except Exception:
                        pass
                
                # Update plan_data
                remix_expected_rev = _plan_rev_cache.get(str(_episode_from_project_id(project_id)))
                plan_data = load_plan(project_id)
                    
                for idx, c in enumerate(plan_data):
                    if int(c.get("num", -1)) == clip_num:
                        plan_data[idx] = recasted_clip
                        break
                
                # Save hub FIRST, then local cache, then Active Master paths (fail loudly on hub outage)
                save_plan(project_id, plan_data, expected_rev=remix_expected_rev)
                    
                # Sync to docs/plan.json if it exists
                if os.path.exists("docs"):
                    try:
                        shutil.copy2('plan.json', os.path.join('docs', 'plan.json'))
                    except Exception as sync_err:
                        print(f"Error syncing to docs/plan.json: {sync_err}")
                
                # Auto re-compile title card intro & curiosity question outro for this clip if compiled/draft video exists
                auto_recompile_clip(project_id, clip_num)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "clip": recasted_clip}).encode('utf-8'))
                return
            except Exception as e:
                import traceback
                tb_str = traceback.format_exc()
                try:
                    print(f"Error in remixing clip {clip_num}: {e}\n{tb_str}")
                except Exception:
                    pass
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/remix-episode':
            # [API-ONLY ENDPOINT] Re-plans full episode with Gemini while preserving existing locked clip flags
            project_id = params.get('id', [None])[0]
            custom_prompt = ""
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    body_json = json.loads(post_data.decode('utf-8'))
                    if not project_id:
                        project_id = body_json.get("project_id") or body_json.get("id")
                    custom_prompt = body_json.get("prompt", "").strip()
            except Exception as ex_body:
                print(f"Warning parsing /remix-episode body: {ex_body}")

            try:
                if not project_id:
                    raise Exception("Missing project id.")

                project_dir = os.path.join("projects", project_id)
                trans_path = os.path.join(project_dir, "transcription.json")
                if not os.path.exists(trans_path):
                    raise Exception(f"transcription.json not found for {project_id}.")

                with open(trans_path, "r", encoding="utf-8") as tf:
                    t_data = json.load(tf)

                words = []
                for seg in t_data.get("segments", []):
                    words.extend(seg.get("words", []))

                if not words:
                    raise Exception("Transcription words list is empty.")

                prompt_template = custom_prompt or get_gemini_episode_default_prompt()
                transcript_summary = "\n".join([f"[{s.get('start', 0):.1f}s - {s.get('end', 0):.1f}s] {s.get('text', '').strip()}" for s in t_data.get("segments", [])])
                full_prompt = f"{prompt_template}\n\nFULL EPISODE TRANSCRIPT:\n{transcript_summary}"

                # Gemini API setup (Env first, then settings.json)
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key and os.path.exists("settings.json"):
                    try:
                        with open("settings.json", "r", encoding="utf-8") as sf:
                            s_data = json.load(sf)
                            api_key = s_data.get("gemini_api_key")
                    except Exception: pass
                if not api_key and not os.path.exists("gemini-creds.json"):
                    raise Exception("Gemini API key is not configured.")

                configure_gemini(api_key)
                model_names = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.0-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]
                gemini_res_text = None
                for m_name in model_names:
                    try:
                        print(f"[{project_id}] Attempting Episode Remix with model {m_name}...")
                        g_model = genai.GenerativeModel(m_name)
                        response = g_model.generate_content(full_prompt)
                        if response and response.text:
                            gemini_res_text = response.text.strip()
                            break
                    except Exception as m_ex:
                        print(f"Model {m_name} failed: {m_ex}")

                if not gemini_res_text:
                    raise Exception("Failed to receive response from Gemini models.")

                # Extract JSON array from Gemini response
                import re
                json_match = re.search(r'\[\s*\{.*\}\s*\]', gemini_res_text, re.DOTALL)
                if not json_match:
                    raise Exception("Gemini response did not contain a valid JSON array of clips.")
                
                ai_clips_raw = json.loads(json_match.group(0))
                
                # Match quotes to Whisper word timestamps
                from ddma import snap_quote_to_words
                existing_locks = {}
                plan_path_existing = os.path.join(project_dir, "plan.json")
                if os.path.exists(plan_path_existing):
                    try:
                        with open(plan_path_existing, "r", encoding="utf-8") as old_pf:
                            for oc in json.load(old_pf):
                                if "num" in oc:
                                    existing_locks[int(oc["num"])] = bool(oc.get("locked", False))
                    except Exception:
                        pass

                new_plan = []
                for c_idx, raw_c in enumerate(ai_clips_raw):
                    c_num = raw_c.get("num", c_idx) if (ai_clips_raw and ai_clips_raw[0].get("num") == 0) else raw_c.get("num", c_idx + 1)
                    s_quote = raw_c.get("start_quote", "")
                    e_quote = raw_c.get("end_quote", "")
                    approx_start = float(raw_c.get("approx_start", c_idx * 115.0))
                    approx_end = float(raw_c.get("approx_end", approx_start + 115.0))
                    
                    s_time_found, _ = snap_quote_to_words(s_quote, words, search_start_sec=approx_start)
                    _, e_time_found = snap_quote_to_words(e_quote, words, search_start_sec=max(0.0, approx_end - 25.0))
                    
                    s_time = s_time_found if s_time_found is not None else round(approx_start, 3)
                    e_time = e_time_found if e_time_found is not None else round(approx_end, 3)
                    
                    # Safeguard clip duration between 60.0s and 165.0s
                    if e_time <= s_time + 50.0:
                        e_time = round(max(s_time + 90.0, approx_end), 3)
                    if e_time - s_time > 170.0:
                        e_time = round(s_time + 165.0, 3)
                        
                    music_file = raw_c.get("music", "deepDive-soft-ok.mp3" if c_num <= 2 else "deepDive-main.mp3")
                    raw_title = raw_c.get("title", f"Clip {c_num}")
                    clean_title = re.sub(r'[:\\/*?<>|"]', ' - ', raw_title)
                    clean_title = re.sub(r'\s+-\s+-', ' -', clean_title)
                    title = re.sub(r'\s+', ' ', clean_title).strip(" -")
                    
                    # Construct 4-Element Segment Flow: Punchline Hook -> Music Sting -> Main Audio -> Ending Music
                    hook_duration = 12.0
                    hook_end = min(round(s_time + hook_duration, 2), round(e_time - 10.0, 2))
                    
                    if hook_end > s_time + 3.0:
                        segments = [
                            {
                                "type": "audio",
                                "start": s_time,
                                "end": hook_end,
                                "duration": round(hook_end - s_time, 2),
                                "volume": 1.0,
                                "crossfade": 0.0,
                                "text": f"{title} (Punchline Hook)"
                            },
                            {
                                "type": "music",
                                "music_file": music_file,
                                "duration": 5.0,
                                "volume": 1.0,
                                "crossfade": 1.0
                            },
                            {
                                "type": "audio",
                                "start": hook_end,
                                "end": e_time,
                                "duration": round(e_time - hook_end, 2),
                                "volume": 1.0,
                                "crossfade": 0.0,
                                "text": title
                            },
                            {
                                "type": "music",
                                "music_file": music_file,
                                "duration": 5.0,
                                "volume": 1.0,
                                "crossfade": 1.0
                            }
                        ]
                    else:
                        segments = [
                            {
                                "type": "music",
                                "music_file": music_file,
                                "duration": 5.0,
                                "volume": 1.0,
                                "crossfade": 1.0
                            },
                            {
                                "type": "audio",
                                "start": s_time,
                                "end": e_time,
                                "duration": round(e_time - s_time, 2),
                                "volume": 1.0,
                                "crossfade": 0.0,
                                "text": title
                            },
                            {
                                "type": "music",
                                "music_file": music_file,
                                "duration": 5.0,
                                "volume": 1.0,
                                "crossfade": 1.0
                            }
                        ]
                        
                    new_plan.append({
                        "num": c_num,
                        "title": title,
                        "start": s_time,
                        "end": e_time,
                        "locked": existing_locks.get(c_num, False),
                        "music": music_file,
                        "music_volume": 1.0,
                        "bridge_text": raw_c.get("bridge_text", [f"What Is Part {c_num + 1} ?"]),
                        "segments": segments
                    })

                plan_path = os.path.join(project_dir, "plan.json")
                with open(plan_path, "w", encoding="utf-8") as pf:
                    json.dump(new_plan, pf, indent=2)

                # Sync regenerated plan to dd_hub vault and src/
                ep_match = re.search(r'\d+', project_id)
                ep_str = ep_match.group(0) if ep_match else None
                if ep_str:
                    hub_root = resolve_dd_hub_root()
                    if os.path.exists(hub_root):
                        hub_ep_plan = os.path.join(hub_root, "episodes", ep_str, "plan.json")
                        try:
                            os.makedirs(os.path.dirname(hub_ep_plan), exist_ok=True)
                            shutil.copy2(plan_path, hub_ep_plan)
                        except Exception:
                            pass
                    for docs_root in ["docs", os.path.join("..", "src", "ddma", "docs")]:
                        docs_ep_plan = os.path.join(docs_root, "episodes", ep_str, "plan.json")
                        try:
                            os.makedirs(os.path.dirname(docs_ep_plan), exist_ok=True)
                            shutil.copy2(plan_path, docs_ep_plan)
                        except Exception:
                            pass

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "plan": new_plan, "clip_count": len(new_plan)}).encode('utf-8'))
                return
            except Exception as ep_err:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(ep_err)}).encode('utf-8'))
                return
                
        elif parsed_url.path == '/save-project-snapshot':
            project_id = params.get('id', [None])[0]
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                
                project_dir = os.path.join("projects", project_id)
                plan_path = os.path.join(project_dir, "plan.json")
                snapshot_path = os.path.join(project_dir, "plan_snapshot.json")
                
                if os.path.exists(plan_path):
                    shutil.copy2(plan_path, snapshot_path)
                else:
                    with open(snapshot_path, "w", encoding="utf-8") as f:
                        json.dump([], f)
                        
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, f"Error saving snapshot: {e}")
                return
                
        elif parsed_url.path == '/restore-project-snapshot':
            project_id = params.get('id', [None])[0]
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                
                project_dir = os.path.join("projects", project_id)
                plan_path = os.path.join(project_dir, "plan.json")
                snapshot_path = os.path.join(project_dir, "plan_snapshot.json")
                
                if not os.path.exists(snapshot_path):
                    raise Exception("No snapshot exists for this project.")
                    
                shutil.copy2(snapshot_path, plan_path)
                shutil.copy2(snapshot_path, "plan.json")
                if os.path.exists("docs"):
                    try:
                        shutil.copy2("plan.json", os.path.join("docs", "plan.json"))
                    except Exception as sync_err:
                        print(f"Error syncing snapshot to docs/plan.json: {sync_err}")
                
                # Load the restored plan
                with open(plan_path, "r", encoding="utf-8") as f:
                    restored_plan = json.load(f)
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "plan": restored_plan}).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, f"Error restoring snapshot: {e}")
                return
                
        elif parsed_url.path == '/save-settings':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                json_data = json.loads(post_data.decode('utf-8'))
                settings_path = "settings.json"
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=4)
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, f"Error saving settings: {e}")
                return
                
        elif parsed_url.path == '/upload-project-audio':
            try:
                project_name = params.get('name', [None])[0]
                original_filename = params.get('filename', ['audio.mp3'])[0]
                
                if not project_name:
                    raise Exception("Missing project name.")
                
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length <= 0:
                    raise Exception("Empty file payload.")
                    
                file_bytes = self.rfile.read(content_length)
                
                # Resolve episode number and uniform project_id (episode_N)
                ep_match = re.search(r'\d+', project_name)
                if ep_match:
                    ep_num = int(ep_match.group(0))
                else:
                    existing_nums = [244]
                    if os.path.exists("projects"):
                        for p in os.listdir("projects"):
                            m = re.search(r'\d+', p)
                            if m: existing_nums.append(int(m.group(0)))
                    ep_num = max(existing_nums) + 1
                
                project_id = f"episode_{ep_num}"
                project_dir = os.path.join("projects", project_id)
                if os.path.exists(project_dir):
                    # Clean up old directory if status was not ready
                    shutil.rmtree(project_dir, ignore_errors=True)
                
                os.makedirs(project_dir, exist_ok=True)
                
                # Save binary audio file
                ext = os.path.splitext(original_filename)[1] or ".m4a"
                dest_audio_name = f"{ep_num}{ext}"
                dest_audio_path = os.path.join(project_dir, dest_audio_name)
                
                with open(dest_audio_path, "wb") as f:
                    f.write(file_bytes)
                    
                info_path = os.path.join(project_dir, "project_info.json")
                info = {
                    "id": project_id,
                    "name": project_name if "Episode" in project_name else f"Episode {ep_num}",
                    "title": project_name,
                    "audio_filename": dest_audio_name,
                    "audio_file": dest_audio_name,
                    "status": "ingesting"
                }
                with open(info_path, "w", encoding="utf-8") as f:
                    json.dump(info, f, indent=4)
                    
                out_json_path = os.path.join(project_dir, "transcription.json")
                t = threading.Thread(target=run_transcribe, args=(project_id, dest_audio_path, out_json_path, info_path), daemon=True)
                t.start()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "project_id": project_id}).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, f"Upload project audio error: {e}")
                return

        elif parsed_url.path == '/create-project':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                json_data = json.loads(post_data.decode('utf-8'))
                project_name = json_data.get("name", "").strip()
                audio_source = json_data.get("audio_source", "").strip()
                
                if not project_name or not audio_source:
                    raise Exception("Project name and audio source are required.")
                
                # Resolve episode number and uniform project_id (episode_N)
                ep_match = re.search(r'\d+', project_name)
                if ep_match:
                    ep_num = int(ep_match.group(0))
                else:
                    existing_nums = [244]
                    if os.path.exists("projects"):
                        for p in os.listdir("projects"):
                            m = re.search(r'\d+', p)
                            if m: existing_nums.append(int(m.group(0)))
                    ep_num = max(existing_nums) + 1
                
                project_id = f"episode_{ep_num}"
                project_dir = os.path.join("projects", project_id)
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir, ignore_errors=True)
                
                os.makedirs(project_dir, exist_ok=True)
                
                # Check if audio file exists in root
                if not os.path.exists(audio_source):
                    raise Exception(f"Source audio file {audio_source} not found.")
                
                # Copy audio to project directory
                ext = os.path.splitext(audio_source)[1]
                dest_audio_name = f"audio{ext}"
                dest_audio_path = os.path.join(project_dir, dest_audio_name)
                
                shutil.copy2(audio_source, dest_audio_path)
                
                # Create project info
                info_path = os.path.join(project_dir, "project_info.json")
                info = {
                    "id": project_id,
                    "name": project_name,
                    "audio_filename": dest_audio_name,
                    "status": "transcribing"
                }
                with open(info_path, "w", encoding="utf-8") as f:
                    json.dump(info, f, indent=4)
                
                # Create empty plan.json
                with open(os.path.join(project_dir, "plan.json"), "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
                
                # Register new episode in docs/episodes.json manifest (and ../src/ddma/docs/episodes.json mirror)
                try:
                    for docs_root in ["docs", os.path.join("..", "src", "ddma", "docs")]:
                        ep_manifest_path = os.path.join(docs_root, "episodes.json")
                        if os.path.exists(ep_manifest_path):
                            with open(ep_manifest_path, "r", encoding="utf-8") as mf:
                                mdata = json.load(mf)
                            
                            title_val = json_data.get("title", project_name)
                            new_entry = {
                                "id": str(ep_num),
                                "number": int(ep_num) if str(ep_num).isdigit() else ep_num,
                                "title": title_val,
                                "fullTitle": f"Episode {ep_num}: {title_val}",
                                "planPath": f"episodes/{ep_num}/plan.json",
                                "clipsDir": f"episodes/{ep_num}/clips",
                                "links": {},
                                "isDefault": False
                            }
                            
                            mdata = [item for item in mdata if str(item.get("id")) != str(ep_num) and str(item.get("number")) != str(ep_num)]
                            mdata.append(new_entry)
                            mdata.sort(key=lambda m: int(m.get("number") or (int(m["id"]) if str(m.get("id", "")).isdigit() else 0)))
                            for m in mdata:
                                m["isDefault"] = False
                            if mdata:
                                mdata[-1]["isDefault"] = True
                            
                            with open(ep_manifest_path, "w", encoding="utf-8") as mf:
                                json.dump(mdata, mf, indent=2)
                except Exception as me:
                    print(f"Warning updating episodes.json manifest during create: {me}")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "project_id": project_id}).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, str(e))
                return

        elif parsed_url.path == '/delete-project':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b""
            json_data = {}
            if post_data:
                try:
                    json_data = json.loads(post_data.decode('utf-8'))
                except Exception:
                    pass
            
            project_id = params.get('id', [None])[0] or json_data.get('id') or json_data.get('project_id')
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                
                # 1. Resolve numeric episode ID (e.g. "episode_245" -> "245")
                ep_num_match = re.search(r'\d+', str(project_id))
                ep_num = ep_num_match.group(0) if ep_num_match else None
                
                print(f"[{project_id}] Starting isolated project deletion policy (ep_num={ep_num})...")

                # 2. Delete projects/<id> directory tree
                project_dir = os.path.join("projects", project_id)
                if os.path.exists(project_dir):
                    info_path = os.path.join(project_dir, "project_info.json")
                    if os.path.exists(info_path):
                        try:
                            os.remove(info_path)
                        except Exception:
                            pass
                    try:
                        shutil.rmtree(project_dir)
                    except Exception as rmtree_err:
                        print(f"shutil.rmtree failed on {project_dir}: {rmtree_err}. Cleaning files individually...")
                        for root, dirs, files in os.walk(project_dir, topdown=False):
                            for name in files:
                                try:
                                    os.remove(os.path.join(root, name))
                                except Exception:
                                    pass
                        try:
                            trash_dir = os.path.join("projects", f".trash_{project_id}_{int(time.time())}")
                            os.rename(project_dir, trash_dir)
                        except Exception:
                            pass

                if ep_num:
                    # 3. Clean clips matching pattern "ep_num-*" from clips/
                    clips_dir = "clips"
                    if os.path.exists(clips_dir):
                        for fname in os.listdir(clips_dir):
                            if fname.startswith(f"{ep_num}-"):
                                try:
                                    os.remove(os.path.join(clips_dir, fname))
                                except Exception as e:
                                    print(f"Warning deleting clip {fname}: {e}")

                    # 5. Clean previews matching preview_project_id_* or preview_episode_ep_num_*
                    previews_dir = "previews"
                    if os.path.exists(previews_dir):
                        for pfname in os.listdir(previews_dir):
                            if pfname.startswith(f"preview_{project_id}_") or pfname.startswith(f"preview_episode_{ep_num}_"):
                                try:
                                    os.remove(os.path.join(previews_dir, pfname))
                                except Exception:
                                    pass

                    # 6. Clean web docs assets: docs/episodes/ep_num/
                    docs_ep_dir = os.path.join("docs", "episodes", ep_num)
                    if os.path.exists(docs_ep_dir):
                        try:
                            shutil.rmtree(docs_ep_dir)
                        except Exception as e:
                            print(f"Warning deleting docs episode folder {docs_ep_dir}: {e}")

                    # 7. Update docs/episodes.json manifest (and ../src/ddma/docs/episodes.json mirror)
                    for docs_root in ["docs", os.path.join("..", "src", "ddma", "docs")]:
                        ep_manifest_path = os.path.join(docs_root, "episodes.json")
                        if os.path.exists(ep_manifest_path):
                            try:
                                with open(ep_manifest_path, "r", encoding="utf-8") as mf:
                                    manifest = json.load(mf)
                                
                                # Filter out deleted episode
                                updated_manifest = [m for m in manifest if str(m.get("id")) != ep_num and str(m.get("number")) != ep_num]
                                
                                # Ensure at least one default episode remains (the latest) if manifest is not empty
                                if updated_manifest:
                                    updated_manifest.sort(key=lambda m: int(m.get("number") or (int(m["id"]) if str(m.get("id", "")).isdigit() else 0)))
                                    has_default = any(m.get("isDefault") for m in updated_manifest)
                                    if not has_default:
                                        updated_manifest[-1]["isDefault"] = True
                                
                                with open(ep_manifest_path, "w", encoding="utf-8") as mf:
                                    json.dump(updated_manifest, mf, indent=2)
                            except Exception as me:
                                print(f"Warning updating {ep_manifest_path} manifest during delete: {me}")

                print(f"[{project_id}] Isolated project deletion complete.")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, f"Error deleting project: {e}")
                return

        elif parsed_url.path == '/update-episode-title':
            project_id = params.get('id', [None])[0]
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                json_data = json.loads(post_data.decode('utf-8'))
                new_title = json_data.get("title", "").strip()
                if not new_title:
                    raise Exception("New episode title is required.")
                
                project_dir = os.path.join("projects", project_id)
                info_path = os.path.join(project_dir, "project_info.json")
                if os.path.exists(info_path):
                    with open(info_path, "r", encoding="utf-8") as f:
                        info = json.load(f)
                    info["title"] = new_title
                    with open(info_path, "w", encoding="utf-8") as f:
                        json.dump(info, f, indent=4)
                
                # Auto-recompile Clip 1 intro card in background
                def run_recompile_clip1(proj_id, p_dir):
                    try:
                        p_file = os.path.join(p_dir, "plan.json")
                        cmd = [sys.executable, "ddma.py", "compile-clip", "--num", "1", "--plan-file", p_file]
                        print(f"[Update-Title][{proj_id}] Recompiling Clip 1 with new episode title: '{new_title}'")
                        subprocess.run(cmd, capture_output=True, text=True, cwd=".")
                    except Exception as ex:
                        print(f"Error recompiling clip 1: {ex}")
                
                threading.Thread(target=run_recompile_clip1, args=(project_id, project_dir), daemon=True).start()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "title": new_title}).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, f"Error updating episode title: {e}")
                return

        elif parsed_url.path == '/rename-project':
            project_id = params.get('id', [None])[0]
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                
                json_data = json.loads(post_data.decode('utf-8'))
                new_name = json_data.get("name", "").strip()
                if not new_name:
                    raise Exception("New name is required.")
                
                # Derive new project ID
                new_id = re.sub(r'[^a-zA-Z0-9_-]', '_', new_name.lower().replace(" ", "_"))
                
                src_dir = os.path.join("projects", project_id)
                dst_dir = os.path.join("projects", new_id)
                
                if new_id != project_id:
                    if os.path.exists(dst_dir):
                        raise Exception(f"A project directory named '{new_id}' already exists. Please delete it first.")
                    
                    # Rename project directory
                    os.rename(src_dir, dst_dir)
                    project_dir = dst_dir
                else:
                    project_dir = src_dir
                
                # Update metadata id and name
                info_path = os.path.join(project_dir, "project_info.json")
                if os.path.exists(info_path):
                    with open(info_path, "r", encoding="utf-8") as f:
                        info = json.load(f)
                    info["id"] = new_id
                    info["name"] = new_name
                    with open(info_path, "w", encoding="utf-8") as f:
                        json.dump(info, f, indent=4)
                
                # Rename matching clip files inside clips/ folder
                if new_id != project_id:
                    old_ep_match = re.search(r'\d+', project_id)
                    new_ep_match = re.search(r'\d+', new_id)
                    if old_ep_match and new_ep_match:
                        old_ep = old_ep_match.group(0)
                        new_ep = new_ep_match.group(0)
                        if old_ep != new_ep:
                            clips_dir = "clips"
                            if os.path.exists(clips_dir):
                                for file in os.listdir(clips_dir):
                                    if file.startswith(f"{old_ep}-"):
                                        old_file_path = os.path.join(clips_dir, file)
                                        # Construct new filename replacing the episode number prefix
                                        new_filename = f"{new_ep}-{file[len(old_ep)+1:]}"
                                        new_file_path = os.path.join(clips_dir, new_filename)
                                        
                                        try:
                                            # Overwrite target if it exists, as requested
                                            if os.path.exists(new_file_path):
                                                os.remove(new_file_path)
                                            os.rename(old_file_path, new_file_path)
                                        except Exception as file_err:
                                            print(f"Error renaming clip file {file} to {new_filename}: {file_err}")
                
                response_data = {
                    "success": True,
                    "new_id": new_id
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
                return

        elif parsed_url.path == '/duplicate-project':
            project_id = params.get('id', [None])[0]
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                
                json_data = json.loads(post_data.decode('utf-8'))
                new_name = json_data.get("name", "").strip()
                if not new_name:
                    raise Exception("New project name is required.")
                
                new_id = re.sub(r'[^a-zA-Z0-9_-]', '_', new_name.lower().replace(" ", "_"))
                src_dir = os.path.join("projects", project_id)
                dst_dir = os.path.join("projects", new_id)
                
                if os.path.exists(dst_dir):
                    raise Exception("Project with this name/id already exists.")
                
                shutil.copytree(src_dir, dst_dir)
                
                # Update project_info.json in the copy
                info_path = os.path.join(dst_dir, "project_info.json")
                if os.path.exists(info_path):
                    with open(info_path, "r", encoding="utf-8") as f:
                        info = json.load(f)
                    info["id"] = new_id
                    info["name"] = new_name
                    with open(info_path, "w", encoding="utf-8") as f:
                        json.dump(info, f, indent=4)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "project_id": new_id}).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, f"Error duplicating project: {e}")
                return

        elif parsed_url.path == '/compile-project-preview':
            project_id = params.get('id', [None])[0]
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                
                project_dir = os.path.join("projects", project_id)
                info_path = os.path.join(project_dir, "project_info.json")
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                
                audio_path = get_project_canonical_audio_path(project_dir, project_id, info)
                if not audio_path or not os.path.exists(audio_path):
                    raise Exception(f"Audio file for project {project_id} not found.")
                
                json_data = json.loads(post_data.decode('utf-8'))
                segments = json_data.get("segments", [])
                clip_idx = json_data.get("clip_idx", 0)
                
                os.makedirs("previews", exist_ok=True)
                output_path = f"previews/preview_{project_id}_{clip_idx}.mp3"
                
                # Perform compilation
                self.compile_segments(segments, output_path, audio_path)
                
                response_data = {
                    "preview_url": f"previews/preview_{project_id}_{clip_idx}.mp3?t={int(time.time() * 1000)}"
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                return
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_error(500, f"Compilation error: {e}")
                return

        elif parsed_url.path == '/get-clip-intro':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                clip_num = int(clip_num)
                
                project_dir = os.path.join("projects", project_id)
                plan_path = os.path.join(project_dir, "plan.json")
                if not os.path.exists(plan_path):
                    raise Exception("plan.json not found.")
                
                with open(plan_path, "r", encoding="utf-8") as f:
                    plan_data = json.load(f)
                
                clip = None
                for c in plan_data:
                    if c["num"] == clip_num:
                        clip = c
                        break
                if not clip:
                    raise Exception(f"Clip {clip_num} not found in plan.")
                
                title = clip.get("title", "")
                
                import re
                ep_num_match = re.search(r'\d+', project_id)
                ep_num = ep_num_match.group(0) if ep_num_match else project_id
                
                from PIL import Image, ImageDraw, ImageFont
                # Pure Glossy Black (#000000) canvas per Monochrome Noir standard — zero blurred background frame bleed
                width, height = 740, 740
                img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
                draw = ImageDraw.Draw(img)
                
                def find_system_fonts():
                    candidates = [
                        (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf"),
                        (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf"),
                    ]
                    for bold, reg in candidates:
                        if os.path.exists(bold) and os.path.exists(reg):
                            return bold, reg
                    return None, None
                
                font_bold, font_reg = find_system_fonts()
                if font_bold and font_reg:
                    font_title = ImageFont.truetype(font_bold, 44)
                    font_sub = ImageFont.truetype(font_reg, 24)
                else:
                    font_title = ImageFont.load_default()
                    font_sub = ImageFont.load_default()
                
                box_width = int(width * 0.85)
                box_height = 280
                x0 = (width - box_width) // 2
                y0 = height // 2 - 160
                x1 = x0 + box_width
                y1 = y0 + box_height
                
                # Clip 0 (Show Prologue / Ep Intro) has NO Part number; Clip 1+ shows EPISODE <num> • PART <num>
                sub_text = f"EPISODE {ep_num}" if clip_num == 0 else f"EPISODE {ep_num} • PART {clip_num}"
                title_text = title if title else (f"Episode {ep_num}" if clip_num == 0 else f"Part {clip_num}")
                
                bbox_sub = draw.textbbox((0, 0), sub_text, font=font_sub)
                w_sub = bbox_sub[2] - bbox_sub[0]
                draw.text(((width - w_sub) // 2, y0 + 35), sub_text, font=font_sub, fill=(180, 180, 180, 255))
                
                def split_title(text):
                    if "\n" in text:
                        return [line.strip() for line in text.split("\n")]
                    if " : " in text:
                        return [p.strip() for p in text.split(" : ", 1)]
                    words = text.split()
                    if len(words) <= 3:
                        return [text]
                    best_diff = float('inf')
                    best_idx = 1
                    for i in range(1, len(words)):
                        part1 = " ".join(words[:i])
                        part2 = " ".join(words[i:])
                        diff = abs(len(part1) - len(part2))
                        if diff < best_diff:
                            best_diff = diff
                            best_idx = i
                    return [" ".join(words[:best_idx]), " ".join(words[best_idx:])]
                
                title_lines = split_title(title_text)
                
                line_spacing = 12
                line_heights = []
                total_title_h = 0
                for line in title_lines:
                    bbox_l = draw.textbbox((0, 0), line, font=font_title)
                    h_l = bbox_l[3] - bbox_l[1]
                    line_heights.append(h_l)
                    total_title_h += h_l
                total_title_h += line_spacing * (len(title_lines) - 1)
                
                box_content_h = y1 - y0 - 120
                start_y = y0 + 80 + (box_content_h - total_title_h) // 2
                if start_y < y0 + 80:
                    start_y = y0 + 80
                
                curr_y = start_y
                for idx, line in enumerate(title_lines):
                    bbox_line = draw.textbbox((0, 0), line, font=font_title)
                    w_line = bbox_line[2] - bbox_line[0]
                    draw.text(((width - w_line) // 2, curr_y), line, font=font_title, fill=(255, 255, 255, 255))
                    curr_y += line_heights[idx] + line_spacing
                
                line_y = y1 - 35
                line_w = 120
                draw.line([((width - line_w) // 2, line_y), ((width - line_w) // 2 + line_w, line_y)], fill=(80, 80, 80, 255), width=2)
                
                final_img = img.convert("RGB")
                temp_png = f"temp_intro_preview_{project_id}_{clip_num}.png"
                final_img.save(temp_png)
                
                os.makedirs("previews", exist_ok=True)
                out_path = f"previews/intro_{project_id}_{clip_num}.mp4"
                
                music_file = None
                fallback_music = [
                    "title-card-music.mp3",
                    os.path.join("music", "deepDive-soft-ok.mp3"),
                    os.path.join("music", "deepDive-main.mp3"),
                    os.path.join("music", "deepDive-strong.mp3")
                ]
                for cand in fallback_music:
                    if os.path.exists(cand):
                        music_file = cand
                        break
                cmd_ffmpeg = [
                    "ffmpeg", "-y",
                    "-loop", "1",
                    "-r", "30",
                    "-i", temp_png,
                    "-i", music_file,
                    "-filter_complex", "[1:a]afade=t=out:st=1.3:d=0.2[a]",
                    "-map", "0:v",
                    "-map", "[a]",
                    "-c:v", "libx264",
                    "-tune", "stillimage",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-ar", "48000",
                    "-ac", "2",
                    "-pix_fmt", "yuv420p",
                    "-t", "1.5",
                    out_path
                ]
                res_ffmpeg = subprocess.run(cmd_ffmpeg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if os.path.exists(temp_png):
                    try:
                        os.remove(temp_png)
                    except OSError as e:
                        print(f"WARNING: could not remove temp file {temp_png}: {e}")
                        
                if res_ffmpeg.returncode != 0:
                    raise Exception(f"FFmpeg render failed: {res_ffmpeg.stderr.decode('utf-8')}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "preview_url": f"/previews/intro_{project_id}_{clip_num}.mp4?t={int(time.time() * 1000)}"
                }).encode('utf-8'))
                return
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/get-clip-outro':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                clip_num = int(clip_num)
                
                project_dir = os.path.join("projects", project_id)
                plan_path = os.path.join(project_dir, "plan.json")
                if not os.path.exists(plan_path):
                    plan_path = "plan.json"
                if not os.path.exists(plan_path):
                    raise Exception("plan.json not found.")
                
                with open(plan_path, "r", encoding="utf-8") as f:
                    plan_data = json.load(f)
                
                clip = None
                for c in plan_data:
                    if c["num"] == clip_num:
                        clip = c
                        break
                if not clip:
                    raise Exception(f"Clip {clip_num} not found in plan.")
                
                sorted_clips = sorted(plan_data, key=lambda x: x["num"])
                is_last_clip = (sorted_clips[-1]["num"] == clip_num)
                
                if is_last_clip:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False, 
                        "error": "This is the last clip of the episode, so it does not have an outro transition card."
                    }).encode('utf-8'))
                    return
                
                bridge_text_input = clip.get("bridge_text", "")
                if isinstance(bridge_text_input, list):
                    bridge_text = " ".join(bridge_text_input)
                else:
                    bridge_text = str(bridge_text_input).strip()
                
                if not bridge_text:
                    bridge_text = "Next question is coming up..."
                
                os.makedirs("previews", exist_ok=True)
                temp_compiled_audio = f"previews/temp_compiled_audio_{project_id}_{clip_num}.mp3"
                
                info_path = os.path.join(project_dir, "project_info.json")
                with open(info_path, "r", encoding="utf-8") as inf_f:
                    info_data = json.load(inf_f)
                full_audio_path = os.path.join(project_dir, info_data["audio_filename"])
                
                segments = clip.get("segments")
                if not segments or not isinstance(segments, list):
                    segments = []
                    if clip.get("music"):
                        segments.append({
                            "type": "music",
                            "music_file": clip.get("music"),
                            "duration": 5.0,
                            "volume": clip.get("music_volume", 1.0),
                            "crossfade": 1.0
                        })
                    segments.append({
                        "type": "audio",
                        "start": clip.get("start", 0.0),
                        "end": clip.get("end", 0.0),
                        "duration": clip.get("end", 0.0) - clip.get("start", 0.0),
                        "volume": 1.0,
                        "crossfade": 0.0,
                        "text": clip.get("title", "")
                    })
                
                self.compile_segments(segments, temp_compiled_audio, full_audio_path)
                audio_source = temp_compiled_audio
                
                duration = 5.0
                try:
                    dur_cmd = [
                        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_source
                    ]
                    dur_res = subprocess.run(dur_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if dur_res.returncode == 0:
                        duration = float(dur_res.stdout.strip())
                except Exception as e:
                    print(f"WARNING: ffprobe duration probe failed ({e}) -- using default duration {duration}.")
                
                start_time = max(0.0, duration - 5.0)
                
                from PIL import Image, ImageDraw, ImageFont
                v_width, v_height = 740, 740
                
                img_outro = Image.new("RGB", (v_width, v_height), color=(0, 0, 0))
                draw_outro = ImageDraw.Draw(img_outro)
                
                font_path = "C:\\Windows\\Fonts\\segoeuib.ttf"
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 34)
                else:
                    font = ImageFont.load_default()
                
                def wrap_text_outro(text, font_obj, max_w):
                    lines = []
                    for paragraph in text.split("\n"):
                        words = paragraph.split()
                        if not words:
                            lines.append("")
                            continue
                        curr = []
                        for word in words:
                            test_line = " ".join(curr + [word])
                            bbox = draw_outro.textbbox((0, 0), test_line, font=font_obj)
                            w = bbox[2] - bbox[0]
                            if w <= max_w:
                                curr.append(word)
                            else:
                                if curr:
                                    lines.append(" ".join(curr))
                                curr = [word]
                        if curr:
                            lines.append(" ".join(curr))
                    return lines
                
                lines = wrap_text_outro(bridge_text, font, v_width - 160)
                
                line_spacing = 18
                line_heights = []
                total_h = 0
                for line in lines:
                    bbox = draw_outro.textbbox((0, 0), line, font=font)
                    h = bbox[3] - bbox[1]
                    line_heights.append(h)
                    total_h += h
                total_h += line_spacing * (len(lines) - 1)
                
                curr_y = (v_height - total_h) // 2
                for idx, line in enumerate(lines):
                    bbox = draw_outro.textbbox((0, 0), line, font=font)
                    w = bbox[2] - bbox[0]
                    draw_outro.text(((v_width - w) // 2, curr_y), line, font=font, fill=(255, 255, 255))
                    curr_y += line_heights[idx] + line_spacing
                
                temp_png_outro = f"temp_outro_preview_{project_id}_{clip_num}.png"
                img_outro.save(temp_png_outro)
                
                os.makedirs("previews", exist_ok=True)
                out_path = f"previews/outro_{project_id}_{clip_num}.mp4"
                
                cmd_ffmpeg_outro = [
                    "ffmpeg", "-y",
                    "-loop", "1",
                    "-r", "30",
                    "-i", temp_png_outro,
                    "-ss", f"{start_time:.6f}",
                    "-i", audio_source,
                    "-map", "0:v",
                    "-map", "1:a",
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-af", "afade=t=out:st=0:d=5.0",
                    "-c:a", "aac",
                    "-ar", "48000",
                    "-ac", "2",
                    "-t", "5.0",
                    out_path
                ]
                res_ffmpeg = subprocess.run(cmd_ffmpeg_outro, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if os.path.exists(temp_png_outro):
                    try:
                        os.remove(temp_png_outro)
                    except OSError as e:
                        print(f"WARNING: could not remove temp file {temp_png_outro}: {e}")
                
                temp_audio_gen = f"previews/temp_compiled_audio_{project_id}_{clip_num}.mp3"
                if os.path.exists(temp_audio_gen):
                    try:
                        os.remove(temp_audio_gen)
                    except OSError as e:
                        print(f"WARNING: could not remove temp file {temp_audio_gen}: {e}")
                
                if res_ffmpeg.returncode != 0:
                    raise Exception(f"FFmpeg render failed: {res_ffmpeg.stderr.decode('utf-8')}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "preview_url": f"/previews/outro_{project_id}_{clip_num}.mp4?t={int(time.time() * 1000)}"
                }).encode('utf-8'))
                return
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/review-episode-bridges':
            project_id = params.get('id', [None])[0]
            content_length = int(self.headers.get('Content-Length', 0))
            custom_prompt = None
            if content_length > 0:
                try:
                    post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                    custom_prompt = post_data.get('custom_prompt')
                except Exception:
                    pass

            try:
                if not project_id:
                    raise Exception("Missing project id.")
                
                project_dir = os.path.join("projects", project_id)
                plan_path = os.path.join(project_dir, "plan.json")
                if not os.path.exists(plan_path):
                    raise Exception("plan.json not found.")
                
                sys.path.insert(0, ".")
                from scratch.review_episode_bridges import review_episode_bridges
                success = review_episode_bridges(plan_path, custom_prompt=custom_prompt)
                if not success:
                    raise Exception("Gemini episode bridge review failed.")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": "Episode bridge cards successfully reviewed and updated by AI!"}).encode('utf-8'))
                return
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/export-project-clip':
            project_id = params.get('id', [None])[0]
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                
                project_dir = os.path.join("projects", project_id)
                info_path = os.path.join(project_dir, "project_info.json")
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                
                audio_path = os.path.join(project_dir, info["audio_filename"])
                
                json_data = json.loads(post_data.decode('utf-8'))
                segments = json_data.get("segments", [])
                clip_num = json_data.get("clip_num", 0)
                title = json_data.get("title", f"Clip-{clip_num}")
                export_format = json_data.get("export_format", "audio")
                resolution = json_data.get("resolution", "1080x1080")
                bg_color = json_data.get("bg_color", "black")
                
                # Verify clip is locked before exporting
                plan_path = os.path.join(project_dir, "plan.json")
                target_clip = None
                if os.path.exists(plan_path):
                    with open(plan_path, "r", encoding="utf-8") as f:
                        plan = json.load(f)
                    for clip in plan:
                        if int(clip.get("num", -1)) == int(clip_num):
                            target_clip = clip
                            break

                is_clip_locked = target_clip.get("locked") if target_clip else json_data.get("locked", False)
                if not is_clip_locked:
                    self.send_response(403)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": f"Clip {clip_num} is unlocked. Lock clip before exporting."}).encode("utf-8"))
                    return
                
                os.makedirs("clips", exist_ok=True)
                
                # Clean title for filename
                clean_title = "".join(c if c.isalnum() or c in "._-" else "_" for c in title)
                
                # Extract prefix from project ID or default
                prefix = project_id.split("_")[-1] if "_" in project_id else project_id
                if not prefix.isdigit():
                    prefix = project_id
                    
                ext = ".mp4" if export_format == "video" else ".mp3"
                output_filename = f"{prefix}-{clip_num}-{clean_title}{ext}"
                output_path = os.path.join("clips", output_filename)
                
                if export_format == "video":
                    temp_audio = f"temp_export_audio_{project_id}_{clip_num}.mp3"
                    try:
                        # 1. Compile audio segments first to temp_audio
                        self.compile_segments(segments, temp_audio, audio_path)
                        
                        # 2. Mux temp_audio with solid color canvas
                        ffmpeg_color = bg_color.replace('#', '0x')
                        cmd = [
                            "ffmpeg", "-y",
                            "-f", "lavfi",
                            "-i", f"color=c={ffmpeg_color}:s={resolution}:r=25",
                            "-i", temp_audio,
                            "-c:v", "libx264",
                            "-tune", "stillimage",
                            "-c:a", "aac",
                            "-b:a", "192k",
                            "-pix_fmt", "yuv420p",
                            "-shortest",
                            output_path
                        ]
                        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if res.returncode != 0:
                            raise Exception(f"FFmpeg video muxing failed: {res.stderr.decode('utf-8')}")
                    finally:
                        if os.path.exists(temp_audio):
                            try:
                                os.remove(temp_audio)
                            except OSError as e:
                                print(f"WARNING: could not remove temp file {temp_audio}: {e}")
                else:
                    # Compile segments directly to the production clips folder as mp3
                    self.compile_segments(segments, output_path, audio_path)
                
                response_data = {
                    "success": True,
                    "filename": f"clips/{output_filename}"
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                return
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_error(500, f"Export clip error: {e}")
                return
                
        elif parsed_url.path == '/upload-music':
            # Raw binary upload handler for globally shared music stings
            filename = self.headers.get('X-Filename')
            if not filename:
                self.send_error(400, "Missing X-Filename header.")
                return
            
            # Sanitize filename
            filename = re.sub(r'[^a-zA-Z0-9_\-\.\s\(\)]', '_', filename)
            music_dir = "music"
            os.makedirs(music_dir, exist_ok=True)
            dest_path = os.path.join(music_dir, filename)
            
            content_length = int(self.headers.get('Content-Length', 0))
            try:
                print(f"Uploading new global sting: {filename} ({content_length} bytes)")
                with open(dest_path, 'wb') as f:
                    remaining = content_length
                    chunk_size = 64 * 1024
                    while remaining > 0:
                        chunk = self.rfile.read(min(chunk_size, remaining))
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "filename": filename}).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, str(e))
                return
                
        elif parsed_url.path == '/delete-music':
            filename = params.get('file', [None])[0]
            if not filename:
                self.send_error(400, "Missing file parameter.")
                return
            
            filename = os.path.basename(filename) # Sanitize
            file_path = os.path.join("music", filename)
            
            try:
                if os.path.exists(file_path):
                    print(f"Deleting global sting: {filename}")
                    os.remove(file_path)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                    return
                else:
                    self.send_error(404, "File not found.")
                    return
            except Exception as e:
                self.send_error(500, str(e))
                return

        
        elif parsed_url.path == '/polish-clip-text':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = {}
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                try:
                    post_data = json.loads(body)
                except Exception:
                    pass
            
            raw_text = post_data.get('text', '').strip()
            title = post_data.get('title', '')
            
            if not raw_text:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "No text provided"}).encode('utf-8'))
                return
            
            polished_text = None
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                settings_path = "settings.json"
                if os.path.exists(settings_path):
                    with open(settings_path, "r", encoding="utf-8") as f:
                        settings = json.load(f)
                        api_key = settings.get("gemini_api_key")
            if configure_gemini(api_key):
                try:
                    prompt = (
                        "You are an expert editorial copywriter for a high-end science and philosophy podcast.\n"
                        "Review the following spoken transcript for a short video clip. Fix all phonetic spelling mistakes, "
                        "transcription errors (e.g. Sanskrit breathwork terms like Pranayama, Kumbhaka, Rechaka, Anulom-Vilom, or medical pulmonology terms like atelectrauma, exhale, etc.), "
                        "capitalize first letters of sentences and the first word, fix punctuation, and format the text into clean, readable paragraphs for social media captions (Instagram, LinkedIn, X/Twitter).\n"
                        "DO NOT add conversational filler or alter the speaker's original meaning. Return ONLY the polished, formatted text.\n\n"
                        f"Clip Title: {title}\n"
                        f"Spoken Transcript:\n{raw_text}"
                    )
                    model = None
                    for m_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]:
                        try:
                            model = genai.GenerativeModel(m_name)
                            break
                        except Exception:
                            continue
                    if model:
                        response = model.generate_content(prompt)
                        if response and response.text:
                            polished_text = response.text.strip()
                except Exception as ge:
                    print(f"[AI Polish] Gemini error: {ge}")
            
            if not polished_text:
                polished_text = smart_format_transcript_py(raw_text)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "polished_text": polished_text}).encode('utf-8'))
            return

        
        elif parsed_url.path == '/open-in-external-editor':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                
                project_dir = os.path.join("projects", project_id)
                plan_path = os.path.join(project_dir, "plan.json")
                if not os.path.exists(plan_path):
                    raise Exception(f"plan.json for project {project_id} not found.")
                
                with open(plan_path, "r", encoding="utf-8") as f:
                    plan = json.load(f)
                
                target_clip = None
                for clip in plan:
                    if int(clip.get("num", -1)) == int(clip_num):
                        target_clip = clip
                        break
                
                if not target_clip:
                    raise Exception(f"Clip {clip_num} not found in plan.")
                
                # Get current text
                if target_clip.get("text") and target_clip.get("text").strip():
                    text_content = target_clip.get("text").strip()
                else:
                    speech_texts = []
                    for seg in target_clip.get("segments", []):
                        if seg.get("type") == "audio" and seg.get("text"):
                            speech_texts.append(seg.get("text").strip())
                    text_content = " ".join(speech_texts)
                
                # Write to temporary file in project directory
                temp_filename = f"clip_{clip_num}_transcript.txt"
                temp_filepath = os.path.abspath(os.path.join(project_dir, temp_filename))
                
                with open(temp_filepath, "w", encoding="utf-8") as tf:
                    tf.write(text_content)
                
                # Determine editor command
                settings_path = "settings.json"
                settings = {}
                if os.path.exists(settings_path):
                    with open(settings_path, "r", encoding="utf-8") as sf:
                        settings = json.load(sf)
                
                editor_cmd = settings.get("external_editor") or os.environ.get("VISUAL") or os.environ.get("EDITOR") or "notepad"
                
                try:
                    cmd_args = shlex.split(editor_cmd, posix=(os.name != 'nt'))
                except Exception:
                    cmd_args = [editor_cmd]
                
                # Resolve gvim/vim path directly if needed
                if shutil.which(cmd_args[0]) is None:
                    local_gvim = os.path.expandvars(r'%LOCALAPPDATA%\Programs\Vim\gvim.exe')
                    local_vim = os.path.expandvars(r'%LOCALAPPDATA%\Programs\Vim\vim.exe')
                    if 'gvim' in cmd_args[0].lower() and os.path.exists(local_gvim):
                        cmd_args[0] = local_gvim
                    elif 'vim' in cmd_args[0].lower() and os.path.exists(local_vim):
                        cmd_args[0] = local_vim

                # Filter out -f or --nofork to allow proper GUI detachment
                cmd_args = [arg for arg in cmd_args if arg not in ('-f', '--nofork')]
                cmd_args.append(temp_filepath)
                print(f"[{project_id}][Clip {clip_num}] Launching external editor (non-blocking): {cmd_args}")
                
                # Execute external editor asynchronously so browser is never stuck
                try:
                    if os.name == 'nt':
                        # Use PowerShell Start-Process so it attaches to the interactive user desktop
                        editor_exe = cmd_args[0]
                        remaining_args = " ".join([f'\"{a}\"' for a in cmd_args[1:]])
                        ps_cmd = f"Start-Process -FilePath '{editor_exe}' -ArgumentList '{remaining_args}'"
                        subprocess.Popen(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_cmd])
                    else:
                        subprocess.Popen(cmd_args)
                except Exception as sub_e:
                    print(f"Specified editor {editor_cmd} failed ({sub_e}), falling back to notepad.exe")
                    if os.name == 'nt':
                        subprocess.Popen(["cmd.exe", "/c", "start", "", "notepad.exe", temp_filepath], shell=True)
                    else:
                        subprocess.Popen(["notepad", temp_filepath])
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True, 
                    "filepath": temp_filepath,
                    "filename": temp_filename,
                    "message": f"Opened {temp_filename} in external editor. Save with :w and click Sync Disk (or switch back to tab)."
                }).encode('utf-8'))
                return
                    
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/sync-clip-file':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                project_dir = os.path.join("projects", project_id)
                temp_filename = f"clip_{clip_num}_transcript.txt"
                temp_filepath = os.path.join(project_dir, temp_filename)
                plan_path = os.path.join(project_dir, "plan.json")
                
                if not os.path.exists(temp_filepath):
                    raise Exception(f"File {temp_filename} not found on disk. Open in external editor first.")
                
                with open(temp_filepath, "r", encoding="utf-8") as tf:
                    updated_text = tf.read().strip()
                
                with open(plan_path, "r", encoding="utf-8") as f:
                    plan = json.load(f)
                
                for clip in plan:
                    if int(clip.get("num", -1)) == int(clip_num):
                        clip["text"] = updated_text
                        break
                
                with open(plan_path, "w", encoding="utf-8") as f:
                    json.dump(plan, f, indent=2, ensure_ascii=False)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "text": updated_text}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/export-to-mosaic':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                
                content_length = int(self.headers.get('Content-Length', 0))
                custom_instructions = ""
                custom_prompt = ""
                if content_length > 0:
                    body = self.rfile.read(content_length).decode('utf-8')
                    try:
                        post_data = json.loads(body)
                        custom_instructions = post_data.get('directive', '').strip()
                        custom_prompt = post_data.get('prompt', '').strip()
                    except Exception:
                        pass
                
                # Check settings
                settings_path = "settings.json"
                settings = {}
                if os.path.exists(settings_path):
                    with open(settings_path, "r", encoding="utf-8") as f:
                        settings = json.load(f)
                
                api_key = settings.get("mosaic_api_key")
                agent_id = settings.get("mosaic_agent_id")
                if not api_key or not agent_id:
                    raise Exception("Mosaic API Key and Agent ID must be configured in System Settings first.")
                
                # Retrieve clip text and title from project plan.json
                project_dir = os.path.join("projects", project_id)
                
                info_path = os.path.join(project_dir, "project_info.json")
                if not os.path.exists(info_path):
                    raise Exception(f"project_info.json for project {project_id} not found.")
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                    
                # Hub-first plan read (fail loudly when unreachable -- never export from a stale cache).
                plan = load_plan(project_id, writer="curator")
                if not isinstance(plan, list) or len(plan) == 0:
                    raise Exception(f"plan for project {project_id} is empty or unreadable from dd_hub.")

                # Find matching clip
                target_clip = None
                for clip in plan:
                    if int(clip.get("num", -1)) == int(clip_num):
                        target_clip = clip
                        break
                
                if not target_clip:
                    raise Exception(f"Clip number {clip_num} not found in plan.")

                if not target_clip.get("locked"):
                    self.send_response(403)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": f"Clip {clip_num} is unlocked. Lock clip before exporting to Mosaic."}).encode("utf-8"))
                    return
                
                # Concatenate segment texts to get complete script
                raw_segment_texts = []
                for seg in target_clip.get("segments", []):
                    if seg.get("type") == "audio" and seg.get("text"):
                        raw_segment_texts.append(seg.get("text").strip())
                raw_transcript = " ".join(raw_segment_texts)

                if target_clip.get("text") and target_clip.get("text").strip():
                    saved_text = target_clip.get("text").strip()
                    raw_words = len(raw_transcript.split())
                    saved_words = len(saved_text.split())
                    if raw_words > 0 and abs(saved_words - raw_words) / max(raw_words, saved_words) > 0.15:
                        transcript = raw_transcript
                    else:
                        transcript = saved_text
                else:
                    transcript = raw_transcript
                
                # Generate custom prompt with user's baseline guidelines
                title = target_clip.get("title", f"Clip {clip_num}")
                if custom_prompt:
                    prompt_content = custom_prompt
                else:
                    prompt_content = build_mosaic_prompt_with_context(
                        title=title,
                        transcript=transcript,
                        custom_instructions=custom_instructions
                    )
                
                # Check if already running
                job_key = (project_id, int(clip_num))
                if job_key in mosaic_runs and mosaic_runs[job_key].get("status") in ("starting", "requesting upload URL", "uploading media", "finalizing upload", "triggering run", "running", "downloading output"):
                    raise Exception("An export is already in progress for this clip.")
                
                # Check for existing run ID in plan.json (cache/resume support)
                force_param = params.get('force', ['false'])[0].lower() == 'true'
                existing_run_id = target_clip.get("mosaic_run_id")
                
                if existing_run_id and not force_param:
                    base_url = "https://api.mosaic.so"
                    headers = {"Authorization": f"Bearer {api_key}"}
                    try:
                        res_status = requests.get(f"{base_url}/agent_run/{existing_run_id}", headers=headers)
                        if res_status.status_code == 200:
                            run_info = res_status.json()
                            status = run_info.get("status")
                            print(f"[{project_id}][Clip {clip_num}] Found existing run {existing_run_id} on Mosaic. API Status: {status}")
                            
                            if status == "completed":
                                # Resume completed run to download video
                                audio_path = get_project_canonical_audio_path(project_dir, project_id, info)
                                segments = target_clip.get("segments", [])
                                t = threading.Thread(
                                    target=run_mosaic_pipeline,
                                    args=(project_id, int(clip_num), settings, prompt_content, segments, audio_path, existing_run_id),
                                    daemon=True
                                )
                                t.start()
                                
                                self.send_response(200)
                                self.send_header('Content-type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()
                                self.wfile.write(json.dumps({
                                    "success": True,
                                    "job_id": f"{project_id}_{clip_num}",
                                    "status_url": f"/get-mosaic-status?id={project_id}&num={clip_num}",
                                    "message": "Resuming completed run to download video."
                                }).encode('utf-8'))
                                return
                            elif status in ("running", "starting"):
                                # Resume active run polling
                                audio_path = get_project_canonical_audio_path(project_dir, project_id, info)
                                segments = target_clip.get("segments", [])
                                t = threading.Thread(
                                    target=run_mosaic_pipeline,
                                    args=(project_id, int(clip_num), settings, prompt_content, segments, audio_path, existing_run_id),
                                    daemon=True
                                )
                                t.start()
                                
                                self.send_response(200)
                                self.send_header('Content-type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()
                                self.wfile.write(json.dumps({
                                    "success": True,
                                    "job_id": f"{project_id}_{clip_num}",
                                    "status_url": f"/get-mosaic-status?id={project_id}&num={clip_num}",
                                    "message": "Resuming active run polling."
                                }).encode('utf-8'))
                                return
                            else:
                                print(f"[{project_id}][Clip {clip_num}] Existing run {existing_run_id} has failed or cancelled. Clearing to start fresh.")
                        else:
                            print(f"[{project_id}][Clip {clip_num}] Existing run {existing_run_id} not found on Mosaic API. Clearing to start fresh.")
                    except Exception as poll_ex:
                        print(f"[{project_id}][Clip {clip_num}] Warning: Failed to query existing run status: {poll_ex}")
                
                # If force rerun, or if the existing run has failed/is missing, clear it in plan.json
                if existing_run_id:
                    try:
                        for c in plan:
                            if int(c.get("num", -1)) == int(clip_num):
                                if "mosaic_run_id" in c:
                                    del c["mosaic_run_id"]
                                break
                        with open(plan_path, "w", encoding="utf-8") as f:
                            json.dump(plan, f, indent=4)
                        print(f"[{project_id}][Clip {clip_num}] Cleared previous mosaic_run_id from plan.json")
                    except Exception as clear_ex:
                        print(f"Warning: Failed to clear mosaic_run_id: {clear_ex}")

                # Load segments and audio source path for automatic draft video generation if needed
                audio_path = get_project_canonical_audio_path(project_dir, project_id, info)
                segments = target_clip.get("segments", [])

                # Kick off new thread
                t = threading.Thread(
                    target=run_mosaic_pipeline,
                    args=(project_id, int(clip_num), settings, prompt_content, segments, audio_path),
                    daemon=True
                )
                t.start()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "job_id": f"{project_id}_{clip_num}",
                    "status_url": f"/get-mosaic-status?id={project_id}&num={clip_num}",
                    "message": "Mosaic run started."
                }).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                notify_failure("W3", "export-to-mosaic", f"{project_id} clip {clip_num}: {e}")
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/set-active-master':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            req_source = params.get('source', ['mosaic'])[0].lower()
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                
                source = "manim" if req_source in ("infographic", "manim") else "mosaic"
                ep_num = project_id.replace('episode_', '')
                plan_path = os.path.join("projects", project_id, "plan.json")
                if not os.path.exists(plan_path):
                    plan_path = "plan.json"

                with open(plan_path, "r", encoding="utf-8") as f:
                    plan_data = json.load(f)
                
                t_clip = next((c for c in plan_data if str(c.get("num")) == str(clip_num)), None)
                if not t_clip:
                    raise Exception(f"Clip {clip_num} not found in plan.")

                t_clip["visual_source"] = source
                with open(plan_path, "w", encoding="utf-8") as f:
                    json.dump(plan_data, f, indent=4)

                docs_plan = os.path.join("docs", "episodes", ep_num, "plan.json")
                if os.path.exists(docs_plan):
                    try:
                        with open(docs_plan, "w", encoding="utf-8") as f:
                            json.dump(plan_data, f, indent=4)
                    except Exception as ex_sync:
                        print(f"Warning: Failed to sync updated plan to docs_plan {docs_plan}: {ex_sync}")

                # Resolve variant source file
                variant_candidates = [
                    os.path.join("clips", f"{ep_num}-{clip_num}-{source}.mp4"),
                ]
                if source == "manim":
                    variant_candidates.append(os.path.join("clips", f"{ep_num}-{clip_num}-infographic.mp4"))
                elif source == "mosaic":
                    m_run_id = t_clip.get("mosaic_run_id")
                    if m_run_id:
                        ensure_local_cache(ep_num, f"{ep_num}-{clip_num}-mosaic-{m_run_id}.mp4")
                        variant_candidates.append(read_working_asset(ep_num, f"{ep_num}-{clip_num}-mosaic-{m_run_id}.mp4"))
                    ensure_local_cache(ep_num, f"{ep_num}-{clip_num}-original.mp4")
                    ensure_audio_slice_cache(ep_num, clip_num)
                    variant_candidates.append(read_working_asset(ep_num, f"{ep_num}-{clip_num}-original.mp4"))

                chosen_variant = None
                for cand in variant_candidates:
                    if os.path.exists(cand) and os.path.getsize(cand) > 10000:
                        chosen_variant = cand
                        break

                synced_deepdive = False
                if chosen_variant:
                    target_mp4 = os.path.join("clips", f"{ep_num}-{clip_num}.mp4")
                    shutil.copy2(chosen_variant, target_mp4)
                    
                    try:
                        deepdive_clips_dir = resolve_deepdive_publication_clips_dir(ep_num)
                        print(f"[{project_id}][Clip {clip_num}] Resolved deepDive publication root: {deepdive_clips_dir}")
                        deepdive_clips_dir.mkdir(parents=True, exist_ok=True)
                        dest_deepdive = os.path.join(str(deepdive_clips_dir), f"{ep_num}-{clip_num}.mp4")
                        shutil.copy2(target_mp4, dest_deepdive)
                        synced_deepdive = True
                        print(f"[{project_id}][Clip {clip_num}] Promoted {source} to ACTIVE MASTER -> synced to deepDive: {dest_deepdive}")
                    except Exception as sync_e:
                        print(f"[{project_id}][Clip {clip_num}] ERROR: Failed to sync promoted active master to deepDive: {sync_e}")
                        raise Exception(f"Failed to stage active master in deepDive publication repo: {sync_e}")
                else:
                    # If variant file doesn't exist yet, trigger compile-clip with this source
                    print(f"[{project_id}][Clip {clip_num}] Compiling fresh {source} as active master...")
                    subprocess.run([sys.executable, "ddma.py", "compile-clip", "--num", str(clip_num), "--plan-file", plan_path, "--source", source], check=True)
                    try:
                        deepdive_clips_dir = resolve_deepdive_publication_clips_dir(ep_num)
                        dest_deepdive = os.path.join(str(deepdive_clips_dir), f"{ep_num}-{clip_num}.mp4")
                        if not os.path.exists(dest_deepdive):
                            raise Exception(f"compile-clip succeeded but active master was not staged to {dest_deepdive}")
                        synced_deepdive = True
                    except Exception as verify_e:
                        print(f"[{project_id}][Clip {clip_num}] ERROR: Verification failed after compile-clip: {verify_e}")
                        raise Exception(f"Failed to verify staged active master: {verify_e}")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "active_master": source,
                    "synced_deepdive": synced_deepdive,
                    "message": f"Active master switched to {source}."
                }).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/compile-clip':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            is_draft = params.get('draft', ['false'])[0].lower() in ('true', '1')
            req_source = params.get('source', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                
                plan_path = os.path.join("projects", project_id, "plan.json")
                if not os.path.exists(plan_path):
                    plan_path = "plan.json"

                ep_num = project_id.replace('episode_', '')
                info_path = os.path.join("projects", project_id, "project_info.json")
                p_info = {}
                ep_title = "Life, Death and the Lysosome"
                if os.path.exists(info_path):
                    with open(info_path, "r", encoding="utf-8") as f_info:
                        p_info = json.load(f_info)
                        if p_info.get("title"):
                            ep_title = p_info["title"]
                        elif p_info.get("name"):
                            ep_title = p_info["name"]
                audio_file = get_project_canonical_audio_path(os.path.join("projects", project_id), project_id, p_info)

                # Smart signature check to avoid redundant audio slicing or video re-encoding
                import hashlib, glob
                need_audio_cut = True
                try:
                    with open(plan_path, "r", encoding="utf-8") as pf_chk:
                        p_data_chk = json.load(pf_chk)
                    t_clip = next((c for c in p_data_chk if str(c.get("num")) == str(clip_num)), None)
                    if t_clip:
                        if not is_draft and not t_clip.get("locked"):
                            self.send_response(403)
                            self.send_header("Content-type", "application/json")
                            self.send_header("Access-Control-Allow-Origin", "*")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": False, "error": f"Clip {clip_num} is unlocked. Lock clip before compiling."}).encode("utf-8"))
                            return
                        if req_source in ("mosaic", "infographic") and t_clip.get("visual_source") != req_source:
                            t_clip["visual_source"] = req_source
                            with open(plan_path, "w", encoding="utf-8") as pf_w:
                                json.dump(p_data_chk, pf_w, indent=4)
                        curr_audio_sig = hashlib.md5((json.dumps(t_clip.get("segments", []), sort_keys=True) + str(audio_file)).encode("utf-8")).hexdigest()
                        curr_compile_sig = hashlib.md5(json.dumps({
                            "title": t_clip.get("title", ""),
                            "ep_title": ep_title,
                            "bridge_text": t_clip.get("bridge_text", ""),
                            "mosaic_run_id": t_clip.get("mosaic_run_id"),
                            "visual_source": t_clip.get("visual_source", ""),
                            "infographic_scenes": t_clip.get("infographic_scenes", []),
                            "segments": t_clip.get("segments", []),
                            "force_draft": is_draft,
                            "text": t_clip.get("text", ""),
                            "caption_chunks": t_clip.get("caption_chunks", []),
                            "vertical_format": "1080x1920_ass_v1"
                        }, sort_keys=True).encode("utf-8")).hexdigest()
                        out_mp4 = os.path.join("clips", f"{ep_num}-{clip_num}.mp4")
                        if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 10000 and t_clip.get("_compiled_sig") == curr_compile_sig:
                            print(f"[{project_id}][Clip {clip_num}] Fast-Hit: Master video {out_mp4} is already up-to-date! Returning immediately.")
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": True, "cached": True, "message": "Master video is already compiled and up to date."}).encode('utf-8'))
                            return
                        existing_mp3s = glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}-*.mp3")) + glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}.mp3"))
                        if existing_mp3s and t_clip.get("_audio_sig") == curr_audio_sig:
                            need_audio_cut = False
                            print(f"[{project_id}][Clip {clip_num}] Fast-Hit: Audio segments unchanged, skipping ddma.py cut.")
                except Exception as sig_err:
                    print(f"[{project_id}][Clip {clip_num}] Warning checking cache signatures: {sig_err}")

                # 1. Re-slice fresh audio from plan.json for this clip only if segments changed or MP3 missing
                if need_audio_cut and audio_file and os.path.exists(audio_file):
                    cut_cmd = [sys.executable, "ddma.py", "cut", "--audio", audio_file, "--plan-file", plan_path, "--out-dir", "clips", "--num", str(clip_num)]
                    print(f"[{project_id}][Clip {clip_num}] Re-slicing fresh audio for Clip {clip_num}: {' '.join(cut_cmd)}")
                    res_cut = subprocess.run(cut_cmd, capture_output=True, text=True, cwd=".")
                    if res_cut.returncode != 0:
                        print(f"[{project_id}][Clip {clip_num}] Warning: Audio re-slicing emitted stderr: {res_cut.stderr}")

                # 2. Synchronously compile intro card, equalized master body, and outro curiosity card
                cmd = [sys.executable, "ddma.py", "compile-clip", "--num", str(clip_num), "--plan-file", plan_path]
                if req_source:
                    src_flag = "manim" if req_source in ("infographic", "manim") else "mosaic"
                    cmd.extend(["--source", src_flag])
                if is_draft:
                    cmd.append("--force-draft")
                print(f"[{project_id}][Clip {clip_num}] Starting synchronous compilation: {' '.join(cmd)}")
                proc = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
                if proc.returncode != 0:
                    raise Exception(f"Compile-clip failed with return code {proc.returncode}: {proc.stderr}")
                print(f"[{project_id}][Clip {clip_num}] Synchronous compilation completed successfully!")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": "Compilation completed successfully."}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                notify_failure("W3", "compile-clip", f"{project_id} clip {clip_num}: {e}")
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/publish-clip':
            # Issue 80: per-clip Publish. Locked-gated, scoped git add/commit/push.
            # The lock is the human's sign-off -- never auto-lock here.
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")

                # (a) Verify the clip is locked -- hub plan is primary (load_plan is hub-first).
                plan_data = load_plan(project_id, writer="curator")
                target_clip = None
                for c in plan_data:
                    if int(c.get("num", -1)) == int(clip_num):
                        target_clip = c
                        break
                if target_clip is None:
                    raise Exception(f"Clip {clip_num} not found in plan for {project_id}.")
                if not target_clip.get("locked"):
                    self.send_response(403)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": f"Clip {clip_num} is unlocked. Lock clip before publishing."}).encode("utf-8"))
                    return

                ep_num = str(project_id.replace('episode_', '')).replace('.md', '').lstrip('_')
                master_name = f"{ep_num}-{clip_num}.mp4"

                # (b) Ensure the finished canonical master exists: local cache, else hub primary, else compile.
                os.makedirs("clips", exist_ok=True)
                local_master = os.path.join("clips", master_name)
                if not (os.path.exists(local_master) and os.path.getsize(local_master) > 10000):
                    hub_master = working_asset_hub_path(ep_num, master_name)
                    if hub_master and os.path.exists(hub_master) and os.path.getsize(hub_master) > 10000:
                        print(f"[{project_id}][Clip {clip_num}] Recovering finished master from hub primary store.")
                        shutil.copy2(hub_master, local_master)
                    else:
                        print(f"[{project_id}][Clip {clip_num}] No finished master -- compiling via ddma.py cut + compile-clip.")
                        local_plan_path = os.path.join("projects", project_id, "plan.json")
                        info_path = os.path.join("projects", project_id, "project_info.json")
                        p_info = {}
                        if os.path.exists(info_path):
                            with open(info_path, "r", encoding="utf-8") as f_info:
                                p_info = json.load(f_info)
                        audio_file = get_project_canonical_audio_path(os.path.join("projects", project_id), project_id, p_info)
                        if audio_file and os.path.exists(audio_file):
                            cut_cmd = [sys.executable, "ddma.py", "cut", "--audio", audio_file, "--plan-file", local_plan_path, "--out-dir", "clips", "--num", str(clip_num)]
                            subprocess.run(cut_cmd, capture_output=True, text=True, cwd=".")
                        cmd = [sys.executable, "ddma.py", "compile-clip", "--num", str(clip_num), "--plan-file", local_plan_path]
                        src = (target_clip.get("visual_source") or "mosaic").lower()
                        cmd.extend(["--source", "manim" if src in ("infographic", "manim") else "mosaic"])
                        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
                        if proc.returncode != 0:
                            raise Exception(f"Compile-clip failed with return code {proc.returncode}: {proc.stderr[-500:] if proc.stderr else ''}")
                if not (os.path.exists(local_master) and os.path.getsize(local_master) > 10000):
                    raise Exception(f"Finished master {master_name} is not available (local, hub, and compile all missed).")

                # (c) Resolve the deepDive repo root from git itself (not directory layout):
                # the published master lives in deepDive's src/, and the git commands
                # below must run inside the deepDive git repo.
                try:
                    _rp = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                         capture_output=True, text=True, cwd=str(DDMA_DIR))
                    repo_root = _rp.stdout.strip() if _rp.returncode == 0 else ""
                except Exception:
                    repo_root = ""
                if not repo_root or not os.path.isdir(os.path.join(repo_root, "src", "ddma", "docs", "episodes")):
                    raise Exception(
                        f"Curator must run from inside the deepDive git repo to publish "
                        f"(resolved repo root from {DDMA_DIR}: {repo_root or 'not a git repo'}).")
                dest_dir = os.path.join(repo_root, "src", "ddma", "docs", "episodes", ep_num, "clips")
                os.makedirs(dest_dir, exist_ok=True)
                dest_clip = os.path.join(dest_dir, master_name)
                shutil.copy2(local_master, dest_clip)

                # (d) Regenerate the episodes manifest (both copies) so availableClips includes the new clip.
                try:
                    ingest_dir = os.path.join(repo_root, "ingest")
                    if ingest_dir not in sys.path:
                        sys.path.insert(0, ingest_dir)
                    import server as _ingest_server
                    _ingest_server.regenerate_episodes_manifest()
                except Exception as me:
                    print(f"[{project_id}][Clip {clip_num}] Manifest regen via ingest failed ({me}) -- surgical fallback.")
                    for mpath in [os.path.join(repo_root, "ddma", "docs", "episodes.json"),
                                  os.path.join(repo_root, "src", "ddma", "docs", "episodes.json")]:
                        try:
                            mdata = []
                            if os.path.exists(mpath):
                                with open(mpath, "r", encoding="utf-8") as mf:
                                    mdata = json.load(mf)
                            if not isinstance(mdata, list):
                                mdata = []
                            entry = next((e for e in mdata if isinstance(e, dict) and str(e.get("id") or e.get("number")) == str(ep_num)), None)
                            if entry is None:
                                entry = {"id": str(ep_num), "number": int(ep_num) if str(ep_num).isdigit() else ep_num,
                                         "title": f"Episode {ep_num}", "planPath": f"episodes/{ep_num}/plan.json",
                                         "clipsDir": f"episodes/{ep_num}/clips", "isDefault": False}
                                mdata.append(entry)
                            avail = entry.get("availableClips") or []
                            if int(clip_num) not in [int(x) for x in avail]:
                                avail.append(int(clip_num))
                            entry["availableClips"] = sorted(avail)
                            os.makedirs(os.path.dirname(mpath), exist_ok=True)
                            with open(mpath, "w", encoding="utf-8") as mf:
                                json.dump(mdata, mf, indent=2)
                        except Exception as fe:
                            print(f"[{project_id}][Clip {clip_num}] Manifest fallback failed for {mpath}: {fe}")

                # (d2) Write the distribution fields into the plan BEFORE the scoped commit:
                # the rendered duration (probed from the staged canonical master) plus the
                # published flag + URL. Hub-first via save_plan (mirrors to the docs/ and
                # src/ published plan copies), so the commit below picks up the copy too.
                clip_url = (f"https://github.com/ashutoshmjain/deepDive/blob/master/src/ddma/docs/episodes/"
                            f"{ep_num}/clips/{master_name}")
                try:
                    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                                            local_master],
                                           capture_output=True, text=True, timeout=30)
                    rendered_dur = round(float(probe.stdout.strip()), 2)
                except Exception as pe:
                    raise Exception(f"Could not probe rendered duration of {master_name}: {pe}")
                target_clip["rendered_duration"] = rendered_dur
                target_clip["published"] = True
                target_clip["published_url"] = clip_url
                save_plan(project_id, plan_data, writer="curator")

                # (e) Scoped git add + commit + push (cwd = repo root). ONLY the clip,
                # the published plan copy, and both manifests.
                # NOTE: forward slashes -- a backslash pathspec can silently match nothing on Git for Windows.
                # Idempotent: if everything already matches HEAD (re-publish), report success without committing.
                rel_clip = "src/ddma/docs/episodes/%s/clips/%s" % (ep_num, master_name)
                rel_plancopy = "src/ddma/docs/episodes/%s/plan.json" % ep_num
                rel_manifests = ["ddma/docs/episodes.json",
                                 "src/ddma/docs/episodes.json"]
                rel_scope = [rel_clip, rel_plancopy] + rel_manifests
                already = False
                try:
                    subprocess.run(["git", "add"] + rel_scope, cwd=repo_root, check=True,
                                   capture_output=True, text=True)
                    staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=repo_root,
                                            capture_output=True, text=True)
                    if not staged.stdout.strip():
                        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--"] + rel_scope,
                                               cwd=repo_root, capture_output=True)
                        if clean.returncode == 0:
                            # Remote-aware idempotency (Issue 91): files matching
                            # the LOCAL head is not enough -- the publish commit
                            # may sit unpushed after a failed push. Only report
                            # "already published" when the remote already has HEAD.
                            subprocess.run(["git", "fetch", "origin", "master", "--quiet"],
                                           cwd=repo_root, check=True,
                                           capture_output=True, text=True)
                            ahead = subprocess.run(["git", "rev-list", "--count", "origin/master..HEAD"],
                                                   cwd=repo_root, check=True,
                                                   capture_output=True, text=True)
                            if ahead.stdout.strip() == "0":
                                already = True
                            else:
                                # Unpushed publish commit(s): push now, succeed
                                # only if the push succeeds (same loud failure
                                # as the fresh path via CalledProcessError).
                                subprocess.run(["git", "push"], cwd=repo_root, check=True,
                                               capture_output=True, text=True)
                        else:
                            raise Exception("git add staged nothing though working files differ from HEAD -- refusing to call it published.")
                    if not already:
                        subprocess.run(["git", "commit", "-m", f"publish: clip {ep_num}-{clip_num} via ddma curator"],
                                       cwd=repo_root, check=True, capture_output=True, text=True)
                        subprocess.run(["git", "push"], cwd=repo_root, check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as ge:
                    raise Exception(f"Git publish failed: {(ge.stderr or ge.stdout or ge)[:500]}")

                # (f) Success with the GitHub URL of the published clip.
                # (Distribution fields were written + mirrored in (d2) above, fresh and
                # already-published paths alike.)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "url": clip_url, "clip": master_name, "already_published": already, "persisted": True}).encode('utf-8'))
                return
            except Exception as e:
                print(f"[publish-clip] {project_id} clip {clip_num}: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/open-storyboard-in-editor':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                filepath = get_storyboard_filepath(project_id, clip_num)
                if not os.path.exists(filepath):
                    generate_or_load_storyboard_data(project_id, clip_num)
                
                settings = load_settings()
                editor_cmd = settings.get("external_editor") or os.environ.get("VISUAL") or os.environ.get("EDITOR") or "gvim"
                try:
                    cmd_args = shlex.split(editor_cmd, posix=(os.name != 'nt'))
                except Exception:
                    cmd_args = [editor_cmd]
                
                if shutil.which(cmd_args[0]) is None:
                    local_gvim = os.path.expandvars(r'%LOCALAPPDATA%\Programs\Vim\gvim.exe')
                    local_vim = os.path.expandvars(r'%LOCALAPPDATA%\Programs\Vim\vim.exe')
                    if 'gvim' in cmd_args[0].lower() and os.path.exists(local_gvim):
                        cmd_args[0] = local_gvim
                    elif 'vim' in cmd_args[0].lower() and os.path.exists(local_vim):
                        cmd_args[0] = local_vim

                cmd_args = [arg for arg in cmd_args if arg not in ('-f', '--nofork')]
                cmd_args.append(filepath)
                print(f"[{project_id}][Clip {clip_num}] Launching external editor on storyboard: {cmd_args}")
                
                if os.name == 'nt':
                    editor_exe = cmd_args[0]
                    remaining_args = " ".join([f'"{a}"' for a in cmd_args[1:]])
                    ps_cmd = f"Start-Process -FilePath '{editor_exe}' -ArgumentList '{remaining_args}'"
                    subprocess.Popen(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_cmd])
                else:
                    subprocess.Popen(cmd_args)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "filepath": filepath,
                    "filename": os.path.basename(filepath),
                    "editor": editor_cmd,
                    "message": f"Opened {os.path.basename(filepath)} in {editor_cmd}."
                }).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/sync-storyboard':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                filepath = get_storyboard_filepath(project_id, clip_num)
                if not os.path.exists(filepath):
                    raise Exception(f"Storyboard file {filepath} not found on disk.")
                
                with open(filepath, "r", encoding="utf-8") as f:
                    sb = json.load(f)
                
                scenes = sb.get("scenes") or []
                if not scenes:
                    raise Exception("No scenes found in storyboard file.")
                
                plan_path = os.path.join("projects", project_id, "plan.json")
                if not os.path.exists(plan_path):
                    plan_path = "plan.json"
                with open(plan_path, "r", encoding="utf-8") as pf:
                    plan_data = json.load(pf)
                t_clip = next((c for c in plan_data if str(c.get("num")) == str(clip_num)), None)
                if t_clip:
                    t_clip["infographic_scenes"] = scenes
                    with open(plan_path, "w", encoding="utf-8") as pf_w:
                        json.dump(plan_data, pf_w, indent=4)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "storyboard": sb,
                    "scene_count": len(scenes)
                }).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/save-storyboard':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                raw_body = self.rfile.read(content_len).decode('utf-8')
                sb_data = json.loads(raw_body)
                
                filepath = get_storyboard_filepath(project_id, clip_num)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(sb_data, f, indent=2)
                
                scenes = sb_data.get("scenes") or []
                plan_path = os.path.join("projects", project_id, "plan.json")
                if not os.path.exists(plan_path):
                    plan_path = "plan.json"
                with open(plan_path, "r", encoding="utf-8") as pf:
                    plan_data = json.load(pf)
                t_clip = next((c for c in plan_data if str(c.get("num")) == str(clip_num)), None)
                if t_clip and scenes:
                    t_clip["infographic_scenes"] = scenes
                    with open(plan_path, "w", encoding="utf-8") as pf_w:
                        json.dump(plan_data, pf_w, indent=4)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/render-local-infographic':
            try:
                query = parse_qs(parsed_url.query)
                project_id = query.get('id', [None])[0]
                clip_num = query.get('num', [None])[0]
                force_regen = query.get('force', ['false'])[0].lower() in ('true', '1')

                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing id or num parameter")

                content_len = int(self.headers.get('Content-Length', 0))
                req_body = {}
                if content_len > 0:
                    raw_body = self.rfile.read(content_len).decode('utf-8')
                    try:
                        req_body = json.loads(raw_body)
                    except Exception:
                        pass
                custom_instructions = str(req_body.get("directive") or req_body.get("instructions") or "").strip()

                if os.getcwd() not in sys.path:
                    sys.path.insert(0, os.getcwd())
                import glob
                import importlib
                import ddma as ddma_mod
                import infographic_engine
                import manim_infographic_engine
                importlib.reload(infographic_engine)

                plan_path = os.path.join("projects", project_id, "plan.json")
                if not os.path.exists(plan_path):
                    plan_path = "plan.json"

                with open(plan_path, "r", encoding="utf-8") as pf:
                    plan_data = json.load(pf)

                t_clip = next((c for c in plan_data if str(c.get("num")) == str(clip_num)), None)
                if not t_clip:
                    raise Exception(f"Clip {clip_num} not found in {plan_path}")

                ep_num = project_id.replace('episode_', '')
                info_path = os.path.join("projects", project_id, "project_info.json")
                p_info = {}
                if os.path.exists(info_path):
                    with open(info_path, "r", encoding="utf-8") as f_info:
                        p_info = json.load(f_info)
                audio_file = get_project_canonical_audio_path(os.path.join("projects", project_id), project_id, p_info)

                # 1. Ensure sliced clip MP3 exists & is up to date with segments
                import hashlib
                curr_audio_sig = hashlib.md5((json.dumps(t_clip.get("segments", []), sort_keys=True) + str(audio_file)).encode("utf-8")).hexdigest()
                
                # Compute expected duration from segments
                segs = t_clip.get("segments", [])
                expected_dur = sum(float(s.get("duration", 0.0)) for s in segs) - sum(float(s.get("crossfade", 0.0)) for s in segs[:-1]) if segs else 0.0

                mp3_matches = glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}-*.mp3")) + glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}.mp3"))
                need_audio_cut = force_regen or not mp3_matches or (t_clip.get("_audio_sig") != curr_audio_sig)
                
                # Check probed duration of existing MP3 against expected segments duration
                if not need_audio_cut and mp3_matches:
                    mp3_matches.sort(key=os.path.getmtime, reverse=True)
                    try:
                        p_probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", mp3_matches[0]], capture_output=True, text=True)
                        if p_probe.returncode == 0 and p_probe.stdout.strip():
                            probed_dur = float(p_probe.stdout.strip())
                            if expected_dur > 0 and abs(probed_dur - expected_dur) > 1.5:
                                print(f"[{project_id}][Clip {clip_num}] Existing MP3 duration ({probed_dur:.2f}s) mismatch with segments ({expected_dur:.2f}s). Re-cutting...")
                                need_audio_cut = True
                    except Exception:
                        pass

                if need_audio_cut and audio_file and os.path.exists(audio_file):
                    print(f"[{project_id}][Clip {clip_num}] Re-slicing fresh audio from segments...")
                    for old_m in mp3_matches:
                        try:
                            if os.path.exists(old_m):
                                os.remove(old_m)
                        except Exception:
                            pass
                    old_info_mp4 = os.path.join("clips", f"{ep_num}-{clip_num}-infographic.mp4")
                    if os.path.exists(old_info_mp4):
                        try:
                            os.remove(old_info_mp4)
                        except Exception:
                            pass
                    cut_res = subprocess.run([sys.executable, "ddma.py", "cut", "--audio", audio_file, "--plan-file", plan_path, "--out-dir", "clips", "--num", str(clip_num)], capture_output=True, text=True, cwd=".")
                    if cut_res.returncode != 0:
                        print(f"[{project_id}][Clip {clip_num}] Cut warning/error: {cut_res.stderr}")
                    mp3_matches = glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}-*.mp3")) + glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}.mp3"))

                if not mp3_matches:
                    raise Exception(f"Could not locate or slice clip MP3 for Clip {clip_num}")
                mp3_matches.sort(key=os.path.getmtime, reverse=True)
                clip_mp3 = mp3_matches[0]

                # 2. Compute body duration & ensure caption_chunks exist
                body_dur = 0.0
                try:
                    p_dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", clip_mp3], capture_output=True, text=True)
                    if p_dur.returncode == 0 and p_dur.stdout.strip():
                        body_dur = float(p_dur.stdout.strip())
                except Exception:
                    pass
                if body_dur <= 0:
                    body_dur = expected_dur if expected_dur > 0 else 60.0

                sorted_clips = sorted(plan_data, key=lambda x: x.get("num", 0))
                is_last = (sorted_clips[-1].get("num") == t_clip.get("num")) if sorted_clips else False

                curr_caption_sig = hashlib.md5(json.dumps({
                    "segments": t_clip.get("segments", []),
                    "text": t_clip.get("text", ""),
                    "intro_offset": 1.5,
                    "has_outro": (not is_last)
                }, sort_keys=True).encode("utf-8")).hexdigest()

                if need_audio_cut or not t_clip.get("caption_chunks") or t_clip.get("_caption_sig") != curr_caption_sig:
                    print(f"[{project_id}][Clip {clip_num}] Re-aligning captions for fresh audio/segments...")
                    ddma_mod.generate_clip_captions(
                        t_clip, plan_file=plan_path, audio_path=clip_mp3,
                        intro_offset=1.5, body_duration=body_dur, has_outro=(not is_last),
                        force_realign=True
                    )
                    t_clip["_caption_sig"] = curr_caption_sig

                INFOGRAPHIC_ENGINE_VERSION = "v4_precompiled_archetypes"
                infographic_mp4 = os.path.join("clips", f"{ep_num}-{clip_num}-infographic.mp4")

                import archetype_studio
                importlib.reload(archetype_studio)
                stitched_from_library = False
                if not custom_instructions:
                    stitched_from_library = archetype_studio.stitch_precompiled_archetypes_for_clip(
                        int(clip_num), clip_mp3, infographic_mp4, body_dur, plan_clip=t_clip
                    )

                if stitched_from_library:
                    meta_obj = archetype_studio.ensure_clip_meta(int(clip_num), plan_clip=t_clip, body_duration=body_dur)
                    t_clip["infographic_scenes"] = meta_obj.get("beats", [])
                    print(f"[{project_id}][Clip {clip_num}] Super-fast stitched {len(t_clip['infographic_scenes'])} pre-compiled archetypes into {infographic_mp4}!")
                else:
                    sb_disk_path = get_storyboard_filepath(project_id, clip_num)
                    scenes = req_body.get("scenes")
                    if not scenes and os.path.exists(sb_disk_path):
                        try:
                            with open(sb_disk_path, "r", encoding="utf-8") as sbf:
                                sb_disk_data = json.load(sbf)
                                if sb_disk_data.get("scenes"):
                                    scenes = sb_disk_data["scenes"]
                                    t_clip["infographic_scenes"] = scenes
                        except Exception:
                            pass
                    if not scenes:
                        scenes = t_clip.get("infographic_scenes")
                    if not scenes or (force_regen and not os.path.exists(sb_disk_path) and not req_body.get("scenes")):
                        settings = load_settings()
                        api_key = settings.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
                        g_mod = genai if (HAS_GENAI and configure_gemini(api_key)) else None
                        scenes = manim_infographic_engine.generate_pedagogical_storyboard(
                            t_clip, body_duration=body_dur, intro_offset=1.5,
                            custom_instructions=custom_instructions, genai_mod=g_mod,
                            force_regenerate=True
                        )
                        t_clip["infographic_scenes"] = scenes
                    manim_infographic_engine.render_manim_infographic_mp4(scenes, clip_mp3, infographic_mp4, duration=body_dur)

                t_clip["_audio_sig"] = curr_audio_sig
                t_clip["audio_duration"] = round(body_dur, 2)
                if not t_clip.get("visual_source"):
                    t_clip["visual_source"] = "manim"
                t_clip["infographic_ready"] = True
                t_clip["_infographic_version"] = INFOGRAPHIC_ENGINE_VERSION
                with open(plan_path, "w", encoding="utf-8") as pf_w:
                    json.dump(plan_data, pf_w, indent=4)

                docs_plan_path = os.path.join("docs", "episodes", ep_num, "plan.json")
                if os.path.exists(docs_plan_path):
                    try:
                        with open(docs_plan_path, "w", encoding="utf-8") as dpf_w:
                            json.dump(plan_data, dpf_w, indent=4)
                    except Exception:
                        pass

                # 3. Compile 1080x1920 vertical captioned video with the 740x740 infographic
                cmd_comp = [sys.executable, "ddma.py", "compile-clip", "--num", str(clip_num), "--plan-file", plan_path, "--source", "manim"]
                proc = subprocess.run(cmd_comp, capture_output=True, text=True, cwd=".")
                if proc.returncode != 0:
                    raise Exception(f"compile-clip failed: {proc.stderr}")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "infographic_file": infographic_mp4,
                    "video_url": f"/clips/{ep_num}-{clip_num}-manim.mp4",
                    "active_master": t_clip.get("visual_source", "mosaic"),
                    "scenes_count": len(t_clip.get("infographic_scenes", [])),
                    "message": "740x740 Manim Pedagogical Video rendered and compiled into 1080x1920 captioned video!"
                }).encode('utf-8'))
                return
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/update-archetype-beat':
            try:
                query = parse_qs(parsed_url.query)
                project_id = query.get('id', [None])[0]
                clip_num = int(query.get('num', [0])[0])
                content_len = int(self.headers.get('Content-Length', 0))
                req_body = json.loads(self.rfile.read(content_len).decode('utf-8')) if content_len > 0 else {}

                class_name = str(req_body.get("class_name", "")).strip()
                beat_index = int(req_body.get("beat_index", 1))
                directive = str(req_body.get("directive", "")).strip()
                spoken_text = str(req_body.get("spoken_text", "")).strip()
                duration = float(req_body.get("duration", 7.5))
                custom_code = req_body.get("custom_code")
                recompile_short = bool(req_body.get("recompile_short", True))

                if os.getcwd() not in sys.path:
                    sys.path.insert(0, os.getcwd())
                import importlib
                import archetype_studio
                importlib.reload(archetype_studio)

                res_update = archetype_studio.update_single_scene_with_ai(
                    clip_num=clip_num,
                    beat_index=beat_index,
                    class_name=class_name,
                    user_directive=directive,
                    spoken_text=spoken_text,
                    duration=duration,
                    custom_code=custom_code,
                )

                ep_num = project_id.replace('episode_', '') if project_id else "248"
                short_video_url = f"/clips/{ep_num}-{clip_num}-manim.mp4?t={int(time.time())}"

                if recompile_short and project_id:
                    plan_path = os.path.join("projects", project_id, "plan.json")
                    if not os.path.exists(plan_path):
                        plan_path = "plan.json"
                    with open(plan_path, "r", encoding="utf-8") as pf:
                        plan_data = json.load(pf)
                    t_clip = next((c for c in plan_data if str(c.get("num")) == str(clip_num)), None)
                    import glob as _glob
                    mp3_matches = _glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}-*.mp3")) + _glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}.mp3"))
                    if mp3_matches and t_clip:
                        mp3_matches.sort(key=os.path.getmtime, reverse=True)
                        clip_mp3 = mp3_matches[0]
                        body_dur = float(t_clip.get("audio_duration") or t_clip.get("duration") or 120.0)
                        infographic_mp4 = os.path.join("clips", f"{ep_num}-{clip_num}-infographic.mp4")
                        archetype_studio.stitch_precompiled_archetypes_for_clip(
                            clip_num, clip_mp3, infographic_mp4, body_dur, plan_clip=t_clip
                        )
                        subprocess.run([sys.executable, "ddma.py", "compile-clip", "--num", str(clip_num), "--plan-file", plan_path, "--source", "manim"], capture_output=True, text=True, cwd=".")

                meta_obj = archetype_studio.ensure_clip_meta(clip_num)
                res_update["short_video_url"] = short_video_url
                res_update["meta"] = meta_obj

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(res_update).encode('utf-8'))
                return
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/generate-clip-captions':
            try:
                query = parse_qs(parsed_url.query)
                project_id = query.get('id', [None])[0]
                clip_num = query.get('num', [None])[0]
                force_whisper = query.get('whisper', ['false'])[0].lower() == 'true'

                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing id or num parameter")

                content_len = int(self.headers.get('Content-Length', 0))
                req_body = {}
                if content_len > 0:
                    raw_body = self.rfile.read(content_len).decode('utf-8')
                    try:
                        req_body = json.loads(raw_body)
                    except Exception:
                        pass

                plan_path = os.path.join("projects", project_id, "plan.json")
                if not os.path.exists(plan_path):
                    plan_path = "plan.json"

                with open(plan_path, "r", encoding="utf-8") as pf:
                    plan_data = json.load(pf)

                t_clip = next((c for c in plan_data if str(c.get("num")) == str(clip_num)), None)
                if not t_clip:
                    raise Exception(f"Clip {clip_num} not found in {plan_path}")

                if "text" in req_body and req_body["text"] is not None:
                    t_clip["text"] = req_body["text"]

                ep_num = project_id.replace('episode_', '')
                import glob
                if os.getcwd() not in sys.path:
                    sys.path.insert(0, os.getcwd())
                import ddma as ddma_mod

                # Ensure rendered clip MP3 exists if force_whisper is requested
                mp3_matches = glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}-*.mp3")) + glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}.mp3"))
                if force_whisper and not mp3_matches:
                    info_path = os.path.join("projects", project_id, "project_info.json")
                    audio_file = None
                    if os.path.exists(info_path):
                        with open(info_path, "r", encoding="utf-8") as f_info:
                            p_info = json.load(f_info)
                            audio_file = p_info.get("audio_file") or p_info.get("audio_filename")
                    if audio_file and not os.path.exists(audio_file):
                        audio_file = os.path.join("projects", project_id, audio_file)
                    if not audio_file or not os.path.exists(audio_file):
                        for candidate_ext in [f"{ep_num}.m4a", f"{ep_num}.mp3", f"episode_{ep_num}.m4a", f"episode_{ep_num}.mp3"]:
                            candidate_path = os.path.join("projects", project_id, candidate_ext)
                            if os.path.exists(candidate_path):
                                audio_file = candidate_path
                                break
                    if audio_file and os.path.exists(audio_file):
                        subprocess.run([sys.executable, "ddma.py", "cut", "--audio", audio_file, "--plan-file", plan_path, "--out-dir", "clips", "--num", str(clip_num)], capture_output=True, text=True)
                        mp3_matches = glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}-*.mp3")) + glob.glob(os.path.join("clips", f"{ep_num}-{clip_num}.mp3"))

                audio_path_for_caps = mp3_matches[0] if mp3_matches else None

                # Compute body duration from segments
                body_dur = 0.0
                segs = t_clip.get("segments", [])
                if segs:
                    for idx_s, s_obj in enumerate(segs):
                        body_dur += float(s_obj.get("duration", 0.0))
                        if idx_s < len(segs) - 1:
                            body_dur -= float(s_obj.get("crossfade", 0.0))
                else:
                    body_dur = max(0.0, float(t_clip.get("end", 0.0)) - float(t_clip.get("start", 0.0)))

                sorted_clips = sorted(plan_data, key=lambda x: x.get("num", 0))
                is_last = (sorted_clips[-1].get("num") == t_clip.get("num")) if sorted_clips else False

                chunks = ddma_mod.generate_clip_captions(
                    t_clip,
                    plan_file=plan_path,
                    audio_path=audio_path_for_caps,
                    intro_offset=1.5,
                    body_duration=body_dur,
                    has_outro=(not is_last),
                    force_whisper=force_whisper,
                    force_realign=True
                )

                with open(plan_path, "w", encoding="utf-8") as pf_w:
                    json.dump(plan_data, pf_w, indent=4)

                docs_plan_path = os.path.join("docs", "episodes", ep_num, "plan.json")
                if os.path.exists(docs_plan_path):
                    try:
                        with open(docs_plan_path, "w", encoding="utf-8") as dpf_w:
                            json.dump(plan_data, dpf_w, indent=4)
                    except Exception:
                        pass

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "caption_chunks": chunks,
                    "count": len(chunks)
                }).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        self.send_error(404, "Not Found")

    def do_GET(self):
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        
        if parsed_url.path in ('/', ''):
            self.path = '/curator.html'
            return super().do_GET()

        if parsed_url.path == '/list-projects':
            projects_list = []
            projects_dir = "projects"
            if os.path.exists(projects_dir):
                for folder in sorted(os.listdir(projects_dir)):
                    info_path = os.path.join(projects_dir, folder, "project_info.json")
                    if os.path.exists(info_path):
                        try:
                            with open(info_path, "r", encoding="utf-8") as f:
                                projects_list.append(json.load(f))
                        except Exception as e:
                            print(f"Error reading info for project {folder}: {e}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(projects_list).encode('utf-8'))
            return
            
        elif parsed_url.path == '/get-project-audio':
            project_id = params.get('id', [None])[0]
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                project_dir = os.path.join("projects", project_id)
                info_path = os.path.join(project_dir, "project_info.json")
                if not os.path.exists(info_path):
                    raise Exception(f"Project info for {project_id} not found.")
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                audio_file_name = info.get("audio_filename") or info.get("audio_file")
                audio_path = os.path.join(project_dir, audio_file_name) if audio_file_name else None
                if not audio_path or not os.path.exists(audio_path):
                    ep_num = project_id.replace("episode_", "")
                    for ext in [".m4a", ".mp3", ".wav"]:
                        cand = os.path.join(project_dir, f"{ep_num}{ext}")
                        if os.path.exists(cand):
                            audio_path = cand
                            break
                    # Automatic fallback to workspace dd_hub/inputs/<ep_num> (and legacy agy_inputs/<ep_num>)
                    if not audio_path or not os.path.exists(audio_path):
                        for hub_base in [
                            os.path.join(resolve_dd_hub_root(), "inputs"),
                            os.path.join(resolve_dd_hub_root(), "agy_inputs"),
                        ]:
                            hub_dir = os.path.join(hub_base, str(ep_num))
                            if os.path.exists(hub_dir):
                                for fn in sorted(os.listdir(hub_dir)):
                                    if fn.lower().endswith((".m4a", ".mp3", ".wav")):
                                        ext = os.path.splitext(fn)[1].lower()
                                        dest_cand = os.path.join(project_dir, f"{ep_num}{ext}")
                                        try:
                                            shutil.copy2(os.path.join(hub_dir, fn), dest_cand)
                                            audio_path = dest_cand
                                            print(f"[Hub Audio Sync] Copied {fn} -> {dest_cand}")
                                            break
                                        except Exception as ge:
                                            print(f"[Hub Audio Sync] Error copying {fn}: {ge}")
                            if audio_path and os.path.exists(audio_path):
                                break
                if not audio_path or not os.path.exists(audio_path):
                    self.send_error(404, f"Audio file for project {project_id} not found.")
                    return
                
                # Delegate to super().do_GET() with path set to static audio file
                # This automatically provides full HTTP 206 Range request support for seeking!
                self.path = "/" + audio_path.replace("\\", "/")
                return super().do_GET()
            except Exception as e:
                self.send_error(500, f"Error getting project audio: {e}")
                return

        elif parsed_url.path == '/list-workspace-audio':
            # Named hub target: deepdive-workspace. Lists input audio under
            # the hub (dd_hub/inputs/**) -- never the app root, never Downloads.
            try:
                hub_root = resolve_dd_hub_root()
                inputs_dir = os.path.join(str(hub_root), "inputs")
                files = []
                if os.path.isdir(inputs_dir):
                    for dirpath, _d, fns in os.walk(inputs_dir):
                        for fn in sorted(fns):
                            if fn.lower().endswith((".mp3", ".wav", ".m4a", ".aac", ".flac")):
                                files.append(os.path.join(dirpath, fn))
                files.sort()
                payload = {"target": "deepdive-workspace",
                           "root": str(hub_root), "files": files}
            except Exception as e:
                self.send_error(500, f"deepdive-workspace unreachable: {e}")
                return
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
            return
            
        elif parsed_url.path == '/get-mosaic-prompt':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                
                project_dir = os.path.join("projects", project_id)
                plan_path = os.path.join(project_dir, "plan.json")
                if not os.path.exists(plan_path):
                    raise Exception(f"plan.json for project {project_id} not found.")
                
                try:
                    plan = safe_load_json(plan_path)
                except Exception as e:
                    raise Exception(f"plan.json for project {project_id} unreadable: {e}")
                
                target_clip = None
                for clip in plan:
                    if int(clip.get("num", -1)) == int(clip_num):
                        target_clip = clip
                        break
                
                if not target_clip:
                    raise Exception(f"Clip number {clip_num} not found in plan.")
                
                raw_segment_texts = []
                for seg in target_clip.get("segments", []):
                    if seg.get("type") == "audio" and seg.get("text"):
                        raw_segment_texts.append(seg.get("text").strip())
                raw_transcript = " ".join(raw_segment_texts)

                if target_clip.get("text") and target_clip.get("text").strip():
                    saved_text = target_clip.get("text").strip()
                    raw_words = len(raw_transcript.split())
                    saved_words = len(saved_text.split())
                    if raw_words > 0 and abs(saved_words - raw_words) / max(raw_words, saved_words) > 0.15:
                        transcript = raw_transcript
                    else:
                        transcript = saved_text
                else:
                    transcript = raw_transcript
                
                title = target_clip.get("title", f"Clip {clip_num}")
                prompt_content = build_mosaic_prompt_with_context(
                    title=title,
                    transcript=transcript
                )
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "prompt": prompt_content}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/get-bridge-review-prompt':
            project_id = params.get('id', [None])[0]
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                project_dir = os.path.join("projects", project_id)
                plan_path = os.path.join(project_dir, "plan.json")
                if not os.path.exists(plan_path):
                    raise Exception("plan.json not found.")
                
                sys.path.insert(0, ".")
                from scratch.review_episode_bridges import build_bridge_review_prompt
                prompt_content = build_bridge_review_prompt(plan_path)
                if not prompt_content:
                    raise Exception("Could not build episode bridge review prompt.")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "prompt": prompt_content}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return
            
        elif parsed_url.path == '/get-gemini-prompt':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                
                prompt_content = build_gemini_prompt(project_id, int(clip_num))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "prompt": prompt_content}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/get-episode-gemini-prompt':
            project_id = params.get('id', [None])[0]
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                
                prompt_template = get_gemini_episode_default_prompt()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "prompt": prompt_template}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return
            
        elif parsed_url.path == '/get-project':
            project_id = params.get('id', [None])[0]
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                
                project_dir = os.path.join("projects", project_id)
                info_path = os.path.join(project_dir, "project_info.json")
                plan_path = os.path.join(project_dir, "plan.json")
                trans_path = os.path.join(project_dir, "transcription.json")
                
                if not os.path.exists(project_dir):
                    raise Exception("Project directory not found.")
                
                with open(info_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                
                # Sync from dd_hub vault or src/.../plan.json if projects/ is missing or out-of-date
                import re
                ep_match = re.search(r"\d+", project_id)
                ep_str = ep_match.group(0) if ep_match else None
                if ep_str:
                    hub_root = resolve_dd_hub_root()
                    hub_plan = os.path.join(hub_root, "episodes", ep_str, "plan.json") if hub_root else None
                    src_plan = os.path.join("..", "src", "ddma", "docs", "episodes", ep_str, "plan.json")
                    docs_plan = os.path.join("docs", "episodes", ep_str, "plan.json")
                    sync_src = None
                    if hub_plan and os.path.exists(hub_plan):
                        if not os.path.exists(plan_path) or os.path.getmtime(hub_plan) > os.path.getmtime(plan_path):
                            sync_src = hub_plan
                    elif src_plan and os.path.exists(src_plan):
                        if not os.path.exists(plan_path) or os.path.getmtime(src_plan) > os.path.getmtime(plan_path):
                            sync_src = src_plan
                    elif docs_plan and os.path.exists(docs_plan):
                        if not os.path.exists(plan_path) or os.path.getmtime(docs_plan) > os.path.getmtime(plan_path):
                            sync_src = docs_plan
                    if sync_src:
                        try:
                            shutil.copy2(sync_src, plan_path)
                            print(f"[{project_id}] Synced plan.json from {sync_src} to {plan_path}")
                        except Exception as se:
                            print(f"Warning syncing plan: {se}")

                plan_data = []
                if os.path.exists(plan_path):
                    with open(plan_path, "r", encoding="utf-8-sig") as f:
                        plan_data = json.load(f)
                    try:
                        shutil.copy2(plan_path, "plan.json")
                        if os.path.exists("docs"):
                            shutil.copy2("plan.json", os.path.join("docs", "plan.json"))
                    except Exception as copy_err:
                        print(f"Error syncing project plan to root/docs: {copy_err}")
                        
                trans_data = None
                if os.path.exists(trans_path):
                    with open(trans_path, "r", encoding="utf-8") as f:
                        trans_data = json.load(f)
                
                has_snapshot = os.path.exists(os.path.join(project_dir, "plan_snapshot.json"))
                
                # Scan for compiled videos matching this project (e.g. episode 244 -> "244-*.mp4")
                compiled_videos_dict = {}
                import re
                ep_num_match = re.search(r'\d+', project_id)

                # Comprehensive Self-healing & Auto-Resume check (polling, downloads, interrupted compiles)
                heal_mosaic_project_state(project_id, plan_data)
                if ep_num_match:
                    ep_num = ep_num_match.group(0)
                    clips_dir = "clips"
                    if os.path.exists(clips_dir):
                        # Sort files so that named files (e.g., 244-1-Title.mp4) are processed first,
                        # and direct standard files (e.g., 244-1.mp4) are processed last, overwriting/prioritizing them.
                        for file in sorted(os.listdir(clips_dir)):
                            if file.startswith(f"{ep_num}-") and file.endswith(".mp4") and not file.endswith("-original.mp4") and not file.endswith("-infographic.mp4") and "-mosaic-" not in file:
                                try:
                                    parts = file.split("-")
                                    if len(parts) >= 2:
                                        clip_num_str = parts[1]
                                        if "." in clip_num_str:
                                            clip_num_str = clip_num_str.split(".")[0]
                                        clip_num = int(clip_num_str)
                                        
                                        # Prioritize the direct standard filename (e.g. 244-2.mp4) over named templates (e.g. 244-2-Title.mp4)
                                        is_direct = (len(parts) == 2 or (len(parts) == 3 and parts[2] == ""))
                                        if is_direct or clip_num not in compiled_videos_dict:
                                            compiled_videos_dict[clip_num] = {
                                                "num": clip_num,
                                                "filename": file,
                                                "url": f"/clips/{file}"
                                            }
                                except Exception:
                                    pass
                compiled_videos = list(compiled_videos_dict.values())
                
                # Scan for status indicators for all clip numbers
                clip_statuses = {}
                if ep_num_match and os.path.exists(clips_dir):
                    ep_num = ep_num_match.group(0)
                    for file in os.listdir(clips_dir):
                        if file.startswith(f"{ep_num}-"):
                            try:
                                parts = file.split("-")
                                if len(parts) >= 2:
                                    clip_num_str = parts[1]
                                    if "." in clip_num_str:
                                        clip_num_str = clip_num_str.split(".")[0]
                                    clip_num = int(clip_num_str)
                                    
                                    if clip_num not in clip_statuses:
                                        clip_statuses[clip_num] = {"has_audio": False, "video_state": "none", "has_mosaic_file": False, "has_infographic_file": False}
                                    
                                    if file.endswith(".mp3"):
                                        clip_statuses[clip_num]["has_audio"] = True
                                    elif file.endswith("-infographic.mp4") or file.endswith("-manim.mp4"):
                                        clip_statuses[clip_num]["video_state"] = "compiled"
                                        clip_statuses[clip_num]["has_infographic_file"] = True
                                    elif file.endswith("-original.mp4") or "-mosaic-" in file or file.endswith("-mosaic.mp4"):
                                        clip_statuses[clip_num]["video_state"] = "compiled"
                                        clip_statuses[clip_num]["has_mosaic_file"] = True
                                    elif file.endswith(".mp4"):
                                        if clip_statuses[clip_num].get("video_state") != "compiled":
                                            clip_statuses[clip_num]["video_state"] = "draft"
                            except Exception:
                                pass
                                
                    if isinstance(plan_data, list):
                        for c in plan_data:
                            c_num = c.get("num")
                            if c_num is not None and c.get("mosaic_run_id"):
                                m_run_id = c.get("mosaic_run_id")
                                v_file = read_working_asset(ep_num, f"{ep_num}-{c_num}-mosaic-{m_run_id}.mp4", quiet=True)
                                orig_file = read_working_asset(ep_num, f"{ep_num}-{c_num}-original.mp4", quiet=True)
                                hub_dir = os.path.dirname(working_asset_hub_path(ep_num, "x") or "")
                                any_mosaics = [f for f in (os.listdir(clips_dir) if os.path.exists(clips_dir) else []) if f.startswith(f"{ep_num}-{c_num}-mosaic-") and f.endswith(".mp4")]
                                any_mosaics += [f for f in (os.listdir(hub_dir) if hub_dir and os.path.exists(hub_dir) else []) if f.startswith(f"{ep_num}-{c_num}-mosaic-") and f.endswith(".mp4") and f not in any_mosaics]
                                if os.path.exists(v_file) or os.path.exists(orig_file) or len(any_mosaics) > 0:
                                    if c_num not in clip_statuses:
                                        clip_statuses[c_num] = {"has_audio": False, "video_state": "compiled", "has_mosaic_file": True}
                                    else:
                                        clip_statuses[c_num]["video_state"] = "compiled"
                                        clip_statuses[c_num]["has_mosaic_file"] = True

                    # Purge stale/auto_compile jobs from mosaic_runs (4 hours / 14400s max)
                    now = time.time()
                    stale_keys = [
                        k for k, v in list(mosaic_runs.items()) 
                        if v.get("run_id") == "auto_compile" or not v.get("start_time") or (now - v.get("start_time", 0) > 14400)
                    ]
                    for k in stale_keys:
                        del mosaic_runs[k]

                    # Scan active background jobs in mosaic_runs & disk jobs to override status to 'processing' or 'failed'
                    disk_jobs = load_mosaic_jobs(project_id)
                    for job_key, job in list(mosaic_runs.items()):
                        if job_key[0] == project_id:
                            disk_jobs[int(job_key[1])] = job

                    for c_num_raw, job in disk_jobs.items():
                        c_num_int = int(c_num_raw)
                        j_status = job.get("status")
                        j_prog = job.get("progress", 0)
                        j_err = job.get("error")
                        
                        if c_num_int not in clip_statuses:
                            clip_statuses[c_num_int] = {"has_audio": False, "video_state": "none", "has_mosaic_file": False}
                        
                        if j_status == "completed":
                            clip_statuses[c_num_int]["mosaic_state"] = "completed"
                            clip_statuses[c_num_int]["mosaic_progress"] = 100
                            clip_statuses[c_num_int]["mosaic_status"] = "completed"
                        elif j_status == "failed":
                            clip_statuses[c_num_int]["mosaic_state"] = "failed"
                            clip_statuses[c_num_int]["mosaic_error"] = j_err or "Mosaic render failed"
                            clip_statuses[c_num_int]["mosaic_progress"] = 0
                            clip_statuses[c_num_int]["mosaic_status"] = "failed"
                        elif j_status:
                            # Any active in-progress state (starting, muxing draft body, uploading, rendering, downloading)
                            clip_statuses[c_num_int]["mosaic_state"] = "processing"
                            clip_statuses[c_num_int]["mosaic_progress"] = j_prog
                            clip_statuses[c_num_int]["mosaic_status"] = j_status
                            clip_statuses[c_num_int]["has_mosaic_file"] = False
                                
                ingestion_progress = None
                progress_file = os.path.join(project_dir, "ingestion_progress.json")
                if os.path.exists(progress_file):
                    try:
                        with open(progress_file, "r", encoding="utf-8") as pf:
                            ingestion_progress = json.load(pf)
                    except Exception:
                        pass

                payload = {
                    "info": info,
                    "plan": plan_data,
                    "transcription": trans_data,
                    "has_snapshot": has_snapshot,
                    "compiled_videos": compiled_videos,
                    "clip_statuses": clip_statuses,
                    "ingestion_progress": ingestion_progress
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, str(e))
                return

        elif parsed_url.path == '/get-ingestion-progress':
            project_id = params.get('id', [None])[0]
            try:
                if not project_id:
                    raise Exception("Missing project id.")
                project_dir = os.path.join("projects", project_id)
                progress_file = os.path.join(project_dir, "ingestion_progress.json")
                data = {"status": "none", "percent": 0}
                if os.path.exists(progress_file):
                    with open(progress_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, str(e))
                return
                
        elif parsed_url.path == '/list-music':
            music_dir = "music"
            files = []
            if os.path.exists(music_dir):
                files = sorted([f for f in os.listdir(music_dir) if f.lower().endswith((".mp3", ".wav", ".m4a"))])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(files).encode('utf-8'))
            return
            
        elif parsed_url.path == '/get-clip-archetypes':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                if os.getcwd() not in sys.path:
                    sys.path.insert(0, os.getcwd())
                import importlib
                import archetype_studio
                importlib.reload(archetype_studio)

                plan_path = os.path.join("projects", project_id, "plan.json")
                if not os.path.exists(plan_path):
                    plan_path = "plan.json"
                t_clip = None
                if os.path.exists(plan_path):
                    with open(plan_path, "r", encoding="utf-8") as pf:
                        plan_data = json.load(pf)
                    t_clip = next((c for c in plan_data if str(c.get("num")) == str(clip_num)), None)

                body_dur = float(t_clip.get("audio_duration") or t_clip.get("duration") or 120.0) if t_clip else 120.0
                meta_obj = archetype_studio.ensure_clip_meta(int(clip_num), plan_clip=t_clip, body_duration=body_dur)

                ep_num = project_id.replace('episode_', '')
                short_mp4 = os.path.join("clips", f"{ep_num}-{clip_num}-manim.mp4")
                if not os.path.exists(short_mp4):
                    short_mp4 = os.path.join("clips", f"{ep_num}-{clip_num}.mp4")
                video_url = f"/clips/{os.path.basename(short_mp4)}" if os.path.exists(short_mp4) else None

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "meta": meta_obj,
                    "has_compiled_short": os.path.exists(short_mp4),
                    "video_url": video_url
                }).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/get-storyboard':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            force_regen = params.get('force', ['false'])[0].lower() in ('true', '1')
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                sb = generate_or_load_storyboard_data(project_id, clip_num, force_regen=force_regen)
                filepath = get_storyboard_filepath(project_id, clip_num)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "storyboard": sb,
                    "filepath": filepath,
                    "filename": os.path.basename(filepath)
                }).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        elif parsed_url.path == '/get-settings':
            try:
                settings_path = "settings.json"
                settings_data = {}
                if os.path.exists(settings_path):
                    with open(settings_path, "r", encoding="utf-8") as f:
                        settings_data = json.load(f)
                else:
                    settings_data = {
                        "theme": "midnight",
                        "export_format": "audio",
                        "resolution": "1080x1080",
                        "bg_color": "black"
                    }
                def_mosaic = get_mosaic_default_prompt()
                settings_data["default_mosaic_prompt"] = def_mosaic
                # Shipped factory fallback -- Reset uses this, never the stored value.
                settings_data["factory_mosaic_prompt"] = get_factory_mosaic_prompt()
                if not settings_data.get("mosaic_default_prompt"):
                    settings_data["mosaic_default_prompt"] = def_mosaic
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(settings_data).encode('utf-8'))
                return
            except Exception as e:
                self.send_error(500, str(e))
                return
                
        elif parsed_url.path == '/get-mosaic-status':
            project_id = params.get('id', [None])[0]
            clip_num = params.get('num', [None])[0]
            try:
                if not project_id or clip_num is None or str(clip_num).strip() == "":
                    raise Exception("Missing project id or clip number.")
                
                job_key = (project_id, int(clip_num))
                job = mosaic_runs.get(job_key)
                
                if not job:
                    # Self-healing check: check if a run was already registered in plan.json
                    project_dir = os.path.join("projects", project_id)
                    plan_path = os.path.join(project_dir, "plan.json")
                    mosaic_run_id = None
                    target_clip = None
                    if os.path.exists(plan_path):
                        try:
                            with open(plan_path, "r", encoding="utf-8") as f:
                                plan = json.load(f)
                            for c in plan:
                                if int(c.get("num", -1)) == int(clip_num):
                                    mosaic_run_id = c.get("mosaic_run_id")
                                    target_clip = c
                                    break
                        except Exception as pe:
                            print(f"Warning: Failed to parse plan.json for run recovery: {pe}")
                    
                    if mosaic_run_id:
                        # Pure read: report stored state, never start a pipeline.
                        # A Mosaic run starts ONLY via the manual Mosaic button
                        # (/export-to-mosaic). Resumability is preserved: the
                        # stored run_id is returned so the UI can offer resume.
                        stored = None
                        try:
                            stored = (load_mosaic_jobs(project_id) or {}).get(int(clip_num))
                        except Exception:
                            stored = None
                        if stored:
                            job = {"status": stored.get("status", "idle"), "progress": stored.get("progress", 0), "error": stored.get("error"), "run_id": mosaic_run_id}
                        else:
                            job = {"status": "idle", "progress": 0, "error": None, "run_id": mosaic_run_id}
                    else:
                        job = {"status": "idle", "progress": 0, "error": None}
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(job).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return
                
        elif parsed_url.path == '/project-audio':
            project_id = params.get('id', [None])[0]
            audio_file = None
            if project_id:
                project_dir = os.path.join("projects", project_id)
                if os.path.exists(project_dir):
                    for f in os.listdir(project_dir):
                        if f.startswith("audio."):
                            audio_file = os.path.join(project_dir, f)
                            break
            
            if audio_file and os.path.exists(audio_file):
                self.path = "/" + audio_file.replace("\\", "/")
                return super().do_GET()
            else:
                self.send_error(404, "Audio file not found for project.")
                return

        return super().do_GET()

    def end_headers(self):
        if self.path.endswith('.html') or self.path.endswith('.js') or 'curator' in self.path:
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def translate_path(self, path):
        translated = super().translate_path(path)
        clean_path = path.split('?')[0]
        if not os.path.exists(translated):
            if clean_path.startswith("/docs/"):
                src_docs_target = os.path.abspath(os.path.join(os.getcwd(), "..", "src", "ddma", clean_path.lstrip("/")))
                if os.path.exists(src_docs_target):
                    return src_docs_target
            elif clean_path.startswith("/episodes/"):
                src_docs_target = os.path.abspath(os.path.join(os.getcwd(), "..", "src", "ddma", "docs", clean_path.lstrip("/")))
                if os.path.exists(src_docs_target):
                    return src_docs_target
        if not os.path.exists(translated) and clean_path.startswith("/media/"):
            parent_media = os.path.abspath(os.path.join(os.getcwd(), "..", clean_path.lstrip("/")))
            if os.path.exists(parent_media):
                return parent_media
        if not os.path.exists(translated) and "/clips/" in clean_path:
            # Fallback 1: Strip 'episode_' prefix (e.g. /clips/episode_245-1.mp4 -> /clips/245-1.mp4)
            if "/clips/episode_" in clean_path:
                alt_clean = clean_path.replace("/clips/episode_", "/clips/")
                alt_trans = super().translate_path(alt_clean)
                if os.path.exists(alt_trans):
                    return alt_trans
            # Fallback 2: Check for any matching file in clips directory (e.g. 245-1-Title.mp4)
            clips_dir = "clips"
            if os.path.exists(clips_dir):
                base_name = os.path.basename(clean_path)
                import re
                ep_match = re.search(r'(\d+)-(\d+)', base_name)
                if ep_match:
                    ep_n = ep_match.group(1)
                    c_n = ep_match.group(2)
                    for f in os.listdir(clips_dir):
                        if f.startswith(f"{ep_n}-{c_n}.") or f.startswith(f"{ep_n}-{c_n}-"):
                            if f.endswith(".mp4") and not f.endswith("-original.mp4"):
                                return os.path.join(os.getcwd(), clips_dir, f)
        return translated

    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path) or os.path.isdir(path):
            return super().send_head()
            
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, "File not found")
            return None
            
        range_header = self.headers.get('Range')
        if not range_header:
            return super().send_head()
            
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if not match:
            self.send_error(400, "Bad Request (invalid range)")
            f.close()
            return None
            
        size = os.path.getsize(path)
        start = int(match.group(1))
        end = match.group(2)
        end = int(end) if end else size - 1
        
        if start >= size or end >= size or start > end:
            self.send_error(416, "Requested Range Not Satisfiable")
            self.send_header('Content-Range', f'bytes */{size}')
            self.end_headers()
            f.close()
            return None
            
        self.send_response(206)
        self.send_header('Content-type', ctype)
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Last-Modified', self.date_time_string(os.path.getmtime(path)))
        self.end_headers()
        
        f.seek(start)
        return f

    def copyfile(self, source, outputfile):
        range_header = self.headers.get('Range')
        if not range_header or self.path.endswith('.html') or self.path.endswith('.json'):
            super().copyfile(source, outputfile)
            return

        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if not match:
            super().copyfile(source, outputfile)
            return

        clean_path = self.path.split('?')[0]
        size = os.path.getsize(self.translate_path(clean_path))
        start = int(match.group(1))
        end = match.group(2)
        end = int(end) if end else size - 1

        length = end - start + 1
        buffer_size = 256 * 1024
        while length > 0:
            chunk = source.read(min(buffer_size, length))
            if not chunk:
                break
            try:
                outputfile.write(chunk)
            except (ConnectionResetError, BrokenPipeError):
                break
            length -= len(chunk)

    def log_message(self, format, *args):
        pass

def start_server():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    host = os.environ.get("CURATOR_HOST", "127.0.0.1")
    try:
        with socketserver.ThreadingTCPServer((host, PORT), RangeHTTPRequestHandler) as httpd:
            print(f"Server started on http://{host}:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")

def main():
    print("==================================================")
    print("      DDMA Clip Curator Launcher v2.0 (Multi-Proj)")
    print("==================================================")
    
    # Run legacy data migration to avoid losing 244 progress
    migrate_legacy_files()
    
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    time.sleep(0.5)
    
    host = os.environ.get("CURATOR_HOST", "127.0.0.1")
    url = f"http://{host}:{PORT}/curator.html"
    print(f"Opening browser at: {url}")
    
    if not os.environ.get("HEADLESS"):
        webbrowser.open(url)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down curator server. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
