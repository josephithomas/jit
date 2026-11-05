---
name: reflex
description: "Full-stack web applications in pure Python with Reflex: reactive state management, Tailwind styling, and Next.js frontend compilation."
license: MIT
source: https://github.com/reflex-dev/reflex
---

# Reflex Full-Stack Python

Building web apps in pure Python without writing JavaScript or HTML.

## Best Practices
- **State Architecture**: Define app state subclasses of `rx.State`. Keep compute methods lightweight and leverage `@rx.var` for derived state.
- **Event Handlers**: Handle asynchronous events cleanly using async generator yields for streaming UI feedback.
- **Components**: Compose layouts using Reflex native UI primitives mapped to Radix UI and Tailwind CSS.
