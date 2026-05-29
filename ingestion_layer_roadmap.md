# Ingestion Layer Roadmap: Research-to-Publish Workflow

## Objective
Evolve the deepDive publishing workflow into a streamlined CLI tool named **md-publish**. The core goal is to serve as the **Ingestion Layer** in an agentic research-to-publish workflow, automating the transfer, sanitization, and media-enrichment of AI-generated reports.

## The Vision: The "Research-to-src" Pipeline
The workflow focuses on a seamless transition from AI research to a production-ready mdbook page:
1.  **Generation:** An LLM (currently Gemini Pro) generates a research report using the **Master Prompt**.
2.  **Ingestion:** The user runs `md-publish --text XXX`.
3.  **Renaming:** The tool automatically identifies the "shielded" markdown file in `Downloads`, renames it to `XXX.md`, and moves it to the `src/` folder.
4.  **Surgical Fix:** The tool triggers the internal sanitization logic to handle KaTeX, currency, and footnotes while stripping the "Shield".
5.  **Synchronization:** The tool automatically updates `SUMMARY.md` to include the new episode in the `# Recent ..` section.
6.  **Media Enrichment:** The user runs `md-publish --image XXX` (and eventually `md-publish --video XXX`) to migrate assets and inject high-engagement visual snippets.

## Future Strategic Direction: Decoupled Publishing
The long-term goal for **md-publish** is to become a platform-agnostic bridge between LLM outputs and structured publishing. Future architectural evolutions will likely include:
- **Tier 1: Agnostic Ingestion:** Hardened sanitization and asset organization in a universal staging area.
- **Tier 2: Specific Synchronization:** A `sync` command to handle platform-specific indexing (e.g., `md-publish sync --target mdbook` for `SUMMARY.md` or `--target obsidian` for vault metadata).
- **Extensible Profiles:** Allowing users to choose their publishing style (mdbook, Obsidian, Hugo) while relying on the same core sanitization engine.

## Architectural Model: mdbook Extension (Current)
- **Configuration:** Source folders (Downloads), destination (`src/`), and script paths are managed via `book.toml`.
- **Scope:** **Text-only CLI Tool**. No web server or UI components.
- **Technology Stack:** **Rust**. The tool functions as both a standalone CLI and an mdbook preprocessor.

## The Roadmap: Refined Baby Steps

### Baby Step 1: The "Ingestion Bridge" (Completed ✅)
- **Goal:** Automate the move and rename from `Downloads` to `src/`.
- **Logic:** Identify the newest `.md` file in `Downloads` and move/rename it based on the provided episode number.

### Baby Step 2: Native Sanitization Logic (Completed ✅)
- **Goal:** Harden and sanitize the Markdown immediately after ingestion.
- **Logic:** Execute the internal `sanitizer.rs` logic (KaTeX hardening, shield stripping, title limits) during the ingestion pass.

### Baby Step 3: SUMMARY.md Sync (Completed ✅)
- **Goal:** Zero-touch update of the book's table of contents.
- **Logic:** Append the new entry to the `SUMMARY.md` file.

### Baby Step 4: Image & Social Ingestion (Completed ✅)
- **Goal:** Automate cover image migration and insert social/monetization widgets.
- **Logic:** 
    1. Identify latest image in `Downloads`.
    2. Move to `src/img/XXX.png`.
    3. Update `src/XXX.md`:
        - Insert image after H1.
        - Insert centered podcast links snippet.
        - Insert lightning/wallet widget (shutosha@primal.net) above references.

### Baby Step 5: Video Ingestion (Completed ✅)
- **Goal:** Automate infographic video migration and present them in a high-engagement carousel.
- **Logic:**
    1. **Master Key Discovery:** Search `Downloads` for all files matching `XXX-*.mp4` (where XXX is the episode number).
    2. **Asset Migration:** Move all matching videos to `src/vid/`.
    3. **The "Scroll Strip" Layout:** Inject a horizontal scrollable `<div>` immediately **above the Wallet/Tips widget**.
    4. **Layout Specs:** 
        - **Flexbox Carousel:** Videos arranged side-by-side.
        - **Scroll Snapping:** Enabled (`scroll-snap-type: x mandatory`) so videos center perfectly on swipe/scroll.
        - **Visual Hint:** First video takes ~85% width to reveal the edge of the next one.
        - **Interactive:** Individual floating toggle-mute buttons for each video.
