# Ingest Cockpit Server

Local web UI and HTTP API server for episode ingestion, audio/clip review, and mdBook publication synchronization.

## What it serves

* `/` — the workspace landing page (the home page): workspace picker, launcher for mdIngest + Cutroom + Beats Studio, and the single drop point for new inputs (Python payload + base audio → `dd_hub/inputs/<episode>/`).
* `/cockpit.html` — the mdIngest Publishing Cockpit (3-pane workspace: ledger, preview, studio).

## Setup

```bash
pip install -r ../requirements.txt
python server.py
```

Runs by default on `http://localhost:8088`.

## Workspace (dd_hub)

This server reads from and writes to the dd_hub workspace (a Google Drive folder mounted as a local path via `DD_HUB_ROOT`). See **Setting up dd_hub** in the [mdIngest README](../README.md) for the full setup — the code only does local file I/O and never calls the Drive web API.

## Bug tracking

We do **not** manage issues on GitHub. Bugs are tracked in the [Bug Tracker Space](https://muse.ai/s/bug-tracker-ixe6daxhoezyxy/g1O341vEl5aXYIzWFP1db5l-xunGJAxBRSwSJccC110).
