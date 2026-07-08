from artifacts.artifact_collection import ArtifactCollection
from artifacts.code_artifact import CodeArtifact
from tools.tool_registry import ToolRegistry
from tools.tool_result import ToolResult


class ArtifactWriter:
    """Persiste CodeArtifact usando herramientas del ToolRegistry."""

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry

    def write(self, artifact: CodeArtifact) -> ToolResult:
        create_file_tool = self._tool_registry.create_tool("create_file")
        return create_file_tool.execute(
            path=artifact.path,
            content=artifact.content,
        )

    def write_all(self, collection: ArtifactCollection) -> list[ToolResult]:
        return [self.write(artifact) for artifact in collection.artifacts]
