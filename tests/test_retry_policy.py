import unittest

from execution.retry_context import RetryContext
from execution.retry_policy import RetryPolicy
from quality.quality_decision import QualityDecision


class RetryPolicyTestCase(unittest.TestCase):
    def _quality_decision(self, *, retry: bool) -> QualityDecision:
        return QualityDecision(
            passed=not retry,
            retry=retry,
            score=0.5 if retry else 0.9,
            reason="Test decision",
        )

    def test_default_max_retries_is_three(self) -> None:
        policy = RetryPolicy()

        self.assertEqual(policy.max_retries, 3)

    def test_retry_allowed_when_quality_requests_it(self) -> None:
        policy = RetryPolicy(max_retries=3)
        decision = self._quality_decision(retry=True)

        self.assertTrue(policy.should_retry(decision, retry_count=0))
        self.assertTrue(policy.should_retry(decision, retry_count=2))

    def test_retry_blocked_when_quality_decision_retry_is_false(self) -> None:
        policy = RetryPolicy(max_retries=3)
        decision = self._quality_decision(retry=False)

        self.assertFalse(policy.should_retry(decision, retry_count=0))

    def test_retry_blocked_when_limit_reached(self) -> None:
        policy = RetryPolicy(max_retries=3)
        decision = self._quality_decision(retry=True)

        self.assertFalse(policy.should_retry(decision, retry_count=3))
        self.assertFalse(policy.should_retry(decision, retry_count=5))

    def test_retry_context_serializes_to_dict(self) -> None:
        decision = self._quality_decision(retry=True)
        context = RetryContext(
            agent_name="Business Analyst",
            retry_count=1,
            max_retries=3,
            last_quality_decision=decision,
        )

        data = context.to_dict()

        self.assertEqual(data["agent_name"], "Business Analyst")
        self.assertEqual(data["retry_count"], 1)
        self.assertEqual(data["max_retries"], 3)
        self.assertTrue(data["last_quality_decision"]["retry"])
        self.assertEqual(data["last_quality_decision"]["reason"], "Test decision")


if __name__ == "__main__":
    unittest.main()
