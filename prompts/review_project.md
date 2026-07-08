# Prompt: Revisión de proyecto

Copia este prompt en Cursor Agent Mode con la rule **reviewer** activa.

---

## Contexto

El desarrollo del MVP está completo. Necesito una revisión de código antes de entregar.

## Referencias

Lee:
- `docs/ARCHITECTURE.md`
- `docs/TASKS.md`
- `docs/REVIEW.md` (sección QA si existe)
- Código en `projects/[nombre-proyecto]/`

## Alcance de la revisión

**Proyecto:** `projects/[nombre-proyecto]/`

**Cambios a revisar:**
- Todo el MVP / o commits recientes / o archivos: [listar]

## Tu tarea

Actúa como **Code Reviewer Agent**.

1. Revisa calidad, mantenibilidad y adherencia arquitectónica.
2. Detecta code smells, duplicación, nombres confusos, falta de tests.
3. Verifica que no hay secretos hardcodeados.
4. Documenta hallazgos en `docs/REVIEW.md` (sección Code Review).
5. NO modifiques código (solo reporta).

## Criterios de evaluación

| Aspecto | Qué revisar |
|---------|-------------|
| Arquitectura | Alineación con ARCHITECTURE.md |
| Legibilidad | Nombres, estructura, comentarios |
| Tests | Cobertura de lógica crítica |
| Seguridad básica | Inputs, secrets, permisos |
| Deuda técnica | Hacks, TODOs críticos |

## Formato de respuesta

Actualiza `docs/REVIEW.md` y reporta:

- **Veredicto:** APROBADO / CAMBIOS REQUERIDOS
- Issues por severidad (crítico / mayor / menor)
- Aspectos positivos
- Recomendaciones para siguiente iteración

## Siguiente paso

Si hay issues críticos → Developer corrige → re-review.  
Si aprobado → ejecutar **Security** (opcional) o marcar entrega final.
