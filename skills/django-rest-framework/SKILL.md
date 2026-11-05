---
name: django-rest-framework
description: "REST API development with Django REST Framework (DRF): Serializers, ViewSets, permissions, pagination, and OpenAPI schema generation."
license: MIT
source: https://github.com/encode/django-rest-framework
---

# Django REST Framework (DRF)

Scalable web API design with DRF.

## Best Practices
- **Serializers**: Use `ModelSerializer` for CRUD and plain `Serializer` for complex domain commands. Validate field-level logic with `validate_<field>()`.
- **ViewSets & Routers**: Use `ModelViewSet` with DefaultRouter for standard resources; override `get_queryset()` and `get_serializer_class()` dynamically based on action.
- **Permissions**: Implement granular permissions with `BasePermission` (`has_permission`, `has_object_permission`).
