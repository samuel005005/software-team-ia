import json

from agents.agent_registry import AgentRegistry
from llm.llm_request import LLMRequest

TEMPERATURE = 0.2
MAX_TOKENS = 1000

RESPONSE_FORMAT = """\
Responde únicamente con JSON válido en este formato:
{
  "nodes": [
    "agent_id_1",
    "agent_id_2"
  ]
}"""


def _format_available_agents(registry: AgentRegistry) -> str:
    lines = []
    for descriptor in registry.list_agents():
        capabilities = ", ".join(descriptor.capabilities) or "N/A"
        lines.append(
            f"- {descriptor.id} ({descriptor.display_name}): "
            f"{descriptor.description}. Capacidades: {capabilities}"
        )
    return "\n".join(lines)


def _format_response_example(registry: AgentRegistry) -> str:
    example = {"nodes": registry.list_ids()}
    return json.dumps(example, ensure_ascii=False, indent=2)


def build(objective: str, registry: AgentRegistry) -> LLMRequest:
    available_agent_ids = ", ".join(registry.list_ids())

    system_prompt = (
        "Eres un Software Execution Planner experto en orquestación de agentes.\n"
        "Tu rol: definir el orden de ejecución de agentes para cumplir un objetivo.\n\n"
        "Agentes disponibles:\n"
        f"{_format_available_agents(registry)}\n\n"
        "Restricciones:\n"
        f"- Usar únicamente ids de agentes disponibles: {available_agent_ids}\n"
        "- Devolver un flujo lineal de nodos\n"
        "- Responder solo con JSON válido\n\n"
        f"{RESPONSE_FORMAT}\n\n"
        "Ejemplo para este proyecto:\n"
        f"{_format_response_example(registry)}"
    )

    user_prompt = (
        "Genera un plan de ejecución para el siguiente objetivo del proyecto.\n\n"
        f"Objetivo:\n{objective or 'Sin objetivo definido'}"
    )

    return LLMRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
