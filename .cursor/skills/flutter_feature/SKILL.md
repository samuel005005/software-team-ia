---
name: flutter-feature
description: Implements Flutter features using Clean Architecture with Riverpod, Repository Pattern, use cases, DTOs, and dependency injection. Use when building or extending Flutter modules under lib/features/.
---

# Flutter Feature

## When to use
- Tarea Developer en `projects/*/lib/features/`.
- Nuevo módulo Flutter (auth, booking, profile, etc.).

## Prerequisites
- Leer `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/TASKS.md`.
- Activar rule `developer`.

## Structure
```
lib/features/<feature>/
├── data/
│   ├── datasources/
│   ├── models/          # DTOs
│   └── repositories/    # Repository implementations
├── domain/
│   ├── entities/
│   ├── repositories/    # Contracts (abstract)
│   └── usecases/
└── presentation/
    ├── pages/
    ├── widgets/
    └── providers/       # Riverpod
```

## Implementation order
1. Domain: entities + repository contracts + use cases.
2. Data: DTOs, datasources (API/local), repository impl.
3. Presentation: providers, pages, widgets.
4. Wire DI via Riverpod providers in `core/` or feature `providers/`.
5. Register routes in `app/router/` (GoRouter).

## Patterns
- **Repository** — abstrae fuentes de datos.
- **Use Case** — una acción de negocio por clase.
- **DTO** — serialización API; mapper a entity.
- **Riverpod** — DI y estado.

## Prohibitions
- No API calls desde widgets.
- No lógica de negocio en UI.
- No librerías no aprobadas en ARCHITECTURE.

## Tests
- Unit: use cases, mappers, repositories (mock datasource).
- Widget: páginas críticas con `ProviderScope`.
- Comandos: `flutter analyze`, `flutter test`.

## Delivery
- Actualizar `docs/TASKS.md` y `docs/CHANGELOG.md`.
- Reporte según rule `developer`.
