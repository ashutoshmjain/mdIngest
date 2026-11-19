# 1920x860 Widescreen Safe Zone & Host Layout Specification

This document defines the exact pixel and coordinate boundaries for rendering Manim scenes inside the 1920x1080 masterclass canvas.

---

## 1. Master Canvas Anatomy (1920 x 1080)

```text
+-----------------------------------------------------------------------------+ y = 0
|  TOP SPOKEN CAPTION RIBBON (y = 20 .. 90)                                  |
|  [ Word-level highlight in #FFD60A, completed in #F1F5F9, upcoming #64748B ]|
+-----------------------------------------------------------------------------+ y = 95 (Separator Line)
| [Satosha Mic]                                                [Satoshi Mic]  | y = 105 .. 160
| (x=220, cy=130)                                             (x=1700, cy=130)|
|                                                                             |
|                      MANIM GRAPHICS VIEWPORT (1920 x 860)                   |
|                        Top Titles: y_manim = UP * 2.4                       |
|         Left Card: x = -2.8                  Right Card: x = +2.8           |
|                                                                             |
|                   Bottom Banner: y_manim = DOWN * 2.2                       |
+-----------------------------------------------------------------------------+ y = 965 (Separator Line)
| [ BROADCAST ARTIFACT CHYRON ]  [ 56-BAR AUDIO VISUALIZER ]   [ 04:30/09:55] | y = 965 .. 1080
+-----------------------------------------------------------------------------+ y = 1080
```

---

## 2. Manim Viewport Mapping

The Manim rendering window is exactly $1920 \times 860$ pixels, pasted into the master canvas at `(0, 105)`.

| Canvas Region | Canvas Y-Range | Manim Local Y | Notes |
| :--- | :--- | :--- | :--- |
| **Top Ribbon** | $y \in [0, 95]$ | Above viewport | Displays word-by-word active caption |
| **Microphone Row** | $y \in [105, 175]$ | $y \approx +2.6 .. +3.1$ | Satosha ($x=220$), Satoshi ($x=1700$) |
| **Manim Title** | $y \in [180, 240]$ | $y = \text{UP} * 2.4$ | Centered horizontally ($x=960$) |
| **Main Visual Area** | $y \in [240, 850]$ | $y \in [-1.8, +1.8]$ | Cards, Kinetics, Diagrams |
| **Bottom Banner** | $y \in [850, 930]$ | $y = \text{DOWN} * 2.2$ | Summary takeaway badge |
| **Bottom Controls** | $y \in [965, 1080]$ | Below viewport | Equalizer, Chyron, Timecode |

---

## 3. Microphones Gutter Buffer

The host condenser microphones (`wsi.draw_host_avatar_nodes`) are positioned at:
- **Left**: $x = 220, cy = 130$ (Satosha, Cyan)
- **Right**: $x = 1700, cy = 130$ (Satoshi, Gold)

To prevent visual collisions:
- In Manim coordinates, $x = 220$ corresponds to $x_{manim} \approx -5.5$.
- $x = 1700$ corresponds to $x_{manim} \approx +5.5$.
- Therefore, all Manim cards MUST stay strictly within $x \in [-5.2, +5.2]$.
- This provides a generous **35-pixel safety buffer** on each side.

---

## 4. Mobile Screen Calibration (6.1" Google Pixel 6a)

When a 16:9 or 2.2:1 video is viewed on a mobile device:
1. Thin lines ($< 3\text{px}$) vanish or become jagged due to downscaling.
2. Small fonts ($< 12\text{pt}$) become unreadable scribbles.
3. Elements placed too close to the screen edge are occluded by mobile bezel radii or system status bars.

### Rules for Mobile Legibility:
- **Minimum Stroke Width**: `stroke_width=4` for cards, `stroke_width=6` for arrows/cables.
- **Minimum Font Size**:
  - Top Titles: `font_size=23` to `24`
  - Card Titles: `font_size=14` to `16`
  - Card Body / Bullet Points: `font_size=11` to `13`
  - Bottom Banner Takeaways: `font_size=11` to `12`
- **Contrast**: Text fill must be bright off-white (`#F1F5F9`) or vibrant accent (`#86EFAC`, `#7DD3FC`, `#FDE68A`). Never use dark grey on dark background.
