import '../../../../../core/utils/result.dart';
import '../entities/availability_day.dart';

abstract interface class BarberAvailabilityRepository {
  Future<Result<List<AvailabilityDay>>> listAvailability();

  Future<Result<List<AvailabilityDay>>> updateAvailability({
    required List<AvailabilityDay> days,
  });
}
