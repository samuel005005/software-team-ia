import '../../../../../core/network/remote_data_source.dart';
import '../../domain/usecases/get_barber_schedule_use_case.dart';
import '../models/barber_schedule_dtos.dart';

class BarberScheduleRemoteDataSource extends RemoteDataSource {
  BarberScheduleRemoteDataSource(super.dio);

  Future<BarberScheduleResponseDto> getSchedule({required DateTime date}) async {
    final response = await dio.get<Map<String, dynamic>>(
      '/barber/schedule',
      queryParameters: {
        'date': GetBarberScheduleUseCase.formatDateIso(date),
      },
    );
    return BarberScheduleResponseDto.fromJson(response.data!);
  }

  Future<BarberScheduleAppointmentDto> updateAppointmentStatus({
    required String appointmentId,
    required String status,
  }) async {
    final response = await dio.patch<Map<String, dynamic>>(
      '/barber/appointments/$appointmentId/status',
      data: {'status': status},
    );
    return BarberScheduleAppointmentDto.fromJson(response.data!);
  }
}
