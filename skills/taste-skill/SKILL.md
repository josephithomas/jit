---
name: taste-skill
description: >-
  Gives coding agents real design taste: art direction, reference images, browser
  verification, and anti-generic landing-page rules so they produce professional,
  company-grade websites instead of AI-slop templates.
license: MIT
source: https://github.com/Leonxlnx/taste-skill
compatibility: Claude Code, Codex, Cursor, and other agents supporting skills / plugins
metadata:
  grok:
    tags: [design taste, anti-slop, art direction, UI, website design, taste]
    related_skills: [impeccable, ponytail]
---

# Taste Skill

Agent skill that forces professional design quality (figma.com / x.ai level) instead of generic AI-generated landing pages.

## When to Activate

- Building or redesigning websites, landing pages, or product UIs
- User complains about "AI slop", generic layouts, or lack of visual taste
- Need art direction, real photography/reference handling, or browser-based design checks

## Core Powers

- Art direction and design-system enforcement (one system, equal edges, section-per-screen)
- Real photographs / licensed stand-ins and real brand/product UI preference
- Browser checker + finish gate that verifies rules before shipping
- Quiet micro-interactions, controlled motion, hero entrances
- Explicit rules against repetitive template layouts

## Quick Activation

```bash
# Follow upstream install instructions
curl -fsSL https://raw.githubusercontent.com/Leonxlnx/taste-skill/main/install.sh | sh
# or clone and point agent at the skills/
git clone https://github.com/Leonxlnx/taste-skill.git
```

## Operating Rules for This Workspace

1. Activate automatically on any UI / website / landing-page task.
2. Pair with `impeccable` for critique vocabulary and `ponytail` for YAGNI restraint.
3. Prefer real visual references and browser verification over pure generation.

## Source

https://github.com/Leonxlnx/taste-skill
