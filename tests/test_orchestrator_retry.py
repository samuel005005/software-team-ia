import unittest
from unittest.mock import MagicMock

from agents.agent_result import AgentResult
from agents.base_agent import BaseAgent
from execution.retry_executor import RetryExecutor
from execution.retry_policy import RetryPolicy
from orchestrator.orchestrator import Orchestrator
from quality.quality_context import QualityContext
from quality.quality_decision import QualityDecision
from quality.quality_pipeline import QualityPipeline
from review.review_result import ReviewResult
from state.project_state import ProjectState


class _StoryAgent(BaseAgent):
    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def process(self, state: ProjectState) -> ProjectState:
        state.user_stories.append(f"story-from-{self._name}")
        return state

    def build_output_summary(self, state: ProjectState) -> str:
        return f"{len(state.user_stories)} historias"


class OrchestratorRetryTestCase(unittest.TestCase):
    def _state(self) -> ProjectState:
        return ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil",
        )

    def _quality_context(
        self,
        *,
        agent_result: AgentResult,
        retry: bool,
        score: float = 0.5,
    ) -> QualityContext:
        return QualityContext(
            agent_result=agent_result,
            review_result=ReviewResult(
                reviewed_agent=agent_result.agent_name,
                approved=not retry,
                score=score,
                summary="Test review",
            ),
            quality_decision=QualityDecision(
                passed=not retry,
                retry=retry,
                score=score,
                reason="Test decision",
            ),
        )

    def _pipeline_with_decisions(self, decisions: list[bool]) -> QualityPipeline:
        pipeline = MagicMock(spec=QualityPipeline)
        contexts: list[QualityContext] = []

        def evaluate(agent_result: AgentResult, **kwargs: object) -> QualityContext:
            retry = decisions[min(len(contexts), len(decisions) - 1)]
            context = self._quality_context(agent_result=agent_result, retry=retry)
            contexts.append(context)
            return context

        pipeline.evaluate.side_effect = evaluate
        return pipeline

    def test_normal_flow_registers_single_history_record_with_metadata(self) -> None:
        agent = _StoryAgent("Business Analyst")
        orchestrator = Orchestrator(
            agents=[agent],
            retry_executor=RetryExecutor(
                quality_pipeline=self._pipeline_with_decisions([False]),
            ),
        )

        result = orchestrator.run(self._state())

        records = result.execution_history.get_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].metadata["attempts"], 1)
        self.assertEqual(records[0].metadata["retry_count"], 0)
        self.assertEqual(records[0].metadata["quality_score"], 0.5)
        self.assertEqual(result.user_stories, ["story-from-Business Analyst"])

    def test_retry_flow_registers_metadata_and_only_final_state(self) -> None:
        agent = _StoryAgent("Business Analyst")
        orchestrator = Orchestrator(
            agents=[agent],
            retry_executor=RetryExecutor(
                quality_pipeline=self._pipeline_with_decisions([True, False]),
                max_retries=3,
            ),
        )

        result = orchestrator.run(self._state())

        record = result.execution_history.get_last()
        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.metadata["attempts"], 2)
        self.assertEqual(record.metadata["retry_count"], 1)
        self.assertEqual(len(result.user_stories), 1)
        self.assertEqual(result.user_stories[0], "story-from-Business Analyst")

    def test_exhausted_retry_uses_final_attempt_metadata(self) -> None:
        agent = _StoryAgent("Business Analyst")
        orchestrator = Orchestrator(
            agents=[agent],
            retry_executor=RetryExecutor(
                quality_pipeline=self._pipeline_with_decisions([True, True, True]),
                retry_policy=RetryPolicy(max_retries=2),
                max_retries=2,
            ),
        )

        result = orchestrator.run(self._state())

        record = result.execution_history.get_last()
        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.metadata["attempts"], 3)
        self.assertEqual(record.metadata["retry_count"], 2)
        self.assertEqual(len(result.user_stories), 1)

    def test_multiple_agents_each_receive_only_final_previous_state(self) -> None:
        analyst = _StoryAgent("Business Analyst")
        architect = _StoryAgent("Software Architect")
        orchestrator = Orchestrator(
            agents=[analyst, architect],
            retry_executor=RetryExecutor(
                quality_pipeline=self._pipeline_with_decisions([False, False]),
            ),
        )

        result = orchestrator.run(self._state())

        self.assertEqual(len(result.execution_history.get_all()), 2)
        self.assertEqual(
            result.user_stories,
            ["story-from-Business Analyst", "story-from-Software Architect"],
        )

    def test_default_retry_executor_preserves_compatibility(self) -> None:
        agent = _StoryAgent("Business Analyst")
        orchestrator = Orchestrator(agents=[agent])

        result = orchestrator.run(self._state())

        self.assertEqual(len(result.execution_history.get_all()), 1)
        self.assertIn("attempts", result.execution_history.get_last().metadata)
        self.assertEqual(result.status, "COMPLETED")


if __name__ == "__main__":
    unittest.main()
