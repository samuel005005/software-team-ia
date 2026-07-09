import 'package:barberia_app/features/admin/barbers/data/models/admin_barber_dtos.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('AdminBarberDto parsea barbero admin', () {
    final dto = AdminBarberDto.fromJson({
      'user_id': '11111111-1111-1111-1111-111111111111',
      'email': 'barbero@test.com',
      'display_name': 'Carlos',
      'bio': 'Fade expert',
      'is_bookable': true,
      'is_active': false,
    });

    final entity = dto.toEntity();

    expect(entity.email, 'barbero@test.com');
    expect(entity.displayName, 'Carlos');
    expect(entity.isActive, isFalse);
  });
}
