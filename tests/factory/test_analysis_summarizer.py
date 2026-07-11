from factory.analysis_summarizer import compact_analysis

SAMPLE = """
# Análisis — T-010

## Criterios de aceptación (checklist)
- [ ] Criterio A

## Estado actual del código
- Nada

## Plan de implementación
### Backend
- crear endpoint

## Riesgos y decisiones
- Ninguno

## Comandos de validación
- pytest

## Notas extra
- texto que no debería aparecer si truncamos por secciones
"""


def test_compact_analysis_keeps_priority_sections() -> None:
    result = compact_analysis(SAMPLE, max_chars=5000)
    assert "## Plan de implementación" in result
    assert "## Comandos de validación" in result
    assert "Notas extra" not in result


def test_compact_analysis_truncates_long_text() -> None:
    long_body = "x" * 8000
    result = compact_analysis(long_body, max_chars=1000)
    assert len(result) <= 1100
    assert "truncado" in result
