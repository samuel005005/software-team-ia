import json
import unittest

from context.context_builder import ContextBuilder
from llm.llm_response import LLMResponse
from llm.mock_provider import MockLLMProvider
from parsers.json_content import parse_json_content
from parsers.parser_error import ParserError
from parsers.response_parser import ResponseParser
from prompts.prompt_builder import PromptBuilder
from state.project_state import ProjectState


def _response(content: str) -> LLMResponse:
    return LLMResponse(content=content, provider="mock", model="mock-model")


class JsonContentTestCase(unittest.TestCase):
    def test_parses_valid_json(self) -> None:
        data = parse_json_content('{"user_stories": ["story"]}')
        self.assertEqual(data["user_stories"], ["story"])

    def test_parses_json_inside_markdown_fence(self) -> None:
        content = '```json\n{"tasks": [{"title": "Test"}]}\n```'
        data = parse_json_content(content)
        self.assertIn("tasks", data)

    def test_raises_on_invalid_json(self) -> None:
        with self.assertRaises(ParserError):
            parse_json_content("{invalid json}")

    def test_raises_on_empty_content(self) -> None:
        with self.assertRaises(ParserError):
            parse_json_content("   ")

    def test_raises_when_json_is_not_object(self) -> None:
        with self.assertRaises(ParserError):
            parse_json_content('["not", "an", "object"]')


class AnalystParserTestCase(unittest.TestCase):
    def test_parses_user_stories(self) -> None:
        content = json.dumps({"user_stories": ["Como usuario quiero registrarme"]})
        result = ResponseParser.for_analyst(_response(content))
        self.assertEqual(result["user_stories"], ["Como usuario quiero registrarme"])

    def test_raises_when_user_stories_missing(self) -> None:
        with self.assertRaises(ParserError):
            ResponseParser.for_analyst(_response("{}"))


class ArchitectParserTestCase(unittest.TestCase):
    def test_parses_architecture_and_patterns(self) -> None:
        content = json.dumps(
            {
                "architecture": {
                    "frontend": "Flutter",
                    "backend": "FastAPI",
                    "database": "PostgreSQL",
                },
                "patterns": ["Clean Architecture"],
                "sdd": "SDD completo",
            }
        )
        result = ResponseParser.for_architect(_response(content))

        self.assertEqual(result["architecture"]["frontend"], "Flutter")
        self.assertEqual(result["patterns"], ["Clean Architecture"])
        self.assertEqual(result["software_design_document"], "SDD completo")
        self.assertIn("Flutter", result["architecture_summary"])

    def test_raises_when_architecture_missing(self) -> None:
        with self.assertRaises(ParserError):
            ResponseParser.for_architect(_response('{"patterns": []}'))


class DeveloperParserTestCase(unittest.TestCase):
    def test_parses_tasks(self) -> None:
        content = json.dumps(
            {
                "tasks": [
                    {"id": 1, "title": "Configurar Flutter", "status": "pending"}
                ]
            }
        )
        result = ResponseParser.for_developer(_response(content))
        self.assertEqual(len(result["tasks"]), 1)
        self.assertEqual(result["tasks"][0]["title"], "Configurar Flutter")

    def test_raises_when_task_missing_title(self) -> None:
        content = json.dumps({"tasks": [{"id": 1}]})
        with self.assertRaises(ParserError):
            ResponseParser.for_developer(_response(content))


class QAParserTestCase(unittest.TestCase):
    def test_parses_qa_report(self) -> None:
        content = json.dumps(
            {
                "qa_report": {
                    "status": "APROBADO",
                    "checks_passed": 3,
                    "checks_total": 3,
                    "details": ["Historias de usuario: OK"],
                }
            }
        )
        result = ResponseParser.for_qa(_response(content))

        self.assertEqual(result["qa_report"]["status"], "APROBADO")
        self.assertIn("REPORTE QA", result["qa_report_text"])

    def test_raises_when_qa_report_missing(self) -> None:
        with self.assertRaises(ParserError):
            ResponseParser.for_qa(_response("{}"))


class ResponseParserTestCase(unittest.TestCase):
    def test_dispatches_by_agent_name(self) -> None:
        analyst_result = ResponseParser.parse(
            "Business Analyst",
            _response(json.dumps({"user_stories": ["story"]})),
        )
        self.assertIn("user_stories", analyst_result)

    def test_raises_for_unknown_agent(self) -> None:
        with self.assertRaises(ParserError):
            ResponseParser.parse("Unknown Agent", _response("{}"))

    def test_end_to_end_context_prompt_mock_parse(self) -> None:
        state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
        )
        context = ContextBuilder.for_analyst(state)
        request = PromptBuilder.build(context)
        response = MockLLMProvider().generate(request)
        result = ResponseParser.parse("Business Analyst", response)

        self.assertEqual(len(result["user_stories"]), 3)


if __name__ == "__main__":
    unittest.main()
