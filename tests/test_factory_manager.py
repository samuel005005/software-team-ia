import unittest
from unittest.mock import MagicMock

from agents.agent_registry import create_default_registry
from factory.factory_manager_agent import (
    FactoryManagerAgent,
    PROJECT_TYPE_NEW,
    PROJECT_TYPE_REVIEW,
)
from llm.llm_response import LLMResponse
from llm.mock_provider import MockLLMProvider
from planning.execution_plan import ExecutionPlan
from project_context.project_snapshot import ProjectSnapshot


class FactoryManagerAgentTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = create_default_registry()

    def test_receives_objective_and_builds_factory_plan(self) -> None:
        manager = FactoryManagerAgent(registry=self.registry)

        plan = manager.create_factory_plan("Crear una aplicación móvil de barbería")

        self.assertEqual(plan.objective, "Crear una aplicación móvil de barbería")
        self.assertEqual(plan.project_type, PROJECT_TYPE_NEW)
        self.assertEqual(plan.execution_plan.metadata["objective"], plan.objective)

    def test_selects_agents_from_registry(self) -> None:
        manager = FactoryManagerAgent(registry=self.registry)

        plan = manager.create_factory_plan("Crear una aplicación móvil de barbería")
        registry_ids = self.registry.list_ids()

        self.assertTrue(plan.selected_agents)
        self.assertTrue(all(agent_id in registry_ids for agent_id in plan.selected_agents))
        self.assertEqual(plan.selected_agents, plan.execution_plan.nodes)

    def test_generates_execution_plan_instance(self) -> None:
        manager = FactoryManagerAgent(registry=self.registry)

        plan = manager.create_factory_plan("Crear una aplicación móvil de barbería")

        self.assertIsInstance(plan.execution_plan, ExecutionPlan)
        self.assertEqual(plan.execution_plan.nodes, plan.selected_agents)
        self.assertIn(plan.execution_plan.metadata["source"], {"planner_v1", "planner_llm"})

    def test_works_with_mock_llm_provider(self) -> None:
        manager = FactoryManagerAgent(
            llm_provider=MockLLMProvider(),
            registry=self.registry,
        )

        plan = manager.create_factory_plan("Crear una aplicación móvil de barbería")

        self.assertEqual(plan.project_type, PROJECT_TYPE_NEW)
        self.assertTrue(plan.selected_agents)
        self.assertEqual(plan.execution_plan.nodes, plan.selected_agents)

    def test_uses_llm_classification_when_valid(self) -> None:
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            content='{"project_type":"existing_project_review"}',
            provider="mock",
            model="mock-model-v1",
        )
        manager = FactoryManagerAgent(
            llm_provider=provider,
            registry=self.registry,
        )

        plan = manager.create_factory_plan("Revisar un sistema legacy")

        self.assertEqual(plan.project_type, PROJECT_TYPE_REVIEW)
        self.assertEqual(plan.execution_plan.metadata["project_type"], PROJECT_TYPE_REVIEW)

    def test_fallback_when_llm_fails(self) -> None:
        provider = MagicMock()
        provider.generate.side_effect = RuntimeError("provider error")
        manager = FactoryManagerAgent(
            llm_provider=provider,
            registry=self.registry,
        )

        plan = manager.create_factory_plan("Crear una aplicación móvil de barbería")

        self.assertEqual(plan.project_type, PROJECT_TYPE_NEW)
        self.assertTrue(plan.selected_agents)
        self.assertEqual(plan.execution_plan.nodes, plan.selected_agents)

    def test_accepts_optional_project_context(self) -> None:
        manager = FactoryManagerAgent(registry=self.registry)
        snapshot = ProjectSnapshot(
            project_path="/tmp/barberia-app",
            project_name="barberia-app",
            detected_stack="flutter",
            technologies=["Flutter", "Dart"],
        )

        plan = manager.create_factory_plan("Mejorar autenticación", context=snapshot)

        self.assertEqual(plan.project_type, PROJECT_TYPE_REVIEW)
        self.assertTrue(plan.metadata["context_used"])
        self.assertEqual(plan.metadata["project_name"], "barberia-app")


if __name__ == "__main__":
    unittest.main()
