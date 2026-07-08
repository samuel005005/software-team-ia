import time
from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, OpenAI

from llm.base_provider import LLMProvider
from llm.llm_request import LLMRequest
from llm.llm_response import LLMResponse
from llm.provider_error import LLMProviderError


class OpenAIProvider(LLMProvider):
    """Proveedor LLM que utiliza la API de OpenAI."""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(
        self,
        api_key: str,
        model: str,
        client: OpenAI | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._client = client or OpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    def generate(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()
        model = request.model or self._model

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.user_prompt},
                ],
                temperature=request.temperature,
                **self._completion_kwargs(request),
            )
        except AuthenticationError as exc:
            raise LLMProviderError(
                "API key inválida para OpenAI",
                provider=self.provider_name,
            ) from exc
        except APITimeoutError as exc:
            raise LLMProviderError(
                "Timeout al conectar con OpenAI",
                provider=self.provider_name,
            ) from exc
        except APIConnectionError as exc:
            raise LLMProviderError(
                "Error de conexión con OpenAI",
                provider=self.provider_name,
            ) from exc
        except APIError as exc:
            raise LLMProviderError(
                f"Error del proveedor OpenAI: {exc}",
                provider=self.provider_name,
            ) from exc

        content = response.choices[0].message.content or ""
        duration_ms = int((time.perf_counter() - started) * 1000)
        usage = response.usage

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=model,
            tokens_input=usage.prompt_tokens if usage else None,
            tokens_output=usage.completion_tokens if usage else None,
            duration_ms=duration_ms,
            metadata={
                "finish_reason": response.choices[0].finish_reason or "",
            },
        )

    def _completion_kwargs(self, request: LLMRequest) -> dict[str, Any]:
        if request.max_tokens is None:
            return {}
        return {"max_tokens": request.max_tokens}
