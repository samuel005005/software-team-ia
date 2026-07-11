from pathlib import Path

from factory.analysis_summarizer import compact_analysis
from factory.config import STATE_DIR, ensure_state_dir, max_analysis_chars
from factory.spec_parser import parse_story_ids

ANALYSIS_DIR = STATE_DIR / "analysis"


def analysis_path(task_id: str) -> Path:
    return ANALYSIS_DIR / f"{task_id}.md"


def story_analysis_path(story_id: str) -> Path:
    return ANALYSIS_DIR / f"_story_{story_id}.md"


def save_analysis(task_id: str, content: str) -> Path:
    ensure_state_dir()
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    path = analysis_path(task_id)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def save_story_analysis(story_id: str, content: str) -> Path:
    ensure_state_dir()
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    path = story_analysis_path(story_id)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def load_analysis_raw(task_id: str) -> str | None:
    path = analysis_path(task_id)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def load_story_analysis(story_id: str) -> str | None:
    path = story_analysis_path(story_id)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def load_analysis(
    task_id: str,
    *,
    story: str | None = None,
    compact: bool = False,
    max_chars: int | None = None,
) -> str | None:
    """Carga análisis de tarea; si no existe, intenta análisis grupal por US."""
    raw = load_analysis_raw(task_id)
    if raw is None and story:
        for story_id in parse_story_ids(story):
            raw = load_story_analysis(story_id)
            if raw:
                break

    if raw is None:
        return None

    if not compact:
        return raw

    limit = max_chars if max_chars is not None else max_analysis_chars()
    return compact_analysis(raw, max_chars=limit)


def has_analysis(task_id: str, *, story: str | None = None) -> bool:
    if analysis_path(task_id).exists():
        return True
    if story:
        for story_id in parse_story_ids(story):
            if story_analysis_path(story_id).exists():
                return True
    return False
