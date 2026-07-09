# Software Factory — Cursor AI Team

Plantilla reutilizable de **fábrica de software** para desarrollo asistido por IA con Cursor. Combina **Spec-Driven Development (SDD)** con roles, skills y un **orquestador automático** (`factory/`).

**No incluye código de producto** — el código vive en `projects/<tu-proyecto>/`. Este repo es la metodología, las reglas y la automatización.

## Qué es esto

| Modo | Cuándo usarlo |
|------|----------------|
| **Cursor manual** | Agent Mode + rules/skills + prompts en el IDE |
| **Orquestador `factory`** | Automatizar tareas de `docs/TASKS.md` desde terminal |

Ambos comparten la misma metodología: `SPEC` → `ARCHITECTURE` → `TASKS` → código en `projects/`.

## Empezar un proyecto nuevo

1. **Documentación** — completa `docs/SPEC.md` (PM) y `docs/ARCHITECTURE.md` + `docs/TASKS.md` (Architect). Plantillas en `docs/templates/`.
2. **Código** — crea `projects/<nombre>/` (Flutter, FastAPI, etc.) según la arquitectura.
3. **Desarrollo** — `python -m factory run next` o Agent Mode con rule `@developer`.

Guía paso a paso: [projects/README.md](projects/README.md) · [README_AI_WORKFLOW.md](README_AI_WORKFLOW.md)

## Metodología

- **Spec-Driven Development (SDD)** — el requerimiento manda
- **Clean Architecture** y **SOLID** (skills por stack)
- Desarrollo incremental por tareas (`T-XXX`)
- Flujo por requerimiento: **Analizar → Crear → Probar**
- Revisiones: QA, Review, Security

```
PM → Architect → Developer → QA → Reviewer → Security
```

## Orquestador automático

**Requisitos:** Python 3.11+, [Cursor Desktop](https://cursor.com) abierto, API key.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-factory.txt

cp .env.example .env   # añade CURSOR_API_KEY
export $(grep -v '^#' .env | xargs)
```

**Comandos principales:**

```bash
python -m factory pending              # ver tareas [ ]
python -m factory run next               # siguiente tarea
python -m factory run T-001              # una tarea (analizar + crear + probar)
python -m factory analyze T-001          # solo análisis
python -m factory role qa                # validación formal
python -m factory pipeline --max-tasks 3
```

Guía completa: [docs/ORCHESTRATOR.md](docs/ORCHESTRATOR.md)

## Estructura del repositorio

```
factory/                 # Orquestador SDD (python -m factory)
.cursor/
├── rules/               # PM, Architect, Developer, QA, Reviewer, Security
└── skills/              # flutter_feature, backend_feature, testing, …

docs/
├── SPEC.md              # Especificación funcional (rellenar)
├── ARCHITECTURE.md      # Arquitectura técnica (rellenar)
├── TASKS.md             # Plan de tareas (rellenar)
├── templates/           # Plantillas para nuevos proyectos
└── SOFTWARE_FACTORY_WORKFLOW.md

prompts/                 # Prompts para Cursor Agent Mode
projects/                # ← Tu código va aquí (vacío al clonar)
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
- [projects/README.md](projects/README.md) — cómo añadir un proyecto
- [docs/ORCHESTRATOR.md](docs/ORCHESTRATOR.md) — orquestador y modelos
- [docs/SOFTWARE_FACTORY_WORKFLOW.md](docs/SOFTWARE_FACTORY_WORKFLOW.md) — metodología SDD
