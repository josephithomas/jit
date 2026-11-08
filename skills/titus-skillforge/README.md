# Titus SkillForge (skills centre entry)

**Single skills centre:** everything lives under `skills/` in this repo (`josephithomas/jit`).

This folder is both:

1. A **skill** (`SKILL.md`) that teaches agents how to create other skills
2. The **tooling** to run SkillForge (web UI, desktop app, CLI, Windows installer)

## Platforms

| Platform | Path / usage |
|----------|----------------|
| Claude | `~/.claude/skills/<name>/SKILL.md` |
| Free Claude Code | Same Claude path via [FCC](https://github.com/Alishahryar1/free-claude-code) |
| Grok | `.grok/skills/<name>/SKILL.md` |
| ChatGPT | Custom GPT instructions |
| Gemini / Antigravity | `~/.gemini/config/skills/<name>/SKILL.md` |

## Quick run

```bash
cd skills/titus-skillforge
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```

Or build Windows installer: `build_installer.bat`

## Standing rule

All skills go only into `skills/<name>/`. No second skills root.
