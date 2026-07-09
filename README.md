# Software Factory — Cursor AI Team

Repositorio de **fábrica de software** para desarrollo asistido por IA con Cursor. Combina **Spec-Driven Development (SDD)** con roles, skills y un **orquestador automático** (`factory/`) sobre Cursor SDK.

## Qué es esto

| Modo | Cuándo usarlo |
|------|----------------|
| **Cursor manual** | Agent Mode + rules/skills + prompts en el IDE |
| **Orquestador `factory`** | Automatizar tareas de `docs/TASKS.md` desde terminal |

Ambos comparten la misma metodología: `SPEC` → `ARCHITECTURE` → `TASKS` → código en `projects/`.

## Metodología

- **Spec-Driven Development (SDD)** — el requerimiento manda
- **Clean Architecture** y **SOLID**
- Desarrollo incremental por tareas (`T-XXX`)
- Flujo por requerimiento: **Analizar → Crear → Probar**
- Revisiones: QA, Review, Security

```
PM → Architect → Developer → QA → Reviewer → Security
```

## Inicio rápido

### 1. Manual (Cursor IDE)

1. [README_AI_WORKFLOW.md](README_AI_WORKFLOW.md) — guía operativa
2. [docs/SOFTWARE_FACTORY_WORKFLOW.md](docs/SOFTWARE_FACTORY_WORKFLOW.md) — fases detalladas
3. Proyecto nuevo → `prompts/new_project.md` + rule `@product_manager`
4. Proyecto existente → skill `project_analysis`

### 2. Orquestador automático

**Requisitos:** Python 3.11+, [Cursor Desktop](https://cursor.com) abierto, API key.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-factory.txt

cp .env.example .env   # añade CURSOR_API_KEY
export $(grep -v '^#' .env | xargs)
```

**Modelos por tier** (en `.env`):

```bash
FACTORY_MODEL_SMART=composer-2.5        # análisis / arquitectura
FACTORY_MODEL_FAST=composer-2.5-fast    # implementación normal
FACTORY_MODEL_CHEAP=composer-2.5-fast   # tareas muy simples (--tier cheap)
```

**Comandos principales:**

```bash
python -m factory pending              # ver tareas [ ]

python -m factory run                  # autopilot: todas las pendientes
python -m factory run next             # siguiente tarea (alias)
python -m factory run --once           # solo la siguiente
python -m factory run --max 3          # límite de tareas por corrida
python -m factory run T-060            # una tarea (analizar + crear + probar)

python -m factory analyze T-060        # solo análisis (smart)
python -m factory task T-060 --use-analysis   # solo implementar (fast)

python -m factory role qa              # validación formal
python -m factory pipeline --max-tasks 1 --review --security
```

Cada `factory run` ejecuta:

1. **Análisis** (modelo smart) → `.factory/analysis/T-XXX.md`
2. **Implementar + probar** (modelo fast) → código + tests + docs

Guía completa: [docs/ORCHESTRATOR.md](docs/ORCHESTRATOR.md)

## Proyecto activo: Barbería App

| Proyecto | Stack | Puerto dev |
|----------|-------|------------|
| `projects/barberia-app/` | Flutter, Riverpod, GoRouter | — |
| `projects/barberia-api/` | FastAPI, SQLAlchemy, PostgreSQL | **8001** (API), **5433** (DB) |

```bash
# Backend
cd projects/barberia-api && make up && make migrate && make api

# Tests
cd projects/barberia-api && pytest
cd projects/barberia-app && flutter test
```

Documentación del producto: `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/TASKS.md`.

## Estructura del repositorio

```
factory/                 # Orquestador SDD (python -m factory)
.cursor/
├── rules/               # PM, Architect, Developer, QA, Reviewer, Security
└── skills/              # flutter_feature, backend_feature, testing, …

docs/
├── SPEC.md              # Especificación funcional
├── ARCHITECTURE.md      # Arquitectura técnica
├── TASKS.md             # Plan de tareas (fuente de verdad del progreso)
├── CHANGELOG.md
├── QA_REPORT.md
├── ORCHESTRATOR.md
└── SOFTWARE_FACTORY_WORKFLOW.md

prompts/                 # Prompts para Cursor Agent Mode
projects/
├── barberia-app/        # Frontend Flutter
└── barberia-api/        # Backend REST
```

## Roles y documentos

| Rule | Documento |
|------|-----------|
| `product_manager` | `docs/SPEC.md` |
| `architect` | `docs/ARCHITECTURE.md`, `docs/TASKS.md` |
| `developer` | `projects/` |
| `qa` | `docs/QA_REPORT.md` |
| `reviewer` | `docs/REVIEW.md` |
| `security` | `docs/SECURITY_REPORT.md` |

## Skills disponibles

`project_analysis` · `feature_design` · `flutter_feature` · `backend_feature` · `database_change` · `bug_fix` · `refactor` · `testing` · `code_review` · `security_audit`

## Enlaces útiles

- [README_AI_WORKFLOW.md](README_AI_WORKFLOW.md) — workflow operativo
- [docs/ORCHESTRATOR.md](docs/ORCHESTRATOR.md) — orquestador y modelos
- [docs/SOFTWARE_FACTORY_WORKFLOW.md](docs/SOFTWARE_FACTORY_WORKFLOW.md) — metodología SDD
- [docs/CLEANUP_REPORT.md](docs/CLEANUP_REPORT.md) — migración Cursor-only (backup commit `63891e5`)
