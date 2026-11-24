# jit

**Personal agent workspace, free-token agent framework, skills library, and educational tooling.**

This repository is the central hub for:

- Building and running **autonomous background AI agents** on free token providers
- A curated, installable **skills centre** for coding agents
- Working catalogs of agent patterns
- Educational / library utilities (OmniSort, PDF tools, Book Wishlist, Titus SkillForge)
- High-signal external harnesses (Affaan ECC, multi-agent swarms, FreeLLMAPI)

---

## Quick Navigation

| Area | Path | Purpose |
|------|------|---------|
| **Agent Framework** | [`agent_core/`](agent_core/) | Free-token background agents, failover routing, Windows `.exe` packaging |
| **Skills Centre** | [`skills/`](skills/) | Single source of truth for installable agent skills (`SKILL.md` format) |
| **Agents Catalog** | [`agents/`](agents/) | Working patterns adapted from real agent projects |
| **Affaan Powers** | [`docs/affaan-powers.md`](docs/affaan-powers.md) | ECC plugin, claude-swarm (both flavors), JARVIS — install paths only |
| **Desktop Apps** | [`apps/`](apps/) + `TitusSkillForge/` | OmniSort Pro, Professional PDF Suite, Book Wishlist, SkillForge |
| **Rules & Principles** | [`RULES.md`](RULES.md) | Standing operating principles and token economy rules |
| **Curated Agent List** | [`docs/AWESOME_AGENTS.md`](docs/AWESOME_AGENTS.md) | Large external “Awesome Agents” reference list |

---

## 1. Agent Core — Free Token Background Agents

Production-ready framework for autonomous background agents that run entirely on free provider tiers with automatic failover.

**Key features**
- **FreeLLMAPI-first** (recommended): one OpenAI-compatible gateway aggregating 87 free providers / 1,313 endpoints with smart routing
- Auto-failover across FreeLLMAPI → Groq → OpenRouter free → GitHub Models → Gemini → local Ollama
- Persistent state (JSON/SQLite) that survives reboots
- Background daemon mode + Windows standalone `.exe` packaging
- Extensible tool registry
- Official CLI integration for Claude Code, Codex, Cline, OpenCode, Cursor, Aider, and more

→ Full documentation: **[agent_core/README.md](agent_core/README.md)**

### FreeLLMAPI (vibe-coding gateway)

```bash
# Point coding agents at your FreeLLMAPI instance
npx freellmapi setup-claude --url http://localhost:3001 --api-key <key>
npx freellmapi setup-codex  --url http://localhost:3001 --api-key <key>
npx freellmapi setup-cline  --url http://localhost:3001 --api-key <key>
npx freellmapi list
```

Upstream: [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi)

---

## 2. Affaan Powers (ECC · claude-swarm · JARVIS)

Highest-leverage external harnesses. **Do not vendor the full trees** — use the official plugin / install paths so `jit` stays clean.

| Power | What you get | How |
|-------|--------------|-----|
| **ECC** | Agent harness, skills, memory, security, research-first patterns (~310k★) | Claude Code plugin: `/plugin marketplace add https://github.com/affaan-m/ECC` then `/plugin install ecc` |
| **claude-swarm (affaan-m)** | Task decomposition + parallel agents + quality gate | `git clone https://github.com/affaan-m/claude-swarm && pip install -e .` |
| **claude-swarm (PyPI)** | Session coordination, file claims, message bus | `pip install claude-swarm` |
| **JARVIS** | OSINT / autonomous scraping pipeline | Clone only when the OSINT use-case appears |

Full install commands and hygiene notes: **[docs/affaan-powers.md](docs/affaan-powers.md)**

Recommended order: **ECC first** → the swarm flavor that matches your session style → JARVIS only if needed.

---

## 3. Skills Centre

There is **one** place for skills:

```text
skills/<skill-name>/SKILL.md
```

All skills used day-to-day are installed under `skills/` so they survive machine and account switches.

**Important files**
- [`skills/SOURCES.md`](skills/SOURCES.md) — Catalog of upstream skill repositories
- [`skills/ACTIVATED_POWERS.md`](skills/ACTIVATED_POWERS.md) — Currently active capabilities
- [`skills/CENTRE.md`](skills/CENTRE.md) — Single-source rule

