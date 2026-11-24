# AGENTS.md

Guidance for AI coding agents working in this repository (Claude Code, Codex, Cursor, Aider, etc.). Humans: see `README.md`.

## What this repo is
A personal agent workspace and skills hub, plus three Windows-oriented desktop apps. It is **not** a single application. Identify which part you are touching before editing.

## Layout and entry points

| Area | Path | Entry point | Notes |
|------|------|-------------|-------|
| OmniSort Pro | `apps/omnisort/` | `run_sorter.py` → `sorter_app.main:main` | PyQt6 UI in `sorter_app/ui/`, pure-Python logic in `sorter_app/core/` |
| PDF Suite | `apps/pdf_suite/` | `App.py` | `App.py` (~4k lines) + `studio_engines.py` + `studio_frames.py`. `studio_frames.py` imports `App` lazily to avoid a circular import; keep that import inside the function |
| Book Wishlist | `apps/book_wishlist/` | `book_wishlist_app.py` | Writes `wishlist_v2.json` next to the script (gitignored) |
| Agent framework | `agent_core/` | `harness/agent_daemon.py` | stdlib only; providers in `providers/`, exe packaging in `packaging/` |
| Skills | `skills/<name>/SKILL.md` | n/a | Single source of truth for skills. Do not create skill trees elsewhere |
| SkillForge | `TitusSkillForge/` | see its README | Has its own `requirements.txt` |
| Tests | `tests/` | `pytest` | Currently covers OmniSort `sorter_app.core` only |

## Commands (run from the repo root)

```bash
pip install -r requirements.txt     # pytest + flake8 (all CI needs)
pytest                              # must pass; pytest.ini sets pythonpath to . and apps/omnisort
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics   # CI hard-fail gate
```

App runtime deps are per app: `pip install -r apps/<app>/requirements.txt`. The GUI apps need a desktop session, so you cannot launch them headless. Verify GUI-adjacent changes with `python -m py_compile <file>` and by testing the non-UI logic.

## Conventions
- Python 3.10 (matches CI). Keep new core logic importable without GUI libraries so it stays testable.
- Put new tests in `tests/test_*.py`. If you add code under a new `apps/<app>/` package, add that folder to `pythonpath` in `pytest.ini`.
- Build files (`*.spec`, `*.iss`, `*.bat`) live beside their app and resolve paths relative to their own folder. Keep them there. Do not move them into a root `build/` (it is gitignored).
- Keep changes small and surgical. Match the style of the file you are editing; do not reformat the large monoliths (`App.py`, `studio_*.py`) wholesale.
- Windows-only code (`win32com`, `keyboard`, `.bat`, Inno Setup) must stay optional or guarded so imports do not fail on Linux/macOS CI.

## Do not
- Commit build output or binaries: `build/`, `dist/`, `Output/`, `*.exe`, `*.msi`, zips of upstream projects.
- Vendor full upstream repositories. Document the official install path instead (see `docs/affaan-powers.md`).
- Create backup copies like `App_backup_vN.py`. Git history is the backup.
- Hardcode API keys. Provider keys are read from environment variables (see `agent_core/README.md`).

## Known issues (pre-existing)
- `Launch_Titus_Statistical_Analytical_Package.bat` at the repo root runs `server.py`, which does not exist.
- `apps/pdf_suite/App.spec` references `titus.ico`, which is not in the repo.
- Only OmniSort core has tests; PDF Suite, Book Wishlist and `agent_core` are untested.

## Related docs
- `RULES.md`: standing operating principles for this workspace
- `CONTRIBUTING.md`: what belongs in this repo and PR expectations
- `skills/CENTRE.md`, `skills/SOURCES.md`: skills conventions
