# The Karmarkar-Feynman-Needham Pedagogy Standard

> "Your AI Knows Manim. It Still Doesn't Know What Makes a Proof Elegant."
> — Vivek Karmarkar (Lessons from attempts at Manimizing Feynman and Needham)

---

## 1. The Core Problem: The "Performance Theater" Trap

Modern Large Language Models and AI coding agents (Claude Code, Cursor, Cline, etc.) have memorized the syntax of Manim:
- They know how to call `Create`, `Transform`, `FadeIn`, `VGroup`, `MathTex`, and coordinate transforms.
- When prompted to create an educational video, an agent will easily write 300 lines of functional Python.
- **The Result**: What Vivek Karmarkar calls **"Performance Theater"**:
  - Objects fly across the screen, glowing lines shoot between circles, numbers update rapidly, and complex camera movements pan around the canvas.
  - It looks impressive on mute for 5 seconds.
  - **Yet, a human viewer learns absolutely nothing.**
  - The motion is gratuitous; the geometry is arbitrary; the visual cognitive load obscures rather than illuminates.

---

## 2. The Two Guiding Pedagogical Giants

To escape Performance Theater, our animation engine adheres to two benchmarks of human explanatory clarity:

### A. Richard Feynman (*The Feynman Lectures on Physics*)
- **Physical Grounding First**: Feynman never started with formal algebraic equations. He started with an intuitive, physical, observable mechanism (e.g., water droplets falling into a mug, heat expanding a balloon, gears interlocking).
- **The Blackboard Test**: If you cannot sketch the argument with a piece of chalk on a rough blackboard and have an undergraduate immediately grasp the physical cause-and-effect, you do not understand it well enough.
- **Translating to Course Animation**: Every animation scene must feature a **figurative physical mechanism** (e.g., a physical power cable being unplugged leading to an offline terminal, a 3-tier cascade waterfall, a mechanical scrambler box) before any metric labels or derivations are shown.

### B. Tristan Needham (*Visual Complex Analysis* & *Visual Differential Geometry*)
- **"Draw the Picture First, Then Do the Algebra"**: Needham revolutionized mathematical exposition by showing that equations are merely symbolic bookkeeping for geometric realities.
- **Geometric Transformations as Proof**: An elegant proof is not an 8-line chain of algebraic manipulations; it is a single geometric insight—a rotation, an area equivalence, a path deformation—that makes the truth self-evident.
- **Spatial Permanence**: Elements do not randomly pop into existence or teleport across the canvas. When an object transforms, the transformation preserves the topological and spatial intuition of what is happening.

---

## 3. Pre-Production Gate: The "Pen-and-Paper Test"

Before writing a single line of Manim code, every proposed scene must pass the **Pen-and-Paper Test**:

> [!IMPORTANT]
> **The Pen-and-Paper Rule:**
> If you cannot comfortably sketch the visual proof on a single sheet of paper with a pen in 60 seconds and explain the core insight to a child without reading numbers, **reject the scene immediately**. Do not use Manim code or animation easing to mask a lack of conceptual clarity.

### The 3 Questions Every Scene Must Answer:
1. **What is the single "Aha!" moment?** (Not three concepts, strictly ONE).
2. **What is the figurative physical analogy?** (e.g., An 18-wheeler truck shipping a single grain of rice on a purple velvet cushion to explain the $0.30 credit card fee on micro-transactions).
3. **What is the kinetic state change?** What transforms from state A to state B that proves the concept?

---

## 4. The 2-Phase Separation (Architect Before Animate)

Never combine storyboarding and code generation into a single prompt:

- **Phase 1: Pedagogy & Narrative Arc (Human Approval Gate)**
  - Identify transcript word-level timestamps ($t_{start}$ to $t_{end}$).
  - Formulate the physical metaphor.
  - Write down the spatial layout (Left Card vs. Right Card vs. Kinetic Center).
  - Submit storyboard description for user review and approval.

- **Phase 2: Manim Vector Implementation**
  - Translate the approved physical metaphor into clean ManimCE geometry.
  - Strictly enforce Safe Zone coordinates ($x \in [-5.2, 5.2]$, $y \in [-2.3, 2.1]$).
  - Use high-contrast Pango fonts (no raw LaTeX compilation traps).
  - Synchronize second-level micro-beats to the spoken transcript audio.