Standing integrations include free-claude-code, Skills-Manager, vibe-security-skill, agent-rules-books, essential-claude-skills, taste-skill, and many curated collections.

---

## 4. Agents Catalog

Working agent implementations and patterns catalogued from high-quality public projects (including the 500-AI-Agents-Projects collection).

Also references notable self-hosted multi-bot systems such as **Superbot** (open-source Grok Bot alternative, forked at [josephithomas/superbot](https://github.com/josephithomas/superbot)).

→ See [`agents/README.md`](agents/README.md)

---

## 5. Desktop Apps (Educational & Library Tools)

Each app is self-contained under `apps/<name>/` with its own `requirements.txt` and its own build files (PyInstaller `.spec`, Inno Setup `.iss`, `.bat` scripts). Build scripts resolve paths relative to their own folder, so run them from inside the app folder.

| App | Folder | Stack | Run |
|-----|--------|-------|-----|
| **Titus OmniSort Pro** — file/folder sorting, duplicate finder, rules, undo | [`apps/omnisort/`](apps/omnisort/) | PyQt6 | `pip install -r apps/omnisort/requirements.txt && cd apps/omnisort && python run_sorter.py` |
| **TSTC Professional PDF Suite** — PDF editing, OCR, conversion, AI assistant | [`apps/pdf_suite/`](apps/pdf_suite/) | customtkinter | `pip install -r apps/pdf_suite/requirements.txt && cd apps/pdf_suite && python App.py` |
| **Book Wishlist Pro** — book wishlist and resource management | [`apps/book_wishlist/`](apps/book_wishlist/) | tkinter | `pip install -r apps/book_wishlist/requirements.txt && cd apps/book_wishlist && python book_wishlist_app.py` |
| **Titus SkillForge** — skill creator + definition tooling | [`TitusSkillForge/`](TitusSkillForge/) | see its README | see [`TitusSkillForge/README.md`](TitusSkillForge/README.md) |

The GUI apps need a desktop session; they cannot run headless. Windows executables are built with `build_exe.bat` (PDF Suite) and `build_omnisort_release.bat` (OmniSort) from inside the app folder.

---

## 6. Operating Principles

See **[RULES.md](RULES.md)** for the full standing rules, including:

- Results & objectives above all
- GitHub space anchored to this repository
- Jurisprudential canons (necessity, proportionality, context)
- Token economy and micro-skill retention
- Vibe-coding + reverse-engineering protocol

---

## Repository Layout

```text
jit/
├── agent_core/        Free-token background agent framework (stdlib only)
├── agents/            Catalog of agent patterns
├── apps/
│   ├── omnisort/      OmniSort Pro (sorter_app/, run_sorter.py, build files)
│   ├── pdf_suite/     PDF Suite (App.py, studio_engines.py, studio_frames.py, build files)
│   └── book_wishlist/ Book Wishlist Pro (book_wishlist_app.py, setup.py, build files)
├── docs/              Guides (Affaan powers, awesome-agents list)
├── hoppscotch/        API test collection + environments (run in CI)
├── skills/            Skills centre: skills/<name>/SKILL.md
├── tests/             pytest suite (currently covers OmniSort core)
├── TitusSkillForge/   Skill creator tooling
├── AGENTS.md          Instructions for AI coding agents (CLAUDE.md points here)
├── RULES.md           Standing operating principles
└── requirements.txt   Dev/CI dependencies (pytest, flake8)
```

## Development

```bash
git clone https://github.com/josephithomas/jit.git
cd jit
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt                      # pytest + flake8

# Run the tests (stdlib only; no GUI libraries required)
pytest

# Lint exactly like CI (hard-fail on syntax errors / undefined names)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

CI (`.github/workflows/python-app.yml`) runs flake8 + pytest on every push and PR to `main`. `api-tests.yml` runs the Hoppscotch collection.

**Using this repo with an AI coding agent?** Read [`AGENTS.md`](AGENTS.md) first.

---

## License & Contribution

See [CONTRIBUTING.md](CONTRIBUTING.md).

This repository is the living workspace for agent development, skill curation, and educational tooling. Keep it clean, keep skills under `skills/`, and prefer surgical, high-signal changes.
