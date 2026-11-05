---
name: pullboard
description: "Autonomous development board from Pullboard: spec-driven agents build against approved requirements, enforce testing rules, and gate merge approvals."
license: MIT
source: https://github.com/pullboard-dev/pullboard
---

# Pullboard Spec-Driven Development

Autonomous development governance and verification board.

## Workflow
1. **Approved Specifications**: Agents only execute against clearly approved user specifications.
2. **Rule Enforcement**: Code changes must adhere to project linters, formatting, and test suites.
3. **Multi-Agent Verification**: Before merging, a verification agent independently validates that the implementation matches the spec criteria.
4. **Human Quality Bar**: Final merge decisions remain under user oversight.
