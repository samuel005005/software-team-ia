from typing import Any

from tools.tool import Tool
from tools.tool_result import ToolResult
from workspace.workspace import Workspace, WorkspaceError


class CreateFileTool(Tool):
    """Crea un archivo de texto, incluyendo directorios padres si hace falta."""

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "create_file"

    @property
    def description(self) -> str:
        return "Crea un archivo de texto y sus directorios padres si no existen"

    def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        if not path:
            return ToolResult.failure_result("El parámetro 'path' es obligatorio")

        content = kwargs.get("content", "")
        if not isinstance(content, str):
            return ToolResult.failure_result("El parámetro 'content' debe ser un string")

        try:
            target = self._workspace.resolve(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        except WorkspaceError as exc:
            return ToolResult.failure_result(str(exc))
        except OSError as exc:
            return ToolResult.failure_result(str(exc))

        return ToolResult.success_result(
            output={"path": str(target), "content": content},
            metadata={"operation": "create_file"},
        )
