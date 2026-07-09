import os

from factory.config import model_for_role, model_for_tier
from factory.models import FactoryRole


def test_model_for_tier_cheap(monkeypatch) -> None:
    monkeypatch.setenv("FACTORY_MODEL_CHEAP", "cheap-model")
    monkeypatch.setenv("FACTORY_MODEL_FAST", "fast-model")
    assert model_for_tier("cheap") == "cheap-model"


def test_model_for_tier_cheap_falls_back_to_fast(monkeypatch) -> None:
    monkeypatch.delenv("FACTORY_MODEL_CHEAP", raising=False)
    monkeypatch.setenv("FACTORY_MODEL_FAST", "fast-model")
    assert model_for_tier("cheap") == "fast-model"


def test_model_for_role_developer_uses_fast(monkeypatch) -> None:
    monkeypatch.setenv("FACTORY_MODEL_SMART", "smart-model")
    monkeypatch.setenv("FACTORY_MODEL_FAST", "fast-model")
    assert model_for_role(FactoryRole.DEVELOPER) == "fast-model"


def test_model_for_role_architect_uses_smart(monkeypatch) -> None:
    monkeypatch.setenv("FACTORY_MODEL_SMART", "smart-model")
    monkeypatch.setenv("FACTORY_MODEL_FAST", "fast-model")
    assert model_for_role(FactoryRole.ARCHITECT) == "smart-model"


def test_model_for_role_tier_override(monkeypatch) -> None:
    monkeypatch.setenv("FACTORY_MODEL_CHEAP", "cheap-model")
    monkeypatch.setenv("FACTORY_MODEL_FAST", "fast-model")
    assert model_for_role(FactoryRole.DEVELOPER, tier="cheap") == "cheap-model"


def test_model_for_role_env_override(monkeypatch) -> None:
    monkeypatch.setenv("FACTORY_MODEL_DEVELOPER", "custom-dev")
    assert model_for_role(FactoryRole.DEVELOPER) == "custom-dev"
