import json
import unittest
from unittest.mock import MagicMock

from agents.base_agent import BaseAgent
from llm.llm_response import LLMResponse
from llm.mock_provider import MockLLMProvider
from llm.provider_error import LLMProviderError
from planning.execution_plan import ExecutionPlan
from planning.planner_agent import PlannerAgent
from workflows.software_creation import (
    build_graph_from_plan,
    create_agent_registry,
    create_software_creation_plan,
)
from memory.memory_store import MemoryStore


class PlannerAgentTestCase(unittest.TestCase):
    def test_plan_returns_expected_linear_flow_without_provider(self) -> None:
        planner = PlannerAgent()
        plan = planner.plan("Crear una aplicación móvil para administrar una barbería")

        self.assertEqual(
            plan.nodes,
            ["analyst", "architect", "developer", "qa"],
        )

    def test_plan_includes_objective_in_metadata(self) -> None:
        objective = "Crear una aplicación móvil para administrar una barbería"
        plan = PlannerAgent().plan(objective)

        self.assertEqual(plan.metadata["objective"], objective)
        self.assertEqual(plan.metadata["source"], "planner_v1")

    def test_plan_without_objective(self) -> None:
        plan = PlannerAgent().plan()

        self.assertEqual(plan.metadata["objective"], "")
        self.assertEqual(len(plan.nodes), 4)

    def test_create_software_creation_plan_matches_default_flow(self) -> None:
        plan = create_software_creation_plan()

        self.assertEqual(
            plan.nodes,
            ["analyst", "architect", "developer", "qa"],
        )

    def test_workflow_builds_graph_from_plan(self) -> None:
        plan = PlannerAgent().plan()
        agents = create_agent_registry(MockLLMProvider(), MemoryStore())

        graph = build_graph_from_plan(plan, agents)

        self.assertEqual(
            graph.get_execution_order(),
            ["analyst", "architect", "developer", "qa"],
        )
        self.assertEqual(len(graph.get_agents()), 4)
        self.assertTrue(all(isinstance(agent, BaseAgent) for agent in graph.get_agents()))

    def test_build_graph_from_plan_raises_for_unknown_node(self) -> None:
        plan = ExecutionPlan(nodes=["analyst", "unknown"])
        agents = create_agent_registry(MockLLMProvider(), MemoryStore())

        with self.assertRaises(ValueError) as ctx:
            build_graph_from_plan(plan, agents)

        self.assertIn("unknown", str(ctx.exception))

    def test_plan_with_mock_llm_provider(self) -> None:
        planner = PlannerAgent(llm_provider=MockLLMProvider())
        plan = planner.plan("Crear una aplicación móvil para administrar una barbería")

        self.assertEqual(
            plan.nodes,
            ["analyst", "architect", "developer", "qa"],
        )
        self.assertEqual(plan.metadata["source"], "planner_llm")

    def test_plan_falls_back_when_provider_raises(self) -> None:
        mock_provider = MagicMock()
        mock_provider.generate.side_effect = LLMProviderError(
            "Error del proveedor",
            provider="mock",
        )

        plan = PlannerAgent(llm_provider=mock_provider).plan("barberia-app")

        self.assertEqual(
            plan.nodes,
            ["analyst", "architect", "developer", "qa"],
        )
        self.assertEqual(plan.metadata["source"], "planner_fallback")

    def test_plan_falls_back_on_invalid_json(self) -> None:
        mock_provider = MagicMock()
        mock_provider.generate.return_value = LLMResponse(
            content="invalid-json",
            provider="mock",
            model="mock-model-v1",
        )

        plan = PlannerAgent(llm_provider=mock_provider).plan("barberia-app")

        self.assertEqual(plan.metadata["source"], "planner_fallback")
        self.assertEqual(len(plan.nodes), 4)

    def test_plan_falls_back_on_unknown_nodes(self) -> None:
        mock_provider = MagicMock()
        mock_provider.generate.return_value = LLMResponse(
            content=json.dumps({"nodes": ["analyst", "reviewer"]}),
            provider="mock",
            model="mock-model-v1",
        )

        plan = PlannerAgent(llm_provider=mock_provider).plan("barberia-app")

        self.assertEqual(plan.metadata["source"], "planner_fallback")
        self.assertEqual(
            plan.nodes,
            ["analyst", "architect", "developer", "qa"],
        )


if __name__ == "__main__":
    unittest.main()
