from pathlib import Path

from factory.models import QAScope
from factory.orchestrator import SDDOrchestrator


def test_resolve_auto_release_scope_when_phase_complete(tmp_path: Path) -> None:
    tasks = """
## Fase 1 — MVP

| T-001 | A | US-001 | Dev | `[x]` |
| T-002 | B | US-001 | Dev | `[x]` |
"""
    path = tmp_path / "TASKS.md"
    path.write_text(tasks, encoding="utf-8")
    orch = SDDOrchestrator(tasks_path=path, auto_release=True)

    scope = orch._resolve_auto_release_scope("T-002")
    assert scope is not None
    assert scope.phase == "Fase 1 — MVP"


def test_resolve_auto_release_scope_when_phase_incomplete(tmp_path: Path) -> None:
    tasks = """
## Fase 1 — MVP

| T-001 | A | US-001 | Dev | `[x]` |
| T-002 | B | US-001 | Dev | `[ ]` |
"""
    path = tmp_path / "TASKS.md"
    path.write_text(tasks, encoding="utf-8")
    orch = SDDOrchestrator(tasks_path=path, auto_release=True)

    assert orch._resolve_auto_release_scope("T-001") is None


def test_finalize_skips_auto_release_when_disabled(tmp_path: Path) -> None:
    tasks = """
## Fase 1 — MVP

| T-001 | A | US-001 | Dev | `[x]` |
"""
    path = tmp_path / "TASKS.md"
    path.write_text(tasks, encoding="utf-8")
    orch = SDDOrchestrator(tasks_path=path, auto_release=False, dry_run=True)

    from factory.models import FactoryRole, RunResult

    results = [
        RunResult(
            role=FactoryRole.DEVELOPER,
            task_id="T-001",
            status="completed",
            agent_id=None,
            summary="ok",
        )
    ]
    out = orch._finalize_dev_batch(results, "T-001")
    assert len(out) == 1
