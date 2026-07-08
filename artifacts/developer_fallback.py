import json
from typing import Any

from artifacts.artifact_collection import ArtifactCollection
from artifacts.code_artifact import CodeArtifact
from state.project_state import ProjectState


def pubspec_name(project_slug: str) -> str:
    sanitized = project_slug.replace("-", "_").lower()
    if sanitized and sanitized[0].isdigit():
        sanitized = f"app_{sanitized}"
    return sanitized or "flutter_app"


def build_pubspec_content(*, pubspec_name: str, description: str) -> str:
    return (
        f"name: {pubspec_name}\n"
        f"description: {description}\n"
        "publish_to: 'none'\n"
        "version: 1.0.0+1\n"
        "\n"
        "environment:\n"
        "  sdk: '>=3.0.0 <4.0.0'\n"
        "\n"
        "dependencies:\n"
        "  flutter:\n"
        "    sdk: flutter\n"
        "\n"
        "dev_dependencies:\n"
        "  flutter_test:\n"
        "    sdk: flutter\n"
        "  flutter_lints: ^3.0.0\n"
        "\n"
        "flutter:\n"
        "  uses-material-design: true\n"
    )


def build_main_dart_content(*, pubspec_name: str) -> str:
    return (
        "import 'package:flutter/material.dart';\n"
        "\n"
        "void main() {\n"
        "  runApp(const MyApp());\n"
        "}\n"
        "\n"
        "class MyApp extends StatelessWidget {\n"
        "  const MyApp({super.key});\n"
        "\n"
        "  @override\n"
        "  Widget build(BuildContext context) {\n"
        "    return MaterialApp(\n"
        f"      title: '{pubspec_name}',\n"
        "      home: Scaffold(\n"
        "        appBar: AppBar(title: const Text('Hello World')),\n"
        "        body: const Center(child: Text('Hello World')),\n"
        "      ),\n"
        "    );\n"
        "  }\n"
        "}\n"
    )


def build_readme_content(state: ProjectState, tasks: list[dict[str, Any]]) -> str:
    lines = [
        f"# {state.project_name or 'Proyecto'}",
        "",
        "## Descripción",
        state.description or "Sin descripción",
        "",
        "## Arquitectura",
        state.architecture or "No definida",
        "",
        "## Tareas generadas",
    ]

    for task in tasks:
        task_id = task.get("id", "?")
        title = task.get("title", "Sin título")
        status = task.get("status", "pending")
        lines.append(f"- [{task_id}] {title} ({status})")
        description = task.get("description")
        if description:
            lines.append(f"  {description}")

    lines.extend(
        [
            "",
            "## Resultado del Developer",
            json.dumps(tasks, ensure_ascii=False, indent=2),
        ]
    )
    return "\n".join(lines)


def build_fallback_collection(
    state: ProjectState,
    tasks: list[dict[str, Any]],
) -> ArtifactCollection:
    """Colección determinista usada cuando falla la generación de código via LLM."""
    project_slug = state.project_name or "proyecto"
    package_name = pubspec_name(project_slug)
    collection = ArtifactCollection()
    collection.add(
        CodeArtifact(
            path=f"{project_slug}/pubspec.yaml",
            language="yaml",
            content=build_pubspec_content(
                pubspec_name=package_name,
                description=state.description or "Flutter Hello World",
            ),
            description="Manifiesto del proyecto Flutter",
            metadata={"source": "developer_fallback", "template": "flutter_hello_world"},
        )
    )
    collection.add(
        CodeArtifact(
            path=f"{project_slug}/lib/main.dart",
            language="dart",
            content=build_main_dart_content(pubspec_name=package_name),
            description="Punto de entrada Flutter Hello World",
            metadata={"source": "developer_fallback", "template": "flutter_hello_world"},
        )
    )
    collection.add(
        CodeArtifact(
            path=f"{project_slug}/README.md",
            language="markdown",
            content=build_readme_content(state, tasks),
            description="Resumen del resultado generado por el Developer",
            metadata={"source": "developer_fallback", "template": "flutter_hello_world"},
        )
    )
    return collection
