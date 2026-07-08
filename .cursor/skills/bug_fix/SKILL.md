---
name: bug-fix
description: Fixes bugs by reproducing the issue, finding root cause, applying minimal fix, and adding regression tests. Use when fixing reported bugs, test failures, or unexpected behavior.
---

# Bug Fix

## When to use
- Bug reportado en QA_REPORT o por usuario.
- Test fallando.
- Comportamiento incorrecto vs SPEC.

## Process
1. **Reproducir** — pasos claros; test que falle si no existe.
2. **Causa raíz** — no parches superficiales.
3. **Solución mínima** — menor diff que corrija el problema.
4. **Test de regresión** — evitar recurrencia.
5. **Validar** — lint + tests + caso original.

## Inputs
- `docs/SPEC.md` (comportamiento esperado).
- `docs/QA_REPORT.md` (si existe).
- Descripción del bug y severidad.

## Rules
- Una causa, un fix (evitar cambios colaterales).
- No refactorizar de más en el mismo PR/tarea.
- Si el bug es por requisito ambiguo → escalar a PM.
- Actualizar `docs/CHANGELOG.md` (sección Fixed).

## Delivery
```markdown
## Bug Fix — [ID]

### Síntoma
### Causa raíz
### Solución
### Test de regresión
### Verificación
```
