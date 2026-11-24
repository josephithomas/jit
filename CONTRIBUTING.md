# Contributing to jit

This is a **personal agent workspace and skills hub**, not a generic open-source library or awesome-list mirror. Contributions are welcome when they raise the signal-to-noise ratio for real agent work.

## What belongs here

- Skills in the canonical form `skills/<name>/SKILL.md`
- Working agent patterns under `agents/`
- Improvements to `agent_core/` (free-token routing, daemon, packaging)
- High-signal docs that help someone *use* the hub faster (install paths, not full vendor trees)
- Educational / library tooling that already lives in this ecosystem (OmniSort, PDF suite, Book Wishlist, Titus SkillForge)

## What does **not** belong here

- Full upstream trees of large projects (ECC, JARVIS, etc.) — document the official install path instead (see `docs/affaan-powers.md` and `RULES.md`)
- Massive binaries, installers, or build artifacts (`build/`, `dist/`, `Output/`) — they are gitignored for a reason
- Low-traction or unmaintained “awesome” entries with no clear value over what already exists
- Parallel skill trees outside `skills/`

## How to contribute

1. Prefer small, surgical PRs with a clear outcome.
2. For skills: place them under `skills/<name>/SKILL.md` and update `skills/SOURCES.md` / `skills/ACTIVATED_POWERS.md` if they are standing capabilities.
3. For Affaan-related tooling: update only `docs/affaan-powers.md` (single source of truth for install commands).
4. Run the existing CI expectations (flake8 + pytest) before pushing.
5. Follow the standing principles in [`RULES.md`](RULES.md) — results first, token economy, no bloat.

## Questions

Open an issue or PR with a concrete objective. Vague “add more agents” requests will be closed; specific, usable patterns will be merged.
