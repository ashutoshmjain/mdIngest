# mdIngest

mdIngest is a pipe that connects your research and conversations into published episodes. It is not a one-click-and-done app — it is an interface that lets you finesse raw research into a polished web page, or a raw conversation into a podcast-quality stream.

It runs locally on your machine — Linux, Windows, or Mac — as a web app on localhost. No login, no paywall, fully open source.

Here's what you do with it, and what you get out of it:

- **You bring raw research → you finesse it into a polished web page.** The Cockpit (http://localhost:8088/cockpit.html) is where you shape your drafts and episodes and publish them as an article on the site.
- **You bring a raw conversation (audio) → you finesse it into a podcast-quality stream.** It gets transcribed once, at the word level, and that one transcription drives everything — the article, the clips, the longform. Nothing ever re-transcribes it.
- **You start at the landing page (http://localhost:8088/)** — the drop point for new inputs and the launcher for the Cockpit, DDMA, and Beats Studio.

DDMA is the extension (Clip Studio + Beats Studio — clips and longform video). It is installed by the same 1-Prompt Setup below; see the [ddma repo](https://github.com/ashutoshmjain/ddma) for what it does.

## Installation — 1-Prompt Setup

Copy and paste this prompt into Antigravity, Muse Code, or Claude to set up the complete publishing environment (mdIngest + DDMA). Do every step in order. If a step fails, fix it and continue — do not stop and ask unless a step explicitly says to ask.

```text
Please set up and verify the complete publishing environment (mdIngest + DDMA) in this workspace. Do every step below in order. Do not skip a step. If a step fails, fix it and continue — do not stop and ask unless a step explicitly says to ask.

1. Verify the toolchain: Python 3.10+, Cargo/Rust, mdbook (v0.5.0+), and mdbook-katex are installed and available on PATH. If mdbook or mdbook-katex are missing, install them via `cargo install mdbook mdbook-katex`.
2. Install the Python packages for mdIngest: from the mdIngest repo root, run `pip install -r ui/requirements.txt` (faster-whisper, av, openai-whisper, numpy — required for transcription; the server starts without them but transcription fails).
3. Install the Python packages for DDMA: from the ddma repo root, run `pip install -r requirements.txt` (faster-whisper, av, manim, google-generativeai, pyyaml, and the rest).
4. Verify ffmpeg is installed and on PATH (`ffmpeg -version`). If it is missing, install it (Windows: `winget install ffmpeg` or `choco install ffmpeg`; macOS: `brew install ffmpeg`; Linux: `sudo apt install ffmpeg` or the distro equivalent). The pipeline cannot compile audio or video without ffmpeg.
5. Build the md-publish preprocessor binary from the mdIngest repo root using `cargo build --release` (the manifest is the repo-root `Cargo.toml`; the binary source is `crate/src/main.rs` — do NOT run the build inside `crate/`, there is no manifest there).
6. Verify the built binary exists at `target/release/md-publish`. Do NOT require `[preprocessor.katex]` or `[preprocessor.ingest]` blocks in the repo-root `book.toml` — that file intentionally has no preprocessors enabled (for manual-build stability); the preprocessor is wired in at publish time.
7. Set up the workspace folder. The user creates an empty folder on Google Drive to be the workspace (ask the user for the folder, or use the folder ID from its Drive URL `https://drive.google.com/drive/folders/<FOLDER_ID>`). Then mount it as a local path — the code only does local file I/O against a local path, never the Google Drive web API:
   - On Windows or macOS: use Google Drive for Desktop. Install it and sign in if it is not already installed. The mount appears at `G:\My Drive\` on Windows, or `~/Library/CloudStorage/GoogleDrive-<email>/My Drive` on macOS. Do NOT use rclone on Windows or macOS.
   - On Linux or WSL: use rclone (Google offers no Drive client for Linux). Install rclone, run `rclone config` to create a Drive remote named `gdrive` (complete the browser sign-in), then mount only the workspace folder by its ID: `rclone mount gdrive: /mnt/gdrive/workspace --drive-root-folder-id <FOLDER_ID> --vfs-cache-mode full --daemon`. On WSL, prefer this native Linux mount over `/mnt/g` (the Windows Drive mount is slow through the WSL bridge, especially for ffmpeg); use `/mnt/g/My Drive/<folder>` only as a fallback if the rclone mount is not possible. If `rclone mount` is not possible at all (no FUSE), use `rclone copy` instead: keep a plain local folder, set the workspace path to it, and copy files to/from Drive with `rclone copy` (pull before working, push after).
   - In Docker or a VM: use rclone as on Linux (there is no desktop app in a container).
   - Create the folder structure inside the mounted workspace folder if any are missing: `episodes/`, `vault/`, `inputs/`, `audio/`, `video/`, `mosaics/`, `manims/`, `rules/`.
   - Set the `DD_HUB_ROOT` environment variable to the mounted workspace path and persist it (shell profile, systemd unit, or Docker entrypoint) so it survives new shells.
8. Set up settings: create `<workspace>/vault/settings.json` from `settings.template.json` (in the mdIngest repo root) if it does not exist. Fill in API keys only if the user provides them; never commit settings.json. If the user already has a settings.json in an existing workspace folder, copy that file into the new workspace folder's `vault/` instead of creating one from the template.
9. Launch the mdIngest Publishing Cockpit server (`python ui/server.py` from the mdIngest repo, or `./start_ui.bat` on Windows) on http://localhost:8088 and verify that http://localhost:3000 is accessible via `mdbook serve`.
10. Launch the DDMA Clip Studio (Curator) server: from the ddma repo root, run `python scratch/run_curator.py` and verify http://localhost:8000/curator.html loads.
11. Launch Beats Studio from the mdIngest landing page (http://localhost:8088/, the "Launch Beats Studio" button) and verify http://localhost:8001 responds.
12. Verify: `DD_HUB_ROOT` resolves, the workspace folder structure exists, `episodes/<N>/plan.json` is readable for an existing episode (or the workspace folder is empty for a fresh workspace), and all three servers respond (cockpit :8088, Curator :8000, Beats :8001).
```

After setup, launch with `python ui/server.py` (or `start_ui.bat` on Windows). The landing page is at http://localhost:8088/.

## State of the app — alpha test phase

mdIngest is in alpha. It works end to end — see [episode 249: What Exactly is Reality?](https://deepdive.shutri.com/249.html) and [episode 250: What Exactly is Infinity?](https://deepdive.shutri.com/250.html) ([Spotify](https://open.spotify.com/episode/1sUNnANbczGUpY8os0i03z)) — but it is still being hardened and tested. Expect rough edges. Bugs are tracked in the [Bug Tracker Space](https://muse.ai/s/bug-tracker-ixe6daxhoezyxy/g1O341vEl5aXYIzWFP1db5l-xunGJAxBRSwSJccC110), not on GitHub Issues.

Licensed under the [MIT License](LICENSE).