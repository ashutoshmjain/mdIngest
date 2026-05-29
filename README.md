# mdbook-ingest (The Ingestion Layer)

**mdbook-ingest** is an opinionated Rust-based ingestion engine designed for high-fidelity research publishing. It is not a generic tool; it is the foundational bridge for a specific **4-Phase Research Process** (as seen on [deepDive.shutri.com](https://deepDive.shutri.com)) that moves content from AI-native drafting (Gemini 2.0/Pro) to a production-ready `mdbook` with dense mathematics, multimedia widgets, and automated indexing.

## 🧬 The Philosophy: The Opinionated Researcher
To use this tool, the researcher must align their workflow with the **Ingestion Layer's** requirements. It automates the "last-mile" friction—KaTeX hardening, structural sanitization, and media enrichment—provided the input follows the **Master Ingestion Protocol**.

---

## 🚀 The 4-Phase Research Process

### Phase 1: Research & Export (The Gemini Protocol)
The researcher conducts deep-dive research in Gemini (latest model). To export the results, they must use the **Master Ingestion Prompt** (see below).
- **Format:** The output MUST be shielded using a Rust raw-string wrapper.
- **Save As:** Save the shielded output as a `.rs` file in your `downloads_path` (e.g., `episode_241.rs`).

### Phase 2: Text Ingestion (`--text`)
The tool strips the "Shield," sanitizes the Markdown, and prepares the chapter.
- **Command:** `mdbook-ingest --text --number XXX`
- **Actions:** 
    - Hardens KaTeX blocks (escapes `$` and fixes whitespace).
    - Enforces a 5-word title limit (Smart Truncation).
    - Re-indexes footnotes sequentially and aggregates duplicate sources.
    - Synchronizes `SUMMARY.md` and the "Recent" articles list.

### Phase 3: Media Ingestion (`--image`)
The tool migrates cover art and injects social/monetization snippets.
- **Setup:** Download your cover art (PNG/JPG) to the same downloads folder.
- **Command:** `mdbook-ingest --image --number XXX`
- **Actions:**
    - Migrates the latest image to `src/img/XXX.png`.
    - Injects **Spotify**, **Apple Podcasts**, and **YouTube** links immediately under the H1.
    - Injects a **Lightning (Zap) Widget** at the end of the article.

### Phase 4: Visual Ingestion (`--video`)
The tool builds a **global cinematic infographic feed** (carousel) and injects it into the chapter.
- **Setup:** Save your Mosaic SO infographics to your **downloads folder** following the naming convention `XXX-description.mp4`.
- **Command:** `mdbook-ingest --video --number XXX`
- **Actions:**
    - Identifies matching videos starting with `XXX-` and migrates them.
    - Rebuilds the **Global Cinematic Scroll Strip** containing ALL episodic infographics.
    - Injects the scroll strip into the Markdown file with auto-focus on the current episode's content.

---

## 🔑 The Master Ingestion Prompt
Copy and paste this prompt into Gemini to generate ingestion-ready output:

```text
Please provide the final version of the report, delivered strictly according to these formatting constraints:

1. Shield the Output from the Parser: Wrap the entire report—including the title, all sections, and the complete bibliography—inside a single Rust code block using a raw string literal wrapper (i.e. start with ```rust followed on the next line by r#" and end with "# followed by ```). This is non-negotiable for my parser.
2. Direct Citations: Embed precise source-id identifiers (e.g. [1, 2]) directly inline next to each claim.
3. Full Bibliography Inclusion: You MUST include a complete, structured "References" or "Bibliography" section at the end of the report, mapping every inline citation to its exact metadata (author, title, year, URL). This section MUST be inside the shield.
4. LaTeX Constraint: Do not include any whitespace immediately adjacent to the '$' or '$$' math delimiters.
5. Table Constraint: Use only single spaces between cell contents and the pipe '|' separators to prevent tabular rendering errors.
```

---

## ✨ Core Features

### 📖 Modular Ingestion (`--text`)
- **Shield Stripping:** Automatically handles Gemini's Rust-style raw string literals (`r#" ... "#`).
- **Footnote Hardening:** Automatically combines multiple sources sharing the same index and flags missing entries.
- **Unicode Sanitization:** Strips invisible control characters and hidden artifacts (like `\u{0332}`).
- **ASCII Conversion:** Automatically wraps ASCII diagrams in code blocks and converts grid-style tables to Markdown.

### 🖼️ Media & Socials (`--image`)
- **Master Key Migration:** Enforces naming strictly to the Episode Number.
- **Surgical Snippets:** Injects cover art and monetization widgets at precise semantic locations.

---

## ⚙️ Configuration (`book.toml`)

Configure `mdbook-ingest` by adding a section to your `book.toml`:

```toml
[preprocessor.ingest]
command = "mdbook-ingest"
# Path to your browser's default download folder
downloads_path = "/mnt/c/Users/ashut/Downloads"
# Your lightning address for the Zap widget
lightning_address = "shutosha@primal.net"
# Maximum number of words for the H1 title
title_word_limit = 5
```

---

## 🛠️ Installation

```bash
# Build and install locally
cargo build --release
cargo install --path .
```

## 🚀 Usage

```bash
# Ingest full stack (with optional title override)
mdbook-ingest --text --number 240 --title "A Catchy Five Word Title"
mdbook-ingest --image --number 240
mdbook-ingest --video --number 240
```

---

## ⚖️ License
MIT License.
