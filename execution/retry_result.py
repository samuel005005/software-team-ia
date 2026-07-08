from dataclasses import dataclass, field
from typing import Any

from agents.agent_result import AgentResult
from quality.quality_context import QualityContext


@dataclass
class RetryResult:
    """Resultado agregado de una ejecución con posibles reintentos."""

    final_result: AgentResult
    attempts: int
    quality_context: QualityContext
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "final_result": self.final_result.to_dict(),
            "attempts": self.attempts,
            "quality_context": self.quality_context.to_dict(),
            "history": self.history,
        }
