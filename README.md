# md² (The mdd Engine & Publishing Cockpit)

> **md²** (pronounced *md-squared*) stands for **mdBook deepDive**. Much like `vim` is a recursion of `vi`, **md²** is a recursive evolution of the `mdbook` ecosystem, transformed into an opinionated, multi-modal publishing web application for the **Personal Knowledge Blockchain**.

---

![md² Ingest Publishing Cockpit UI](screenshot.png)

---

## The Philosophy: Personal Knowledge Blockchain

In the age of LLMs, the cost of generating information has collapsed to zero, but the cost of maintaining **Signal** has skyrocketed. Most research dies in transient chat windows. 

**md²** provides a formal framework to organize research into an immutable ledger of discovery:

* **Block 0 (The Genesis Block):** The hardcoded rules of your universe. It contains the **Six Foundational Pillars** (e.g., Bitcoin, Intelligence, Physics) that anchor all subsequent research.
* **Knowledge Blocks (Block 1, 2, ...):** Chronological epochs of discovery. Each block is limited by the **Law of 21**; once the 21st episodic transaction is mined, the block is sealed into the permanent chain.
* **The Mempool:** The volatile staging zone for unmined research drafts (`src/_<slug>.md`).
* **The Block Template:** The active mining epoch holding verified episodes awaiting block seal.

---

## The md² Publishing Cockpit (Web Application)

`mdIngest` includes a standalone, zero-dependency desktop web application styled in the **Shutri.com Minimalist Editorial design system** (`#fbf9f5` warm sand canvas, `#e7e5e4` stone borders, `#d97706` amber accents, and `#1c1917` ink typography).

### 1. 3-Pane Modular Workspace

* **Left Pane (Active Ledger Scope):**
  * **Mempool Drafts:** Visual list of active drafts (`src/_<slug>.md`) with live status indicators.
  * **Two-Way Inline Title Editor:** Hover `✏️` or double-click to edit summary titles with real-time 5-word limit badges. Auto-saves and synchronizes `SUMMARY.md` instantly.
  * **Draft Management:** 1-Click `🗑️` deletion for unmined drafts with automatic tree reconciliation.
  * **Block Template & Chain Archive:** Visual inspection of active epoch episodes and historical Genesis blocks.
  * **Collapsible & Expandable:** Toggle via edge tabs (`LEDGER` / `STUDIO`) or keyboard shortcuts (`[` and `]`).

* **Central Pane (Live Editorial Preview):**
  * **Absolute KaTeX Pipeline:** High-fidelity mathematical formula rendering ($\mathbb{R}, \mathbb{C}, \mathbb{H}, \mathbb{O}$, Dirac spinors, quaternions, and matrices) with delimiter hardening.
  * **Clean Paper Typography:** Seamless reading experience matching physical book aesthetics.
  * **Podcast Syndication Strip:** Live preview links for Spotify, Apple Podcasts, YouTube Music, and Fountain.fm.

* **Right Pane (Studio & Ingestion):**
  * **Lossless `.py` Payload Extractor:** AST-driven Python script unpacker with live metadata diagnostics and citation counters.
  * **Single-Asset Store Discovery:** Automatically discovers 740×740 square video clips and cover art across both `src/vid/` and DDMA single-asset archives.

* **Top Command Bar:**
  * **`⚡ Mine & Lock`:** 1-Click atomic mining—allocates the next sequential episode number (e.g. `# 247`), updates `SUMMARY.md`, and moves the draft into the Block Template.
  * **`🟢 mdserve:3000` (Two-Way Toggle):** Starts/stops the local `mdbook serve` process on `0.0.0.0:3000` with live port probing.
  * **`🚀 Push (Remote)`:** Stages, commits, and pushes changes to your remote Git repository with automated semantic messages.
  * **`📋 Prompt`:** One-click clipboard copy of the canonical Master Packaging Prompt.
  * **`⚙️ Settings`:** Manage podcast URLs and publishing word limits.

---

## Dependencies & System Requirements

