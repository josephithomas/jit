---
name: impeccable
description: "Design vocabulary, aesthetic critique, and UI polish skills from Peter Bakaus. Eliminates AI-generated UI slop, enforces typographic rhythm, visual hierarchy, and cohesive design tokens."
license: MIT
source: https://github.com/pbakaus/impeccable
---

# Impeccable Design & UI Polish

Design vocabulary and critique guidelines to eliminate AI-generated UI slop.

## Anti-Slop Checkpoints
- **Typography**: Establish distinct typographic scale (display, heading, body, caption). Avoid generic system fallbacks when custom theme is intended. Respect line-height ratios (1.2 for headings, 1.5 for body).
- **Color Harmony**: Use cohesive palettes with intentional contrast (minimum 4.5:1 WCAG AA). Avoid harsh pure #000000 or saturated generic neon unless specifically stylized.
- **Spacing & Rhythm**: Use strict 4px or 8px baseline grids. Maintain proportional padding inside containers.
- **Micro-Interactions**: Provide active, hover, and focus-visible states for all interactive elements with smooth, subtle transition curves (150ms-250ms ease-out).
- **Empty & Error States**: Design helpful, informative empty states and contextual error messages instead of blank space or cryptic codes.
