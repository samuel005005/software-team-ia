import re
from pathlib import Path

from factory.models import TaskItem, TaskStatus

STATUS_TOKEN = r"`(\[[ x~!]\])`"

# 6 columnas: | T-040 | Título | US-003 | Developer | skip | `[x]` |
TASK_ROW_6COL = re.compile(
    rf"^\|\s*(T-\d+)\s*\|\s*(.+?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*{STATUS_TOKEN}\s*\|"
)

# 5 columnas: | T-040 | Título | US-003 | Developer | `[x]` |
TASK_ROW_5COL = re.compile(
    rf"^\|\s*(T-\d+)\s*\|\s*(.+?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*{STATUS_TOKEN}\s*\|"
)

# 4 columnas: | T-001 | Título | Developer | `[x]` |
TASK_ROW_4COL = re.compile(
    rf"^\|\s*(T-\d+)\s*\|\s*(.+?)\s*\|\s*([^|]*?)\s*\|\s*{STATUS_TOKEN}\s*\|"
)

_STATUS_MAP = {
    "[ ]": TaskStatus.PENDING,
    "[x]": TaskStatus.COMPLETED,
    "[~]": TaskStatus.IN_PROGRESS,
    "[!]": TaskStatus.BLOCKED,
}

_TITLE_SKIP_MARKERS = re.compile(
    r"\[(?:skip-analyze|simple|no-analyze)\]",
    re.IGNORECASE,
)

_ANALYZE_SKIP_VALUES = frozenset({"skip", "no", "off", "false", "0", "-", "simple"})
_ANALYZE_FORCE_VALUES = frozenset({"force", "yes", "on", "true", "1", "always"})


def _parse_analyze_column(value: str | None) -> tuple[bool, bool]:
    """Devuelve (skip_analyze, force_analyze) desde columna Análisis."""
    if not value:
        return False, False
    normalized = value.strip().lower()
    if normalized in _ANALYZE_SKIP_VALUES:
        return True, False
    if normalized in _ANALYZE_FORCE_VALUES:
        return False, True
    return False, False


def _clean_title(title: str) -> tuple[str, bool]:
    """Quita marcadores [skip-analyze]/[simple] del título."""
    skip = bool(_TITLE_SKIP_MARKERS.search(title))
    cleaned = _TITLE_SKIP_MARKERS.sub("", title)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned, skip


_PHASE_HEADER = re.compile(r"^##\s+(.+)$")


def _parse_task_row(line: str, *, use_analyze_column: bool) -> tuple[str, str, str | None, str, str, str | None] | None:
    stripped = line.strip()

    if use_analyze_column:
        match_6 = TASK_ROW_6COL.match(stripped)
        if match_6:
            task_id, title, story, owner, analyze_col, status_token = match_6.groups()
            return task_id, title, story.strip() or None, owner.strip(), status_token, analyze_col.strip()

    match_5 = TASK_ROW_5COL.match(stripped)
    if match_5:
        task_id, title, story, owner, status_token = match_5.groups()
        return task_id, title, story.strip() or None, owner.strip(), status_token, None

    match_4 = TASK_ROW_4COL.match(stripped)
    if match_4:
        task_id, title, owner, status_token = match_4.groups()
        return task_id, title, None, owner.strip(), status_token, None

    return None


def _table_has_analyze_column(tasks_md: str) -> bool:
    for line in tasks_md.splitlines():
        lowered = line.lower()
        if "|" in line and ("análisis" in lowered or "analisis" in lowered):
            return True
    return False


def parse_tasks(tasks_md: str) -> list[TaskItem]:
    use_analyze_column = _table_has_analyze_column(tasks_md)
    items: list[TaskItem] = []
    current_phase: str | None = None

    for index, line in enumerate(tasks_md.splitlines(), start=1):
        phase_match = _PHASE_HEADER.match(line.strip())
        if phase_match and "fase" in phase_match.group(1).lower():
            current_phase = phase_match.group(1).strip()
            continue

        parsed = _parse_task_row(line, use_analyze_column=use_analyze_column)
        if parsed is None:
            continue

        task_id, title, story, owner, status_token, analyze_col = parsed
        title_clean, skip_from_title = _clean_title(title.strip())
        skip_from_col, force_from_col = _parse_analyze_column(analyze_col)

        items.append(
            TaskItem(
                task_id=task_id,
                title=title_clean,
                story=story,
                owner=owner,
                status=_STATUS_MAP[status_token],
                line_number=index,
                skip_analyze=skip_from_title or skip_from_col,
                force_analyze=force_from_col,
                phase=current_phase,
            )
        )
    return items


