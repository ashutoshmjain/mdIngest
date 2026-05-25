# mdbook-ingest preprocessor (The Ingestion Layer)

**mdbook-ingest** is a professional Rust-based preprocessor for `mdbook`. Its specific role is the "Ingestion Layer"—transforming raw AI-generated research into production-ready `mdbook` assets.

While the current implementation is optimized for **Google Gemini Pro** (via a specific "Master Prompt"), the architecture is designed to be LLM-agnostic.

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
- **Shield Stripping:** Automatically handles "shielded" content blocks (Gemini's Rust-style raw string literals).
- **Intelligent Sanitization:** 
    - Enforces a word-limit for H1 titles (e.g., 5 words).
    - **Smart Truncation:** Automatically avoids ending titles on prepositions or conjunctions.
- **Footnote Hardening:** 
    - **Aggregation:** Automatically combines multiple sources sharing the same index into a single, comprehensive footnote.
    - **Validation:** Identifies and flags missing bibliography entries in the text.
    - **Clickability:** Strips backticks from source URLs to ensure they render as clickable Markdown links.
- **Unicode Sanitization:** Strips invisible control characters and hidden artifacts.

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

## 🛠️ Prerequisites & Installation

### 1. System Dependencies
Before installing the preprocessor, ensure you have the following tools installed and available in your `PATH`:

*   **Rust & Cargo:** [Install Rust](https://www.rust-lang.org/tools/install)
*   **mdbook:** `cargo install mdbook`
*   **mdbook-katex:** `cargo install mdbook-katex` (Required for math rendering validation)

### 2. Build & Install
```bash
# Clone the repository
git clone <repo-url>
cd mdIngest

# Build the binary
cargo build --release

# (Optional) Install to your cargo bin path
cargo install --path .
```

## 🚀 Usage

```bash
# Ingest text (strips shield, sanitizes markdown)
./target/release/mdbook-ingest --text --number 240

# Ingest media (migrates cover art, injects widgets)
./target/release/mdbook-ingest --image --number 240
```

---

## ⚖️ License
MIT License.
