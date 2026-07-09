import '../../../../../core/application/use_case.dart';
import '../../../../../core/utils/result.dart';
import '../entities/business_hours_day.dart';
import '../repositories/admin_business_hours_repository.dart';

class ListAdminBusinessHoursUseCase
    extends UseCase<List<BusinessHoursDay>, NoParams> {
  ListAdminBusinessHoursUseCase(this._repository);

  final AdminBusinessHoursRepository _repository;

  @override
  Future<Result<List<BusinessHoursDay>>> call(NoParams params) {
    return _repository.listBusinessHours();
  }
}

class UpdateAdminBusinessHoursParams {
  const UpdateAdminBusinessHoursParams({required this.days});

  final List<BusinessHoursDay> days;
}

class UpdateAdminBusinessHoursUseCase
    extends UseCase<List<BusinessHoursDay>, UpdateAdminBusinessHoursParams> {
  UpdateAdminBusinessHoursUseCase(this._repository);

  final AdminBusinessHoursRepository _repository;

  @override
  Future<Result<List<BusinessHoursDay>>> call(
    UpdateAdminBusinessHoursParams params,
  ) {
    return _repository.updateBusinessHours(days: params.days);
  }
}

List<BusinessHoursDay> mergeBusinessHoursWithDefaults(
  List<BusinessHoursDay> configured,
) {
  final defaults = BusinessHoursDay.defaultWeek();
  if (configured.isEmpty) {
    return defaults;
  }

  final byWeekday = {for (final day in configured) day.weekday: day};
  return defaults.map((day) => byWeekday[day.weekday] ?? day).toList();
}
