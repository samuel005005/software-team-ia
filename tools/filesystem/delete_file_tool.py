from typing import Any

from tools.tool import Tool
from tools.tool_result import ToolResult
from workspace.workspace import Workspace, WorkspaceError


class DeleteFileTool(Tool):
    """Elimina un archivo del sistema de archivos."""

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "delete_file"

    @property
    def description(self) -> str:
        return "Elimina un archivo del sistema de archivos"

    def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        if not path:
            return ToolResult.failure_result("El parámetro 'path' es obligatorio")

        try:
            target = self._workspace.resolve(path)
            if not target.is_file():
                return ToolResult.failure_result(f"No es un archivo: {path}")
            target.unlink()
        except WorkspaceError as exc:
            return ToolResult.failure_result(str(exc))
        except OSError as exc:
            return ToolResult.failure_result(str(exc))

        return ToolResult.success_result(
            output={"path": str(target)},
            metadata={"operation": "delete_file"},
        )
