# Antigravity Workspace Guidelines & Push Rules

> Slim always-on core. The deep specs moved to `.agents/rules/` (trigger: `model_decision`) — read the matching guide when the task touches its area; do not paste them into context unasked. This file must stay under 24,000 bytes or Antigravity truncates it.

## Repository Roles & Strict Media Boundaries

1. **`mdIngest` (Merged Upstream Repository)**:
   - The ONE repo users fork. App code lives in `ingest/` (servers, cockpit, landing page); the DDMA extension lives in `ddma/` (Curator/Clip Studio + Beats Studio).
   - Contains ONLY code and templates. **STRICT RULE**: NEVER commit or push audio/video media files or binary assets to `mdIngest` — including its `ddma/` folder.
   - The standalone `ddma` repo is archived. Do NOT mirror to it, push to it, or clone it for setup.

2. **`deepDive` (Local Studio Workbench & Publication Repository)**:
   - **Dual Role**:
     a. **Unified Local Runtime**: On local machines, `deepDive` acts as the active "monorepo" execution workbench (`start_ingest.bat` launches `python ingest/server.py` and calls `ddma/ddma.py` inside `deepDive`).
     b. **Publication Repository**: Designated repository for published episode articles (`src/<num>.md`) and curated episode publication media (`src/ddma/docs/episodes/<num>/clips/*.mp4`).

## Primary Workbench & Fan-Out Push Invariant

1. **`deepDive` is the Active Development Workbench**:
   - Because `start_ingest.bat` launches `python ingest/server.py` and executes `ddma/ddma.py` directly inside `deepDive`, **all active code changes, bug fixes, UI styling, and testing must be done directly in `deepDive`**:
     - UI & Server fixes → `deepDive/ingest/` (`server.py`, `cockpit.html`, `settings.json`)
     - Engine & animation fixes → `deepDive/ddma/` (`ddma.py`, `curator.html`, `scratch/run_curator.py`, `scratch/review_episode_bridges.py`, `archetype_studio.py`, etc.)
   - This guarantees that what you test on `localhost:8088` and `localhost:8000` is immediately what is running.

2. **The "Push All" Fan-Out Protocol**:
   Whenever instructed to commit and push per our push strategy:
   - **Step 1: Fan-Out Mirroring**: Copy the tested code from `deepDive` outward into the merged repo:
     - `deepDive/ingest/*` (server.py, cockpit.html, etc. — everything EXCEPT `settings.json`, template only) ⟶ `mdIngest/ingest/*`
     - `deepDive/ddma/` engine + harness ⟶ `mdIngest/ddma/` (same relative paths)
     - After mirroring, blob-compare (`git hash-object`) every file the workbench commit touched in engine/UI scope. A fix that adds a new script or test must extend the pair list in `scripts/check_fanout.py` in the same edit.
     - The standalone `ddma` repo is archived. Do NOT mirror to it, push to it, or clone it for setup.
  - **Step 2: Pre-Push Media Verification**: Verify that `mdIngest` (including its `ddma/` folder) contains ONLY code and templates -- **NEVER binary media** (`*.mp4`, `*.mp3`, `*.wav`, `*.m4a`) and **NEVER `settings.json`** (it holds live API keys; template only, no keys).
   - **Step 3: Two-Repo Commit & Push**:
     - Commit and push `deepDive` to its GitHub remote (preserves local workbench + publication articles/media).
      - **Current phase (pre-release): `deepDive` is a backup mirror of the local workbench — commit everything except large media files, intermediate manim-production artifacts, and live secrets. `settings.json` holds live API keys, so only its sanitized `settings.template.json` goes in the repo; the live file stays local-only (back it up in the private dd_hub vault, never on public GitHub). `mdIngest` is the codebase without assets — data-free and settings-free, template only. Keep both repos in sync until a release candidate. At RC/GA, switch to a real Dev/QA/Prod strategy (selective releases, staging, QA gate) — the mirror rule ends there.**
     - Commit and push `mdIngest` to its GitHub remote (clean upstream app + extension).
     - After mirroring and before committing, run `python scripts/check_fanout.py` from the workbench root: it recomputes every workbench-to-mdIngest pair and blob-compares them. Any NON-ZERO exit (unmirrored or modified copy) means STOP -- do not commit, do not push, re-mirror first.

