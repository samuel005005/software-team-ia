import '../../../../../core/utils/result.dart';
import '../../domain/entities/admin_client.dart';
import '../../domain/entities/admin_client_appointment.dart';
import '../../domain/repositories/admin_clients_repository.dart';
import '../datasources/admin_clients_remote_data_source.dart';
import '../models/admin_client_dtos.dart';

class AdminClientsRepositoryImpl implements AdminClientsRepository {
  AdminClientsRepositoryImpl(this._remote);

  final AdminClientsRemoteDataSource _remote;

  @override
  Future<Result<List<AdminClient>>> listClients() async {
    final result = await _remote.execute(_remote.listClients);
    return result.when(
      success: (dto) => Success(dto.items.map((item) => item.toEntity()).toList()),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<AdminClient>> updateClient({
    required String userId,
    bool? isActive,
  }) async {
    final result = await _remote.execute(
      () => _remote.updateClient(
        userId,
        UpdateAdminClientRequestDto(isActive: isActive),
      ),
    );

    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<List<AdminClientAppointment>>> listClientAppointments(
    String userId,
  ) async {
    final result = await _remote.execute(() => _remote.listClientAppointments(userId));
    return result.when(
      success: (dto) => Success(dto.items.map((item) => item.toEntity()).toList()),
      error: (failure) => Error(failure),
    );
  }
}
