import '../../../../../core/utils/result.dart';
import '../../domain/entities/business_hours_day.dart';
import '../../domain/repositories/admin_business_hours_repository.dart';
import '../datasources/admin_business_hours_remote_data_source.dart';
import '../models/admin_business_hours_dtos.dart';

class AdminBusinessHoursRepositoryImpl implements AdminBusinessHoursRepository {
  AdminBusinessHoursRepositoryImpl(this._remote);

  final AdminBusinessHoursRemoteDataSource _remote;

  @override
  Future<Result<List<BusinessHoursDay>>> listBusinessHours() async {
    final result = await _remote.execute(_remote.listBusinessHours);
    return result.when(
      success: (dto) => Success(
        dto.items.map((item) => item.toEntity()).toList(),
      ),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<List<BusinessHoursDay>>> updateBusinessHours({
    required List<BusinessHoursDay> days,
  }) async {
    final result = await _remote.execute(
      () => _remote.updateBusinessHours(
        UpdateBusinessHoursRequestDto(
          items: days
              .map(
                (day) => BusinessHoursDayDto(
                  weekday: day.weekday,
                  openTime: day.openTime,
                  closeTime: day.closeTime,
                  isClosed: day.isClosed,
                ),
              )
              .toList(),
        ),
      ),
    );

    return result.when(
      success: (dto) => Success(
        dto.items.map((item) => item.toEntity()).toList(),
      ),
      error: (failure) => Error(failure),
    );
  }
}
