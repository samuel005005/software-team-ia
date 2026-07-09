import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../core/application/use_case.dart';
import '../../../../../core/providers/network_providers.dart';
import '../../data/datasources/admin_business_hours_remote_data_source.dart';
import '../../data/repositories/admin_business_hours_repository_impl.dart';
import '../../domain/repositories/admin_business_hours_repository.dart';
import '../../domain/usecases/admin_business_hours_use_cases.dart';

final adminBusinessHoursRemoteDataSourceProvider =
    Provider<AdminBusinessHoursRemoteDataSource>((ref) {
  return AdminBusinessHoursRemoteDataSource(ref.watch(dioProvider));
});

final adminBusinessHoursRepositoryProvider =
    Provider<AdminBusinessHoursRepository>((ref) {
  return AdminBusinessHoursRepositoryImpl(
    ref.watch(adminBusinessHoursRemoteDataSourceProvider),
  );
});

final listAdminBusinessHoursUseCaseProvider =
    Provider<ListAdminBusinessHoursUseCase>((ref) {
  return ListAdminBusinessHoursUseCase(
    ref.watch(adminBusinessHoursRepositoryProvider),
  );
});

final updateAdminBusinessHoursUseCaseProvider =
    Provider<UpdateAdminBusinessHoursUseCase>((ref) {
  return UpdateAdminBusinessHoursUseCase(
    ref.watch(adminBusinessHoursRepositoryProvider),
  );
});

final adminBusinessHoursProvider = FutureProvider.autoDispose((ref) async {
  final result =
      await ref.watch(listAdminBusinessHoursUseCaseProvider).call(const NoParams());
  return result.when(
    success: (days) => mergeBusinessHoursWithDefaults(days),
    error: (failure) => throw failure,
  );
});
