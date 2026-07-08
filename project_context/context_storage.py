import json
from pathlib import Path

from project_context.project_snapshot import ProjectSnapshot
from workspace.workspace import Workspace


class ContextStorage:
    """Persistencia de snapshots bajo projects/<project>/.factory/context.json."""

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    def save(self, snapshot: ProjectSnapshot) -> Path:
        context_file = self._context_file(snapshot.project_name)
        context_file.parent.mkdir(parents=True, exist_ok=True)
        context_file.write_text(
            json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return context_file

    def load(self, project_name: str) -> ProjectSnapshot | None:
        context_file = self._context_file(project_name)
        if not context_file.is_file():
            return None

        data = json.loads(context_file.read_text(encoding="utf-8"))
        return ProjectSnapshot.from_dict(data)

    def _context_file(self, project_name: str) -> Path:
        return self._workspace.resolve(f"{project_name}/.factory/context.json")
