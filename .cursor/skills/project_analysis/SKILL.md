---
name: project-analysis
description: Analyzes existing software projects for structure, technologies, architecture, dependencies, and issues. Generates docs/PROJECT_ANALYSIS.md. Use when onboarding an existing codebase, auditing project health, or before planning migrations.
---

# Project Analysis

## When to use
- Proyecto existente sin documentación SDD.
- Antes de Architect o refactor mayor.
- Usuario pide analizar estructura o deuda técnica.

## Inputs
- Ruta del proyecto (`projects/<nombre>/` o ruta indicada).
- `README.md`, manifests (`pubspec.yaml`, `package.json`, `requirements.txt`).
- Estructura de carpetas y código principal.

## Process
1. Leer `docs/SPEC.md` si existe (contexto funcional).
2. Explorar estructura, stack y dependencias.
3. Identificar arquitectura actual vs deseada.
4. Listar problemas, riesgos y oportunidades.
5. Generar `docs/PROJECT_ANALYSIS.md` usando plantilla en `docs/templates/PROJECT_ANALYSIS.template.md`.

## Output — `docs/PROJECT_ANALYSIS.md`
- Resumen ejecutivo
- Stack y dependencias
- Estructura actual
- Arquitectura detectada
- Problemas encontrados (severidad)
- Recomendaciones
- Próximos pasos (PM → Architect)

## Rules
- No modificar código.
- Evidencia con rutas de archivo.
- Distinguir hechos vs suposiciones.
