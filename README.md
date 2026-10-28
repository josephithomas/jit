# JIT — Antigravity Skills

My personal Antigravity IDE skills collection, installable on any Windows machine.

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

## Custom Skills

| Skill | Description |
|-------|-------------|
| `vibecoding` | Build mood/aesthetic-driven web experiences (dreamy, cyberpunk, lofi, etc.) |

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
