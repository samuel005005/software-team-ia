"""Compacta análisis largos para inyectar al Developer sin gastar tokens."""

import re

_PRIORITY_SECTIONS = (
    "## Criterios de aceptación",
    "## Plan de implementación",
    "## Comandos de validación",
    "## Estado actual del código",
    "## Riesgos y decisiones",
)


def _extract_section(text: str, header: str) -> str | None:
    start = text.find(header)
    if start == -1:
        return None

    rest = text[start + len(header) :]
    next_header = re.search(r"\n## ", rest)
    end = start + len(header) + (next_header.start() if next_header else len(rest))
    return text[start:end].strip()


def compact_analysis(text: str, *, max_chars: int) -> str:
    """Extrae secciones clave y trunca si hace falta."""
    if not text.strip():
        return ""

    parts: list[str] = []
    for header in _PRIORITY_SECTIONS:
        section = _extract_section(text, header)
        if section:
            parts.append(section)

    if parts:
        combined = "\n\n".join(parts)
        if len(combined) <= max_chars:
            return combined
        compact = combined[:max_chars].rstrip()
        return compact + "\n\n…(análisis truncado; lee el archivo completo en `.factory/analysis/`)"

    if len(text) <= max_chars:
        return text.strip()

    compact = text[:max_chars].rstrip()
    return compact + "\n\n…(análisis truncado; lee `.factory/analysis/` completo si hace falta)"
