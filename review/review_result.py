from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ReviewResult:
    """Resultado estructurado de una revisión de salida de agente."""

    reviewed_agent: str
    approved: bool
    score: float
    summary: str
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
