import '../../../../../core/utils/result.dart';
import '../entities/business_hours_day.dart';

abstract interface class AdminBusinessHoursRepository {
  Future<Result<List<BusinessHoursDay>>> listBusinessHours();

  Future<Result<List<BusinessHoursDay>>> updateBusinessHours({
    required List<BusinessHoursDay> days,
  });
}
