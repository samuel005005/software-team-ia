import '../../../../../core/network/remote_data_source.dart';
import '../models/barber_availability_dtos.dart';

class BarberAvailabilityRemoteDataSource extends RemoteDataSource {
  BarberAvailabilityRemoteDataSource(super.dio);

  Future<BarberAvailabilityListResponseDto> listAvailability() async {
    final response =
        await dio.get<Map<String, dynamic>>('/barber/availability');
    return BarberAvailabilityListResponseDto.fromJson(response.data!);
  }

  Future<BarberAvailabilityListResponseDto> updateAvailability(
    UpdateBarberAvailabilityRequestDto request,
  ) async {
    final response = await dio.patch<Map<String, dynamic>>(
      '/barber/availability',
      data: request.toJson(),
    );
    return BarberAvailabilityListResponseDto.fromJson(response.data!);
  }
}
