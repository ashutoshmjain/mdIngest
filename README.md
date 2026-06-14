# md-publish (The Ingestion Layer)

**md-publish** sits at the center of a new paradigm for deep research. 

Traditionally, research was confined to static papers in arcane archives. Today, LLMs have democratized the generation of high-fidelity information. **md-publish** transforms this raw intelligence into a multi-modal publication that can be promoted like any modern media:
- **Text:** Anchored on `mdbook` for deep, structured reading.
- **Visual:** Introduced by short-form video overviews (created with tools like [Motion](https://motion.so)) for promotion on TikTok, Instagram, and YouTube.
- **Audio:** Supplemented by audio overviews (via tools like NotebookLM) for distribution on Spotify, Apple Podcasts, and Fountain.

## The Vision
We are moving away from the "static image and text" standard of the last century. This tool prioritizes **Video-as-Cover**, allowing researchers to introduce their work through engaging infographics. It is a bridge between rigorous academic depth and the reach of modern social media.

**Live Example:** [What exactly is Immutability?](https://deepdive.shutri.com/241.html)

### Why this stack?
We use **Python** scripts for the **Packaging Phase** because LLMs are, by design, exceptionally proficient at generating and executing Python code. This ensures a seamless, high-fidelity export from the LLM. 

For the **Publishing Phase**, we use **Rust**. As the native language of the `mdbook` ecosystem, Rust is the natural choice for building a high-performance **preprocessor**. An `mdbook` preprocessor acts as an automated middleware: it intercepts the Markdown source, performs complex transformations (like our KaTeX hardening, citation re-indexing, and widget injection), and passes the refined content to the renderer. This guarantees production integrity and ensures every research paper adheres to our "Gold Standard" without manual intervention.

## Installation & Setup

### Dependencies
To build and run **md-publish**, you must have the following installed on your system:
- **Rust & Cargo:** Required to compile the utility (v1.88.0+ recommended).
- **mdbook:** The underlying publishing framework (**v0.5.3** required for current build).
- **mdbook-katex:** Required for mathematical formula rendering (**v0.10.0-alpha** or higher).
- **Specialized mdbook Crates:** The utility now leverages the modular `mdbook` 0.5 architecture:
    - `mdbook-core`
    - `mdbook-preprocessor`
    - `mdbook-markdown`
    - `mdbook-summary`
- **Python 3:** Required for executing the extraction payloads.

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ashutoshmjain/mdIngest.git
    cd mdIngest
    ```
2.  **Build the utility:**
    ```bash
    cargo build --release
    ```
3.  **Add to Path:** Copy the binary to your local bin or reference it directly:
    ```bash
    cp target/release/md-publish /usr/local/bin/
    ```

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

## The Blockchain of Knowledge Taxonomy

As a research publication scales, managing the visual taxonomy and PWA health becomes critical. `md-publish` automatically enforces a **"Blockchain of Knowledge"** structural taxonomy within `SUMMARY.md` while guaranteeing absolute **URL Permanence**.

### The Three Structural Layers

1.  **# mempool (The Catchment)**
    *   The high-entropy zone for raw research and parked episodes. 
    *   Episodes here are prefixed with an underscore (e.g., `_242.md`) and are considered volatile drafts awaiting validation.
2.  **# block template (Active Mining)**
    *   The active mining space for finalized research. 
    *   Each block is strictly governed by the **Law of 21**; once the 21st episode is confirmed, the block is locked and moved to the immutable chain.
3.  **# chain (The Ledger)**
    *   The commitment to permanence. Each link represents a verified epoch of research (e.g., **block 1**), stacked in descending order.
    *   **genesis:** The non-episodic discovery layer anchoring the chain through six absolute pillars.

### Immutability & "Cast in Stone"
To protect URL integrity, an episode is considered **"Cast in Stone"** if an associated infographic video exists in the `src/vid/` directory. Locked episodes cannot be parked or renumbered.
- Only "draft" episodes (without videos) can transition into the Parked state.


### Managing the Lifecycle (Commands)

Use the following commands from your repository root to manage episode states:

*   **List Parked Episodes:**
    ```bash
    md-publish --list-parked
    ```
    *Displays a terminal list of all currently parked episodes and their titles.*

*   **Park an Episode:**
    ```bash
    md-publish --park [EPISODE_NUMBER]
    ```
    *Performs the immutability check. If safe, renames `src/[NUM].md` to `src/_[NUM].md` and updates the indexes.*

*   **Unpark & Renumber an Episode:**
    ```bash
    md-publish --unpark [OLD_NUMBER] [NEW_NUMBER]
    ```
    *Restores the episode to the `Recent` list. It automatically renames the file and updates the H1 Markdown title inside the document.*

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

## CI/CD Integration (GitHub Actions)

Since **md-publish** is designed as a local ingestion utility, it is not intended to run in your CI environment (e.g., GitHub Actions). Running it in CI would require a full Rust build environment and would risk "pipe deadlocks" or build hangs due to the scale of the preprocessor input.

### The "Surgical Disable" Strategy
To ensure your CI builds remain stable while preserving the `[preprocessor.ingest]` configuration for local use, you should surgically remove the preprocessor section from your `book.toml` during the CI build process.

**Recommended Workflow:**
1.  **Ingest Locally:** Run `md-publish` locally to sanitize and enrich your content.
2.  **Commit Processes Assets:** Commit the resulting `src/*.md` files and the updated `SUMMARY.md`.
3.  **Disable in CI:** Update your `.github/workflows/mdbook.yml` to remove the preprocessor section before running the build command.

**GitHub Actions Snippet:**
```yaml
      - name: Build with mdBook
        run: |
          # Surgically remove the ingest preprocessor to prevent CI hangs
          sed -i '/\[preprocessor.ingest\]/,/title_word_limit = 5/d' book.toml
          mdbook build
```

This approach guarantees that the CI only publishes what you have already verified and hardened on your local machine, ensuring 100% fidelity between development and production.

---

## PWA Setup (Highly Recommended)

Transforming your `mdbook` into a Progressive Web App (PWA) provides an "app-like" experience, including offline reading, "Resume Reading" persistence, and home-screen installation.

### 1. Project Structure
Create a `pwa/` directory in your repository root to house the PWA assets:
```text
your-repo/
├── pwa/
│   ├── icons/
│   │   ├── icon-192.png
│   │   └── icon-512.png
│   ├── manifest.json
│   ├── sw-register.js
│   └── sw-src.js
├── workbox-config.js
└── package.json
```

### 2. Configuration Files

#### `pwa/manifest.json`
```json
{
  "name": "Your Book Title",
  "short_name": "Book",
  "start_url": "./index.html",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2E2E2E",
  "icons": [
    { "src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

#### `pwa/sw-register.js`
This script handles service worker registration and update notifications.
```javascript
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').then(reg => {
      reg.onupdatefound = () => {
        const installingWorker = reg.installing;
        installingWorker.onstatechange = () => {
          if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New content available! Show an update button to the user.
            showUpdateUI(reg.waiting);
          }
        };
      };
    });
  });
}

function showUpdateUI(waitingWorker) {
  const btn = document.createElement('button');
  btn.innerHTML = '✨ New Content! Update Now';
  Object.assign(btn.style, { position: 'fixed', bottom: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: '1000' });
  btn.onclick = () => {
    waitingWorker.postMessage({ type: 'SKIP_WAITING' });
    window.location.reload();
  };
  document.body.appendChild(btn);
}
```

#### `pwa/sw-src.js`
The source for your service worker, utilizing Workbox for caching strategies.
```javascript
importScripts('https://storage.googleapis.com/workbox-cdn/releases/6.4.1/workbox-sw.js');

if (workbox) {
  workbox.precaching.precacheAndRoute(self.__WB_MANIFEST || []);
  
  // Cache videos for 30 days
  workbox.routing.registerRoute(
    ({ request }) => request.destination === 'video',
    new workbox.strategies.CacheFirst({
      cacheName: 'videos',
      plugins: [
        new workbox.cacheableResponse.CacheableResponsePlugin({ statuses: [200] }),
        new workbox.rangeRequests.RangeRequestsPlugin(),
        new workbox.expiration.ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 30 * 24 * 60 * 60 }),
      ],
    })
  );
}
```

#### `workbox-config.js`
```javascript
module.exports = {
  globDirectory: "book",
  globPatterns: ["**/*.{html,js,css,png}"],
  swSrc: "pwa/sw-src.js",
  swDest: "book/sw.js",
  globIgnores: ["sw.js"]
};
```

### 3. Integrating with mdBook Theme
Copy the default `index.hbs` to your `theme/` folder and add the following to the `<head>` section:
```html
<link rel="manifest" href="manifest.json">
<script src="sw-register.js"></script>
<script>
    // Resume Reading Persistence
    (function() {
        const key = 'last-read-path';
        if (window.location.pathname.length > 5) localStorage.setItem(key, window.location.href);
        if (window.location.pathname.endsWith('/') || window.location.pathname.endsWith('index.html')) {
            const last = localStorage.getItem(key);
            if (last && last !== window.location.href) window.location.href = last;
        }
    })();
</script>
```

### 4. Build Scripts (`package.json`)
Add `workbox-cli` to your `devDependencies` and set up the build script:
```json
"scripts": {
  "build:pwa": "mdbook build && cp pwa/manifest.json pwa/sw-register.js book/ && cp -r pwa/icons book/ && workbox injectManifest workbox-config.js"
}
```

### 5. Complete GitHub Actions Workflow
This workflow automates the entire process: stripping the preprocessor, building the book, and injecting the PWA manifest.

```yaml
name: Deploy mdBook PWA

on:
  push:
    branches: [ master ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup mdBook
        uses: peaceiris/actions-mdbook@v2
        with:
          mdbook-version: '0.5.3'

      - name: Install mdbook-katex
        run: cargo install mdbook-katex --version 0.10.0-alpha

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install PWA Tools
        run: npm install -g workbox-cli && npm ci

      - name: Build PWA
        run: |
          # Disable preprocessor for CI
          sed -i '/\[preprocessor.ingest\]/,/title_word_limit = 5/d' book.toml
          npm run build:pwa

      - name: Upload Pages Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./book

  deploy:
    needs: build
    runs-on: ubuntu-latest
    permissions: { pages: write, id-token: write }
    environment: { name: github-pages }
    steps:
      - uses: actions/deploy-pages@v4
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
- **Intelligent Hierarchical Sequencing:** 
    Videos are sequenced using a "Bucket" logic:
    1.  **Priority 0:** `[Number].mp4` or `[Number]-Intro.mp4` always stays at the head.
    2.  **Priority 1 (Buckets):** Indexed files are sorted lexicographically to allow nested ranges (e.g., `241-2` comes before `241-21`, which comes before `241-3`).
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
