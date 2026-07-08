from dataclasses import asdict, dataclass
from typing import Any

from quality.quality_decision import QualityDecision


@dataclass
class RetryContext:
    """Contexto de reintento para un agente evaluado por calidad."""

    agent_name: str
    retry_count: int
    max_retries: int
    last_quality_decision: QualityDecision

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "last_quality_decision": self.last_quality_decision.to_dict(),
        }
