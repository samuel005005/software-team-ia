import '../../../../core/utils/result.dart';
import '../../domain/entities/availability_data.dart';
import '../../domain/entities/barber_summary.dart';
import '../../domain/entities/booked_appointment.dart';
import '../../domain/repositories/booking_repository.dart';
import '../datasources/appointments_remote_data_source.dart';
import '../datasources/availability_remote_data_source.dart';
import '../datasources/barbers_remote_data_source.dart';

class BookingRepositoryImpl implements BookingRepository {
  BookingRepositoryImpl({
    required BarbersRemoteDataSource barbersRemote,
    required AvailabilityRemoteDataSource availabilityRemote,
    required AppointmentsRemoteDataSource appointmentsRemote,
  })  : _barbersRemote = barbersRemote,
        _availabilityRemote = availabilityRemote,
        _appointmentsRemote = appointmentsRemote;

  final BarbersRemoteDataSource _barbersRemote;
  final AvailabilityRemoteDataSource _availabilityRemote;
  final AppointmentsRemoteDataSource _appointmentsRemote;

  @override
  Future<Result<List<BarberSummary>>> listBarbersForService(
    String serviceId,
  ) async {
    final result = await _barbersRemote.execute(
      () => _barbersRemote.listBarbers(serviceId: serviceId),
    );
    return result.when(
      success: (dto) => Success(
        dto.items.map((item) => item.toEntity()).toList(),
      ),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<AvailabilityData>> getAvailability({
    required String serviceId,
    required DateTime date,
    String? barberId,
  }) async {
    final result = await _availabilityRemote.execute(
      () => _availabilityRemote.getAvailability(
        serviceId: serviceId,
        date: date,
        barberId: barberId,
      ),
    );
    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<BookedAppointment>> createAppointment({
    required String barberUserId,
    required String serviceId,
    required String scheduledStartIso,
  }) async {
    final result = await _appointmentsRemote.execute(
      () => _appointmentsRemote.createAppointment(
        barberUserId: barberUserId,
        serviceId: serviceId,
        scheduledStartIso: scheduledStartIso,
      ),
    );
    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }
}
