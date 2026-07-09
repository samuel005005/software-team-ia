import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../core/application/use_case.dart';
import '../../../../../core/providers/network_providers.dart';
import '../../data/datasources/admin_clients_remote_data_source.dart';
import '../../data/repositories/admin_clients_repository_impl.dart';
import '../../domain/repositories/admin_clients_repository.dart';
import '../../domain/usecases/admin_clients_use_cases.dart';

final adminClientsRemoteDataSourceProvider =
    Provider<AdminClientsRemoteDataSource>((ref) {
  return AdminClientsRemoteDataSource(ref.watch(dioProvider));
});

final adminClientsRepositoryProvider = Provider<AdminClientsRepository>((ref) {
  return AdminClientsRepositoryImpl(ref.watch(adminClientsRemoteDataSourceProvider));
});

final listAdminClientsUseCaseProvider = Provider<ListAdminClientsUseCase>((ref) {
  return ListAdminClientsUseCase(ref.watch(adminClientsRepositoryProvider));
});

final updateAdminClientUseCaseProvider = Provider<UpdateAdminClientUseCase>((ref) {
  return UpdateAdminClientUseCase(ref.watch(adminClientsRepositoryProvider));
});

final listClientAppointmentsUseCaseProvider =
    Provider<ListClientAppointmentsUseCase>((ref) {
  return ListClientAppointmentsUseCase(ref.watch(adminClientsRepositoryProvider));
});

final adminClientsProvider = FutureProvider.autoDispose((ref) async {
  final result =
      await ref.watch(listAdminClientsUseCaseProvider).call(const NoParams());
  return result.when(
    success: (clients) => clients,
    error: (failure) => throw failure,
  );
});
