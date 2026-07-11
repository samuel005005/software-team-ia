from factory.models import TaskStatus
from factory.prompt_builder import build_role_prompt, build_analyze_prompt
from factory.models import FactoryRole, TaskItem


def _sample_task() -> TaskItem:
    return TaskItem(
        task_id="T-010",
        title="Crear API",
        story="US-001",
        owner="Developer",
        status=TaskStatus.PENDING,
        line_number=1,
    )


def test_lean_prompt_is_shorter_than_full() -> None:
    task = _sample_task()
    lean = build_role_prompt(FactoryRole.DEVELOPER, task=task, lean=True)
    full = build_role_prompt(FactoryRole.DEVELOPER, task=task, lean=False)
    assert len(lean) < len(full)
    assert ".cursor/rules/developer.md" in lean
    assert "## Rule (léela en el repo)" in lean


def test_lean_analyze_references_files() -> None:
    task = _sample_task()
    prompt = build_analyze_prompt(task, lean=True)
    assert ".cursor/rules/architect.md" in prompt
    assert "No codifiques" in prompt or "no implement" in prompt.lower()
