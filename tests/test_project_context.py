import tempfile
import unittest
from pathlib import Path

from project_context.project_context import ProjectContextService
from project_context.project_snapshot import ProjectSnapshot
from workspace.workspace import Workspace


class ProjectContextServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Workspace(self._tmpdir.name)
        self.service = ProjectContextService(self.workspace)
        self.project_name = "barberia-app"
        self.project_root = Path(self._tmpdir.name) / self.project_name
        self.project_root.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _create_flutter_project_files(self) -> None:
        (self.project_root / "README.md").write_text("# Barberia\n", encoding="utf-8")
        (self.project_root / "pubspec.yaml").write_text(
            "name: barberia_app\n",
            encoding="utf-8",
        )
        lib_dir = self.project_root / "lib"
        lib_dir.mkdir(parents=True, exist_ok=True)
        (lib_dir / "main.dart").write_text("void main() {}\n", encoding="utf-8")

    def test_creates_snapshot(self) -> None:
        self._create_flutter_project_files()

        snapshot = self.service.analyze(self.project_name)

        self.assertIsInstance(snapshot, ProjectSnapshot)
        self.assertEqual(snapshot.project_name, self.project_name)
        self.assertTrue(snapshot.project_path.endswith(self.project_name))
        self.assertTrue(snapshot.created_at)
        self.assertTrue(snapshot.updated_at)

    def test_detects_flutter_project(self) -> None:
        self._create_flutter_project_files()

        snapshot = self.service.analyze(self.project_name)

        self.assertEqual(snapshot.detected_stack, "flutter")
        self.assertIn("Flutter", snapshot.technologies)
        self.assertIn("Dart", snapshot.technologies)
        exists = snapshot.files_summary["exists"]
        self.assertTrue(exists["pubspec.yaml"])
        self.assertTrue(exists["README.md"])

    def test_detects_structure(self) -> None:
        self._create_flutter_project_files()
        (self.project_root / "docs").mkdir()
        (self.project_root / "analysis_options.yaml").write_text(
            "lints: true\n",
            encoding="utf-8",
        )

        snapshot = self.service.analyze(self.project_name)
        structure = snapshot.structure

        self.assertIn("lib", structure["top_level_dirs"])
        self.assertIn("docs", structure["top_level_dirs"])
        self.assertIn("README.md", structure["top_level_files"])
        self.assertIn("lib/main.dart", structure["important_files"])

    def test_saves_context(self) -> None:
        self._create_flutter_project_files()
        snapshot = self.service.analyze(self.project_name)

        saved_path = self.service.save(snapshot)

        self.assertTrue(saved_path.is_file())
        expected_path = self.workspace.resolve(f"{self.project_name}/.factory/context.json")
        self.assertEqual(
            saved_path,
            expected_path,
        )

    def test_loads_previous_context(self) -> None:
        self._create_flutter_project_files()
        snapshot = self.service.analyze(self.project_name)
        self.service.save(snapshot)

        loaded = self.service.load(self.project_name)

        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.project_name, snapshot.project_name)
        self.assertEqual(loaded.detected_stack, snapshot.detected_stack)
        self.assertEqual(loaded.files_summary, snapshot.files_summary)
        self.assertEqual(loaded.structure, snapshot.structure)
        self.assertEqual(loaded.technologies, snapshot.technologies)

    def test_works_with_temporary_workspace(self) -> None:
        project_name = "demo-python"
        project_root = Path(self._tmpdir.name) / project_name
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "requirements.txt").write_text("pytest\n", encoding="utf-8")
        (project_root / "main.py").write_text("print('ok')\n", encoding="utf-8")

        snapshot = self.service.analyze(project_name)
        self.service.save(snapshot)
        loaded = self.service.load(project_name)

        self.assertEqual(snapshot.detected_stack, "python")
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertIn("Python", loaded.technologies)


if __name__ == "__main__":
    unittest.main()
