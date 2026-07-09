import '../../../../core/utils/result.dart';
import '../../domain/entities/service_item.dart';
import '../../domain/repositories/services_repository.dart';
import '../datasources/services_remote_data_source.dart';

class ServicesRepositoryImpl implements ServicesRepository {
  ServicesRepositoryImpl(this._remote);

  final ServicesRemoteDataSource _remote;

  @override
  Future<Result<List<ServiceItem>>> listActiveServices() async {
    final result = await _remote.execute(_remote.listActiveServices);
    return result.when(
      success: (dto) => Success(dto.items.map((item) => item.toEntity()).toList()),
      error: (failure) => Error(failure),
    );
  }
}
