import 'package:flutter/material.dart';

class AppointmentStatusChip extends StatelessWidget {
  const AppointmentStatusChip({
    super.key,
    required this.status,
    required this.isUpcoming,
  });

  final String status;
  final bool isUpcoming;

  static String labelFor(String status) {
    return switch (status) {
      'pendiente' => 'Pendiente',
      'confirmada' => 'Confirmada',
      'en_progreso' => 'En progreso',
      'completada' => 'Completada',
      'cancelada' => 'Cancelada',
      'no_show' => 'No asistió',
      _ => status,
    };
  }

  Color _backgroundColor(ColorScheme scheme) {
    if (!isUpcoming) {
      return scheme.surfaceContainerHighest;
    }

    return switch (status) {
      'confirmada' => scheme.primaryContainer,
      'en_progreso' => scheme.tertiaryContainer,
      'pendiente' => scheme.secondaryContainer,
      _ => scheme.surfaceContainerHighest,
    };
  }

  Color _foregroundColor(ColorScheme scheme) {
    if (!isUpcoming) {
      return scheme.onSurfaceVariant;
    }

    return switch (status) {
      'confirmada' => scheme.onPrimaryContainer,
      'en_progreso' => scheme.onTertiaryContainer,
      'pendiente' => scheme.onSecondaryContainer,
      _ => scheme.onSurfaceVariant,
    };
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;

    return Chip(
      label: Text(labelFor(status)),
      backgroundColor: _backgroundColor(scheme),
      labelStyle: TextStyle(color: _foregroundColor(scheme)),
      visualDensity: VisualDensity.compact,
      side: BorderSide.none,
    );
  }
}
