import '../../../../../core/utils/result.dart';
import '../entities/admin_service.dart';

abstract class AdminServicesRepository {
  Future<Result<List<AdminService>>> listServices();

  Future<Result<AdminService>> createService({
    required String name,
    required int durationMinutes,
    required String priceDop,
    String? description,
    bool isActive = true,
  });

  Future<Result<AdminService>> updateService({
    required String id,
    String? name,
    int? durationMinutes,
    String? priceDop,
    String? description,
    bool? isActive,
  });
}
