import '../../../../../core/network/remote_data_source.dart';
import '../models/admin_service_dtos.dart';

class AdminServicesRemoteDataSource extends RemoteDataSource {
  AdminServicesRemoteDataSource(super.dio);

  Future<AdminServiceListResponseDto> listServices() async {
    final response = await dio.get<Map<String, dynamic>>('/admin/services');
    return AdminServiceListResponseDto.fromJson(response.data!);
  }

  Future<AdminServiceDto> createService(CreateAdminServiceRequestDto request) async {
    final response = await dio.post<Map<String, dynamic>>(
      '/admin/services',
      data: request.toJson(),
    );
    return AdminServiceDto.fromJson(response.data!);
  }

  Future<AdminServiceDto> updateService(
    String id,
    UpdateAdminServiceRequestDto request,
  ) async {
    final response = await dio.patch<Map<String, dynamic>>(
      '/admin/services/$id',
      data: request.toJson(),
    );
    return AdminServiceDto.fromJson(response.data!);
  }
}
