from typing import Any

from llm.llm_response import LLMResponse
from parsers.json_content import parse_json_content
from parsers.parser_error import ParserError


def parse(response: LLMResponse) -> dict[str, Any]:
    data = parse_json_content(response.content)

    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        raise ParserError(
            "El campo 'tasks' es obligatorio y debe ser una lista",
            agent_name="Flutter Developer",
        )

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ParserError(
                f"La tarea en índice {index} debe ser un objeto",
                agent_name="Flutter Developer",
            )
        if "title" not in task:
            raise ParserError(
                f"La tarea en índice {index} debe incluir 'title'",
                agent_name="Flutter Developer",
            )

    return {"tasks": tasks}
