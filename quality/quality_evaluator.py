from quality.quality_decision import QualityDecision
from review.review_result import ReviewResult

PASS_SCORE_THRESHOLD = 0.75


class QualityEvaluator:
    """Evalúa un ReviewResult y produce una decisión de calidad reutilizable."""

    def __init__(self, pass_score_threshold: float = PASS_SCORE_THRESHOLD) -> None:
        self._pass_score_threshold = pass_score_threshold

    def evaluate(self, review: ReviewResult) -> QualityDecision:
        if not review.approved:
            return QualityDecision(
                passed=False,
                retry=True,
                score=review.score,
                reason="Revisión no aprobada",
                metadata={
                    "reviewed_agent": review.reviewed_agent,
                    "approved": review.approved,
                    "threshold": self._pass_score_threshold,
                },
            )

        if review.score >= self._pass_score_threshold:
            return QualityDecision(
                passed=True,
                retry=False,
                score=review.score,
                reason="Revisión aprobada con score suficiente",
                metadata={
                    "reviewed_agent": review.reviewed_agent,
                    "approved": review.approved,
                    "threshold": self._pass_score_threshold,
                },
            )

        return QualityDecision(
            passed=False,
            retry=True,
            score=review.score,
            reason="Score por debajo del umbral mínimo",
            metadata={
                "reviewed_agent": review.reviewed_agent,
                "approved": review.approved,
                "threshold": self._pass_score_threshold,
            },
        )
