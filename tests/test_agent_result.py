import unittest

from agents.agent_result import AgentResult
from agents.analyst_agent import AnalystAgent
from llm.mock_provider import MockLLMProvider
from state.project_state import ProjectState


class AgentResultTestCase(unittest.TestCase):
    def test_creation_with_minimal_values(self) -> None:
        result = AgentResult(
            agent_name="Business Analyst",
            success=True,
            output="3 historias de usuario generadas",
        )

        self.assertEqual(result.agent_name, "Business Analyst")
        self.assertTrue(result.success)
        self.assertEqual(result.output, "3 historias de usuario generadas")

    def test_default_values(self) -> None:
        result = AgentResult(
            agent_name="QA Engineer",
            success=True,
            output="Reporte QA generado",
        )

        self.assertEqual(result.confidence, 1.0)
        self.assertEqual(result.warnings, [])
        self.assertEqual(result.issues, [])
        self.assertEqual(result.metadata, {})

    def test_failure_sets_confidence_to_zero(self) -> None:
        result = AgentResult(
            agent_name="Flutter Developer",
            success=False,
            output="Error durante ejecución",
        )

        self.assertFalse(result.success)
        self.assertEqual(result.confidence, 0.0)

    def test_warnings_and_issues(self) -> None:
        result = AgentResult(
            agent_name="Software Architect",
            success=False,
            output="SDD incompleto",
            warnings=["Faltan patrones explícitos"],
            issues=["No se encontró arquitectura backend"],
        )

        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(len(result.issues), 1)
        self.assertIn("patrones", result.warnings[0])

    def test_metadata(self) -> None:
        result = AgentResult(
            agent_name="Business Analyst",
            success=True,
            output="ok",
            metadata={"pipeline": "llm", "provider": "mock"},
        )

        self.assertEqual(result.metadata["pipeline"], "llm")
        self.assertEqual(result.metadata["provider"], "mock")

    def test_to_dict_serialization(self) -> None:
        result = AgentResult.success_result(
            agent_name="QA Engineer",
            output="Reporte QA generado",
            warnings=["Validación parcial"],
            metadata={"checks_passed": 3},
        )

        data = result.to_dict()

        self.assertEqual(data["agent_name"], "QA Engineer")
        self.assertTrue(data["success"])
        self.assertEqual(data["output"], "Reporte QA generado")
        self.assertEqual(data["warnings"], ["Validación parcial"])
        self.assertEqual(data["metadata"]["checks_passed"], 3)

    def test_success_result_factory(self) -> None:
        result = AgentResult.success_result(
            agent_name="Business Analyst",
            output="3 historias generadas",
            confidence=0.95,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.issues, [])

    def test_failure_result_factory(self) -> None:
        result = AgentResult.failure_result(
            agent_name="Flutter Developer",
            output="Error durante ejecución",
            issues=["ParserError: campo tasks faltante"],
        )

        self.assertFalse(result.success)
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(len(result.issues), 1)

    def test_base_agent_builds_result_on_execute(self) -> None:
        analyst = AnalystAgent(llm_provider=MockLLMProvider())
        state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
        )

        analyst.execute(state)
        result = analyst.last_result

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.agent_name, "Business Analyst")
        self.assertTrue(result.success)
        self.assertIn("historias", result.output)


if __name__ == "__main__":
    unittest.main()
