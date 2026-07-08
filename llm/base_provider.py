from abc import ABC, abstractmethod

from llm.llm_request import LLMRequest
from llm.llm_response import LLMResponse


class LLMProvider(ABC):
    """Interfaz abstracta para proveedores de modelos de lenguaje."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nombre identificador del proveedor."""
        ...

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Genera una respuesta a partir de la solicitud dada."""
        ...
