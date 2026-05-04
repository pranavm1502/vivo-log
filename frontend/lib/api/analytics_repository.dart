import 'package:dio/dio.dart';
import '../api/api_client.dart';
import '../models/analytics_models.dart';

class AnalyticsRepository {
  final Dio _dio = ApiClient().dio;

  Future<List<CohortSeries>> getTumorGrowth(int studyId) async {
    final r = await _dio.get('/analytics/studies/$studyId/tumor-growth');
    return (r.data as List).map((e) => CohortSeries.fromJson(e)).toList();
  }

  Future<List<CohortSeries>> getBodyWeight(int studyId) async {
    final r = await _dio.get('/analytics/studies/$studyId/body-weight');
    return (r.data as List).map((e) => CohortSeries.fromJson(e)).toList();
  }

  Future<StudySummary> getStudySummary(int studyId) async {
    final r = await _dio.get('/analytics/studies/$studyId/summary');
    return StudySummary.fromJson(r.data);
  }

  Future<List<DashboardStudy>> getDashboard() async {
    final r = await _dio.get('/analytics/dashboard');
    return (r.data as List).map((e) => DashboardStudy.fromJson(e)).toList();
  }
}
