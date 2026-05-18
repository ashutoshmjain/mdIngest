# GoogleDocs-to-mdbook: The Asset Ingestion Bridge

## Objective
Evolve the deepDive publishing workflow into a streamlined CLI tool named **GoogleDocs-to-mdbook**. The core goal is to bridge the gap between authoring in Google Docs and publishing in mdbook by automating the transfer and sanitization of text directly from the command line.

## The Vision: The "Downloads-to-src" Pipeline
The workflow focuses on a seamless transition from a Google Docs export to a production-ready mdbook page:
1.  **Export:** A Google Docs extension (external) exports the document to the user's `Downloads` folder.
2.  **Ingestion:** The user runs `mdbook-googledocs-to-mdbook ingest-text --number XXX`.
3.  **Renaming:** The tool automatically identifies the latest markdown file in `Downloads`, renames it to `XXX.md`, and moves it to the `src/` folder.
4.  **Surgical Fix:** The tool triggers the Tier 1 `fix_markdown.py` script to handle KaTeX, currency, and footnotes.
5.  **Synchronization:** The tool automatically updates `SUMMARY.md` to include the new episode in the `# Recent ..` section.

## Architectural Model: mdbook Extension
- **Configuration:** Source folders (Downloads), destination (`src/`), and script paths are managed via `book.toml`.
- **Scope:** **Text-only CLI Tool**. No web server or UI components.
- **Technology Stack:** **Rust**. The tool functions as both a standalone CLI and an mdbook preprocessor.

## The Roadmap: Refined Baby Steps

### Baby Step 1: The "Ingestion Bridge"
- **Goal:** Automate the move and rename from `Downloads` to `src/`.
- **Logic:** Identify the newest `.md` file in `Downloads` and move/rename it based on the provided episode number.

### Baby Step 2: Automated Fixer Integration
- **Goal:** Run `fix_markdown.py` immediately after ingestion.
- **Logic:** Execute the Python script and verify the output.

### Baby Step 3: SUMMARY.md Sync
- **Goal:** Zero-touch update of the book's table of contents.
- **Logic:** Append the new entry to the `SUMMARY.md` file.
