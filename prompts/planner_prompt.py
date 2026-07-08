import json

from agents.agent_registry import AgentRegistry
from llm.llm_request import LLMRequest
from project_context.project_snapshot import ProjectSnapshot

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


def _format_project_context(snapshot: ProjectSnapshot | None) -> str:
    if snapshot is None:
        return "Proyecto actual:\nSin contexto previo disponible."

    important_files = snapshot.structure.get("important_files", [])
    metadata = snapshot.metadata or {}
    metadata_lines = (
        "\n".join(f"- {key}: {value}" for key, value in metadata.items())
        if metadata
        else "- Sin metadata"
    )
    files_lines = (
        "\n".join(f"- {file_path}" for file_path in important_files)
        if important_files
        else "- No detectados"
    )
    technologies = ", ".join(snapshot.technologies) or "No detectadas"
    return (
        "Proyecto actual:\n"
        f"- Nombre: {snapshot.project_name}\n"
        f"- Stack detectado: {snapshot.detected_stack}\n"
        f"- Tecnologías: {technologies}\n"
        f"- Ruta: {snapshot.project_path}\n"
        "Archivos importantes:\n"
        f"{files_lines}\n"
        "Metadata relevante:\n"
        f"{metadata_lines}"
    )


def build(
    objective: str,
    registry: AgentRegistry,
    project_context: ProjectSnapshot | None = None,
) -> LLMRequest:
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
        f"{_format_project_context(project_context)}\n\n"
        f"Objetivo:\n{objective or 'Sin objetivo definido'}"
    )

    return LLMRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
