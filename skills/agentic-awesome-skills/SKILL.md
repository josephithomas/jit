---
name: agentic-awesome-skills
description: >-
  Massive catalog of 2,957+ installable SKILL.md playbooks for Claude Code, Codex,
  Cursor, Gemini CLI and other agents. Covers brainstorming, development, backend,
  DevOps, security, cloud, ML, and more. Includes AAS Core for local catalog discovery
  and stack composition.
license: MIT (imported skills retain original licenses)
source: https://github.com/sickn33/agentic-awesome-skills
compatibility: Claude Code, Codex, Cursor, Gemini CLI, any SKILL.md host
metadata:
  grok:
    tags: [agentic awesome skills, AAS, skill catalog, 2957 skills, multi-agent, playbooks]
    related_skills: [awesome-agent-skills, agentskills, free-claude-code]
---

# Agentic Awesome Skills (AAS)

Library of **2,957+** reusable, installable `SKILL.md` playbooks (v20.8.0).

Official site: https://aaskills.tech/

## When to Activate

- Need a specialized domain playbook (backend, security, cloud, ML, DevOps, etc.)
- Building multi-skill stacks or composing agent capabilities
- Searching the largest curated open catalog of agent skills
- Using Claude Code, Codex, Cursor, or Gemini CLI and want ready-to-install skills

## Core Powers

- 2,957+ individual skills with standard SKILL.md structure
- AAS Core: local catalog discovery, agent-owned selection, stack validation & plan preview
- Single-command install targets for major harnesses
- Categories spanning web, backend, DevOps, security, cloud platforms, ML engineering, and more
- Hosted catalog + Workbench at aaskills.tech for discovery without cloning everything

## Quick Activation / Usage

**Preferred (do not clone the whole catalog into jit):**

1. Browse / search: https://aaskills.tech/core/ or https://aaskills.tech/workbench
2. Or clone upstream only when needed:
   ```bash
   git clone --depth 1 https://github.com/sickn33/agentic-awesome-skills.git
   ```
3. Point the agent at specific skill folders or use AAS Core tooling for stack composition.

**Install notes (upstream):** see the project’s getting-started and harness-specific docs (Codex / Claude Code).
npm publishing is currently paused; use GitHub for the latest skills.

## Operating Rules for This Workspace

1. Treat this as the primary large catalog source. Do **not** bulk-copy thousands of SKILL.md files into `skills/` — that violates repository hygiene.
2. When a task needs a specialized playbook, search the upstream catalog (or aaskills.tech) and install/reference only the required skills.
3. Keep this thin SKILL.md as the permanent entry point and activation record inside jit.
4. Prefer composing small, high-signal stacks over loading the entire catalog.

## Source

https://github.com/sickn33/agentic-awesome-skills  
Catalog explorer: https://aaskills.tech/
