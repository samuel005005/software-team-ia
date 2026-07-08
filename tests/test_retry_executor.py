import unittest
from unittest.mock import MagicMock

from agents.agent_result import AgentResult
from agents.base_agent import BaseAgent
from execution.retry_executor import RetryExecutor
from execution.retry_policy import RetryPolicy
from quality.quality_context import QualityContext
from quality.quality_decision import QualityDecision
from quality.quality_pipeline import QualityPipeline
from review.review_result import ReviewResult
from state.project_state import ProjectState


class _ConfigurableAgent(BaseAgent):
    def __init__(self, outcomes: list[tuple[bool, str]]) -> None:
        super().__init__()
        self._outcomes = outcomes
        self._call_count = 0

    @property
    def name(self) -> str:
        return "Test Agent"

    def process(self, state: ProjectState) -> ProjectState:
        if self._call_count >= len(self._outcomes):
            success, output = self._outcomes[-1]
        else:
            success, output = self._outcomes[self._call_count]

        self._call_count += 1
        self._current_output = output
        if not success:
            raise RuntimeError(output)
        return state

    def build_output_summary(self, state: ProjectState) -> str:
        return getattr(self, "_current_output", "ok")


class RetryExecutorTestCase(unittest.TestCase):
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

    def _pipeline_with_decisions(
        self,
        decisions: list[bool],
    ) -> QualityPipeline:
        pipeline = MagicMock(spec=QualityPipeline)
        contexts: list[QualityContext] = []

        def evaluate(agent_result: AgentResult, **kwargs: object) -> QualityContext:
            retry = decisions[min(len(contexts), len(decisions) - 1)]
            context = self._quality_context(agent_result=agent_result, retry=retry)
            contexts.append(context)
            return context

        pipeline.evaluate.side_effect = evaluate
        return pipeline

    def test_execute_without_retry(self) -> None:
        agent = _ConfigurableAgent([(True, "ok")])
        pipeline = self._pipeline_with_decisions([False])
        executor = RetryExecutor(quality_pipeline=pipeline, max_retries=3)

        result = executor.execute(agent, self._state())

        self.assertEqual(result.attempts, 1)
        self.assertTrue(result.final_result.success)
        self.assertEqual(agent._call_count, 1)
        self.assertFalse(result.quality_context.quality_decision.retry)

    def test_execute_with_successful_retry(self) -> None:
        agent = _ConfigurableAgent([(True, "primer intento"), (True, "segundo intento")])
        pipeline = self._pipeline_with_decisions([True, False])
        executor = RetryExecutor(quality_pipeline=pipeline, max_retries=3)

        result = executor.execute(agent, self._state())

        self.assertEqual(result.attempts, 2)
        self.assertEqual(agent._call_count, 2)
        self.assertEqual(result.final_result.output, "segundo intento")
        self.assertEqual(len(result.history), 2)

    def test_execute_respects_retry_limit(self) -> None:
        agent = _ConfigurableAgent([(True, "intento")] * 5)
        pipeline = self._pipeline_with_decisions([True, True, True, True, True])
        executor = RetryExecutor(
            quality_pipeline=pipeline,
            retry_policy=RetryPolicy(max_retries=2),
            max_retries=2,
        )

        result = executor.execute(agent, self._state())

        self.assertEqual(result.attempts, 3)
        self.assertEqual(agent._call_count, 3)
        self.assertEqual(len(result.history), 3)

    def test_execute_preserves_last_valid_result_on_agent_error(self) -> None:
        agent = _ConfigurableAgent([(True, "primero"), (False, "fallo")])
        pipeline = self._pipeline_with_decisions([True, False])
        executor = RetryExecutor(quality_pipeline=pipeline, max_retries=3)

        result = executor.execute(agent, self._state())

        self.assertEqual(result.attempts, 2)
        self.assertTrue(result.final_result.success)
        self.assertEqual(result.final_result.output, "primero")

    def test_retry_result_serializes_to_dict(self) -> None:
        agent = _ConfigurableAgent([(True, "ok")])
        pipeline = self._pipeline_with_decisions([False])
        executor = RetryExecutor(quality_pipeline=pipeline)

        result = executor.execute(agent, self._state())
        data = result.to_dict()

        self.assertEqual(data["attempts"], 1)
        self.assertTrue(data["final_result"]["success"])
        self.assertIsNotNone(data["quality_context"])
        self.assertEqual(len(data["history"]), 1)


if __name__ == "__main__":
    unittest.main()
