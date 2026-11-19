import os
import sys
import re
import json
import time
import requests
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_ROOT = os.path.dirname(SCRIPT_DIR)
SETTINGS_PATH = os.path.join(SCRIPT_DIR, "settings.json")
BASE_URL = "https://api.mosaic.so"

def get_ep_num():
    for i, arg in enumerate(sys.argv):
        if arg in ("--ep", "-e") and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return "249"

EP_NUM = get_ep_num()
PROJECT_DIR = os.path.join(SCRIPT_DIR, "projects", f"episode_{EP_NUM}")
PLAN_PATH = os.path.join(PROJECT_DIR, "plan.json")
DOCS_PLAN_PATH = os.path.join(GITHUB_ROOT, "src", "ddma", "docs", "episodes", EP_NUM, "plan.json")
CLIPS_DIR = os.path.join(SCRIPT_DIR, "clips")
os.makedirs(CLIPS_DIR, exist_ok=True)

settings = {}
if os.path.exists(SETTINGS_PATH):
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except Exception as e:
        print(f"[WARNING] Failed reading settings.json: {e}", file=sys.stderr)
else:
    print(
        f"[NOTICE] settings.json not found at {SETTINGS_PATH}. "
        "Required keys (or env vars): mosaic_api_key (MOSAIC_API_KEY), mosaic_agent_id (MOSAIC_AGENT_ID), "
        "mosaic_mogr_node_id (MOSAIC_MOGR_NODE_ID), mosaic_captions_node_id (MOSAIC_CAPTIONS_NODE_ID).",
        file=sys.stderr
    )

def resolve_hub_root():
    """Workspace root, same semantics as the Curator resolver: env DD_HUB_ROOT
    -> settings.json dd_hub_root -> plain local <repo>/dd_hub default (loud)."""
    e = os.environ.get("DD_HUB_ROOT")
    if e and os.path.exists(e):
        return e
    cfg = settings.get("dd_hub_root") if isinstance(settings, dict) else None
    if cfg and os.path.exists(cfg):
        return cfg
    local_default = os.path.join(GITHUB_ROOT, "dd_hub")
    print(f"WARNING: DD_HUB_ROOT is unset and no dd_hub directory exists at any known location -- defaulting to plain local folder {local_default} (set DD_HUB_ROOT to your workspace to override).")
    return local_default

HUB_PLAN_PATH = os.path.join(resolve_hub_root(), "episodes", EP_NUM, "plan.json")

API_KEY = settings.get("mosaic_api_key") or os.environ.get("MOSAIC_API_KEY", "")
AGENT_ID = settings.get("mosaic_agent_id") or os.environ.get("MOSAIC_AGENT_ID", "")
MOGR_NODE_ID = settings.get("mosaic_mogr_node_id") or os.environ.get("MOSAIC_MOGR_NODE_ID", "")
CAPTIONS_NODE_ID = settings.get("mosaic_captions_node_id") or os.environ.get("MOSAIC_CAPTIONS_NODE_ID", "")

HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

def load_clip(clip_num):
    # Workspace first, then the repo's published copy. Both are repo-layout
    # independent; the plan's canonical home is the workspace.
    target_plan = None
    for cand in [HUB_PLAN_PATH, DOCS_PLAN_PATH]:
        if os.path.exists(cand):
            target_plan = cand
            break
    if not target_plan:
        print(f"Error: plan for episode {EP_NUM} not found in workspace or published copy.")
        return None, None, None
    with open(target_plan, "r", encoding="utf-8") as f:
        plan = json.load(f)
    for c in plan:
        if int(c.get("num", -1)) == int(clip_num):
            return c, plan, target_plan
    return None, None, None

def save_run_id(clip_num, run_id):
    # Hub primary first, then the local working copy and the published copy.
    for p_path in [HUB_PLAN_PATH, PLAN_PATH, DOCS_PLAN_PATH]:
        if os.path.exists(p_path):
            try:
                with open(p_path, "r", encoding="utf-8") as f:
                    plan = json.load(f)
                for c in plan:
                    if int(c.get("num", -1)) == int(clip_num):
                        c["mosaic_run_id"] = run_id
                        break
                with open(p_path, "w", encoding="utf-8") as f:
                    json.dump(plan, f, indent=4)
                print(f"Saved mosaic_run_id {run_id} to {p_path}")
            except Exception as e:
                print(f"Warning saving to {p_path}: {e}")

