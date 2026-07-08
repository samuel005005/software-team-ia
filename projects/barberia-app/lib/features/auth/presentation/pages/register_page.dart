import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/router/routes.dart';

/// Pantalla pública de registro (placeholder T-002).
class RegisterPage extends StatelessWidget {
  const RegisterPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Registro')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Módulo auth — el registro se implementará en Fase 3.',
            ),
            const SizedBox(height: 24),
            OutlinedButton(
              onPressed: () => context.go(AppRoutes.login),
              child: const Text('Volver al login'),
            ),
          ],
        ),
      ),
    );
  }
}
