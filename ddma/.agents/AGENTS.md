# Roles and Responsibilities

This document defines the roles, responsibilities, and operational guidelines for the **DeepDive Media Automator (DDMA)** project workflow.

## 🎯 Project Paradigm: Progressive Media Production
DDMA is NOT a clip cutter. It is a progressive workflow engine that transforms raw audio recordings into fully-produced baseline podcast episodes and social promotional videos:
1. **Raw Audio Input**: Ingests multi-hour raw, unedited recordings.
2. **Storyboarding & Music stings**: Segments high-engagement topics, applies targeted music ducking/crossfading, and handles sample-accurate cutting.
3. **The Baseline Audio Podcast**: Combines the curated clips chronologically to create a high-value, condensed podcast episode. E.g., [Episode 244 on Spotify](https://open.spotify.com/episode/1KKvm3TbYgxgsffHMj5MwJ?si=NeKNaPJ9QQG11-zcNB92Nw) was progressively compiled from a 63-minute raw track into a 40-minute published master.
4. **The Baseline Video Episode**: Joins all clips with 5-second curiosity question slide transitions, producing the final long-form video baseline for YouTube publishing.
5. **Micro-Promotional Clips**: Individual segments serve as vertical video assets (TikTok, Instagram Reels, YouTube Shorts) to build anticipation and promote the main episode launch.

---

## 👥 Roles & Responsibilities

### 🧑‍💻 The User (Content Creator & Human Director)
*   **Audio Source**: Responsible for providing raw audio files (e.g., from NotebookLM).
*   **Intuitive Verification**: Responsible for verifying the output clips and videos from a human aesthetic and intuition standpoint (e.g., listening for cut quality, verifying word boundary transitions).
*   **Guidance & Steering**: Provides feedback, direction, and creative suggestions to refine clip markers or video specifications.

### 🤖 The Agent (Developer & Automated Tester)
*   **Automated Execution**: Executes commands in the background on behalf of the user to transcribe, segment, and render videos.
*   **Script Iteration**: Responsible for acting as the developer/tester to build, debug, and iteratively improve the DDMA script until it is bug-free.
*   **Controlled Mode Transitions**: **CRITICAL**: Only act in "Developer" or "Tester" mode when the user explicitly requests it. Otherwise, focus on serving as the executor/orchestrator of the existing script.
*   **Muxing Focus**: Generate video assets selectively (one clip at a time) to ensure the user can focus and review without cognitive overload.
*   **Comprehensive E2E Testing & Continuous Test Bed Expansion**: Always execute both automated Puppeteer test suites (`node scratch/test-env/test_curator.js` and `node scratch/test-env/test_player.js`) after making any modifications to the curator application (`curator.html`, `run_curator.py`) or the preview player workspace (`index.html`, `player.js`, `style.css`). **MANDATORY RULE**: Whenever a new feature is added or a bug/regression is identified (e.g., input editing, volume slider changes, dropdown deduplication, clip switching, audio/video stream matching), the agent MUST expand `test_curator.js` and/or `test_player.js` to cover that exact interaction BEFORE presenting changes to the user for manual verification.

---

## 🛠️ Script Design Rules & Constraints

When developing or executing segmentation tasks, the agent must enforce the following technical constraints:
1.  **Duration Limit**: No clip may exceed **2 minutes and 55 seconds** (to prevent YouTube Shorts or Instagram Reels from rejecting them).
2.  **Sample-Accurate Slicing**: Always re-encode audio during cuts (`-c:a libmp3lame -q:a 2`) instead of stream copying to prevent word splitting at boundaries.
3.  **Selective Forward Chronology**: Identify and plan high-engagement thematic concepts in forward chronological order (no requirement to cover the entire timeline sequentially). Focus on standalone clip integrity.
4.  **Dynamic Black Canvas Muxing (Mosaic Drafts)**: Automatically mux audio clips with a solid black (`0, 0, 0`) `740x740` background video generated in-memory via FFmpeg's `color` filter (no external files required). This creates the raw draft (`clips/<episode>-<num>.mp4`) for Mosaic.
5.  **Title Card Music**: Prepend title cards (typically 2 seconds) using the custom audio file `title-card-music.mp3` as the audio track instead of silent audio (`anullsrc`), ensuring audio profiles (sample rates, layouts) are correctly matched during concatenation.
6.  **Dynamic Title Card Intro Prepending**: For finished clips from Mosaic, dynamically generate a matching title card image in Python/Pillow on a charcoal background, render it as a 2-second intro matching the master's properties, and concatenate them losslessly directly to the start of the master clip:
    *   **Part 1 Exception**: The title card for Part 1 shows `EPISODE [X]` on the top line and the full episode title on the bottom line (the clip-specific title is hidden).
    *   **Part 2+ Layout**: Shows `EPISODE [X] • PART [Y]` on the top line and the clip title on the bottom line.
    *   **Multi-Line Layout**: Titles are automatically split into two balanced lines to stay inside the Instagram safe zone. If the title contains explicit `\n` characters in `plan.json`, the script splits the text exactly at those positions (e.g., to force a 3-line format).
7.  **Audio/Video Stream Duration Equalization**: Before compiling or combining video clips, always equalize their video and audio stream durations (by trimming the longer stream to match the duration of the shorter stream). This prevents cumulative audio/video desync or drift during concatenation and satisfies publishing requirements (e.g. Spotify's error regarding mismatched video/audio track lengths).
8.  **Narrative Bridge Cards**: Insert 5.0-second black transition slides containing one single bold curiosity-provoking question between clips to preserve storyboard continuity. The texts are editable under the `"bridge_text"` key in `plan.json`. Text is rendered in **Segoe UI Bold (`34px`)** in white, fully centered on a black background. The slide audio is the final 5.0s of audio extracted from the preceding clip, linearly faded out, to prevent abrupt silences.
9.  **Timebase Normalization**: When crossfading intro/outro streams using FFmpeg's `xfade`, apply `[in]settb=1/90000[out]` to both input streams to prevent timescale mismatch errors (specifically when combining Remotion-exported assets with custom PIL renders).
10. **Welcome Music Placement & Placement Restriction**: The welcome music stings (`deepDive-soft-ok.mp3` and `deepDive-strong.mp3`) contain spoken introductory vocals ("Welcome to Deep Dive!"). Because Segment 0 (the top intro sting before the hook) overlaps with the 2-second Title Card, Segment 0 MUST use pure non-vocal music stings (`Bluesy Vibes`, `Howling`, etc.) with a ~1.3s crossfade. Vocal tag stings (`deepDive-strong` / `deepDive-soft-ok`) MUST ONLY be placed as Segment 2 (the transition sting AFTER the hook and before the main body) in Clip 1 or Clip 2, avoiding awkward vocal repetitions at the very top of clips.
11. **External API & Cost Protection (Mosaic & Gemini Remix)**: Mosaic rendering and Gemini Remix operations incur external processing latency and API costs. External operations MUST NEVER be triggered automatically on input auto-saves. UI buttons for external services (`🌌 Mosaic` and `🤖 Remix`) MUST require explicit card locking (`locked === true`) so they can only be invoked intentionally after the human director has finalized the clip structure.
12. **Master Clip Reference & Specification Hook**: Before modifying, debugging, or extending clip features, the Agent MUST read and adhere to [.agents/rules/clip-dynamics.md](file:///c:/Users/ashut/OneDrive/Desktop/github/deepDive/.agents/rules/clip-dynamics.md). All code changes and automated tests (`test_curator.js`) must strictly align with the Four-Element Construct Model, content origins, safety latches, and stream duration contracts specified in that document.

---

## 🔄 The End-to-End Media Automation Pipeline

Below is the step-by-step operational workflow for processing podcast episodes, from a raw audio file to final social media clips:

### 1. Transcribe
*   **Command**: `powershell -Command "python ddma.py transcribe --audio <episode>.mp3"`
*   **Action**: Transcribes the long audio file using OpenAI Whisper (`large-v3-turbo` by default) with native word-level timestamps (`word_timestamps=True`) enabled.
*   **Output**: Creates a `transcription.json` file containing start/end timestamps for every spoken word.

### 2. Plan
*   **Action**: Analyze the transcription to find high-engagement concepts, metaphors, and logical statements. Select specific target ranges (typically between 90 and 165 seconds).
*   **Command**: `powershell -Command "python ddma.py plan --audio <episode>.mp3 --ranges '<start>-<end>, <start>-<end>'"` (or generate the `plan.json` programmatically).
*   **Output**: Generates a `plan.json` containing the curated clips with titles and snapped start/end times.

### 3. Title Curating
*   **Action**: Open `plan.json` and curate or manually refine the `"title"`, snap boundaries, and add `"bridge_text"` lists of questions for transitions.

### 4. Audio Slice
*   **Command**: `powershell -Command "python ddma.py cut --audio <episode>.mp3 --plan-file plan.json --out-dir clips"`
*   **Action**: Splits the long audio into sample-accurate MP3 clip slices using exact Whisper word timestamps (without artificial leading silence trimming). Applies EBU R128 loudness normalization (`-16 LUFS / -1.5 dB Peak`) across all output audio.
*   **Output**: Saves clips to `clips/` named with their title (e.g., `clips/243-1-Memory vs Healing Trade-off.mp3`).

### 5. Draft Mux
*   **Command**: `powershell -Command "python ddma.py mux-clip --num <clip_number>"`
*   **Action**: Merges the audio clip with a dynamically generated solid black `740x740` background video.
*   **Output**: Saves the draft video directly to `clips/<episode>-<num>.mp4` (e.g., `clips/243-1.mp4`).

### 6. Infographic Overlay (Mosaic)
*   **Action**: Import the draft `clips/<episode>-<num>.mp4` video into Mosaic to add infographics and visual graphics. Use Mosaic's timeline to trim any remaining millisecond-level room tone silence at the end to ensure the video loops seamlessly when auto-played on Instagram/TikTok.
*   **Output**: Export the finished animation, overwriting the file at `clips/<episode>-<num>.mp4`.

### 7. Add Intro
*   **Command**: `powershell -Command "python ddma.py compile-clip --num <clip_number>"`
*   **Action**: Automatically:
    1. Backs up the master clip to `clips/<episode>-<num>-original.mp4`.
    2. Loads the title and formatting from `plan.json`.
    3. Normalizes and equalizes the master clip's video and audio stream durations.
    4. Dynamically generates the title card image (with Part 1 exception, two-line wrapping, or explicit newlines).
    5. Probes the master clip properties and renders a 2-second intro matching them exactly.
    6. Losslessly concatenates the intro and normalized master clip with a 1-second crossfade (using `settb=1/90000`).
*   **Output**: Overwrites `clips/<episode>-<num>.mp4` with the final compiled video.

### 8. Combine Episode
*   **Command**: `powershell -Command "python ddma.py combine-audio --episode <num>"` (working audio-only combine; video combine is pending the workflow-4 renderer decision)
*   **Action**: Reads `plan.json` and stitches canonical continuous `.m4a` audio segments and bridge transitions.
*   **Output**: Generates unified continuous audio for the episode. Video combine pending workflow-4 renderer decision.

---

## ⚡ 1-Click Automated Episode Ingestion Pipeline

To ingest a new raw audio episode with full automated rigor:
```powershell
powershell -Command "python ddma.py ingest-episode --audio <episode_file.m4a> --episode <number> --title '<Title text>'"
```
This automated command runs the full end-to-end pipeline:
1. **Workspace Setup**: Creates `projects/episode_<num>/` directory and populates `project_info.json` with both `audio_filename` and `audio_file` metadata.
2. **Transcription**: Executes OpenAI Whisper with word-level timestamps (`word_timestamps=True`).
3. **Plan Generation**: Divides audio into 18 structural ~2-minute clips with `deepDive-soft-ok.mp3` stings for Clips 1-2 and `deepDive-main.mp3` stings for Clips 3+.
4. **Audio Cutting**: Slices clips with EBU R128 loudness normalization (`-16 LUFS / -1.5 dB Peak`).
5. **Draft Muxing & Compilation**: Muxes black canvas videos and renders 2-second Title Card Intros and 5-second Curiosity Question Outros.
6. **Preview Manifest Registration**: Appends episode entry into `docs/episodes.json` for multi-episode GitHub Pages switching.


