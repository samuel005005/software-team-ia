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
    google_api_key: str | None = None

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "LLMConfig":
        env = environ if environ is not None else os.environ
        provider_name = env.get("LLM_PROVIDER", "mock").strip().lower()
        model = env.get("LLM_MODEL") or None
        fixed_duration_ms = int(env.get("LLM_FIXED_DURATION_MS", "5"))
        openai_api_key = env.get("OPENAI_API_KEY") or None
        anthropic_api_key = env.get("ANTHROPIC_API_KEY") or None
        google_api_key = env.get("GOOGLE_API_KEY") or env.get("GEMINI_API_KEY") or None

        return cls(
            provider_name=provider_name,
            model=model,
            fixed_duration_ms=fixed_duration_ms,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
            google_api_key=google_api_key,
        )

    def to_factory_kwargs(self) -> dict[str, object]:
        kwargs: dict[str, object] = {"fixed_duration_ms": self.fixed_duration_ms}
        if self.model:
            kwargs["model"] = self.model
        if self.provider_name == "openai" and self.openai_api_key:
            kwargs["api_key"] = self.openai_api_key
        elif self.provider_name == "claude" and self.anthropic_api_key:
            kwargs["api_key"] = self.anthropic_api_key
        elif self.provider_name == "gemini" and self.google_api_key:
            kwargs["api_key"] = self.google_api_key
        return kwargs

    def required_api_key_env_var(self) -> str | None:
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "gemini": "GOOGLE_API_KEY",
        }
        return env_vars.get(self.provider_name)

    def validate(self) -> None:
        """Valida que la configuración pueda instanciar el proveedor seleccionado."""
        if self.provider_name == "mock":
            return

        api_key = self.to_factory_kwargs().get("api_key")
        if api_key:
            return

        env_var = self.required_api_key_env_var() or "API_KEY"
        raise ValueError(
            f"LLM_PROVIDER={self.provider_name} requiere la variable de entorno {env_var}"
        )
