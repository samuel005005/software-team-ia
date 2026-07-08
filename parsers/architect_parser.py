from typing import Any

from llm.llm_response import LLMResponse
from parsers.json_content import parse_json_content
from parsers.parser_error import ParserError


def _format_architecture_summary(architecture: dict[str, Any]) -> str:
    frontend = architecture.get("frontend", "No definido")
    backend = architecture.get("backend", "No definido")
    database = architecture.get("database", "No definido")
    return (
        f"Frontend:\n{frontend}\n\n"
        f"Backend:\n{backend}\n\n"
        f"Database:\n{database}"
    )


def parse(response: LLMResponse) -> dict[str, Any]:
    data = parse_json_content(response.content)

    architecture = data.get("architecture")
    if not isinstance(architecture, dict):
        raise ParserError(
            "El campo 'architecture' es obligatorio y debe ser un objeto",
            agent_name="Software Architect",
        )

    patterns = data.get("patterns", [])
    if not isinstance(patterns, list):
        raise ParserError(
            "El campo 'patterns' debe ser una lista",
            agent_name="Software Architect",
        )

    sdd = data.get("sdd")
    if sdd is not None and not isinstance(sdd, str):
        raise ParserError(
            "El campo 'sdd' debe ser un string",
            agent_name="Software Architect",
        )

    return {
        "architecture": architecture,
        "architecture_summary": _format_architecture_summary(architecture),
        "patterns": patterns,
        "software_design_document": sdd,
    }
