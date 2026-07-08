from typing import Any

from artifacts.artifact_collection import ArtifactCollection
from artifacts.code_artifact import CodeArtifact
from llm.llm_response import LLMResponse
from parsers.json_content import parse_json_content
from parsers.parser_error import ParserError

DEVELOPER_AGENT_NAME = "Flutter Developer"


def parse(response: LLMResponse) -> dict[str, Any]:
    """Parsea la respuesta de tareas de desarrollo del Developer."""
    data = parse_json_content(response.content)

    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        raise ParserError(
            "El campo 'tasks' es obligatorio y debe ser una lista",
            agent_name=DEVELOPER_AGENT_NAME,
        )

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ParserError(
                f"La tarea en índice {index} debe ser un objeto",
                agent_name=DEVELOPER_AGENT_NAME,
            )
        if "title" not in task:
            raise ParserError(
                f"La tarea en índice {index} debe incluir 'title'",
                agent_name=DEVELOPER_AGENT_NAME,
            )

    return {"tasks": tasks}


def parse_artifacts(
    response: LLMResponse,
    *,
    project_slug: str,
) -> ArtifactCollection:
    """Convierte la respuesta JSON del Developer en una ArtifactCollection."""
    data = parse_json_content(response.content)

    files = data.get("files")
    if not isinstance(files, list):
        raise ParserError(
            "El campo 'files' es obligatorio y debe ser una lista",
            agent_name=DEVELOPER_AGENT_NAME,
        )

    if not files:
        raise ParserError(
            "El campo 'files' no puede estar vacío",
            agent_name=DEVELOPER_AGENT_NAME,
        )

    collection = ArtifactCollection()
    for index, file_data in enumerate(files):
        if not isinstance(file_data, dict):
            raise ParserError(
                f"El archivo en índice {index} debe ser un objeto",
                agent_name=DEVELOPER_AGENT_NAME,
            )

        path = file_data.get("path")
        language = file_data.get("language")
        content = file_data.get("content")

        if not isinstance(path, str) or not path.strip():
            raise ParserError(
                f"El archivo en índice {index} debe incluir 'path'",
                agent_name=DEVELOPER_AGENT_NAME,
            )
        if not isinstance(language, str) or not language.strip():
            raise ParserError(
                f"El archivo en índice {index} debe incluir 'language'",
                agent_name=DEVELOPER_AGENT_NAME,
            )
        if not isinstance(content, str):
            raise ParserError(
                f"El archivo en índice {index} debe incluir 'content' como string",
                agent_name=DEVELOPER_AGENT_NAME,
            )

        description = file_data.get("description", "")
        if description is not None and not isinstance(description, str):
            raise ParserError(
                f"El archivo en índice {index} tiene 'description' inválida",
                agent_name=DEVELOPER_AGENT_NAME,
            )

        collection.add(
            CodeArtifact(
                path=_normalize_path(path.strip(), project_slug),
                language=language.strip(),
                content=content,
                description=description or "",
                metadata={"source": "developer_llm"},
            )
        )

    return collection


def _normalize_path(path: str, project_slug: str) -> str:
    normalized = path.lstrip("/")
    if normalized.startswith(f"{project_slug}/"):
        return normalized
    return f"{project_slug}/{normalized}"
