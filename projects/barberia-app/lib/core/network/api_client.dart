import 'package:dio/dio.dart';

import '../config/app_config.dart';
import '../constants/app_constants.dart';

/// Cliente HTTP centralizado basado en Dio.
class ApiClient {
  ApiClient(this._dio);

  final Dio _dio;

  Dio get dio => _dio;

  factory ApiClient.create(AppConfig config) {
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

    if (config.enableLogging) {
      dio.interceptors.add(
        LogInterceptor(
          requestBody: true,
          responseBody: true,
          requestHeader: false,
          responseHeader: false,
        ),
      );
    }

    return ApiClient(dio);
  }
}
