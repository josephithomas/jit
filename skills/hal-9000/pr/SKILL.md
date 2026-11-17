---
name: pr
description: Use when the user wants to open a PR, rewrite a PR description, or wait for CI and merge. Fast path for GitHub PR workflow.
---

Handle the full PR lifecycle quickly:

1. Ensure the current branch is pushed (`git push -u origin HEAD` if needed).
2. Open or update the PR with `gh pr create` / `gh pr edit` using a clear title and body derived from the commits.
3. If asked to wait for CI and merge: poll status, then `gh pr merge` when green (prefer squash or the repo default).
4. Report the PR URL and final state.

Keep messages concise. Prefer the cheap model for routine PR work.
