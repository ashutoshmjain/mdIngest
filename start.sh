#!/bin/bash
# Start the mdIngest + DDMA stack (Linux / WSL).
# Mounts the Google Drive workspace with rclone (if not already mounted),
# then starts the Cockpit, Curator, and mdbook servers in the background.
#
# Usage: ./start.sh
#   - Set DD_HUB_ROOT to the workspace path (default: /mnt/gdrive/workspace).
#   - If the workspace is not yet mounted, set DD_HUB_FOLDER_ID to the
#     Google Drive folder ID so rclone can mount it.
#   - Python: uses a virtual environment if one exists (.venv in this repo
#     or ../.venv), otherwise the system python3.

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${DD_HUB_ROOT:-/mnt/gdrive/workspace}"
FOLDER_ID="${DD_HUB_FOLDER_ID:-}"

# The ddma repo must sit next to this repo (the 1-Prompt Setup clones both
# side by side). Fail early with a clear message if it is missing.
if [ ! -d "$REPO_ROOT/../ddma" ]; then
  echo "ERROR: ddma repo not found at $REPO_ROOT/../ddma. Clone it next to mdIngest, then run ./start.sh again."
  exit 1
fi

# 1. Mount the Drive workspace if it isn't already mounted.
if mountpoint -q "$WORKSPACE" 2>/dev/null; then
  echo "Workspace already mounted at $WORKSPACE"
elif [ -n "$FOLDER_ID" ]; then
  echo "Mounting Google Drive workspace..."
  rclone mount gdrive: "$WORKSPACE" --drive-root-folder-id "$FOLDER_ID" --vfs-cache-mode full --daemon
  for i in $(seq 1 10); do
    if mountpoint -q "$WORKSPACE" 2>/dev/null; then
      echo "Mounted at $WORKSPACE"
      break
    fi
    sleep 1
  done
  if ! mountpoint -q "$WORKSPACE" 2>/dev/null; then
    echo "ERROR: mount did not come up. Run 'rclone config' and check the gdrive remote, then try again."
    exit 1
  fi
else
  echo "Workspace at $WORKSPACE is not mounted and DD_HUB_FOLDER_ID is not set."
  echo "Mount it first (rclone mount) or set DD_HUB_FOLDER_ID to the Drive folder ID, then run ./start.sh again."
  exit 1
fi

export DD_HUB_ROOT="$WORKSPACE"

# 2. Pick a Python (venv preferred, system python3 as fallback).
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PY="$REPO_ROOT/.venv/bin/python"
elif [ -x "$REPO_ROOT/../.venv/bin/python" ]; then
  PY="$REPO_ROOT/../.venv/bin/python"
else
  PY="python3"
fi
echo "Using Python: $PY"

# 3. Start the servers in the background (logs go to ~/logs/).
mkdir -p ~/logs
cd "$REPO_ROOT" && DD_HUB_ROOT="$WORKSPACE" nohup "$PY" ui/server.py > ~/logs/cockpit.log 2>&1 &
cd "$REPO_ROOT/../ddma" && DD_HUB_ROOT="$WORKSPACE" nohup "$PY" scratch/run_curator.py > ~/logs/curator.log 2>&1 &
cd "$REPO_ROOT" && nohup mdbook serve --port 3000 > ~/logs/mdbook.log 2>&1 &

sleep 3
echo ""
echo "Servers starting:"
echo "  Cockpit:  http://localhost:8088/"
echo "  mdbook:   http://localhost:3000/"
echo "  Curator:  http://localhost:8000/curator.html"
echo "  Beats:    launch from the landing page (http://localhost:8088/ -> Launch Beats Studio)"
echo "Logs: ~/logs/cockpit.log, ~/logs/curator.log, ~/logs/mdbook.log"