def load_tasks(path: Path) -> list[TaskItem]:
    return parse_tasks(path.read_text(encoding="utf-8"))


def next_pending_task(path: Path) -> TaskItem | None:
    for task in load_tasks(path):
        if task.status == TaskStatus.PENDING:
            return task
    return None


def next_in_progress_task(path: Path) -> TaskItem | None:
    for task in load_tasks(path):
        if task.status == TaskStatus.IN_PROGRESS:
            return task
    return None


def next_actionable_task(path: Path, *, exclude: set[str] | None = None) -> TaskItem | None:
    """Siguiente tarea pendiente o en progreso (orden TASKS.md)."""
    skip = exclude or set()
    for task in load_tasks(path):
        if task.task_id in skip:
            continue
        if task.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS):
            return task
    return None


def list_actionable_tasks(path: Path) -> list[TaskItem]:
    return [
        task
        for task in load_tasks(path)
        if task.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)
    ]


def tasks_for_story(path: Path, story_id: str) -> list[TaskItem]:
    """Tareas accionables que referencian una historia (US-XXX)."""
    return [
        task
        for task in load_tasks(path)
        if task.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)
        and task.story
        and story_id in task.story
    ]


def list_phases(path: Path) -> list[str]:
    phases: list[str] = []
    for task in load_tasks(path):
        if task.phase and task.phase not in phases:
            phases.append(task.phase)
    return phases


def tasks_in_phase(path: Path, phase: str) -> list[TaskItem]:
    needle = phase.strip().lower()
    return [
        task
        for task in load_tasks(path)
        if task.phase
        and (
            task.phase.strip().lower() == needle
            or needle in task.phase.strip().lower()
        )
    ]


def resolve_scope_tasks(
    path: Path,
    *,
    phase: str | None = None,
    story_ids: list[str] | None = None,
    task_ids: list[str] | None = None,
) -> list[TaskItem]:
    """Tareas del alcance (sin filtrar por estado)."""
    all_tasks = load_tasks(path)
    if task_ids:
        wanted = {tid.strip().upper() for tid in task_ids}
        return [t for t in all_tasks if t.task_id in wanted]
    if story_ids:
        stories = {sid.strip().upper() for sid in story_ids}
        return [t for t in all_tasks if t.story and any(s in t.story.upper() for s in stories)]
    if phase:
        return tasks_in_phase(path, phase)
    return all_tasks


def pending_in_scope(path: Path, tasks: list[TaskItem]) -> list[TaskItem]:
    return [t for t in tasks if t.status != TaskStatus.COMPLETED]


def phase_is_complete(path: Path, phase: str) -> bool:
    tasks = tasks_in_phase(path, phase)
    if not tasks:
        return False
    return all(t.status == TaskStatus.COMPLETED for t in tasks)


def mark_task_status(path: Path, task_id: str, status: TaskStatus) -> bool:
    token = {
        TaskStatus.PENDING: "[ ]",
        TaskStatus.IN_PROGRESS: "[~]",
        TaskStatus.COMPLETED: "[x]",
        TaskStatus.BLOCKED: "[!]",
    }[status]

    lines = path.read_text(encoding="utf-8").splitlines()
    pattern = re.compile(rf"^\|\s*{re.escape(task_id)}\s*\|(.+)\|\s*`(\[[ x~!]\])`\s*\|$")
    updated = False

    for index, line in enumerate(lines):
        match = pattern.match(line.strip())
        if not match:
            continue
        prefix = match.group(1)
        lines[index] = f"| {task_id} |{prefix}| `{token}` |"
        updated = True
        break

    if updated:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return updated
