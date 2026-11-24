# Agents Catalog

Working AI agent implementations catalogued from [ashishpatel26/500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects).

Source site: https://ashishpatel26.github.io/500-AI-Agents-Projects/

When a need matches one of these agents, adapt the pattern into a Grok-compatible skill or runnable form and keep the adapted version under this repo.

## Notable External Multi-Bot / Self-Hosted Systems

| Project | Description | Language / Stack | Local Fork | Upstream |
|---------|-------------|------------------|------------|----------|
| **Superbot** | Open-source, self-hosted Grok Bot alternative. Team of named AI Bots, each with job, memory, and real computer (screen/browser). Harness-agnostic (Claude Code, Codex, Pi adapters). Routines, bot-to-bot, approvals planned. | Rust (server + adapters), web UI | [josephithomas/superbot](https://github.com/josephithomas/superbot) | [davidondrej/superbot](https://github.com/davidondrej/superbot) |
| **ECC (Everything Claude Code)** | Agent harness: 71 specialized agents, 314+ skills, hooks, session memory, AgentShield guardrails. Works with Claude Code, Cursor, Codex, OpenCode. | Node/Shell, markdown agents | [josephithomas/ecc](https://github.com/josephithomas/ecc) | [affaan-m/ECC](https://github.com/affaan-m/ECC) |
| **Hoppscotch** | Open-source API development ecosystem (REST, GraphQL, WebSocket, SSE, Socket.IO, MQTT); web, desktop and CLI. Used by agents to design, test and document APIs while vibe coding. | TypeScript / Vue, Rust (desktop) | installed as `skills/hoppscotch/` | [hoppscotch/hoppscotch](https://github.com/hoppscotch/hoppscotch) |

Use Superbot patterns (durable bots + shared computer + memory files + harness adapters) when building persistent multi-agent teams that need computer use or long-running autonomy.

## Agent Index

| # | Agent | Framework | Industry | Difficulty | Source |
|---|-------|-----------|----------|------------|--------|
| 01 | Web Research Agent | LangGraph | General | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/01-web-research-agent) |
| 02 | Code Review Agent | LangChain | Software Dev | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/02-code-review-agent) |
| 03 | PDF Q&A Agent | LlamaIndex | Research | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/03-pdf-qa-agent) |
| 04 | SQL Query Agent | LangChain | Data | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/04-sql-query-agent) |
| 05 | Email Drafting Agent | CrewAI | Communication | ⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/05-email-drafting-agent) |
| 06 | News Summarizer Agent | LangChain | Media | ⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/06-news-summarizer-agent) |
| 07 | GitHub Issue Triager | LangGraph | DevOps | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/07-github-issue-triager) |
| 08 | Data Analysis Agent | LangChain | Analytics | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/08-data-analysis-agent) |
| 09 | Resume Parser Agent | LangChain | HR | ⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/09-resume-parser-agent) |
| 10 | Meeting Notes Agent | LangChain | Productivity | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/10-meeting-notes-agent) |
| 11 | Stock Research Agent | LangChain | Finance | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/11-stock-research-agent) |
| 12 | Travel Planner Agent | CrewAI | Travel | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/12-travel-planner-agent) |
| 13 | Customer Support Agent | LangGraph | Customer Service | ⭐⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/13-customer-support-agent) |
| 14 | Social Media Content Agent | CrewAI | Marketing | ⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/14-social-media-agent) |
| 15 | Unit Test Generator Agent | LangChain | Software Dev | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/15-unit-test-generator) |
| 16 | Documentation Writer Agent | LangChain | Software Dev | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/16-documentation-writer) |
| 17 | Recipe Recommendation Agent | LangChain | Food | ⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/17-recipe-agent) |
| 18 | Job Application Agent | CrewAI | HR | ⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/18-job-application-agent) |
| 19 | Competitive Analysis Agent | LangGraph | Business | ⭐⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/19-competitive-analysis-agent) |
| 20 | Multi-Agent Debate System | LangChain | Research | ⭐⭐⭐ | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/20-multi-agent-debate) |
| 21 | PII Sanitization Agent | — | Security / Compliance | — | [source](https://github.com/ashishpatel26/500-AI-Agents-Projects/tree/main/agents/21-pii-sanitization-agent) |

## Usage Policy (Standing Mandates Apply)

This catalog and every addition to it operate under the permanent rules in `RULES.md`:

- **GitHub Space Anchor**: All cloning, forking, hosting, and vibe-coding work stays anchored to `https://github.com/josephithomas/jit`. The Superbot fork lives at `josephithomas/superbot` and is referenced from here.
- **No full vendoring**: Do not copy entire third-party agent codebases into this repo unless actively adapting them. Superbot is referenced and forked for study; selective pattern extraction only.
- **Adaptation path**: When a need arises, pull the relevant pattern, adapt it to Grok / local tools / free-token stack, and place the adapted skill or agent under `skills/` or `agents/`.
- **Prefer SKILL.md**: Convert useful patterns into Grok-compatible `SKILL.md` format for persistence across accounts.
- **Vibe-coding + reverse-engineering protocol**: Any future extraction or adaptation of Superbot patterns (or any other external source) must follow the coding & reverse-engineering protocol in `RULES.md` and **must be audited with `skills/vibe-security-skill`** before shipping.

Last updated: 2026-11-17
