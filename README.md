# md-publish (The Ingestion Layer)

**md-publish** is an opinionated Rust-based ingestion engine designed for high-fidelity research publishing. It is not a generic tool; it is the foundational bridge for a specific **4-Phase Research Process** (as seen on [deepDive.shutri.com](https://deepDive.shutri.com)) that moves content from AI-native drafting (Gemini 2.0/Pro) to a production-ready `mdbook`. 

When you run `md-publish`, you aren't just fixing Markdown or adding assets—you are **publishing the episode**. The tool handles structural sanitization, media injection, and the critical **synchronization of `SUMMARY.md`**, effectively making the chapter ready for local serving (e.g., via `mdbook serve`) the moment the command finishes.

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
- **Command:** `md-publish --text XXX`
- **Actions:** 
    - Hardens KaTeX blocks (escapes `$` and fixes whitespace).
    - Enforces a 5-word title limit (Smart Truncation).
    - Re-indexes footnotes sequentially and aggregates duplicate sources.
    - Synchronizes `SUMMARY.md` and the "Recent" articles list.

### Phase 3: Media Ingestion (`--image`)
The tool migrates cover art and injects social/monetization snippets.
- **Setup:** Download your cover art (PNG/JPG) to the same downloads folder.
- **Command:** `md-publish --image XXX`
- **Actions:**
    - Migrates the latest image to `src/img/XXX.png`.
    - Injects **Spotify**, **Apple Podcasts**, and **YouTube** links immediately under the H1.
    - Injects a **Lightning (Zap) Widget** at the end of the article.

### Phase 4: Visual Ingestion (`--video`)
The tool builds a **global cinematic infographic feed** (carousel) and injects it into the chapter.
- **Setup:** Save your Mosaic SO infographics to your **downloads folder** following the naming convention `XXX-description.mp4`.
- **Command:** `md-publish --video XXX`
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
2. Direct Citations: Embed precise source-id identifiers (e.g. [1, 2]) directly inline next to each claim. Use ONLY numbers, no letters.
3. EXPLICIT & SERIALIZED BIBLIOGRAPHY: You MUST include a complete, structured "References" or "Bibliography" section at the end of the report. This is the most critical part. 
   - Every single inline citation [1], [2], etc., MUST map to a unique, full entry in the bibliography.
   - Each entry MUST include: [Index Number], Author, Title, Year, and URL.
   - DO NOT summarize or omit entries (e.g., "Citations [1-33] are in the repo"). Every reference MUST be fully written out inside the shield.
   - If the report is long, prioritize completing the bibliography over descriptive filler.
4. LaTeX Constraint: Do not include any whitespace immediately adjacent to the '$' or '$$' math delimiters. (e.g., use $x+y$ not $ x+y $).
5. Table & Footnote Constraint: For the footnote table (if used), ensure it is standard Markdown. Do not use complex KaTeX environments for tables; keep them as Markdown tables inside the shield.
6. ASCII Diagrams: For visual flowcharts or feedback loops, use clear ASCII markers (e.g., `+---+`, `===>`, `[ Box ]`). Wrap these in a separate code block IF they contain pipe characters that could confuse the Markdown table parser.
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

Configure `md-publish` by adding a section to your `book.toml`:

```toml
[preprocessor.ingest]
command = "md-publish"
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
md-publish --text 240 --title "A Catchy Five Word Title"
md-publish --image 240
md-publish --video 240
```

---

## ⚖️ License
MIT License.
