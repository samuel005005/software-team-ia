from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Clase base abstracta para todas las herramientas del sistema."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre identificador de la herramienta."""
        ...

    @abstractmethod
    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """Ejecuta una acción de la herramienta con los parámetros dados."""
        ...
