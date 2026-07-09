import '../../../../../core/network/remote_data_source.dart';
import '../../../../services/data/models/service_dtos.dart';
import '../models/admin_barber_dtos.dart';

class AdminBarbersRemoteDataSource extends RemoteDataSource {
  AdminBarbersRemoteDataSource(super.dio);

  Future<AdminBarberListResponseDto> listBarbers() async {
    final response = await dio.get<Map<String, dynamic>>('/admin/barbers');
    return AdminBarberListResponseDto.fromJson(response.data!);
  }

  Future<AdminBarberDto> createBarber(CreateAdminBarberRequestDto request) async {
    final response = await dio.post<Map<String, dynamic>>(
      '/admin/barbers',
      data: request.toJson(),
    );
    return AdminBarberDto.fromJson(response.data!);
  }

  Future<AdminBarberDto> updateBarber(
    String userId,
    UpdateAdminBarberRequestDto request,
  ) async {
    final response = await dio.patch<Map<String, dynamic>>(
      '/admin/barbers/$userId',
      data: request.toJson(),
    );
    return AdminBarberDto.fromJson(response.data!);
  }

  Future<ServiceListResponseDto> getBarberServices(String userId) async {
    final response = await dio.get<Map<String, dynamic>>(
      '/admin/barbers/$userId/services',
    );
    return ServiceListResponseDto.fromJson(response.data!);
  }

  Future<ServiceListResponseDto> setBarberServices(
    String userId,
    List<String> serviceIds,
  ) async {
    final response = await dio.put<Map<String, dynamic>>(
      '/admin/barbers/$userId/services',
      data: {'service_ids': serviceIds},
    );
    return ServiceListResponseDto.fromJson(response.data!);
  }
}
