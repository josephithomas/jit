# Affaan Powers Integration (ECC • claude-swarm • JARVIS)

No fork required. These are the practical ways to get Affaan Mustafa’s agent harness, multi-agent orchestration, and OSINT tooling into the jit ecosystem.

**Single source of truth** for install commands. Keep this file current; do not vendor the full upstream trees.

## 1. ECC (highest priority — the real powerhouse)

**What it is**: Agent harness / skills / memory / security / research-first system used with Claude Code, Cursor, Codex, OpenCode, etc. ~310k stars.

**Install (Claude Code / compatible harness)**:
```bash
/plugin marketplace add https://github.com/josephithomas/ecc
/plugin install ecc@ecc
```

Later:
```bash
/plugin update ecc@ecc
```

Official site: https://ecc.tools

This gives you the skills, instincts, memory patterns, and security tooling that map cleanly onto TitusSkillForge + agent_core workflows.

## 2. Multi-agent orchestration

Two related but distinct tools exist under similar names:

### A. affaan-m/claude-swarm (task decomposition + parallel agents + quality gate)
```bash
git clone https://github.com/affaan-m/claude-swarm
cd claude-swarm
pip install -e .
# or follow its current README for the exact entrypoint
```

### B. PyPI `claude-swarm` (session coordination, file claims, message bus, git locks)
Already installable and present in many environments:
```bash
pip install claude-swarm
claude-swarm --help
```

Use whichever matches the workflow you need that day (task swarm vs multi-session coordination).

## 3. JARVIS (specialized OSINT / autonomous scraping + glasses pipeline)
```bash
git clone https://github.com/affaan-m/JARVIS
# Follow ARCHITECTURE.md / README — FastAPI + Next.js + face recognition + browser agents
```

Less central for pure desktop agent work; useful when you need real-time person/dossier intelligence.

## Recommended order for jit users
1. Install / enable **ECC** first.
2. Add the multi-agent orchestration tool that fits your current session style.
3. Reach for JARVIS only when the OSINT use-case appears.

## Complementary free-token layer

Pair these with the free-token stack already in this repo:

- **FreeLLMAPI** (recommended primary gateway) — see `agent_core/README.md`
- **agent_core** auto-failover router (FreeLLMAPI → Groq → OpenRouter free → GitHub Models → Gemini → Ollama)
- **free-claude-code** skill under `skills/free-claude-code/` for multi-harness routing

## Repo hygiene note
We deliberately do **not** vendor the full ECC tree via subtree/submodule. It is large and the official plugin path is cleaner and stays up to date. The same applies to JARVIS.

Keep this file as the single source of truth for “how do I get Affaan’s powers into jit”.
