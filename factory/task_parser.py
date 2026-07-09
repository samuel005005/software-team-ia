import re
from pathlib import Path

from factory.models import TaskItem, TaskStatus

TASK_ROW = re.compile(
    r"^\|\s*(T-\d+)\s*\|\s*(.+?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*`(\[[ x~!]\])`\s*\|"
)

_STATUS_MAP = {
    "[ ]": TaskStatus.PENDING,
    "[x]": TaskStatus.COMPLETED,
    "[~]": TaskStatus.IN_PROGRESS,
    "[!]": TaskStatus.BLOCKED,
}


def parse_tasks(tasks_md: str) -> list[TaskItem]:
    items: list[TaskItem] = []
    for index, line in enumerate(tasks_md.splitlines(), start=1):
        match = TASK_ROW.match(line.strip())
        if not match:
            continue
        task_id, title, story, owner, status_token = match.groups()
        items.append(
            TaskItem(
                task_id=task_id,
                title=title.strip(),
                story=story.strip() or None,
                owner=owner.strip(),
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
