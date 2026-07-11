import os
from pathlib import Path

from factory.env_loader import load_dotenv


def test_load_dotenv_sets_variables(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("CURSOR_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text('CURSOR_API_KEY="test-key-123"\n', encoding="utf-8")

    assert load_dotenv(env_file) is True
    assert os.environ["CURSOR_API_KEY"] == "test-key-123"


def test_load_dotenv_skips_existing_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "from-shell")
    env_file = tmp_path / ".env"
    env_file.write_text("CURSOR_API_KEY=from-file\n", encoding="utf-8")

    load_dotenv(env_file)
    assert os.environ["CURSOR_API_KEY"] == "from-shell"


def test_load_dotenv_missing_file(tmp_path: Path) -> None:
    assert load_dotenv(tmp_path / "missing.env") is False
