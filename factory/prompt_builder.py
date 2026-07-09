from pathlib import Path

from factory.config import DOCS_DIR, PROMPTS_DIR, PROJECTS_DIR, RULES_DIR
from factory.models import FactoryRole, TaskItem
from factory.spec_parser import extract_user_stories, parse_story_ids

SPEC_PATH = DOCS_DIR / "SPEC.md"

REQUIREMENT_DRIVEN_WORKFLOW = """
## Workflow obligatorio: Analizar → Crear → Probar

No saltes pasos. Todo parte del **requerimiento** (SPEC + historia de usuario).

### Fase 1 — ANALIZAR (requerimiento)
1. Lee la historia de usuario y sus **criterios de aceptación** (abajo o en SPEC).
2. Cruza con `docs/ARCHITECTURE.md`: capas, endpoints, entidades.
3. Revisa código existente relacionado (no reimplementar lo ya hecho).
4. Escribe mentalmente (o en comentario de commit) el plan mínimo:
   - qué archivos tocar
   - qué endpoints/pantallas faltan
   - qué tests añadir

**No codifiques hasta entender el requerimiento.**

### Fase 2 — CREAR (implementación)
1. Implementa **solo** lo necesario para cumplir los criterios de aceptación.
2. Sigue Clean Architecture y convenciones del repo.
3. Cambios mínimos; una tarea = un incremento acotado.

### Fase 3 — PROBAR (validación)
1. Ejecuta tests del stack definido en `docs/ARCHITECTURE.md`, por ejemplo:
   - Backend Python: `cd projects/<api> && pytest`
   - Flutter: `cd projects/<app> && flutter analyze && flutter test`
   - Node: `cd projects/<api> && npm test`
2. Verifica **cada criterio de aceptación** de la US contra lo implementado.
3. Si algo falla, corrige antes de cerrar la tarea.

### Cierre (solo si Fase 3 OK)
1. Marca la tarea como `[x]` en `docs/TASKS.md` con notas breves.
2. Actualiza `docs/CHANGELOG.md` y `docs/QA_REPORT.md`.
3. Reporta: archivos tocados, tests ejecutados, criterios cumplidos.
"""

ROLE_PROMPT_FILES: dict[FactoryRole, str] = {
    FactoryRole.PRODUCT_MANAGER: "new_project.md",
    FactoryRole.ARCHITECT: "new_project.md",
    FactoryRole.DEVELOPER: "implement_feature.md",
    FactoryRole.QA: "review_project.md",
    FactoryRole.REVIEWER: "review_project.md",
    FactoryRole.SECURITY: "security_audit.md",
}

ROLE_SKILL_HINTS: dict[FactoryRole, list[str]] = {
    FactoryRole.DEVELOPER: ["backend_feature", "flutter_feature", "database_change"],
    FactoryRole.QA: ["testing"],
    FactoryRole.REVIEWER: ["code_review"],
    FactoryRole.SECURITY: ["security_audit"],
}


def _read_rule(role: FactoryRole) -> str:
    path = RULES_DIR / f"{role.value}.md"
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()


def _read_prompt_template(role: FactoryRole) -> str:
    filename = ROLE_PROMPT_FILES[role]
    path = PROMPTS_DIR / filename
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _task_requirement_sections(task: TaskItem) -> list[str]:
    story_ids = parse_story_ids(task.story)
    requirement_block = ""
    if story_ids and SPEC_PATH.exists():
        stories_text = extract_user_stories(SPEC_PATH.read_text(encoding="utf-8"), story_ids)
        if stories_text:
            requirement_block = stories_text

    sections = [
        "",
        "## Tarea asignada",
        f"- **ID:** {task.task_id}",
        f"- **Título:** {task.title}",
        f"- **Historia:** {task.story or 'N/A'}",
        f"- **Responsable:** {task.owner}",
    ]

    if requirement_block:
        sections.extend(
            [
                "",
                "## Requerimiento (SPEC — criterios de aceptación)",
                requirement_block,
                "",
                "La implementación debe satisfacer **todos** los criterios marcados arriba.",
            ]
        )
    else:
        sections.append(
            f"\nBusca `{task.story or task.task_id}` en `docs/SPEC.md` y extrae criterios de aceptación."
        )

    return sections


