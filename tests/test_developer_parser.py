import json
import unittest

from llm.llm_response import LLMResponse
from parsers.developer_parser import parse, parse_artifacts
from parsers.parser_error import ParserError


def _response(content: str) -> LLMResponse:
    return LLMResponse(content=content, provider="mock", model="mock-model")


class DeveloperTasksParserTestCase(unittest.TestCase):
    def test_parses_tasks(self) -> None:
        content = json.dumps(
            {
                "tasks": [
                    {"id": 1, "title": "Configurar Flutter", "status": "pending"}
                ]
            }
        )
        result = parse(_response(content))
        self.assertEqual(len(result["tasks"]), 1)
        self.assertEqual(result["tasks"][0]["title"], "Configurar Flutter")

    def test_raises_when_tasks_missing(self) -> None:
        with self.assertRaises(ParserError):
            parse(_response("{}"))

    def test_raises_when_task_missing_title(self) -> None:
        content = json.dumps({"tasks": [{"id": 1}]})
        with self.assertRaises(ParserError):
            parse(_response(content))


class DeveloperArtifactsParserTestCase(unittest.TestCase):
    def test_parses_files_into_artifact_collection(self) -> None:
        content = json.dumps(
            {
                "files": [
                    {
                        "path": "pubspec.yaml",
                        "language": "yaml",
                        "description": "Manifiesto",
                        "content": "name: demo_app\n",
                    },
                    {
                        "path": "lib/main.dart",
                        "language": "dart",
                        "description": "Entry point",
                        "content": "void main() {}",
                    },
                ]
            }
        )

        collection = parse_artifacts(_response(content), project_slug="barberia-app")

        self.assertEqual(len(collection.artifacts), 2)
        self.assertEqual(collection.artifacts[0].path, "barberia-app/pubspec.yaml")
        self.assertEqual(collection.artifacts[0].language, "yaml")
        self.assertEqual(collection.artifacts[0].content, "name: demo_app\n")
        self.assertEqual(collection.artifacts[1].path, "barberia-app/lib/main.dart")

    def test_keeps_existing_project_prefix(self) -> None:
        content = json.dumps(
            {
                "files": [
                    {
                        "path": "barberia-app/README.md",
                        "language": "markdown",
                        "description": "Docs",
                        "content": "# Demo",
                    }
                ]
            }
        )

        collection = parse_artifacts(_response(content), project_slug="barberia-app")
        self.assertEqual(collection.artifacts[0].path, "barberia-app/README.md")

    def test_raises_on_invalid_json(self) -> None:
        with self.assertRaises(ParserError):
            parse_artifacts(_response("{invalid json}"), project_slug="demo")

    def test_raises_when_files_missing(self) -> None:
        with self.assertRaises(ParserError):
            parse_artifacts(_response("{}"), project_slug="demo")

    def test_raises_when_files_empty(self) -> None:
        with self.assertRaises(ParserError):
            parse_artifacts(_response('{"files": []}'), project_slug="demo")

    def test_raises_when_file_missing_content(self) -> None:
        content = json.dumps(
            {
                "files": [
                    {
                        "path": "pubspec.yaml",
                        "language": "yaml",
                        "description": "Manifiesto",
                    }
                ]
            }
        )
        with self.assertRaises(ParserError):
            parse_artifacts(_response(content), project_slug="demo")


if __name__ == "__main__":
    unittest.main()
