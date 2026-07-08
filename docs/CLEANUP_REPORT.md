# Reporte de limpieza — Migración a Software Factory con Cursor

**Fecha:** 2026-07-08  
**Objetivo:** Eliminar el framework Python de agentes y adoptar metodología basada en Cursor Rules + documentación + prompts.

---

## 1. Análisis del repositorio actual

### Qué es el framework anterior (a eliminar)

| Módulo | Propósito | Reemplazado por Cursor |
|--------|-----------|------------------------|
| `agents/` | Agentes Python (Analyst, Architect, Developer, QA) | Cursor Rules + Agent Mode por rol |
| `orchestrator/` | Ejecución secuencial de agentes | Workflow manual/documentado en `docs/` |
| `execution/` | ExecutionGraph, Retry, Policies | Proceso por fases en Cursor |
| `planning/` | PlannerAgent, ExecutionPlan | Product Manager + Architect Rules |
| `factory/` | FactoryManagerAgent | Workflow documentado |
| `llm/` | Providers OpenAI/Claude/Gemini/Mock | Modelos nativos de Cursor |
| `parsers/` | Parsers JSON de respuestas LLM | Salida estructurada en `docs/*.md` |
| `prompts/*.py` | Prompt builders Python | `prompts/*.md` copiables en Cursor |
| `memory/` | MemoryStore por agente | Contexto del proyecto + docs |
| `context/` | AgentContext builder | Archivos abiertos + Rules |
| `state/` | ProjectState compartido | `docs/SPEC.md`, `TASKS.md`, etc. |
| `artifacts/` | ArtifactCollection/Writer | Código real en `projects/` |
| `tools/` | ToolRegistry, filesystem tools | Herramientas nativas de Cursor |
| `workspace/` | Sandbox de paths | Workspace de Cursor |
| `project_context/` | ProjectContextService | `analyze_existing_project.md` |
| `quality/` | QualityEvaluator/Pipeline | QA Rule + `REVIEW.md` |
| `review/` | ReviewerAgent | Reviewer Rule |
| `actions/` | ActionExecutor | Developer en Cursor |
| `workflows/` | software_creation.py | `SOFTWARE_FACTORY_WORKFLOW.md` |
| `tests/` | 347 tests del framework | No aplica (sin código) |
| `main.py` | Demo del harness | `README_AI_WORKFLOW.md` |
| `requirements.txt` | anthropic, openai, google-genai, pytest | Sin dependencias Python |

### Qué se conserva

| Elemento | Motivo |
|----------|--------|
| `projects/barberia-app/` | Proyecto de ejemplo |
| `.gitignore` | Control de versiones |
| Historial Git | Commit de respaldo antes de limpieza |

---

## 2. Inventario de eliminación

### Directorios completos (18)

```text
actions/
agents/
artifacts/
context/
execution/
factory/
llm/
memory/
orchestrator/
parsers/
planning/
project_context/
prompts/          # módulos Python; se recrea con .md
quality/
review/
state/
tests/
tools/
workflows/
workspace/
```

### Archivos sueltos (2)

```text
main.py
requirements.txt
```

### Archivos parciales previos (reemplazados)

```text
.cursor/rules/*.mdc   → reemplazados por .md según especificación
```

**Total estimado:** ~150 archivos Python + tests eliminados.

---

## 3. Nueva estructura

```text
software-team-ai/
├── .cursor/rules/          # Roles de la fábrica
│   ├── product_manager.md
│   ├── architect.md
│   ├── developer.md
│   ├── qa.md
│   ├── reviewer.md
│   └── security.md
├── docs/                   # Artefactos del proceso
│   ├── SPEC.md
│   ├── ARCHITECTURE.md
│   ├── TASKS.md
│   ├── CHANGELOG.md
│   ├── REVIEW.md
│   ├── SOFTWARE_FACTORY_WORKFLOW.md
│   └── CLEANUP_REPORT.md
├── prompts/                # Prompts copiables en Cursor
│   ├── new_project.md
│   ├── analyze_existing_project.md
│   ├── implement_feature.md
│   ├── review_project.md
│   └── security_audit.md
├── projects/               # Proyectos generados
│   └── barberia-app/
├── README.md
└── README_AI_WORKFLOW.md
```

---

## 4. Commit de respaldo

Commit creado antes de la limpieza con mensaje:
`backup: estado completo del framework Python antes de migración Cursor`

Para recuperar el framework anterior:
```bash
git log --oneline | head -5
git checkout <commit-backup> -- .
```
