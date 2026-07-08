import unittest
from unittest.mock import MagicMock

from agents.agent_result import AgentResult
from llm.llm_response import LLMResponse
from llm.mock_provider import MockLLMProvider
from llm.provider_error import LLMProviderError
from quality.quality_pipeline import QualityPipeline
from review.reviewer_agent import ReviewerAgent


class QualityPipelineTestCase(unittest.TestCase):
    def _agent_result(
        self,
        *,
        agent_name: str = "Business Analyst",
        output: str = "3 historias de usuario generadas",
        success: bool = True,
    ) -> AgentResult:
        if success:
            return AgentResult.success_result(
                agent_name=agent_name,
                output=output,
            )
        return AgentResult.failure_result(
            agent_name=agent_name,
            output=output,
            issues=["Error de ejecución"],
        )

    def test_evaluate_generates_review_result(self) -> None:
        pipeline = QualityPipeline()
        context = pipeline.evaluate(
            self._agent_result(),
            objective="barberia-app",
        )

        self.assertIsNotNone(context.review_result)
        assert context.review_result is not None
        self.assertEqual(context.review_result.reviewed_agent, "Business Analyst")
        self.assertIn("Revisión determinista", context.review_result.summary)

    def test_evaluate_generates_quality_decision(self) -> None:
        pipeline = QualityPipeline()
        context = pipeline.evaluate(self._agent_result())

        self.assertIsNotNone(context.quality_decision)
        assert context.quality_decision is not None
        self.assertTrue(context.quality_decision.passed)
        self.assertFalse(context.quality_decision.retry)

    def test_evaluate_preserves_agent_result(self) -> None:
        agent_result = self._agent_result()
        pipeline = QualityPipeline()
        context = pipeline.evaluate(agent_result)

        self.assertIs(context.agent_result, agent_result)
        self.assertEqual(context.agent_result.output, "3 historias de usuario generadas")

    def test_evaluate_with_reviewer_mock_provider(self) -> None:
        pipeline = QualityPipeline(reviewer=ReviewerAgent(llm_provider=MockLLMProvider()))
        context = pipeline.evaluate(
            self._agent_result(),
            objective="barberia-app",
        )

        self.assertIsNotNone(context.review_result)
        assert context.review_result is not None
        self.assertEqual(context.review_result.metadata["source"], "reviewer_llm")
        self.assertEqual(context.review_result.score, 0.94)
        self.assertIsNotNone(context.quality_decision)
        assert context.quality_decision is not None
        self.assertTrue(context.quality_decision.passed)

    def test_evaluate_handles_reviewer_fallback(self) -> None:
        mock_provider = MagicMock()
        mock_provider.generate.side_effect = LLMProviderError(
            "Error del proveedor",
            provider="mock",
        )
        pipeline = QualityPipeline(reviewer=ReviewerAgent(llm_provider=mock_provider))
        context = pipeline.evaluate(
            self._agent_result(agent_name="Software Architect"),
            objective="barberia-app",
        )

        self.assertIsNotNone(context.review_result)
        assert context.review_result is not None
        self.assertEqual(context.review_result.summary, "Fallback review")
        self.assertEqual(context.review_result.metadata["source"], "reviewer_fallback")
        self.assertIsNotNone(context.quality_decision)
        assert context.quality_decision is not None
        self.assertTrue(context.quality_decision.passed)

    def test_evaluate_handles_invalid_reviewer_json_via_fallback(self) -> None:
        mock_provider = MagicMock()
        mock_provider.generate.return_value = LLMResponse(
            content="invalid-json",
            provider="mock",
            model="mock-model-v1",
        )
        pipeline = QualityPipeline(reviewer=ReviewerAgent(llm_provider=mock_provider))
        context = pipeline.evaluate(self._agent_result(agent_name="QA Engineer"))

        self.assertEqual(context.review_result.summary, "Fallback review")
        self.assertTrue(context.quality_decision.passed)

    def test_to_dict_serializes_full_context(self) -> None:
        pipeline = QualityPipeline()
        context = pipeline.evaluate(self._agent_result())

        data = context.to_dict()

        self.assertEqual(data["agent_result"]["agent_name"], "Business Analyst")
        self.assertIsNotNone(data["review_result"])
        self.assertIsNotNone(data["quality_decision"])
        self.assertIn("passed", data["quality_decision"])


if __name__ == "__main__":
    unittest.main()
