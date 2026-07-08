from dataclasses import asdict, dataclass, field
from pathlib import PurePosixPath
from typing import Any


@dataclass
class CodeArtifact:
    """Representa un archivo de código generado por un agente."""

    path: str
    language: str
    content: str
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def size(self) -> int:
        return len(self.content)

    def extension(self) -> str:
        return PurePosixPath(self.path).suffix.lstrip(".")

    def filename(self) -> str:
        return PurePosixPath(self.path).name

    def directory(self) -> str:
        parent = PurePosixPath(self.path).parent
        if str(parent) == ".":
            return ""
        return str(parent)

    def is_empty(self) -> bool:
        return not self.content.strip()
