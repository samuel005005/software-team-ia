import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/application/use_case.dart';
import '../../../../core/providers/network_providers.dart';
import '../../data/datasources/appointments_remote_data_source.dart';
import '../../data/repositories/appointments_repository_impl.dart';
import '../../domain/repositories/appointments_repository.dart';
import '../../domain/usecases/cancel_appointment_use_case.dart';
import '../../domain/usecases/list_my_appointments_use_case.dart';

final appointmentsRemoteDataSourceProvider =
    Provider<AppointmentsRemoteDataSource>((ref) {
  return AppointmentsRemoteDataSource(ref.watch(dioProvider));
});

final appointmentsRepositoryProvider = Provider<AppointmentsRepository>((ref) {
  return AppointmentsRepositoryImpl(
    ref.watch(appointmentsRemoteDataSourceProvider),
  );
});

final listMyAppointmentsUseCaseProvider =
    Provider<ListMyAppointmentsUseCase>((ref) {
  return ListMyAppointmentsUseCase(ref.watch(appointmentsRepositoryProvider));
});

final cancelAppointmentUseCaseProvider =
    Provider<CancelAppointmentUseCase>((ref) {
  return CancelAppointmentUseCase(ref.watch(appointmentsRepositoryProvider));
});

final myAppointmentsProvider = FutureProvider.autoDispose((ref) async {
  final result =
      await ref.watch(listMyAppointmentsUseCaseProvider).call(const NoParams());
  return result.when(
    success: (appointments) => appointments,
    error: (failure) => throw failure,
  );
});
