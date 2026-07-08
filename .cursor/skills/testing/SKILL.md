---
name: testing
description: Creates unit, integration, and widget tests including negative cases and edge scenarios. Use when adding test coverage, validating features, or preparing for QA.
---

# Testing

## When to use
- Nueva feature o bug fix sin tests.
- Preparación para fase QA.
- Casos límite del SPEC.

## Inputs
- `docs/SPEC.md` — criterios de aceptación.
- Código bajo prueba.
- Stack del proyecto (Flutter, pytest, Jest, etc.).

## Test types

| Tipo | Qué cubre |
|------|-----------|
| Unit | Use cases, mappers, validators, domain |
| Integration | Repositories, API, DB |
| Widget/UI | Pantallas críticas, flujos usuario |
| E2E | Flujos completos (si hay infra) |

## Process
1. Mapear criterios de aceptación → casos de prueba.
2. Incluir casos **negativos** y límites.
3. AAA: Arrange, Act, Assert.
4. Mocks en fronteras (API, DB), no en dominio puro.
5. Ejecutar suite y documentar resultados.

## Naming
- `test_<unit>_<scenario>_<expected>`
- Descripción legible del comportamiento.

## Flutter
- `flutter test`
- `ProviderScope` para widgets con Riverpod.
- `mocktail` o `mockito` si está en ARCHITECTURE.

## Backend
- Fixtures para DB de test.
- Aislar tests de red externa.

## Delivery
- Archivos de test + comandos ejecutados.
- Cobertura de criterios de aceptación (tabla).
