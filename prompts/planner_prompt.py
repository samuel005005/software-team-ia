from llm.llm_request import LLMRequest

TEMPERATURE = 0.2
MAX_TOKENS = 1000

AVAILABLE_AGENTS = [
    {
        "id": "analyst",
        "description": "Genera historias de usuario a partir del objetivo del proyecto",
    },
    {
        "id": "architect",
        "description": "Genera el Software Design Document y la arquitectura",
    },
    {
        "id": "developer",
        "description": "Genera tareas de desarrollo y acciones ejecutables",
    },
    {
        "id": "qa",
        "description": "Valida la calidad y completitud del proyecto",
    },
]

RESPONSE_FORMAT = """\
Responde únicamente con JSON válido en este formato:
{
  "nodes": [
    "analyst",
    "architect",
    "developer",
    "qa"
  ]
}"""


def _format_available_agents() -> str:
    lines = []
    for agent in AVAILABLE_AGENTS:
        lines.append(f"- {agent['id']}: {agent['description']}")
    return "\n".join(lines)


def build(objective: str) -> LLMRequest:
    system_prompt = (
        "Eres un Software Execution Planner experto en orquestación de agentes.\n"
        "Tu rol: definir el orden de ejecución de agentes para cumplir un objetivo.\n\n"
        "Agentes disponibles:\n"
        f"{_format_available_agents()}\n\n"
        "Restricciones:\n"
        "- Usar únicamente ids de agentes disponibles\n"
        "- Devolver un flujo lineal de nodos\n"
        "- Responder solo con JSON válido\n\n"
        f"{RESPONSE_FORMAT}"
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
