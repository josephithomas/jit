---
name: claude-code-best-practice
description: "Comprehensive playbook from Shan Rais: skills, orchestration workflows, commands, hooks, and tactical practices for coding agents."
license: MIT
source: https://github.com/shanraisshan/claude-code-best-practice
---

# Claude Code Best Practice

Battle-tested guidelines for transition from vibe coding to agentic engineering.

## Directives
- **Plan First**: Formulate an explicit roadmap before writing code.
- **Autonomous Feedback**: Equip agents with test runners and linters to catch errors before returning to the user.
- **Context Hygiene**: Keep diffs tight; avoid loading unnecessary directories or huge build logs into active memory.
- **Error Remediation**: When a command fails, trace backwards to the environment state before re-running.
