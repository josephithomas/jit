---
name: vibecoding
description: >-
  Activate this skill when the user wants to "vibecode" — i.e., build something
  based on a vibe, mood, aesthetic, or feeling rather than a rigid spec.
  Use this when the user says things like "make it feel dreamy", "dark and
  cyberpunk", "lofi chill vibes", "something that feels alive", or any other
  mood/aesthetic-driven prompt. This skill guides the agent to prioritize
  creative expression, immersive design, and emotional resonance over
  traditional feature-first thinking.
---

# Vibecoding

Vibecoding is about building experiences driven by **mood, aesthetic, and
feeling** — not just functional requirements. When the user gives you a vibe,
your job is to translate that energy into code.

---

## Core Philosophy

- **Feel > Feature**: The emotional impact comes first. A button that *pulses*
  with the right energy matters more than one that merely works.
- **Immersion**: Everything — colors, fonts, sounds, motion, layout — should
  reinforce the vibe cohesively.
- **Surprise and Delight**: Add small, unexpected details that make the user
  smile or gasp. Easter eggs, parallax layers, reactive cursor trails, etc.
- **No Generic Defaults**: Never use plain white backgrounds, system fonts, or
  flat colors. Every pixel should feel intentional.

---

## Workflow

### 1. Decode the Vibe

Before writing a single line of code, interpret the user's aesthetic intent:

- **Identify the mood**: dreamy, dark, cyberpunk, cottagecore, retro, minimal,
  brutalist, glitchy, surreal, cozy, futuristic, etc.
- **Map mood to design tokens**:
  - *Cyberpunk*: neon cyan/magenta on deep black, glitch effects, monospace fonts, scanlines
  - *Dreamy*: soft lavender/blush pastels, blur/glow, serif or rounded fonts, slow floating animations
  - *Lofi/Chill*: warm amber/brown tones, grain texture, cassette aesthetic, muted palette
  - *Dark Luxury*: deep navy/charcoal + gold accents, sharp typography, subtle shimmer
  - *Retro/Y2K*: bright lime/hot pink, pixel fonts, starfield backgrounds, 3D chrome text
  - *Nature/Cottagecore*: sage greens, parchment whites, botanical motifs, handwritten fonts
  - *Glitch/Vaporwave*: RGB splits, scanlines, synthwave gradients (purple to pink to blue)
  - *Minimal Zen*: near-white or near-black, single accent color, extreme whitespace, small text

### 2. Build the Atmosphere First

Start with the *container* — the full-page background, ambient effects, and
base palette — before building any UI components:

```css
/* Example: Cyberpunk atmosphere */
body {
  background: #050510;
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(0, 255, 255, 0.05) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(255, 0, 255, 0.05) 0%, transparent 60%);
  font-family: "Share Tech Mono", monospace;
  color: #00ffcc;
}
```

Always load appropriate Google Fonts that match the vibe.

### 3. Motion and Life

Static UIs feel dead. Add motion thoughtfully:

- **Ambient animations**: Slowly drifting particles, breathing gradients,
  floating elements (infinite CSS keyframes at low speed).
- **Interaction feedback**: Hover states that glow, ripple, or shift. Click
  effects. Cursor trails for immersive themes.
- **Entrance animations**: Elements that fade, slide, or materialize in when
  the page loads. Use animation-delay to stagger them.
- **Parallax**: Subtle depth with transform or JS mousemove tracking.

```css
@keyframes breathe {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50%       { opacity: 1;   transform: scale(1.03); }
}
.ambient-orb { animation: breathe 6s ease-in-out infinite; }
```

### 4. Texture and Depth

Flat is boring. Layer these techniques:

- **Glassmorphism**: backdrop-filter: blur(12px) + semi-transparent backgrounds
- **Noise/Grain**: SVG feTurbulence filter overlay at low opacity for organic texture
- **Gradients**: Always multi-stop, never 2-color. Use conic-gradient or radial-gradient for energy.
- **Borders**: Subtle glows with box-shadow instead of hard borders.
- **Depth**: Use z-index layering with parallax or perspective for 3D feel.

### 5. Typography as Atmosphere

Font choice IS part of the vibe:

| Vibe | Google Font suggestions |
|---|---|
| Cyberpunk / Tech | Share Tech Mono, Orbitron, Space Mono |
| Dreamy / Ethereal | Playfair Display, Cormorant Garamond, Lora |
| Lofi / Retro | VT323, Press Start 2P, Special Elite |
| Luxury / Editorial | Bodoni Moda, DM Serif Display, Fraunces |
| Clean / Futuristic | Space Grotesk, Syne, Outfit, Plus Jakarta Sans |
| Handwritten / Cozy | Caveat, Pacifico, Dancing Script |

Use large display text as a design element. Headlines should feel like
posters, not labels.

### 6. Color Harmony Rules

- Use HSL for color manipulation — it is easier to stay harmonious.
- Pick one dominant color, one accent, and one neutral.
- For dark themes: background lightness < 10%, text lightness > 80%.
- Avoid pure #000000 black — use very dark hues (hsl(240, 15%, 5%)).
- Avoid pure #ffffff white — use warm or cool near-whites.
- Use opacity / alpha variants of your palette for layered depth.

### 7. Sound (Optional but Powerful)

For deeply immersive vibes, consider the Web Audio API:
- Ambient drone/pad sounds on load (looped, low volume)
- UI interaction sounds (soft clicks, whooshes)
- Always include a mute toggle — never force audio

---

## Anti-Patterns to Avoid

- Default browser fonts (Arial, Times New Roman)
- Plain white or plain black backgrounds
- Flat, colorless buttons
- Symmetric, grid-only layouts (break the grid for organic feel)
- Zero animations
- Lorem ipsum — write real, evocative placeholder copy that fits the vibe
- Stock icon libraries without customization

---

## Vibe Checklist Before Delivering

Before considering the work done, verify:

- Does the background have atmosphere? (gradient, texture, particles?)
- Are fonts loaded from Google Fonts and appropriate to the vibe?
- Do interactive elements respond with motion on hover/click?
- Is there at least one ambient/looping animation?
- Does the color palette feel cohesive and intentional?
- Is the copy (text content) evocative, not generic?
- Are there any delightful micro-details that reward exploration?

---

## Example: Translating a Vibe Prompt

**User**: "make a page that feels like walking through a dark forest at night"

**Decode**:
- Palette: deep greens (#0a1a0f), moonlight silver (#c8d8c0), mist grey
- Texture: subtle noise, layered tree silhouettes as SVG
- Motion: slow swaying animations on foreground trees, floating fireflies (dots
  with randomized drift keyframes), fog overlay that drifts horizontally
- Font: IM Fell English (eerie, old-world feel)
- Sound (optional): cricket ambience, gentle wind

Then build that atmosphere in code, layer by layer.
