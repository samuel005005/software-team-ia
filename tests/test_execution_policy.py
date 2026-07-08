import unittest

from agents.agent_result import AgentResult
from execution.execution_graph import ExecutionGraph
from execution.execution_node import ExecutionNode
from execution.execution_policy import DefaultExecutionPolicy, ExecutionPolicy


class _AlwaysSecondPolicy(ExecutionPolicy):
    """Política de prueba: siempre elige el segundo next_node si existe."""

    def choose_next(self, current_node, agent_result, execution_graph):
        if not current_node.next_nodes:
            return None
        if len(current_node.next_nodes) > 1:
            return current_node.next_nodes[1]
        return current_node.next_nodes[0]


class ExecutionPolicyTestCase(unittest.TestCase):
    def _make_node(self, node_id: str) -> ExecutionNode:
        from agents.base_agent import BaseAgent

        class _StubAgent(BaseAgent):
            @property
            def name(self) -> str:
                return node_id

            def process(self, state):
                return state

        return ExecutionNode(id=node_id, agent=_StubAgent())

    def _success_result(self, agent_name: str) -> AgentResult:
        return AgentResult.success_result(agent_name=agent_name, output="ok")

    def test_default_policy_without_next_node_returns_none(self) -> None:
        policy = DefaultExecutionPolicy()
        node = self._make_node("qa")
        graph = ExecutionGraph(policy=policy)
        graph.add_node(node)

        next_node = policy.choose_next(node, self._success_result("qa"), graph)

        self.assertIsNone(next_node)

    def test_default_policy_with_one_next_node(self) -> None:
        policy = DefaultExecutionPolicy()
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        analyst.connect(architect)

        graph = ExecutionGraph(policy=policy)
        graph.add_node(analyst)
        graph.add_node(architect)

        next_node = policy.choose_next(
            analyst,
            self._success_result("analyst"),
            graph,
        )

        self.assertIs(next_node, architect)

    def test_default_policy_with_multiple_next_nodes_chooses_first(self) -> None:
        policy = DefaultExecutionPolicy()
        current = self._make_node("current")
        first = self._make_node("first")
        second = self._make_node("second")
        current.connect(first)
        current.connect(second)

        graph = ExecutionGraph(policy=policy)
        for node in (current, first, second):
            graph.add_node(node)

        next_node = policy.choose_next(
            current,
            self._success_result("current"),
            graph,
        )

        self.assertIs(next_node, first)

    def test_custom_policy_can_choose_different_branch(self) -> None:
        policy = _AlwaysSecondPolicy()
        current = self._make_node("current")
        first = self._make_node("first")
        second = self._make_node("second")
        current.connect(first)
        current.connect(second)

        graph = ExecutionGraph(policy=policy)
        for node in (current, first, second):
            graph.add_node(node)

        next_node = policy.choose_next(
            current,
            self._success_result("current"),
            graph,
        )

        self.assertIs(next_node, second)

    def test_graph_uses_default_policy_when_not_specified(self) -> None:
        graph = ExecutionGraph()
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        graph.add_node(analyst)
        graph.add_node(architect)
        graph.set_start(analyst)
        analyst.connect(architect)

        self.assertIsInstance(graph.policy, DefaultExecutionPolicy)
        self.assertEqual(graph.get_execution_order(), ["analyst", "architect"])

    def test_graph_traversal_uses_custom_policy(self) -> None:
        policy = _AlwaysSecondPolicy()
        graph = ExecutionGraph(policy=policy)
        start = self._make_node("start")
        first = self._make_node("first")
        second = self._make_node("second")
        end = self._make_node("end")

        for node in (start, first, second, end):
            graph.add_node(node)

        graph.set_start(start)
        start.connect(first)
        start.connect(second)
        second.connect(end)

        self.assertEqual(graph.get_execution_order(), ["start", "second", "end"])


if __name__ == "__main__":
    unittest.main()
