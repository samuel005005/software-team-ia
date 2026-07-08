# Prompt: Nuevo proyecto

Copia este prompt en Cursor Agent Mode con la rule **product_manager** activa.

---

## Contexto

Estoy iniciando un proyecto nuevo en la Software Factory. Necesito definir la especificación completa antes de diseñar arquitectura o escribir código.

## Proyecto

**Nombre:** [nombre-del-proyecto]

**Descripción:**
[Describe la idea en 2-5 oraciones]

**Usuarios objetivo:**
[Quién usará el producto]

**Restricciones conocidas:**
- Stack preferido (si hay): [Flutter / React / Python / etc.]
- Plazo: [si aplica]
- Otras: [si aplica]

## Tu tarea

Actúa como **Product Manager Agent**.

1. Lee `docs/SPEC.md` (plantilla actual).
2. Completa la especificación con:
   - Objetivo claro
   - Historias de usuario (formato: Como / Quiero / Para)
   - Criterios de aceptación verificables por historia
   - Alcance MVP vs fuera de alcance
   - Supuestos y riesgos
3. Actualiza `docs/SPEC.md` con el contenido final.
4. Agrega entrada inicial en `docs/CHANGELOG.md`.
5. NO escribas código ni arquitectura técnica.

## Formato de respuesta

Al terminar, reporta:
- Resumen del MVP
- Número de historias creadas
- Preguntas abiertas para el usuario
- Archivos modificados

## Siguiente paso

Cuando el usuario apruebe el SPEC, ejecutar **Architect** con `docs/SPEC.md`.
