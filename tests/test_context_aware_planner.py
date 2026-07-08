import json
import unittest
from unittest.mock import MagicMock

from agents.agent_registry import create_default_registry
from factory.factory_manager_agent import FactoryManagerAgent
from llm.llm_response import LLMResponse
from llm.provider_error import LLMProviderError
from planning.planner_agent import PlannerAgent
from project_context.project_snapshot import ProjectSnapshot


class ContextAwarePlannerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = create_default_registry()
        self.snapshot = ProjectSnapshot(
            project_path="/tmp/barberia-app",
            project_name="barberia-app",
            detected_stack="flutter",
            technologies=["Flutter", "Dart"],
            structure={"important_files": ["pubspec.yaml", "lib/main.dart"]},
            metadata={"source": "test"},
        )

    def test_planner_without_context_keeps_default_behavior(self) -> None:
        plan = PlannerAgent().plan("Crear una app de barbería")

        self.assertEqual(plan.nodes, ["analyst", "architect", "developer", "qa"])
        self.assertFalse(plan.metadata["context_used"])

    def test_planner_with_snapshot_includes_context_in_prompt(self) -> None:
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            content=json.dumps({"nodes": ["analyst", "architect", "developer", "qa"]}),
            provider="mock",
            model="mock-model-v1",
        )
        planner = PlannerAgent(llm_provider=provider, registry=self.registry)

        planner.plan("Agregar autenticación", project_context=self.snapshot)

        request = provider.generate.call_args.args[0]
        self.assertIn("Stack detectado: flutter", request.user_prompt)
        self.assertIn("Tecnologías: Flutter, Dart", request.user_prompt)
        self.assertIn("pubspec.yaml", request.user_prompt)
        self.assertIn("lib/main.dart", request.user_prompt)

    def test_factory_manager_passes_context_to_planner(self) -> None:
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            content=json.dumps({"nodes": ["analyst", "architect", "developer", "qa"]}),
            provider="mock",
            model="mock-model-v1",
        )
        manager = FactoryManagerAgent(llm_provider=provider, registry=self.registry)

        plan = manager.create_factory_plan("Mejorar autenticación", context=self.snapshot)

        self.assertTrue(plan.metadata["context_used"])
        self.assertEqual(plan.metadata["project_name"], "barberia-app")
        request = provider.generate.call_args.args[0]
        self.assertIn("Proyecto actual:", request.user_prompt)
        self.assertIn("barberia-app", request.user_prompt)

    def test_mock_provider_receives_context(self) -> None:
        provider = MagicMock()
        provider.generate.return_value = LLMResponse(
            content=json.dumps({"nodes": ["analyst", "architect", "developer", "qa"]}),
            provider="mock",
            model="mock-model-v1",
        )
        planner = PlannerAgent(llm_provider=provider, registry=self.registry)

        plan = planner.plan("Agregar autenticación", project_context=self.snapshot)

        self.assertEqual(plan.metadata["source"], "planner_llm")
        request = provider.generate.call_args.args[0]
        self.assertIn("Stack detectado: flutter", request.user_prompt)

    def test_fallback_works_without_context(self) -> None:
        provider = MagicMock()
        provider.generate.side_effect = LLMProviderError("boom", provider="mock")
        planner = PlannerAgent(llm_provider=provider, registry=self.registry)

        plan = planner.plan("Crear una app")

        self.assertEqual(plan.metadata["source"], "planner_fallback")
        self.assertFalse(plan.metadata["context_used"])
        self.assertEqual(plan.nodes, ["analyst", "architect", "developer", "qa"])


if __name__ == "__main__":
    unittest.main()
