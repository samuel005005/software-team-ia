import unittest

from artifacts.code_artifact import CodeArtifact


class CodeArtifactTestCase(unittest.TestCase):
    def _artifact(self) -> CodeArtifact:
        return CodeArtifact(
            path="lib/main.dart",
            language="dart",
            content="void main() {}",
            description="Punto de entrada de la app",
            metadata={"agent": "developer"},
        )

    def test_to_dict_serializes_all_fields(self) -> None:
        data = self._artifact().to_dict()

        self.assertEqual(data["path"], "lib/main.dart")
        self.assertEqual(data["language"], "dart")
        self.assertEqual(data["content"], "void main() {}")
        self.assertEqual(data["description"], "Punto de entrada de la app")
        self.assertEqual(data["metadata"]["agent"], "developer")

    def test_filename(self) -> None:
        self.assertEqual(self._artifact().filename(), "main.dart")

    def test_extension(self) -> None:
        self.assertEqual(self._artifact().extension(), "dart")

    def test_directory(self) -> None:
        self.assertEqual(self._artifact().directory(), "lib")

    def test_directory_for_root_file(self) -> None:
        artifact = CodeArtifact(
            path="README.md",
            language="markdown",
            content="# Demo",
        )

        self.assertEqual(artifact.directory(), "")

    def test_size_counts_characters(self) -> None:
        self.assertEqual(self._artifact().size(), len("void main() {}"))

    def test_is_empty_detects_blank_content(self) -> None:
        empty = CodeArtifact(path="lib/empty.dart", language="dart", content="   ")
        filled = self._artifact()

        self.assertTrue(empty.is_empty())
        self.assertFalse(filled.is_empty())


if __name__ == "__main__":
    unittest.main()
