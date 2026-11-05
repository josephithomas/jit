---
name: paperclip
description: "Agent management at work from Paperclip. Orchestrates multi-agent task execution, organizational workflows, worker delegation, and durable goal tracking."
license: MIT
source: https://github.com/paperclipai/paperclip
---

# Paperclip

Multi-agent coordination and workplace task governance.

## Principles
- **Role Scoping**: Explicitly assign tasks to specialized agent personas rather than a single monolithic prompt.
- **Durable Task States**: Maintain clear checkpoints for tasks: PENDING, IN_PROGRESS, REVIEW, BLOCKED, COMPLETED.
- **Human-in-the-Loop Gates**: Surface critical architectural decisions and destructive operations for explicit user approval before execution.
- **Workspace Isolation**: Run parallel worker tasks in dedicated sub-processes or isolated worktrees to avoid state collision.
