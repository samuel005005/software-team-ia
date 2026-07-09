import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../core/providers/network_providers.dart';
import '../../data/datasources/barber_schedule_remote_data_source.dart';
import '../../data/repositories/barber_schedule_repository_impl.dart';
import '../../domain/entities/barber_schedule_appointment.dart';
import '../../domain/repositories/barber_schedule_repository.dart';
import '../../domain/usecases/get_barber_schedule_use_case.dart';
import '../../domain/usecases/update_barber_appointment_status_use_case.dart';

DateTime todayDateOnly() {
  final now = DateTime.now();
  return DateTime(now.year, now.month, now.day);
}

final barberScheduleRemoteDataSourceProvider =
    Provider<BarberScheduleRemoteDataSource>((ref) {
  return BarberScheduleRemoteDataSource(ref.watch(dioProvider));
});

final barberScheduleRepositoryProvider =
    Provider<BarberScheduleRepository>((ref) {
  return BarberScheduleRepositoryImpl(
    ref.watch(barberScheduleRemoteDataSourceProvider),
  );
});

final getBarberScheduleUseCaseProvider =
    Provider<GetBarberScheduleUseCase>((ref) {
  return GetBarberScheduleUseCase(
    ref.watch(barberScheduleRepositoryProvider),
  );
});

final updateBarberAppointmentStatusUseCaseProvider =
    Provider<UpdateBarberAppointmentStatusUseCase>((ref) {
  return UpdateBarberAppointmentStatusUseCase(
    ref.watch(barberScheduleRepositoryProvider),
  );
});

final selectedScheduleDateProvider =
    StateProvider<DateTime>((ref) => todayDateOnly());

final barberScheduleProvider = FutureProvider.autoDispose
    .family<List<BarberScheduleAppointment>, DateTime>((ref, date) async {
  final normalized = DateTime(date.year, date.month, date.day);
  final result = await ref
      .watch(getBarberScheduleUseCaseProvider)
      .call(GetBarberScheduleParams(date: normalized));
  return result.when(
    success: (appointments) => appointments,
    error: (failure) => throw failure,
  );
});
