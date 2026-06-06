# md-publish (The Ingestion Layer)

**md-publish** is a tool used to move high-fidelity research from an LLM (Gemini, ChatGPT, or Claude) into a production-ready `mdbook` environment. It handles formatting, mathematical proofs (KaTeX), and required metadata for publishing.

## The Workflow

### 1. Research Phase
Conduct your research in a chat session with your preferred LLM. Ensure all facts, citations, and mathematical formulas are established within the chat context.

### 2. Packaging Phase (The "Lossless Tunnel")
Once the research is complete, use the **Master Packaging Prompt** (see below) to export the data. This forces the LLM to package the entire session as a **self-extracting Python script**. 

**What happens here:** The LLM uses its internal interpreter to compress your entire 10,000+ word session into a single, immutable Base64 payload embedded in a `.py` file. This prevents the LLM from "pruning" or summarizing the text during export.

### 3. Publishing Phase
1.  **Extract the text:** Copy the Python script from the LLM and save it as `export.py`. Run it in your terminal:
    ```bash
    python3 export.py
    ```
    This will generate a file named `final_research.md` containing your 100% intact research.
2.  **Run `md-publish`:** Rename `final_research.md` to your episode number (e.g., `241.md`) and place it in the `src/` folder. Then use the tool to inject production features:
    ```bash
    # Process text, KaTeX, and sync SUMMARY.md
    md-publish --text 241
    
    # Inject Video Covers and Visual Links
    md-publish --video 241
    ```

---

## The Master Packaging Prompt

Use this prompt in your LLM chat session to export your research:

> **Objective:** Convert the exhaustive research conducted in this session into a self-extracting Python payload to ensure 100% structural integrity and zero-loss transmission.
> 
> **1. Packaging Requirements:**
> *   **Full Fidelity:** Package the exhaustive research in its entirety. Do not summarize or prune.
> *   **Absolute KaTeX:** Wrap all mathematical notation and symbols in Absolute KaTeX delimiters: `$...$` for inline and `$$...$$` for block displays.
> *   **Hyperlinked Bibliography:** Format every entry in the "Works Cited" section as a clickable Markdown link: `[^N]: [Author, Title, Year](URL)`.
> *   **Footnote Mapping:** Ensure all `[^N]` markers are placed in the body text corresponding to the bibliography.
>
> **2. Technical Encoding:**
> Generate a **Python Script** that performs the following:
> 1. Assign the complete Markdown text to a variable named `payload_text`.
> 2. Gzip-compress and Base64-encode the `payload_text`.
> 3. Output the final Python script containing this encoded string and the logic to decode and write it to a file named `final_research.md`.
> 
> **Constraint:** Do not output standard chat text. Only output the self-extracting Python script.

---

## Features

### Text Ingestion (`--text`)
- **KaTeX Hardening:** Fixes formatting for mathematical expressions.
- **Citation Management:** Re-indexes footnotes and handles duplicate sources.
- **Summary Sync:** Automatically adds the new file to `SUMMARY.md`.
- **Audio Links:** Injets **Spotify**, **Apple Podcasts**, and **YouTube Music** links immediately under the title.
- **Lightning Wallet:** Adds a Zap-compatible wallet widget (shutosha@primal.net) for reader tips.

### Visual Ingestion (`--video`)
We believe static cover images are obsolete. Instead, we use short-form video infographics to introduce research.
- **Dynamic Layout Toggling:**
    - **Single Video:** If only one MP4 is found (e.g., `241-Intro.mp4`), it is injected as a full-width, responsive, unmutable cover.
    - **Horizontal Scroll:** If multiple MP4s are found, the utility creates a "Cinematic Scroll" horizontal strip for the reader to swipe through.
- **Visual Social Links:** Injects buttons for **TikTok**, **Instagram**, and **YouTube (Vids/Shorts)** directly below the video area.

---

## Configuration (`book.toml`)

```toml
[preprocessor.ingest]
command = "md-publish"
downloads_path = "/path/to/your/downloads"
lightning_address = "shutosha@primal.net"
title_word_limit = 5
```
