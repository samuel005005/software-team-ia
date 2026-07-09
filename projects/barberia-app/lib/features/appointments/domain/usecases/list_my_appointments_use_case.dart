import '../../../../core/application/use_case.dart';
import '../../../../core/utils/result.dart';
import '../entities/appointment_summary.dart';
import '../repositories/appointments_repository.dart';

class ListMyAppointmentsUseCase
    extends UseCase<List<AppointmentSummary>, NoParams> {
  ListMyAppointmentsUseCase(this._repository);

  final AppointmentsRepository _repository;

  @override
  Future<Result<List<AppointmentSummary>>> call(NoParams params) {
    return _repository.listMyAppointments();
  }
}
