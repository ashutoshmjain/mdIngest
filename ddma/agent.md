# Configuration Management & Canonical Asset Architecture

## 📁 Source of Truth for Video & Audio Assets on GitHub

All media assets in this repository reside strictly under the src/ tree with **ZERO duplication**:

### 1. Legacy Episodes (Episodes 220 – 243) &rarr; src/vid/
- **Location**: src/vid/
- **Scope**: Contains the legacy video files generated **before** the adoption of the DDMA architecture (e.g., src/vid/220-qualia.mp4, src/vid/241-1-intro.mp4, src/vid/242-*.mp4, src/vid/243-*.mp4).
- **Usage**: Referenced directly in markdown text for legacy mdBook chapter pages.

### 2. Modern DDMA Episodes (Episodes 244+ & Future) &rarr; src/ddma/docs/episodes/<ep>/clips/
- **Location**: src/ddma/docs/episodes/<episode_number>/clips/
- **Scope**: **All new and future episodes** generated using the DDMA architecture.
- **Structure**:
  - src/ddma/docs/episodes/<ep>/plan.json (Storyboard metadata, script, timestamps, trims)
  - src/ddma/docs/episodes/<ep>/clips/<ep>-<clip_num>.mp4 (740×740 locked video/audio segments)
- **Usage**: Powers the Infographics Player, Slopcast Audio Player, and chapter video carousels on deepdive.shutri.com.

---

## 🚫 Asset Management Rules for AI Agents & Developers
1. **Zero Duplication**:
   - There is **no overlap** between src/vid/ and src/ddma/docs/episodes/.
   - Never duplicate files between src/vid/ and src/ddma/docs/episodes/.
   - Never create or track media in root ddma/clips/, ddma/docs/episodes/, uild_temp/, or scratch directories.
2. **New Episodes Standard**:
   - All new episodes MUST be placed in src/ddma/docs/episodes/<ep>/ with their plan.json and clips/ folder.
   - Do NOT add new episodes to src/vid/.
3. **Build Pipeline**:
   - 
pm run build:pwa compiles src/ &rarr; ook/ directly via mdbook build.
   - GitHub Pages serves directly from ./book.
