import tempfile
import unittest
from pathlib import Path

from agents.developer_agent import DeveloperAgent
from artifacts.artifact_writer import ArtifactWriter
from llm.mock_provider import MockLLMProvider
from memory.memory_store import MemoryStore
from state.project_state import ProjectState
from tools.tool_registry import create_default_tool_registry
from workspace.workspace import Workspace


class DeveloperArtifactsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Workspace(self._tmpdir.name)
        self.artifact_writer = ArtifactWriter(
            create_default_tool_registry(self.workspace)
        )
        self.developer = DeveloperAgent(
            llm_provider=MockLLMProvider(),
            memory_store=MemoryStore(),
            artifact_writer=self.artifact_writer,
        )
        self.state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
            software_design_document="Software Design Document generado por MockLLMProvider",
            architecture="Frontend: Flutter + Riverpod | Backend: FastAPI | DB: PostgreSQL",
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_developer_generates_code_artifact(self) -> None:
        result = self.developer.execute(self.state)

        artifacts = self.developer.last_artifacts
        readme = artifacts.find("barberia-app/README.md")

        self.assertIsNotNone(readme)
        assert readme is not None
        self.assertEqual(readme.language, "markdown")
        self.assertIn("Configurar proyecto Flutter", readme.content)
        self.assertIn("Resultado del Developer", readme.content)
        self.assertEqual(len(result.tasks), 2)

    def test_developer_persists_readme_physically(self) -> None:
        self.developer.execute(self.state)

        readme_path = Path(self._tmpdir.name) / "barberia-app" / "README.md"

        self.assertTrue(readme_path.is_file())
        content = readme_path.read_text(encoding="utf-8")
        self.assertIn("# barberia-app", content)
        self.assertIn("Implementar autenticación JWT", content)

    def test_developer_updates_generated_files_in_state(self) -> None:
        result = self.developer.execute(self.state)

        self.assertEqual(len(result.generated_files), 3)
        paths = {file["path"] for file in result.generated_files}
        self.assertIn("barberia-app/pubspec.yaml", paths)
        self.assertIn("barberia-app/lib/main.dart", paths)
        self.assertIn("barberia-app/README.md", paths)


if __name__ == "__main__":
    unittest.main()
