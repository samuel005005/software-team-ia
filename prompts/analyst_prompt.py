import json
from typing import Any

from context.agent_context import AgentContext
from llm.llm_request import LLMRequest

TEMPERATURE = 0.3
MAX_TOKENS = 1500

RESPONSE_FORMAT = """\
Responde únicamente con JSON válido en este formato:
{
  "user_stories": [
    "Como usuario quiero ..."
  ]
}"""


def _format_constraints(constraints: list[str]) -> str:
    if not constraints:
        return "Sin restricciones adicionales."
    return "\n".join(f"- {constraint}" for constraint in constraints)


def _format_inputs(inputs: dict[str, Any]) -> str:
    return json.dumps(inputs, ensure_ascii=False, indent=2)


def build(context: AgentContext) -> LLMRequest:
    system_prompt = (
        f"Eres un {context.agent_name} experto en desarrollo de software.\n"
        f"Tu rol: {context.role}\n\n"
        f"Restricciones:\n{_format_constraints(context.constraints)}\n\n"
        f"{RESPONSE_FORMAT}"
    )

    user_prompt = (
        "Genera historias de usuario para el siguiente proyecto.\n\n"
        f"Datos del proyecto:\n{_format_inputs(context.inputs)}"
    )

    return LLMRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
