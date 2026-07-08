import json
import unittest

from context.agent_context import AgentContext
from context.context_builder import ContextBuilder
from llm.llm_request import LLMRequest
from llm.mock_provider import MockLLMProvider
from prompts.prompt_builder import PromptBuilder
from state.project_state import ProjectState


class PromptBuilderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
            requirements=["Gestión de citas"],
            user_stories=["Como usuario quiero registrarme"],
            software_design_document="SDD de prueba",
            architecture="Flutter + FastAPI",
            tasks=[{"id": 1, "title": "Configurar Flutter"}],
        )

    def _analyst_context(self) -> AgentContext:
        return ContextBuilder.for_analyst(self.state)

    def _architect_context(self) -> AgentContext:
        return ContextBuilder.for_architect(self.state)

    def _developer_context(self) -> AgentContext:
        return ContextBuilder.for_developer(self.state)

    def _qa_context(self) -> AgentContext:
        return ContextBuilder.for_qa(self.state)

    def test_analyst_prompt_generates_llm_request(self) -> None:
        request = PromptBuilder.for_analyst(self._analyst_context())
        self.assertIsInstance(request, LLMRequest)

    def test_analyst_system_prompt_not_empty(self) -> None:
        request = PromptBuilder.for_analyst(self._analyst_context())
        self.assertTrue(request.system_prompt.strip())

    def test_analyst_user_prompt_contains_inputs(self) -> None:
        request = PromptBuilder.for_analyst(self._analyst_context())
        self.assertIn("barberia-app", request.user_prompt)
        self.assertIn("Crear una aplicación móvil", request.user_prompt)
        self.assertIn("Gestión de citas", request.user_prompt)

    def test_analyst_constraints_in_system_prompt(self) -> None:
        request = PromptBuilder.for_analyst(self._analyst_context())
        self.assertIn("No definir arquitectura técnica", request.system_prompt)
        self.assertIn("Como usuario quiero", request.system_prompt)

    def test_analyst_response_format_in_system_prompt(self) -> None:
        request = PromptBuilder.for_analyst(self._analyst_context())
        self.assertIn("user_stories", request.system_prompt)

    def test_architect_user_prompt_contains_user_stories(self) -> None:
        request = PromptBuilder.for_architect(self._architect_context())
        self.assertIn("Como usuario quiero registrarme", request.user_prompt)
        self.assertIn("Software Design Document", request.system_prompt)

    def test_developer_user_prompt_contains_sdd(self) -> None:
        request = PromptBuilder.for_developer(self._developer_context())
        self.assertIn("SDD de prueba", request.user_prompt)
        self.assertIn("tasks", request.system_prompt)

    def test_qa_user_prompt_contains_validation_inputs(self) -> None:
        request = PromptBuilder.for_qa(self._qa_context())
        self.assertIn("user_stories_count", request.user_prompt)
        self.assertIn("has_architecture", request.user_prompt)
        self.assertIn("qa_report", request.system_prompt)

    def test_build_dispatches_by_agent_name(self) -> None:
        contexts = [
            (self._analyst_context(), "user_stories"),
            (self._architect_context(), "architecture"),
            (self._developer_context(), "tasks"),
            (self._qa_context(), "qa_report"),
        ]

        for context, expected_key in contexts:
            request = PromptBuilder.build(context)
            self.assertIsInstance(request, LLMRequest)
            self.assertIn(expected_key, request.system_prompt)

    def test_build_raises_for_unknown_agent(self) -> None:
        context = AgentContext(agent_name="Unknown Agent", role="Test")
        with self.assertRaises(ValueError):
            PromptBuilder.build(context)

    def test_context_to_prompt_to_mock_end_to_end(self) -> None:
        context = self._analyst_context()
        request = PromptBuilder.build(context)
        response = MockLLMProvider().generate(request)

        parsed = json.loads(response.content)
        self.assertIn("user_stories", parsed)
        self.assertEqual(response.provider, "mock")

    def test_temperature_configured_per_agent(self) -> None:
        self.assertEqual(PromptBuilder.for_analyst(self._analyst_context()).temperature, 0.3)
        self.assertEqual(PromptBuilder.for_architect(self._architect_context()).temperature, 0.2)
        self.assertEqual(PromptBuilder.for_developer(self._developer_context()).temperature, 0.3)
        self.assertEqual(PromptBuilder.for_qa(self._qa_context()).temperature, 0.1)


if __name__ == "__main__":
    unittest.main()
