import 'package:barberia_app/features/admin/business_hours/data/models/admin_business_hours_dtos.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('BusinessHoursDayDto parsea horario del local', () {
    final dto = BusinessHoursDayDto.fromJson({
      'weekday': 6,
      'open_time': '10:00:00',
      'close_time': '20:00:00',
      'is_closed': false,
    });

    final entity = dto.toEntity();

    expect(entity.weekday, 6);
    expect(entity.openTime, '10:00:00');
    expect(entity.isClosed, isFalse);
  });

  test('UpdateBusinessHoursRequestDto serializa semana completa', () {
    final dto = UpdateBusinessHoursRequestDto(
      items: [
        BusinessHoursDayDto(
          weekday: 1,
          openTime: '09:00:00',
          closeTime: '18:00:00',
          isClosed: false,
        ),
        BusinessHoursDayDto(
          weekday: 7,
          openTime: '00:00:00',
          closeTime: '00:00:00',
          isClosed: true,
        ),
      ],
    );

    expect(dto.toJson(), {
      'items': [
        {
          'weekday': 1,
          'open_time': '09:00:00',
          'close_time': '18:00:00',
          'is_closed': false,
        },
        {
          'weekday': 7,
          'open_time': '00:00:00',
          'close_time': '00:00:00',
          'is_closed': true,
        },
      ],
    });
  });
}
