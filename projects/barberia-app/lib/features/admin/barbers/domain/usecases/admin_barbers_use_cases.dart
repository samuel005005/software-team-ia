import '../../../../../core/application/use_case.dart';
import '../../../../../core/utils/result.dart';
import '../entities/admin_barber.dart';
import '../repositories/admin_barbers_repository.dart';

class ListAdminBarbersUseCase extends UseCase<List<AdminBarber>, NoParams> {
  ListAdminBarbersUseCase(this._repository);

  final AdminBarbersRepository _repository;

  @override
  Future<Result<List<AdminBarber>>> call(NoParams params) {
    return _repository.listBarbers();
  }
}

class CreateAdminBarberParams {
  const CreateAdminBarberParams({
    required this.email,
    required this.password,
    required this.displayName,
    this.bio,
    this.photoUrl,
    this.isBookable = true,
  });

  final String email;
  final String password;
  final String displayName;
  final String? bio;
  final String? photoUrl;
  final bool isBookable;
}

class CreateAdminBarberUseCase extends UseCase<AdminBarber, CreateAdminBarberParams> {
  CreateAdminBarberUseCase(this._repository);

  final AdminBarbersRepository _repository;

  @override
  Future<Result<AdminBarber>> call(CreateAdminBarberParams params) {
    return _repository.createBarber(
      email: params.email,
      password: params.password,
      displayName: params.displayName,
      bio: params.bio,
      photoUrl: params.photoUrl,
      isBookable: params.isBookable,
    );
  }
}

class UpdateAdminBarberParams {
  const UpdateAdminBarberParams({
    required this.userId,
    this.displayName,
    this.bio,
    this.photoUrl,
    this.isBookable,
    this.isActive,
  });

  final String userId;
  final String? displayName;
  final String? bio;
  final String? photoUrl;
  final bool? isBookable;
  final bool? isActive;
}

class UpdateAdminBarberUseCase extends UseCase<AdminBarber, UpdateAdminBarberParams> {
  UpdateAdminBarberUseCase(this._repository);

  final AdminBarbersRepository _repository;

  @override
  Future<Result<AdminBarber>> call(UpdateAdminBarberParams params) {
    return _repository.updateBarber(
      userId: params.userId,
      displayName: params.displayName,
      bio: params.bio,
      photoUrl: params.photoUrl,
      isBookable: params.isBookable,
      isActive: params.isActive,
    );
  }
}

class GetBarberServiceIdsParams {
  const GetBarberServiceIdsParams(this.userId);

  final String userId;
}

class GetBarberServiceIdsUseCase extends UseCase<List<String>, GetBarberServiceIdsParams> {
  GetBarberServiceIdsUseCase(this._repository);

  final AdminBarbersRepository _repository;

  @override
  Future<Result<List<String>>> call(GetBarberServiceIdsParams params) {
    return _repository.getBarberServiceIds(params.userId);
  }
}

class SetBarberServicesParams {
  const SetBarberServicesParams({
    required this.userId,
    required this.serviceIds,
  });

  final String userId;
  final List<String> serviceIds;
}

class SetBarberServicesUseCase extends UseCase<List<String>, SetBarberServicesParams> {
  SetBarberServicesUseCase(this._repository);

  final AdminBarbersRepository _repository;

  @override
  Future<Result<List<String>>> call(SetBarberServicesParams params) {
    return _repository.setBarberServices(
      userId: params.userId,
      serviceIds: params.serviceIds,
    );
  }
}
