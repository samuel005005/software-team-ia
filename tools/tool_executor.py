from typing import Any

from tools.base_tool import BaseTool


class ToolExecutor:
    """Registra y ejecuta herramientas disponibles por nombre y acción."""

    def __init__(self, tools: list[BaseTool] | None = None) -> None:
        self._tools: dict[str, BaseTool] = {}
        if tools:
            for tool in tools:
                self.register(tool)

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def execute(
        self,
        tool_name: str,
        action: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tool = self._tools.get(tool_name)
        if tool is None:
            return {
                "success": False,
                "logs": [f"[tool_executor] Herramienta no encontrada: {tool_name}"],
            }

        return tool.execute(action, params or {})
