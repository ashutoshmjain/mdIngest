# Manim Community Edition (ManimCE) Technical Rules & Best Practices

Synthesized from the `adithya-s-k/manim_skill` open-source skill repository and adapted for high-throughput headless course rendering.

---

## 1. Scene Structure & Configuration

Every scene class must subclass `Scene` and configure 1080p Widescreen dimensions:

```python
from manim import *
import numpy as np

config.background_color = "#080c14"
config.pixel_width = 1920
config.pixel_height = 860   # Dedicated 1920x860 graphics viewport
config.frame_rate = 25
```

---

## 2. Safe Zone & Coordinate Budget

At $1920 \times 860$ (aspect ratio $\approx 2.23:1$), the default camera frame spans $x \in [-7.11, +7.11]$ and $y \in [-3.18, +3.18]$.

To prevent collisions with:
1. Top caption ribbon ($y = 20..95$ in canvas pixels)
2. Host microphones at $x = 220$ (Satosha) and $x = 1700$ (Satoshi), $cy = 130$
3. Bottom audio visualizer and chyron tags ($y = 965..1080$)
4. Mobile phone vertical cropping on 6.1" Pixel 6a displays

**Strict Coordinate Budget**:
- **Usable Horizontal Bounds**: $x \in [-5.2, +5.2]$
- **Usable Vertical Bounds**: $y \in [-2.3, +2.1]$
- **Top Titles**: Exactly `shift(UP * 2.4)` (never lower than 2.3 to avoid box collision; never higher than 2.5 to avoid caption collision).
- **Two-Column Card Layout**:
  - Left Card: Centered at `LEFT * 2.8 + DOWN * 0.1`, width `3.8 - 4.2`, height `3.0 - 3.4`.
  - Right Card: Centered at `RIGHT * 2.8 + DOWN * 0.1`, width `3.8 - 4.2`, height `3.0 - 3.4`.
- **Bottom Summary Banner**: Centered at `DOWN * 2.2`, width $\le 8.2$, height `0.65 - 0.75`.

---

## 3. Typography & Text Invariants (The Windows / Headless Trap)

> [!CAUTION]
> **NEVER use `MathTex` or `Tex` in this environment.**
> Standard Windows headless rendering lacks a standalone `latex.exe` / `kpathsea` distribution. Calling `MathTex` will throw a fatal `FileNotFoundError: latex error converting to dvi`.

### Best Practices:
1. **Always use `Text(..., font="Arial", weight=BOLD)` or `font="Consolas"`**:
   Manim uses Pango/Cairo for `Text`, which renders natively and rapidly across all platforms without LaTeX dependencies.
2. **Avoid Font Ligature / Arrow Glyphs**:
   Do NOT use `->`, `=>`, or unmapped Unicode glyphs like `✔`, `💀`, `📞` directly in text strings. On Windows, Pango will substitute unmapped glyphs with ugly rectangular `[?]` boxes.
   - Use plain ASCII labels: `[OK]`, `FATAL: DELAY`, `VERIFIED // 0.1MS`.
   - Or draw native vector geometry: `Line(...)`, `Circle(...)`, `Arc(...)`.
3. **Multi-line Text Formatting**:
   Always set `line_spacing=1.1` to `1.2` for multi-line text blocks to prevent vertical clipping.

---

## 4. Animation Pacing & Micro-Beats

Grant Sanderson (3Blue1Brown) and Vivek Karmarkar both emphasize:
- **Spatial Anchors**: Introduce the reference container first (`Create(box)`), then populate contents (`FadeIn(contents)`), then trigger the interaction (`GrowArrow`, `Rotate`, `Flash`).
- **No Idle Time**: In a 30-second scene, structure **3 distinct micro-beats**:
  - `0.0s - 3.0s`: Establish the paradigm/problem (Left Card).
  - `3.0s - 12.0s`: Introduce the mechanism or kinetic transformation (Center/Right Card).
  - `12.0s - 25.0s`: Show the resolution, contrast, or failure mode + Bottom Banner.
- **Run Times**:
  - Entrances: `run_time=0.8` to `1.5`
  - Kinetic transforms / rotations: `run_time=1.0` to `2.0`
  - Highlighting / Flash: `run_time=0.6` to `0.8`
  - Sustained reading buffer: `self.wait(...)` to fill remaining scene allocation.

---

## 5. Grouping & Layout Management (`VGroup`)

From `adithya-s-k/manim_skill`:
- Always group related mobjects into `VGroup` before animating entrances:
  ```python
  card_group = VGroup(box, label, icon, badge, text)
  self.play(Create(card_group), run_time=1.5)
  ```
- Use `.next_to()` with explicit `buff`:
  ```python
  label.next_to(box, UP, buff=0.15)
  badge.next_to(label, DOWN, buff=0.2)
  ```
- Use `.align_to()` to maintain rigid visual axes:
  ```python
  item2.align_to(item1, LEFT)
  ```

---

## 6. Color Palette Hierarchy

Adhere strictly to the Deep Dive Masterclass Luminous Palette:
- **Background**: `#080c14` (Deep obsidian blue)
- **Container Surfaces**: `#0e1726` (Navy card), `#180e14` (Crimson card), `#0c1e14` (Emerald card), `#2b1c0a` (Amber card)
- **Primary Accents**:
  - `#00E5FF` (Radiant Cyan / Satosha)
  - `#FFD60A` (Luminous Gold / Satoshi)
  - `#22C55E` (Emerald Green / Success / Proof)
  - `#EF4444` (Vibrant Crimson / Debt / Friction / Failure)
  - `#A855F7` (Electric Violet / Metaphor / Novel Concept)
- **Stroke Widths**: Containers `stroke_width=4`, connectors/cables `stroke_width=5-6`, secondary lines `stroke_width=2`.
