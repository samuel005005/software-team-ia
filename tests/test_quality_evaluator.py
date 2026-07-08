import unittest

from quality.quality_evaluator import QualityEvaluator
from review.review_result import ReviewResult


class QualityEvaluatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluator = QualityEvaluator()

    def _review(
        self,
        *,
        approved: bool,
        score: float,
        reviewed_agent: str = "analyst",
    ) -> ReviewResult:
        return ReviewResult(
            reviewed_agent=reviewed_agent,
            approved=approved,
            score=score,
            summary="Test review",
        )

    def test_approved_with_high_score_passes_without_retry(self) -> None:
        decision = self.evaluator.evaluate(
            self._review(approved=True, score=0.94),
        )

        self.assertTrue(decision.passed)
        self.assertFalse(decision.retry)
        self.assertEqual(decision.score, 0.94)
        self.assertIn("score suficiente", decision.reason)

    def test_approved_at_threshold_passes_without_retry(self) -> None:
        decision = self.evaluator.evaluate(
            self._review(approved=True, score=0.75),
        )

        self.assertTrue(decision.passed)
        self.assertFalse(decision.retry)

    def test_not_approved_fails_with_retry(self) -> None:
        decision = self.evaluator.evaluate(
            self._review(approved=False, score=0.9),
        )

        self.assertFalse(decision.passed)
        self.assertTrue(decision.retry)
        self.assertEqual(decision.reason, "Revisión no aprobada")

    def test_approved_with_low_score_fails_with_retry(self) -> None:
        decision = self.evaluator.evaluate(
            self._review(approved=True, score=0.6),
        )

        self.assertFalse(decision.passed)
        self.assertTrue(decision.retry)
        self.assertEqual(decision.reason, "Score por debajo del umbral mínimo")

    def test_decision_metadata_includes_review_context(self) -> None:
        decision = self.evaluator.evaluate(
            self._review(approved=True, score=0.8, reviewed_agent="architect"),
        )

        self.assertEqual(decision.metadata["reviewed_agent"], "architect")
        self.assertTrue(decision.metadata["approved"])
        self.assertEqual(decision.metadata["threshold"], 0.75)

    def test_decision_serializes_via_to_dict(self) -> None:
        decision = self.evaluator.evaluate(
            self._review(approved=True, score=0.94),
        )

        data = decision.to_dict()

        self.assertTrue(data["passed"])
        self.assertFalse(data["retry"])
        self.assertEqual(data["score"], 0.94)
        self.assertIn("reason", data)
        self.assertIn("metadata", data)


if __name__ == "__main__":
    unittest.main()
