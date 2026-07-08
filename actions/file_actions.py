from typing import Any

from actions.base_action import BaseAction
from tools.tool_executor import ToolExecutor


class CreateFileAction(BaseAction):
    """Acción para crear un archivo en el sistema de archivos."""

    def __init__(self, path: str, content: str = "") -> None:
        self.path = path
        self.content = content

    @property
    def name(self) -> str:
        return "create_file"

    def execute(self, tool_executor: ToolExecutor) -> dict[str, Any]:
        return tool_executor.execute(
            "filesystem",
            "create_file",
            {"path": self.path, "content": self.content},
        )


class CreateDirectoryAction(BaseAction):
    """Acción para crear un directorio en el sistema de archivos."""

    def __init__(self, path: str) -> None:
        self.path = path

    @property
    def name(self) -> str:
        return "create_directory"

    def execute(self, tool_executor: ToolExecutor) -> dict[str, Any]:
        return tool_executor.execute(
            "filesystem",
            "create_directory",
            {"path": self.path},
        )
