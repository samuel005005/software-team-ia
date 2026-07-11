from pathlib import Path

from factory.config import (
    DOCS_DIR,
    PROMPTS_DIR,
    PROJECTS_DIR,
    RULES_DIR,
    lean_prompt_enabled,
    max_spec_chars,
)
from factory.models import FactoryRole, QAScope, TaskItem
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

LEAN_DEV_WORKFLOW = """
## Workflow (resumido)
1. **Crear** — solo lo necesario para los criterios de aceptación.
2. **Probar** — tests del stack en ARCHITECTURE; corrige antes de cerrar.
3. **Cerrar** — marca `[x]` en TASKS.md, actualiza CHANGELOG y QA_REPORT.
"""

ROLE_PROMPT_FILES: dict[FactoryRole, str] = {
    FactoryRole.PRODUCT_MANAGER: "new_project.md",
    FactoryRole.ARCHITECT: "new_project.md",
    FactoryRole.DEVELOPER: "implement_feature.md",
    FactoryRole.QA: "qa_validate.md",
    FactoryRole.REVIEWER: "review_project.md",
    FactoryRole.SECURITY: "security_audit.md",
}

ROLE_SKILL_HINTS: dict[FactoryRole, list[str]] = {
    FactoryRole.DEVELOPER: ["backend_feature", "flutter_feature", "database_change"],
    FactoryRole.QA: ["testing"],
    FactoryRole.REVIEWER: ["code_review"],
    FactoryRole.SECURITY: ["security_audit"],
}

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

LEAN_ANALYZE_WORKFLOW = """
## Solo analizar (no implementar)
Lee SPEC + ARCHITECTURE + código en `projects/`. Guarda el plan en `.factory/analysis/{task_id}.md`.
Incluye: criterios, estado actual, plan por capa, riesgos, comandos de validación.
"""


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


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n\n…(truncado por límite de tokens del orquestador)"


def _rule_reference(role: FactoryRole) -> str:
    return f".cursor/rules/{role.value}.md"


def _prompt_reference(role: FactoryRole) -> str:
    return f"prompts/{ROLE_PROMPT_FILES[role]}"


def _task_requirement_sections(task: TaskItem, *, max_spec: int | None = None) -> list[str]:
    story_ids = parse_story_ids(task.story)
    requirement_block = ""
    if story_ids and SPEC_PATH.exists():
        stories_text = extract_user_stories(SPEC_PATH.read_text(encoding="utf-8"), story_ids)
        if stories_text:
            limit = max_spec if max_spec is not None else max_spec_chars()
            requirement_block = _truncate_text(stories_text, limit)

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


def _tasks_requirement_sections(tasks: list[TaskItem], *, max_spec: int | None = None) -> list[str]:
    sections = ["", "## Tareas del lote"]
    for task in tasks:
        sections.append(f"- **{task.task_id}** — {task.title} ({task.story or 'sin US'})")

    story_ids: list[str] = []
    for task in tasks:
        story_ids.extend(parse_story_ids(task.story))
    unique_stories = list(dict.fromkeys(story_ids))

    if unique_stories and SPEC_PATH.exists():
        stories_text = extract_user_stories(SPEC_PATH.read_text(encoding="utf-8"), unique_stories)
        if stories_text:
            limit = max_spec if max_spec is not None else max_spec_chars()
            sections.extend(
                [
                    "",
                    "## Requerimiento (SPEC)",
                    _truncate_text(stories_text, limit),
                ]
            )

    return sections


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


