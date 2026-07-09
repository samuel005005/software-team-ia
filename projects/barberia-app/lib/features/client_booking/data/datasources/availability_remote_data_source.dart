import '../../../../core/network/remote_data_source.dart';
import '../models/booking_dtos.dart';

String _formatDate(DateTime date) {
  final month = date.month.toString().padLeft(2, '0');
  final day = date.day.toString().padLeft(2, '0');
  return '${date.year}-$month-$day';
}

class AvailabilityRemoteDataSource extends RemoteDataSource {
  AvailabilityRemoteDataSource(super.dio);

  Future<AvailabilityResponseDto> getAvailability({
    required String serviceId,
    required DateTime date,
    String? barberId,
  }) async {
    final response = await dio.get<Map<String, dynamic>>(
      '/availability',
      queryParameters: {
        'service_id': serviceId,
        'date': _formatDate(date),
        if (barberId != null) 'barber_id': barberId,
      },
    );
    return AvailabilityResponseDto.fromJson(response.data!);
  }
}
