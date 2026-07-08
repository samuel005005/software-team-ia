from agents.agent_result import AgentResult
from quality.quality_context import QualityContext
from quality.quality_evaluator import QualityEvaluator
from review.reviewer_agent import ReviewerAgent


class QualityPipeline:
    """Coordina la revisión y evaluación de calidad de un AgentResult."""

    def __init__(
        self,
        reviewer: ReviewerAgent | None = None,
        evaluator: QualityEvaluator | None = None,
    ) -> None:
        self._reviewer = reviewer or ReviewerAgent()
        self._evaluator = evaluator or QualityEvaluator()

    def evaluate(
        self,
        agent_result: AgentResult,
        *,
        objective: str = "",
        review_criteria: list[str] | None = None,
    ) -> QualityContext:
        review_result = self._reviewer.review(
            reviewed_agent=agent_result.agent_name,
            objective=objective,
            agent_output=agent_result.output,
            review_criteria=review_criteria,
        )
        quality_decision = self._evaluator.evaluate(review_result)

        return QualityContext(
            agent_result=agent_result,
            review_result=review_result,
            quality_decision=quality_decision,
        )
