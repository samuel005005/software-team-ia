# Barbería App

Aplicación móvil Flutter para gestión de citas de barbería.

## Arquitectura

Clean Architecture por features:

```text
lib/
├── app/                 # Bootstrap, router, tema
├── core/                # Cross-cutting: config, red, errores, use cases base
├── shared/              # Widgets y utilidades compartidas
└── features/<feature>/
    ├── domain/          # Entidades y contratos de repositorio
    ├── data/            # DTOs, datasources, implementaciones
    ├── application/     # Casos de uso
    └── presentation/    # UI, widgets, providers Riverpod
```

## Stack

- Flutter SDK >= 3.0
- Riverpod — estado e inyección de dependencias
- GoRouter — navegación
- Dio — HTTP

## Comandos

```bash
flutter pub get
flutter analyze
flutter test
flutter run
flutter run --dart-define=APP_ENV=staging
```

## Entornos

| `APP_ENV` | Descripción |
|-----------|-------------|
| `dev` (default) | Desarrollo local |
| `staging` | Pre-producción |
| `production` | Producción |

Configuración en `lib/core/config/app_config.dart`.

## Estado

- **T-001** ✅ Base Clean Architecture
- **T-002** ✅ Navegación pública/autenticada con guards por rol
- **T-003** ✅ Estado global y providers base (theme/locale/loading)
- **T-004** ✅ Cliente HTTP, errores e interceptores de auth
- **T-005** ✅ Almacenamiento seguro de sesión (flutter_secure_storage)
- **T-006+** Backend y dominio pendientes
