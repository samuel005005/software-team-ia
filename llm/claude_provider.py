import time
from typing import Any

from anthropic import APIConnectionError, APIError, APITimeoutError, Anthropic, AuthenticationError

from llm.base_provider import LLMProvider
from llm.llm_request import LLMRequest
from llm.llm_response import LLMResponse
from llm.provider_error import LLMProviderError


class ClaudeProvider(LLMProvider):
    """Proveedor LLM que utiliza la API de Anthropic Claude."""

    DEFAULT_MODEL = "claude-3-5-sonnet-latest"
    DEFAULT_MAX_TOKENS = 4096

    def __init__(
        self,
        api_key: str,
        model: str,
        client: Anthropic | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._client = client or Anthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "claude"

    def generate(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()
        model = request.model or self._model

        try:
            response = self._client.messages.create(
                model=model,
                system=request.system_prompt,
                messages=[
                    {"role": "user", "content": request.user_prompt},
                ],
                temperature=request.temperature,
                **self._message_kwargs(request),
            )
        except AuthenticationError as exc:
            raise LLMProviderError(
                "API key inválida para Anthropic Claude",
                provider=self.provider_name,
            ) from exc
        except APITimeoutError as exc:
            raise LLMProviderError(
                "Timeout al conectar con Anthropic Claude",
                provider=self.provider_name,
            ) from exc
        except APIConnectionError as exc:
            raise LLMProviderError(
                "Error de conexión con Anthropic Claude",
                provider=self.provider_name,
            ) from exc
        except APIError as exc:
            raise LLMProviderError(
                f"Error del proveedor Anthropic Claude: {exc}",
                provider=self.provider_name,
            ) from exc

        content = self._extract_content(response)
        duration_ms = int((time.perf_counter() - started) * 1000)
        usage = response.usage

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=model,
            tokens_input=usage.input_tokens if usage else None,
            tokens_output=usage.output_tokens if usage else None,
            duration_ms=duration_ms,
            metadata={
                "stop_reason": response.stop_reason or "",
            },
        )

    def _message_kwargs(self, request: LLMRequest) -> dict[str, Any]:
        return {
            "max_tokens": request.max_tokens or self.DEFAULT_MAX_TOKENS,
        }

    def _extract_content(self, response: Any) -> str:
        parts: list[str] = []
        for block in response.content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "".join(parts)
