# Prompt: Auditoría de seguridad

Copia este prompt en Cursor Agent Mode con la rule **security** activa.

---

## Contexto

Necesito auditar la seguridad del proyecto antes de entrega o despliegue.

## Referencias

- Código: `projects/[nombre-proyecto]/`
- `docs/ARCHITECTURE.md` (flujos de auth y datos)
- `.gitignore`
- Archivos de configuración y dependencias

## Proyecto

**Ruta:** `projects/[nombre-proyecto]/`

**Tipo:** [web / mobile / API / fullstack]

## Tu tarea

Actúa como **Security Agent**.

1. Busca secretos expuestos (API keys, tokens, passwords).
2. Revisa validación y sanitización de inputs.
3. Evalúa autenticación y autorización.
4. Revisa dependencias conocidas con vulnerabilidades.
5. Verifica manejo de datos sensibles y logs.
6. Documenta en `docs/SECURITY_REPORT.md`.
7. NO modifiques código (solo reporta).

## Checklist

- [ ] Sin credenciales en el repositorio
- [ ] `.env` en `.gitignore`
- [ ] Inputs validados en puntos de entrada
- [ ] Auth implementada correctamente
- [ ] Sin datos sensibles en logs
- [ ] Dependencias sin CVEs críticos
- [ ] HTTPS/TLS donde aplique
- [ ] Permisos mínimos necesarios

## Formato de respuesta

Actualiza `docs/REVIEW.md` y reporta:

```markdown
## Security Audit — [Fecha]

### Veredicto: SEGURO / RIESGOS / INSEGURO

### Hallazgos CRITICAL/HIGH
| ID | Ubicación | Descripción | Mitigación |

### Acciones inmediatas
1. 
```

## Siguiente paso

Issues CRITICAL → Developer corrige → re-audit.  
Sin CRITICAL → marcar veredicto final en `REVIEW.md`.
