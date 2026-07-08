import time
from typing import Any

import httpx
from google import genai
from google.genai import errors, types

from llm.base_provider import LLMProvider
from llm.llm_request import LLMRequest
from llm.llm_response import LLMResponse
from llm.provider_error import LLMProviderError


class GeminiProvider(LLMProvider):
    """Proveedor LLM que utiliza la API de Google Gemini."""

    DEFAULT_MODEL = "gemini-2.0-flash"
    DEFAULT_MAX_TOKENS = 4096

    def __init__(
        self,
        api_key: str,
        model: str,
        client: genai.Client | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._client = client or genai.Client(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "gemini"

    def generate(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()
        model = request.model or self._model

        try:
            response = self._client.models.generate_content(
                model=model,
                contents=request.user_prompt,
                config=self._build_config(request),
            )
        except errors.ClientError as exc:
            if exc.code in (401, 403):
                raise LLMProviderError(
                    "API key inválida para Google Gemini",
                    provider=self.provider_name,
                ) from exc
            raise LLMProviderError(
                f"Error del proveedor Google Gemini: {exc}",
                provider=self.provider_name,
            ) from exc
        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                "Timeout al conectar con Google Gemini",
                provider=self.provider_name,
            ) from exc
        except httpx.ConnectError as exc:
            raise LLMProviderError(
                "Error de conexión con Google Gemini",
                provider=self.provider_name,
            ) from exc
        except errors.APIError as exc:
            raise LLMProviderError(
                f"Error del proveedor Google Gemini: {exc}",
                provider=self.provider_name,
            ) from exc

        content = response.text or ""
        duration_ms = int((time.perf_counter() - started) * 1000)
        usage = response.usage_metadata

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=model,
            tokens_input=usage.prompt_token_count if usage else None,
            tokens_output=usage.candidates_token_count if usage else None,
            duration_ms=duration_ms,
            metadata={
                "finish_reason": self._extract_finish_reason(response),
            },
        )

    def _build_config(self, request: LLMRequest) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=request.system_prompt,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens or self.DEFAULT_MAX_TOKENS,
        )

    def _extract_finish_reason(self, response: Any) -> str:
        candidates = getattr(response, "candidates", None)
        if not candidates:
            return ""
        finish_reason = getattr(candidates[0], "finish_reason", None)
        return str(finish_reason) if finish_reason is not None else ""
