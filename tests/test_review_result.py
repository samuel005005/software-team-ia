import unittest

from review.review_result import ReviewResult


class ReviewResultTestCase(unittest.TestCase):
    def test_to_dict_includes_all_fields(self) -> None:
        result = ReviewResult(
            reviewed_agent="analyst",
            approved=True,
            score=0.94,
            summary="Salida válida",
            issues=["Detalle menor"],
            recommendations=["Agregar más contexto"],
            metadata={"source": "reviewer_llm"},
        )

        data = result.to_dict()

        self.assertEqual(data["reviewed_agent"], "analyst")
        self.assertTrue(data["approved"])
        self.assertEqual(data["score"], 0.94)
        self.assertEqual(data["summary"], "Salida válida")
        self.assertEqual(data["issues"], ["Detalle menor"])
        self.assertEqual(data["recommendations"], ["Agregar más contexto"])
        self.assertEqual(data["metadata"]["source"], "reviewer_llm")

    def test_defaults_for_optional_lists(self) -> None:
        result = ReviewResult(
            reviewed_agent="architect",
            approved=False,
            score=0.4,
            summary="Salida incompleta",
        )

        self.assertEqual(result.issues, [])
        self.assertEqual(result.recommendations, [])
        self.assertEqual(result.metadata, {})


if __name__ == "__main__":
    unittest.main()
