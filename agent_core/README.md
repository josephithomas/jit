# Autonomous Background Agents Framework & Free Token Engine

A production-ready, battery-included framework for building, running, and deploying **autonomous background AI agents** powered entirely by **free token providers**.

Designed specifically for standalone Windows executables (`.exe`), headless background services, and multi-platform deployment targets.

---

## 🌟 0. FreeLLMAPI — Recommended Primary Gateway (Vibe Coding)

**[tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi)** is the preferred unified free-token layer for this repository.

- **~10.1 billion tokens/month** aggregated across free tiers  
- **87 free LLM providers** / **1,313 free model endpoints**  
- Single OpenAI-compatible `/v1` endpoint + smart routing + automatic failover  
- Encrypted key storage, usage tracking, decision models, and a rich dashboard  
- Official CLI that configures Claude Code, Codex, Cline, OpenCode, Cursor, Aider, Continue, Goose, Roo, Pi, and many more in one command

### Quick start with FreeLLMAPI

1. Install / run the gateway (Docker or desktop app — see upstream docs).
2. Point any coding agent at it:

```bash
# Claude Code
npx freellmapi setup-claude --url http://localhost:3001 --api-key <your-unified-key>

# Codex
npx freellmapi setup-codex --url http://localhost:3001 --api-key <your-unified-key>

# Cline / OpenCode / Cursor / Aider / Continue / Goose / Pi / ...
npx freellmapi setup-cline --url http://localhost:3001 --api-key <your-unified-key>
npx freellmapi setup-opencode --url http://localhost:3001 --api-key <your-unified-key>
npx freellmapi setup-cursor --url http://localhost:3001 --api-key <your-unified-key>
npx freellmapi list   # see all supported tools
```

Environment variables used by this repo’s router:

| Variable | Purpose |
|----------|---------|
| `FREELLMAPI_URL` | Full chat-completions URL (default `http://localhost:3001/v1/chat/completions`) |
| `FREELLMAPI_API_KEY` | Unified API key from the FreeLLMAPI dashboard |
| `FREELLMAPI_MODEL` | Model id or `auto` (default) |

FreeLLMAPI becomes the **first** provider tried by `FreeAIProviderRouter`. Direct Groq / Gemini / OpenRouter / Ollama remain as automatic fallbacks.

Upstream: https://github.com/tashfeenahmed/freellmapi  ·  https://freellmapi.co

---

## 🌟 1. Massive Sources of Free Token Providers

All agents built with this framework tap into generous, zero-cost API tiers with automatic failover routing:

