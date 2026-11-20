# mdIngest

mdIngest is a pipe that connects your research and conversations into published episodes. It is not a one-click-and-done app — it is an interface that lets you finesse raw research into a polished web page, or a raw conversation into a podcast-quality stream.

It runs locally on your machine — Linux, Windows, or Mac — as a web app on localhost. No login, no paywall, fully open source.

Here's what you do with it, and what you get out of it:

- **You start at the landing page** — the drop point for new inputs and the launcher for the Cockpit, Cutroom, and Beats Studio.
- **You bring raw research → you finesse it into a polished web page.** The Cockpit is where you shape your drafts and episodes and publish them as an article on the site.
- **You bring a raw conversation (audio) → you finesse it into a podcast-quality stream.** It gets transcribed once, at the word level, and that one transcription drives everything — the article, the clips, the longform. Nothing ever re-transcribes it.

Cutroom is the extension inside this repo (the `ddma/` folder: Curator/Clip Studio + Beats Studio — clips and longform video). It comes with the clone below and is started by the same setup — no second repo to fork.

## Minimum configuration

- **OS:** Windows 10/11, macOS 12+, or Ubuntu 20.04+ (or any modern Linux).
- **CPU:** Quad-core (Intel Core i5 8th Gen+ / AMD Ryzen 5 3000+ / Apple Silicon M1+). Whisper runs on 8 threads.
- **RAM:** 8 GB minimum, 16 GB recommended.
- **Disk:** 10 GB free (Python packages, the ~1.6 GB Whisper model, ffmpeg, and your media).
- **GPU:** Optional. An NVIDIA GPU with CUDA speeds up transcription; without one it runs on CPU.

## Installation — 1-Prompt Setup

Copy and paste this prompt into Antigravity, Muse Code, or Claude to set up the complete publishing environment (mdIngest + Cutroom). Do every step in order. If a step fails, fix it and continue — do not stop and ask unless a step explicitly says to ask.

```text
Please set up and verify the complete publishing environment (mdIngest) in this workspace. Do every step below in order. Do not skip a step. If a step fails, fix it and continue — do not stop and ask unless a step explicitly says to ask.

Use the Python virtual environment at `.venv` in the repo root for every Python command below. If a step needs sudo (only a Linux package install can), do not run sudo yourself: open a new terminal, ask the user to authenticate there, and run the install command in that terminal.

1. Verify the toolchain: Python 3.10+, Cargo/Rust, mdbook (v0.5.0+), mdbook-katex, and the GitHub CLI (`gh`) are installed and on PATH, and `gh auth status` shows an authenticated account. If mdbook or mdbook-katex are missing, install them via `cargo install mdbook mdbook-katex`. If `gh` is missing or unauthenticated, ask the user to install it and sign in before continuing.
2. Fork mdIngest and clone your fork into this workspace: `gh repo fork ashutoshmjain/mdIngest --clone`, then `cd mdIngest`. All paths below are relative to the repo root, and every command below runs from there.
3. Create the virtual environment if it does not exist (`python3 -m venv .venv` — on Windows: `py -3 -m venv .venv`), activate it, and install the Python packages from the repo root: `pip install -r requirements.txt`. This one list covers the cockpit server, transcription, Cutroom, and Manim. (On Debian/Ubuntu, if venv creation fails because the venv package is missing, install it using the sudo-terminal pattern above.)
4. Verify ffmpeg is installed and on PATH (`ffmpeg -version`). If it is missing, install it (Windows: `winget install ffmpeg` or `choco install ffmpeg`; macOS: `brew install ffmpeg`; Linux: `apt install ffmpeg` or the distro equivalent, using the sudo-terminal pattern). The pipeline cannot compile audio or video without ffmpeg.
5. Build the md-publish preprocessor binary from the repo root using `cargo build --release` (the manifest is the repo-root `Cargo.toml`; the binary source is `crate/src/main.rs` — do NOT run the build inside `crate/`, there is no manifest there).
6. Verify the built binary exists at `target/release/md-publish`. The book infrastructure ships configured in the repo-root `book.toml` (full katex + ingest preprocessor sections, theme) — do NOT run `mdbook init` in this repo: it overwrites `book.toml` with a minimal stub and wipes that configuration. If it happens, recover with `git checkout -- book.toml`.
7. Set up the workspace folder. Ask the user for a path to a local folder to be the workspace — call it the dd root hub (`DD_HUB_ROOT`). This is where all episodes, audio, plans, and settings live. Create the folder if it does not exist, then create the folder structure inside it if any are missing: `episodes/`, `vault/`, `inputs/`, `audio/`, `video/`, `mosaics/`, `manims/`, `rules/`. Set the `DD_HUB_ROOT` environment variable to that path and persist it (shell profile, systemd unit, or Docker entrypoint) so it survives new shells. The app only does local file I/O against this path. If the user wants the workspace backed up and shared across machines, they can sync this folder with Google Drive (Drive for Desktop on Windows/Mac; rclone on Linux/WSL/Docker) or any other sync tool they prefer — that choice is theirs, and the app does not need it to run.
8. Settings: if the user already has a `settings.json` in an existing workspace folder, copy that file into the new workspace folder's `vault/` instead of creating one. Otherwise skip settings entirely — the user adds API keys later, inside the app, once they know what each key unlocks (the landing page explains them). Never commit settings.json.
9. Launch the mdIngest Publishing Cockpit server (`python ingest/server.py` from the repo root, using the venv) on http://localhost:8088. In a second terminal, from the repo root, start the book preview — `mdbook serve --hostname 0.0.0.0 -p 3000` — and verify http://localhost:3000 responds.
10. Launch the Cutroom Clip Studio (Curator) server: from the repo-root `ddma/` folder, run `python scratch/run_curator.py` using the venv, and verify http://localhost:8000/curator.html loads.
11. Launch Beats Studio from the mdIngest landing page (http://localhost:8088/, the "Launch Beats Studio" button) and verify http://localhost:8001 responds.
12. Verify: `DD_HUB_ROOT` resolves, the workspace folder structure exists, `episodes/<N>/plan.json` is readable for an existing episode (or the workspace folder is empty for a fresh workspace), and all four servers respond (cockpit :8088, book preview :3000, Curator :8000, Beats :8001).
```

After setup, launch with `python ingest/server.py` (or `start_ui.bat` on Windows, or `./start.sh` on Linux/WSL — it mounts the Drive workspace if needed and starts all four servers). The landing page is at http://localhost:8088/.

## State of the app — alpha test phase

mdIngest is in alpha. It works end to end — see [episode 249: What Exactly is Reality?](https://deepdive.shutri.com/249.html) and [episode 250: What Exactly is Infinity?](https://deepdive.shutri.com/250.html) ([Spotify](https://open.spotify.com/episode/1sUNnANbczGUpY8os0i03z)) — but it is still being hardened and tested. Expect rough edges. Bugs are tracked in the [Bug Tracker Space](https://muse.ai/s/bug-tracker-ixe6daxhoezyxy/g1O341vEl5aXYIzWFP1db5l-xunGJAxBRSwSJccC110), not on GitHub Issues.

Licensed under the [MIT License](LICENSE).
