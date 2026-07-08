import tempfile
import unittest
from pathlib import Path

from agents.analyst_agent import AnalystAgent
from agents.architect_agent import ArchitectAgent
from agents.developer_agent import DeveloperAgent
from artifacts.artifact_writer import ArtifactWriter
from llm.mock_provider import MockLLMProvider
from memory.memory_store import MemoryStore
from orchestrator.orchestrator import Orchestrator
from state.project_state import ProjectState
from tools.tool_registry import create_default_tool_registry
from workflows.software_creation import create_tool_executor, get_software_creation_agents
from workspace.workspace import Workspace


class DeveloperLLMIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Workspace(self._tmpdir.name)
        self.artifact_writer = ArtifactWriter(
            create_default_tool_registry(self.workspace)
        )
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
            artifact_writer=self.artifact_writer,
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

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

    def test_developer_persists_readme_artifact(self) -> None:
        result = self.developer.execute(self.state)

        self.assertEqual(len(result.actions), 0)
        self.assertEqual(len(self.developer.last_artifacts.artifacts), 3)
        self.assertIsNotNone(self.developer.last_artifacts.find("barberia-app/pubspec.yaml"))
        self.assertIsNotNone(self.developer.last_artifacts.find("barberia-app/lib/main.dart"))
        readme = self.developer.last_artifacts.find("barberia-app/README.md")
        self.assertIsNotNone(readme)
        target = Path(self._tmpdir.name) / "barberia-app" / "README.md"
        self.assertTrue(target.is_file())

    def test_orchestrator_records_generated_files_from_developer(self) -> None:
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
            any("Artefacto persistido" in log for log in result.logs)
        )

    def test_execution_history_recorded(self) -> None:
        result = self.developer.execute(self.state)

        records = result.execution_history.get_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].agent_name, "DeveloperAgent")
        self.assertEqual(records[0].status, "SUCCESS")
        self.assertIn("artefactos", records[0].output_summary)

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

        readme_path = Path("projects") / "barberia-app" / "README.md"
        pubspec_path = Path("projects") / "barberia-app" / "pubspec.yaml"
        main_dart_path = Path("projects") / "barberia-app" / "lib" / "main.dart"
        self.assertTrue(readme_path.is_file())
        self.assertTrue(pubspec_path.is_file())
        self.assertTrue(main_dart_path.is_file())

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
            artifact_writer=self.artifact_writer,
        )

        state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
        )
        state = analyst.execute(state)
        state = architect.execute(state)
        state = developer.execute(state)

        self.assertEqual(len(state.tasks), 2)
        self.assertEqual(len(state.actions), 0)
        self.assertEqual(len(state.generated_files), 3)
        self.assertEqual(len(state.execution_history.get_all()), 3)


if __name__ == "__main__":
    unittest.main()
