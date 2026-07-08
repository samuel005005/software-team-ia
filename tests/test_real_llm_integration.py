import os
import tempfile
import unittest
from unittest.mock import patch

from agents.developer_agent import DeveloperAgent
from llm.claude_provider import ClaudeProvider
from llm.gemini_provider import GeminiProvider
from llm.llm_config import LLMConfig
from llm.openai_provider import OpenAIProvider
from llm.provider_factory import ProviderFactory
from tests.helpers.real_llm_flow import (
    build_claude_provider_with_router,
    build_gemini_provider_with_router,
    build_openai_provider_with_router,
    run_software_creation_flow,
)


class RealLLMIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_openai_provider_runs_full_software_creation_flow(self) -> None:
        provider, client = build_openai_provider_with_router()

        self.assertIsInstance(provider, OpenAIProvider)

        final_state, plan, agents = run_software_creation_flow(
            provider,
            workspace_root=self._tmpdir.name,
        )
        developer = agents["developer"]
        assert isinstance(developer, DeveloperAgent)

        self.assertEqual(plan.metadata["source"], "planner_llm")
        self.assertEqual(plan.metadata["provider"], "openai")
        self.assertEqual(developer.last_artifact_source, "developer_llm")
        self.assertGreaterEqual(len(final_state.generated_files), 3)
        self.assertGreater(client.chat.completions.create.call_count, 4)

    def test_claude_provider_runs_full_software_creation_flow(self) -> None:
        provider, client = build_claude_provider_with_router()

        self.assertIsInstance(provider, ClaudeProvider)

        final_state, plan, agents = run_software_creation_flow(
            provider,
            workspace_root=self._tmpdir.name,
        )
        developer = agents["developer"]
        assert isinstance(developer, DeveloperAgent)

        self.assertEqual(plan.metadata["source"], "planner_llm")
        self.assertEqual(plan.metadata["provider"], "claude")
        self.assertEqual(developer.last_artifact_source, "developer_llm")
        self.assertGreaterEqual(len(final_state.generated_files), 3)
        self.assertGreater(client.messages.create.call_count, 4)

    def test_gemini_provider_runs_full_software_creation_flow(self) -> None:
        provider, client = build_gemini_provider_with_router()

        self.assertIsInstance(provider, GeminiProvider)

        final_state, plan, agents = run_software_creation_flow(
            provider,
            workspace_root=self._tmpdir.name,
        )
        developer = agents["developer"]
        assert isinstance(developer, DeveloperAgent)

        self.assertEqual(plan.metadata["source"], "planner_llm")
        self.assertEqual(plan.metadata["provider"], "gemini")
        self.assertEqual(developer.last_artifact_source, "developer_llm")
        self.assertGreaterEqual(len(final_state.generated_files), 3)
        self.assertGreater(client.models.generate_content.call_count, 4)

    def test_factory_from_config_uses_real_provider_classes(self) -> None:
        configs = [
            ("openai", {"OPENAI_API_KEY": "sk-test"}, OpenAIProvider),
            ("claude", {"ANTHROPIC_API_KEY": "sk-ant-test"}, ClaudeProvider),
            ("gemini", {"GOOGLE_API_KEY": "google-test"}, GeminiProvider),
        ]

        for provider_name, env, expected_type in configs:
            with self.subTest(provider=provider_name):
                env_map = {"LLM_PROVIDER": provider_name, **env}
                config = LLMConfig.from_env(env_map)
                provider = ProviderFactory.from_config(config)
                self.assertIsInstance(provider, expected_type)
                self.assertEqual(provider.provider_name, provider_name)

    def test_factory_validate_requires_api_key_for_real_providers(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ProviderFactory.from_config(LLMConfig(provider_name="openai"))

        self.assertIn("OPENAI_API_KEY", str(ctx.exception))

    @patch.dict(os.environ, {"LLM_PROVIDER": "mock"}, clear=False)
    def test_default_env_still_uses_mock_in_factory(self) -> None:
        provider = ProviderFactory.from_config(LLMConfig.from_env())
        self.assertEqual(provider.provider_name, "mock")


if __name__ == "__main__":
    unittest.main()
