# Prompt: Analizar proyecto existente

Copia este prompt en Cursor Agent Mode. Usar rule **product_manager** primero, luego **architect**.

---

## Contexto

Tengo un proyecto existente que quiero analizar, documentar y mejorar usando la Software Factory.

## Proyecto

**Ruta:** `projects/[nombre-proyecto]/`

**Objetivo del análisis:**
[Ej: documentar estado actual, detectar deuda técnica, planificar feature X]

## Tu tarea — Fase 1: Product Manager

1. Explora la estructura del proyecto en `projects/[nombre]/`.
2. Lee archivos clave: README, pubspec.yaml / package.json / requirements.txt, main entry point.
3. Identifica qué hace el proyecto hoy vs qué falta.
4. Actualiza `docs/SPEC.md` con:
   - Estado actual (as-is)
   - Historias existentes inferidas
   - Nuevas historias propuestas
   - Gaps y deuda funcional
5. NO modifiques código todavía.

## Tu tarea — Fase 2: Architect (siguiente sesión)

1. Lee `docs/SPEC.md` actualizado.
2. Documenta arquitectura real en `docs/ARCHITECTURE.md`:
   - Stack detectado
   - Estructura de carpetas actual
   - Módulos existentes
   - Problemas arquitectónicos
3. Crea plan de mejoras en `docs/TASKS.md`.

## Formato de respuesta

Reporta:
- Stack detectado
- Estado funcional actual
- Gaps identificados
- Propuesta de próximos pasos
- Archivos de documentación actualizados

## Siguiente paso

Ejecutar **Developer** con tareas priorizadas de `docs/TASKS.md`.
