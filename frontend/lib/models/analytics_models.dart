class TimeSeriesPoint {
  final int day;
  final double mean;
  final double sem;
  final int n;

  TimeSeriesPoint({required this.day, required this.mean, required this.sem, required this.n});

  factory TimeSeriesPoint.fromJson(Map<String, dynamic> json) => TimeSeriesPoint(
        day: json['day'] as int,
        mean: (json['mean'] as num).toDouble(),
        sem: (json['sem'] as num).toDouble(),
        n: json['n'] as int,
      );
}

class CohortSeries {
  final int cohortId;
  final String cohortName;
  final List<TimeSeriesPoint> series;

  CohortSeries({required this.cohortId, required this.cohortName, required this.series});

  factory CohortSeries.fromJson(Map<String, dynamic> json) => CohortSeries(
        cohortId: json['cohort_id'] as int,
        cohortName: json['cohort_name'] as String,
        series: (json['series'] as List).map((e) => TimeSeriesPoint.fromJson(e)).toList(),
      );
}

class CohortSummary {
  final int cohortId;
  final String cohortName;
  final int enrollmentCount;
  final double? latestMeanVolume;

  CohortSummary({
    required this.cohortId,
    required this.cohortName,
    required this.enrollmentCount,
    this.latestMeanVolume,
  });

  factory CohortSummary.fromJson(Map<String, dynamic> json) => CohortSummary(
        cohortId: json['cohort_id'] as int,
        cohortName: json['cohort_name'] as String,
        enrollmentCount: json['enrollment_count'] as int,
        latestMeanVolume: (json['latest_mean_volume'] as num?)?.toDouble(),
      );
}

class StudySummary {
  final int studyId;
  final String studyName;
  final String status;
  final int daysElapsed;
  final int totalEnrollments;
  final int totalMeasurements;
  final List<CohortSummary> cohorts;

  StudySummary({
    required this.studyId,
    required this.studyName,
    required this.status,
    required this.daysElapsed,
    required this.totalEnrollments,
    required this.totalMeasurements,
    required this.cohorts,
  });

  factory StudySummary.fromJson(Map<String, dynamic> json) => StudySummary(
        studyId: json['study_id'] as int,
        studyName: json['study_name'] as String,
        status: json['status'] as String,
        daysElapsed: json['days_elapsed'] as int,
        totalEnrollments: json['total_enrollments'] as int,
        totalMeasurements: json['total_measurements'] as int,
        cohorts: (json['cohorts'] as List).map((e) => CohortSummary.fromJson(e)).toList(),
      );
}

class DashboardStudy {
  final int studyId;
  final String studyName;
  final int daysElapsed;
  final int cohortCount;
  final int totalEnrollments;
  final int totalMeasurements;
  final double? latestMeanVolume;

  DashboardStudy({
    required this.studyId,
    required this.studyName,
    required this.daysElapsed,
    required this.cohortCount,
    required this.totalEnrollments,
    required this.totalMeasurements,
    this.latestMeanVolume,
  });

  factory DashboardStudy.fromJson(Map<String, dynamic> json) => DashboardStudy(
        studyId: json['study_id'] as int,
        studyName: json['study_name'] as String,
        daysElapsed: json['days_elapsed'] as int,
        cohortCount: json['cohort_count'] as int,
        totalEnrollments: json['total_enrollments'] as int,
        totalMeasurements: json['total_measurements'] as int,
        latestMeanVolume: (json['latest_mean_volume'] as num?)?.toDouble(),
      );
}
