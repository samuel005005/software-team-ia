import json
import unittest

from llm.base_provider import LLMProvider
from llm.llm_request import LLMRequest
from llm.llm_response import LLMResponse
from llm.mock_provider import MockLLMProvider


class MockLLMProviderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = MockLLMProvider(fixed_duration_ms=10)
        self.request = LLMRequest(
            system_prompt="Eres un Business Analyst experto.",
            user_prompt="Genera historias de usuario para una app de barbería.",
            model="mock-test-model",
            temperature=0.5,
            max_tokens=500,
        )

    def test_implements_llm_provider_interface(self) -> None:
        self.assertIsInstance(self.provider, LLMProvider)
        self.assertEqual(self.provider.provider_name, "mock")

    def test_receives_llm_request(self) -> None:
        response = self.provider.generate(self.request)
        self.assertIsInstance(response, LLMResponse)

    def test_returns_llm_response_with_content(self) -> None:
        response = self.provider.generate(self.request)

        self.assertTrue(response.content)
        parsed = json.loads(response.content)
        self.assertIn("user_stories", parsed)
        self.assertEqual(len(parsed["user_stories"]), 3)

    def test_metadata_fields(self) -> None:
        response = self.provider.generate(self.request)

        self.assertEqual(response.provider, "mock")
        self.assertEqual(response.model, "mock-test-model")
        self.assertIsNotNone(response.tokens_input)
        self.assertIsNotNone(response.tokens_output)
        self.assertIsNotNone(response.duration_ms)
        self.assertGreaterEqual(response.duration_ms, 10)
        self.assertEqual(response.metadata["mode"], "mock")

    def test_uses_default_model_when_not_provided(self) -> None:
        request = LLMRequest(
            system_prompt="Sistema",
            user_prompt="Usuario",
        )
        response = self.provider.generate(request)

        self.assertEqual(response.model, MockLLMProvider.DEFAULT_MODEL)

    def test_returns_structured_architect_response(self) -> None:
        request = LLMRequest(
            system_prompt="Eres Software Architect",
            user_prompt="Genera un SDD para el proyecto",
        )
        response = self.provider.generate(request)
        parsed = json.loads(response.content)

        self.assertIn("architecture", parsed)
        self.assertEqual(parsed["architecture"]["frontend"], "Flutter + Riverpod")

    def test_returns_structured_developer_response(self) -> None:
        request = LLMRequest(
            system_prompt="Eres un Flutter Developer experto en desarrollo.",
            user_prompt="Genera tareas de desarrollo basadas en el SDD del proyecto.",
        )
        response = self.provider.generate(request)
        parsed = json.loads(response.content)

        self.assertIn("tasks", parsed)
        self.assertEqual(len(parsed["tasks"]), 2)
        self.assertEqual(parsed["tasks"][0]["title"], "Configurar proyecto Flutter")

    def test_returns_structured_developer_code_response(self) -> None:
        request = LLMRequest(
            system_prompt="Eres un Flutter Developer experto en generación de proyectos.",
            user_prompt="Genera los archivos del proyecto Flutter en formato JSON.\n\nProyecto: barberia-app",
        )
        response = self.provider.generate(request)
        parsed = json.loads(response.content)

        self.assertIn("files", parsed)
        paths = {file_data["path"] for file_data in parsed["files"]}
        self.assertEqual(paths, {"pubspec.yaml", "lib/main.dart", "README.md"})

    def test_returns_structured_qa_response(self) -> None:
        request = LLMRequest(
            system_prompt="Eres un QA Engineer experto en aseguramiento de calidad.",
            user_prompt="Valida la calidad y completitud del proyecto según los artefactos.",
        )
        response = self.provider.generate(request)
        parsed = json.loads(response.content)

        self.assertIn("qa_report", parsed)
        self.assertEqual(parsed["qa_report"]["status"], "APROBADO")
        self.assertEqual(parsed["qa_report"]["checks_passed"], 3)


if __name__ == "__main__":
    unittest.main()
