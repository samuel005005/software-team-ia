import unittest

from agents.analyst_agent import AnalystAgent
from llm.mock_provider import MockLLMProvider
from memory.memory_store import MemoryStore
from orchestrator.orchestrator import Orchestrator
from state.project_state import ProjectState
from workflows.software_creation import create_tool_executor, get_software_creation_agents


class AnalystLLMIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
            requirements=["Gestión de citas"],
        )
        self.memory_store = MemoryStore()
        self.llm_provider = MockLLMProvider()
        self.analyst = AnalystAgent(
            llm_provider=self.llm_provider,
            memory_store=self.memory_store,
        )

    def test_analyst_uses_llm_pipeline(self) -> None:
        self.assertTrue(self.analyst.uses_llm_pipeline)

    def test_analyst_generates_user_stories_via_llm(self) -> None:
        result = self.analyst.execute(self.state)

        self.assertEqual(len(result.user_stories), 3)
        self.assertIn("Como usuario quiero registrarme", result.user_stories)

    def test_execution_history_recorded(self) -> None:
        result = self.analyst.execute(self.state)

        records = result.execution_history.get_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].agent_name, "AnalystAgent")
        self.assertEqual(records[0].status, "SUCCESS")
        self.assertIn("historias", records[0].output_summary)

    def test_memory_store_receives_notes(self) -> None:
        self.analyst.execute(self.state)
        memory = self.memory_store.get("Business Analyst")

        self.assertTrue(memory.notes)
        self.assertTrue(memory.decisions)
        self.assertTrue(
            any("historias de usuario" in note for note in memory.notes)
        )

    def test_logs_indicate_llm_pipeline(self) -> None:
        result = self.analyst.execute(self.state)

        self.assertTrue(
            any("pipeline LLM" in log for log in result.logs)
        )
        self.assertTrue(
            any("via LLM" in log for log in result.logs)
        )

    def test_full_orchestrator_with_migrated_analyst(self) -> None:
        agents = get_software_creation_agents()
        orchestrator = Orchestrator(agents, tool_executor=create_tool_executor())
        result = orchestrator.run(
            ProjectState(
                project_name="barberia-app",
                description="Crear una aplicación móvil para administrar una barbería",
            )
        )

        self.assertEqual(len(result.user_stories), 3)
        self.assertTrue(result.software_design_document)
        self.assertEqual(len(result.tasks), 7)
        self.assertTrue(result.qa_report)
        self.assertEqual(len(result.execution_history.get_all()), 4)


if __name__ == "__main__":
    unittest.main()
