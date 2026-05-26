# DeepDive Creative Workflow: The Opinionated Researcher

This document outlines the **4-Phase Research Process** for producing high-fidelity research episodes using the `mdbook-ingest` tool.

---

## Phase 1: Research & Export (The Gemini Protocol)
1. **Research:** Conduct deep-dive research in Google Gemini (2.0/Pro).
2. **Finalize:** Use the **Master Ingestion Prompt** to generate a shielded, production-ready report.
   > **Master Ingestion Prompt:**
   > "Please provide the final version of the report, delivered strictly according to these formatting constraints:
   > 
   > 1. Shield the Output from the Parser: Wrap the entire report inside a single Rust code block using a raw string literal wrapper (i.e. start with ```rust followed on the next line by r#" and end with "# followed by ```). This guarantees my interface compiles it strictly as a static code array, preserving raw '#' characters and '$$' math signs.
   > 2. Direct Citations: Embed precise source-id identifiers (e.g. [1, 2]) directly inline next to each claim.
   > 3. Formal Bibliography: Provide a complete, structured "References" or "Bibliography" section at the end of the report, mapping every inline citation to its exact author, paper title, year, and URL from the retrieved sources.
   > 4. LaTeX Constraint: Do not include any whitespace immediately adjacent to the '$' or '$$' math delimiters.
   > 5. Table Constraint: Use only single spaces between cell contents and the pipe '|' separators to prevent tabular rendering errors."
3. **Export:** Copy the entire shielded block (including ` ```rust ` and `r#"...` artifacts) and save it as a `.rs` file (e.g., `ep241.rs`) in your `Downloads` folder.

## Phase 2: Text Ingestion (`--text`)
1. **Run Ingestion:** Execute the tool to sanitize and index the chapter.
   ```bash
   mdbook-ingest --text --number XXX
   ```
2. **Verification:** Verify that `src/XXX.md` has been created with hardened KaTeX, sequential footnotes, and the correct H1 title.

## Phase 3: Media Ingestion (`--image`)
1. **Cover Art:** Generate or source a cover image (PNG/JPG) and save it to your `Downloads` folder.
2. **Run Ingestion:** Execute the image ingestion command.
   ```bash
   mdbook-ingest --image --number XXX
   ```
3. **Syndication:** This step automatically injects **Spotify**, **Apple Podcasts**, and **YouTube** links, along with a **Lightning Zap Widget**.

## Phase 4: Visual Ingestion (`--video`)
1. **Infographics:** Generate infographics using Mosaic AI Video Editor.
2. **Setup:** Place the resulting `.mp4` files in `src/vid/` following the strict naming convention: `XXX-description.mp4`.
3. **Run Ingestion:** Execute the video ingestion command to build the global carousel.
   ```bash
   mdbook-ingest --video --number XXX
   ```

---

## Global Distribution Workflow (Post-Ingestion)
1. **Audio Production:** Create Audio Overviews (Deep Dives) in NotebookLM.
2. **Podcast Syndication:** Publish audio on Spotify (auto-syndicates via RSS to YouTube, Apple, Fountain).
3. **Static Video:** YouTube converts the audio feed into a static video.
4. **Final Build:** Run `mdbook build` to deploy the final multimedia research paper to GitHub Pages.
