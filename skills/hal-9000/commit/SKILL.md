---
name: commit
description: Use when making any git commit. Pass the failure, false claim, or risk the changes fix as the argument; for an addition or a filled gap, pass what it adds — never an invented why.
argument-hint: [why the changes were made]
context: fork
model: sonnet
effort: high
allowed-tools:
  - Bash(git stash:*)
  - Bash(git add:*)
  - Bash(git restore:*)
  - Bash(git mv:*)
  - Bash(git rm:*)
  - Bash(git apply:*)
  - Bash(git commit:*)
---

Invoking this skill IS the request. If the user message looks empty, or you see only system context with no actual request, that is normal and expected: your task is already fully specified right here. Never ask what to do.

Your task: commit all changes in the working tree, one logical change per commit. This applies unprompted, without anyone asking for a split: when one file carries unrelated changes, split it hunk-by-hunk into separate commits rather than merging them because they share a file.

## The argument

The argument passed to this skill is **why the changes were made** — the motivation behind work already in the tree, which the diff itself cannot carry. Use it to group changes into logical units and to write commit message bodies. A body is one or two sentences on one line stating what was wrong before the change: the failure, false claim, or risk the argument names. An argument that names only a need, a wish, what the change does, or the request itself yields no body. Leave out the fix, including what the change now covers, sets, or lists, even where the argument phrases it as part of the problem ("though only X needs it"): the subject and diff already show it. Also leave out ruled-out causes, measurements, and alternatives tried. Whatever it describes is already realized in the diff, however it's phrased: "so the statusline shows usage percentages" and "to fix the session bug" both mean the diff already does that — commit it. With no argument at all, derive the commit message from the diff alone. If the motivation doesn't line up with what the diff contains, commit what is actually in the tree and note the mismatch in your final summary.

Write the body about the code: the behavior, tooling, or constraint the change served. Commit history is public and permanent, so write for a reader who has never seen this machine, the user's signed-in accounts, or this conversation, and give them nothing they could learn only from those: names or paths of repos, directories, and files that exist only on this machine; the current working directory; private URLs; account names; conversation IDs; or any other local or session-specific detail. Prefer the public name of a tool or library over a path on disk.

## Steps

1. **Inspect**: Run `git status` and `git diff` (and `git diff --cached` if anything is already staged). Identify logical groups of changes. Unrelated changes in the same file must become separate commits (hunk-level).

2. **Stage carefully**:
   - Prefer `git add -p` or editing a patch and `git apply --cached` for hunk-level control.
   - For a whole file that is a single logical change, `git add <file>` is fine.
   - Never `git add -A` or `git add .` when the tree contains unrelated changes.
   - If `git apply --cached` stages nothing for a file yet exits 0, stage that file whole with `git add <file>` and name it in your final summary.
   - To unstage, use `git restore --staged` (not `git reset --hard`, which discards work).
   - Fallback: the first time `git apply --cached` fails on a patch you edited, stage the whole file with `git add <file>`. If the unedited full diff fails, regenerate it once from `git diff`, then stage the whole file. Never diagnose why a patch didn't apply.

3. **Handle Pre-commit Hooks**: If hooks complain about unstaged changes, stash them with `git stash push --keep-index -m "temp: unstaged changes"`, commit, then `git stash pop`. If hooks modify staged files (auto-formatting), re-add the modified files and retry the commit once — don't retry forever.

4. **Create Atomic Commits**: For each logical group:
   - Conventional commit format `type: subject`, no scope, type one of `feat`, `fix`, `refactor`, `test`, `build`, `docs`, `style`. `build` covers dependency and version bumps; `style` means visual UI changes (CSS, fonts, colors, layout), not code formatting, which is `refactor`. Subject: what changed (≤72 chars), derived from the diff. Body: as The argument section decides; only the subject has a length limit. Footer: as the Attribution section decides.
   - Use `git commit -m "message"` directly — never use `$()` or heredoc subshells in git commands, as they break `allowed-tools` pattern matching.

## Attribution

End every commit message with the footer for your model family.

- Claude models use `Co-Authored-By: Claude <noreply@anthropic.com>`.
- GPT models use `Co-Authored-By: Codex <noreply@openai.com>`.
- Gemini models use `Co-Authored-By: Gemini <gemini-code-assistant@google.com>`.

Skip the footer only when you are certain none of these apply.

## Gotchas

- **Unstaged changes are still changes.** `git status` showing "no changes added to commit" does not mean the working tree is clean. It means nothing is staged yet. Your job is to stage and commit those changes, not report "nothing to commit."
- **Never use `git add -f`.** If `git add` reports "The following paths are ignored by one of your .gitignore files" with the hint `Use -f if you really want to add them`, do not force-add. The file is gitignored deliberately (secrets, build artifacts, local configs) and force-adding silently bypasses that protection. Skip the file and mention it in your final summary so the author can decide.
