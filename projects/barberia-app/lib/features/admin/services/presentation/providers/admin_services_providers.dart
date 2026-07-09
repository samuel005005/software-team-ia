import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../core/application/use_case.dart';
import '../../../../../core/providers/network_providers.dart';
import '../../data/datasources/admin_services_remote_data_source.dart';
import '../../data/repositories/admin_services_repository_impl.dart';
import '../../domain/repositories/admin_services_repository.dart';
import '../../domain/usecases/admin_services_use_cases.dart';

final adminServicesRemoteDataSourceProvider =
    Provider<AdminServicesRemoteDataSource>((ref) {
  return AdminServicesRemoteDataSource(ref.watch(dioProvider));
});

final adminServicesRepositoryProvider = Provider<AdminServicesRepository>((ref) {
  return AdminServicesRepositoryImpl(ref.watch(adminServicesRemoteDataSourceProvider));
});

final listAdminServicesUseCaseProvider = Provider<ListAdminServicesUseCase>((ref) {
  return ListAdminServicesUseCase(ref.watch(adminServicesRepositoryProvider));
});

final createAdminServiceUseCaseProvider = Provider<CreateAdminServiceUseCase>((ref) {
  return CreateAdminServiceUseCase(ref.watch(adminServicesRepositoryProvider));
});

final updateAdminServiceUseCaseProvider = Provider<UpdateAdminServiceUseCase>((ref) {
  return UpdateAdminServiceUseCase(ref.watch(adminServicesRepositoryProvider));
});

final adminServicesProvider = FutureProvider.autoDispose((ref) async {
  final result =
      await ref.watch(listAdminServicesUseCaseProvider).call(const NoParams());
  return result.when(
    success: (services) => services,
    error: (failure) => throw failure,
  );
});
