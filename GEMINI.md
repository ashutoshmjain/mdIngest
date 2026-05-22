# Project GEMINI: mdIngest (Ingestion Bridge)

## **The Mission: Developer & Tester Role**
In this repository, the Gemini CLI agent is not merely a user but the **Lead Developer and Automation Tester**. Your primary goal is to iteratively harden the `mdbook-ingest` tool through real-world "episode intakes."

### **The Hardened Testing Workflow**
Whenever a manual "surgical" fix is required to deliver an episode, you must treat it as a tool failure and follow this protocol:
1.  **Root Cause Analysis (RCA):** Identify exactly why the Rust tool failed to process the asset correctly.
2.  **Harden the Code:** Implement the logic for the fix directly into the Rust codebase (`src/sanitizer.rs` or `src/main.rs`).
3.  **Retest:** Rerun the ingestion tool on the original source asset to verify that the tool now handles the case autonomously.
4.  **Validate Build:** Run `mdbook build` to ensure the changes didn't break the rendering.

## **Architectural Standards**
- **Surgical Processing:** The tool must remain a lean CLI utility.
- **The Master Key:** Use the Episode Number (`--number XXX`) as the primary key for all file renaming and indexing.
- **SUMMARY.md Sync:** The tool is responsible for maintaining the `# Recent ..` section.

## **Operational Pre-Authorization**
The following actions are pre-authorized to minimize interruptions:
- **Rust Development:** Modifying `.rs` files, adding dependencies to `Cargo.toml`, and running `cargo build`.
- **Filing Backups:** Creating `.bak` or `.tmp` files during the testing phase.
- **Build Checks:** Running `mdbook build` and `mdbook-katex`.
