---
name: fastapi
description: "High-performance, async-native Python web API architecture using FastAPI, Pydantic v2, and modern dependency injection."
license: MIT
source: https://github.com/fastapi/fastapi
---

# FastAPI Architecture & Engineering

Expert guidance for high-performance Python web APIs.

## Best Practices
- **Async & Concurrency**: Use `async def` for I/O-bound endpoints (database, HTTP calls) and standard `def` with threadpool for CPU-bound tasks.
- **Pydantic v2**: Strict typing with `BaseModel`, explicit validation aliases, and granular field constraints (`Field(..., ge=0)`).
- **Dependency Injection**: Utilize `Depends()` for database sessions, authentication, and service providers to ensure testability.
- **Router Modularization**: Structure apps with `APIRouter` across distinct feature domains.