def _role_context_sections(role: FactoryRole, *, lean: bool) -> list[str]:
    skills = ", ".join(f"`{name}`" for name in ROLE_SKILL_HINTS.get(role, []))

    if lean:
        sections = [
            "## Rule (léela en el repo)",
            f"- `{_rule_reference(role)}`",
            "",
            "## Plantilla de prompt",
            f"- `{_prompt_reference(role)}`",
            "",
            "## Documentos (solo lo necesario)",
            "- `docs/SPEC.md` — US de esta tarea",
            "- `docs/ARCHITECTURE.md`",
            f"- `docs/TASKS.md` — fila de la tarea",
            "- `docs/CHANGELOG.md`",
        ]
        if skills:
            sections.extend(["", "## Skills (si aplican)", skills])
        return sections

    rule = _read_rule(role)
    template = _read_prompt_template(role)
    sections = [
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
    return sections


def build_analyze_prompt(task: TaskItem, *, lean: bool | None = None) -> str:
    use_lean = lean_prompt_enabled() if lean is None else lean
    workflow = LEAN_ANALYZE_WORKFLOW.format(task_id=task.task_id) if use_lean else ANALYZE_ONLY_WORKFLOW.strip()

    sections = [
        "# Rol: architect (modo análisis)",
        "",
        "Analiza la tarea antes de implementar. **No codifiques.**",
        "",
        *_role_context_sections(FactoryRole.ARCHITECT, lean=use_lean),
        "",
        workflow,
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


def build_analyze_batch_prompt(story_id: str, tasks: list[TaskItem], *, lean: bool | None = None) -> str:
    use_lean = lean_prompt_enabled() if lean is None else lean
    workflow = (
        f"Analiza **todas** las tareas del lote para {story_id}. No implementes. "
        f"Guarda en `.factory/analysis/_story_{story_id}.md` con sección por T-XXX."
    )

    sections = [
        f"# Rol: architect (análisis grupal — {story_id})",
        "",
        workflow,
        "",
        *_role_context_sections(FactoryRole.ARCHITECT, lean=use_lean),
        *_tasks_requirement_sections(tasks),
        "",
        "## Entregable obligatorio",
        f"`.factory/analysis/_story_{story_id}.md` — una sección `## T-XXX` por tarea.",
        "",
        "## Contexto del repo",
        f"- Raíz: {DOCS_DIR.parent}",
        _projects_context(),
    ]
    return "\n".join(sections)


_STATUS_TOKEN = {
    "pending": "`[ ]`",
    "in_progress": "`[~]`",
    "completed": "`[x]`",
    "blocked": "`[!]`",
}


def _qa_scope_sections(scope_tasks: list[TaskItem], scope_label: str) -> list[str]:
    from factory.spec_parser import parse_story_ids

    sections = [
        "",
        "## Alcance de esta validación",
        f"**Ámbito:** {scope_label}",
        "",
        "### Tareas en alcance",
    ]
    for task in scope_tasks:
        token = _STATUS_TOKEN.get(task.status.value, task.status.value)
        sections.append(f"- **{task.task_id}** — {task.title} — {task.story or 'sin US'} — estado {token}")

    story_ids: list[str] = []
    for task in scope_tasks:
        story_ids.extend(parse_story_ids(task.story))
    unique_stories = list(dict.fromkeys(story_ids))
    if unique_stories:
        sections.extend(["", "### Historias de usuario a validar", ", ".join(unique_stories)])

    sections.extend(
        [
            "",
            "Valida **solo** este alcance. Si una tarea no está `[x]`, repórtalo y veredicto **RECHAZADO**.",
            "Ejecuta tests del stack y documenta comandos en QA_REPORT.",
        ]
    )
    return sections


def build_qa_prompt(
    scope_tasks: list[TaskItem],
    scope_label: str,
    *,
    lean: bool | None = None,
) -> str:
    use_lean = lean_prompt_enabled() if lean is None else lean
    sections = [
        "# Rol: qa (validación formal)",
        "",
        "Validación contra SPEC del alcance indicado.",
        "",
        *_role_context_sections(FactoryRole.QA, lean=use_lean),
        *_qa_scope_sections(scope_tasks, scope_label),
        "",
        "## Veredicto obligatorio en QA_REPORT.md",
        "Sección `## Veredicto` con **APROBADO**, **CONDICIONAL** o **RECHAZADO** (exactamente así).",
        "",
        "## Contexto del repo",
        f"- Raíz: {DOCS_DIR.parent}",
        _projects_context(),
    ]
    return "\n".join(sections)


def build_closure_prompt(
    role: FactoryRole,
    scope_label: str,
    *,
    lean: bool | None = None,
) -> str:
    """Prompt para Reviewer / Security con alcance explícito."""
    use_lean = lean_prompt_enabled() if lean is None else lean
    report = "REVIEW.md" if role == FactoryRole.REVIEWER else "SECURITY_REPORT.md"
    verdict_hint = (
        "**APROBADO** o **CAMBIOS REQUERIDOS**"
        if role == FactoryRole.REVIEWER
        else "**SEGURO**, **RIESGOS** o **INSEGURO**"
    )

    return "\n".join(
        [
            f"# Rol: {role.value} (cierre de release)",
            "",
            f"**Alcance:** {scope_label}",
            "",
            *_role_context_sections(role, lean=use_lean),
            "",
            f"Actualiza `docs/{report}` con veredicto en `## Veredicto`: {verdict_hint}.",
            "",
            "## Contexto del repo",
            f"- Raíz: {DOCS_DIR.parent}",
            _projects_context(),
        ]
    )


def build_dev_followup_prompt(task: TaskItem, *, lean: bool | None = None) -> str:
    """Segundo mensaje en sesión única: implementar sin repetir contexto."""
    use_lean = lean_prompt_enabled() if lean is None else lean
    workflow = LEAN_DEV_WORKFLOW.strip() if use_lean else REQUIREMENT_DRIVEN_WORKFLOW.strip()

    return "\n".join(
        [
            f"# Continúa — Developer ({task.task_id})",
            "",
            "Ya analizaste esta tarea. **Implementa y prueba** según tu plan anterior.",
            "No repitas exploración innecesaria del repo.",
            "",
            workflow.strip(),
            *_task_requirement_sections(task),
            "",
            "## Cierre",
            f"Marca `[x]` en `docs/TASKS.md` solo si los tests y criterios pasan.",
        ]
    )


def build_role_prompt(
    role: FactoryRole,
    *,
    task: TaskItem | None = None,
    extra_instruction: str | None = None,
    analysis_context: str | None = None,
    lean: bool | None = None,
    include_workflow: bool = True,
) -> str:
    use_lean = lean_prompt_enabled() if lean is None else lean

    sections = [
        f"# Rol: {role.value}",
        "",
        "Sigue estrictamente la rule del rol y el workflow SDD del repositorio.",
        "",
        *_role_context_sections(role, lean=use_lean),
    ]

    if task and include_workflow:
        workflow = LEAN_DEV_WORKFLOW.strip() if use_lean else REQUIREMENT_DRIVEN_WORKFLOW.strip()
        sections.extend([workflow, *_task_requirement_sections(task)])

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
