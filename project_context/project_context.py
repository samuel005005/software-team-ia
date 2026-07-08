from pathlib import Path

from project_context.context_storage import ContextStorage
from project_context.project_snapshot import ProjectSnapshot, utc_now_iso
from workspace.workspace import Workspace

KEY_FILES = (
    "README.md",
    "package.json",
    "pubspec.yaml",
    "requirements.txt",
    "pom.xml",
    "build.gradle",
)
MAIN_FILE_CANDIDATES = (
    "lib/main.dart",
    "src/main.py",
    "main.py",
    "src/index.ts",
    "src/index.js",
)


class ProjectContextService:
    """Analiza proyectos existentes y mantiene contexto persistente por proyecto."""

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace
        self._storage = ContextStorage(workspace)

    def analyze(self, project_name: str) -> ProjectSnapshot:
        project_path = self._workspace.resolve(project_name)
        if not project_path.is_dir():
            raise FileNotFoundError(f"Proyecto no encontrado: {project_name}")

        files_summary = self._build_files_summary(project_path)
        structure = self._build_structure(project_path)
        technologies = self._detect_technologies(files_summary, structure)
        detected_stack = self._detect_stack(files_summary, technologies)

        now = utc_now_iso()
        previous = self.load(project_name)
        created_at = previous.created_at if previous is not None else now

        return ProjectSnapshot(
            project_path=str(project_path),
            project_name=project_name,
            detected_stack=detected_stack,
            files_summary=files_summary,
            structure=structure,
            technologies=technologies,
            metadata={"analyzer": "project_context_v1"},
            created_at=created_at,
            updated_at=now,
        )

    def save(self, snapshot: ProjectSnapshot) -> Path:
        return self._storage.save(snapshot)

    def load(self, project_name: str) -> ProjectSnapshot | None:
        return self._storage.load(project_name)

    def _build_files_summary(self, project_path: Path) -> dict[str, object]:
        summary: dict[str, object] = {
            "exists": {},
            "main_files": [],
        }
        exists = {}
        for filename in KEY_FILES:
            exists[filename] = (project_path / filename).is_file()
        summary["exists"] = exists

        main_files: list[str] = []
        for relative_path in MAIN_FILE_CANDIDATES:
            if (project_path / relative_path).is_file():
                main_files.append(relative_path)
        summary["main_files"] = main_files
        return summary

    def _build_structure(self, project_path: Path) -> dict[str, list[str]]:
        top_level_dirs: list[str] = []
        top_level_files: list[str] = []
        for entry in sorted(project_path.iterdir(), key=lambda item: item.name):
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                top_level_dirs.append(entry.name)
            elif entry.is_file():
                top_level_files.append(entry.name)

        important_files: list[str] = []
        for relative_path in MAIN_FILE_CANDIDATES:
            if (project_path / relative_path).is_file():
                important_files.append(relative_path)

        return {
            "top_level_dirs": top_level_dirs,
            "top_level_files": top_level_files,
            "important_files": important_files,
        }

    def _detect_technologies(
        self,
        files_summary: dict[str, object],
        structure: dict[str, list[str]],
    ) -> list[str]:
        exists = dict(files_summary.get("exists", {}))
        technologies: list[str] = []

        if exists.get("pubspec.yaml"):
            technologies.extend(["Flutter", "Dart"])
        if exists.get("package.json"):
            technologies.extend(["Node.js", "JavaScript"])
        if exists.get("requirements.txt"):
            technologies.append("Python")
        if exists.get("pom.xml"):
            technologies.append("Java")
        if exists.get("build.gradle"):
            technologies.extend(["Gradle", "JVM"])

        top_level_dirs = structure.get("top_level_dirs", [])
        if "lib" in top_level_dirs and "Flutter" not in technologies:
            technologies.append("Dart")
        if "src" in top_level_dirs and "Node.js" not in technologies:
            technologies.append("Source-based project")

        return sorted(set(technologies))

    def _detect_stack(
        self,
        files_summary: dict[str, object],
        technologies: list[str],
    ) -> str:
        exists = dict(files_summary.get("exists", {}))
        if exists.get("pubspec.yaml"):
            return "flutter"
        if exists.get("package.json"):
            return "node"
        if exists.get("requirements.txt"):
            return "python"
        if exists.get("pom.xml") or exists.get("build.gradle"):
            return "java"
        if technologies:
            return technologies[0].lower().replace(" ", "_")
        return "unknown"
