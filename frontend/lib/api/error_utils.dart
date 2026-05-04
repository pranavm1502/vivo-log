import 'package:dio/dio.dart';

/// Extracts a user-friendly error message from a DioException.
/// Returns the server's `detail` field for 409 errors, or a generic message.
String extractErrorMessage(Object error) {
  if (error is DioException) {
    final response = error.response;
    if (response != null && response.data is Map) {
      final detail = response.data['detail'];
      if (detail is String) return detail;
    }
    if (response != null) {
      switch (response.statusCode) {
        case 409:
          return 'Operation conflicts with existing data';
        case 404:
          return 'Resource not found';
        case 422:
          return 'Invalid data submitted';
      }
    }
    return 'Network error: ${error.message}';
  }
  return error.toString();
}