| Tool | Version Requirement | Purpose |
| :--- | :--- | :--- |
| **Python** | `3.10+` (e.g. `3.12`) | Powers the Cockpit backend server (`server.py`), AST payload extractor, and rolling backup engine. **Zero pip dependencies** (built with pure standard library). |
| **Rust & Cargo** | `1.85+` (e.g. `1.97+`) | Compiles the optional headless `md-publish` preprocessor binary. |
| **mdbook** | `v0.5.0+` (e.g. `v0.5.4`) | High-performance CLI documentation engine and local preview server. |
| **mdbook-katex** | `v0.5.1+` (or `v0.10.0+`) | Preprocessor for high-fidelity LaTeX/KaTeX mathematical equation rendering. |

---

## 🗄️ Setting up dd_hub (the workspace)

dd_hub is the workspace — a Google Drive folder that holds the plan, settings, inputs, working assets, and audio/video outputs. mdIngest (the Publishing Cockpit) and DDMA (the clip engine) both read from and write to dd_hub. GitHub is only the intermediary for the *published* Active Master clips; dd_hub is the live workspace. **mdIngest is the entry point**: its landing page is the workspace home.

> [!IMPORTANT]
> **The core rule**: The code only does **local file I/O against a local path**. It **never** calls the Google Drive web API for file access. So dd_hub must be mounted as a local filesystem path on every machine that runs mdIngest or DDMA. The code reads the mount path from the `DD_HUB_ROOT` environment variable.

### What you need

* A Google Drive folder to be your dd_hub. Create a new folder, or use an existing one. Note its folder ID from the Drive URL: `https://drive.google.com/drive/folders/<FOLDER_ID>`.
* The folder should contain (create any that are missing): `episodes/`, `vault/`, `inputs/`, `audio/`, `video/`, `mosaics/`, `manims/`, `rules/`.

### Windows (the reference environment)

