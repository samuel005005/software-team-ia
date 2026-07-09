import '../../../../core/network/remote_data_source.dart';
import '../models/booking_dtos.dart';

class AppointmentsRemoteDataSource extends RemoteDataSource {
  AppointmentsRemoteDataSource(super.dio);

  Future<AppointmentResponseDto> createAppointment({
    required String barberUserId,
    required String serviceId,
    required String scheduledStartIso,
  }) async {
    final request = AppointmentCreateRequestDto(
      barberUserId: barberUserId,
      serviceId: serviceId,
      scheduledStartIso: scheduledStartIso,
    );

    final response = await dio.post<Map<String, dynamic>>(
      '/appointments',
      data: request.toJson(),
    );
    return AppointmentResponseDto.fromJson(response.data!);
  }
}
