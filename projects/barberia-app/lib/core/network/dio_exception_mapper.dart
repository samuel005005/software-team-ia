import 'package:dio/dio.dart';

import '../error/app_exception.dart';

/// Adaptador entre [DioException] y excepciones internas de la app.
abstract final class DioExceptionMapper {
  static AppException map(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
      case DioExceptionType.connectionError:
      case DioExceptionType.transformTimeout:
        return const NetworkException(
          'No fue posible conectar con el servidor.',
        );
      case DioExceptionType.badResponse:
        return _mapBadResponse(error);
      case DioExceptionType.cancel:
        return const NetworkException('Solicitud cancelada.');
      case DioExceptionType.badCertificate:
      case DioExceptionType.unknown:
        return _mapUnknown(error);
    }
  }

  static AppException _mapBadResponse(DioException error) {
    final statusCode = error.response?.statusCode;
    final message = _extractMessage(error.response?.data) ??
        'Error del servidor (${statusCode ?? 'sin código'}).';

    if (statusCode == 401 || statusCode == 403) {
      return UnauthorizedException(message);
    }

    if (statusCode != null && statusCode >= 400 && statusCode < 500) {
      return ValidationException(message);
    }

    return ServerException(message, statusCode: statusCode);
  }

  static AppException _mapUnknown(DioException error) {
    final message = error.message;
    if (message != null && message.isNotEmpty) {
      return NetworkException(message);
    }
    return const NetworkException('Error de red desconocido.');
  }

  static String? _extractMessage(Object? data) {
    if (data is Map<String, dynamic>) {
      final detail = data['detail'];
      if (detail is String && detail.isNotEmpty) return detail;
      final message = data['message'];
      if (message is String && message.isNotEmpty) return message;
    }
    return null;
  }
}
