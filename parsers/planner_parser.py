from agents.agent_registry import AgentRegistry
from llm.llm_response import LLMResponse
from parsers.json_content import parse_json_content
from parsers.parser_error import ParserError
from planning.execution_plan import ExecutionPlan

PLANNER_AGENT_NAME = "Planner"


def parse(
    response: LLMResponse,
    *,
    registry: AgentRegistry,
    objective: str = "",
) -> ExecutionPlan:
    allowed_node_ids = frozenset(registry.list_ids())
    if not allowed_node_ids:
        raise ParserError(
            "No hay agentes registrados en el registry",
            agent_name=PLANNER_AGENT_NAME,
        )

    data = parse_json_content(response.content)

    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        raise ParserError(
            "El campo 'nodes' es obligatorio y debe ser una lista",
            agent_name=PLANNER_AGENT_NAME,
        )

    if not nodes:
        raise ParserError(
            "El campo 'nodes' no puede estar vacío",
            agent_name=PLANNER_AGENT_NAME,
        )

    for index, node_id in enumerate(nodes):
        if not isinstance(node_id, str):
            raise ParserError(
                f"El nodo en índice {index} debe ser un string",
                agent_name=PLANNER_AGENT_NAME,
            )
        if node_id not in allowed_node_ids:
            raise ParserError(
                f"Nodo desconocido en índice {index}: '{node_id}'",
                agent_name=PLANNER_AGENT_NAME,
            )

    execution_plan = ExecutionPlan(
        metadata={
            "objective": objective,
            "source": "planner_llm",
            "provider": response.provider,
        },
    )
    for node_id in nodes:
        execution_plan.add_node(node_id)

    return execution_plan
