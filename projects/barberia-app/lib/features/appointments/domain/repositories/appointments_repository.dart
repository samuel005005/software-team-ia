import '../../../../core/utils/result.dart';
import '../entities/appointment_summary.dart';

abstract class AppointmentsRepository {
  Future<Result<List<AppointmentSummary>>> listMyAppointments();

  Future<Result<AppointmentSummary>> cancelAppointment(String appointmentId);
}
