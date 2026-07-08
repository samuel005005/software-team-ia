import unittest
from unittest.mock import MagicMock

from agents.base_agent import BaseAgent
from execution.execution_graph import ExecutionGraph
from execution.execution_node import ExecutionNode
from workflows.software_creation import create_software_creation_graph


class _StubAgent(BaseAgent):
    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def process(self, state):
        return state


class ExecutionGraphTestCase(unittest.TestCase):
    def _make_node(self, node_id: str) -> ExecutionNode:
        return ExecutionNode(id=node_id, agent=_StubAgent(node_id))

    def test_add_node_registers_node(self) -> None:
        graph = ExecutionGraph()
        node = self._make_node("analyst")

        graph.add_node(node)

        self.assertIs(graph.get_node("analyst"), node)

    def test_add_duplicate_node_raises(self) -> None:
        graph = ExecutionGraph()
        graph.add_node(self._make_node("analyst"))

        with self.assertRaises(ValueError):
            graph.add_node(self._make_node("analyst"))

    def test_connect_nodes(self) -> None:
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")

        analyst.connect(architect)

        self.assertEqual(analyst.next_nodes, [architect])

    def test_connect_returns_other_for_chaining(self) -> None:
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        developer = self._make_node("developer")

        result = analyst.connect(architect).connect(developer)

        self.assertIs(result, developer)
        self.assertEqual(architect.next_nodes, [developer])

    def test_set_start_node(self) -> None:
        graph = ExecutionGraph()
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        graph.add_node(analyst)
        graph.add_node(architect)

        graph.set_start(architect)

        self.assertEqual(graph.get_execution_order(), ["architect"])

    def test_linear_traversal_order(self) -> None:
        graph = ExecutionGraph()
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        developer = self._make_node("developer")
        qa = self._make_node("qa")

        for node in (analyst, architect, developer, qa):
            graph.add_node(node)

        graph.set_start(analyst)
        analyst.connect(architect).connect(developer).connect(qa)

        self.assertEqual(
            graph.get_execution_order(),
            ["analyst", "architect", "developer", "qa"],
        )

    def test_get_agents_returns_agents_in_order(self) -> None:
        graph = ExecutionGraph()
        analyst = self._make_node("analyst")
        architect = self._make_node("architect")
        graph.add_node(analyst)
        graph.add_node(architect)
        graph.set_start(analyst)
        analyst.connect(architect)

        agents = graph.get_agents()

        self.assertEqual(len(agents), 2)
        self.assertIsInstance(agents[0], BaseAgent)
        self.assertEqual(agents[0].name, "analyst")
        self.assertEqual(agents[1].name, "architect")

    def test_empty_graph_returns_empty_order(self) -> None:
        graph = ExecutionGraph()

        self.assertEqual(graph.traverse(), [])
        self.assertEqual(graph.get_execution_order(), [])
        self.assertEqual(graph.get_agents(), [])

    def test_software_creation_graph_is_linear(self) -> None:
        graph = create_software_creation_graph()

        self.assertEqual(
            graph.get_execution_order(),
            ["analyst", "architect", "developer", "qa"],
        )
        self.assertEqual(len(graph.get_agents()), 4)


if __name__ == "__main__":
    unittest.main()
