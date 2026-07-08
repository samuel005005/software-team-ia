import json
import unittest

from llm.llm_response import LLMResponse
from parsers.parser_error import ParserError
from parsers.planner_parser import parse


class PlannerParserTestCase(unittest.TestCase):
    def _response(self, content: str) -> LLMResponse:
        return LLMResponse(
            content=content,
            provider="mock",
            model="mock-model-v1",
        )

    def test_parse_valid_response(self) -> None:
        content = json.dumps(
            {"nodes": ["analyst", "architect", "developer", "qa"]},
            ensure_ascii=False,
        )
        plan = parse(self._response(content), objective="barberia-app")

        self.assertEqual(plan.nodes, ["analyst", "architect", "developer", "qa"])
        self.assertEqual(plan.metadata["objective"], "barberia-app")
        self.assertEqual(plan.metadata["source"], "planner_llm")

    def test_parse_invalid_json_raises(self) -> None:
        with self.assertRaises(ParserError):
            parse(self._response("not-json"), objective="test")

    def test_parse_missing_nodes_raises(self) -> None:
        content = json.dumps({"flow": ["analyst"]})

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content))

        self.assertIn("nodes", str(ctx.exception))

    def test_parse_empty_nodes_raises(self) -> None:
        content = json.dumps({"nodes": []})

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content))

        self.assertIn("vacío", str(ctx.exception))

    def test_parse_unknown_node_raises(self) -> None:
        content = json.dumps({"nodes": ["analyst", "reviewer"]})

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content))

        self.assertIn("reviewer", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
