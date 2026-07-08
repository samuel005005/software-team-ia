from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProjectSnapshot:
    """Representa el estado analizado de un proyecto en un momento dado."""

    project_path: str
    project_name: str
    detected_stack: str
    files_summary: dict[str, Any] = field(default_factory=dict)
    structure: dict[str, list[str]] = field(default_factory=dict)
    technologies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_path": self.project_path,
            "project_name": self.project_name,
            "detected_stack": self.detected_stack,
            "files_summary": dict(self.files_summary),
            "structure": {key: list(value) for key, value in self.structure.items()},
            "technologies": list(self.technologies),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectSnapshot":
        return cls(
            project_path=str(data.get("project_path", "")),
            project_name=str(data.get("project_name", "")),
            detected_stack=str(data.get("detected_stack", "unknown")),
            files_summary=dict(data.get("files_summary", {})),
            structure={
                str(key): list(value)
                for key, value in dict(data.get("structure", {})).items()
            },
            technologies=list(data.get("technologies", [])),
            metadata=dict(data.get("metadata", {})),
            created_at=str(data.get("created_at", utc_now_iso())),
            updated_at=str(data.get("updated_at", utc_now_iso())),
        )
