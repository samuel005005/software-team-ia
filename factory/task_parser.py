import re
from pathlib import Path

from factory.models import TaskItem, TaskStatus

STATUS_TOKEN = r"`(\[[ x~!]\])`"

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


def _parse_task_row(line: str) -> tuple[str, str, str | None, str, str] | None:
    stripped = line.strip()
    match_5 = TASK_ROW_5COL.match(stripped)
    if match_5:
        task_id, title, story, owner, status_token = match_5.groups()
        return task_id, title, story.strip() or None, owner.strip(), status_token

    match_4 = TASK_ROW_4COL.match(stripped)
    if match_4:
        task_id, title, owner, status_token = match_4.groups()
        return task_id, title, None, owner.strip(), status_token

    return None


def parse_tasks(tasks_md: str) -> list[TaskItem]:
    items: list[TaskItem] = []
    for index, line in enumerate(tasks_md.splitlines(), start=1):
        parsed = _parse_task_row(line)
        if parsed is None:
            continue
        task_id, title, story, owner, status_token = parsed
        items.append(
            TaskItem(
                task_id=task_id,
                title=title.strip(),
                story=story,
                owner=owner,
                status=_STATUS_MAP[status_token],
                line_number=index,
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
