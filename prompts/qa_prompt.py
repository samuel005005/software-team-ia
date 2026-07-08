import json
from typing import Any

from context.agent_context import AgentContext
from llm.llm_request import LLMRequest

TEMPERATURE = 0.1
MAX_TOKENS = 1000

RESPONSE_FORMAT = """\
Responde únicamente con JSON válido en este formato:
{
  "qa_report": {
    "status": "APROBADO",
    "checks_passed": 3,
    "checks_total": 3,
    "details": [
      "Historias de usuario: OK",
      "Arquitectura técnica: OK",
      "Tareas de desarrollo: OK"
    ]
  }
}"""


def _format_constraints(constraints: list[str]) -> str:
    if not constraints:
        return "Sin restricciones adicionales."
    return "\n".join(f"- {constraint}" for constraint in constraints)


def _format_inputs(inputs: dict[str, Any]) -> str:
    return json.dumps(inputs, ensure_ascii=False, indent=2)


def build(context: AgentContext) -> LLMRequest:
    system_prompt = (
        f"Eres un {context.agent_name} experto en aseguramiento de calidad de software.\n"
        f"Tu rol: {context.role}\n\n"
        f"Restricciones:\n{_format_constraints(context.constraints)}\n\n"
        f"{RESPONSE_FORMAT}"
    )

    user_prompt = (
        "Valida la calidad y completitud del proyecto según los artefactos disponibles.\n\n"
        f"Datos de validación:\n{_format_inputs(context.inputs)}"
    )

    return LLMRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
