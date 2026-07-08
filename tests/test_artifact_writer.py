import tempfile
import unittest
from pathlib import Path

from artifacts.artifact_collection import ArtifactCollection
from artifacts.artifact_writer import ArtifactWriter
from artifacts.code_artifact import CodeArtifact
from tools.tool_registry import create_default_tool_registry
from workspace.workspace import Workspace


class ArtifactWriterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Workspace(self._tmpdir.name)
        self.writer = ArtifactWriter(create_default_tool_registry(self.workspace))

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_write_creates_file_using_create_file_tool(self) -> None:
        artifact = CodeArtifact(
            path="demo/README.md",
            language="markdown",
            content="# Demo",
        )

        result = self.writer.write(artifact)

        self.assertTrue(result.success)
        target = Path(self._tmpdir.name) / "demo" / "README.md"
        self.assertTrue(target.is_file())
        self.assertEqual(target.read_text(encoding="utf-8"), "# Demo")

    def test_write_all_persists_collection(self) -> None:
        collection = ArtifactCollection()
        collection.add(
            CodeArtifact(
                path="alpha.txt",
                language="text",
                content="alpha",
            )
        )
        collection.add(
            CodeArtifact(
                path="nested/beta.txt",
                language="text",
                content="beta",
            )
        )

        results = self.writer.write_all(collection)

        self.assertEqual(len(results), 2)
        self.assertTrue(all(result.success for result in results))
        self.assertTrue((Path(self._tmpdir.name) / "alpha.txt").is_file())
        self.assertTrue((Path(self._tmpdir.name) / "nested" / "beta.txt").is_file())


if __name__ == "__main__":
    unittest.main()
