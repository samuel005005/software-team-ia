import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configuración para instanciar un proveedor LLM."""

    provider_name: str = "mock"
    model: str | None = None
    fixed_duration_ms: int = 5
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "LLMConfig":
        env = environ if environ is not None else os.environ
        provider_name = env.get("LLM_PROVIDER", "mock").strip().lower()
        model = env.get("LLM_MODEL") or None
        fixed_duration_ms = int(env.get("LLM_FIXED_DURATION_MS", "5"))
        openai_api_key = env.get("OPENAI_API_KEY") or None
        anthropic_api_key = env.get("ANTHROPIC_API_KEY") or None

        return cls(
            provider_name=provider_name,
            model=model,
            fixed_duration_ms=fixed_duration_ms,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
        )

    def to_factory_kwargs(self) -> dict[str, object]:
        kwargs: dict[str, object] = {"fixed_duration_ms": self.fixed_duration_ms}
        if self.model:
            kwargs["model"] = self.model
        if self.provider_name == "openai" and self.openai_api_key:
            kwargs["api_key"] = self.openai_api_key
        elif self.provider_name == "claude" and self.anthropic_api_key:
            kwargs["api_key"] = self.anthropic_api_key
        return kwargs
