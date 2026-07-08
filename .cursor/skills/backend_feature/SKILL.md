---
name: backend-feature
description: Implements backend features with Domain, Application, Infrastructure, and API layers using use cases, repositories, DTOs, and validations. Use for REST APIs, FastAPI, Node, or similar backend work.
---

# Backend Feature

## When to use
- Tarea Developer en backend (`projects/*/api`, `src/`, etc.).
- Nuevos endpoints, casos de uso o integraciones.

## Prerequisites
- Leer `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/TASKS.md`.
- Activar rule `developer`.

## Structure
```
<backend>/
├── api/              # Routes, controllers, request/response DTOs
├── application/      # Use cases, orchestration
├── domain/           # Entities, repository interfaces, domain rules
└── infrastructure/   # DB, external services, repository impl
```

## Implementation order
1. Domain: entities, repository contracts, domain rules.
2. Application: use cases (sin dependencias de framework).
3. Infrastructure: persistence, adapters externos.
4. API: endpoints, DTOs, validación entrada, mapeo a use cases.
5. Tests por capa.

## Patterns
- **Repository** — persistencia abstracta.
- **Use Case** — lógica de aplicación.
- **DTO** — contrato HTTP; no exponer entidades de dominio directamente.
- **Adapter** — integraciones externas (pagos, email).

## Validations
- Input validation en boundary (API).
- AuthZ por rol donde aplique SPEC.
- Errores consistentes (códigos HTTP, mensajes seguros).

## Tests
- Unit: domain y use cases.
- Integration: repositories, endpoints críticos.
- Comando según stack (`pytest`, `npm test`, etc.).

## Delivery
- Actualizar `docs/TASKS.md` y `docs/CHANGELOG.md`.
