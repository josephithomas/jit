---
name: gradio
description: "Fast ML model demos, multimodal interfaces, and web UIs with Gradio Blocks and Components."
license: MIT
source: https://github.com/gradio-app/gradio
---

# Gradio Machine Learning Interfaces

Web interfaces for machine learning models and multimodal agents.

## Best Practices
- **Blocks API**: Use `gr.Blocks()` for custom layouts, multi-page apps, and complex event wiring.
- **Streaming**: Stream LLM tokens and audio waveforms with Python generators (`yield`).
- **State Management**: Use `gr.State()` to maintain per-user conversation histories across turns.
