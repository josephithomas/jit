# JIT — Antigravity Skills & Autonomous Agent Core

My personal Antigravity IDE skills collection, installable on any Windows machine, plus the **Autonomous Background Agent Engine**.

## Install on a New Machine

Open **PowerShell** and run:

```powershell
irm https://raw.githubusercontent.com/josephithomas/jit/main/install.ps1 | iex
```

This will:
1. Install all **custom skills** from this repo (`skills/` folder)
2. Install **518+ Grok skills** from [LifeJiggy/Awesome-Grok-Skills](https://github.com/LifeJiggy/Awesome-Grok-Skills)

Skills are installed to: `%USERPROFILE%\.gemini\config\skills\`

Restart Antigravity IDE after running.

---

## Autonomous Background Agent Engine (`agent_core/`)

A production-ready framework for building **autonomous background AI agents** powered by **free token providers**:
- **Zero Token Cost**: Auto-failover across GroqCloud, Google Gemini, OpenRouter Free Tier, GitHub Models, and local Ollama.
- **Standalone Windows Executables (`.exe`)**: Single-file packaging with windowless headless mode or interactive CLI.
- **Multi-Platform Deployment**: Windows Services, Task Scheduler, System Tray daemons, and Docker containers.
- See the full guide in [`agent_core/README.md`](agent_core/README.md).

---

## Custom Skills

| Skill | Description |
|-------|-------------|
| `vibecoding` | Build mood/aesthetic-driven web experiences (dreamy, cyberpunk, lofi, etc.) |
| `reverse-engineer-anything` | Deep multi-target reverse engineering (native, .NET PE/CLI, Electron, web, runtime tracing) via REA |
| `vibe-coding` | Main vibe-coding skill — taste, flow, ship fast, feel over perfection |
| `modern-frontend` | Next.js + Tailwind + Shadcn + Framer Motion patterns for modern UIs |
| `ui-polish` | Elevate UI: spacing, hierarchy, micro-interactions, remove AI-slop |
| `indie-product` | Solo/small-team product loop — scope, ship, price, distribute |
| `workflow-composer` | Compose linear/branching workflows from goals without killing flow |
| `adaptive-workflow-composer` | Adaptive multi-step agent workflows from goals and available skills |
| `planning-with-files` | Lightweight file-based planning that stays in the coding loop |
| `code-reviewer` | Catch real bugs/security without turning into bureaucracy |
| `auto-tester` | Quick validation after rapid changes |
| `github-repo-scout` | Orient fast in a repo before you start shaping it |
| `product-requirements-document` | Light PRD when scope starts drifting |
| `goal-verifier` | Verify you actually shipped the thing you meant |

---

## Vibe Coding Pack

These skills form a practical stack for vibe coding (taste + speed + shipping):

| Skill | Role in vibe coding |
|-------|---------------------|
| `vibe-coding` | Core mode — taste, flow, ship fast |
| `modern-frontend` | Primary UI stack on Node/JS |
| `ui-polish` | Make it feel premium |
| `indie-product` | Scope and ship as a solo builder |
| `workflow-composer` / `adaptive-workflow-composer` | Multi-step plans without bureaucracy |
| `planning-with-files` | File-based plans in the loop |
| `code-reviewer` | Catch bugs/security without process theater |
| `auto-tester` | Fast validation after rapid changes |
| `github-repo-scout` | Quick orientation in a repo |
| `product-requirements-document` | Light PRD when scope drifts |
| `goal-verifier` | Confirm the goal was actually met |

## Adding New Skills

1. Create a folder under `skills/<skill-name>/`
2. Add a `SKILL.md` with YAML frontmatter:
   ```markdown
   ---
   name: my-skill
   description: >-
     When to use this skill and what it does.
   ---
   # My Skill
   ...instructions...
   ```
3. Push to GitHub — the install script auto-discovers all folders under `skills/`
