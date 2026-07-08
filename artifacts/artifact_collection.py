from dataclasses import dataclass, field
from typing import Any

from artifacts.code_artifact import CodeArtifact


@dataclass
class ArtifactCollection:
    """Colección ordenada de artefactos de código generados."""

    artifacts: list[CodeArtifact] = field(default_factory=list)

    def add(self, artifact: CodeArtifact) -> None:
        existing = self.find(artifact.path)
        if existing is not None:
            self.artifacts.remove(existing)
        self.artifacts.append(artifact)

    def find(self, path: str) -> CodeArtifact | None:
        for artifact in self.artifacts:
            if artifact.path == path:
                return artifact
        return None

    def list_paths(self) -> list[str]:
        return [artifact.path for artifact in self.artifacts]

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
        }
