# Titus SkillForge — Universal SKILL.md Creator

Convert any document, SOP, prompt, or description into a **production-ready `SKILL.md`** that works across:

| Platform | How to use |
|----------|------------|
| **Claude** (Code / Desktop) | `~/.claude/skills/<name>/SKILL.md` |
| **Free Claude Code (FCC)** | Same Claude skill path — works via FCC proxy. See [Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code) |
| **xAI Grok** | `.grok/skills/<name>/SKILL.md` |
| **ChatGPT** | Paste body into Custom GPT instructions |
| **Google Gemini** | System instructions / Antigravity skills |
| **Antigravity** | `~/.gemini/config/skills/<name>/SKILL.md` |

Generated files include proper YAML frontmatter, trigger criteria, numbered workflows, safety boundaries, input/output contracts, and error handling.

---

## Quick Start (Web UI)

```bash
cd TitusSkillForge
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://127.0.0.1:8000**

1. Paste text / upload PDF · DOCX · PPTX · image · markdown
2. (Optional) set name, category, boundary level
3. Click **⚡ Synthesize SKILL.md**
4. Validate, copy, download `.md`, or export a ready-to-distribute ZIP

---

## CLI

```bash
python cli.py --help
```

---

## Desktop App & Windows Installer

```cmd
python make_icon.py
build_installer.bat
```

Produces:
- `dist\TitusSkillForge.exe` (portable)
- `Output\TitusSkillForge-Setup-1.0.0.exe` (Windows installer)

See `BUILD_INSTALLER.md` for details.

---

## License

For educational and personal use. Titus Universal branding.
