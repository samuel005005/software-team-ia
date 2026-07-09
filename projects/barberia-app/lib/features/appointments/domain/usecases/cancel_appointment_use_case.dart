import '../../../../core/application/use_case.dart';
import '../../../../core/utils/result.dart';
import '../entities/appointment_summary.dart';
import '../repositories/appointments_repository.dart';

class CancelAppointmentParams {
  const CancelAppointmentParams(this.appointmentId);

  final String appointmentId;
}

class CancelAppointmentUseCase
    extends UseCase<AppointmentSummary, CancelAppointmentParams> {
  CancelAppointmentUseCase(this._repository);

  final AppointmentsRepository _repository;

  @override
  Future<Result<AppointmentSummary>> call(CancelAppointmentParams params) {
    return _repository.cancelAppointment(params.appointmentId);
  }
}
