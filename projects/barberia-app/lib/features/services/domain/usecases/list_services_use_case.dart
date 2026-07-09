import '../../../../core/application/use_case.dart';
import '../../../../core/utils/result.dart';
import '../entities/service_item.dart';
import '../repositories/services_repository.dart';

class ListActiveServicesUseCase extends UseCase<List<ServiceItem>, NoParams> {
  ListActiveServicesUseCase(this._repository);

  final ServicesRepository _repository;

  @override
  Future<Result<List<ServiceItem>>> call(NoParams params) {
    return _repository.listActiveServices();
  }
}
