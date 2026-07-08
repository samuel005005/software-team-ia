import json
import unittest

from llm.llm_response import LLMResponse
from parsers.parser_error import ParserError
from parsers.reviewer_parser import parse


class ReviewerParserTestCase(unittest.TestCase):
    def _response(self, content: str) -> LLMResponse:
        return LLMResponse(
            content=content,
            provider="mock",
            model="mock-model-v1",
        )

    def test_parse_valid_response(self) -> None:
        content = json.dumps(
            {
                "approved": True,
                "score": 0.94,
                "summary": "La salida cumple con el objetivo",
                "issues": [],
                "recommendations": ["Agregar más detalle"],
            },
            ensure_ascii=False,
        )

        result = parse(
            self._response(content),
            reviewed_agent="analyst",
            objective="barberia-app",
        )

        self.assertEqual(result.reviewed_agent, "analyst")
        self.assertTrue(result.approved)
        self.assertEqual(result.score, 0.94)
        self.assertEqual(result.summary, "La salida cumple con el objetivo")
        self.assertEqual(result.recommendations, ["Agregar más detalle"])
        self.assertEqual(result.metadata["source"], "reviewer_llm")
        self.assertEqual(result.metadata["objective"], "barberia-app")

    def test_parse_invalid_json_raises(self) -> None:
        with self.assertRaises(ParserError):
            parse(self._response("not-json"), reviewed_agent="analyst")

    def test_parse_missing_approved_raises(self) -> None:
        content = json.dumps({"score": 0.8, "summary": "ok"})

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content), reviewed_agent="analyst")

        self.assertIn("approved", str(ctx.exception))

    def test_parse_invalid_score_raises(self) -> None:
        content = json.dumps(
            {"approved": True, "score": "alto", "summary": "ok"},
        )

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content), reviewed_agent="analyst")

        self.assertIn("score", str(ctx.exception))

    def test_parse_score_out_of_range_raises(self) -> None:
        content = json.dumps(
            {"approved": True, "score": 1.5, "summary": "ok"},
        )

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content), reviewed_agent="analyst")

        self.assertIn("0.0 y 1.0", str(ctx.exception))

    def test_parse_missing_summary_raises(self) -> None:
        content = json.dumps({"approved": True, "score": 0.9})

        with self.assertRaises(ParserError) as ctx:
            parse(self._response(content), reviewed_agent="analyst")

        self.assertIn("summary", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