| Provider | Free Models Included | Free Allowance / Rate Limits | Best Use Case |
| :--- | :--- | :--- | :--- |
| **FreeLLMAPI (recommended)** | 1,313 endpoints from 87 providers | Aggregated free tiers (~10.1B tokens/mo) | Vibe coding, multi-harness agents, smart routing |
| **Google AI Studio (Gemini)** | `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro` | **15 RPM**, 1,000,000 TPM, 1,500 requests/day free | Complex reasoning, massive context (1M+ tokens), multimodal |
| **GroqCloud** | `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `gemma2-9b-it` | **30 RPM**, 14,400 requests/day free, 300+ tok/s | Lightning-fast background tool loops & instant responses |
| **OpenRouter Free Tier** | `deepseek/deepseek-r1:free`, `meta-llama/llama-3.3-70b-instruct:free`, `mistralai/mistral-7b:free` | **200 requests/day** on all `:free` models | Frontier reasoning (DeepSeek R1) & diverse open models |
| **GitHub Models** | `gpt-4o-mini`, `Phi-3.5-mini-instruct`, `meta-llama-3.1-70b` | **150 requests/day** free with standard GitHub PAT | Safe, OpenAI-compatible enterprise coding agents |
| **Hugging Face Serverless** | 100,000+ open-source models (Qwen, Mistral, Zephyr) | Generous community rate tier with free user token | Specialized domain agents, NLP, and code classifiers |
| **Cloudflare Workers AI** | `deepseek-r1`, `llama-3.3-70b`, `whisper` | **10,000 free neurons/day** | Serverless edge background execution |
| **Local Ollama / LLaMA.cpp** | Any local GGUF model (`llama3.2`, `qwen2.5-coder`, `mistral`) | **100% Free, infinite tokens, zero telemetry, offline** | Standalone offline Windows software |

---

## 🚀 2. Free Multi-Harness Coding Agents

### Preferred path: FreeLLMAPI CLI

Use the official FreeLLMAPI CLI (shown above) to wire Claude Code, Codex, Cline, OpenCode, Cursor, Aider, Continue, Goose, Roo Code, Pi, and others to a single free-token gateway with automatic failover.

### Complementary path: free-claude-code

For full **Claude Code**, **Codex**, **OpenCode**, **Cline**, **Pi**, **Aider**, **Antigravity**, **VS Code Chat**, and other coding harnesses, this project also integrates:

**[Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code)** (FCC)

FCC is complementary to both FreeLLMAPI and the built-in `FreeAIProviderRouter`:
- Use **FreeLLMAPI** as the unified free-tier backend (recommended).
- Use **agent_core** free providers for lightweight background / custom agents.
- Use **free-claude-code** when you want its extra harness-specific features on top of free tokens.

---

## 🏗️ 3. Core Framework Architecture

```
agent_core/
├── providers/
│   └── free_providers.py    # Auto-failover client (FreeLLMAPI first, then Groq/Gemini/…/Ollama)
├── harness/
│   └── agent_daemon.py      # Background execution loop, persistent memory, tool-calling engine
├── packaging/
│   └── build_agent_exe.py   # Standalone Windows .exe compiler (headless or console)
├── templates/
│   └── sample_background_agent.py # Ready-to-deploy autonomous agent script
└── README.md                # Comprehensive documentation
```

### Key Capabilities
- **FreeLLMAPI-first routing**: One OpenAI-compatible endpoint that already aggregates dozens of free providers.
- **Automatic Fallback Routing**: If FreeLLMAPI is unavailable, the router falls through to Groq → OpenRouter → GitHub Models → Gemini → local Ollama. The agent neverhalts.
- **Persistent State**: Execution history, learned micro-skills, and goals are stored in local JSON/SQLite to survive reboots.
- **Background Daemon Mode**: Runs in a separate daemon thread without blocking host applications or freezing the OS.
- **Extensible Tool Registry**: Add custom file, network, OS, or calculation tools with a single line: `agent.register_tool(name, func)`.
- **Multi-harness free coding** via FreeLLMAPI CLI + free-claude-code.

---

## 📦 4. Deployment Formats

### A. Standalone Windows Executable (`.exe`)
Compile any background agent into a single, portable Windows binary:

```powershell
# Build windowless silent background daemon
python agent_core/packaging/build_agent_exe.py --entry agent_core/templates/sample_background_agent.py --name "OmniWorkerAgent"

# Build interactive CLI agent (keeps console open)
python agent_core/packaging/build_agent_exe.py --entry agent_core/templates/sample_background_agent.py --name "OmniWorkerCLI" --console
```

The resulting executable in `dist/OmniWorkerAgent.exe` can run on any Windows PC without Python installed.

### B. Windows Background Service / Task Scheduler
Run the agent at system startup or on an interval:
```powershell
# Register scheduled task to run silently on login
schtasks /create /tn "OmniAgentDaemon" /tr "D:\My Software Source Codes\PDF Tool\dist\OmniWorkerAgent.exe" /sc onlogon /rl highest
```

### C. System Tray Desktop Monitor
Easily wrap the `BackgroundAgent` inside a PyQt6 / tkinter system tray icon to provide live status, desktop notifications, and pause/resume controls.

### D. Serverless / Docker Containers
Deploy the harness inside a minimal Python container with environment variables passed for zero-cost cloud runs.

---

## ⚡ 5. Quickstart Example

```python
from agent_core.harness.agent_daemon import BackgroundAgent

# 1. Initialize agent
agent = BackgroundAgent(name="DocAuditWorker", state_file="doc_audit_state.json")

# 2. Add custom business tools
def count_invoices(folder: str) -> str:
    # Custom business logic
    return f"Found 14 invoices in {folder}"

agent.register_tool("count_invoices", count_invoices)

# 3. Execute autonomous goal
result = agent.run_goal("Scan ~/Downloads for invoices and summarize total amount.")
print(result)
```
