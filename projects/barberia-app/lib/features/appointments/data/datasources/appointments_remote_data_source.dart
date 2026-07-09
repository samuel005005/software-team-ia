import '../../../../core/network/remote_data_source.dart';
import '../models/appointment_dtos.dart';

class AppointmentsRemoteDataSource extends RemoteDataSource {
  AppointmentsRemoteDataSource(super.dio);

  Future<AppointmentListResponseDto> listMyAppointments() async {
    final response = await dio.get<Map<String, dynamic>>('/appointments');
    return AppointmentListResponseDto.fromJson(response.data!);
  }

  Future<AppointmentSummaryDto> cancelAppointment(String appointmentId) async {
    final response = await dio.patch<Map<String, dynamic>>(
      '/appointments/$appointmentId/cancel',
    );
    return AppointmentSummaryDto.fromJson(response.data!);
  }
}
