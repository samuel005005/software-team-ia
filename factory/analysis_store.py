from pathlib import Path

from factory.config import STATE_DIR, ensure_state_dir

ANALYSIS_DIR = STATE_DIR / "analysis"


def analysis_path(task_id: str) -> Path:
    return ANALYSIS_DIR / f"{task_id}.md"


def save_analysis(task_id: str, content: str) -> Path:
    ensure_state_dir()
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    path = analysis_path(task_id)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def load_analysis(task_id: str) -> str | None:
    path = analysis_path(task_id)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()
