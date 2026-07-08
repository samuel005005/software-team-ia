---
name: database-change
description: Plans and implements database schema changes including migrations, models, indexes, constraints, and rollback strategy. Use for new tables, columns, indexes, or data model updates.
---

# Database Change

## When to use
- Cambios de esquema en SPEC/ARCHITECTURE.
- Nueva entidad persistente.
- Índices, constraints, migraciones.

## Prerequisites
- Leer `docs/ARCHITECTURE.md` (modelo de datos).
- Leer tarea en `docs/TASKS.md`.
- Identificar motor (PostgreSQL, SQLite, etc.).

## Process
1. Diseñar cambio alineado al modelo en ARCHITECTURE.
2. Escribir migración up/down (o equivalente).
3. Actualizar modelos/entidades en domain e infrastructure.
4. Agregar índices y constraints necesarios.
5. Documentar rollback y datos existentes afectados.
6. Tests de migración o integración si aplica.

## Checklist
- [ ] Migración reversible o plan de rollback
- [ ] Tipos y nullability correctos
- [ ] FK y constraints de integridad
- [ ] Índices para consultas frecuentes
- [ ] Sin breaking change sin migración de datos
- [ ] CHANGELOG actualizado

## Safety
- No ejecutar DROP destructivo sin confirmación explícita.
- No incluir datos sensibles en migraciones seed.
- Validar en entorno dev antes de prod.

## Delivery
- Archivos de migración + modelos actualizados.
- Nota en `docs/CHANGELOG.md`.
