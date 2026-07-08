from typing import Any

from tools.tool import Tool
from tools.tool_result import ToolResult
from workspace.workspace import Workspace, WorkspaceError


class ReadFileTool(Tool):
    """Lee el contenido de un archivo de texto."""

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Lee el contenido de un archivo de texto"

    def execute(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        if not path:
            return ToolResult.failure_result("El parámetro 'path' es obligatorio")

        try:
            target = self._workspace.resolve(path)
            if not target.is_file():
                return ToolResult.failure_result(f"No es un archivo: {path}")
            content = target.read_text(encoding="utf-8")
        except WorkspaceError as exc:
            return ToolResult.failure_result(str(exc))
        except OSError as exc:
            return ToolResult.failure_result(str(exc))

        return ToolResult.success_result(
            output={"path": str(target), "content": content},
            metadata={"operation": "read_file"},
        )
