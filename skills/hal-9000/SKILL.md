# vinta/hal-9000 Skills Collection

Opinionated agentic skills from Vinta Chen's HAL-9000 project, sharpened by daily use for Claude Code, Codex, and other coding agents.

Source: https://github.com/vinta/hal-9000

## Included Skills

- **commit**: Splits changes into atomic conventional commits, hunk by hunk if needed
- **pr**: Opens, rewrites, or waits for CI and merges a PR quickly
- **difference**: Quick pros/cons and "what's the difference?" answers
- **fuck-over-engineering**: Ranks what to cut in a codebase; deletes only what you pick
- **best-practices**: Searches for the recommended way and common gotchas
- **blindspot**: Turns unknown unknowns into known unknowns for exploration
- **simple-english**: Rewrites text in Global English (plain, native-sounding)
- **write-like-me**: Drafts/rewrites English prose in a specific voice
- **audit-agent-settings**: Audits Claude Code or Codex settings against latest docs
- **refactor-agents-md**: Refactors CLAUDE.md / AGENTS.md so every line earns its cost
- **refactor-memory**: Prunes stale Claude Code and Codex memories
- **refactor-skill**: Refactors a skill by simplifying it

Install originally via:
```bash
npx skills add vinta/hal-9000
# or Claude Code / Codex plugin marketplaces
```

These skills are now mirrored under `skills/hal-9000/` in josephithomas/jit for local use and reproducibility.
