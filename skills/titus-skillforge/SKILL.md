---
name: titus-skillforge
description: Universal SKILL.md creator that turns documents, SOPs, prompts and descriptions into production-ready agent skills for Claude, Free Claude Code (FCC), Grok, ChatGPT, Gemini and Antigravity. Use when the user wants to author, convert, validate or package a new skill.
version: 1.0.0
author: Titus Universal / Joseph I Thomas
compatibility: claude, fcc, grok, chatgpt, gemini, antigravity
metadata:
  category: tooling
  tags: [skill-creator, documentation, agent-skills, titus]
---

# Titus SkillForge

## Purpose

Create high-quality, cross-platform `SKILL.md` files from any source material and install them into the single skills centre of this repository: `skills/`.

## When to use

- User asks to turn a PDF, Word file, SOP, prompt or description into a skill
- User wants a new skill validated for Claude / Free Claude Code / Grok / ChatGPT / Gemini / Antigravity
- User wants a packaged ZIP or local install of a skill

## Single skills centre

All generated skills belong under:

```
skills/<skill-name>/SKILL.md
```

This repository (`josephithomas/jit`) is the only skills centre. Do not create parallel top-level skill trees.

## Workflow

1. Ingest source (text, PDF, DOCX, PPTX, image)
2. Synthesize structured SKILL.md (YAML frontmatter + workflow + boundaries)
3. Validate compatibility
4. Save into `skills/<name>/SKILL.md`
5. Optional: export ZIP or install to local Claude / Antigravity folders

## Free Claude Code

Skills installed for Claude also work through Free Claude Code (FCC):

https://github.com/Alishahryar1/free-claude-code

Same path: `~/.claude/skills/<name>/SKILL.md`

## Tool location in this repo

```
skills/titus-skillforge/
```

Contains the web UI, desktop app, CLI, synthesizer, validator and Windows installer scripts.
