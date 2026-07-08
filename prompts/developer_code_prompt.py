import json
from typing import Any

from llm.llm_request import LLMRequest

TEMPERATURE = 0.2
MAX_TOKENS = 4000

RESPONSE_FORMAT = """\
Responde únicamente con JSON válido en este formato:
{
  "files": [
    {
      "path": "pubspec.yaml",
      "language": "yaml",
      "description": "Manifiesto del proyecto Flutter",
      "content": "name: demo_app\\ndescription: Demo\\n..."
    },
    {
      "path": "lib/main.dart",
      "language": "dart",
      "description": "Punto de entrada de la app",
      "content": "import 'package:flutter/material.dart';\\n..."
    },
    {
      "path": "README.md",
      "language": "markdown",
      "description": "Documentación del proyecto",
      "content": "# Demo\\n..."
    }
  ]
}"""


def build(
    *,
    objective: str,
    project_name: str,
    software_design_document: str,
    tasks: list[dict[str, Any]],
    architecture: str = "",
) -> LLMRequest:
    tasks_json = json.dumps(tasks, ensure_ascii=False, indent=2)

    system_prompt = (
        "Eres un Flutter Developer experto en generación de proyectos mínimos ejecutables.\n"
        "Tu rol: generar los archivos iniciales del proyecto como artefactos de código.\n\n"
        "Restricciones:\n"
        "- Incluir pubspec.yaml, lib/main.dart y README.md como mínimo\n"
        "- Las rutas deben ser relativas al directorio raíz del proyecto\n"
        "- El contenido debe ser código válido y ejecutable\n"
        "- Responder solo con JSON válido\n\n"
        f"{RESPONSE_FORMAT}"
    )

    user_prompt = (
        "Genera los archivos del proyecto Flutter en formato JSON.\n\n"
        f"Proyecto: {project_name or 'proyecto'}\n\n"
        f"Objetivo:\n{objective or 'Sin objetivo definido'}\n\n"
        f"Software Design Document:\n{software_design_document or 'No disponible'}\n\n"
        f"Arquitectura:\n{architecture or 'No definida'}\n\n"
        f"Tareas de desarrollo:\n{tasks_json}"
    )

    return LLMRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