3. **Active Master Clips Publication & Distribution Invariant**:
   - **Local Staging vs. Remote Distribution**:
     - Whenever an active master clip is compiled in DDMA (`ddma compile-clip` or Curator `/set-active-master`), it is automatically staged to:
       a. `deepDive/src/ddma/docs/episodes/<ep>/clips/<ep>-<clip>.mp4` (via `resolve_deepdive_publication_clips_dir()`, anchored on `Path(__file__).resolve()`).
       b. `dd_hub/mosaics/<ep>-<clip>.mp4` (or `manims/`) for 1-tap mobile review.
     - **CRITICAL DISTRIBUTION RULE**: Google Drive (`dd_hub/mosaics/` and `manims/`) serves ONLY as a personal mobile review outbox and manual fallback. **The Active Master reel has THREE independent consumers, and ALL of them pick it up from GitHub Pages (`deepDive/src/ddma/docs/episodes/<ep>/clips/`) — never from Drive:**
       - **(1) The distribution agent (`meta-muse` / Muse)** — picks the mp4 file from the repo and re-publishes it to Nostr / Instagram / YouTube / TikTok (X and LinkedIn get link posts, not video).
       - **(2) `deepdive.shutri.com`** — serves the reel two ways: the episode-page carousel (`VIDEO_STRIP` in `src/<ep>.md`) and the DDMA player (`ddma/docs/index.html`, driven by `episodes.json` + per-episode `plan.json`; the player HEAD-probes each clip and silently hides missing ones).
       - **(3) `shutri.com`** — the Shutri peer-review site, where deepDive is the reference implementation; it links visitors to the player and episode pages (no direct mp4 fetch), so its showcase breaks whenever a clip is not live on GitHub Pages.
     - An active clip is **NOT considered published or live on the web until it is committed and pushed to GitHub in `deepDive` AND passes the 3-point live check below**.
   - **Pre-Push Markdown Carousel Synchronization**:
     - Before committing and pushing `deepDive`, `sync_episode_clips_and_markdown(ep)` MUST be executed (either automatically triggered by Cockpit's "Push (Remote)" button at `/api/git/push` or run as part of the push checklist).
     - This automatically scans all canonical clips (`<ep>-*.mp4`) in both `deepDive/ddma/clips/` and `deepDive/src/ddma/docs/episodes/<ep>/clips/`, stages them into `src/ddma/docs/episodes/<ep>/clips/`, and regenerates the `<!-- VIDEO_STRIP_START -->` ... `<!-- VIDEO_STRIP_END -->` carousel in `src/<ep>.md` so the live mdBook article embeds the full clip deck.
   - **Idempotent Overwrite on Re-Run**:
     - Re-running Mosaic or Manim on an active clip automatically overwrites the local staged master in `deepDive/src/ddma/docs/episodes/<ep>/clips/<ep>-<clip>.mp4` and `dd_hub/mosaics/<ep>-<clip>.mp4`.
     - Upon the next Push, Git seamlessly commits and pushes the updated binary video replacing the previous version on GitHub, updating `deepdive.shutri.com` and Muse without changing URL schemes or breaking links.
   - **Strict Pure-Code Boundaries on Standalone Repos**:
     - `deepDive` is the **ONLY** repository permitted to stage and push active binary clips (`src/ddma/docs/episodes/<ep>/clips/*.mp4`).
     - `mdIngest` must **NEVER** contain or stage binary `.mp4` assets during the Fan-Out push.

### Clips are the key product — three consumers, one file

Of everything the pipeline produces, the short reel (`<ep>-<clip>.mp4`, 9:16 Active Master) is the key product: it is the only asset with three independent consumers (distribution agent, `deepdive.shutri.com`, `shutri.com`). The article, the longform audio, and the longform video each have a single pickup path. Treat a missing or stale clip as a pipeline-down event, not a single-platform miss.

A clip is **NOT considered published or live** until ALL THREE of these hold:
1. The file is committed and pushed to GitHub in `deepDive` AND reachable at its GitHub Pages URL (`https://deepdive.shutri.com/ddma/docs/episodes/<ep>/clips/<ep>-<clip>.mp4`).
2. The episode is listed in `ddma/docs/episodes.json` (and its `src/` mirror) so the player can find it, and the clip appears in the episode-page carousel in `src/<ep>.md` (regenerated by `sync_episode_clips_and_markdown`).
3. The distribution agent can pick the same file from the repo (same path, same bytes).

The 2026-11-09 incident is the reference case: 249-5 "Quaternions" reached Drive but never GitHub, and distribution, the episode page, the player, and the shutri.com showcase all broke at once from one missing file.

## Secret & Configuration Contract

- **Environment-First Resolution**: All engines (`ingest/server.py`, `ddma/ddma.py`, `ddma/scratch/run_curator.py`) resolve configuration secrets (`GEMINI_API_KEY`, `MOSAIC_API_KEY`, `DD_HUB_ROOT`, etc.) by checking process environment variables FIRST before falling back to local `settings.json`.
- **Zero Secrets Committed**: `settings.json` is strictly ignored by git in all repositories (`.gitignore`). Neither `deepDive`, `mdIngest`, nor `ddma` may ever commit or stage live API keys. A sanitised `settings.template.json` is maintained at repo root as the canonical schema reference.
- **Factory Defaults Backup**: the shipped Mosaic default prompt lives tracked at `ddma/scratch/mosaic_factory_defaults.json` (force-add: `scratch/` is git-ignored). Curator Reset restores this text via the `factory_mosaic_prompt` field — never the stored value. Suites must restore any prompt they overwrite. The full gold text is backed up below (canonical human-readable copy; the JSON file is the machine-readable copy the code reads).
- **Gold Mosaic default prompt** (must match `mosaic_default_prompt` in `ddma/scratch/mosaic_factory_defaults.json` and the hardcoded fallback in `get_factory_mosaic_prompt()`):
```
MOTION DESIGN INSTRUCTIONS (YOUTUBE SHORTS - around 150 to 180 seconds long)

- Cover the entire timeline of the video with Dan Koe-style motion graphics. Visual coverage must be active and persistent from 0:00 to the very last second with ZERO blank frames.

- Maintain uniform graphic density across all segments.

- Plan 10 to 12 continuous segments of roughly ~ 15 seconds each, perfectly mapped to the clip length. Each segment renders a dynamic diagrammatic graphic with changing visual steps and text reveals.

- Assume background video is a blank black glossy screen (#000000). Keep persistent visuals (animations, conceptual geometry, or text) throughout. Segments must hand off to each other seamlessly like a relay race.

--------------------------------------------------
PACING & ANIMATION RULES
--------------------------------------------------
- No static holds beyond 6 seconds. Introduce visual changes or step reveals every 2-4 seconds.
- Use only basic transforms: opacity, position, scale. Keep animations single-property per element.
- Prefer step-based reveals over continuous complex motion. Avoid preset/template animations.
- No gaps in infographic coverage. Zero external asset dependencies.
```

## Pre-Push Verification Checklist
- Before committing and pushing in `mdIngest`, always verify that NO binary media files (`*.mp4`, `*.mp3`, `*.wav`, `*.m4a`) and NO `settings.json` are staged.
- Only code, templates, and JSON metadata are allowed in `mdIngest`.
- Always mirror changes made in `deepDive` out to `mdIngest` (`ingest/` + `ddma/`) before finalizing pushes.
- For active episode clips: verify that `sync_episode_clips_and_markdown(ep)` has staged all active master clips (`<ep>-<clip>.mp4`) into `deepDive/src/ddma/docs/episodes/<ep>/clips/` and regenerated the `src/<ep>.md` video strip before committing `deepDive`.

## Clip invariants (summary — full detail in `.agents/rules/`)

- **0-based numbering**: `Clip 0` = prologue / cold open; `Clip 1+` matches the spoken `"Clip 1"`, `"Clip 2"`. Never re-index in UI or code.
- **Intro titles max 3 words** (`Clip 0` shows `EPISODE <n>` + episode title, no Part number); **outro bridges max 5 words** (a curiosity question, never a repeat of the spoken "Coming up in...").
- **Pure `#000000` intro & outro cards**; never use clip frames as card backgrounds.
- **Engine purity**: a clip is 100% Mosaic OR 100% Manim; `visual_source` in `plan.json` picks the Active Master.
- **Never cut from the mastered `.mp3`** — canonical audio is always the continuous `.m4a` (inserted stings shift timestamps ~35s).

## Detail guides (`.agents/rules/` — `trigger: model_decision`, read on demand)

- `distribution-strategy.md` — dd_hub layout, platform routing and pickup rules, Manim `media/` rules.
- `clip-dynamics.md` — tripartite spoken pattern, clip numbering, intro/outro card invariants.
- `clip-stitching-acoustics.md` — 3-stage assembly, acoustic word-boundary resolvers, short-reel vs longform dual-track.
- `visual-standards.md` — canvas, typography, and cartoon standards for reels and longform video.

## Token Budget & Context Hygiene

- Never read raw `transcript.jsonl` into context (46 KB / ~12,000 tokens a call); extract the last 5–10 step summaries with a compact script instead.
- Never read entire generated Manim scripts into context; inspect with targeted regex/AST and patch in batches.
- Keep CLI output to summary lines; verbose tracebacks go to log files.
- One background compilation/render at a time; delegate repetitive loops to a subagent and `/compact` between major phases.
