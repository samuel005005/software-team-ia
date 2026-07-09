import 'package:barberia_app/features/barber_schedule/data/models/barber_schedule_dtos.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('BarberScheduleAppointmentDto parsea JSON del API', () {
    final dto = BarberScheduleAppointmentDto.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'status': 'confirmada',
      'scheduled_start': '2026-07-09T09:00:00-04:00',
      'scheduled_end': '2026-07-09T09:30:00-04:00',
      'service_id': '22222222-2222-2222-2222-222222222222',
      'service_name': 'Corte',
      'client_user_id': '33333333-3333-3333-3333-333333333333',
      'client_display_name': 'Juan Pérez',
    });

    final entity = dto.toEntity();

    expect(entity.id, '11111111-1111-1111-1111-111111111111');
    expect(entity.status, 'confirmada');
    expect(entity.serviceName, 'Corte');
    expect(entity.clientDisplayName, 'Juan Pérez');
    expect(entity.scheduledStart, isA<DateTime>());
    expect(entity.scheduledEnd, isA<DateTime>());
  });

  test('BarberScheduleResponseDto parsea lista vacía', () {
    final dto = BarberScheduleResponseDto.fromJson({
      'from_date': '2026-07-09',
      'to_date': '2026-07-09',
      'items': [],
    });

    expect(dto.fromDate, DateTime(2026, 7, 9));
    expect(dto.toDate, DateTime(2026, 7, 9));
    expect(dto.items, isEmpty);
  });

  test('BarberScheduleResponseDto preserva orden de items', () {
    final dto = BarberScheduleResponseDto.fromJson({
      'from_date': '2026-07-09',
      'to_date': '2026-07-09',
      'items': [
        {
          'id': '11111111-1111-1111-1111-111111111111',
          'status': 'confirmada',
          'scheduled_start': '2026-07-09T09:00:00-04:00',
          'scheduled_end': '2026-07-09T09:30:00-04:00',
          'service_id': '22222222-2222-2222-2222-222222222222',
          'service_name': 'Corte',
          'client_user_id': '33333333-3333-3333-3333-333333333333',
          'client_display_name': 'Juan Pérez',
        },
        {
          'id': '44444444-4444-4444-4444-444444444444',
          'status': 'confirmada',
          'scheduled_start': '2026-07-09T14:00:00-04:00',
          'scheduled_end': '2026-07-09T14:45:00-04:00',
          'service_id': '22222222-2222-2222-2222-222222222222',
          'service_name': 'Barba',
          'client_user_id': '55555555-5555-5555-5555-555555555555',
          'client_display_name': 'María López',
        },
      ],
    });

    expect(dto.items, hasLength(2));
    expect(dto.items[0].serviceName, 'Corte');
    expect(dto.items[1].serviceName, 'Barba');
  });
}
