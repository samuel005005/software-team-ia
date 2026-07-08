---
name: code-review
description: Reviews code changes for architecture, readability, duplication, complexity, and test quality. Generates structured findings for docs/REVIEW.md. Use when reviewing PRs, diffs, or post-development quality checks.
---

# Code Review

## When to use
- Post-implementación Developer.
- Antes de merge o entrega.
- Activar con rule `reviewer`.

## Inputs
- `docs/ARCHITECTURE.md`
- `docs/TASKS.md`
- Diff o archivos cambiados en `projects/`
- `docs/QA_REPORT.md` (contexto)

## Review checklist

### Arquitectura
- [ ] Capas respetadas (no API en UI, dominio sin framework).
- [ ] Responsabilidad única por módulo/clase.
- [ ] Dependencias en dirección correcta.

### Código
- [ ] Legible, nombres claros.
- [ ] Sin duplicación evitable.
- [ ] Errores manejados.
- [ ] Sin secretos hardcodeados.

### Tests
- [ ] Lógica crítica cubierta.
- [ ] Tests significativos (no triviales).

## Severity
- **CRITICAL** — bug, seguridad, violación arquitectónica grave.
- **MAJOR** — mantenibilidad, falta tests importantes.
- **MINOR** — estilo, mejoras opcionales.

## Output
Generar o actualizar `docs/REVIEW.md` usando `docs/templates/REVIEW.template.md`.

## Rules
- No editar código (solo reportar).
- Feedback accionable con archivo/línea.
- Veredicto: APROBADO / CAMBIOS REQUERIDOS.
