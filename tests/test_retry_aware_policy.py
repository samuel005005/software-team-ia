import unittest

from agents.agent_result import AgentResult
from execution.execution_graph import ExecutionGraph
from execution.execution_node import ExecutionNode
from execution.execution_policy import DefaultExecutionPolicy
from execution.retry_aware_policy import RetryAwareExecutionPolicy
from execution.retry_context import RetryContext
from execution.retry_policy import RetryPolicy
from quality.quality_decision import QualityDecision


class RetryAwareExecutionPolicyTestCase(unittest.TestCase):
    def _make_node(self, node_id: str) -> ExecutionNode:
        from agents.base_agent import BaseAgent

        class _StubAgent(BaseAgent):
            @property
            def name(self) -> str:
                return node_id

            def process(self, state):
                return state

        return ExecutionNode(id=node_id, agent=_StubAgent())

    def _quality_decision(self, *, retry: bool, score: float = 0.5) -> QualityDecision:
        return QualityDecision(
            passed=not retry,
            retry=retry,
            score=score,
            reason="Test decision",
        )

    def _retry_context(
        self,
        *,
        agent_name: str,
        retry_count: int,
        quality_decision: QualityDecision,
        max_retries: int = 3,
    ) -> RetryContext:
        return RetryContext(
            agent_name=agent_name,
            retry_count=retry_count,
            max_retries=max_retries,
            last_quality_decision=quality_decision,
        )

    def test_retry_returns_same_node(self) -> None:
        policy = RetryAwareExecutionPolicy()
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        analyst.connect(architect)

        graph = ExecutionGraph(policy=policy)
        graph.add_node(analyst)
        graph.add_node(architect)

        decision = self._quality_decision(retry=True)
        context = self._retry_context(
            agent_name="analyst",
            retry_count=1,
            quality_decision=decision,
        )

        next_node = policy.choose_next(
            analyst,
            AgentResult.success_result(agent_name="analyst", output="ok"),
            graph,
            quality_decision=decision,
            retry_context=context,
        )

        self.assertIs(next_node, analyst)

    def test_retry_blocked_by_limit_continues_to_next_node(self) -> None:
        policy = RetryAwareExecutionPolicy(RetryPolicy(max_retries=3))
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        analyst.connect(architect)

        graph = ExecutionGraph(policy=policy)
        graph.add_node(analyst)
        graph.add_node(architect)

        decision = self._quality_decision(retry=True)
        context = self._retry_context(
            agent_name="analyst",
            retry_count=3,
            quality_decision=decision,
        )

        next_node = policy.choose_next(
            analyst,
            AgentResult.success_result(agent_name="analyst", output="ok"),
            graph,
            quality_decision=decision,
            retry_context=context,
        )

        self.assertIs(next_node, architect)

    def test_approved_quality_continues_to_next_node(self) -> None:
        policy = RetryAwareExecutionPolicy()
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        analyst.connect(architect)

        graph = ExecutionGraph(policy=policy)
        graph.add_node(analyst)
        graph.add_node(architect)

        decision = self._quality_decision(retry=False, score=0.94)

        next_node = policy.choose_next(
            analyst,
            AgentResult.success_result(agent_name="analyst", output="ok"),
            graph,
            quality_decision=decision,
        )

        self.assertIs(next_node, architect)

    def test_without_quality_context_matches_default_policy(self) -> None:
        retry_policy = RetryAwareExecutionPolicy()
        default_policy = DefaultExecutionPolicy()
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        analyst.connect(architect)

        graph = ExecutionGraph()
        graph.add_node(analyst)
        graph.add_node(architect)

        agent_result = AgentResult.success_result(agent_name="analyst", output="ok")

        retry_next = retry_policy.choose_next(analyst, agent_result, graph)
        default_next = default_policy.choose_next(analyst, agent_result, graph)

        self.assertIs(retry_next, architect)
        self.assertIs(default_next, architect)

    def test_graph_with_default_policy_remains_unchanged(self) -> None:
        graph = ExecutionGraph()
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        graph.add_node(analyst)
        graph.add_node(architect)
        graph.set_start(analyst)
        analyst.connect(architect)

        self.assertIsInstance(graph.policy, DefaultExecutionPolicy)
        self.assertEqual(graph.get_execution_order(), ["analyst", "architect"])


if __name__ == "__main__":
    unittest.main()
