import '../../../../core/application/use_case.dart';
import '../../../../core/utils/result.dart';
import '../entities/availability_data.dart';
import '../repositories/booking_repository.dart';

class GetAvailabilityParams {
  const GetAvailabilityParams({
    required this.serviceId,
    required this.date,
    this.barberId,
  });

  final String serviceId;
  final DateTime date;
  final String? barberId;
}

class GetAvailabilityUseCase
    extends UseCase<AvailabilityData, GetAvailabilityParams> {
  GetAvailabilityUseCase(this._repository);

  final BookingRepository _repository;

  @override
  Future<Result<AvailabilityData>> call(GetAvailabilityParams params) {
    return _repository.getAvailability(
      serviceId: params.serviceId,
      date: params.date,
      barberId: params.barberId,
    );
  }
}
