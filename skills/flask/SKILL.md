---
name: flask
description: "Lightweight, decoupled Python web applications using Flask, Blueprints, application factories, and clean extensions."
license: MIT
source: https://github.com/pallets/flask
---

# Flask Microframework Engineering

Minimalist, flexible web services with Flask.

## Best Practices
- **Application Factory**: Always instantiate the application inside a `create_app()` factory function for clean configuration and testing.
- **Blueprints**: Separate route handlers and static assets into modular Blueprints.
- **Context Awareness**: Understand the lifecycle of Application Context (`current_app`, `g`) vs Request Context (`request`, `session`).
