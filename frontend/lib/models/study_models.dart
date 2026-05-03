class Study {
  final int id;
  final String name;
  final String? description;
  final String startDate;
  final String? endDate;
  final String status;

  Study({
    required this.id,
    required this.name,
    this.description,
    required this.startDate,
    this.endDate,
    required this.status,
  });

  factory Study.fromJson(Map<String, dynamic> json) => Study(
        id: json['id'],
        name: json['name'],
        description: json['description'],
        startDate: json['start_date'],
        endDate: json['end_date'],
        status: json['status'],
      );
}

class Cohort {
  final int id;
  final int studyId;
  final String name;
  final String? description;

  Cohort({
    required this.id,
    required this.studyId,
    required this.name,
    this.description,
  });

  factory Cohort.fromJson(Map<String, dynamic> json) => Cohort(
        id: json['id'],
        studyId: json['study_id'],
        name: json['name'],
        description: json['description'],
      );
}

class Enrollment {
  final int id;
  final int cohortId;
  final int mouseId;
  final String enrolledAt;
  final String? removedAt;
  final String? removalReason;

  Enrollment({
    required this.id,
    required this.cohortId,
    required this.mouseId,
    required this.enrolledAt,
    this.removedAt,
    this.removalReason,
  });

  factory Enrollment.fromJson(Map<String, dynamic> json) => Enrollment(
        id: json['id'],
        cohortId: json['cohort_id'],
        mouseId: json['mouse_id'],
        enrolledAt: json['enrolled_at'],
        removedAt: json['removed_at'],
        removalReason: json['removal_reason'],
      );
}

class Measurement {
  final int id;
  final int enrollmentId;
  final String recordedAt;
  final double? tumorLengthMm;
  final double? tumorWidthMm;
  final double? tumorVolumeMm3;
  final double? bodyWeightG;
  final String? notes;

  Measurement({
    required this.id,
    required this.enrollmentId,
    required this.recordedAt,
    this.tumorLengthMm,
    this.tumorWidthMm,
    this.tumorVolumeMm3,
    this.bodyWeightG,
    this.notes,
  });

  factory Measurement.fromJson(Map<String, dynamic> json) => Measurement(
        id: json['id'],
        enrollmentId: json['enrollment_id'],
        recordedAt: json['recorded_at'],
        tumorLengthMm: (json['tumor_length_mm'] as num?)?.toDouble(),
        tumorWidthMm: (json['tumor_width_mm'] as num?)?.toDouble(),
        tumorVolumeMm3: (json['tumor_volume_mm3'] as num?)?.toDouble(),
        bodyWeightG: (json['body_weight_g'] as num?)?.toDouble(),
        notes: json['notes'],
      );
}
