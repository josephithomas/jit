# Autonomous Background Agents Framework & Free Token Engine

A production-ready, battery-included framework for building, running, and deploying **autonomous background AI agents** powered entirely by **free token providers**.

Designed specifically for standalone Windows executables (`.exe`), headless background services, and multi-platform deployment targets.

---

## 🌟 1. Massive Sources of Free Token Providers

All agents built with this framework tap into generous, zero-cost API tiers with automatic failover routing:

| Provider | Free Models Included | Free Allowance / Rate Limits | Best Use Case |
| :--- | :--- | :--- | :--- |
| **Google AI Studio (Gemini)** | `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro` | **15 RPM**, 1,000,000 TPM, 1,500 requests/day free | Complex reasoning, massive context (1M+ tokens), multimodal |
| **GroqCloud** | `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `gemma2-9b-it` | **30 RPM**, 14,400 requests/day free, 300+ tok/s | Lightning-fast background tool loops & instant responses |
| **OpenRouter Free Tier** | `deepseek/deepseek-r1:free`, `meta-llama/llama-3.3-70b-instruct:free`, `mistralai/mistral-7b:free` | **200 requests/day** on all `:free` models | Frontier reasoning (DeepSeek R1) & diverse open models |
| **GitHub Models** | `gpt-4o-mini`, `Phi-3.5-mini-instruct`, `meta-llama-3.1-70b` | **150 requests/day** free with standard GitHub PAT | Safe, OpenAI-compatible enterprise coding agents |
| **Hugging Face Serverless** | 100,000+ open-source models (Qwen, Mistral, Zephyr) | Generous community rate tier with free user token | Specialized domain agents, NLP, and code classifiers |
| **Cloudflare Workers AI** | `deepseek-r1`, `llama-3.3-70b`, `whisper` | **10,000 free neurons/day** | Serverless edge background execution |
| **Local Ollama / LLaMA.cpp** | Any local GGUF model (`llama3.2`, `qwen2.5-coder`, `mistral`) | **100% Free, infinite tokens, zero telemetry, offline** | Standalone offline Windows software |

---

## 🚀 2. Free Multi-Harness Coding Agents (via free-claude-code)

For full **Claude Code**, **Codex**, **OpenCode**, **Cline**, **Pi**, **Aider**, **Antigravity**, **VS Code Chat**, and other coding harnesses running on free / low-cost providers, this project now officially integrates and recommends:

**[Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code)** (FCC)

### What free-claude-code adds

- Routes any of **12+ supported harnesses** to models from **60+ providers** (free tiers, subscription, local, custom).
- **1.3B+ free tokens** availability (subject to provider limits and TOS).
- Native streaming, tool use, and interleaved thinking preserved.
- Automatic retries, rate-limit handling, concurrency control, multi-key rotation, and model/provider fallback.
- Works from terminal, desktop apps, IDE extensions, phone (Discord/Telegram + voice notes), and browser (native sessions).
- Token optimization via RTK + Headroom.
- Chat Completions ingress + native Gemini egress support.

### Quick install (macOS / Linux)

```bash
curl -fsSL "https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/install.sh" | sh
```

### Quick install (Windows PowerShell)

```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/install.ps1")))
```

After install, start the FCC server / tray app and configure a free provider (e.g. NVIDIA NIM, OpenRouter free models, or local). Then launch:

```bash
fcc-claude      # Claude Code
fcc-codex       # Codex
fcc-opencode    # OpenCode
fcc-cline       # Cline
fcc-pi          # Pi
# ... and other harnesses
```

FCC is complementary to the built-in `FreeAIProviderRouter` in this repo:
- Use **agent_core** free providers for lightweight background / custom agents.
- Use **free-claude-code** when you need full-featured coding harnesses (Claude Code style tool loops, IDE integration, etc.) on free tokens.

---

## 🏗️ 3. Core Framework Architecture

```
agent_core/
├── providers/
│   └── free_providers.py    # Auto-failover client across Groq, Gemini, OpenRouter, GitHub, Ollama
├── harness/
│   └── agent_daemon.py      # Background execution loop, persistent memory, tool-calling engine
├── packaging/
│   └── build_agent_exe.py   # Standalone Windows .exe compiler (headless or console)
├── templates/
│   └── sample_background_agent.py # Ready-to-deploy autonomous agent script
└── README.md                # Comprehensive documentation
```

### Key Capabilities
- **Automatic Fallback Routing**: If Groq hits a rate limit, the router immediately fails over to Gemini, then OpenRouter, then GitHub Models, then local Ollama. The agent neverhalts.
- **Persistent State**: Execution history, learned micro-skills, and goals are stored in local JSON/SQLite to survive reboots.
- **Background Daemon Mode**: Runs in a separate daemon thread without blocking host applications or freezing the OS.
- **Extensible Tool Registry**: Add custom file, network, OS, or calculation tools with a single line: `agent.register_tool(name, func)`.
- **Multi-harness free coding** (via free-claude-code integration above).

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
