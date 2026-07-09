import '../../../../../core/utils/result.dart';
import '../entities/admin_barber.dart';

abstract class AdminBarbersRepository {
  Future<Result<List<AdminBarber>>> listBarbers();

  Future<Result<AdminBarber>> createBarber({
    required String email,
    required String password,
    required String displayName,
    String? bio,
    String? photoUrl,
    bool isBookable = true,
  });

  Future<Result<AdminBarber>> updateBarber({
    required String userId,
    String? displayName,
    String? bio,
    String? photoUrl,
    bool? isBookable,
    bool? isActive,
  });

  Future<Result<List<String>>> getBarberServiceIds(String userId);

  Future<Result<List<String>>> setBarberServices({
    required String userId,
    required List<String> serviceIds,
  });
}
