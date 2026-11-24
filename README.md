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
| **Educational Tools** | Root + `TitusSkillForge/` | OmniSort Pro, Professional PDF Suite, Book Wishlist, SkillForge |
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

## 5. Educational & Library Tools

| Tool | Description |
|------|-------------|
| **OmniSort Pro** | Advanced file/folder sorting and organization utilities |
| **TSTC Professional PDF Suite** | PDF tools for library and academic use |
| **Book Wishlist** | Book wishlist and resource management |
| **Titus SkillForge** | Skill creator + definition tooling |

These live primarily at the repository root and under `TitusSkillForge/`.

---

## 6. Operating Principles

See **[RULES.md](RULES.md)** for the full standing rules, including:

- Results & objectives above all
- GitHub space anchored to this repository
- Jurisprudential canons (necessity, proportionality, context)
- Token economy and micro-skill retention
- Vibe-coding + reverse-engineering protocol

---

## Development

```bash
# Clone
git clone https://github.com/josephithomas/jit.git
cd jit

# CI runs flake8 + pytest on every push to main
# See .github/workflows/python-app.yml
```

---

## License & Contribution

See [CONTRIBUTING.md](CONTRIBUTING.md).

This repository is the living workspace for agent development, skill curation, and educational tooling. Keep it clean, keep skills under `skills/`, and prefer surgical, high-signal changes.
