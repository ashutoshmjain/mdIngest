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

## 🔑 Master Ingestion Protocol 2.0 (The JSON Edition)

For maximum reliability across Gemini, Claude, and GPT-4, use the **One-Shot JSON Capsule**. It is optimized for the "3,500-word sweet spot," ensuring high-density research and a complete bibliography fit within a single response.

### 🚀 The One-Shot JSON Ingestion Capsule (Primary)
Use this as the "Final Export" command once your collaborative research is ready for publication.

```text
Deliver the final version of our research strictly as a single JSON object wrapped in a ```json code block.

JSON SCHEMA:
{
  "title": "A catchy five-word title for our paper",
  "body": "The full research text with [1] style inline citations.",
  "references": [
    { "id": 1, "text": "Full citation (Author, Title, Year, URL)" }
  ]
}

CRITICAL CONSTRAINTS:
1. SWEET SPOT CAPACITY: Target approximately 3,500 words of high-information-density narrative.
2. JSON INTEGRITY: Prioritize the completion of the "references" array and the closing "}" brace. If you approach your output limit, prioritize completing the bibliography over descriptive filler in the body.
3. LATEX/KATEX: No whitespace allowed next to '$' or '$$' math delimiters (e.g. $x+y$).
4. ASCII DIAGRAMS: Wrap all ASCII diagrams in their own code blocks (```text\n...\n```) inside the JSON body.
5. ESCAPING: Use proper JSON escaping for all internal quotes (\") and newlines (\n).
6. INDEXING: Every inline citation [1] must have a matching entry in the "references" array.
```

---

### 🛡️ The 2-Phase Fallback (For Ultra-Long Reports)
If your report exceeds 5,000 words, Gemini may truncate the JSON. Use this two-turn strategy as a fail-safe:

#### Phase 1: Research Extraction
Extract the body only, focusing on depth and inline citations.

```text
Conduct a comprehensive deep-dive report on [TOPIC]. Provide the full body with inline citations [1], [2], but DO NOT provide the bibliography or JSON yet.
```

#### Phase 2: The JSON Capsule
Package the body from Phase 1 along with the full bibliography into the JSON schema provided in the One-Shot prompt above.
```
CRITICAL PACKAGING CONSTRAINTS:
1. LATEX/KATEX: No whitespace allowed next to '$' or '$$' delimiters (e.g. $x+y$).
2. ASCII DIAGRAMS: Wrap all ASCII diagrams in their own code blocks (```text\n...\n```) inside the JSON body.
3. ESCAPING: Use proper JSON escaping for all internal quotes (\") and newlines (\n).
4. BIBLIOGRAPHY: Every inline citation [1] must have a matching entry in the "references" array.
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
