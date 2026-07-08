from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    """Respuesta normalizada de un proveedor LLM."""

    content: str
    provider: str
    model: str
    tokens_input: int | None = None
    tokens_output: int | None = None
    duration_ms: int | None = None
    metadata: dict[str, str] = field(default_factory=dict)
