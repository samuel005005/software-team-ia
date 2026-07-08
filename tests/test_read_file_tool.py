import shutil
import tempfile
import unittest
from pathlib import Path

from tools.filesystem.read_file_tool import ReadFileTool
from tools.tool_registry import create_default_tool_registry
from workspace.workspace import Workspace


class ReadFileToolTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Workspace(self._tmpdir.name)
        self.tool = ReadFileTool(self.workspace)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_reads_existing_file(self) -> None:
        target = Path(self._tmpdir.name) / "notes.txt"
        target.write_text("hola mundo", encoding="utf-8")

        result = self.tool.execute(path="notes.txt")

        self.assertTrue(result.success)
        self.assertEqual(result.output["path"], "notes.txt")
        self.assertEqual(result.output["content"], "hola mundo")
        self.assertEqual(result.output["size"], target.stat().st_size)

    def test_returns_content_and_size(self) -> None:
        content = "línea uno\nlínea dos\n"
        target = Path(self._tmpdir.name) / "nested" / "data.txt"
        target.parent.mkdir(parents=True)
        target.write_text(content, encoding="utf-8")

        result = self.tool.execute(path="nested/data.txt")

        self.assertTrue(result.success)
        self.assertEqual(result.output["content"], content)
        self.assertEqual(result.output["size"], len(content.encode("utf-8")))

    def test_fails_when_file_does_not_exist(self) -> None:
        result = self.tool.execute(path="missing.txt")

        self.assertFalse(result.success)
        self.assertIn("no existe", (result.error or "").lower())

    def test_blocks_parent_directory_traversal(self) -> None:
        result = self.tool.execute(path="../../escape.txt")

        self.assertFalse(result.success)
        self.assertIn("..", result.error or "")

    def test_blocks_absolute_paths(self) -> None:
        result = self.tool.execute(path="/etc/passwd")

        self.assertFalse(result.success)
        self.assertIn("absolut", (result.error or "").lower())

    def test_blocks_symlink_escape(self) -> None:
        outside_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outside_dir)
        outside_file = Path(outside_dir) / "secret.txt"
        outside_file.write_text("secret", encoding="utf-8")

        link_path = Path(self._tmpdir.name) / "escape-link"
        link_path.symlink_to(outside_file)

        result = self.tool.execute(path="escape-link")

        self.assertFalse(result.success)
        self.assertIn("fuera del workspace", result.error or "")

    def test_fails_when_path_is_directory(self) -> None:
        directory = Path(self._tmpdir.name) / "docs"
        directory.mkdir()

        result = self.tool.execute(path="docs")

        self.assertFalse(result.success)
        self.assertIn("no es un archivo", (result.error or "").lower())

    def test_fails_when_path_parameter_missing(self) -> None:
        result = self.tool.execute()

        self.assertFalse(result.success)
        self.assertIn("path", (result.error or "").lower())

    def test_is_registered_in_default_tool_registry(self) -> None:
        registry = create_default_tool_registry(workspace=self.workspace)

        self.assertTrue(registry.exists("read_file"))
        tool = registry.create_tool("read_file")
        self.assertIsInstance(tool, ReadFileTool)


if __name__ == "__main__":
    unittest.main()
