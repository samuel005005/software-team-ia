import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/application/use_case.dart';
import '../../../../core/providers/network_providers.dart';
import '../../data/datasources/services_remote_data_source.dart';
import '../../data/repositories/services_repository_impl.dart';
import '../../domain/repositories/services_repository.dart';
import '../../domain/usecases/list_services_use_case.dart';

final servicesRemoteDataSourceProvider = Provider<ServicesRemoteDataSource>((ref) {
  return ServicesRemoteDataSource(ref.watch(dioProvider));
});

final servicesRepositoryProvider = Provider<ServicesRepository>((ref) {
  return ServicesRepositoryImpl(ref.watch(servicesRemoteDataSourceProvider));
});

final listActiveServicesUseCaseProvider = Provider<ListActiveServicesUseCase>((ref) {
  return ListActiveServicesUseCase(ref.watch(servicesRepositoryProvider));
});

final activeServicesProvider = FutureProvider.autoDispose((ref) async {
  final result =
      await ref.watch(listActiveServicesUseCaseProvider).call(const NoParams());
  return result.when(
    success: (services) => services,
    error: (failure) => throw failure,
  );
});
