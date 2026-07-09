import 'package:barberia_app/features/appointments/data/models/appointment_dtos.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('AppointmentSummaryDto mapea JSON de API a entidad', () {
    final dto = AppointmentSummaryDto.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'status': 'confirmada',
      'scheduled_start': '2026-07-15T10:00:00-04:00',
      'scheduled_end': '2026-07-15T10:30:00-04:00',
      'service_name': 'Corte',
      'barber_display_name': 'Carlos',
    });

    final entity = dto.toEntity();

    expect(entity.id, '11111111-1111-1111-1111-111111111111');
    expect(entity.status, 'confirmada');
    expect(entity.serviceName, 'Corte');
    expect(entity.barberDisplayName, 'Carlos');
    expect(entity.scheduledStart, isNotNull);
    expect(entity.scheduledEnd, isNotNull);
  });

  test('AppointmentListResponseDto parsea lista de citas', () {
    final dto = AppointmentListResponseDto.fromJson({
      'items': [
        {
          'id': '11111111-1111-1111-1111-111111111111',
          'status': 'confirmada',
          'scheduled_start': '2026-07-15T10:00:00-04:00',
          'scheduled_end': '2026-07-15T10:30:00-04:00',
          'service_name': 'Corte',
          'barber_display_name': 'Carlos',
        },
        {
          'id': '22222222-2222-2222-2222-222222222222',
          'status': 'completada',
          'scheduled_start': '2026-06-01T14:00:00-04:00',
          'scheduled_end': '2026-06-01T14:30:00-04:00',
          'service_name': 'Barba',
          'barber_display_name': 'Luis',
        },
      ],
    });

    expect(dto.items, hasLength(2));
    expect(dto.items.first.serviceName, 'Corte');
    expect(dto.items.last.barberDisplayName, 'Luis');
  });
}
