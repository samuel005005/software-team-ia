import '../../../../core/utils/result.dart';
import '../../domain/entities/appointment_summary.dart';
import '../../domain/repositories/appointments_repository.dart';
import '../datasources/appointments_remote_data_source.dart';

class AppointmentsRepositoryImpl implements AppointmentsRepository {
  AppointmentsRepositoryImpl(this._remote);

  final AppointmentsRemoteDataSource _remote;

  @override
  Future<Result<List<AppointmentSummary>>> listMyAppointments() async {
    final result = await _remote.execute(_remote.listMyAppointments);
    return result.when(
      success: (dto) => Success(
        dto.items.map((item) => item.toEntity()).toList(),
      ),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<AppointmentSummary>> cancelAppointment(
    String appointmentId,
  ) async {
    final result = await _remote.execute(
      () => _remote.cancelAppointment(appointmentId),
    );
    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }
}
