from pathlib import Path

from factory.task_parser import list_actionable_tasks, next_actionable_task

SAMPLE = """
| T-040 | A | US-1 | Dev | `[x]` |
| T-044 | B | US-2 | Dev | `[ ]` |
| T-045 | C | US-3 | Dev | `[~]` |
| T-050 | D | US-4 | Dev | `[ ]` |
"""


def test_next_actionable_prefers_pending_order(tmp_path: Path) -> None:
    path = tmp_path / "TASKS.md"
    path.write_text(SAMPLE, encoding="utf-8")
    task = next_actionable_task(path)
    assert task is not None
    assert task.task_id == "T-044"


def test_next_actionable_skips_excluded(tmp_path: Path) -> None:
    path = tmp_path / "TASKS.md"
    path.write_text(SAMPLE, encoding="utf-8")
    task = next_actionable_task(path, exclude={"T-044"})
    assert task.task_id == "T-045"


def test_list_actionable_tasks(tmp_path: Path) -> None:
    path = tmp_path / "TASKS.md"
    path.write_text(SAMPLE, encoding="utf-8")
    ids = [t.task_id for t in list_actionable_tasks(path)]
    assert ids == ["T-044", "T-045", "T-050"]
