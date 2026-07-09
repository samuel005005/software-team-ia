import 'package:barberia_app/features/barber_schedule/data/models/barber_availability_dtos.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('AvailabilityDayDto parsea bloque de disponibilidad', () {
    final dto = AvailabilityDayDto.fromJson({
      'weekday': 4,
      'start_time': '10:00:00',
      'end_time': '20:00:00',
      'is_active': true,
    });

    final entity = dto.toEntity();

    expect(entity.weekday, 4);
    expect(entity.startTime, '10:00:00');
    expect(entity.isActive, isTrue);
  });

  test('UpdateBarberAvailabilityRequestDto serializa semana completa', () {
    final dto = UpdateBarberAvailabilityRequestDto(
      items: [
        AvailabilityDayDto(
          weekday: 1,
          startTime: '09:00:00',
          endTime: '18:00:00',
          isActive: true,
        ),
        AvailabilityDayDto(
          weekday: 7,
          startTime: '00:00:00',
          endTime: '00:00:00',
          isActive: false,
        ),
      ],
    );

    expect(dto.toJson(), {
      'items': [
        {
          'weekday': 1,
          'start_time': '09:00:00',
          'end_time': '18:00:00',
          'is_active': true,
        },
        {
          'weekday': 7,
          'start_time': '00:00:00',
          'end_time': '00:00:00',
          'is_active': false,
        },
      ],
    });
  });
}
