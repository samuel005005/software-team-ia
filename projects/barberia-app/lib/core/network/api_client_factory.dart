import 'package:dio/dio.dart';

import '../config/app_config.dart';
import '../constants/app_constants.dart';
import 'api_client.dart';
import 'contracts/auth_token_provider.dart';
import 'interceptors/auth_interceptor.dart';
import 'interceptors/error_mapping_interceptor.dart';
import 'interceptors/unauthorized_interceptor.dart';

/// Factory para construir [ApiClient] con interceptores estándar.
abstract final class ApiClientFactory {
  static ApiClient create({
    required AppConfig config,
    required AuthTokenProvider tokenProvider,
    required void Function() onSessionExpired,
    Future<bool> Function()? onRefreshToken,
  }) {
    final dio = Dio(
      BaseOptions(
        baseUrl: config.apiBaseUrl,
        connectTimeout: AppConstants.connectTimeout,
        receiveTimeout: AppConstants.receiveTimeout,
        headers: {
          'Content-Type': AppConstants.jsonContentType,
          'Accept': AppConstants.jsonContentType,
        },
      ),
    );

    dio.interceptors.addAll([
      AuthInterceptor(tokenProvider: tokenProvider),
      UnauthorizedInterceptor(
        onRefreshToken: onRefreshToken ?? () async => false,
        onSessionExpired: onSessionExpired,
      ),
      ErrorMappingInterceptor(),
      if (config.enableLogging)
        LogInterceptor(
          requestBody: true,
          responseBody: true,
          requestHeader: false,
          responseHeader: false,
        ),
    ]);

    return ApiClient(dio);
  }
}
