import '../../../../core/utils/result.dart';
import '../entities/service_item.dart';

abstract class ServicesRepository {
  Future<Result<List<ServiceItem>>> listActiveServices();
}
