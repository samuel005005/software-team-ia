import 'package:barberia_app/features/admin/services/data/models/admin_service_dtos.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('AdminServiceDto parsea servicio admin con estado activo', () {
    final dto = AdminServiceDto.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'name': 'Corte clásico',
      'duration_minutes': 30,
      'price_dop': '400.00',
      'is_active': false,
    });

    final entity = dto.toEntity();

    expect(entity.isActive, isFalse);
    expect(entity.name, 'Corte clásico');
  });

  test('CreateAdminServiceRequestDto serializa payload', () {
    const dto = CreateAdminServiceRequestDto(
      name: 'Afeitado',
      durationMinutes: 20,
      priceDop: '250.00',
      description: 'Tradicional',
    );

    expect(dto.toJson(), {
      'name': 'Afeitado',
      'duration_minutes': 20,
      'price_dop': '250.00',
      'description': 'Tradicional',
      'is_active': true,
    });
  });
}
