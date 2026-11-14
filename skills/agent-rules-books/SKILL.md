---
name: agent-rules-books
description: >-
  AGENTS.md rules and skills for Codex, Cursor, and Claude Code, distilled from
  classic software engineering books (Clean Code, Refactoring, DDD, Pragmatic
  Programmer, Legacy Code, Release It!, etc.). Mini / nano / full versions for
  different context budgets.
license: MIT
source: https://github.com/ciembor/agent-rules-books
compatibility: Claude Code, Codex, Cursor, any agent supporting AGENTS.md / SKILL.md
metadata:
  grok:
    tags: [agent rules, books, clean code, refactoring, DDD, pragmatic programmer, legacy code]
    related_skills: [karpathy-guidelines, evergreen-dev-skills, ponytail, superpowers]
---

# Agent Rules from Programming Books

Ready-to-use rule sets and skills inspired by classic software design, architecture, refactoring, legacy code, reliability, and data-intensive systems books.

## When to Activate

- Applying book-derived engineering principles (Clean Code, Refactoring, DDD, Pragmatic Programmer, etc.)
- Need always-on or on-demand rules for Codex / Cursor / Claude Code
- Prefer distilled, tool-agnostic Markdown rules with mini/nano/full size options

## Core Powers

- Rules distilled from major engineering books (mini / nano / full variants)
- Standard SKILL.md entrypoints per book/topic
- Installable via Agent Skills CLI (`npx skills add ciembor/agent-rules-books`)
- Covers: refactoring, domain-driven design, enterprise patterns, legacy code, reliability, pragmatic practices, and more

## Quick Activation

```sh
# List available skills
npx skills add ciembor/agent-rules-books --list

# Install all
npx skills add ciembor/agent-rules-books --all

# Install one (example)
npx skills add ciembor/agent-rules-books --skill refactoring
```

Or clone and reference individual book directories / SKILL.md files as needed.

## Operating Rules for This Workspace

1. Prefer the **mini** variant for most real tasks; use **nano** only under tight context limits; keep **full** as reference.
2. Do not bulk-copy every book rule file into jit — keep this thin entry and pull specific skills on demand.
3. Pair with Karpathy guidelines, evergreen-dev-skills, and ponytail for complementary philosophy.

## Source

https://github.com/ciembor/agent-rules-books
