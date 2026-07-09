import '../../../../../core/utils/result.dart';
import '../../domain/entities/availability_day.dart';
import '../../domain/repositories/barber_availability_repository.dart';
import '../datasources/barber_availability_remote_data_source.dart';
import '../models/barber_availability_dtos.dart';

class BarberAvailabilityRepositoryImpl implements BarberAvailabilityRepository {
  BarberAvailabilityRepositoryImpl(this._remote);

  final BarberAvailabilityRemoteDataSource _remote;

  @override
  Future<Result<List<AvailabilityDay>>> listAvailability() async {
    final result = await _remote.execute(_remote.listAvailability);
    return result.when(
      success: (dto) => Success(
        dto.items.map((item) => item.toEntity()).toList(),
      ),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<List<AvailabilityDay>>> updateAvailability({
    required List<AvailabilityDay> days,
  }) async {
    final result = await _remote.execute(
      () => _remote.updateAvailability(
        UpdateBarberAvailabilityRequestDto(
          items: days
              .map(
                (day) => AvailabilityDayDto(
                  weekday: day.weekday,
                  startTime: day.startTime,
                  endTime: day.endTime,
                  isActive: day.isActive,
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
