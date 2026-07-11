from factory.analysis_store import analysis_path, load_analysis, save_analysis


def test_save_and_load_analysis(tmp_path, monkeypatch) -> None:
    from factory import analysis_store

    monkeypatch.setattr(analysis_store, "ANALYSIS_DIR", tmp_path)
    monkeypatch.setattr(analysis_store, "STATE_DIR", tmp_path.parent)

    save_analysis("T-051", "# Análisis\n\nPlan de slots.")
    assert analysis_path("T-051") == tmp_path / "T-051.md"
    assert load_analysis("T-051") == "# Análisis\n\nPlan de slots."


def test_load_missing_analysis() -> None:
    assert load_analysis("T-999") is None


def test_load_story_analysis_fallback(tmp_path, monkeypatch) -> None:
    from factory import analysis_store

    monkeypatch.setattr(analysis_store, "ANALYSIS_DIR", tmp_path)
    monkeypatch.setattr(analysis_store, "STATE_DIR", tmp_path.parent)

    analysis_store.save_story_analysis("US-003", "# Plan grupal\n\n## Plan de implementación\n- API")
    loaded = load_analysis("T-044", story="US-003")
    assert loaded is not None
    assert "Plan grupal" in loaded


def test_load_analysis_compact(tmp_path, monkeypatch) -> None:
    from factory import analysis_store

    monkeypatch.setattr(analysis_store, "ANALYSIS_DIR", tmp_path)
    monkeypatch.setattr(analysis_store, "STATE_DIR", tmp_path.parent)

    body = "## Plan de implementación\n" + ("detalle " * 500)
    analysis_store.save_analysis("T-060", body)
    compact = load_analysis("T-060", compact=True, max_chars=200)
    assert compact is not None
    assert len(compact) <= 280
