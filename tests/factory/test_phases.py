from pathlib import Path

from factory.models import TaskStatus
from factory.task_parser import list_phases, parse_tasks, phase_is_complete, resolve_scope_tasks, tasks_in_phase

SAMPLE_PHASES = """
## Fase 1 — Fundamentos

| T-001 | Setup | US-001 | Dev | `[x]` |
| T-002 | API base | US-001 | Dev | `[ ]` |

## Fase 2 — Features

| T-010 | Pantalla login | US-002 | Dev | `[ ]` |
"""


def test_parse_tasks_assign_phase() -> None:
    tasks = parse_tasks(SAMPLE_PHASES)
    assert tasks[0].phase == "Fase 1 — Fundamentos"
    assert tasks[2].phase == "Fase 2 — Features"


def test_tasks_in_phase_partial_name(tmp_path: Path) -> None:
    path = tmp_path / "TASKS.md"
    path.write_text(SAMPLE_PHASES, encoding="utf-8")
    phase_tasks = tasks_in_phase(path, "Fase 1")
    assert len(phase_tasks) == 2
    assert phase_tasks[0].task_id == "T-001"


def test_phase_is_complete(tmp_path: Path) -> None:
    path = tmp_path / "TASKS.md"
    path.write_text(SAMPLE_PHASES, encoding="utf-8")
    assert phase_is_complete(path, "Fase 1") is False
    assert phase_is_complete(path, "Fase 2") is False


def test_list_phases(tmp_path: Path) -> None:
    path = tmp_path / "TASKS.md"
    path.write_text(SAMPLE_PHASES, encoding="utf-8")
    phases = list_phases(path)
    assert len(phases) == 2


def test_resolve_scope_by_story(tmp_path: Path) -> None:
    path = tmp_path / "TASKS.md"
    path.write_text(SAMPLE_PHASES, encoding="utf-8")
    tasks = resolve_scope_tasks(path, story_ids=["US-002"])
    assert len(tasks) == 1
    assert tasks[0].task_id == "T-010"
