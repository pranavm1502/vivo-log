import 'dart:typed_data';
import 'package:dio/dio.dart';
import '../api/api_client.dart';

class ExportRepository {
  final Dio _dio = ApiClient().dio;

  Future<Uint8List> exportMice({String format = 'csv'}) async {
    final r = await _dio.get(
      '/export/mice',
      queryParameters: {'format': format},
      options: Options(responseType: ResponseType.bytes),
    );
    return Uint8List.fromList(r.data);
  }

  Future<Uint8List> exportCages({String format = 'csv'}) async {
    final r = await _dio.get(
      '/export/cages',
      queryParameters: {'format': format},
      options: Options(responseType: ResponseType.bytes),
    );
    return Uint8List.fromList(r.data);
  }

  Future<Uint8List> exportGenotypes({String format = 'csv'}) async {
    final r = await _dio.get(
      '/export/genotypes',
      queryParameters: {'format': format},
      options: Options(responseType: ResponseType.bytes),
    );
    return Uint8List.fromList(r.data);
  }

  Future<Uint8List> exportStudyMeasurements(int studyId, {String format = 'csv'}) async {
    final r = await _dio.get(
      '/export/studies/$studyId/measurements',
      queryParameters: {'format': format},
      options: Options(responseType: ResponseType.bytes),
    );
    return Uint8List.fromList(r.data);
  }

  Future<Uint8List> exportStudyEnrollments(int studyId, {String format = 'csv'}) async {
    final r = await _dio.get(
      '/export/studies/$studyId/enrollments',
      queryParameters: {'format': format},
      options: Options(responseType: ResponseType.bytes),
    );
    return Uint8List.fromList(r.data);
  }
}
