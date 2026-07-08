import unittest
from unittest.mock import MagicMock, Mock

import httpx
from google.genai import errors

from llm.base_provider import LLMProvider
from llm.gemini_provider import GeminiProvider
from llm.llm_request import LLMRequest
from llm.llm_response import LLMResponse
from llm.provider_error import LLMProviderError
from llm.provider_factory import ProviderFactory


def _build_request() -> LLMRequest:
    return LLMRequest(
        system_prompt="Eres un Business Analyst experto.",
        user_prompt="Genera historias de usuario para una app de barbería.",
        model="gemini-2.0-flash",
        temperature=0.5,
        max_tokens=500,
    )


def _build_gemini_response(content: str) -> MagicMock:
    response = MagicMock()
    response.text = content
    response.usage_metadata.prompt_token_count = 44
    response.usage_metadata.candidates_token_count = 19
    candidate = MagicMock()
    candidate.finish_reason = "STOP"
    response.candidates = [candidate]
    return response


class GeminiProviderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.request = _build_request()
        self.mock_client = MagicMock()
        self.provider = GeminiProvider(
            api_key="test-api-key",
            model="gemini-2.0-flash",
            client=self.mock_client,
        )

    def test_provider_name(self) -> None:
        self.assertEqual(self.provider.provider_name, "gemini")

    def test_implements_llm_provider_interface(self) -> None:
        self.assertIsInstance(self.provider, LLMProvider)

    def test_generate_returns_llm_response(self) -> None:
        self.mock_client.models.generate_content.return_value = _build_gemini_response(
            '{"user_stories": ["Como usuario quiero registrarme"]}'
        )

        response = self.provider.generate(self.request)

        self.assertIsInstance(response, LLMResponse)
        self.assertIn("user_stories", response.content)
        self.assertEqual(response.provider, "gemini")
        self.assertEqual(response.model, "gemini-2.0-flash")
        self.assertEqual(response.tokens_input, 44)
        self.assertEqual(response.tokens_output, 19)
        self.assertIsNotNone(response.duration_ms)
        self.assertEqual(response.metadata["finish_reason"], "STOP")

    def test_generate_uses_default_model_when_request_has_none(self) -> None:
        request = LLMRequest(
            system_prompt="Sistema",
            user_prompt="Usuario",
        )
        self.mock_client.models.generate_content.return_value = _build_gemini_response(
            "ok"
        )

        response = self.provider.generate(request)

        self.assertEqual(response.model, "gemini-2.0-flash")
        call_kwargs = self.mock_client.models.generate_content.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "gemini-2.0-flash")

    def test_generate_passes_prompts_and_config(self) -> None:
        self.mock_client.models.generate_content.return_value = _build_gemini_response(
            "ok"
        )

        self.provider.generate(self.request)

        call_kwargs = self.mock_client.models.generate_content.call_args.kwargs
        self.assertEqual(call_kwargs["contents"], self.request.user_prompt)
        config = call_kwargs["config"]
        self.assertEqual(config.system_instruction, self.request.system_prompt)
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.max_output_tokens, 500)

    def test_generate_uses_default_max_tokens_when_missing(self) -> None:
        request = LLMRequest(
            system_prompt="Sistema",
            user_prompt="Usuario",
        )
        self.mock_client.models.generate_content.return_value = _build_gemini_response(
            "ok"
        )

        self.provider.generate(request)

        call_kwargs = self.mock_client.models.generate_content.call_args.kwargs
        self.assertEqual(
            call_kwargs["config"].max_output_tokens,
            GeminiProvider.DEFAULT_MAX_TOKENS,
        )

    def test_authentication_error_raises_llm_provider_error(self) -> None:
        self.mock_client.models.generate_content.side_effect = errors.ClientError(
            401,
            {"error": {"message": "Invalid API key", "status": "UNAUTHENTICATED"}},
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "gemini")
        self.assertIn("API key", str(ctx.exception))

    def test_timeout_error_raises_llm_provider_error(self) -> None:
        self.mock_client.models.generate_content.side_effect = httpx.TimeoutException(
            "timeout"
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "gemini")
        self.assertIn("Timeout", str(ctx.exception))

    def test_connection_error_raises_llm_provider_error(self) -> None:
        self.mock_client.models.generate_content.side_effect = httpx.ConnectError(
            "connection failed"
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "gemini")
        self.assertIn("conexión", str(ctx.exception))

    def test_api_error_raises_llm_provider_error(self) -> None:
        self.mock_client.models.generate_content.side_effect = errors.APIError(
            500,
            {"error": {"message": "Internal error", "status": "INTERNAL"}},
        )

        with self.assertRaises(LLMProviderError) as ctx:
            self.provider.generate(self.request)

        self.assertEqual(ctx.exception.provider, "gemini")
        self.assertIn("Google Gemini", str(ctx.exception))

    def test_factory_creates_gemini_provider(self) -> None:
        provider = ProviderFactory.create(
            "gemini",
            api_key="test-api-key",
            model="gemini-2.0-flash",
        )

        self.assertIsInstance(provider, GeminiProvider)
        self.assertEqual(provider.provider_name, "gemini")

    def test_factory_requires_api_key_for_gemini(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            ProviderFactory.create("gemini")

        self.assertIn("api_key", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
