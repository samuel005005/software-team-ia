from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class FileSystemTool(BaseTool):
    """Herramienta para operaciones de sistema de archivos usando pathlib."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or PROJECT_ROOT

    @property
    def name(self) -> str:
        return "filesystem"

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        actions = {
            "create_directory": self.create_directory,
            "create_file": self.create_file,
            "read_file": self.read_file,
        }

        handler = actions.get(action)
        if handler is None:
            return {
                "success": False,
                "logs": [f"[filesystem] Acción no soportada: {action}"],
            }

        return handler(**params)

    def _resolve_path(self, path: str | Path) -> Path:
        resolved = Path(path)
        if not resolved.is_absolute():
            resolved = self._base_dir / resolved
        return resolved

    def create_directory(self, path: str | Path) -> dict[str, Any]:
        target = self._resolve_path(path)
        target.mkdir(parents=True, exist_ok=True)
        return {
            "success": True,
            "path": str(target),
            "logs": [f"[filesystem] Directorio creado: {target}"],
        }

    def create_file(self, path: str | Path, content: str = "") -> dict[str, Any]:
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "path": str(target),
            "logs": [f"[filesystem] Archivo creado: {target}"],
        }

    def read_file(self, path: str | Path) -> dict[str, Any]:
        target = self._resolve_path(path)
        content = target.read_text(encoding="utf-8")
        return {
            "success": True,
            "path": str(target),
            "content": content,
            "logs": [f"[filesystem] Archivo leído: {target}"],
        }
