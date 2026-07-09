import '../../../../../core/application/use_case.dart';
import '../../../../../core/utils/result.dart';
import '../entities/admin_client.dart';
import '../entities/admin_client_appointment.dart';
import '../repositories/admin_clients_repository.dart';

class ListAdminClientsUseCase extends UseCase<List<AdminClient>, NoParams> {
  ListAdminClientsUseCase(this._repository);

  final AdminClientsRepository _repository;

  @override
  Future<Result<List<AdminClient>>> call(NoParams params) {
    return _repository.listClients();
  }
}

class UpdateAdminClientParams {
  const UpdateAdminClientParams({
    required this.userId,
    this.isActive,
  });

  final String userId;
  final bool? isActive;
}

class UpdateAdminClientUseCase extends UseCase<AdminClient, UpdateAdminClientParams> {
  UpdateAdminClientUseCase(this._repository);

  final AdminClientsRepository _repository;

  @override
  Future<Result<AdminClient>> call(UpdateAdminClientParams params) {
    return _repository.updateClient(
      userId: params.userId,
      isActive: params.isActive,
    );
  }
}

class ListClientAppointmentsParams {
  const ListClientAppointmentsParams(this.userId);

  final String userId;
}

class ListClientAppointmentsUseCase
    extends UseCase<List<AdminClientAppointment>, ListClientAppointmentsParams> {
  ListClientAppointmentsUseCase(this._repository);

  final AdminClientsRepository _repository;

  @override
  Future<Result<List<AdminClientAppointment>>> call(ListClientAppointmentsParams params) {
    return _repository.listClientAppointments(params.userId);
  }
}
