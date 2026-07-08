from dataclasses import dataclass


@dataclass
class LLMRequest:
    """Solicitud de generación enviada a un proveedor LLM."""

    system_prompt: str
    user_prompt: str
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
