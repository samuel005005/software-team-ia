from dataclasses import dataclass
from typing import Any

from agents.agent_result import AgentResult
from quality.quality_decision import QualityDecision
from review.review_result import ReviewResult


@dataclass
class QualityContext:
    """Contexto de calidad que une el resultado del agente, la revisión y la decisión."""

    agent_result: AgentResult
    review_result: ReviewResult | None = None
    quality_decision: QualityDecision | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_result": self.agent_result.to_dict(),
            "review_result": (
                self.review_result.to_dict() if self.review_result is not None else None
            ),
            "quality_decision": (
                self.quality_decision.to_dict()
                if self.quality_decision is not None
                else None
            ),
        }
