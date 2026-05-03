import 'package:dio/dio.dart';
import '../api/api_client.dart';
import '../models/study_models.dart';

class StudyRepository {
  final Dio _dio = ApiClient().dio;

  // ── Studies ──
  Future<List<Study>> getStudies() async {
    final r = await _dio.get('/studies');
    return (r.data as List).map((e) => Study.fromJson(e)).toList();
  }

  Future<Study> getStudy(int id) async {
    final r = await _dio.get('/studies/$id');
    return Study.fromJson(r.data);
  }

  Future<Study> createStudy(Map<String, dynamic> data) async {
    final r = await _dio.post('/studies', data: data);
    return Study.fromJson(r.data);
  }

  Future<Study> updateStudy(int id, Map<String, dynamic> data) async {
    final r = await _dio.patch('/studies/$id', data: data);
    return Study.fromJson(r.data);
  }

  // ── Cohorts ──
  Future<List<Cohort>> getCohorts(int studyId) async {
    final r = await _dio.get('/studies/$studyId/cohorts');
    return (r.data as List).map((e) => Cohort.fromJson(e)).toList();
  }

  Future<Cohort> createCohort(int studyId, Map<String, dynamic> data) async {
    final r = await _dio.post('/studies/$studyId/cohorts', data: data);
    return Cohort.fromJson(r.data);
  }

  // ── Enrollments ──
  Future<List<Enrollment>> getEnrollments(int studyId, int cohortId) async {
    final r = await _dio.get('/studies/$studyId/cohorts/$cohortId/enrollments');
    return (r.data as List).map((e) => Enrollment.fromJson(e)).toList();
  }

  Future<Enrollment> enrollMouse(int studyId, int cohortId, int mouseId) async {
    final r = await _dio.post(
      '/studies/$studyId/cohorts/$cohortId/enrollments',
      data: {'mouse_id': mouseId},
    );
    return Enrollment.fromJson(r.data);
  }

  Future<Enrollment> removeEnrollment(
      int studyId, int cohortId, int enrollmentId, String? reason) async {
    final r = await _dio.post(
      '/studies/$studyId/cohorts/$cohortId/enrollments/$enrollmentId/remove',
      data: {'removal_reason': reason},
    );
    return Enrollment.fromJson(r.data);
  }

  // ── Measurements ──
  Future<List<Measurement>> getMeasurements(
      int studyId, int cohortId, int enrollmentId) async {
    final r = await _dio.get(
      '/studies/$studyId/cohorts/$cohortId/enrollments/$enrollmentId/measurements',
    );
    return (r.data as List).map((e) => Measurement.fromJson(e)).toList();
  }

  Future<Measurement> createMeasurement(
      int studyId, int cohortId, int enrollmentId, Map<String, dynamic> data) async {
    final r = await _dio.post(
      '/studies/$studyId/cohorts/$cohortId/enrollments/$enrollmentId/measurements',
      data: data,
    );
    return Measurement.fromJson(r.data);
  }
}
