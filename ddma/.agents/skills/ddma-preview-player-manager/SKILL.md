---
name: ddma-preview-player-manager
description: >-
  Guidelines and specifications for managing and validating the DDMA preview player workspace. Explains asset structures, Audio vs Video timelines, and running the E2E test suite.
---

# DDMA Preview Player Manager

## Overview
This skill outlines the specifications, file structure, playback timelines, and E2E verification guidelines for the DDMA Editor's Preview player.

## Dependencies
None.

## Quick Start
To run the automated E2E test suite:
1. Ensure the curator server is running (`python scratch/run_curator.py`).
2. Navigate to the test environment directory and run the tests:
   ```bash
   node scratch/test-env/test_player.js
   ```

## Timeline Mode Rules

### 1. Video Mode Timeline
* **Sequence**: Video Clips + 5.0s Black Transition Bridge Cards (rendered dynamically with white wrapped Segoe UI text on a black canvas).
* **Audio-Only Filter**: Clips with `"audio_only": true` are **omitted/skipped** from the video timeline entirely.

### 2. Audio Mode Timeline
* **Sequence**: Clips played back-to-back with crossfades. Transition bridge cards and title card intros are **omitted/skipped**.
* **Audio-Only Filter**: Clips with `"audio_only": true` **are included** using their preview MP3 tracks.

## Core Architecture & CORS Requirements
* **Hybrid Audio Playback**: Natively unmuted HTML5 controls for Video Mode (immune to browser CORS/AudioContext locks), Web Audio API for Audio Mode (to feed the analyser node and draw the visualizer wave).
* **CORS Settings**:
  * `<video id="videoPlayer" crossorigin="anonymous">` must have the CORS attribute set.
  * The local Python HTTP server (`scratch/run_curator.py`) must send the `Access-Control-Allow-Origin: *` header for all assets.
* **Cache-Busting**: To bypass browser media caching blocks, append a query parameter (e.g. `?v=3`) to the media sources.

## Verification
* Run `node scratch/test-env/test_player.js` after making modifications.
* If a test fails, inspect the browser logs programmatically, debug, and self-heal the Javascript code.

## Common Mistakes
* **Dual-Player Swap**: Never re-introduce the background dual-player preloader swaps; it causes decoding stutters and freezing.
* **Mute State Over-ride**: Do not set `videoPlayer.muted = true` in Web Audio mode without also setting the main gain node value to `0.0` (as setting native mute blocks the stream before it gets routed).
