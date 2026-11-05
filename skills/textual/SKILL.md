---
name: textual
description: "Modern Terminal User Interfaces (TUI) in Python using Textual: reactive widgets, CSS layout, and asynchronous event loops."
license: MIT
source: https://github.com/Textualize/textual
---

# Textual TUI Development

Rich interactive terminal applications in pure Python.

## Best Practices
- **Reactive Attributes**: Declare UI state with `reactive()` to automatically trigger DOM updates upon value changes.
- **CSS Styling**: Keep styling cleanly organized in `.tcss` stylesheets using grid/box layouts.
- **Async Workers**: Run long-running tasks, file scanning, and network requests inside `@work` decorators to keep the UI running at 60fps.
