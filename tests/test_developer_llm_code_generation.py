import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from agents.developer_agent import DeveloperAgent
from artifacts.artifact_writer import ArtifactWriter
from artifacts.developer_fallback import build_fallback_collection
from llm.llm_response import LLMResponse
from llm.mock_provider import MockLLMProvider
from memory.memory_store import MemoryStore
from prompts.developer_code_prompt import build as build_code_prompt
from state.project_state import ProjectState
from tools.tool_registry import create_default_tool_registry
from workspace.workspace import Workspace


class DeveloperLLMCodeGenerationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Workspace(self._tmpdir.name)
        self.artifact_writer = ArtifactWriter(
            create_default_tool_registry(self.workspace)
        )
        self.state = ProjectState(
            project_name="barberia-app",
            description="Crear una aplicación móvil para administrar una barbería",
            software_design_document="Software Design Document generado por MockLLMProvider",
            architecture="Frontend: Flutter + Riverpod | Backend: FastAPI | DB: PostgreSQL",
        )
        self.tasks = [
            {
                "id": 1,
                "title": "Configurar proyecto Flutter",
                "description": "Crear carpetas lib/core, lib/features y lib/shared",
                "status": "pending",
            }
        ]

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_developer_code_prompt_requests_json_files(self) -> None:
        request = build_code_prompt(
            objective=self.state.description or "",
            project_name=self.state.project_name or "",
            software_design_document=self.state.software_design_document or "",
            tasks=self.tasks,
            architecture=self.state.architecture or "",
        )

        self.assertIn("files", request.system_prompt)
        self.assertIn("Genera los archivos del proyecto Flutter", request.user_prompt)
        self.assertIn("barberia-app", request.user_prompt)

    def test_mock_provider_returns_valid_developer_code_json(self) -> None:
        request = build_code_prompt(
            objective=self.state.description or "",
            project_name=self.state.project_name or "",
            software_design_document=self.state.software_design_document or "",
            tasks=self.tasks,
            architecture=self.state.architecture or "",
        )
        response = MockLLMProvider().generate(request)
        parsed = json.loads(response.content)

        self.assertIn("files", parsed)
        paths = {file_data["path"] for file_data in parsed["files"]}
        self.assertEqual(paths, {"pubspec.yaml", "lib/main.dart", "README.md"})

    def test_developer_uses_llm_generated_artifacts(self) -> None:
        developer = DeveloperAgent(
            llm_provider=MockLLMProvider(),
            memory_store=MemoryStore(),
            artifact_writer=self.artifact_writer,
        )

        result = developer.execute(self.state)

        self.assertEqual(developer.last_artifact_source, "developer_llm")
        self.assertEqual(len(developer.last_artifacts.artifacts), 3)
        self.assertTrue(
            any("pipeline LLM de código" in log for log in result.logs)
        )
        self.assertTrue(
            (Path(self._tmpdir.name) / "barberia-app" / "lib" / "main.dart").is_file()
        )

    def test_developer_falls_back_on_invalid_code_json(self) -> None:
        provider = MagicMock()
        provider.generate.side_effect = [
            LLMResponse(
                content=json.dumps({"tasks": self.tasks}),
                provider="mock",
                model="mock-model",
            ),
            LLMResponse(content="{invalid json}", provider="mock", model="mock-model"),
        ]

        developer = DeveloperAgent(
            llm_provider=provider,
            memory_store=MemoryStore(),
            artifact_writer=self.artifact_writer,
        )
        result = developer.execute(self.state)

        self.assertEqual(developer.last_artifact_source, "developer_fallback")
        self.assertTrue(any("Fallback de artefactos" in log for log in result.logs))
        self.assertEqual(len(result.generated_files), 3)

    def test_developer_falls_back_when_provider_fails(self) -> None:
        provider = MagicMock()
        provider.generate.side_effect = [
            LLMResponse(
                content=json.dumps({"tasks": self.tasks}),
                provider="mock",
                model="mock-model",
            ),
            RuntimeError("provider unavailable"),
        ]

        developer = DeveloperAgent(
            llm_provider=provider,
            memory_store=MemoryStore(),
            artifact_writer=self.artifact_writer,
        )
        result = developer.execute(self.state)

        self.assertEqual(developer.last_artifact_source, "developer_fallback")
        self.assertEqual(len(result.generated_files), 3)

    def test_fallback_matches_previous_template_output(self) -> None:
        fallback = build_fallback_collection(self.state, self.tasks)
        developer = DeveloperAgent(
            llm_provider=MagicMock(),
            memory_store=MemoryStore(),
            artifact_writer=self.artifact_writer,
        )
        provider = developer._llm_provider
        assert provider is not None
        provider.generate.side_effect = [
            LLMResponse(
                content=json.dumps({"tasks": self.tasks}),
                provider="mock",
                model="mock-model",
            ),
            LLMResponse(content='{"files": []}', provider="mock", model="mock-model"),
        ]

        developer.execute(self.state)

        for expected, actual in zip(
            fallback.artifacts,
            developer.last_artifacts.artifacts,
            strict=True,
        ):
            self.assertEqual(expected.path, actual.path)
            self.assertEqual(expected.language, actual.language)
            self.assertEqual(expected.content, actual.content)


if __name__ == "__main__":
    unittest.main()
