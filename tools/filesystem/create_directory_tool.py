from typing import Any

from tools.tool import Tool
from tools.tool_result import ToolResult
from workspace.workspace import Workspace, WorkspaceError


class CreateDirectoryTool(Tool):
    """Crea un directorio, incluyendo padres si hace falta."""

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "create_directory"

    @property
    def description(self) -> str:
        return "Crea un directorio y sus directorios padres si no existen"

    def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        if not path:
            return ToolResult.failure_result("El parámetro 'path' es obligatorio")

        try:
            target = self._workspace.resolve(path)
            target.mkdir(parents=True, exist_ok=True)
        except WorkspaceError as exc:
            return ToolResult.failure_result(str(exc))
        except OSError as exc:
            return ToolResult.failure_result(str(exc))

        return ToolResult.success_result(
            output={"path": str(target)},
            metadata={"operation": "create_directory"},
        )
