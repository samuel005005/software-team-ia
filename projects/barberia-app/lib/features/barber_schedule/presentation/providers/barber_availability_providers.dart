import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../core/application/use_case.dart';
import '../../../../../core/providers/network_providers.dart';
import '../../data/datasources/barber_availability_remote_data_source.dart';
import '../../data/repositories/barber_availability_repository_impl.dart';
import '../../domain/repositories/barber_availability_repository.dart';
import '../../domain/usecases/barber_availability_use_cases.dart';

final barberAvailabilityRemoteDataSourceProvider =
    Provider<BarberAvailabilityRemoteDataSource>((ref) {
  return BarberAvailabilityRemoteDataSource(ref.watch(dioProvider));
});

final barberAvailabilityRepositoryProvider =
    Provider<BarberAvailabilityRepository>((ref) {
  return BarberAvailabilityRepositoryImpl(
    ref.watch(barberAvailabilityRemoteDataSourceProvider),
  );
});

final listBarberAvailabilityUseCaseProvider =
    Provider<ListBarberAvailabilityUseCase>((ref) {
  return ListBarberAvailabilityUseCase(
    ref.watch(barberAvailabilityRepositoryProvider),
  );
});

final updateBarberAvailabilityUseCaseProvider =
    Provider<UpdateBarberAvailabilityUseCase>((ref) {
  return UpdateBarberAvailabilityUseCase(
    ref.watch(barberAvailabilityRepositoryProvider),
  );
});

final barberAvailabilityProvider = FutureProvider.autoDispose((ref) async {
  final result =
      await ref.watch(listBarberAvailabilityUseCaseProvider).call(const NoParams());
  return result.when(
    success: (days) => mergeAvailabilityWithDefaults(days),
    error: (failure) => throw failure,
  );
});
