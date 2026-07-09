import '../../../../../core/network/remote_data_source.dart';
import '../models/admin_client_dtos.dart';

class AdminClientsRemoteDataSource extends RemoteDataSource {
  AdminClientsRemoteDataSource(super.dio);

  Future<AdminClientListResponseDto> listClients() async {
    final response = await dio.get<Map<String, dynamic>>('/admin/users');
    return AdminClientListResponseDto.fromJson(response.data!);
  }

  Future<AdminClientDto> updateClient(
    String userId,
    UpdateAdminClientRequestDto request,
  ) async {
    final response = await dio.patch<Map<String, dynamic>>(
      '/admin/users/$userId',
      data: request.toJson(),
    );
    return AdminClientDto.fromJson(response.data!);
  }

  Future<AdminClientAppointmentListResponseDto> listClientAppointments(
    String userId,
  ) async {
    final response = await dio.get<Map<String, dynamic>>(
      '/admin/users/$userId/appointments',
    );
    return AdminClientAppointmentListResponseDto.fromJson(response.data!);
  }
}
