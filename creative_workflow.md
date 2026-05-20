# DeepDive Creative Workflow

The end-to-end creative workflow for producing an episode is as follows:

1. **Drafting:** Create a write-up using Google Gemini Pro.
2. **Review & Edit:** Export the draft to Google Docs to comfortably read and make manual edits (mathematical equations render beautifully as native objects here).
3. **Pure Markdown Extraction:** Once edits are finalized, ask Gemini to output the exact final text inside a single raw Markdown code block. Copy this code block and save it as a `.md` file in your `Downloads` folder.
4. **Text Ingestion:** Run the `mdbook-ingest` CLI tool (e.g., `mdbook-ingest --text --number XXX`) to automatically ingest the file. The tool will rename it, sanitize the formatting, wrap ASCII diagrams in code blocks, protect native KaTeX, and automatically update `SUMMARY.md`.
5. **Cover Image:** Import the markdown into NotebookLM to generate a cover image, then download the image (into the `Downloads` folder). *(Image ingestion pipeline to be developed).*
6. **Initial Publication:** Use the markdown and image artifacts to publish the research on GitHub Pages via `mdbook build`.
7. **Audio Production:** Run Audio Overviews (Deep Dives) in NotebookLM to create audio files, download them, and use Audacity to edit.
8. **Podcast Syndication:** Publish the audio as a podcast on Spotify, which automatically syndicates to all other platforms via RSS feed (YouTube, Apple, Fountain, etc.).
9. **Video Generation:** YouTube automatically converts the audio feed into a video file with a static picture.
10. **Clipping:** Use YouTube's clipping tool to create 2-3 minute clips (still with a static picture).
11. **Infographics & Final Integration:** Upload the clips one-by-one to Mosaic AI Video Editor to generate infographics. These resulting video files are then placed back into the original research pages based on context via the upcoming video ingestion workflow.
