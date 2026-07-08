import unittest

from llm.llm_config import LLMConfig


class LLMConfigTestCase(unittest.TestCase):
    def test_defaults(self) -> None:
        config = LLMConfig()

        self.assertEqual(config.provider_name, "mock")
        self.assertIsNone(config.model)
        self.assertEqual(config.fixed_duration_ms, 5)
        self.assertIsNone(config.openai_api_key)
        self.assertIsNone(config.anthropic_api_key)
        self.assertIsNone(config.google_api_key)

    def test_from_env_uses_defaults(self) -> None:
        config = LLMConfig.from_env({})

        self.assertEqual(config.provider_name, "mock")
        self.assertIsNone(config.model)
        self.assertEqual(config.fixed_duration_ms, 5)
        self.assertIsNone(config.openai_api_key)
        self.assertIsNone(config.anthropic_api_key)
        self.assertIsNone(config.google_api_key)

    def test_from_env_reads_provider_and_model(self) -> None:
        config = LLMConfig.from_env(
            {
                "LLM_PROVIDER": "claude",
                "LLM_MODEL": "claude-sonnet-4-6",
                "LLM_FIXED_DURATION_MS": "10",
            }
        )

        self.assertEqual(config.provider_name, "claude")
        self.assertEqual(config.model, "claude-sonnet-4-6")
        self.assertEqual(config.fixed_duration_ms, 10)

    def test_from_env_normalizes_provider_name(self) -> None:
        config = LLMConfig.from_env({"LLM_PROVIDER": "  MOCK  "})

        self.assertEqual(config.provider_name, "mock")

    def test_to_factory_kwargs_includes_model_when_present(self) -> None:
        config = LLMConfig(provider_name="mock", model="mock-model-v1")

        kwargs = config.to_factory_kwargs()

        self.assertEqual(kwargs["model"], "mock-model-v1")
        self.assertEqual(kwargs["fixed_duration_ms"], 5)

    def test_from_env_reads_openai_api_key(self) -> None:
        config = LLMConfig.from_env({"OPENAI_API_KEY": "sk-test-key"})

        self.assertEqual(config.openai_api_key, "sk-test-key")

    def test_from_env_reads_anthropic_api_key(self) -> None:
        config = LLMConfig.from_env({"ANTHROPIC_API_KEY": "sk-ant-test-key"})

        self.assertEqual(config.anthropic_api_key, "sk-ant-test-key")

    def test_from_env_reads_google_api_key(self) -> None:
        config = LLMConfig.from_env({"GOOGLE_API_KEY": "google-test-key"})

        self.assertEqual(config.google_api_key, "google-test-key")

    def test_to_factory_kwargs_includes_google_api_key_for_gemini(self) -> None:
        config = LLMConfig(
            provider_name="gemini",
            google_api_key="google-test-key",
        )

        kwargs = config.to_factory_kwargs()

        self.assertEqual(kwargs["api_key"], "google-test-key")

    def test_to_factory_kwargs_includes_openai_api_key(self) -> None:
        config = LLMConfig(provider_name="openai", openai_api_key="sk-test-key")

        kwargs = config.to_factory_kwargs()

        self.assertEqual(kwargs["api_key"], "sk-test-key")

    def test_to_factory_kwargs_includes_anthropic_api_key_for_claude(self) -> None:
        config = LLMConfig(
            provider_name="claude",
            anthropic_api_key="sk-ant-test-key",
        )

        kwargs = config.to_factory_kwargs()

        self.assertEqual(kwargs["api_key"], "sk-ant-test-key")

    def test_to_factory_kwargs_omits_empty_model(self) -> None:
        config = LLMConfig()

        kwargs = config.to_factory_kwargs()

        self.assertNotIn("model", kwargs)
        self.assertEqual(kwargs["fixed_duration_ms"], 5)

    def test_to_factory_kwargs_omits_empty_openai_api_key(self) -> None:
        config = LLMConfig()

        kwargs = config.to_factory_kwargs()

        self.assertNotIn("api_key", kwargs)

    def test_from_env_reads_gemini_api_key_alias(self) -> None:
        config = LLMConfig.from_env({"GEMINI_API_KEY": "gemini-test-key"})

        self.assertEqual(config.google_api_key, "gemini-test-key")

    def test_validate_allows_mock_without_api_key(self) -> None:
        LLMConfig(provider_name="mock").validate()

    def test_validate_requires_openai_api_key(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            LLMConfig(provider_name="openai").validate()

        self.assertIn("OPENAI_API_KEY", str(ctx.exception))

    def test_validate_requires_claude_api_key(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            LLMConfig(provider_name="claude").validate()

        self.assertIn("ANTHROPIC_API_KEY", str(ctx.exception))

    def test_validate_requires_gemini_api_key(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            LLMConfig(provider_name="gemini").validate()

        self.assertIn("GOOGLE_API_KEY", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
