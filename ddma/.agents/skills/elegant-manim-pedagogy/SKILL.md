---
name: elegant-manim-pedagogy
description: >-
  Use this skill whenever designing, storyboarding, coding, reviewing, or rendering
  Manim (Mathematical Animation Engine) scenes for animated courses, explainer videos,
  or masterclass modules. Ensures mathematical elegance, physical first-principles
  storytelling (the Feynman & Tristan Needham standard), avoidance of AI "Performance
  Theater", strict 1920x860 widescreen safe zone compliance, and mobile-first legibility.
---

# Elegant Manim Pedagogy & Masterclass Animation

This skill guides the creation of educational animations using **Manim Community Edition (ManimCE)**. It incorporates the insights of physicist **Vivek Karmarkar** (*"Your AI Knows Manim. It Still Doesn't Know What Makes a Proof Elegant"*), holding AI code generation to the pedagogical standards of **Richard Feynman** and **Tristan Needham**.

---

## The Core Philosophy: Escaping "Performance Theater"

Modern AI models know Manim syntax, but default to **Performance Theater**: generating busy, moving shapes, spinning gears, and floating numbers that look sophisticated on mute but fail to teach.

True pedagogical elegance is rooted in:
1. **The Feynman Standard**: Physical intuition before equations. Everyday physical analogies (faucets, trucks, furnaces, suspension bridges) anchor abstract concepts.
2. **The Needham Axiom**: *"Draw the picture first, then do the algebra."* Proofs and concepts must be visually self-evident geometric transformations.
3. **The Pen-and-Paper Test**: If an argument cannot be clearly sketched on a piece of paper in 60 seconds and understood without labels, **it must not be animated**.

Detailed reading: [The Karmarkar-Feynman-Needham Pedagogy Standard](./references/karmarkar-pedagogy-standard.md)

---

## Pre-Production Workflow: The 4 Gates

### Gate 1: The Pen-and-Paper Pre-Approval Gate
Before writing a single line of Manim Python code:
1. Group the dialogue into ~25–30 second scenes (~2 animations per minute).
2. For each scene, define:
   - **The Core Insight / "Aha!" Moment** (strictly one per scene).
   - **The Figurative Physical Metaphor** (e.g., An 18-wheeler shipping a single grain of rice on a velvet pillow).
   - **The Kinetic Transformation** (what changes state from A to B).
3. Present the storyboard table to the user for formal approval.

### Gate 2: The Module Asset Quota & Invariants
Across any course module:
- **Dynamic Slides** (data tables, code diffs, financial ledger proofs): **Strictly MAXIMUM ONE per module**. Never begin a module with a Dynamic Slide.
- **Kinetics** (mechanical multi-stage interactive physics/flows): **Exactly TWO per module**.
- **Non-Repetition**: Kinetics, Dynamic Slides, and specific analogies strictly **NEVER repeat** across the course.
- **Micro-Beats**: Within each 30s scene, structure at least 2 visual micro-beats timed to spoken syllables in the transcript.

### Gate 3: Safe Zone & Viewport Budget Enforcement
Every scene renders to a $1920 \times 860$ viewport pasted at $(0, 105)$ on the $1920 \times 1080$ master canvas:
- **Horizontal Bounds**: $x \in [-5.2, +5.2]$ (protects 35px buffer for Satosha mic at $x=220$ and Satoshi mic at $x=1700$).
- **Vertical Bounds**: $y \in [-2.3, +2.1]$ (protects top caption ribbon $y=20..95$ and bottom visualizer $y=965..1080$).
- **Top Titles**: Exactly `shift(UP * 2.4)` with `font_size=23` to `24`.
- **Card Columns**: Left card centered at `LEFT * 2.8`, Right card centered at `RIGHT * 2.8`.
- **Bottom Banner**: Centered at `DOWN * 2.2`, width $\le 8.2$.

Detailed dimensions: [1920x860 Widescreen Safe Zone Specification](./references/safe-zone-widescreen-spec.md)

### Gate 4: Technical Code Standards (ManimCE & Headless Traps)
Adhere to the best practices synthesized from `adithya-s-k/manim_skill`:
1. **Pango Fonts Only (NO `MathTex`)**: Windows and headless servers lack `latex.exe`. Always use `Text(..., font="Arial", weight=BOLD)` or `font="Consolas"`.
2. **ASCII Labels Only**: Avoid unmapped glyphs like `✔`, `💀`, `📞` or font ligatures like `->` in text strings. Use `[OK]`, `FATAL: DELAY`, or native vector geometry (`Line`, `Circle`).
3. **Color Contrast & Bold Strokes**: Cards use `stroke_width=4` on dark surfaces (`#0e1726`, `#180e14`, `#0c1e14`). Text fills must be high-contrast (`#F1F5F9`, `#86EFAC`, `#7DD3FC`, `#FDE68A`).
4. **Grouped Entrances**: Organize mobjects into `VGroup` and enter via `Create`, `FadeIn`, or `GrowArrow`.

Detailed rules: [ManimCE Technical Rules & Best Practices](./references/manimce-rules-reference.md)

---

## Production Execution Runbook

### Step 1: Scene Coding
Write modular script files in `scratch/manim_module_XX/`:
- `scenes_p1.py` (Scenes 1–10)
- `scenes_p2.py` (Scenes 11–20)
- Test single frames rapidly using:
  ```bash
  manim -s -o test_frame.png scratch/manim_module_XX/scenes_p1.py Scene01_Name
  ```

### Step 2: Batch Scene Rendering
Run headless batch compiler (`render_all.py`):
```bash
python scratch/manim_module_XX/render_all.py
```
Ensures all 20 MP4 clips are compiled into `scratch/manim_module_XX/rendered/scene_01.mp4` through `scene_20.mp4`.

### Step 3: Masterclass Bookend Compositing
Composite the final video with the Bookend Pipeline:
1. **Intro Sting**: 10.0s prepend of `deepDive-strong.mp3` (5.0s music fadeout, 3.0s visual crossfade from Course Roadmap into Scene 1).
2. **Speech Body**: Spoken dialogue with synchronized top caption ribbon, Satosha (Left) and Satoshi (Right) Yeti microphones, and 56-bar audio spectrum visualizer.
3. **Outro Sting**: 7.0s append of `deepDive-conclusion.mp3` with Course Module Closure Card.

### Step 4: Verification & Delivery
1. Generate 20-second boundary verification clips via `course_boundary_inspector.py`.
2. Deliver full module video, thumbnail, and updated `course_meta.json` to `G:/My Drive/Course_Pickup/`.
3. Check `git status` in `ddma` and `mdIngest` to verify **NO binary media files** are staged before pushing code.
