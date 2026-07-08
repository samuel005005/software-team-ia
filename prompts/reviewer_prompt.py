import json
from typing import Any

from llm.llm_request import LLMRequest

TEMPERATURE = 0.1
MAX_TOKENS = 1000

RESPONSE_FORMAT = """\
Responde únicamente con JSON válido en este formato:
{
  "approved": true,
  "score": 0.94,
  "summary": "Resumen breve de la revisión",
  "issues": [],
  "recommendations": []
}"""


def _format_criteria(criteria: list[str]) -> str:
    if not criteria:
        return "- Relevancia respecto al objetivo\n- Completitud de la salida\n- Claridad y coherencia"
    return "\n".join(f"- {criterion}" for criterion in criteria)


def _format_output(agent_output: Any) -> str:
    if isinstance(agent_output, str):
        return agent_output
    return json.dumps(agent_output, ensure_ascii=False, indent=2)


def build(
    *,
    reviewed_agent: str,
    objective: str,
    agent_output: Any,
    review_criteria: list[str] | None = None,
) -> LLMRequest:
    criteria = review_criteria or []

    system_prompt = (
        "Eres un Software Reviewer experto en evaluación de resultados de agentes.\n"
        "Tu rol: revisar la salida de un agente y emitir un veredicto estructurado.\n\n"
        "Criterios de revisión:\n"
        f"{_format_criteria(criteria)}\n\n"
        "Restricciones:\n"
        "- score debe ser un número entre 0.0 y 1.0\n"
        "- approved debe ser un booleano\n"
        "- Responder solo con JSON válido\n\n"
        f"{RESPONSE_FORMAT}"
    )

    user_prompt = (
        "Revisa el resultado del agente según el objetivo y los criterios indicados.\n\n"
        f"Agente revisado: {reviewed_agent}\n\n"
        f"Objetivo:\n{objective or 'Sin objetivo definido'}\n\n"
        f"Salida del agente:\n{_format_output(agent_output)}"
    )

    return LLMRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
