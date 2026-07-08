---
name: refactor
description: Improves existing code structure without changing external behavior. Validates tests before and after changes. Use for code cleanup, reducing duplication, or improving architecture adherence.
---

# Refactor

## When to use
- Deuda técnica en REVIEW.md.
- Violación de capas sin cambio funcional.
- Duplicación o complejidad alta.

## Process
1. Confirmar comportamiento actual (tests verdes).
2. Definir objetivo del refactor (una mejora clara).
3. Cambios incrementales pequeños.
4. Tests verdes después de cada paso.
5. Sin cambio de API pública salvo tarea explícita.

## Rules
- **No cambiar comportamiento** observable.
- Tests antes y después obligatorios.
- No mezclar refactor con feature nueva.
- Alinearse con `docs/ARCHITECTURE.md`.

## Validación
```bash
# Ejecutar suite completa del proyecto
flutter test   # o pytest, npm test, etc.
```

## Delivery
- Diff enfocado.
- `docs/CHANGELOG.md` (Changed).
- Nota en REVIEW si cierra deuda técnica.
