import unittest

from agents.analyst_agent import AnalystAgent
from agents.architect_agent import ArchitectAgent
from llm.mock_provider import MockLLMProvider
from memory.memory_store import MemoryStore
from orchestrator.orchestrator import Orchestrator
from state.project_state import ProjectState
from workflows.software_creation import create_tool_executor, get_software_creation_agents


class ArchitectLLMIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
            user_stories=[
                "Como usuario quiero registrarme",
                "Como usuario quiero iniciar sesión",
            ],
        )
        self.memory_store = MemoryStore()
        self.llm_provider = MockLLMProvider()
        self.architect = ArchitectAgent(
            llm_provider=self.llm_provider,
            memory_store=self.memory_store,
        )

    def test_architect_uses_llm_pipeline(self) -> None:
        self.assertTrue(self.architect.uses_llm_pipeline)

    def test_architect_generates_sdd_via_llm(self) -> None:
        result = self.architect.execute(self.state)

        self.assertTrue(result.software_design_document)
        self.assertIn("Software Design Document", result.software_design_document)
        self.assertTrue(result.architecture)
        self.assertIn("Flutter", result.architecture)

    def test_architect_updates_project_state(self) -> None:
        result = self.architect.execute(self.state)

        self.assertIsNotNone(result.architecture)
        self.assertIsNotNone(result.software_design_document)
        self.assertIn("FastAPI", result.architecture)

    def test_execution_history_recorded(self) -> None:
        result = self.architect.execute(self.state)

        records = result.execution_history.get_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].agent_name, "ArchitectAgent")
        self.assertEqual(records[0].status, "SUCCESS")
        self.assertIn("SDD", records[0].output_summary)

    def test_memory_store_receives_notes(self) -> None:
        self.architect.execute(self.state)
        memory = self.memory_store.get("Software Architect")

        self.assertTrue(memory.notes)
        self.assertTrue(memory.decisions)
        self.assertTrue(any("SDD" in note for note in memory.notes))
        self.assertTrue(any("Patrones" in decision for decision in memory.decisions))

    def test_logs_indicate_llm_pipeline(self) -> None:
        result = self.architect.execute(self.state)

        self.assertTrue(any("pipeline LLM" in log for log in result.logs))
        self.assertTrue(any("via LLM" in log for log in result.logs))
        self.assertTrue(
            any("Software Design Document generado" in log for log in result.logs)
        )

    def test_full_orchestrator_with_migrated_architect(self) -> None:
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
        self.assertIn("Flutter", result.architecture)
        self.assertEqual(len(result.tasks), 2)
        self.assertTrue(result.qa_report)
        self.assertEqual(len(result.execution_history.get_all()), 4)

    def test_architect_runs_after_analyst_in_pipeline(self) -> None:
        memory_store = MemoryStore()
        llm_provider = MockLLMProvider()
        analyst = AnalystAgent(
            llm_provider=llm_provider,
            memory_store=memory_store,
        )
        architect = ArchitectAgent(
            llm_provider=llm_provider,
            memory_store=memory_store,
        )

        state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
        )
        state = analyst.execute(state)
        state = architect.execute(state)

        self.assertEqual(len(state.user_stories), 3)
        self.assertTrue(state.software_design_document)
        self.assertEqual(len(state.execution_history.get_all()), 2)


if __name__ == "__main__":
    unittest.main()
