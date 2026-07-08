from abc import ABC, abstractmethod
from typing import Any

from tools.tool_executor import ToolExecutor


class BaseAction(ABC):
    """Clase base abstracta para acciones que representan decisiones de un agente."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre identificador de la acción."""
        ...

    @abstractmethod
    def execute(self, tool_executor: ToolExecutor) -> dict[str, Any]:
        """Ejecuta la acción usando el ToolExecutor disponible."""
        ...
