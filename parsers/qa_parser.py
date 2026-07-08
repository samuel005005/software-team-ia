from typing import Any

from llm.llm_response import LLMResponse
from parsers.json_content import parse_json_content
from parsers.parser_error import ParserError


def _format_qa_report_text(qa_report: dict[str, Any]) -> str:
    status = qa_report.get("status", "DESCONOCIDO")
    checks_passed = qa_report.get("checks_passed", 0)
    checks_total = qa_report.get("checks_total", 0)
    details = qa_report.get("details", [])

    lines = [
        "=== REPORTE QA ===",
        f"Estado general: {status}",
        f"Verificaciones: {checks_passed}/{checks_total}",
        "",
        "Detalle de verificaciones:",
    ]

    if isinstance(details, list):
        for detail in details:
            lines.append(f"  - {detail}")

    return "\n".join(lines)


def parse(response: LLMResponse) -> dict[str, Any]:
    data = parse_json_content(response.content)

    qa_report = data.get("qa_report")
    if not isinstance(qa_report, dict):
        raise ParserError(
            "El campo 'qa_report' es obligatorio y debe ser un objeto",
            agent_name="QA Engineer",
        )

    return {
        "qa_report": qa_report,
        "qa_report_text": _format_qa_report_text(qa_report),
    }
