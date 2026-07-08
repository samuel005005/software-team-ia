import unittest

from actions.file_actions import CreateDirectoryAction, CreateFileAction
from agents.analyst_agent import AnalystAgent
from agents.architect_agent import ArchitectAgent
from agents.developer_agent import DeveloperAgent
from llm.mock_provider import MockLLMProvider
from memory.memory_store import MemoryStore
from orchestrator.orchestrator import Orchestrator
from state.project_state import ProjectState
from workflows.software_creation import create_tool_executor, get_software_creation_agents


class DeveloperLLMIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
            software_design_document="Software Design Document generado por MockLLMProvider",
            architecture="Frontend: Flutter + Riverpod | Backend: FastAPI | DB: PostgreSQL",
        )
        self.memory_store = MemoryStore()
        self.llm_provider = MockLLMProvider()
        self.developer = DeveloperAgent(
            llm_provider=self.llm_provider,
            memory_store=self.memory_store,
        )

    def test_developer_uses_llm_pipeline(self) -> None:
        self.assertTrue(self.developer.uses_llm_pipeline)

    def test_developer_generates_tasks_via_llm(self) -> None:
        result = self.developer.execute(self.state)

        self.assertEqual(len(result.tasks), 2)
        self.assertEqual(result.tasks[0]["title"], "Configurar proyecto Flutter")
        self.assertEqual(result.tasks[1]["title"], "Implementar autenticación JWT")

    def test_developer_updates_project_state(self) -> None:
        result = self.developer.execute(self.state)

        self.assertEqual(len(result.tasks), 2)
        self.assertEqual(result.tasks[0]["status"], "pending")

    def test_developer_generates_actions(self) -> None:
        result = self.developer.execute(self.state)

        self.assertEqual(len(result.actions), 2)
        self.assertIsInstance(result.actions[0], CreateDirectoryAction)
        self.assertIsInstance(result.actions[1], CreateFileAction)
        self.assertEqual(result.actions[0].path, "projects/barberia-app/lib")
        self.assertEqual(result.actions[1].path, "projects/barberia-app/README.md")

    def test_action_executor_runs_developer_actions(self) -> None:
        orchestrator = Orchestrator(
            [self.developer],
            tool_executor=create_tool_executor(),
        )
        result = orchestrator.run(self.state)

        self.assertTrue(result.generated_files)
        self.assertTrue(
            any("README.md" in file["path"] for file in result.generated_files)
        )
        self.assertTrue(
            any("ActionExecutor" in log for log in result.logs)
        )
        self.assertTrue(
            any("Archivo creado correctamente" in log for log in result.logs)
        )

    def test_execution_history_recorded(self) -> None:
        result = self.developer.execute(self.state)

        records = result.execution_history.get_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].agent_name, "DeveloperAgent")
        self.assertEqual(records[0].status, "SUCCESS")
        self.assertIn("tareas", records[0].output_summary)

    def test_memory_store_receives_notes(self) -> None:
        self.developer.execute(self.state)
        memory = self.memory_store.get("Flutter Developer")

        self.assertTrue(memory.notes)
        self.assertTrue(memory.decisions)
        self.assertTrue(any("tareas" in note for note in memory.notes))

    def test_logs_indicate_llm_pipeline(self) -> None:
        result = self.developer.execute(self.state)

        self.assertTrue(any("pipeline LLM" in log for log in result.logs))
        self.assertTrue(any("via LLM" in log for log in result.logs))

    def test_full_orchestrator_with_migrated_developer(self) -> None:
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
        self.assertEqual(len(result.execution_history.get_all()), 4)

    def test_developer_runs_after_architect_in_pipeline(self) -> None:
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

        state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
        )
        state = analyst.execute(state)
        state = architect.execute(state)
        state = developer.execute(state)

        self.assertEqual(len(state.tasks), 2)
        self.assertEqual(len(state.actions), 2)
        self.assertEqual(len(state.execution_history.get_all()), 3)


if __name__ == "__main__":
    unittest.main()
