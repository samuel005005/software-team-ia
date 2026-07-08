import json
import re
import time

from artifacts.developer_fallback import (
    build_main_dart_content,
    build_pubspec_content,
    build_readme_content,
    pubspec_name,
)
from llm.base_provider import LLMProvider
from llm.llm_request import LLMRequest
from llm.llm_response import LLMResponse
from state.project_state import ProjectState


class MockLLMProvider(LLMProvider):
    """Proveedor simulado para desarrollo y pruebas sin APIs externas."""

    DEFAULT_MODEL = "mock-model-v1"

    def __init__(self, fixed_duration_ms: int = 5) -> None:
        self._fixed_duration_ms = fixed_duration_ms

    @property
    def provider_name(self) -> str:
        return "mock"

    def generate(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()
        content = self._build_content(request)
        duration_ms = max(
            self._fixed_duration_ms,
            int((time.perf_counter() - started) * 1000),
        )

        tokens_input = self._estimate_tokens(request.system_prompt, request.user_prompt)
        tokens_output = self._estimate_tokens(content)

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=request.model or self.DEFAULT_MODEL,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            duration_ms=duration_ms,
            metadata={"mode": "mock", "temperature": str(request.temperature)},
        )

    def _build_content(self, request: LLMRequest) -> str:
        system = request.system_prompt.lower()
        user = request.user_prompt.lower()

        if "software execution planner" in system or "genera un plan de ejecución" in user:
            return json.dumps(
                {
                    "nodes": [
                        "analyst",
                        "architect",
                        "developer",
                        "qa",
                    ]
                },
                ensure_ascii=False,
                indent=2,
            )

        if "software architect" in system or "genera un software design document" in user:
            return json.dumps(
                {
                    "architecture": {
                        "frontend": "Flutter + Riverpod",
                        "backend": "FastAPI",
                        "database": "PostgreSQL",
                    },
                    "patterns": ["Clean Architecture", "Feature First"],
                    "sdd": "Software Design Document generado por MockLLMProvider",
                },
                ensure_ascii=False,
                indent=2,
            )

        if "business analyst" in system or "genera historias de usuario" in user:
            return json.dumps(
                {
                    "user_stories": [
                        "Como usuario quiero registrarme",
                        "Como usuario quiero iniciar sesión",
                        "Como usuario quiero gestionar mi información",
                    ]
                },
                ensure_ascii=False,
                indent=2,
            )

        if "genera los archivos del proyecto flutter" in user:
            return self._build_developer_code_content(request)

        if "genera tareas" in user:
            return json.dumps(
                {
                    "tasks": [
                        {
                            "id": 1,
                            "title": "Configurar proyecto Flutter",
                            "description": "Crear carpetas lib/core, lib/features y lib/shared con Clean Architecture",
                            "status": "pending",
                        },
                        {
                            "id": 2,
                            "title": "Implementar autenticación JWT",
                            "description": "Registro, inicio de sesión y Secure Storage en el cliente",
                            "status": "pending",
                        },
                    ]
                },
                ensure_ascii=False,
                indent=2,
            )

        if "qa engineer" in system or "valida la calidad" in user:
            return json.dumps(
                {
                    "qa_report": {
                        "status": "APROBADO",
                        "checks_passed": 3,
                        "checks_total": 3,
                        "details": [
                            "Historias de usuario: OK",
                            "Arquitectura técnica: OK",
                            "Tareas de desarrollo: OK",
                        ],
                    }
                },
                ensure_ascii=False,
                indent=2,
            )

        if "software reviewer" in system or "revisa el resultado del agente" in user:
            return json.dumps(
                {
                    "approved": True,
                    "score": 0.94,
                    "summary": "Mock review passed",
                    "issues": [],
                    "recommendations": ["Consider adding more detail"],
                },
                ensure_ascii=False,
                indent=2,
            )

        return json.dumps(
            {
                "message": "Respuesta simulada del MockLLMProvider",
                "system_prompt_preview": request.system_prompt[:80],
                "user_prompt_preview": request.user_prompt[:80],
            },
            ensure_ascii=False,
            indent=2,
        )

    def _build_developer_code_content(self, request: LLMRequest) -> str:
        project_slug = self._extract_project_name(request.user_prompt) or "barberia-app"
        package_name = pubspec_name(project_slug)
        tasks = [
            {
                "id": 1,
                "title": "Configurar proyecto Flutter",
                "description": "Crear carpetas lib/core, lib/features y lib/shared con Clean Architecture",
                "status": "pending",
            },
            {
                "id": 2,
                "title": "Implementar autenticación JWT",
                "description": "Registro, inicio de sesión y Secure Storage en el cliente",
                "status": "pending",
            },
        ]
        state = ProjectState(
            project_name=project_slug,
            description="Crear una aplicación móvil para administrar una barbería",
            architecture="Frontend: Flutter + Riverpod | Backend: FastAPI | DB: PostgreSQL",
        )

        return json.dumps(
            {
                "files": [
                    {
                        "path": "pubspec.yaml",
                        "language": "yaml",
                        "description": "Manifiesto del proyecto Flutter",
                        "content": build_pubspec_content(
                            pubspec_name=package_name,
                            description=state.description or "Flutter Hello World",
                        ),
                    },
                    {
                        "path": "lib/main.dart",
                        "language": "dart",
                        "description": "Punto de entrada Flutter Hello World",
                        "content": build_main_dart_content(pubspec_name=package_name),
                    },
                    {
                        "path": "README.md",
                        "language": "markdown",
                        "description": "Resumen del resultado generado por el Developer",
                        "content": build_readme_content(state, tasks),
                    },
                ]
            },
            ensure_ascii=False,
            indent=2,
        )

    @staticmethod
    def _extract_project_name(user_prompt: str) -> str | None:
        match = re.search(r"Proyecto:\s*(\S+)", user_prompt)
        if match is None:
            return None
        return match.group(1).strip()

    def _estimate_tokens(self, *texts: str) -> int:
        combined = " ".join(text for text in texts if text)
        return max(1, len(combined.split()))
