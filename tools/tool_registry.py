from pathlib import Path

from tools.filesystem.create_directory_tool import CreateDirectoryTool
from tools.filesystem.create_file_tool import CreateFileTool
from tools.filesystem.delete_file_tool import DeleteFileTool
from tools.filesystem.list_directory_tool import ListDirectoryTool
from tools.filesystem.read_file_tool import ReadFileTool
from tools.filesystem.write_file_tool import WriteFileTool
from tools.tool import Tool
from tools.tool_descriptor import ToolDescriptor
from workspace.workspace import Workspace

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKSPACE_ROOT = PROJECT_ROOT / "projects"


class ToolRegistry:
    """Registro centralizado de herramientas disponibles en el harness."""

    def __init__(self) -> None:
        self._descriptors: dict[str, ToolDescriptor] = {}
        self._registration_order: list[str] = []

    def register(self, descriptor: ToolDescriptor) -> None:
        if descriptor.name in self._descriptors:
            raise ValueError(
                f"Ya existe una herramienta registrada con name '{descriptor.name}'"
            )

        self._descriptors[descriptor.name] = descriptor
        self._registration_order.append(descriptor.name)

    def get(self, name: str) -> ToolDescriptor | None:
        return self._descriptors.get(name)

    def list_tools(self) -> list[ToolDescriptor]:
        return [self._descriptors[name] for name in self._registration_order]

    def exists(self, name: str) -> bool:
        return name in self._descriptors

    def list_names(self) -> list[str]:
        return list(self._registration_order)

    def create_tool(self, name: str) -> Tool:
        descriptor = self.get(name)
        if descriptor is None:
            raise KeyError(f"No hay herramienta registrada con name '{name}'")
        return descriptor.tool_factory()


def create_default_tool_registry(
    workspace: Workspace | None = None,
) -> ToolRegistry:
    """Construye el registro por defecto de herramientas del harness."""
    active_workspace = workspace or Workspace(str(DEFAULT_WORKSPACE_ROOT))
    registry = ToolRegistry()
    registry.register(
        ToolDescriptor(
            name="create_file",
            description="Crea un archivo de texto",
            capabilities=["filesystem", "create"],
            tool_factory=lambda: CreateFileTool(active_workspace),
        )
    )
    registry.register(
        ToolDescriptor(
            name="read_file",
            description="Lee un archivo de texto",
            capabilities=["filesystem", "read"],
            tool_factory=lambda: ReadFileTool(active_workspace),
        )
    )
    registry.register(
        ToolDescriptor(
            name="write_file",
            description="Sobrescribe un archivo de texto",
            capabilities=["filesystem", "write"],
            tool_factory=lambda: WriteFileTool(active_workspace),
        )
    )
    registry.register(
        ToolDescriptor(
            name="delete_file",
            description="Elimina un archivo",
            capabilities=["filesystem", "delete"],
            tool_factory=lambda: DeleteFileTool(active_workspace),
        )
    )
    registry.register(
        ToolDescriptor(
            name="list_directory",
            description="Lista el contenido de un directorio",
            capabilities=["filesystem", "list"],
            tool_factory=lambda: ListDirectoryTool(active_workspace),
        )
    )
    registry.register(
        ToolDescriptor(
            name="create_directory",
            description="Crea un directorio",
            capabilities=["filesystem", "create"],
            tool_factory=lambda: CreateDirectoryTool(active_workspace),
        )
    )
    return registry
