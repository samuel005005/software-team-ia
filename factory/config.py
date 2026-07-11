import os
from pathlib import Path

from factory.models import FactoryRole, ModelTier

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
PROJECTS_DIR = REPO_ROOT / "projects"
PROMPTS_DIR = REPO_ROOT / "prompts"
RULES_DIR = REPO_ROOT / ".cursor" / "rules"
SKILLS_DIR = REPO_ROOT / ".cursor" / "skills"
STATE_DIR = REPO_ROOT / ".factory"
STATE_FILE = STATE_DIR / "state.json"

DEFAULT_MODEL = os.getenv("FACTORY_MODEL", "composer-2.5")
DEFAULT_CWD = Path(os.getenv("FACTORY_CWD", str(REPO_ROOT)))

# Override opcional por rol: FACTORY_MODEL_DEVELOPER, FACTORY_MODEL_ARCHITECT, …
_ROLE_ENV = {
    FactoryRole.PRODUCT_MANAGER: "FACTORY_MODEL_PM",
    FactoryRole.ARCHITECT: "FACTORY_MODEL_ARCHITECT",
    FactoryRole.DEVELOPER: "FACTORY_MODEL_DEVELOPER",
    FactoryRole.QA: "FACTORY_MODEL_QA",
    FactoryRole.REVIEWER: "FACTORY_MODEL_REVIEWER",
    FactoryRole.SECURITY: "FACTORY_MODEL_SECURITY",
}

_ANALYSIS_ROLES = {
    FactoryRole.PRODUCT_MANAGER,
    FactoryRole.ARCHITECT,
    FactoryRole.REVIEWER,
    FactoryRole.SECURITY,
}

_DEFAULT_TIER_BY_ROLE: dict[FactoryRole, ModelTier] = {
    FactoryRole.PRODUCT_MANAGER: "smart",
    FactoryRole.ARCHITECT: "smart",
    FactoryRole.REVIEWER: "smart",
    FactoryRole.SECURITY: "smart",
    FactoryRole.DEVELOPER: "fast",
    FactoryRole.QA: "fast",
}


def _fallback_model() -> str:
    return os.getenv("FACTORY_MODEL", "composer-2.5")


def model_for_tier(tier: ModelTier) -> str:
    """Resuelve slug de modelo para un tier (smart / fast / cheap)."""
    fallback = _fallback_model()
    env_by_tier = {
        "smart": os.getenv("FACTORY_MODEL_SMART", fallback),
        "fast": os.getenv("FACTORY_MODEL_FAST", fallback),
        "cheap": os.getenv("FACTORY_MODEL_CHEAP", os.getenv("FACTORY_MODEL_FAST", fallback)),
    }
    return env_by_tier[tier]


def model_for_role(role: FactoryRole, *, tier: ModelTier | None = None) -> str:
    """Resuelve el modelo según rol, tier explícito o override por rol."""
    env_key = _ROLE_ENV.get(role)
    if env_key and os.getenv(env_key):
        return os.environ[env_key]

    resolved_tier = tier or _DEFAULT_TIER_BY_ROLE.get(role, "fast")
    return model_for_tier(resolved_tier)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def lean_prompt_enabled() -> bool:
    """Prompts por referencia a archivos (menos tokens que inline)."""
    return _env_bool("FACTORY_LEAN_PROMPT", True)


def single_session_enabled() -> bool:
    """Análisis + dev en un solo agente (reutiliza contexto)."""
    return _env_bool("FACTORY_SINGLE_SESSION", True)


def max_analysis_chars() -> int:
    return _env_int("FACTORY_MAX_ANALYSIS_CHARS", 4000)


def max_spec_chars() -> int:
    return _env_int("FACTORY_MAX_SPEC_CHARS", 6000)


def auto_release_enabled() -> bool:
    """Al completar una fase, ejecutar QA + Review + Security + gate."""
    return _env_bool("FACTORY_AUTO_RELEASE", True)


def auto_release_include_review() -> bool:
    return _env_bool("FACTORY_AUTO_RELEASE_REVIEW", True)


def auto_release_include_security() -> bool:
    return _env_bool("FACTORY_AUTO_RELEASE_SECURITY", True)


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
