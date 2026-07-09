import '../../../../../core/utils/result.dart';
import '../../domain/entities/admin_service.dart';
import '../../domain/repositories/admin_services_repository.dart';
import '../datasources/admin_services_remote_data_source.dart';
import '../models/admin_service_dtos.dart';

class AdminServicesRepositoryImpl implements AdminServicesRepository {
  AdminServicesRepositoryImpl(this._remote);

  final AdminServicesRemoteDataSource _remote;

  @override
  Future<Result<List<AdminService>>> listServices() async {
    final result = await _remote.execute(_remote.listServices);
    return result.when(
      success: (dto) => Success(dto.items.map((item) => item.toEntity()).toList()),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<AdminService>> createService({
    required String name,
    required int durationMinutes,
    required String priceDop,
    String? description,
    bool isActive = true,
  }) async {
    final result = await _remote.execute(
      () => _remote.createService(
        CreateAdminServiceRequestDto(
          name: name,
          durationMinutes: durationMinutes,
          priceDop: priceDop,
          description: description,
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
  Future<Result<AdminService>> updateService({
    required String id,
    String? name,
    int? durationMinutes,
    String? priceDop,
    String? description,
    bool? isActive,
  }) async {
    final result = await _remote.execute(
      () => _remote.updateService(
        id,
        UpdateAdminServiceRequestDto(
          name: name,
          durationMinutes: durationMinutes,
          priceDop: priceDop,
          description: description,
          isActive: isActive,
        ),
      ),
    );

    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }
}
