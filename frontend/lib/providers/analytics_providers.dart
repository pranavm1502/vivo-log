import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/analytics_repository.dart';
import '../models/analytics_models.dart';

final analyticsRepositoryProvider = Provider((ref) => AnalyticsRepository());

final tumorGrowthProvider = FutureProvider.family<List<CohortSeries>, int>(
  (ref, studyId) => ref.read(analyticsRepositoryProvider).getTumorGrowth(studyId),
);

final bodyWeightProvider = FutureProvider.family<List<CohortSeries>, int>(
  (ref, studyId) => ref.read(analyticsRepositoryProvider).getBodyWeight(studyId),
);

final studySummaryProvider = FutureProvider.family<StudySummary, int>(
  (ref, studyId) => ref.read(analyticsRepositoryProvider).getStudySummary(studyId),
);

final dashboardProvider = FutureProvider<List<DashboardStudy>>(
  (ref) => ref.read(analyticsRepositoryProvider).getDashboard(),
);
