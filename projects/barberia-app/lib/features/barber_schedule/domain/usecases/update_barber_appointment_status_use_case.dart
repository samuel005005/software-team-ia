import '../../../../core/application/use_case.dart';
import '../../../../core/utils/result.dart';
import '../entities/barber_schedule_appointment.dart';
import '../repositories/barber_schedule_repository.dart';

class UpdateBarberAppointmentStatusParams {
  const UpdateBarberAppointmentStatusParams({
    required this.appointmentId,
    required this.status,
  });

  final String appointmentId;
  final String status;
}

class UpdateBarberAppointmentStatusUseCase
    extends UseCase<BarberScheduleAppointment, UpdateBarberAppointmentStatusParams> {
  UpdateBarberAppointmentStatusUseCase(this._repository);

  final BarberScheduleRepository _repository;

  @override
  Future<Result<BarberScheduleAppointment>> call(
    UpdateBarberAppointmentStatusParams params,
  ) {
    return _repository.updateAppointmentStatus(
      appointmentId: params.appointmentId,
      status: params.status,
    );
  }
}
