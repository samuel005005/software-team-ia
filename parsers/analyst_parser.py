from typing import Any

from llm.llm_response import LLMResponse
from parsers.json_content import parse_json_content
from parsers.parser_error import ParserError


def parse(response: LLMResponse) -> dict[str, Any]:
    data = parse_json_content(response.content)

    user_stories = data.get("user_stories")
    if not isinstance(user_stories, list):
        raise ParserError(
            "El campo 'user_stories' es obligatorio y debe ser una lista",
            agent_name="Business Analyst",
        )

    if not all(isinstance(story, str) for story in user_stories):
        raise ParserError(
            "Cada historia de usuario debe ser un string",
            agent_name="Business Analyst",
        )

    return {"user_stories": user_stories}
