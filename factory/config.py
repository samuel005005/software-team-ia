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


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
