## ADDED Requirements

### Requirement: Create study from the app
The system SHALL provide a form in the Flutter app to create a new study with name, description, and start date. The form SHALL validate that name is not empty.

#### Scenario: Create study via form
- **WHEN** user fills in study name "PD-L1 Blockade Study", description "Evaluating anti-PD-L1 efficacy", start date "2026-05-01" and submits
- **THEN** the system creates the study with status "Draft" and shows it in the study list

#### Scenario: Reject empty study name
- **WHEN** user attempts to submit the study form with an empty name
- **THEN** the form shows a validation error "Name is required"

### Requirement: Edit study from the app
The system SHALL provide a form in the Flutter app to edit an existing study's name, description, start date, end date, and status. The form SHALL be pre-filled with current values.

#### Scenario: Edit study to activate it
- **WHEN** user opens edit form for a "Draft" study and changes status to "Active" and submits
- **THEN** the system updates the study status and the study now accepts enrollments

#### Scenario: Edit study end date
- **WHEN** user opens edit form for an active study and sets end date to "2026-08-01" and submits
- **THEN** the system updates the end date

### Requirement: Delete study from the app with confirmation
The system SHALL allow users to delete a study from the app. If the study has cohorts with enrollments, the system SHALL show an error explaining the constraint.

#### Scenario: Delete draft study with no cohorts
- **WHEN** user taps delete on a "Draft" study with no cohorts and confirms
- **THEN** the system deletes the study and removes it from the list

#### Scenario: Reject delete of study with enrollments
- **WHEN** user taps delete on a study that has cohorts with active enrollments and confirms
- **THEN** the system shows an error "Cannot delete study because it has active enrollments"

### Requirement: Create cohort from the app
The system SHALL provide a form in the Flutter app to create a new cohort within a study. The form SHALL require a cohort name.

#### Scenario: Create cohort via form
- **WHEN** user navigates to an active study and taps "Add Cohort", fills in name "High Dose 20mg/kg" and submits
- **THEN** the system creates the cohort and shows it in the study's cohort list

### Requirement: Edit cohort from the app
The system SHALL provide a form in the Flutter app to edit an existing cohort's name. The form SHALL be pre-filled with the current name.

#### Scenario: Edit cohort name
- **WHEN** user opens edit form for cohort "Vehicle Control" and changes name to "Saline Control" and submits
- **THEN** the system updates the cohort name

### Requirement: Delete cohort from the app with confirmation
The system SHALL allow users to delete a cohort. If the cohort has enrollments, the system SHALL show an error.

#### Scenario: Delete empty cohort
- **WHEN** user taps delete on a cohort with no enrollments and confirms
- **THEN** the system deletes the cohort and removes it from the study detail view

#### Scenario: Reject delete of cohort with enrollments
- **WHEN** user taps delete on a cohort with active enrollments and confirms
- **THEN** the system shows an error "Cannot delete cohort because it has enrollments"

### Requirement: Enroll mouse from the app
The system SHALL provide a UI to enroll a mouse into a cohort directly from the cohort detail screen. The UI SHALL show only eligible mice (status "Alive") and exclude already-enrolled mice.

#### Scenario: Enroll mouse via UI
- **WHEN** user taps "Enroll Mouse" on a cohort, selects mouse "M-005" from the eligible list, and confirms
- **THEN** the system creates the enrollment and shows the mouse in the cohort's enrollment list

### Requirement: Remove enrollment from the app
The system SHALL provide a UI to remove a mouse from a cohort with an optional reason. The removal SHALL record the timestamp and reason.

#### Scenario: Remove enrollment via UI
- **WHEN** user taps "Remove" on an enrolled mouse and enters reason "Reached humane endpoint" and confirms
- **THEN** the system records the removal with timestamp and reason, and marks the enrollment as removed

### Requirement: Add measurement from the app
The system SHALL provide a form to record a measurement for an enrolled mouse with fields for tumor length, tumor width, and body weight. The tumor volume SHALL be previewed in real-time.

#### Scenario: Record measurement via form
- **WHEN** user opens measurement form for enrollment of mouse "M-001", enters tumor length 15.2, tumor width 9.1, body weight 23.4 and submits
- **THEN** the system records the measurement with calculated tumor volume and shows it in the measurement history

### Requirement: Delete measurement from the app
The system SHALL allow users to delete a measurement with confirmation. This is for correcting data entry errors.

#### Scenario: Delete measurement with confirmation
- **WHEN** user taps delete on a measurement record and confirms
- **THEN** the system deletes the measurement and removes it from the history list

### Requirement: Backend supports cohort update
The system SHALL provide a PATCH endpoint to update a cohort's name.

#### Scenario: Update cohort name via API
- **WHEN** a PATCH request is made to `/api/v1/studies/{study_id}/cohorts/{cohort_id}` with body `{"name": "New Name"}`
- **THEN** the server updates the cohort name and returns the updated cohort

### Requirement: Backend supports measurement deletion
The system SHALL provide a DELETE endpoint to remove a measurement record.

#### Scenario: Delete measurement via API
- **WHEN** a DELETE request is made to `/api/v1/studies/{study_id}/cohorts/{cohort_id}/enrollments/{enrollment_id}/measurements/{measurement_id}`
- **THEN** the server deletes the measurement and returns 204 No Content

### Requirement: Backend returns 409 on study-related constraint violations
The system SHALL return HTTP 409 Conflict when a delete operation on a study, cohort, or enrollment fails due to dependencies.

#### Scenario: Delete study with cohorts returns 409
- **WHEN** a DELETE request is made to `/api/v1/studies/{id}` for a study with cohorts that have enrollments
- **THEN** the server returns 409 with body `{"detail": "Cannot delete study because it has active enrollments"}`

#### Scenario: Delete cohort with enrollments returns 409
- **WHEN** a DELETE request is made to `/api/v1/studies/{study_id}/cohorts/{cohort_id}` for a cohort with enrollments
- **THEN** the server returns 409 with body `{"detail": "Cannot delete cohort because it has enrollments"}`
