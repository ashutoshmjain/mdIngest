# md² (The mdd Engine)

> **md²** (pronounced *md-squared*) stands for **mdBook deepDive**. Much like `vim` is a recursion of `vi`, **md²** is a recursive evolution of the `mdbook` ecosystem, transformed into an opinionated platform for the **Personal Knowledge Blockchain**.

---

## The Philosophy: Personal Knowledge Blockchain

In the age of LLMs, the cost of generating information has collapsed to zero, but the cost of maintaining **Signal** has skyrocketed. Most research dies in transient chat windows. 

**md²** is the engine for those who refuse to let their inquiries evaporate. It provides a formal framework to organize research into an immutable ledger of discovery:

### 1. The Block Structure
*   **Block 0 (The Genesis Block):** The hardcoded rules of your universe. It contains the **Six Foundational Pillars** (e.g., Bitcoin, Intelligence, Physics) that anchor all subsequent research.
*   **Knowledge Blocks (Block 1, 2, ...):** Chronological epochs of discovery. Each block is limited by the **Law of 21**; once the 21st episodic transaction is mined, the block is locked into the permanent chain.
*   **The Mempool:** The high-entropy zone for unconfirmed drafts and raw signal.

### 2. The Genesis Bump (Hierarchy of Synthesis)
Research in **md²** follows a "Bottom-Up Mining, Top-Down Reading" flow. As insights are discovered within individual episodes, they are "bumped up" to the **Block 0** pillars. Over time, the Genesis Block becomes a compressed, high-fidelity synthesis of your entire knowledge chain.

---

## The Multi-Modal Standard

**md²** transforms raw LLM intelligence into a "Clean Internet" publication that spans three densities:

1.  **The Slice (Visual):** Cinematic video infographics (short-form) used as "Visual Covers."
2.  **The Cake (Audio):** High-level audio overviews for podcast distribution (Spotify, Apple, Fountain).
3.  **The Dough (Text):** Deep, KaTeX-hardened mathematical research papers anchored on `mdbook`.

---

## The Workflow: Mining Knowledge

### Phase 1: Lossless Packaging
To prevent "LLM Pruning" during export, use the **Master Packaging Prompt** to force the LLM to generate a self-extracting Python payload. This ensures 100% structural integrity and zero-loss transmission of complex math and citations.

### Phase 2: Ingestion & Sanitization
Run the `md-publish` binary to "mine" the payload into the chain. The engine automatically:
*   **Hardens KaTeX:** Fixes math delimiters and escapes currency for mdbook-katex compatibility.
*   **Re-indexes Citations:** Manages sequential footnotes and duplicate references.
*   **Syncs Sidebar:** Enforces the 3-layered 4-space hierarchy in `SUMMARY.md`.
*   **Injects Multi-modal UI:** Adds the GitHub download CTA, lightning widgets, and video carousels.

---

## Technical Installation

### Dependencies
- **Rust & Cargo:** (v1.88.0+)
- **mdbook:** (v0.5.3+)
- **mdbook-katex:** (v0.10.0-alpha+)
- **Python 3:** For payload extraction.

### Setup
```bash
# 1. Clone the mdd engine
git clone https://github.com/ashutoshmjain/mdIngest.git
cd mdIngest

# 2. Build the mining tool
cargo build --release

# 3. Add to Path
cp target/release/md-publish /usr/local/bin/
```

---

## Configuration (`book.toml`)

```toml
[preprocessor.ingest]
command = "md-publish"
downloads_path = "/path/to/your/downloads"
video_source = "/path/to/your/video/archive"
lightning_address = "yourname@primal.net"
title_word_limit = 5
```

---

## The Master Packaging Prompt

*Copy this into your LLM session to generate a lossless export:*

```text
Objective: Convert the exhaustive research conducted in this session into a self-extracting Python payload to ensure 100% structural integrity and zero-loss transmission.

1. Packaging Requirements:
* Full Fidelity: Package the exhaustive research in its entirety. Do not summarize or prune.
* Absolute KaTeX: Wrap all mathematical notation and symbols in Absolute KaTeX delimiters: $...$ for inline and $$...$$ for block displays.
* Hyperlinked Bibliography: Format every entry in the "Works Cited" section as a clickable Markdown link: [^N]: [Author, Title, Year](URL).

2. Technical Encoding:
Generate a Python Script that performs the following:
1. Assign the complete Markdown text to a variable named payload_text.
2. Gzip-compress and Base64-encode the payload_text.
3. Output the final Python script containing this encoded string and the logic to decode and write it to a file named final_research.md.
```

---

## License
Licensed under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/). Build the future.
