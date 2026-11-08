---
name: free-claude-code
description: >-
  Route Claude Code, Codex, Pi, OpenCode, Cline, Hermes, DeepSeek Harness, Grok Build,
  Muse Code, Aider, Antigravity CLI, and VS Code Chat through a local proxy to 60+
  free, paid, subscription, and local providers. Use for free high-volume coding
  agents, multi-provider fallback, token optimization, and offline-capable agent routing.
license: AGPL-3.0
source: https://github.com/Alishahryar1/free-claude-code
compatibility: Grok agent; local install of Free Claude Code (FCC)
metadata:
  grok:
    tags: [free claude code, multi-provider, coding agent, free tokens, claude code alternative, provider router]
    related_skills: [awesome-claude-code, claude-code-best-practice, agent-core]
---

# Free Claude Code (FCC)

Independent open-source local proxy that lets any supported coding harness talk to models from dozens of providers (including large free tiers) while preserving native streaming, tool use, and interleaved thinking.

## When to Activate

- User wants **free or low-cost Claude Code / Codex-style coding agents**
- Need for **multi-provider fallback**, automatic retries, or rate-limit resilience
- Desire to route Claude Code, Codex, Aider, Cline, Antigravity CLI, Grok Build, etc. through free or local models
- Token optimization (RTK + Headroom) or high monthly free-token volume
- Local / privacy-respecting coding-agent infrastructure

## Core Powers

- **12 harnesses**: Claude Code, Codex, Pi, OpenCode, Cline, Hermes, DeepSeek Harness, Grok Build, Muse Code, Aider, Antigravity CLI, VS Code Chat
- **61 providers** (free, paid, subscription, local): NVIDIA NIM, OpenRouter free, Groq, Gemini, xAI, DeepSeek, Ollama, LM Studio, llama.cpp, and many more
- Local Admin UI for keys, model selection, fallbacks, and proxy auth
- Automatic model/provider fallback, multi-key rotation, retries, concurrency control
- Native streaming + tool use preserved
- Optional token optimizers (RTK, Headroom) for up to ~90% lower usage
- Desktop tray / menu-bar control on Windows & macOS; `fcc-server` on Linux
- OpenAI-compatible `/v1` endpoint for any Chat Completions client

## Quick Activation

```powershell
# Windows
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/install.ps1")))
```

```bash
# macOS / Linux
curl -fsSL "https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/install.sh" | sh
```

Then start the Admin UI, add at least one free provider key (e.g. NVIDIA NIM, OpenRouter free, Groq, Gemini), select a model, Apply, and launch:

```bash
fcc-claude    # or fcc-codex, fcc-grok, fcc-aider, fcc-agy, etc.
```

## Operating Rules for This Workspace

1. Prefer FCC when the user needs sustained free or multi-provider coding-agent capacity.
2. Recommend free-tier providers first (NVIDIA NIM, OpenRouter free, Groq, Gemini free tier, Ollama local) before paid keys.
3. Keep the local FCC server running for any session that routes through it.
4. Document chosen models and fallback order in the session notes when relevant.
5. Treat FCC as complementary to the existing `agent_core` free-provider failover system, not a replacement.

## Error Handling

| Failure | Response |
|---------|----------|
| Provider rate-limited / down | Automatic fallback to next model in the ordered list |
| No free key configured | Guide user to NVIDIA NIM / OpenRouter / Groq / Gemini free signup |
| Harness not connecting | Verify FCC server is up and `/v1` base URL is set correctly |

## Source

https://github.com/Alishahryar1/free-claude-code
