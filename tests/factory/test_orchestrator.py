from factory.models import TaskItem, TaskStatus
from factory.orchestrator import should_skip_analyze


def _task(**kwargs) -> TaskItem:
    defaults = {
        "task_id": "T-001",
        "title": "Test",
        "story": "US-001",
        "owner": "Developer",
        "status": TaskStatus.PENDING,
        "line_number": 1,
        "skip_analyze": False,
        "force_analyze": False,
    }
    defaults.update(kwargs)
    return TaskItem(**defaults)


def test_should_skip_when_task_marked_simple() -> None:
    task = _task(skip_analyze=True)
    assert should_skip_analyze(task) is True


def test_should_force_analyze_overrides_reuse() -> None:
    task = _task(force_analyze=True)
    assert should_skip_analyze(task, reuse_if_exists=True) is False


def test_should_skip_when_flag_skip_phase() -> None:
    task = _task()
    assert should_skip_analyze(task, skip_phase=True) is True
