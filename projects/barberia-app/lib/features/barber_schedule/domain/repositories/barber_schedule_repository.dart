import '../../../../../core/utils/result.dart';
import '../entities/barber_schedule_appointment.dart';

abstract interface class BarberScheduleRepository {
  Future<Result<List<BarberScheduleAppointment>>> getScheduleForDate({
    required DateTime date,
  });

  Future<Result<BarberScheduleAppointment>> updateAppointmentStatus({
    required String appointmentId,
    required String status,
  });
}
