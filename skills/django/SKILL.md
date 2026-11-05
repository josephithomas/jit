---
name: django
description: "Production-grade full-stack web framework engineering with Django: ORM optimization, migrations, security, and caching."
license: MIT
source: https://github.com/django/django
---

# Django Engineering

Robust web applications using Django's batteries-included architecture.

## Best Practices
- **ORM Optimization**: Always use `select_related()` for ForeignKey/OneToOne and `prefetch_related()` for ManyToMany to eliminate N+1 queries.
- **Database Migrations**: Keep migrations atomic; avoid large blocking schema migrations on production tables without planning.
- **Security**: Leverage Django's built-in CSRF, clickjacking protection, secure cookie flags, and parameterized query execution.
- **Settings Architecture**: Decouple settings via environment variables (`django-environ` or `pydantic-settings`).
