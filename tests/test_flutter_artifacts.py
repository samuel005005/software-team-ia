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


class FlutterArtifactsTestCase(unittest.TestCase):
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

    def test_developer_generates_three_flutter_artifacts(self) -> None:
        self.developer.execute(self.state)

        paths = self.developer.last_artifacts.list_paths()
        self.assertEqual(
            paths,
            [
                "barberia-app/pubspec.yaml",
                "barberia-app/lib/main.dart",
                "barberia-app/README.md",
            ],
        )

    def test_flutter_project_files_exist_on_disk(self) -> None:
        self.developer.execute(self.state)

        project_root = Path(self._tmpdir.name) / "barberia-app"
        pubspec = project_root / "pubspec.yaml"
        main_dart = project_root / "lib" / "main.dart"
        readme = project_root / "README.md"

        self.assertTrue(pubspec.is_file())
        self.assertTrue(main_dart.is_file())
        self.assertTrue(readme.is_file())

    def test_pubspec_contains_project_name(self) -> None:
        self.developer.execute(self.state)

        pubspec = (Path(self._tmpdir.name) / "barberia-app" / "pubspec.yaml").read_text(
            encoding="utf-8"
        )

        self.assertIn("name: barberia_app", pubspec)
        self.assertIn("flutter:", pubspec)

    def test_main_dart_is_hello_world(self) -> None:
        self.developer.execute(self.state)

        main_dart = (
            Path(self._tmpdir.name) / "barberia-app" / "lib" / "main.dart"
        ).read_text(encoding="utf-8")

        self.assertIn("void main()", main_dart)
        self.assertIn("Hello World", main_dart)
        self.assertIn("package:flutter/material.dart", main_dart)

    def test_readme_documents_project(self) -> None:
        self.developer.execute(self.state)

        readme = (Path(self._tmpdir.name) / "barberia-app" / "README.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("# barberia-app", readme)
        self.assertIn("Configurar proyecto Flutter", readme)


if __name__ == "__main__":
    unittest.main()
