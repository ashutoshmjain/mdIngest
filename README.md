# md-publish (The Ingestion Layer)

**md-publish** sits at the center of a new paradigm for deep research. 

Traditionally, research was confined to static papers in arcane archives. Today, LLMs have democratized the generation of high-fidelity information. **md-publish** transforms this raw intelligence into a multi-modal publication that can be promoted like any modern media:
- **Text:** Anchored on `mdbook` for deep, structured reading.
- **Visual:** Introduced by short-form video overviews (created with tools like [Motion](https://motion.so)) for promotion on TikTok, Instagram, and YouTube.
- **Audio:** Supplemented by audio overviews (via tools like NotebookLM) for distribution on Spotify, Apple Podcasts, and Fountain.

## The Vision
We are moving away from the "static image and text" standard of the last century. This tool prioritizes **Video-as-Cover**, allowing researchers to introduce their work through engaging infographics. It is a bridge between rigorous academic depth and the reach of modern social media.

---

## The Workflow

### 1. Research Phase
Conduct your research in a chat session with your preferred LLM. Ensure all facts, citations, and mathematical formulas are established within the chat context.

### 2. Packaging Phase (The "Lossless Tunnel")
Once the research is complete, use the **Master Packaging Prompt** (see below) to export the data. This forces the LLM to package the entire session as a **self-extracting Python script**. 

**What happens here:** The LLM uses its internal interpreter to compress your entire session into a single, immutable Base64 payload embedded in a `.py` file. This prevents the LLM from "pruning" or summarizing the text during export.

### 3. Publishing Phase
**Execution Note:** You MUST run `md-publish` from the root directory of your target `mdbook` repository. This ensures the tool correctly maps to your `src/` and `SUMMARY.md` files.

1.  **Extract the text:** Copy the Python script from the LLM and save it as `export.py`. Run it in your terminal:
    ```bash
    python3 export.py
    ```
    This will generate a file named `final_research.md`.
2.  **Run `md-publish`:** Rename `final_research.md` to your **Research Index** (e.g., `241.md`) and place it in the `src/` folder of your publishing repo. Then use the tool to inject production features:
    ```bash
    # Process text, KaTeX, and sync SUMMARY.md
    md-publish --text [RESEARCH_INDEX]
    
    # Inject Video Covers and Visual Links
    md-publish --video [RESEARCH_INDEX]
    ```

---

## The Master Packaging Prompt

Copy and paste this exact block into your LLM chat session to package your research:

```text
Objective: Convert the exhaustive research conducted in this session into a self-extracting Python payload to ensure 100% structural integrity and zero-loss transmission.

1. Packaging Requirements:
* Full Fidelity: Package the exhaustive research in its entirety. Do not summarize or prune.
* Absolute KaTeX: Wrap all mathematical notation and symbols in Absolute KaTeX delimiters: $...$ for inline and $$...$$ for block displays.
* Hyperlinked Bibliography: Format every entry in the "Works Cited" section as a clickable Markdown link: [^N]: [Author, Title, Year](URL).
* Footnote Mapping: Ensure all [^N] markers are placed in the body text corresponding to the bibliography.

2. Technical Encoding:
Generate a Python Script that performs the following:
1. Assign the complete Markdown text to a variable named payload_text.
2. Gzip-compress and Base64-encode the payload_text.
3. Output the final Python script containing this encoded string and the logic to decode and write it to a file named final_research.md.

Constraint: Do not output standard chat text. Only output the self-extracting Python script.
```

---

## Features

### Text Ingestion (`--text`)
- **KaTeX Hardening:** Fixes formatting for mathematical expressions.
- **Citation Management:** Re-indexes footnotes and handles duplicate sources.
- **Summary Sync:** Automatically adds the new file to `SUMMARY.md`.
- **Audio Links:** Injets **Spotify**, **Apple Podcasts**, and **Fountain** links below the wallet.
- **Lightning Wallet:** Adds a Zap-compatible wallet widget (shutosha@primal.net) for reader tips.

### Visual Ingestion (`--video`)
We believe static cover images are obsolete. Instead, we use short-form video infographics to introduce research.
- **Dynamic Layout Toggling:**
    - **Single Video:** If only one MP4 is found for the Research Index, it is injected as a full-width, responsive, unmutable cover.
    - **Horizontal Scroll:** If multiple MP4s are found, the utility creates a "Cinematic Scroll" horizontal strip for the reader to swipe through.
- **Visual Social Links:** Injects buttons for **TikTok**, **Instagram**, and **YouTube** directly below the video area.

---

## Configuration (`book.toml`)

```toml
[preprocessor.ingest]
command = "md-publish"
downloads_path = "/path/to/your/downloads"
lightning_address = "shutosha@primal.net"
title_word_limit = 5
```
