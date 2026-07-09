import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/application/use_case.dart';
import '../../../../core/providers/network_providers.dart';
import '../../data/datasources/profile_remote_data_source.dart';
import '../../data/repositories/profile_repository_impl.dart';
import '../../domain/repositories/profile_repository.dart';
import '../../domain/usecases/profile_use_cases.dart';

final profileRemoteDataSourceProvider = Provider<ProfileRemoteDataSource>((ref) {
  return ProfileRemoteDataSource(ref.watch(dioProvider));
});

final profileRepositoryProvider = Provider<ProfileRepository>((ref) {
  return ProfileRepositoryImpl(ref.watch(profileRemoteDataSourceProvider));
});

final getMyProfileUseCaseProvider = Provider<GetMyProfileUseCase>((ref) {
  return GetMyProfileUseCase(ref.watch(profileRepositoryProvider));
});

final updateMyProfileUseCaseProvider = Provider<UpdateMyProfileUseCase>((ref) {
  return UpdateMyProfileUseCase(ref.watch(profileRepositoryProvider));
});

final myProfileProvider = FutureProvider.autoDispose((ref) async {
  final result = await ref.watch(getMyProfileUseCaseProvider).call(const NoParams());
  return result.when(
    success: (profile) => profile,
    error: (failure) => throw failure,
  );
});
