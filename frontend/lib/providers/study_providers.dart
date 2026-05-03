import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/study_repository.dart';
import '../models/study_models.dart';

final studyRepositoryProvider = Provider((ref) => StudyRepository());

final studiesProvider = FutureProvider<List<Study>>(
  (ref) => ref.read(studyRepositoryProvider).getStudies(),
);

final studyProvider = FutureProvider.family<Study, int>(
  (ref, id) => ref.read(studyRepositoryProvider).getStudy(id),
);

final cohortsProvider = FutureProvider.family<List<Cohort>, int>(
  (ref, studyId) => ref.read(studyRepositoryProvider).getCohorts(studyId),
);

final enrollmentsProvider =
    FutureProvider.family<List<Enrollment>, ({int studyId, int cohortId})>(
  (ref, params) => ref
      .read(studyRepositoryProvider)
      .getEnrollments(params.studyId, params.cohortId),
);

final measurementsProvider = FutureProvider.family<List<Measurement>,
    ({int studyId, int cohortId, int enrollmentId})>(
  (ref, params) => ref.read(studyRepositoryProvider).getMeasurements(
      params.studyId, params.cohortId, params.enrollmentId),
);
