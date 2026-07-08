---
name: security-audit
description: Audits project security for authentication, authorization, secrets, input validation, data exposure, and common vulnerabilities. Generates docs/SECURITY_REPORT.md. Use for security reviews before release or after major changes.
---

# Security Audit

## When to use
- Pre-entrega o release.
- Cambios en auth, permisos, APIs.
- Activar con rule `security`.

## Inputs
- Código en `projects/`
- `docs/ARCHITECTURE.md` (auth, datos sensibles)
- `docs/SPEC.md` (roles)
- `.gitignore`, env examples, dependencias

## Audit areas
1. **Secretos** — no keys/tokens en repo; `.env` ignorado.
2. **AuthN/AuthZ** — JWT/sesión, roles Cliente/Barbero/Admin.
3. **Inputs** — validación server-side y client-side.
4. **Datos** — PII, logs, respuestas de error.
5. **Dependencias** — CVEs conocidos (si verificable).
6. **Transporte** — HTTPS, CORS, headers de seguridad.
7. **OWASP Top 10** — injection, broken access control, etc.

## Severity
- **CRITICAL** — explotable, datos expuestos, auth bypass.
- **HIGH** — riesgo significativo con mitigación incompleta.
- **MEDIUM** — hardening recomendado.
- **LOW** — mejora defensiva.

## Output
Generar `docs/SECURITY_REPORT.md` usando `docs/templates/SECURITY_REPORT.template.md`.

## Rules
- No modificar código.
- Evidencia por hallazgo (ubicación, escenario).
- CRITICAL bloquea veredicto SEGURO.
- Veredicto: SEGURO / RIESGOS / INSEGURO.
