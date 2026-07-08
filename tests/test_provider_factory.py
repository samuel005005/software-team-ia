import unittest

from llm.base_provider import LLMProvider
from llm.llm_config import LLMConfig
from llm.mock_provider import MockLLMProvider
from llm.claude_provider import ClaudeProvider
from llm.gemini_provider import GeminiProvider
from llm.openai_provider import OpenAIProvider
from llm.provider_factory import ProviderFactory
from orchestrator.orchestrator import Orchestrator
from state.project_state import ProjectState
from workflows.software_creation import create_tool_executor, get_software_creation_agents


class ProviderFactoryTestCase(unittest.TestCase):
    def test_create_mock_provider(self) -> None:
        provider = ProviderFactory.create("mock")

        self.assertIsInstance(provider, LLMProvider)
        self.assertIsInstance(provider, MockLLMProvider)
        self.assertEqual(provider.provider_name, "mock")

    def test_create_mock_provider_with_config(self) -> None:
        provider = ProviderFactory.create("mock", fixed_duration_ms=25)

        self.assertIsInstance(provider, MockLLMProvider)
        self.assertEqual(provider._fixed_duration_ms, 25)

    def test_create_normalizes_provider_name(self) -> None:
        provider = ProviderFactory.create("  MOCK  ")

        self.assertEqual(provider.provider_name, "mock")

    def test_from_config_creates_mock_provider(self) -> None:
        config = LLMConfig(provider_name="mock", fixed_duration_ms=12)
        provider = ProviderFactory.from_config(config)

        self.assertIsInstance(provider, MockLLMProvider)
        self.assertEqual(provider._fixed_duration_ms, 12)

    def test_unknown_provider_raises_value_error(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ProviderFactory.create("unknown-provider")

        self.assertIn("desconocido", str(ctx.exception))

    def test_create_openai_provider(self) -> None:
        provider = ProviderFactory.create(
            "openai",
            api_key="test-api-key",
            model="gpt-4o-mini",
        )

        self.assertIsInstance(provider, OpenAIProvider)
        self.assertEqual(provider.provider_name, "openai")

    def test_create_openai_provider_requires_api_key(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ProviderFactory.create("openai")

        self.assertIn("api_key", str(ctx.exception))

    def test_create_claude_provider(self) -> None:
        provider = ProviderFactory.create(
            "claude",
            api_key="test-api-key",
            model="claude-3-5-sonnet-latest",
        )

        self.assertIsInstance(provider, ClaudeProvider)
        self.assertEqual(provider.provider_name, "claude")

    def test_create_claude_provider_requires_api_key(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ProviderFactory.create("claude")

        self.assertIn("api_key", str(ctx.exception))

    def test_create_gemini_provider(self) -> None:
        provider = ProviderFactory.create(
            "gemini",
            api_key="test-api-key",
            model="gemini-2.0-flash",
        )

        self.assertIsInstance(provider, GeminiProvider)
        self.assertEqual(provider.provider_name, "gemini")

    def test_create_gemini_provider_requires_api_key(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ProviderFactory.create("gemini")

        self.assertIn("api_key", str(ctx.exception))

    def test_workflow_uses_factory_by_default(self) -> None:
        agents = get_software_creation_agents()

        for agent in agents:
            with self.subTest(agent=type(agent).__name__):
                self.assertIsInstance(agent._llm_provider, MockLLMProvider)

    def test_orchestrator_still_works_with_factory_provider(self) -> None:
        agents = get_software_creation_agents()
        orchestrator = Orchestrator(agents, tool_executor=create_tool_executor())
        result = orchestrator.run(
            ProjectState(
                project_name="barberia-app",
                description="Crear una aplicación móvil para administrar una barbería",
            )
        )

        self.assertEqual(len(result.user_stories), 3)
        self.assertTrue(result.software_design_document)
        self.assertEqual(len(result.tasks), 2)
        self.assertTrue(result.qa_report)
        self.assertEqual(len(result.execution_history.get_all()), 4)


if __name__ == "__main__":
    unittest.main()
