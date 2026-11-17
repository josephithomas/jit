---
name: fuck-over-engineering
description: Use when the user wants to simplify a codebase, remove unnecessary complexity, or asks what can be cut. Ranks candidates and only deletes what the user picks.
---

Your job is to surface over-engineering and help the user cut it surgically.

1. Inspect the relevant code/docs.
2. Rank candidates by impact vs. risk (high impact / low risk first).
3. Present a short prioritized list with a one-line rationale each. Do not delete anything yet.
4. Wait for the user to pick what to remove or keep.
5. Apply only the chosen cuts, with minimal, clean diffs.

Prefer deleting dead code, unused abstractions, premature generalization, and configuration that is never read. Preserve public APIs and behavior the user relies on unless they explicitly approve changing them.
