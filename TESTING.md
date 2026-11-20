# Testing Strategy — the e2e suite, two tiers

The end-to-end suite is `ingest/tests/cockpit_e2e.js` (puppeteer). It runs in **two
tiers**, because the suite assumes a lived-in install and mdIngest is deliberately a
template. Neither tier substitutes for the other.

## Tier 1 — Clean room (WSL, mdIngest clone, no data)

Proves the pure codebase boots, serves, and keeps its user-visible strings honest,
in a repo with **no episode content at all**.

- One-time setup: `cd ingest/tests && npm install` (puppeteer brings its own
  Chromium; no sudo). Test dependencies are dev-only — they are **never** part of
  the user install prompt in the README.
- Run recipe (identical every time, so runs are comparable): start
  `python3 ingest/server.py` with `PORT=8088`, run the suite with `NO_BROWSER=1`,
  workspace pointed at the empty test workspace (the rclone-mounted test folder —
  an empty workspace structure with one settings.json).
- After a run, clean up before any fan-out check: delete generated ingest/backups/*.bak files (run residue). ingest/tests/package-lock.json is committed and mirrored — if an install ever changes it, mirror the change.
- **Baseline (2026-11-20): 8 pass / 10 fail.** The 10 failures below are fixture
  absences, not bugs. Judge every run against this list: a failure **outside**
  the list, or a pass count **below** baseline, is a real finding. A red run
  that matches the list exactly is a healthy run.

### The fixture-failure list (Tier 1)

1. *Initial Page Boot & Status Rendering* — no episode cards (no `src/` content).
2. *Landing: workspace URL + resolved path* — the resolved path has no `dd_hub`
   segment; the WSL test workspace is the mount root. Environment-bound.
3. *Landing launcher: DDMA launch* — no base transcription for episode 247.
4. *DDMA launch: panel states* — blocked upstream by #3; this is also where the
   two `✓ Cutroom ready: ` assertions live, so they only verify live in Tier 2
   (or here, if a transcription fixture ever exists).
5. *Workspace home link* — Curator is not running on :8000 in this tier.
6. *Research Paper Sheet* — no episode card in the ledger tree.
7. *Reels Media Grid* — no clips in the workspace.
8. *Episode Listen Buttons* — no episode 249 content.
9. *DDMA Auto-Seeding* — same missing episode-247 transcription as #3.
10. *Overwrite Guards* — `src/249.md` does not exist in a template repo.

## Tier 2 — Loaded workbench (Windows, deepDive clone, real data)

The full suite against the real install: real episodes in `src/`, the real
workspace (transcriptions, plans, clips), and the **full stack running** —
ingest server on :8088 **and** Curator on :8000. Here, every test is expected
to pass; any failure is a finding. This is the only tier where content flows
(transcription reuse, listen buttons, overwrite guards) verify end to end.

## Keeping this file true

- When a test is added, removed, or changes what it needs, update the Tier-1
  baseline and the fixture list in the same commit.
- When a fixture failure stops being one (an assertion fixed, a fixture added),
  move it out of the list and restate the baseline numbers.
- This file lives identically in both repos (deepDive and mdIngest). Edit it in
  one, mirror it to the other, and keep the fan-out checker green.
