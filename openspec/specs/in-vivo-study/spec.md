## ADDED Requirements

### Requirement: Create and manage studies
The system SHALL allow users to create studies with a name, description, start date, and optional end date. A study SHALL have a status of "Draft", "Active", or "Completed". Only "Active" studies SHALL accept new enrollments.

#### Scenario: Create a new study
- **WHEN** user creates a study named "Tumor Growth Efficacy Study" with start date "2026-03-01"
- **THEN** the system creates the study with status "Draft" and returns the study identifier

#### Scenario: Activate a study
- **WHEN** user changes study status from "Draft" to "Active"
- **THEN** the study accepts new cohort and enrollment operations

#### Scenario: Reject enrollment in a non-active study
- **WHEN** user attempts to enroll a mouse into a cohort of a study with status "Draft"
- **THEN** the system rejects the request with an error indicating the study must be "Active"

### Requirement: Define cohorts within a study
The system SHALL allow creating named cohorts within a study (e.g., "Vehicle Control", "Treatment 10mg/kg"). Each cohort belongs to exactly one study.

#### Scenario: Create a cohort
- **WHEN** user creates cohort "Vehicle Control" within study "Tumor Growth Efficacy Study"
- **THEN** the system creates the cohort linked to that study

#### Scenario: List cohorts for a study
- **WHEN** user requests all cohorts for study "Tumor Growth Efficacy Study"
- **THEN** the system returns all cohorts belonging to that study

### Requirement: Enroll mice into cohorts
The system SHALL allow enrolling a mouse into a cohort with a timestamp. A mouse SHALL NOT be enrolled if its status is "Deceased" or "Culled". A mouse MAY be enrolled in multiple cohorts across different studies.

#### Scenario: Successfully enroll an alive mouse
- **GIVEN** mouse "M-001" has status "Alive"
- **WHEN** user enrolls mouse "M-001" into cohort "Vehicle Control"
- **THEN** the system records the enrollment with the current timestamp

#### Scenario: Reject enrollment of a deceased mouse
- **GIVEN** mouse "M-002" has status "Deceased"
- **WHEN** user attempts to enroll mouse "M-002" into cohort "Vehicle Control"
- **THEN** the system rejects the enrollment with an error indicating deceased mice cannot be enrolled

#### Scenario: Reject enrollment of a culled mouse
- **GIVEN** mouse "M-003" has status "Culled"
- **WHEN** user attempts to enroll mouse "M-003" into cohort "Treatment 10mg/kg"
- **THEN** the system rejects the enrollment with an error indicating culled mice cannot be enrolled

#### Scenario: Remove a mouse from a cohort
- **WHEN** user removes mouse "M-001" from cohort "Vehicle Control" with reason "Reached humane endpoint"
- **THEN** the system records the removal timestamp and reason, and the mouse is no longer actively enrolled in that cohort

### Requirement: Record experimental measurements
The system SHALL allow recording timestamped measurements for an enrolled mouse including tumor length (mm), tumor width (mm), and body weight (g). All measurement values MUST be non-negative numbers.

#### Scenario: Record a complete measurement
- **WHEN** user records a measurement for enrolled mouse "M-001" with tumor length 12.5 mm, tumor width 8.3 mm, and body weight 22.1 g
- **THEN** the system stores the measurement with the provided values and the recording timestamp

#### Scenario: Record body weight only
- **WHEN** user records a measurement for enrolled mouse "M-001" with only body weight 21.8 g (no tumor dimensions)
- **THEN** the system stores the measurement with body weight and null tumor dimensions

#### Scenario: Reject negative measurement values
- **WHEN** user attempts to record a measurement with tumor length -5.0 mm
- **THEN** the system rejects the request with a validation error indicating measurements must be non-negative

### Requirement: Calculate tumor volume automatically
The system SHALL automatically calculate tumor volume using the formula Volume = Length × Width² / 2 whenever both tumor length and tumor width are provided in a measurement. The calculated volume SHALL be stored alongside the raw dimensions. If either dimension is missing, the tumor volume SHALL be null.

#### Scenario: Tumor volume calculated from dimensions
- **GIVEN** a measurement is being recorded with tumor length 12.5 mm and tumor width 8.3 mm
- **WHEN** the measurement is saved
- **THEN** the system calculates tumor volume as 12.5 × 8.3² / 2 = 430.5625 mm³ and stores it with the measurement

#### Scenario: Tumor volume is null when width is missing
- **GIVEN** a measurement is being recorded with tumor length 12.5 mm and no tumor width
- **WHEN** the measurement is saved
- **THEN** the tumor volume is stored as null

#### Scenario: Tumor volume is null when length is missing
- **GIVEN** a measurement is being recorded with tumor width 8.3 mm and no tumor length
- **WHEN** the measurement is saved
- **THEN** the tumor volume is stored as null

### Requirement: View measurement history for an enrollment
The system SHALL provide a chronological list of all measurements recorded for a given enrollment, ordered by recording timestamp.

#### Scenario: Retrieve measurement history
- **WHEN** user requests measurements for the enrollment of mouse "M-001" in cohort "Vehicle Control"
- **THEN** the system returns all measurements for that enrollment ordered by timestamp ascending

#### Scenario: No measurements recorded yet
- **WHEN** user requests measurements for a newly created enrollment with no recorded data
- **THEN** the system returns an empty list
