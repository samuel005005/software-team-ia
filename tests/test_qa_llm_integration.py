import unittest

from agents.analyst_agent import AnalystAgent
from agents.architect_agent import ArchitectAgent
from agents.developer_agent import DeveloperAgent
from agents.qa_agent import QAAgent
from llm.mock_provider import MockLLMProvider
from memory.memory_store import MemoryStore
from orchestrator.orchestrator import Orchestrator
from state.project_state import ProjectState
from workflows.software_creation import create_tool_executor, get_software_creation_agents


class QALLMIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
            user_stories=[
                "Como usuario quiero registrarme",
                "Como usuario quiero iniciar sesión",
            ],
            architecture="Frontend: Flutter + Riverpod",
            software_design_document="Software Design Document generado por MockLLMProvider",
            tasks=[
                {"id": 1, "title": "Configurar proyecto Flutter", "status": "pending"},
            ],
            generated_files=[{"path": "projects/barberia-app/README.md", "content": "# test"}],
        )
        self.memory_store = MemoryStore()
        self.llm_provider = MockLLMProvider()
        self.qa = QAAgent(
            llm_provider=self.llm_provider,
            memory_store=self.memory_store,
        )

    def test_qa_uses_llm_pipeline(self) -> None:
        self.assertTrue(self.qa.uses_llm_pipeline)

    def test_qa_generates_report_via_llm(self) -> None:
        result = self.qa.execute(self.state)

        self.assertTrue(result.qa_report)
        self.assertIn("=== REPORTE QA ===", result.qa_report)
        self.assertIn("APROBADO", result.qa_report)
        self.assertIn("3/3", result.qa_report)
        self.assertIn("Historias de usuario: OK", result.qa_report)

    def test_qa_updates_project_state(self) -> None:
        result = self.qa.execute(self.state)

        self.assertIsNotNone(result.qa_report)
        self.assertIn("Detalle de verificaciones:", result.qa_report)

    def test_execution_history_recorded(self) -> None:
        result = self.qa.execute(self.state)

        records = result.execution_history.get_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].agent_name, "QAAgent")
        self.assertEqual(records[0].status, "SUCCESS")
        self.assertIn("Reporte QA", records[0].output_summary)

    def test_memory_store_receives_notes(self) -> None:
        self.qa.execute(self.state)
        memory = self.memory_store.get("QA Engineer")

        self.assertTrue(memory.notes)
        self.assertTrue(any("QA report generado mediante LLM" in note for note in memory.notes))

    def test_logs_indicate_llm_pipeline(self) -> None:
        result = self.qa.execute(self.state)

        self.assertTrue(any("pipeline LLM" in log for log in result.logs))
        self.assertTrue(any("via LLM" in log for log in result.logs))
        self.assertTrue(any("Artefactos:" in log for log in result.logs))

    def test_full_orchestrator_with_migrated_qa(self) -> None:
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
        self.assertEqual(len(result.tasks), 2)
        self.assertTrue(result.generated_files)
        self.assertTrue(result.qa_report)
        self.assertIn("APROBADO", result.qa_report)
        self.assertEqual(len(result.execution_history.get_all()), 4)

    def test_all_agents_use_llm_pipeline(self) -> None:
        agents = get_software_creation_agents()

        for agent in agents:
            with self.subTest(agent=type(agent).__name__):
                self.assertTrue(agent.uses_llm_pipeline)

    def test_qa_runs_after_developer_in_pipeline(self) -> None:
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
        developer = DeveloperAgent(
            llm_provider=llm_provider,
            memory_store=memory_store,
        )
        qa = QAAgent(
            llm_provider=llm_provider,
            memory_store=memory_store,
        )

        state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
        )
        state = analyst.execute(state)
        state = architect.execute(state)
        state = developer.execute(state)
        state = qa.execute(state)

        self.assertTrue(state.qa_report)
        self.assertEqual(len(state.execution_history.get_all()), 4)


if __name__ == "__main__":
    unittest.main()
