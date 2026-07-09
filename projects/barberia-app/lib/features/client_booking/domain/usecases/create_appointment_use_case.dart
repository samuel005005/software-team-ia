import '../../../../core/application/use_case.dart';
import '../../../../core/utils/result.dart';
import '../entities/booked_appointment.dart';
import '../repositories/booking_repository.dart';

class CreateAppointmentParams {
  const CreateAppointmentParams({
    required this.barberUserId,
    required this.serviceId,
    required this.scheduledStartIso,
  });

  final String barberUserId;
  final String serviceId;
  final String scheduledStartIso;
}

class CreateAppointmentUseCase
    extends UseCase<BookedAppointment, CreateAppointmentParams> {
  CreateAppointmentUseCase(this._repository);

  final BookingRepository _repository;

  @override
  Future<Result<BookedAppointment>> call(CreateAppointmentParams params) {
    return _repository.createAppointment(
      barberUserId: params.barberUserId,
      serviceId: params.serviceId,
      scheduledStartIso: params.scheduledStartIso,
    );
  }
}
