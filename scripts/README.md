# Scripts Directory

This directory contains the automation tools for the `deepDive` project. The publication routine is a two-tier process designed to ensure all articles adhere to the project's technical and aesthetic standards.

---

## The Publication Workflow

The workflow is divided into **Independent Automation** (handled by separate scripts) and **Intelligent Orchestration** (handled by the AI agent).

### Tier 1: Execution Engine (Standalone Scripts)
We use three distinct scripts to handle text, images, and videos independently, as these artifacts are often produced and integrated at different times.

#### 1. `fix_markdown.py`
**Purpose:** Handles text sanitization, KaTeX protection, and technical formatting.
- **Deep Sanitization:** Strips invisible Unicode characters and control codes.
- **KaTeX & Currency:** Standardizes math blocks and converts `$` to `USD`.
- **Citations:** Re-numbers footnotes sequentially and normalizes the "References" section.
- **Wallet:** Appends the Lightning widget.

#### 2. `fix_pics.py`
**Purpose:** Handles H1 layout, cover image integration, and indexing.
- **Layout:** Enforces `# Index : Title` format and injects the episode's cover image (`src/img/<number>.png`).
- **Podcast Snippet:** Injects centered links to major podcast platforms.
- **Navigation:** Automatically updates `SUMMARY.md` to include the file in the `# Recent ..` section.

#### 3. `fix_vids.py`
**Purpose:** Automates the expansion of complex "Cinematic Infographic" video HTML.
- **Expansion:** Searches for simple markers like `[vid: 234-intro.mp4]` and expands them into the full, styled HTML block with autoplay/mute controls.

---

### Tier 2: Agent Orchestration (The Intelligence)
While the scripts handle the structure, the AI agent (Gemini CLI) provides the "intelligence" and is pre-authorized via the project's automation policy (`.gemini/policies/automation.toml`).

#### Agent Responsibilities:
1.  **Semantic Media Placement:** Reads the article content and identifies the best paragraph to insert video markers or additional images.
2.  **Paragraph Optimization:** Breaks up large "walls of text" into digestible paragraphs for mobile readability.
3.  **Research & Validation:** Fetches missing citation URLs and verifies the build with `mdbook build`.
4.  **Source Control:** Finalizes the task by staging, committing, and pushing to the repository.

---

## The Evolutionary Development Cycle

To reach the goal of autonomous publishing with minimal intelligence, the toolchain follows an iterative testing loop for every new episode:

1.  **Data Intake:** User providesNumbered `.md`, `.png`, and `.mp4` files.
2.  **Independent Execution:** Run the relevant script(s) for the available artifacts.
3.  **Manual Supplement:** The agent fixes remaining edge cases (citations, KaTeX) manually.
4.  **Publication:** The verified article is committed and pushed.
5.  **Root Cause Analysis (RCA):** The agent identifies script limitations.
6.  **Refactoring:** Scripts are updated to handle the new edge cases automatically.

---

## Progressive Web App (PWA) & Offline Support

The project transforms the `mdbook` into a standalone, installable application.

### 1. Simplified Installation
Installation instructions are integrated directly into the landing page for all platforms (iOS, Android, and Desktop).

**Benefits:**
- **Offline Access:** Read the entire book without an internet connection.
- **Performance:** Faster loading times via localized caching.
- **Home Screen Integration:** A clean icon for instant access.

### 2. Live Content Updates
- **Update Notifications:** The Service Worker detects new publications and displays a "✨ New Content Available!" notification.
- **Instant Refresh:** Users can update the app instantly.

---

### Usage

Run the scripts independently based on the artifacts you have ready:

```bash
python3 scripts/fix_markdown.py src/225.md
python3 scripts/fix_pics.py src/225.md
python3 scripts/fix_vids.py src/225.md
```
