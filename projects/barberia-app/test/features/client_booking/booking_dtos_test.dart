import 'package:barberia_app/features/client_booking/data/models/booking_dtos.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('AvailabilityResponseDto parsea barberos y slots ISO8601', () {
    final dto = AvailabilityResponseDto.fromJson({
      'service_id': '11111111-1111-1111-1111-111111111111',
      'date': '2026-07-15',
      'barbers': [
        {
          'user_id': '22222222-2222-2222-2222-222222222222',
          'display_name': 'Carlos',
          'bio': 'Cortes clásicos',
          'photo_url': 'https://cdn.example.com/carlos.jpg',
          'is_bookable': true,
        },
      ],
      'slots': [
        {
          'start': '2026-07-15T10:00:00-04:00',
          'end': '2026-07-15T10:30:00-04:00',
          'barber_user_id': '22222222-2222-2222-2222-222222222222',
        },
      ],
    });

    final entity = dto.toEntity();

    expect(entity.serviceId, '11111111-1111-1111-1111-111111111111');
    expect(entity.barbers, hasLength(1));
    expect(entity.barbers.first.displayName, 'Carlos');
    expect(entity.slots, hasLength(1));
    expect(entity.slots.first.barberUserId,
        '22222222-2222-2222-2222-222222222222');
    expect(entity.slots.first.startIso, '2026-07-15T10:00:00-04:00');
  });

  test('AppointmentCreateRequestDto serializa scheduled_start ISO8601', () {
    final dto = AppointmentCreateRequestDto(
      barberUserId: '22222222-2222-2222-2222-222222222222',
      serviceId: '11111111-1111-1111-1111-111111111111',
      scheduledStartIso: '2026-07-15T10:00:00-04:00',
    );

    final json = dto.toJson();

    expect(json['barber_user_id'], '22222222-2222-2222-2222-222222222222');
    expect(json['service_id'], '11111111-1111-1111-1111-111111111111');
    expect(json['scheduled_start'], '2026-07-15T10:00:00-04:00');
  });

  test('AppointmentResponseDto mapea a BookedAppointment', () {
    final dto = AppointmentResponseDto.fromJson({
      'id': '33333333-3333-3333-3333-333333333333',
      'status': 'confirmada',
      'scheduled_start': '2026-07-15T10:00:00-04:00',
      'scheduled_end': '2026-07-15T10:30:00-04:00',
      'service_id': '11111111-1111-1111-1111-111111111111',
      'service_name': 'Corte clásico',
      'barber_user_id': '22222222-2222-2222-2222-222222222222',
      'barber_display_name': 'Carlos',
    });

    final entity = dto.toEntity();

    expect(entity.id, '33333333-3333-3333-3333-333333333333');
    expect(entity.status, 'confirmada');
    expect(entity.serviceName, 'Corte clásico');
    expect(entity.barberDisplayName, 'Carlos');
  });
}
