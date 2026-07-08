import unittest
from unittest.mock import MagicMock, Mock

from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError

from llm.base_provider import LLMProvider
from llm.llm_request import LLMRequest
from llm.llm_response import LLMResponse
from llm.openai_provider import OpenAIProvider
from llm.provider_error import LLMProviderError
from llm.provider_factory import ProviderFactory


def _build_request() -> LLMRequest:
    return LLMRequest(
        system_prompt="Eres un Business Analyst experto.",
        user_prompt="Genera historias de usuario para una app de barbería.",
        model="gpt-4o-mini",
        temperature=0.5,
        max_tokens=500,
    )


def _build_openai_response(content: str) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    response.choices[0].finish_reason = "stop"
    response.usage.prompt_tokens = 42
    response.usage.completion_tokens = 17
    return response


class OpenAIProviderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.request = _build_request()
        self.mock_client = MagicMock()
        self.provider = OpenAIProvider(
            api_key="test-api-key",
            model="gpt-4o",
            client=self.mock_client,
        )

    def test_provider_name(self) -> None:
        self.assertEqual(self.provider.provider_name, "openai")

    def test_implements_llm_provider_interface(self) -> None:
        self.assertIsInstance(self.provider, LLMProvider)

    def test_generate_returns_llm_response(self) -> None:
        self.mock_client.chat.completions.create.return_value = _build_openai_response(
            '{"user_stories": ["Como usuario quiero registrarme"]}'
        )

        response = self.provider.generate(self.request)

        self.assertIsInstance(response, LLMResponse)
        self.assertIn("user_stories", response.content)
        self.assertEqual(response.provider, "openai")
        self.assertEqual(response.model, "gpt-4o-mini")
        self.assertEqual(response.tokens_input, 42)
        self.assertEqual(response.tokens_output, 17)
        self.assertIsNotNone(response.duration_ms)
        self.assertEqual(response.metadata["finish_reason"], "stop")

    def test_generate_uses_default_model_when_request_has_none(self) -> None:
        request = LLMRequest(
            system_prompt="Sistema",
            user_prompt="Usuario",
        )
        self.mock_client.chat.completions.create.return_value = _build_openai_response(
            "ok"
        )

        response = self.provider.generate(request)

        self.assertEqual(response.model, "gpt-4o")
        call_kwargs = self.mock_client.chat.completions.create.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "gpt-4o")

    def test_generate_passes_prompts_and_temperature(self) -> None:
        self.mock_client.chat.completions.create.return_value = _build_openai_response(
            "ok"
        )

        self.provider.generate(self.request)

        call_kwargs = self.mock_client.chat.completions.create.call_args.kwargs
        self.assertEqual(call_kwargs["temperature"], 0.5)
        self.assertEqual(call_kwargs["max_tokens"], 500)
        self.assertEqual(call_kwargs["messages"][0]["content"], self.request.system_prompt)
        self.assertEqual(call_kwargs["messages"][1]["content"], self.request.user_prompt)

    def test_authentication_error_raises_llm_provider_error(self) -> None:
        response = Mock()
        response.request = Mock()
        self.mock_client.chat.completions.create.side_effect = AuthenticationError(
            "Invalid API key",
            response=response,
            body=None,
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "openai")
        self.assertIn("API key", str(ctx.exception))

    def test_timeout_error_raises_llm_provider_error(self) -> None:
        self.mock_client.chat.completions.create.side_effect = APITimeoutError(
            request=Mock(),
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "openai")
        self.assertIn("Timeout", str(ctx.exception))

    def test_connection_error_raises_llm_provider_error(self) -> None:
        self.mock_client.chat.completions.create.side_effect = APIConnectionError(
            request=Mock(),
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "openai")
        self.assertIn("conexión", str(ctx.exception))

    def test_api_error_raises_llm_provider_error(self) -> None:
        self.mock_client.chat.completions.create.side_effect = APIError(
            "Provider error",
            request=Mock(),
            body=None,
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "openai")
        self.assertIn("proveedor OpenAI", str(ctx.exception))

    def test_factory_creates_openai_provider(self) -> None:
        provider = ProviderFactory.create(
            "openai",
            api_key="test-api-key",
            model="gpt-4o-mini",
        )

        self.assertIsInstance(provider, OpenAIProvider)
        self.assertEqual(provider.provider_name, "openai")

    def test_factory_requires_api_key_for_openai(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ProviderFactory.create("openai")

        self.assertIn("api_key", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
