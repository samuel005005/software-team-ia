---
name: feature-design
description: Designs new features from SPEC by identifying entities, business rules, technical impact, and implementable tasks. Use when planning a new feature, epic, or user story before development.
---

# Feature Design

## When to use
- Nueva funcionalidad aprobada en SPEC.
- Antes de asignar tareas al Developer.
- Impacto técnico no documentado.

## Inputs
- `docs/SPEC.md` (historias y reglas de negocio).
- `docs/ARCHITECTURE.md` (módulos y contratos).
- Descripción de la funcionalidad.

## Process
1. Leer SPEC y localizar historias/reglas relacionadas.
2. Identificar entidades, casos de uso y flujos.
3. Mapear impacto: frontend, backend, DB, auth, tests.
4. Definir contratos (API, DTOs, repositorios) a alto nivel.
5. Crear o actualizar tareas en `docs/TASKS.md` con IDs, dependencias y criterios.
6. Documentar decisiones breves en `docs/ARCHITECTURE.md` si cambian contratos (solicitar aprobación Architect).

## Output
- Tareas en `docs/TASKS.md`
- Notas de diseño (en chat o ARCHITECTURE si aplica)

## Checklist
- [ ] Historias SPEC vinculadas
- [ ] Reglas de negocio identificadas
- [ ] Capas afectadas definidas
- [ ] Tareas pequeñas e implementables
- [ ] Dependencias entre tareas
- [ ] Criterios de aceptación por tarea

## Rules
- No implementar código.
- No inventar requisitos fuera del SPEC.
- Patrones solo si resuelven problema real.