def initiate_mosaic_run(clip_num, force=False):
    clip, plan, plan_file = load_clip(clip_num)
    if not clip:
        print(f"Error: Clip {clip_num} not found in plan.")
        sys.exit(1)

    existing_run_id = clip.get("mosaic_run_id")
    if existing_run_id and not force:
        print(f"Clip {clip_num} already has active mosaic_run_id: {existing_run_id}")
        check_status(clip_num)
        return existing_run_id

    file_path = os.path.join(CLIPS_DIR, f"{EP_NUM}-{clip_num}.mp4")
    if not os.path.exists(file_path):
        print(f"Draft video {file_path} not found. Running ddma.py mux-clip...")
        env = dict(os.environ)
        env["PATH"] = f"/home/antigravity/.local/bin:{env.get('PATH', '')}"
        res = subprocess.run([
            sys.executable, "ddma.py", "mux-clip",
            "--num", str(clip_num),
            "--plan-file", plan_file,
            "--out-dir", CLIPS_DIR
        ], cwd=SCRIPT_DIR, env=env, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error muxing draft video: {res.stderr}")
            sys.exit(1)
        print(f"Created draft video: {file_path}")

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"\n[Clip {clip_num}] Preparing Mosaic upload ({file_path}, {file_size_mb:.2f} MB)...")

    # 1. Request upload URL
    res = requests.post(f"{BASE_URL}/uploads/video/get_upload_url", headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"Mosaic get_upload_url failed ({res.status_code}): {res.text}")
    up_data = res.json()
    upload_url = up_data["upload_url"]
    upload_fields = up_data.get("upload_fields", {})
    video_id = up_data["video_id"]
    print(f"[Clip {clip_num}] Upload URL received. Video ID: {video_id}")

    # 2. Upload file to S3
    print(f"[Clip {clip_num}] Uploading {file_path} to Mosaic S3...")
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "video/mp4")}
        res_s3 = requests.post(upload_url, data=upload_fields, files=files)
    if res_s3.status_code not in (200, 201, 204):
        raise Exception(f"S3 upload failed ({res_s3.status_code}): {res_s3.text}")
    print(f"[Clip {clip_num}] S3 upload successful.")

    # 3. Finalize upload
    print(f"[Clip {clip_num}] Finalizing upload...")
    res_fin = requests.post(f"{BASE_URL}/uploads/video/finalize_upload", headers=HEADERS, json={"video_id": video_id})
    if res_fin.status_code != 200:
        raise Exception(f"Mosaic finalize_upload failed ({res_fin.status_code}): {res_fin.text}")
    print(f"[Clip {clip_num}] Upload finalized.")

    # 4. Build prompt
    title = clip.get("title", f"Clip {clip_num}")
    raw_segment_texts = [s.get("text", "").strip() for s in clip.get("segments", []) if s.get("type") == "audio" and s.get("text")]
    transcript = " ".join(raw_segment_texts) or clip.get("text", "")
    base_prompt = settings.get("mosaic_prompt_with_captions_backup") or settings.get("mosaic_default_prompt", "")
    full_prompt = (
        f"{base_prompt}\n\n"
        "--------------------------------------------------\n"
        "DYNAMIC CLIP CONTEXT\n"
        "--------------------------------------------------\n"
        f"- Visual Theme / Topic: {title}\n"
        f"- Spoken Dialogue Audio Context: {transcript}"
    )

    update_params = {}
    if MOGR_NODE_ID:
        update_params[MOGR_NODE_ID] = {
            "prompt": full_prompt,
            "model_tier": "pro",
            "style_video_url": "https://www.youtube.com/shorts/xybpfL1GnEQ",
            "frequency_per_minute": "auto",
            "reference_links": "",
            "only_generate_full_screen_graphics": True
        }

    run_body = {"video_ids": [video_id]}
    if update_params:
        run_body["update_params"] = update_params

    # 5. Trigger run
    print(f"[Clip {clip_num}] Triggering Mosaic Agent run (Agent ID: {AGENT_ID})...")
    res_run = requests.post(f"{BASE_URL}/agent/{AGENT_ID}/run", headers=HEADERS, json=run_body)
    if res_run.status_code != 200:
        raise Exception(f"Failed to start agent run ({res_run.status_code}): {res_run.text}")
    run_id = res_run.json().get("run_id")
    if not run_id:
        raise Exception(f"No run_id returned: {res_run.text}")

    print(f"\n==================================================")
    print(f"   SUCCESS: Mosaic Run Triggered for Clip {clip_num}!")
    print(f"   Run ID: {run_id}")
    print(f"==================================================")

    save_run_id(clip_num, run_id)
    return run_id

