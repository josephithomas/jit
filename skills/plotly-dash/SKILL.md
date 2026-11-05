---
name: plotly-dash
description: "Enterprise analytical web applications in Python using Dash, Plotly graphing libraries, and reactive callbacks."
license: MIT
source: https://github.com/plotly/dash
---

# Plotly Dash Analytics

High-performance data visualization web apps.

## Best Practices
- **Callbacks**: Use `@callback` with `Output`, `Input`, and `State`. Keep callbacks pure and fast.
- **Client-Side Callbacks**: Offload simple UI manipulations or chart filtering to browser JavaScript via `clientside_callback`.
- **Data Sharing**: Share intermediate datasets between callbacks using `dcc.Store` with memory or local storage.
