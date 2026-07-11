import os
from pathlib import Path

from factory.config import REPO_ROOT


def load_dotenv(path: Path | None = None, *, override: bool = False) -> bool:
    """Carga variables desde `.env` en la raíz del repo (sin dependencia externa)."""
    env_path = path or (REPO_ROOT / ".env")
    if not env_path.is_file():
        return False

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        if not override and key in os.environ:
            continue
        os.environ[key] = value

    return True
