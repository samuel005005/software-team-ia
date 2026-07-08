import shutil
import tempfile
import unittest
from pathlib import Path

from workspace.workspace import Workspace, WorkspaceError


class WorkspaceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Workspace(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_creates_root_directory_if_missing(self) -> None:
        root = Path(tempfile.mkdtemp())
        shutil.rmtree(root)

        workspace = Workspace(str(root))

        self.assertTrue(workspace.root.is_dir())
        shutil.rmtree(root)

    def test_resolve_relative_path_inside_workspace(self) -> None:
        resolved = self.workspace.resolve("nested/file.txt")

        self.assertEqual(
            resolved,
            (Path(self._tmpdir.name) / "nested" / "file.txt").resolve(),
        )

    def test_exists_returns_false_for_invalid_path(self) -> None:
        self.assertFalse(self.workspace.exists("../../outside.txt"))

    def test_absolute_path_matches_resolve(self) -> None:
        self.assertEqual(
            self.workspace.absolute_path("demo.txt"),
            self.workspace.resolve("demo.txt"),
        )

    def test_rejects_parent_directory_traversal(self) -> None:
        with self.assertRaises(WorkspaceError) as ctx:
            self.workspace.resolve("../outside.txt")

        self.assertIn("..", str(ctx.exception))

    def test_rejects_absolute_paths(self) -> None:
        with self.assertRaises(WorkspaceError) as ctx:
            self.workspace.resolve("/etc/passwd")

        self.assertIn("absolut", str(ctx.exception).lower())

    def test_rejects_symlink_escape(self) -> None:
        outside_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outside_dir)
        outside_file = Path(outside_dir) / "secret.txt"
        outside_file.write_text("secret", encoding="utf-8")

        link_path = Path(self._tmpdir.name) / "escape-link"
        link_path.symlink_to(outside_file)

        with self.assertRaises(WorkspaceError) as ctx:
            self.workspace.resolve("escape-link")

        self.assertIn("fuera del workspace", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
