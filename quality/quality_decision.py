from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class QualityDecision:
    """Decisión de calidad derivada de una revisión de agente."""

    passed: bool
    retry: bool
    score: float
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
