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
