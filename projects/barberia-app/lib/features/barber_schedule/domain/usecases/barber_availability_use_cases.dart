import '../../../../../core/application/use_case.dart';
import '../../../../../core/utils/result.dart';
import '../entities/availability_day.dart';
import '../repositories/barber_availability_repository.dart';

class ListBarberAvailabilityUseCase
    extends UseCase<List<AvailabilityDay>, NoParams> {
  ListBarberAvailabilityUseCase(this._repository);

  final BarberAvailabilityRepository _repository;

  @override
  Future<Result<List<AvailabilityDay>>> call(NoParams params) {
    return _repository.listAvailability();
  }
}

class UpdateBarberAvailabilityParams {
  const UpdateBarberAvailabilityParams({required this.days});

  final List<AvailabilityDay> days;
}

class UpdateBarberAvailabilityUseCase
    extends UseCase<List<AvailabilityDay>, UpdateBarberAvailabilityParams> {
  UpdateBarberAvailabilityUseCase(this._repository);

  final BarberAvailabilityRepository _repository;

  @override
  Future<Result<List<AvailabilityDay>>> call(
    UpdateBarberAvailabilityParams params,
  ) {
    return _repository.updateAvailability(days: params.days);
  }
}

List<AvailabilityDay> mergeAvailabilityWithDefaults(
  List<AvailabilityDay> configured,
) {
  final defaults = AvailabilityDay.defaultWeek();
  if (configured.isEmpty) {
    return defaults;
  }

  final byWeekday = {for (final day in configured) day.weekday: day};
  return defaults.map((day) => byWeekday[day.weekday] ?? day).toList();
}