def check_status(clip_num):
    clip, _, _ = load_clip(clip_num)
    if not clip:
        print(f"Clip {clip_num} not found.")
        return None
    run_id = clip.get("mosaic_run_id")
    if not run_id:
        print(f"Clip {clip_num} has no active mosaic_run_id.")
        return None

    res = requests.get(f"{BASE_URL}/agent_run/{run_id}", headers=HEADERS)
    if res.status_code != 200:
        print(f"Error checking status for {run_id}: {res.status_code} {res.text}")
        return None
    data = res.json()
    status = data.get("status")
    print(f"[Clip {clip_num}][Run {run_id}] Status: {status}")
    if status == "completed":
        outputs = data.get("outputs", [])
        if outputs and outputs[0].get("video_url"):
            print(f"Output Video URL: {outputs[0]['video_url']}")
            return outputs[0]["video_url"]
    elif status in ("failed", "cancelled"):
        print(f"Error details: {data.get('status_message')} {data.get('errors')}")
    return status

def download_and_compile(clip_num):
    clip, _, plan_file = load_clip(clip_num)
    if not clip:
        print(f"Clip {clip_num} not found (no plan).")
        return
    run_id = clip.get("mosaic_run_id")
    if not run_id:
        print(f"Clip {clip_num} has no mosaic_run_id.")
        return

    res = requests.get(f"{BASE_URL}/agent_run/{run_id}", headers=HEADERS)
    if res.status_code != 200:
        print(f"Error checking status: {res.text}")
        return
    data = res.json()
    if data.get("status") != "completed":
        print(f"Run {run_id} is not completed yet (current status: {data.get('status')}).")
        return

    video_url = data["outputs"][0]["video_url"]
    mosaic_raw_file = os.path.join(CLIPS_DIR, f"{EP_NUM}-{clip_num}-mosaic-{run_id}.mp4")
    print(f"[Clip {clip_num}] Downloading rendered Mosaic video from {video_url}...")
    with requests.get(video_url, stream=True) as r:
        r.raise_for_status()
        with open(mosaic_raw_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192*16):
                f.write(chunk)
    print(f"Downloaded: {mosaic_raw_file} ({os.path.getsize(mosaic_raw_file)/(1024*1024):.2f} MB)")

    # Compile final clip with title intro & mux
    env = dict(os.environ)
    env["PATH"] = f"/home/antigravity/.local/bin:{env.get('PATH', '')}"
    cmd = [
        sys.executable, "ddma.py", "compile-clip",
        "--num", str(clip_num),
        "--plan-file", plan_file,
        "--source", "mosaic",
        "--out-dir", CLIPS_DIR
    ]
    print(f"Compiling final clip: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=SCRIPT_DIR, env=env, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(f"Error compiling clip: {res.stderr}")
        return

    final_clip = os.path.join(CLIPS_DIR, f"{EP_NUM}-{clip_num}.mp4")
    target_docs_clip = os.path.join(GITHUB_ROOT, "src", "ddma", "docs", "episodes", EP_NUM, "clips", f"{EP_NUM}-{clip_num}.mp4")
    if os.path.exists(final_clip):
        os.makedirs(os.path.dirname(target_docs_clip), exist_ok=True)
        import shutil
        shutil.copy2(final_clip, target_docs_clip)
        print(f"Delivered final clip to {target_docs_clip}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mosaic_runner.py [--initiate|--status|--download] <clip_num> [--force]")
        sys.exit(1)

    cmd = sys.argv[1]
    clip_n = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].isdigit() else "1"
    is_force = "--force" in sys.argv

    if cmd == "--initiate":
        initiate_mosaic_run(clip_n, force=is_force)
    elif cmd == "--status":
        check_status(clip_n)
    elif cmd == "--download":
        download_and_compile(clip_n)
    else:
        print(f"Unknown command {cmd}")
