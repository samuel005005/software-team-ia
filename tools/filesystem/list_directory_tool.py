from typing import Any

from tools.tool import Tool
from tools.tool_result import ToolResult
from workspace.workspace import Workspace, WorkspaceError


class ListDirectoryTool(Tool):
    """Lista el contenido de un directorio."""

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return "Lista archivos y directorios dentro de una ruta del workspace"

    def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")
        if not isinstance(path, str) or not path.strip():
            return ToolResult.failure_result("El parámetro 'path' es obligatorio")

        try:
            target = self._workspace.resolve(path)
            if not target.is_dir():
                return ToolResult.failure_result(f"No es un directorio: {path}")
            entries = sorted(entry.name for entry in target.iterdir())
        except WorkspaceError as exc:
            return ToolResult.failure_result(str(exc))
        except OSError as exc:
            return ToolResult.failure_result(str(exc))

        return ToolResult.success_result(
            output={"path": str(target), "entries": entries},
            metadata={"operation": "list_directory"},
        )
