---
name: skills-manager
description: >-
  Free open-source desktop app (Tauri) that manages AI agent skills in one place
  and syncs them via symlinks to 32 coding tools (Claude Code, Codex, Cursor,
  Gemini CLI, Windsurf, Trae, and more). Includes marketplace, CLI (skm),
  translation, and granular enable/disable per tool.
license: Check upstream
source: https://github.com/jiweiyeah/Skills-Manager
compatibility: Desktop (macOS, Windows, Linux); companion CLI skm
metadata:
  grok:
    tags: [skills manager, skill sync, multi-tool, symlink, marketplace, Tauri]
    related_skills: [agentskills, agentic-awesome-skills, free-claude-code]
---

# Skills Manager

Unified desktop application for organizing, syncing, and sharing AI coding assistant skills across many tools.

Website: https://skillsmanager.freeourdays.com/

## When to Activate

- Need one place to manage skills used by multiple AI coding tools
- Want write-once, sync-everywhere (symlink-based) skill deployment
- Prefer a GUI marketplace + CLI (`skm`) workflow for skill lifecycle

## Core Powers

- Central skill storage with smart symlink (or junction/copy) sync
- Support for ~32 tools: Claude Code, Codex, Cursor, Gemini CLI, Windsurf, Trae, etc.
- Granular enable/disable per tool without deleting sources
- In-app marketplace for community skills
- AI translation of skill content
- Cross-platform native app (Tauri 2 + React); companion CLI `skm`
- Homebrew cask available on macOS

## Quick Activation

- Downloads / installers: https://github.com/jiweiyeah/Skills-Manager/releases  
  or site: https://skillsmanager.freeourdays.com/
- macOS Homebrew:
  ```bash
  brew tap jiweiyeah/tap
  brew install --cask jiweiyeah/tap/skills-manager
  ```
- Clone for reference:
  ```bash
  git clone --depth 1 https://github.com/jiweiyeah/Skills-Manager.git
  ```

## Operating Rules for This Workspace

1. Treat as a **management tool**, not a skill pack to bulk-copy into jit.
2. Do **not** vendor the app binary or full source tree into `skills/`.
3. Keep this thin SKILL.md as the activation entry; install the app separately when needed.
4. Follow full Standing Instructions in `RULES.md` on every use.

## Source

https://github.com/jiweiyeah/Skills-Manager
