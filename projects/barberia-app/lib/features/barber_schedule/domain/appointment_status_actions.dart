class BarberStatusAction {
  const BarberStatusAction({
    required this.targetStatus,
    required this.label,
  });

  final String targetStatus;
  final String label;
}

List<BarberStatusAction> allowedBarberActions({
  required String currentStatus,
  required DateTime scheduledStart,
  required DateTime now,
}) {
  final canMarkNoShow = !scheduledStart.isAfter(now);

  return switch (currentStatus) {
    'pendiente' => [
      const BarberStatusAction(targetStatus: 'confirmada', label: 'Confirmar'),
      if (canMarkNoShow)
        const BarberStatusAction(targetStatus: 'no_show', label: 'No asistió'),
    ],
    'confirmada' => [
      const BarberStatusAction(targetStatus: 'en_progreso', label: 'Iniciar'),
      if (canMarkNoShow)
        const BarberStatusAction(targetStatus: 'no_show', label: 'No asistió'),
    ],
    'en_progreso' => [
      const BarberStatusAction(targetStatus: 'completada', label: 'Completar'),
    ],
    _ => const <BarberStatusAction>[],
  };
}

String successMessageFor(String targetStatus) {
  return switch (targetStatus) {
    'confirmada' => 'Cita confirmada',
    'en_progreso' => 'Cita iniciada',
    'completada' => 'Cita completada',
    'no_show' => 'Cita marcada como no asistió',
    _ => 'Estado actualizado',
  };
}

String confirmationTitleFor(String targetStatus) {
  return switch (targetStatus) {
    'no_show' => '¿Confirmar que el cliente no asistió?',
    'completada' => '¿Completar la cita?',
    _ => '¿Confirmar cambio de estado?',
  };
}
