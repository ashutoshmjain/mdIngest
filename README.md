# mdbook-ingest (The Ingestion Layer)

**mdbook-ingest** is a modular component of an emerging **Agentic Research-to-Publish Workflow**. Its specific role is the "Ingestion Layer"—transforming raw AI-generated research into production-ready `mdbook` assets.

While the current implementation is optimized for **Google Gemini Pro** (via a specific "Master Prompt"), the architecture is designed to be LLM-agnostic, with future support planned for ChatGPT, Claude, and other research agents.

## 🤖 The Agentic Vision: From Research to Global Syndication

This tool is one part of a larger, multi-agent system:
1.  **Research Agent:** (Future) Specialized agent to conduct research and extract text from LLMs using standardized prompts.
2.  **Ingestion Agent (This Tool):** Sanitizes text, manages media, and indexes episodes using the **Master Key** (Episode Number).
3.  **Publishing Agent:** (Future) Handles syndication to GitHub Pages, LinkedIn, Nostr, and other platforms.

## 🚀 Current Pipeline: Gemini-to-mdbook

Currently, the tool supports a streamlined transition from Gemini Pro research to `mdbook`:

1.  **Draft:** Generate a report in Gemini Pro using the **Master Prompt**.
2.  **Ingest Text:** Run `mdbook-ingest --text --number XXX`. The tool strips the "Shield" and sanitizes the content.
3.  **Ingest Image:** Run `mdbook-ingest --image --number XXX`. The tool migrates cover art and injects social/monetization widgets.

---

## 🔑 The Master Prompt (Current Standard)

To ensure compatibility with the ingestion layer's sanitization logic, use this prompt in Gemini Pro:

```text
Please provide the final version of the report, delivered strictly according to these formatting constraints:

1. Shield the Output from the Parser: Wrap the entire report inside a single Rust code block using a raw string literal wrapper (i.e. start with ```rust followed on the next line by r#" and end with "# followed by ```). This guarantees my interface compiles it strictly as a static code array, preserving raw '#' characters and '$$' math signs.
2. Direct Citations: Embed precise source-id identifiers (e.g. [1, 2]) directly inline next to each claim.
3. Formal Bibliography: Provide a complete, structured "References" or "Bibliography" section at the end of the report, mapping every inline citation to its exact author, paper title, year, and URL from the retrieved sources.
4. LaTeX Constraint: Do not include any whitespace immediately adjacent to the '$' or '$$' math delimiters.
5. Table Constraint: Use only single spaces between cell contents and the pipe '|' separators to prevent tabular rendering errors.
```

---

## ✨ Features

### 📖 Modular Ingestion (`--text`)
- **Shield Stripping:** Automatically handles "shielded" content blocks (currently supporting Gemini's Rust-style raw string literals).
- **Intelligent Sanitization:** 
    - Enforces a 5-word limit for H1 titles.
    - Strips invisible Unicode characters (`\u{0332}`, etc.).
    - Wraps ASCII diagrams and tables in Markdown-compatible syntax.
- **Footnote Hardening:** Re-numbers and formats bibliography sections for perfect KaTeX rendering.

### 🖼️ Media & Socials (`--image`)
- **Master Key Migration:** Moves images to `src/img/XXX.png` based on episode number.
- **Surgical Snippets:** Injects cover art, podcast links, and Lightning Wallet widgets at precise semantic locations.

---

## ⚙️ Configuration (`book.toml`)

`mdbook-ingest` is highly customizable. You can configure the tool by adding an `[preprocessor.ingest]` section to your `book.toml`. If any fields are omitted, the tool uses sane defaults.

```toml
[preprocessor.ingest]
command = "mdbook-ingest"
# Path to your browser's default download folder
downloads_path = "/mnt/c/Users/ashut/Downloads"
# Your lightning address for the Zap widget
lightning_address = "shutosha@primal.net"
# Maximum number of words for the H1 title
title_word_limit = 5
# Custom HTML snippet for podcast or social links
podcast_html = """
<center><a href="https://open.spotify.com/..." style="...">Spotify</a></center>
"""
```

---

## 🛠️ Installation & Usage

```bash
cargo build --release
./target/release/mdbook-ingest --text --number 243
./target/release/mdbook-ingest --image --number 243
```

---

## ⚖️ License
MIT License.
