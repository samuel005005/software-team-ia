import unittest

from quality.quality_decision import QualityDecision


class QualityDecisionTestCase(unittest.TestCase):
    def test_to_dict_includes_all_fields(self) -> None:
        decision = QualityDecision(
            passed=True,
            retry=False,
            score=0.94,
            reason="Revisión aprobada con score suficiente",
            metadata={"reviewed_agent": "analyst", "threshold": 0.75},
        )

        data = decision.to_dict()

        self.assertTrue(data["passed"])
        self.assertFalse(data["retry"])
        self.assertEqual(data["score"], 0.94)
        self.assertEqual(data["reason"], "Revisión aprobada con score suficiente")
        self.assertEqual(data["metadata"]["reviewed_agent"], "analyst")

    def test_defaults_for_metadata(self) -> None:
        decision = QualityDecision(
            passed=False,
            retry=True,
            score=0.5,
            reason="Revisión no aprobada",
        )

        self.assertEqual(decision.metadata, {})


if __name__ == "__main__":
    unittest.main()
