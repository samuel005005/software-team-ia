import '../../../../core/network/remote_data_source.dart';
import '../models/booking_dtos.dart';

class BarbersRemoteDataSource extends RemoteDataSource {
  BarbersRemoteDataSource(super.dio);

  Future<BarberListResponseDto> listBarbers({String? serviceId}) async {
    final response = await dio.get<Map<String, dynamic>>(
      '/barbers',
      queryParameters: {
        if (serviceId != null) 'service_id': serviceId,
      },
    );
    return BarberListResponseDto.fromJson(response.data!);
  }
}
