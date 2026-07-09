import '../../../../../core/utils/result.dart';
import '../../domain/entities/admin_barber.dart';
import '../../domain/repositories/admin_barbers_repository.dart';
import '../datasources/admin_barbers_remote_data_source.dart';
import '../models/admin_barber_dtos.dart';

class AdminBarbersRepositoryImpl implements AdminBarbersRepository {
  AdminBarbersRepositoryImpl(this._remote);

  final AdminBarbersRemoteDataSource _remote;

  @override
  Future<Result<List<AdminBarber>>> listBarbers() async {
    final result = await _remote.execute(_remote.listBarbers);
    return result.when(
      success: (dto) => Success(dto.items.map((item) => item.toEntity()).toList()),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<AdminBarber>> createBarber({
    required String email,
    required String password,
    required String displayName,
    String? bio,
    String? photoUrl,
    bool isBookable = true,
  }) async {
    final result = await _remote.execute(
      () => _remote.createBarber(
        CreateAdminBarberRequestDto(
          email: email,
          password: password,
          displayName: displayName,
          bio: bio,
          photoUrl: photoUrl,
          isBookable: isBookable,
        ),
      ),
    );

    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<AdminBarber>> updateBarber({
    required String userId,
    String? displayName,
    String? bio,
    String? photoUrl,
    bool? isBookable,
    bool? isActive,
  }) async {
    final result = await _remote.execute(
      () => _remote.updateBarber(
        userId,
        UpdateAdminBarberRequestDto(
          displayName: displayName,
          bio: bio,
          photoUrl: photoUrl,
          isBookable: isBookable,
          isActive: isActive,
        ),
      ),
    );

    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<List<String>>> getBarberServiceIds(String userId) async {
    final result = await _remote.execute(() => _remote.getBarberServices(userId));
    return result.when(
      success: (dto) => Success(dto.items.map((item) => item.id).toList()),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<List<String>>> setBarberServices({
    required String userId,
    required List<String> serviceIds,
  }) async {
    final result = await _remote.execute(
      () => _remote.setBarberServices(userId, serviceIds),
    );
    return result.when(
      success: (dto) => Success(dto.items.map((item) => item.id).toList()),
      error: (failure) => Error(failure),
    );
  }
}
