from factory.cli import _resolve_run_mode


def test_run_next_alias() -> None:
    task_id, run_once, run_all = _resolve_run_mode("next", once_flag=False)
    assert task_id is None
    assert run_once is True
    assert run_all is False


def test_run_all_alias() -> None:
    task_id, run_once, run_all = _resolve_run_mode("all", once_flag=False)
    assert task_id is None
    assert run_once is False
    assert run_all is True


def test_run_task_id() -> None:
    task_id, run_once, run_all = _resolve_run_mode("T-060", once_flag=False)
    assert task_id == "T-060"
    assert run_once is False
    assert run_all is False


def test_run_empty_defaults_to_all() -> None:
    task_id, run_once, run_all = _resolve_run_mode(None, once_flag=False)
    assert task_id is None
    assert run_once is False
    assert run_all is True
