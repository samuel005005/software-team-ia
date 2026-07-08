from abc import ABC, abstractmethod
from typing import Any

from tools.tool_result import ToolResult


class Tool(ABC):
    """Clase base abstracta para herramientas del harness."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre identificador de la herramienta."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Descripción breve de la herramienta."""

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """Ejecuta la herramienta con los parámetros dados."""
