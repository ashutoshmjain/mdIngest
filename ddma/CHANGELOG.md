# Changelog - DDMA (DeepDive Media Automator)

All notable changes to the **DDMA** open-source media automation tool will be documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and follows a **weekly release update strategy** toward a stable `v1.0.0` core engine.

---

## [0.1.0] - 2026-08-01

### 🚀 Initial Open-Source Alpha Release (`v0.1.0`)

* **Core Media Automator (`ddma.py`):** Standalone Python engine driving FFmpeg timeline demuxing, Whisper word-level transcription parsing, and symmetric music sting crossfades (`acrossfade`).
* **740x740 Square Video Standard:** Built-in rendering pipeline tuned for Nostr protocol compliance (<20 MB relay size limits), Instagram Reels, TikTok, and YouTube Shorts.
* **Curator Web UI (`curator.html`):** Browser-based curation dashboard for managing project timelines, adjusting crossfade stings, and previewing episode segments.
* **Open-Source Music Stings:** Integrated default sting library in `music/` for transition accents.
* **Architecture Decoupling:** Decoupled engine codebase from master production assets (which reside in the `deepDive` kitchen repository).

---

## 📅 Release Management & Product Roadmap

```
  v0.1.0 (Current) ➔ v0.2.0 (Weekly Hardening) ➔ ... ➔ v1.0.0 (Stable Engine) ➔ Desktop / Mobile Wrappers
```

* **v0.1.0 (Current Alpha):** Initial open-source release of core Python demuxer, Curator web UI, and FFmpeg crossfade pipeline.
* **v0.2.0 - v0.9.0 (Weekly Updates):** Continuous engine performance optimization, batch transcript processing, automated subtitle overlay styling, and preset configurations.
* **v1.0.0 (Stable Core):** Production-ready engine API for external research publishers.
* **Future Phase (v2.0+):** Native cross-platform desktop application (Windows / macOS) and mobile companion app (iOS / Android).
