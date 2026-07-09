import '../../../../../core/utils/result.dart';
import '../../domain/entities/barber_schedule_appointment.dart';
import '../../domain/repositories/barber_schedule_repository.dart';
import '../datasources/barber_schedule_remote_data_source.dart';

class BarberScheduleRepositoryImpl implements BarberScheduleRepository {
  BarberScheduleRepositoryImpl(this._remote);

  final BarberScheduleRemoteDataSource _remote;

  @override
  Future<Result<List<BarberScheduleAppointment>>> getScheduleForDate({
    required DateTime date,
  }) async {
    final result = await _remote.execute(
      () => _remote.getSchedule(date: date),
    );
    return result.when(
      success: (dto) => Success(
        dto.items.map((item) => item.toEntity()).toList(),
      ),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<BarberScheduleAppointment>> updateAppointmentStatus({
    required String appointmentId,
    required String status,
  }) async {
    final result = await _remote.execute(
      () => _remote.updateAppointmentStatus(
        appointmentId: appointmentId,
        status: status,
      ),
    );
    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }
}
