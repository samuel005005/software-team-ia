from pathlib import Path

from factory.models import TaskStatus
from factory.task_parser import load_tasks, mark_task_status, next_pending_task, parse_tasks

SAMPLE = """
| ID | Tarea | Historia | Responsable | Estado |
|----|-------|----------|-------------|--------|
| T-040 | Listar servicios | US-003 | Developer | `[x]` |
| T-044 | Gestionar clientes | US-017 | Developer | `[ ]` |
| T-045 | Horarios local | US-016 | Developer | `[~]` |
"""


def test_parse_tasks(tmp_path: Path) -> None:
    tasks = parse_tasks(SAMPLE)
    assert len(tasks) == 3
    assert tasks[1].task_id == "T-044"
    assert tasks[1].status == TaskStatus.PENDING


def test_next_pending_task(tmp_path: Path) -> None:
    path = tmp_path / "TASKS.md"
    path.write_text(SAMPLE, encoding="utf-8")
    task = next_pending_task(path)
    assert task is not None
    assert task.task_id == "T-044"


def test_mark_task_status(tmp_path: Path) -> None:
    path = tmp_path / "TASKS.md"
    path.write_text(SAMPLE, encoding="utf-8")
    assert mark_task_status(path, "T-044", TaskStatus.IN_PROGRESS)
    updated = path.read_text(encoding="utf-8")
    assert "T-044" in updated
    assert "[~]" in updated
    assert load_tasks(path)[1].status == TaskStatus.IN_PROGRESS


SAMPLE_4COL = """
| ID | Tarea | Responsable | Estado |
|----|-------|-------------|--------|
| T-001 | Setup base | Developer | `[x]` |
| T-070 | Tests dominio | Developer | `[ ]` |
"""


def test_parse_tasks_4_columns() -> None:
    tasks = parse_tasks(SAMPLE_4COL)
    assert len(tasks) == 2
    assert tasks[0].task_id == "T-001"
    assert tasks[0].story is None
    assert tasks[0].status == TaskStatus.COMPLETED
    assert tasks[1].task_id == "T-070"
    assert tasks[1].status == TaskStatus.PENDING


def test_next_pending_task_4_columns(tmp_path: Path) -> None:
    path = tmp_path / "TASKS.md"
    path.write_text(SAMPLE_4COL, encoding="utf-8")
    task = next_pending_task(path)
    assert task is not None
    assert task.task_id == "T-070"


def test_load_real_tasks_md_includes_phase_7() -> None:
    path = Path(__file__).resolve().parents[2] / "docs" / "TASKS.md"
    tasks = load_tasks(path)
    ids = [t.task_id for t in tasks]
    assert "T-001" in ids
    assert "T-070" in ids
    assert "T-073" in ids
    pending = [t.task_id for t in tasks if t.status == TaskStatus.PENDING]
    assert pending[0] == "T-070"
