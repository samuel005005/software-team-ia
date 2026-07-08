import unittest
from unittest.mock import MagicMock, Mock

from anthropic import APIConnectionError, APIError, APITimeoutError, AuthenticationError

from llm.base_provider import LLMProvider
from llm.claude_provider import ClaudeProvider
from llm.llm_request import LLMRequest
from llm.llm_response import LLMResponse
from llm.provider_error import LLMProviderError
from llm.provider_factory import ProviderFactory


def _build_request() -> LLMRequest:
    return LLMRequest(
        system_prompt="Eres un Business Analyst experto.",
        user_prompt="Genera historias de usuario para una app de barbería.",
        model="claude-3-5-sonnet-latest",
        temperature=0.5,
        max_tokens=500,
    )


def _build_claude_response(content: str) -> MagicMock:
    text_block = MagicMock()
    text_block.text = content
    response = MagicMock()
    response.content = [text_block]
    response.stop_reason = "end_turn"
    response.usage.input_tokens = 38
    response.usage.output_tokens = 15
    return response


class ClaudeProviderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.request = _build_request()
        self.mock_client = MagicMock()
        self.provider = ClaudeProvider(
            api_key="test-api-key",
            model="claude-3-5-sonnet-latest",
            client=self.mock_client,
        )

    def test_provider_name(self) -> None:
        self.assertEqual(self.provider.provider_name, "claude")

    def test_implements_llm_provider_interface(self) -> None:
        self.assertIsInstance(self.provider, LLMProvider)

    def test_generate_returns_llm_response(self) -> None:
        self.mock_client.messages.create.return_value = _build_claude_response(
            '{"user_stories": ["Como usuario quiero registrarme"]}'
        )

        response = self.provider.generate(self.request)

        self.assertIsInstance(response, LLMResponse)
        self.assertIn("user_stories", response.content)
        self.assertEqual(response.provider, "claude")
        self.assertEqual(response.model, "claude-3-5-sonnet-latest")
        self.assertEqual(response.tokens_input, 38)
        self.assertEqual(response.tokens_output, 15)
        self.assertIsNotNone(response.duration_ms)
        self.assertEqual(response.metadata["stop_reason"], "end_turn")

    def test_generate_uses_default_model_when_request_has_none(self) -> None:
        request = LLMRequest(
            system_prompt="Sistema",
            user_prompt="Usuario",
        )
        self.mock_client.messages.create.return_value = _build_claude_response("ok")

        response = self.provider.generate(request)

        self.assertEqual(response.model, "claude-3-5-sonnet-latest")
        call_kwargs = self.mock_client.messages.create.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "claude-3-5-sonnet-latest")

    def test_generate_passes_prompts_and_temperature(self) -> None:
        self.mock_client.messages.create.return_value = _build_claude_response("ok")

        self.provider.generate(self.request)

        call_kwargs = self.mock_client.messages.create.call_args.kwargs
        self.assertEqual(call_kwargs["temperature"], 0.5)
        self.assertEqual(call_kwargs["max_tokens"], 500)
        self.assertEqual(call_kwargs["system"], self.request.system_prompt)
        self.assertEqual(call_kwargs["messages"][0]["content"], self.request.user_prompt)

    def test_generate_uses_default_max_tokens_when_missing(self) -> None:
        request = LLMRequest(
            system_prompt="Sistema",
            user_prompt="Usuario",
        )
        self.mock_client.messages.create.return_value = _build_claude_response("ok")

        self.provider.generate(request)

        call_kwargs = self.mock_client.messages.create.call_args.kwargs
        self.assertEqual(call_kwargs["max_tokens"], ClaudeProvider.DEFAULT_MAX_TOKENS)

    def test_authentication_error_raises_llm_provider_error(self) -> None:
        response = Mock()
        response.request = Mock()
        self.mock_client.messages.create.side_effect = AuthenticationError(
            "Invalid API key",
            response=response,
            body=None,
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "claude")
        self.assertIn("API key", str(ctx.exception))

    def test_timeout_error_raises_llm_provider_error(self) -> None:
        self.mock_client.messages.create.side_effect = APITimeoutError(
            request=Mock(),
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "claude")
        self.assertIn("Timeout", str(ctx.exception))

    def test_connection_error_raises_llm_provider_error(self) -> None:
        self.mock_client.messages.create.side_effect = APIConnectionError(
            request=Mock(),
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "claude")
        self.assertIn("conexión", str(ctx.exception))

    def test_api_error_raises_llm_provider_error(self) -> None:
        self.mock_client.messages.create.side_effect = APIError(
            "Provider error",
            request=Mock(),
            body=None,
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "claude")
        self.assertIn("Anthropic Claude", str(ctx.exception))

    def test_factory_creates_claude_provider(self) -> None:
        provider = ProviderFactory.create(
            "claude",
            api_key="test-api-key",
            model="claude-3-5-sonnet-latest",
        )

        self.assertIsInstance(provider, ClaudeProvider)
        self.assertEqual(provider.provider_name, "claude")

    def test_factory_requires_api_key_for_claude(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ProviderFactory.create("claude")

        self.assertIn("api_key", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
