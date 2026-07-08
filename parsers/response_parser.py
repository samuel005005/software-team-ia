from collections.abc import Callable
from typing import Any

from llm.llm_response import LLMResponse
from parsers.parser_error import ParserError

from . import analyst_parser, architect_parser, developer_parser, qa_parser

ParserFn = Callable[[LLMResponse], dict[str, Any]]


class ResponseParser:
    """Transforma LLMResponse en datos estructurados del dominio."""

    _PARSERS: dict[str, ParserFn] = {
        "Business Analyst": analyst_parser.parse,
        "Software Architect": architect_parser.parse,
        "Flutter Developer": developer_parser.parse,
        "QA Engineer": qa_parser.parse,
    }

    @classmethod
    def parse(cls, agent_name: str, response: LLMResponse) -> dict[str, Any]:
        parser = cls._PARSERS.get(agent_name)
        if parser is None:
            raise ParserError(f"No hay parser para el agente: {agent_name}")

        try:
            return parser(response)
        except ParserError:
            raise
        except Exception as exc:
            raise ParserError(
                f"Error inesperado al parsear respuesta: {exc}",
                agent_name=agent_name,
            ) from exc

    @staticmethod
    def for_analyst(response: LLMResponse) -> dict[str, Any]:
        return analyst_parser.parse(response)

    @staticmethod
    def for_architect(response: LLMResponse) -> dict[str, Any]:
        return architect_parser.parse(response)

    @staticmethod
    def for_developer(response: LLMResponse) -> dict[str, Any]:
        return developer_parser.parse(response)

    @staticmethod
    def for_qa(response: LLMResponse) -> dict[str, Any]:
        return qa_parser.parse(response)
