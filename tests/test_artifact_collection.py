import unittest

from artifacts.artifact_collection import ArtifactCollection
from artifacts.code_artifact import CodeArtifact


class ArtifactCollectionTestCase(unittest.TestCase):
    def _artifact(self, path: str, content: str) -> CodeArtifact:
        return CodeArtifact(
            path=path,
            language="dart",
            content=content,
        )

    def test_add_and_list_paths(self) -> None:
        collection = ArtifactCollection()
        collection.add(self._artifact("lib/main.dart", "main"))
        collection.add(self._artifact("lib/app.dart", "app"))

        self.assertEqual(
            collection.list_paths(),
            ["lib/main.dart", "lib/app.dart"],
        )

    def test_find_returns_matching_artifact(self) -> None:
        collection = ArtifactCollection()
        artifact = self._artifact("lib/main.dart", "main")
        collection.add(artifact)

        self.assertIs(collection.find("lib/main.dart"), artifact)
        self.assertIsNone(collection.find("lib/missing.dart"))

    def test_add_replaces_existing_path(self) -> None:
        collection = ArtifactCollection()
        collection.add(self._artifact("lib/main.dart", "v1"))
        collection.add(self._artifact("lib/main.dart", "v2"))

        self.assertEqual(len(collection.artifacts), 1)
        self.assertEqual(collection.find("lib/main.dart").content, "v2")

    def test_to_dict_serializes_collection(self) -> None:
        collection = ArtifactCollection()
        collection.add(
            CodeArtifact(
                path="pubspec.yaml",
                language="yaml",
                content="name: demo",
                description="Manifest",
            )
        )

        data = collection.to_dict()

        self.assertEqual(len(data["artifacts"]), 1)
        self.assertEqual(data["artifacts"][0]["path"], "pubspec.yaml")
        self.assertEqual(data["artifacts"][0]["description"], "Manifest")


if __name__ == "__main__":
    unittest.main()
