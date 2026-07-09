import '../../../../core/utils/result.dart';
import '../entities/availability_data.dart';
import '../entities/barber_summary.dart';
import '../entities/booked_appointment.dart';

abstract class BookingRepository {
  Future<Result<List<BarberSummary>>> listBarbersForService(String serviceId);

  Future<Result<AvailabilityData>> getAvailability({
    required String serviceId,
    required DateTime date,
    String? barberId,
  });

  Future<Result<BookedAppointment>> createAppointment({
    required String barberUserId,
    required String serviceId,
    required String scheduledStartIso,
  });
}
