import '../../../../core/network/remote_data_source.dart';
import '../models/service_dtos.dart';

class ServicesRemoteDataSource extends RemoteDataSource {
  ServicesRemoteDataSource(super.dio);

  Future<ServiceListResponseDto> listActiveServices() async {
    final response = await dio.get<Map<String, dynamic>>('/services');
    return ServiceListResponseDto.fromJson(response.data!);
  }
}
