import json
import re
from typing import Any

from parsers.parser_error import ParserError


def parse_json_content(content: str) -> dict[str, Any]:
    """Extrae y parsea JSON desde el contenido de una respuesta LLM."""
    text = content.strip()
    if not text:
        raise ParserError("La respuesta del LLM está vacía")

    fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced_match:
        text = fenced_match.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ParserError(f"JSON inválido en la respuesta del LLM: {exc}") from exc

    if not isinstance(data, dict):
        raise ParserError("La respuesta del LLM debe ser un objeto JSON")

    return data
