from typing import Any


class ParserError(Exception):
    """Error al parsear la respuesta de un proveedor LLM."""

    def __init__(self, message: str, *, agent_name: str | None = None) -> None:
        self.agent_name = agent_name
        super().__init__(message)
