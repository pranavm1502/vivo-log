## ADDED Requirements

### Requirement: Create genotype from the app
The system SHALL provide a form in the Flutter app to create a new genotype with name, description, and zygosity fields. The form SHALL validate that name is not empty before submission.

#### Scenario: Create genotype via form
- **WHEN** user fills in genotype name "KRAS-G12D", description "Oncogenic KRAS mutation", zygosity "Heterozygous" and submits
- **THEN** the system creates the genotype and navigates back to the genotype list showing the new entry

#### Scenario: Reject empty genotype name
- **WHEN** user attempts to submit the genotype form with an empty name
- **THEN** the form shows a validation error "Name is required"

### Requirement: Edit genotype from the app
The system SHALL provide a form in the Flutter app to edit an existing genotype's name, description, and zygosity. The form SHALL be pre-filled with current values.

#### Scenario: Edit genotype via form
- **WHEN** user opens edit form for genotype "BRCA1-KO" and changes description to "Updated description" and submits
- **THEN** the system updates the genotype and reflects the change in the UI

### Requirement: Delete genotype from the app with confirmation
The system SHALL allow users to delete a genotype from the app. A confirmation dialog SHALL be shown before deletion. If the genotype is assigned to any mice, the system SHALL show an error message explaining the constraint.

#### Scenario: Delete genotype with confirmation
- **WHEN** user taps delete on genotype "Unused-Genotype" and confirms in the dialog
- **THEN** the system deletes the genotype and removes it from the list

#### Scenario: Reject delete of genotype in use
- **WHEN** user taps delete on genotype "BRCA1-KO" which is assigned to mice and confirms
- **THEN** the system shows an error "Cannot delete genotype because it is assigned to one or more mice"

### Requirement: Create cage from the app
The system SHALL provide a form in the Flutter app to create a new cage with label, location, and capacity fields. Capacity SHALL be a positive integer.

#### Scenario: Create cage via form
- **WHEN** user fills in cage label "R3-A01", location "Room 3", capacity 5 and submits
- **THEN** the system creates the cage and navigates back to the cage list

#### Scenario: Reject invalid cage capacity
- **WHEN** user attempts to submit the cage form with capacity 0
- **THEN** the form shows a validation error "Capacity must be at least 1"

### Requirement: Edit cage from the app
The system SHALL provide a form in the Flutter app to edit an existing cage's label, location, and capacity. The form SHALL be pre-filled with current values.

#### Scenario: Edit cage via form
- **WHEN** user opens edit form for cage "R1-A01" and changes capacity to 6 and submits
- **THEN** the system updates the cage and reflects the new capacity in the UI

### Requirement: Delete cage from the app with confirmation
The system SHALL allow users to delete a cage from the app. If mice are assigned to the cage, the system SHALL show an error message explaining the constraint.

#### Scenario: Delete empty cage
- **WHEN** user taps delete on an empty cage and confirms
- **THEN** the system deletes the cage and removes it from the list

#### Scenario: Reject delete of occupied cage
- **WHEN** user taps delete on a cage that has mice assigned and confirms
- **THEN** the system shows an error "Cannot delete cage because it still contains mice"

### Requirement: Create mouse from the app
The system SHALL provide a form in the Flutter app to create a new mouse with ear tag, sex, date of birth, genotype selection, and optional cage assignment. The form SHALL validate that ear tag is unique and not empty.

#### Scenario: Create mouse via form
- **WHEN** user fills in ear tag "M-050", sex "Female", date of birth "2026-04-01", selects genotype "BRCA1-KO", selects cage "R1-A01" and submits
- **THEN** the system creates the mouse with status "Alive" and shows it in the mouse list

#### Scenario: Reject duplicate ear tag
- **WHEN** user attempts to create a mouse with ear tag "M-001" that already exists
- **THEN** the system shows an error "A mouse with this ear tag already exists"

### Requirement: Edit mouse from the app
The system SHALL provide a form in the Flutter app to edit an existing mouse's ear tag, sex, date of birth, genotype, cage assignment, and status. The form SHALL be pre-filled with current values.

#### Scenario: Edit mouse status via form
- **WHEN** user opens edit form for mouse "M-001" and changes status to "Culled" and submits
- **THEN** the system updates the mouse status and reflects it in the UI

#### Scenario: Edit mouse cage assignment
- **WHEN** user opens edit form for mouse "M-001" and changes cage to "R2-A01" and submits
- **THEN** the system updates the cage assignment if the target cage has capacity

### Requirement: Delete mouse from the app with confirmation
The system SHALL allow users to delete a mouse from the app. If the mouse is referenced as a sire or dam, or is enrolled in a study, the system SHALL show an error explaining the constraint.

#### Scenario: Delete unreferenced mouse
- **WHEN** user taps delete on mouse "M-050" which has no lineage references or enrollments, and confirms
- **THEN** the system deletes the mouse and removes it from the list

#### Scenario: Reject delete of mouse with lineage references
- **WHEN** user taps delete on mouse "M-001" which is a sire of other mice, and confirms
- **THEN** the system shows an error "Cannot delete mouse because it is referenced as a parent by other mice"

### Requirement: Backend returns 409 on constraint violations
The system SHALL return HTTP 409 Conflict with a JSON body containing a `detail` field when a delete operation fails due to foreign key constraints.

#### Scenario: Delete genotype returns 409
- **WHEN** a DELETE request is made to `/api/v1/colony/genotypes/{id}` for a genotype assigned to mice
- **THEN** the server returns 409 with body `{"detail": "Cannot delete genotype because it is assigned to one or more mice"}`

#### Scenario: Delete mouse returns 409
- **WHEN** a DELETE request is made to `/api/v1/colony/mice/{id}` for a mouse referenced as sire
- **THEN** the server returns 409 with body `{"detail": "Cannot delete mouse because it is referenced as a parent by other mice"}`

#### Scenario: Delete cage returns 409
- **WHEN** a DELETE request is made to `/api/v1/colony/cages/{id}` for a cage with mice assigned
- **THEN** the server returns 409 with body `{"detail": "Cannot delete cage because it still contains mice"}`
