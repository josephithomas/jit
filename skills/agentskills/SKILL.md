---
name: agentskills
description: "Specification and reference documentation for the open Agent Skills standard (SKILL.md format, metadata schemas, and tool interop)."
license: MIT
source: https://github.com/agentskills/agentskills
---

# Agent Skills Standard

The universal open specification for agentic skills and modular agent behavior.

## Specification Contract
- **Frontmatter**: YAML block enclosed in `---` at the start of `SKILL.md`. Must contain `name` and `description`.
- **Triggers**: Explicit keywords or user scenarios that activate the skill.
- **Process**: Numbered, deterministic steps for executing the capability.
- **Verification**: Concrete tests, command runs, or assertions that confirm successful completion.
