import '../../../../../core/network/remote_data_source.dart';
import '../models/admin_business_hours_dtos.dart';

class AdminBusinessHoursRemoteDataSource extends RemoteDataSource {
  AdminBusinessHoursRemoteDataSource(super.dio);

  Future<BusinessHoursListResponseDto> listBusinessHours() async {
    final response = await dio.get<Map<String, dynamic>>('/admin/business-hours');
    return BusinessHoursListResponseDto.fromJson(response.data!);
  }

  Future<BusinessHoursListResponseDto> updateBusinessHours(
    UpdateBusinessHoursRequestDto request,
  ) async {
    final response = await dio.patch<Map<String, dynamic>>(
      '/admin/business-hours',
      data: request.toJson(),
    );
    return BusinessHoursListResponseDto.fromJson(response.data!);
  }
}
