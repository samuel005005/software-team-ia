import '../../../../../core/application/use_case.dart';
import '../../../../../core/utils/result.dart';
import '../entities/admin_service.dart';
import '../repositories/admin_services_repository.dart';

class ListAdminServicesUseCase extends UseCase<List<AdminService>, NoParams> {
  ListAdminServicesUseCase(this._repository);

  final AdminServicesRepository _repository;

  @override
  Future<Result<List<AdminService>>> call(NoParams params) {
    return _repository.listServices();
  }
}

class CreateAdminServiceParams {
  const CreateAdminServiceParams({
    required this.name,
    required this.durationMinutes,
    required this.priceDop,
    this.description,
    this.isActive = true,
  });

  final String name;
  final int durationMinutes;
  final String priceDop;
  final String? description;
  final bool isActive;
}

class CreateAdminServiceUseCase extends UseCase<AdminService, CreateAdminServiceParams> {
  CreateAdminServiceUseCase(this._repository);

  final AdminServicesRepository _repository;

  @override
  Future<Result<AdminService>> call(CreateAdminServiceParams params) {
    return _repository.createService(
      name: params.name,
      durationMinutes: params.durationMinutes,
      priceDop: params.priceDop,
      description: params.description,
      isActive: params.isActive,
    );
  }
}

class UpdateAdminServiceParams {
  const UpdateAdminServiceParams({
    required this.id,
    this.name,
    this.durationMinutes,
    this.priceDop,
    this.description,
    this.isActive,
  });

  final String id;
  final String? name;
  final int? durationMinutes;
  final String? priceDop;
  final String? description;
  final bool? isActive;
}

class UpdateAdminServiceUseCase extends UseCase<AdminService, UpdateAdminServiceParams> {
  UpdateAdminServiceUseCase(this._repository);

  final AdminServicesRepository _repository;

  @override
  Future<Result<AdminService>> call(UpdateAdminServiceParams params) {
    return _repository.updateService(
      id: params.id,
      name: params.name,
      durationMinutes: params.durationMinutes,
      priceDop: params.priceDop,
      description: params.description,
      isActive: params.isActive,
    );
  }
}
