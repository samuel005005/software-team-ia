import unittest

from tools.tool_result import ToolResult


class ToolResultTestCase(unittest.TestCase):
    def test_success_result_factory(self) -> None:
        result = ToolResult.success_result(
            output={"message": "ok"},
            metadata={"tool": "echo"},
        )

        self.assertTrue(result.success)
        self.assertEqual(result.output, {"message": "ok"})
        self.assertIsNone(result.error)
        self.assertEqual(result.metadata["tool"], "echo")

    def test_failure_result_factory(self) -> None:
        result = ToolResult.failure_result(
            error="No se pudo ejecutar",
            output=None,
            metadata={"reason": "invalid-params"},
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error, "No se pudo ejecutar")
        self.assertEqual(result.metadata["reason"], "invalid-params")

    def test_to_dict_serializes_all_fields(self) -> None:
        result = ToolResult(
            success=True,
            output="done",
            metadata={"duration_ms": 12},
        )

        data = result.to_dict()

        self.assertTrue(data["success"])
        self.assertEqual(data["output"], "done")
        self.assertIsNone(data["error"])
        self.assertEqual(data["metadata"]["duration_ms"], 12)


if __name__ == "__main__":
    unittest.main()
