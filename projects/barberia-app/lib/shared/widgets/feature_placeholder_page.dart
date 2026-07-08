import 'package:flutter/material.dart';

/// Contenido placeholder sin scaffold (para usar dentro de [AuthenticatedShell]).
class FeaturePlaceholderPage extends StatelessWidget {
  const FeaturePlaceholderPage({
    super.key,
    required this.title,
    required this.module,
  });

  final String title;
  final String module;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 12),
          Text(
            'Módulo $module — implementación pendiente.',
            style: Theme.of(context).textTheme.bodyLarge,
          ),
        ],
      ),
    );
  }
}
