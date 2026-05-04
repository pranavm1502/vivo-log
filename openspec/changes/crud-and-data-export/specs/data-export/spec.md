## ADDED Requirements

### Requirement: Export colony data as CSV
The system SHALL allow users to export colony data (mice, genotypes, cages) as a CSV file. The export SHALL include all records of the selected entity type with all fields. The CSV SHALL use UTF-8 encoding with a header row.

#### Scenario: Export all mice as CSV
- **WHEN** user requests export of mice in CSV format
- **THEN** the system returns a downloadable CSV file containing all mouse records with columns: id, ear_tag, sex, date_of_birth, status, genotype_name, cage_label, sire_ear_tag, dam_ear_tag

#### Scenario: Export all cages as CSV
- **WHEN** user requests export of cages in CSV format
- **THEN** the system returns a downloadable CSV file containing all cage records with columns: id, label, location, capacity, current_occupancy

#### Scenario: Export all genotypes as CSV
- **WHEN** user requests export of genotypes in CSV format
- **THEN** the system returns a downloadable CSV file containing all genotype records with columns: id, name, description, zygosity

### Requirement: Export study data as CSV
The system SHALL allow users to export study data (enrollments and measurements) as a CSV file. The export SHALL flatten nested relationships into a single table for analysis.

#### Scenario: Export measurements for a study as CSV
- **WHEN** user requests export of measurements for study "Tumor Growth Efficacy Study" in CSV format
- **THEN** the system returns a CSV file with columns: study_name, cohort_name, mouse_ear_tag, enrolled_at, recorded_at, tumor_length_mm, tumor_width_mm, tumor_volume_mm3, body_weight_g

#### Scenario: Export enrollments for a study as CSV
- **WHEN** user requests export of enrollments for study "Tumor Growth Efficacy Study" in CSV format
- **THEN** the system returns a CSV file with columns: study_name, cohort_name, mouse_ear_tag, enrolled_at, removed_at, removal_reason

### Requirement: Export data as XLSX
The system SHALL allow users to export data in XLSX format with the same content as CSV exports. Each export SHALL produce a single-sheet workbook with a header row and formatted columns.

#### Scenario: Export mice as XLSX
- **WHEN** user requests export of mice in XLSX format
- **THEN** the system returns a downloadable XLSX file with the same columns and data as the CSV export

#### Scenario: Export study measurements as XLSX
- **WHEN** user requests export of study measurements in XLSX format
- **THEN** the system returns a downloadable XLSX file with the same columns and data as the CSV export

### Requirement: Export triggers file download in Flutter app
The system SHALL provide an export button on list screens (mice, cages, studies) that triggers a file download. The user SHALL be able to choose between CSV and XLSX format. The downloaded file SHALL be shared via the system share sheet.

#### Scenario: User exports mice from the app
- **WHEN** user taps the export button on the mice list screen and selects CSV format
- **THEN** the app downloads the file from the server and opens the system share sheet

#### Scenario: User exports study data from the app
- **WHEN** user taps the export button on the study detail screen and selects XLSX format
- **THEN** the app downloads the measurements file and opens the system share sheet
