from typing import Any

from tools.tool import Tool
from tools.tool_result import ToolResult
from workspace.workspace import Workspace, WorkspaceError


class WriteFileTool(Tool):
    """Sobrescribe el contenido de un archivo existente."""

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Sobrescribe el contenido de un archivo existente"

    def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        if not path:
            return ToolResult.failure_result("El parámetro 'path' es obligatorio")

        content = kwargs.get("content")
        if content is None:
            return ToolResult.failure_result("El parámetro 'content' es obligatorio")
        if not isinstance(content, str):
            return ToolResult.failure_result("El parámetro 'content' debe ser un string")

        try:
            target = self._workspace.resolve(path)
            if not target.is_file():
                return ToolResult.failure_result(f"El archivo no existe: {path}")
            target.write_text(content, encoding="utf-8")
        except WorkspaceError as exc:
            return ToolResult.failure_result(str(exc))
        except OSError as exc:
            return ToolResult.failure_result(str(exc))

        return ToolResult.success_result(
            output={"path": str(target), "content": content},
            metadata={"operation": "write_file"},
        )
