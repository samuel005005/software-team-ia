import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../core/application/use_case.dart';
import '../../../../../core/providers/network_providers.dart';
import '../../data/datasources/admin_barbers_remote_data_source.dart';
import '../../data/repositories/admin_barbers_repository_impl.dart';
import '../../domain/repositories/admin_barbers_repository.dart';
import '../../domain/usecases/admin_barbers_use_cases.dart';

final adminBarbersRemoteDataSourceProvider =
    Provider<AdminBarbersRemoteDataSource>((ref) {
  return AdminBarbersRemoteDataSource(ref.watch(dioProvider));
});

final adminBarbersRepositoryProvider = Provider<AdminBarbersRepository>((ref) {
  return AdminBarbersRepositoryImpl(ref.watch(adminBarbersRemoteDataSourceProvider));
});

final listAdminBarbersUseCaseProvider = Provider<ListAdminBarbersUseCase>((ref) {
  return ListAdminBarbersUseCase(ref.watch(adminBarbersRepositoryProvider));
});

final createAdminBarberUseCaseProvider = Provider<CreateAdminBarberUseCase>((ref) {
  return CreateAdminBarberUseCase(ref.watch(adminBarbersRepositoryProvider));
});

final updateAdminBarberUseCaseProvider = Provider<UpdateAdminBarberUseCase>((ref) {
  return UpdateAdminBarberUseCase(ref.watch(adminBarbersRepositoryProvider));
});

final getBarberServiceIdsUseCaseProvider = Provider<GetBarberServiceIdsUseCase>((ref) {
  return GetBarberServiceIdsUseCase(ref.watch(adminBarbersRepositoryProvider));
});

final setBarberServicesUseCaseProvider = Provider<SetBarberServicesUseCase>((ref) {
  return SetBarberServicesUseCase(ref.watch(adminBarbersRepositoryProvider));
});

final adminBarbersProvider = FutureProvider.autoDispose((ref) async {
  final result =
      await ref.watch(listAdminBarbersUseCaseProvider).call(const NoParams());
  return result.when(
    success: (barbers) => barbers,
    error: (failure) => throw failure,
  );
});
