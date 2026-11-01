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

---

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
