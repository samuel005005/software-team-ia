from llm.base_provider import LLMProvider
from llm.llm_config import LLMConfig
from llm.mock_provider import MockLLMProvider

_PLANNED_PROVIDERS = frozenset({"gemini"})


class ProviderFactory:
    """Crea instancias de LLMProvider según nombre y configuración."""

    @staticmethod
    def create(provider_name: str, **config) -> LLMProvider:
        name = provider_name.strip().lower()

        if name == "mock":
            return MockLLMProvider(
                fixed_duration_ms=int(config.get("fixed_duration_ms", 5)),
            )

        if name == "openai":
            from llm.openai_provider import OpenAIProvider

            api_key = config.get("api_key")
            if not api_key:
                raise ValueError("OpenAIProvider requiere api_key en la configuración")
            model = str(config.get("model") or OpenAIProvider.DEFAULT_MODEL)
            return OpenAIProvider(api_key=str(api_key), model=model)

        if name == "claude":
            from llm.claude_provider import ClaudeProvider

            api_key = config.get("api_key")
            if not api_key:
                raise ValueError("ClaudeProvider requiere api_key en la configuración")
            model = str(config.get("model") or ClaudeProvider.DEFAULT_MODEL)
            return ClaudeProvider(api_key=str(api_key), model=model)

        if name in _PLANNED_PROVIDERS:
            raise NotImplementedError(
                f"El proveedor '{name}' no está implementado aún. "
                "Use 'mock' para desarrollo y pruebas."
            )

        raise ValueError(f"Proveedor LLM desconocido: '{provider_name}'")

    @staticmethod
    def from_config(config: LLMConfig) -> LLMProvider:
        return ProviderFactory.create(
            config.provider_name,
            **config.to_factory_kwargs(),
        )