ANALYZE_ONLY_WORKFLOW = """
## Fase 1 — SOLO ANALIZAR (no implementar)

**No escribas código de producto.** No marques la tarea como `[x]`.

1. Lee el requerimiento y criterios de aceptación.
2. Cruza con `docs/ARCHITECTURE.md` y el código existente en `projects/`.
3. Produce un **plan de implementación** con este formato:

```markdown
# Análisis — [T-XXX]

## Criterios de aceptación (checklist)
- [ ] Criterio 1 — …
- [ ] Criterio 2 — …

## Estado actual del código
- Qué ya existe
- Qué falta

## Plan de implementación
### Backend
- archivos / endpoints / tests

### Flutter (si aplica)
- archivos / pantallas / tests

## Riesgos y decisiones
- …

## Comandos de validación
- pytest …
- flutter test …
```

4. **Guarda el análisis** en `.factory/analysis/{task_id}.md` (obligatorio).
5. Resume en tu respuesta final: archivos clave y pasos siguientes.
"""


def _projects_context() -> str:
    if not PROJECTS_DIR.is_dir():
        return "- Carpeta `projects/` no encontrada"
    entries = sorted(
        p.name for p in PROJECTS_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")
    )
    if not entries:
        return "- `projects/` vacío — crear el código según ARCHITECTURE.md (ver projects/README.md)"
    lines = [f"- `projects/{name}/`" for name in entries]
    return "\n".join(lines)


def build_analyze_prompt(task: TaskItem) -> str:
    rule = _read_rule(FactoryRole.ARCHITECT)
    sections = [
        "# Rol: architect (modo análisis)",
        "",
        "Analiza la tarea antes de implementar. **No codifiques.**",
        "",
        "## Rule (Architect)",
        rule or "(rule no encontrada)",
        "",
        ANALYZE_ONLY_WORKFLOW.strip(),
        *_task_requirement_sections(task),
        "",
        "## Entregable obligatorio",
        f"Escribe el análisis completo en: `.factory/analysis/{task.task_id}.md`",
        "",
        "## Contexto del repo",
        f"- Raíz: {DOCS_DIR.parent}",
        _projects_context(),
    ]
    return "\n".join(sections)


def build_role_prompt(
    role: FactoryRole,
    *,
    task: TaskItem | None = None,
    extra_instruction: str | None = None,
    analysis_context: str | None = None,
) -> str:
    rule = _read_rule(role)
    template = _read_prompt_template(role)
    skills = ", ".join(f"`{name}`" for name in ROLE_SKILL_HINTS.get(role, []))

    sections = [
        f"# Rol: {role.value}",
        "",
        "Sigue estrictamente la rule del rol y el workflow SDD del repositorio.",
        "",
        "## Rule",
        rule or "(rule no encontrada)",
        "",
        "## Plantilla de prompt",
        template or "(plantilla no encontrada)",
        "",
        "## Documentos obligatorios",
        "- docs/SPEC.md",
        "- docs/ARCHITECTURE.md",
        "- docs/TASKS.md",
        "- docs/CHANGELOG.md",
    ]

    if skills:
        sections.extend(["", "## Skills recomendadas", skills])

    if task:
        sections.extend([REQUIREMENT_DRIVEN_WORKFLOW.strip(), *_task_requirement_sections(task)])

        if analysis_context:
            sections.extend(
                [
                    "",
                    "## Análisis previo (Fase 1 — ya completado)",
                    "Sigue este plan. No repitas exploración innecesaria.",
                    "",
                    analysis_context,
                ]
            )

    if extra_instruction:
        sections.extend(["", "## Instrucción adicional", extra_instruction.strip()])

    sections.extend(
        [
            "",
            "## Contexto del repo",
            f"- Raíz: {DOCS_DIR.parent}",
            _projects_context(),
        ]
    )

    return "\n".join(sections)
