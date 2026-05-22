# DeepDive Creative Workflow

The end-to-end creative workflow for producing an episode is as follows:

1. **Drafting & Editing:** Create and refine the research report directly in the Google Gemini Pro workspace. Use the following prompt to finalize the text with the necessary formatting constraints:
   > "Please provide the final version of the report, delivered strictly according to these formatting constraints:
   > 
   > 1. Shield the Output from the Parser: Wrap the entire report inside a single Rust code block using a raw string literal wrapper (i.e. start with ```rust followed on the next line by r#" and end with "# followed by ```). This guarantees my interface compiles it strictly as a static code array, preserving raw '#' characters and '$$' math signs.
   > 2. Direct Citations: Embed precise source-id identifiers (e.g. [1, 2]) directly inline next to each claim.
   > 3. Formal Bibliography: Provide a complete, structured "References" or "Bibliography" section at the end of the report, mapping every inline citation to its exact author, paper title, year, and URL from the retrieved sources.
   > 4. LaTeX Constraint: Do not include any whitespace immediately adjacent to the '$' or '$$' math delimiters.
   > 5. Table Constraint: Use only single spaces between cell contents and the pipe '|' separators to prevent tabular rendering errors."
2. **Extraction:** Save the final raw markdown content (from the Rust code block) as a `.md` file in your `Downloads` folder.
3. **Text Ingestion:** Run the `mdbook-ingest` CLI tool (e.g., `./target/release/mdbook-ingest --text --number XXX --title "Title"`) to automatically ingest, sanitize, and index the file.
4. **Cover Image:** Import the markdown into NotebookLM to generate a cover image, then download the image (into the `Downloads` folder). *(Image ingestion pipeline to be developed).*
5. **Initial Publication:** Use the markdown and image artifacts to publish the research on GitHub Pages via `mdbook build`.
6. **Audio Production:** Run Audio Overviews (Deep Dives) in NotebookLM to create audio files, download them, and use Audacity to edit.
7. **Podcast Syndication:** Publish the audio as a podcast on Spotify, which automatically syndicates to all other platforms via RSS feed (YouTube, Apple, Fountain, etc.).
8. **Video Generation:** YouTube automatically converts the audio feed into a video file with a static picture.
9. **Clipping:** Use YouTube's clipping tool to create 2-3 minute clips (still with a static picture).
10. **Infographics & Final Integration:** Upload the clips one-by-one to Mosaic AI Video Editor to generate infographics. These resulting video files are then placed back into the original research pages based on context via the upcoming video ingestion workflow.
