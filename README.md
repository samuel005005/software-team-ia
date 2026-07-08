# Software Factory — Cursor AI Team

Repositorio de **fábrica de software** para desarrollo asistido por IA con Cursor. No incluye framework de agentes en Python: usa **Agent Mode**, **Rules** y **Skills**.

## Metodología

- **Spec-Driven Development (SDD)**
- **Clean Architecture** y **SOLID**
- **Design Patterns** cuando aporten valor
- Desarrollo incremental por tareas
- Revisiones de calidad (QA, Review, Security)

## Flujo del equipo

```
PM → Architect → Developer → QA → Reviewer → Security
```

## Inicio rápido

1. [README_AI_WORKFLOW.md](README_AI_WORKFLOW.md) — guía operativa
2. [docs/SOFTWARE_FACTORY_WORKFLOW.md](docs/SOFTWARE_FACTORY_WORKFLOW.md) — fases detalladas
3. Proyecto nuevo → `prompts/new_project.md` + rule `@product_manager`
4. Proyecto existente → skill `project_analysis` + `prompts/analyze_existing_project.md`

## Estructura del repositorio

```
.cursor/
├── rules/          # Roles: PM, Architect, Developer, QA, Reviewer, Security
└── skills/         # Workflows: flutter_feature, backend_feature, testing, etc.

docs/
├── SPEC.md              # Especificación (PM)
├── ARCHITECTURE.md      # Arquitectura (Architect)
├── TASKS.md             # Plan de tareas
├── CHANGELOG.md         # Historial de cambios
├── QA_REPORT.md         # Reporte QA
├── REVIEW.md            # Code review
├── SECURITY_REPORT.md   # Auditoría de seguridad
├── templates/           # Plantillas para nuevos proyectos
└── SOFTWARE_FACTORY_WORKFLOW.md

prompts/            # Prompts copiables en Cursor Agent Mode
projects/           # Proyectos de software (ej. barberia-app)
```

## Roles y documentos

| Rule | Documento principal |
|------|---------------------|
| `product_manager` | `docs/SPEC.md` |
| `architect` | `docs/ARCHITECTURE.md`, `docs/TASKS.md` |
| `developer` | `projects/` |
| `qa` | `docs/QA_REPORT.md` |
| `reviewer` | `docs/REVIEW.md` |
| `security` | `docs/SECURITY_REPORT.md` |

## Skills disponibles

`project_analysis` · `feature_design` · `flutter_feature` · `backend_feature` · `database_change` · `bug_fix` · `refactor` · `testing` · `code_review` · `security_audit`

## Proyecto de ejemplo

`projects/barberia-app/` — Barbería App (Flutter), con SPEC y arquitectura en `docs/`.

## Historial

Framework Python de agentes eliminado en favor de metodología Cursor-only. Backup: commit `63891e5`. Detalle: [docs/CLEANUP_REPORT.md](docs/CLEANUP_REPORT.md).
