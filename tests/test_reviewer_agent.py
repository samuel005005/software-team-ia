import json
import unittest
from unittest.mock import MagicMock

from llm.llm_response import LLMResponse
from llm.mock_provider import MockLLMProvider
from llm.provider_error import LLMProviderError
from review.reviewer_agent import ReviewerAgent


class ReviewerAgentTestCase(unittest.TestCase):
    def test_review_without_provider_uses_deterministic_logic(self) -> None:
        reviewer = ReviewerAgent()
        result = reviewer.review(
            reviewed_agent="analyst",
            objective="barberia-app",
            agent_output={"user_stories": ["story-1"]},
        )

        self.assertTrue(result.approved)
        self.assertEqual(result.score, 1.0)
        self.assertEqual(result.metadata["source"], "reviewer_v1")
        self.assertEqual(result.issues, [])

    def test_review_without_provider_rejects_empty_output(self) -> None:
        reviewer = ReviewerAgent()
        result = reviewer.review(
            reviewed_agent="analyst",
            objective="barberia-app",
            agent_output="",
        )

        self.assertFalse(result.approved)
        self.assertEqual(result.score, 0.5)
        self.assertEqual(result.issues, ["Salida vacía o ausente"])

    def test_review_with_mock_provider(self) -> None:
        reviewer = ReviewerAgent(llm_provider=MockLLMProvider())
        result = reviewer.review(
            reviewed_agent="analyst",
            objective="barberia-app",
            agent_output={"user_stories": ["story-1", "story-2"]},
        )

        self.assertTrue(result.approved)
        self.assertEqual(result.score, 0.94)
        self.assertEqual(result.metadata["source"], "reviewer_llm")
        self.assertIn("Mock review", result.summary)

    def test_review_falls_back_on_invalid_json(self) -> None:
        mock_provider = MagicMock()
        mock_provider.generate.return_value = LLMResponse(
            content="invalid-json",
            provider="mock",
            model="mock-model-v1",
        )

        reviewer = ReviewerAgent(llm_provider=mock_provider)
        result = reviewer.review(
            reviewed_agent="architect",
            objective="barberia-app",
            agent_output={"architecture": "Flutter"},
        )

        self.assertTrue(result.approved)
        self.assertEqual(result.score, 1.0)
        self.assertEqual(result.summary, "Fallback review")
        self.assertEqual(result.metadata["source"], "reviewer_fallback")

    def test_review_falls_back_on_provider_exception(self) -> None:
        mock_provider = MagicMock()
        mock_provider.generate.side_effect = LLMProviderError(
            "Error del proveedor",
            provider="mock",
        )

        reviewer = ReviewerAgent(llm_provider=mock_provider)
        result = reviewer.review(
            reviewed_agent="developer",
            objective="barberia-app",
            agent_output={"tasks": [{"id": 1}]},
        )

        self.assertTrue(result.approved)
        self.assertEqual(result.summary, "Fallback review")
        self.assertEqual(result.metadata["source"], "reviewer_fallback")

    def test_review_falls_back_on_parser_validation_error(self) -> None:
        mock_provider = MagicMock()
        mock_provider.generate.return_value = LLMResponse(
            content=json.dumps(
                {
                    "approved": True,
                    "score": 0.9,
                }
            ),
            provider="mock",
            model="mock-model-v1",
        )

        reviewer = ReviewerAgent(llm_provider=mock_provider)
        result = reviewer.review(
            reviewed_agent="qa",
            objective="barberia-app",
            agent_output={"qa_report": "ok"},
        )

        self.assertEqual(result.summary, "Fallback review")
        self.assertEqual(result.metadata["source"], "reviewer_fallback")


if __name__ == "__main__":
    unittest.main()
