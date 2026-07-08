import shutil
import tempfile
import unittest
from pathlib import Path

from tools.filesystem import (
    CreateDirectoryTool,
    CreateFileTool,
    DeleteFileTool,
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
)
from tools.tool_registry import create_default_tool_registry
from workspace.workspace import Workspace


class FileSystemToolsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Workspace(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_create_file_creates_nested_parents(self) -> None:
        result = CreateFileTool(self.workspace).execute(
            path="nested/demo.txt",
            content="hola",
        )

        self.assertTrue(result.success)
        target = Path(self._tmpdir.name) / "nested" / "demo.txt"
        self.assertTrue(target.is_file())
        self.assertEqual(target.read_text(encoding="utf-8"), "hola")

    def test_read_file_returns_content(self) -> None:
        target = Path(self._tmpdir.name) / "read-me.txt"
        target.write_text("contenido", encoding="utf-8")

        result = ReadFileTool(self.workspace).execute(path="read-me.txt")

        self.assertTrue(result.success)
        self.assertEqual(result.output["content"], "contenido")

    def test_write_file_overwrites_existing_file(self) -> None:
        target = Path(self._tmpdir.name) / "write-me.txt"
        target.write_text("viejo", encoding="utf-8")

        result = WriteFileTool(self.workspace).execute(
            path="write-me.txt",
            content="nuevo",
        )

        self.assertTrue(result.success)
        self.assertEqual(target.read_text(encoding="utf-8"), "nuevo")

    def test_write_file_fails_when_file_missing(self) -> None:
        result = WriteFileTool(self.workspace).execute(
            path="missing.txt",
            content="nuevo",
        )

        self.assertFalse(result.success)
        self.assertIn("no existe", result.error or "")

    def test_delete_file_removes_file(self) -> None:
        target = Path(self._tmpdir.name) / "delete-me.txt"
        target.write_text("temp", encoding="utf-8")

        result = DeleteFileTool(self.workspace).execute(path="delete-me.txt")

        self.assertTrue(result.success)
        self.assertFalse(target.exists())

    def test_create_directory_creates_nested_path(self) -> None:
        result = CreateDirectoryTool(self.workspace).execute(path="a/b/c")

        self.assertTrue(result.success)
        self.assertTrue((Path(self._tmpdir.name) / "a" / "b" / "c").is_dir())

    def test_list_directory_returns_entries(self) -> None:
        root = Path(self._tmpdir.name)
        (root / "alpha.txt").write_text("a", encoding="utf-8")
        (root / "beta").mkdir()

        result = ListDirectoryTool(self.workspace).execute(path=".")

        self.assertTrue(result.success)
        self.assertEqual(result.output["entries"], ["alpha.txt", "beta"])

    def test_blocks_parent_directory_traversal(self) -> None:
        result = CreateFileTool(self.workspace).execute(
            path="../../escape.txt",
            content="hack",
        )

        self.assertFalse(result.success)
        self.assertIn("..", result.error or "")

    def test_blocks_absolute_paths(self) -> None:
        result = CreateFileTool(self.workspace).execute(
            path="/etc/passwd",
            content="hack",
        )

        self.assertFalse(result.success)
        self.assertIn("absolut", (result.error or "").lower())

    def test_blocks_symlink_escape(self) -> None:
        outside_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outside_dir)
        outside_file = Path(outside_dir) / "secret.txt"
        outside_file.write_text("secret", encoding="utf-8")

        link_path = Path(self._tmpdir.name) / "escape-link"
        link_path.symlink_to(outside_file)

        result = ReadFileTool(self.workspace).execute(path="escape-link")

        self.assertFalse(result.success)
        self.assertIn("fuera del workspace", result.error or "")

    def test_default_registry_registers_filesystem_tools(self) -> None:
        registry = create_default_tool_registry(workspace=self.workspace)

        self.assertEqual(
            registry.list_names(),
            [
                "create_file",
                "read_file",
                "write_file",
                "delete_file",
                "list_directory",
                "create_directory",
            ],
        )
        self.assertTrue(all(registry.exists(name) for name in registry.list_names()))


if __name__ == "__main__":
    unittest.main()
