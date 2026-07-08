# Prompt: Implementar funcionalidad

Copia este prompt en Cursor Agent Mode con la rule **developer** activa.

---

## Contexto

Necesito implementar una funcionalidad siguiendo la especificación y arquitectura del proyecto.

## Referencias obligatorias

Lee antes de codificar:
- `docs/SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/TASKS.md`

## Tarea a implementar

**ID de tarea:** [T-XXX]

**Historia relacionada:** [US-XXX]

**Descripción:**
[Qué hay que implementar]

**Criterios de aceptación:**
- [ ] Criterio 1
- [ ] Criterio 2

**Proyecto:** `projects/[nombre-proyecto]/`

## Tu tarea

Actúa como **Developer Agent**.

1. Lee la documentación de referencia.
2. Implementa la funcionalidad en el proyecto.
3. Sigue la arquitectura definida en `ARCHITECTURE.md`.
4. Escribe tests si la lógica es crítica.
5. Marca la tarea como `[x]` en `docs/TASKS.md`.
6. Agrega entrada en `docs/CHANGELOG.md`.
7. NO modifiques `SPEC.md` ni `ARCHITECTURE.md`.

## Restricciones

- Cambios mínimos y enfocados en la tarea.
- Sin sobre-ingeniería.
- Sin secretos en el código.
- Mantener convenciones del proyecto existente.

## Formato de respuesta

```markdown
## Implementación — [T-XXX]

### Archivos modificados
- 

### Cambios realizados
- 

### Cómo probar
```bash
# comandos
```

### Deuda técnica / notas
- 
```

## Siguiente paso

Cuando todas las tareas MVP estén `[x]`, ejecutar **QA** con `docs/SPEC.md`.
