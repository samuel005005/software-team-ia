import json
from datetime import datetime, timezone
from typing import Any

from factory.config import STATE_FILE, ensure_state_dir
from factory.models import FactoryRole, RunResult


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {"runs": []}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def append_run(result: RunResult) -> None:
    ensure_state_dir()
    state = load_state()
    state.setdefault("runs", []).append(
        {
            "timestamp": _now_iso(),
            "role": result.role.value,
            "task_id": result.task_id,
            "status": result.status,
            "agent_id": result.agent_id,
            "summary": (result.summary or "")[:2000],
            "error": result.error,
        }
    )
    state["last_run"] = state["runs"][-1]
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
