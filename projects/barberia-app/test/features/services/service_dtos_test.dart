import 'package:barberia_app/features/services/data/models/service_dtos.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('ServiceSummaryDto mapea JSON de API a entidad', () {
    final dto = ServiceSummaryDto.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'name': 'Corte clásico',
      'description': 'Incluye lavado',
      'duration_minutes': 30,
      'price_dop': '400.00',
      'is_active': true,
    });

    final entity = dto.toEntity();

    expect(entity.id, '11111111-1111-1111-1111-111111111111');
    expect(entity.name, 'Corte clásico');
    expect(entity.description, 'Incluye lavado');
    expect(entity.durationMinutes, 30);
    expect(entity.priceDop, '400.00');
  });

  test('ServiceListResponseDto parsea lista de servicios', () {
    final dto = ServiceListResponseDto.fromJson({
      'items': [
        {
          'id': '11111111-1111-1111-1111-111111111111',
          'name': 'Afeitado',
          'duration_minutes': 20,
          'price_dop': '250.50',
        },
      ],
    });

    expect(dto.items, hasLength(1));
    expect(dto.items.first.name, 'Afeitado');
  });
}
