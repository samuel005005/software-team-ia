import 'package:intl/intl.dart';

import '../../../../../core/application/use_case.dart';
import '../../../../../core/utils/result.dart';
import '../entities/barber_schedule_appointment.dart';
import '../repositories/barber_schedule_repository.dart';

class GetBarberScheduleParams {
  const GetBarberScheduleParams({required this.date});

  final DateTime date;
}

class GetBarberScheduleUseCase
    extends UseCase<List<BarberScheduleAppointment>, GetBarberScheduleParams> {
  GetBarberScheduleUseCase(this._repository);

  final BarberScheduleRepository _repository;

  static final _dateFormat = DateFormat('yyyy-MM-dd');

  @override
  Future<Result<List<BarberScheduleAppointment>>> call(
    GetBarberScheduleParams params,
  ) {
    final normalized = DateTime(
      params.date.year,
      params.date.month,
      params.date.day,
    );
    return _repository.getScheduleForDate(date: normalized);
  }

  static String formatDateIso(DateTime date) {
    return _dateFormat.format(
      DateTime(date.year, date.month, date.day),
    );
  }
}