* Install Google Drive for Desktop. It mounts your Drive as a local drive (typically `G:\My Drive\`).
* Your dd_hub folder is then at `G:\My Drive\dd_hub` (if your folder is named dd_hub).
* Set `DD_HUB_ROOT` to that path. The code's first candidate is `G:\My Drive\dd_hub`, so this works out of the box.
* All reads/writes are plain local file I/O through the mount. No Drive web API calls are made.

### Linux / VM / Docker

* Install rclone. Configure a Google Drive remote (for example, named `gdrive`).
* Mount the dd_hub folder by its ID to a local path (for example `/mnt/gdrive/dd_hub`):
  ```bash
  rclone mount gdrive: /mnt/gdrive/dd_hub --drive-root-folder-id <FOLDER_ID> --vfs-cache-mode full --daemon
  ```
* Use `--vfs-cache-mode full` — the pipeline does many small reads/writes, and the cache makes it fast. A generous `--vfs-cache-max-size` helps.
* Set `DD_HUB_ROOT` to the mount path (for example `/mnt/gdrive/dd_hub`) and persist it (shell profile, systemd unit, or Docker entrypoint) so it survives new shells.
* In Docker, the entrypoint mounts the Drive folder by ID via rclone to a local path, sets `DD_HUB_ROOT`, then starts the server.

### Settings (the vault)

* The canonical settings file is `dd_hub/vault/settings.json`. It holds the app settings **and** the API keys (Mosaic, Gemini, etc.).
* Create it from `settings.template.json` (in the repo root) and fill in your keys.
* `settings.json` is **never** committed to git. The repo holds only `settings.template.json`. The vault lives in dd_hub, not in the repo.
* Any environment with workspace access gets the full settings.json, including keys.

### Verify the setup

* `echo $DD_HUB_ROOT` shows the mount path.
* The mount contains `episodes/`, `vault/`, `inputs/`, `audio/`, `video/`, `mosaics/`, `manims/`, `rules/`.
* `episodes/<N>/plan.json` is readable (for an existing episode).
* If the mount is unreachable, the apps fall back to the local cache with a loud warning (read-only); writes fail closed — they refuse rather than writing to a stale local copy.

### What NOT to do

* Do **not** use the Google Drive web API or a Drive plugin as the file store. API-level access is too slow and is not a local file path — the pipeline will not work with it. (Fine for one-off reads only.)
* Do **not** fake a local dd_hub folder (an empty local directory named dd_hub). The apps will write to it and the work will never reach the real workspace.
* Do **not** commit `settings.json` (or any file with API keys) to git.
* Do **not** set `DD_HUB_ROOT` to a path that isn't the mounted dd_hub folder.

---

## 🤖 1-Prompt Setup for Antigravity & AI Assistants

If you are setting up `mdIngest` in a new workspace using **Antigravity** or another AI coding assistant, copy and paste this prompt to configure the complete publishing stack automatically:

```text
Please set up and verify the complete md² (mdIngest) publishing environment in this workspace:
1. Verify that Python 3.10+, Cargo/Rust, mdbook (v0.5.0+), and mdbook-katex are installed and available on PATH. If mdbook or mdbook-katex are missing, install them via `cargo install mdbook mdbook-katex`.
2. Build the md-publish preprocessor binary in the `crate/` directory using `cargo build --release`.
3. Verify that `book.toml` contains the required `[preprocessor.katex]` and `[preprocessor.ingest]` configuration blocks.
4. Launch the md² Publishing Cockpit server (`python ui/server.py` or `./start_ui.bat`) on http://localhost:8088 and verify that http://localhost:3000 is accessible via `mdbook serve`.
```

---

## Quick Start: Launching the Cockpit

### Windows 1-Click Launcher
Double-click `start_ui.bat` or run:
```cmd
start_ui.bat
```

### Universal Launch (macOS / Linux / Windows)
```bash
python ui/server.py
```
This opens the workspace landing page at `http://localhost:8088/` — the workspace home (workspace picker, launcher for mdIngest + DDMA + Beats Studio, and the single drop point for new inputs). The Publishing Cockpit is at `http://localhost:8088/cockpit.html`.

---

## The Master Packaging Prompt

*Copy this into Google Gemini, Claude, or ChatGPT to generate a 100% lossless self-extracting payload:*

```text
Objective: Package the complete exhaustive research from this session into a self-extracting Python script without summarizing or pruning.

1. Packaging Requirements:
* Full Fidelity: Package the exhaustive research in its entirety. Do not summarize or prune.
* Absolute KaTeX: Wrap all mathematical notation and symbols in Absolute KaTeX delimiters: $...$ for inline and $$...$$ for block displays. Never leave whitespace adjacent to '$'. Escape financial dollar amounts as \$ (e.g. \$100M).
* Hyperlinked Bibliography: Format every entry in the "Works Cited" section as a clickable Markdown link: [^N]: [Author, Title, Year](URL).
* Title Header: Ensure the document begins with a strict H1 title adhering to a 5-word maximum limit: # [Title].

2. Python Script Format:
Create an executable Python script where the full exhaustive research markdown is stored in raw_markdown:

raw_markdown = """
# [Title]

[Insert complete exhaustive markdown research here with $inline$ and $$block$$ math and [^1] citations...]
"""

if __name__ == '__main__':
    with open('final_research.md', 'w', encoding='utf-8') as f:
        f.write(raw_markdown)
    print("✅ Extracted final_research.md successfully.")
```

---

## The Underlying Rust Preprocessor (`md-publish`)

For automated headless CI/CD builds, `mdIngest` includes the high-performance `md-publish` Rust binary.

### Build & Installation:
```bash
# Build the Rust preprocessor
cargo build --release

# Add to system PATH
cp target/release/md-publish /usr/local/bin/
```

### `book.toml` Configuration:
```toml
[preprocessor.ingest]
command = "md-publish"
downloads_path = "/path/to/downloads"
video_source = "/path/to/video/archive"
lightning_address = "yourname@primal.net"
title_word_limit = 5
```

---

## Safety & Integrity Mechanisms

To ensure `SUMMARY.md` is never corrupted:
1. **Automated Pre-Write Backups:** `server.py` writes rolling timestamped snapshots to `ingest/backups/SUMMARY_<timestamp>.md.bak` before every write.
2. **Surgical AST Section Isolation:** Reconstructs Mempool and Block Template sections while keeping Genesis Pillars and Header links 100% immutable.
3. **Git Atomic Versioning:** Every transaction is tracked in Git with 1-click rollback.

---

## 🐛 Bug tracking

We do **not** manage issues on GitHub. Bugs and fixes for mdIngest, the deepDive pipeline, DDMA, and the portfolio app are tracked in the [Bug Tracker Space](https://muse.ai/s/bug-tracker-ixe6daxhoezyxy/g1O341vEl5aXYIzWFP1db5l-xunGJAxBRSwSJccC110) — a read-only list of all bugs with their status.

---

## License
Licensed under the [MIT License](LICENSE).
