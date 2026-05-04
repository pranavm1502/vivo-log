## ADDED Requirements

### Requirement: Tumor growth time-series endpoint
The system SHALL provide a GET endpoint at `/api/v1/analytics/studies/{study_id}/tumor-growth` that returns per-cohort tumor volume time-series data. Each data point SHALL include the day (days post-enrollment), mean tumor volume, standard error of mean, and sample count.

#### Scenario: Successful tumor growth retrieval
- **WHEN** a GET request is made to `/api/v1/analytics/studies/{study_id}/tumor-growth`
- **THEN** the response SHALL contain an array of cohort objects, each with `cohort_id`, `cohort_name`, and a `series` array of `{day, mean, sem, n}` objects sorted by day ascending

#### Scenario: Study with no measurements
- **WHEN** a GET request is made for a study that has enrollments but no measurements
- **THEN** the response SHALL return an empty `series` array for each cohort

#### Scenario: Study not found
- **WHEN** a GET request is made for a non-existent study_id
- **THEN** the response SHALL return 404

### Requirement: Body weight time-series endpoint
The system SHALL provide a GET endpoint at `/api/v1/analytics/studies/{study_id}/body-weight` that returns per-cohort body weight time-series data. Each data point SHALL include the day (days post-enrollment), mean body weight, standard error of mean, and sample count.

#### Scenario: Successful body weight retrieval
- **WHEN** a GET request is made to `/api/v1/analytics/studies/{study_id}/body-weight`
- **THEN** the response SHALL contain an array of cohort objects, each with `cohort_id`, `cohort_name`, and a `series` array of `{day, mean, sem, n}` objects sorted by day ascending

#### Scenario: Measurements without body weight data
- **WHEN** measurements exist but have null body_weight_g values
- **THEN** those measurements SHALL be excluded from the body weight aggregation

### Requirement: Study summary endpoint
The system SHALL provide a GET endpoint at `/api/v1/analytics/studies/{study_id}/summary` that returns summary statistics for the study including total enrollments, total measurements, days since study start, and per-cohort latest mean tumor volume.

#### Scenario: Successful summary retrieval
- **WHEN** a GET request is made to `/api/v1/analytics/studies/{study_id}/summary`
- **THEN** the response SHALL include `study_id`, `study_name`, `status`, `days_elapsed`, `total_enrollments`, `total_measurements`, and a `cohorts` array with `{cohort_id, cohort_name, enrollment_count, latest_mean_volume}`

### Requirement: Dashboard summary endpoint
The system SHALL provide a GET endpoint at `/api/v1/analytics/dashboard` that returns a summary of all active studies with key metrics for quick assessment.

#### Scenario: Successful dashboard retrieval
- **WHEN** a GET request is made to `/api/v1/analytics/dashboard`
- **THEN** the response SHALL include an array of study summaries for all studies with status "Active", each containing `study_id`, `study_name`, `days_elapsed`, `cohort_count`, `total_enrollments`, `total_measurements`, and `latest_mean_volume` (across all cohorts)

#### Scenario: No active studies
- **WHEN** no studies have status "Active"
- **THEN** the response SHALL return an empty array

### Requirement: Day calculation relative to enrollment
The system SHALL calculate measurement days as the number of days between the measurement's `recorded_at` timestamp and the corresponding enrollment's `enrolled_at` timestamp, rounded to the nearest integer.

#### Scenario: Same-day measurement
- **WHEN** a measurement is recorded on the same day as enrollment
- **THEN** the day value SHALL be 0

#### Scenario: Measurement 7 days after enrollment
- **WHEN** a measurement is recorded 7 days after the enrollment date
- **THEN** the day value SHALL be 7
