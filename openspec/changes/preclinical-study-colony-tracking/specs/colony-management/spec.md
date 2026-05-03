## ADDED Requirements

### Requirement: Create and manage mouse records
The system SHALL allow users to create mouse records with an ear tag, sex, date of birth, and initial status of "Alive". The system SHALL allow updating mouse status to "Alive", "Deceased", or "Culled". Each mouse record SHALL be uniquely identified.

#### Scenario: Create a new mouse record
- **WHEN** user submits a new mouse with ear tag "M-001", sex "Female", and date of birth "2026-01-15"
- **THEN** the system creates a mouse record with status "Alive" and returns the assigned unique identifier

#### Scenario: Update mouse status to Deceased
- **WHEN** user updates mouse "M-001" status to "Deceased"
- **THEN** the system records the status change and the mouse status is "Deceased"

#### Scenario: Reject invalid mouse status
- **WHEN** user attempts to set mouse status to "Unknown"
- **THEN** the system rejects the request with a validation error listing the allowed statuses

### Requirement: Track mouse lineage
The system SHALL allow assigning a sire (father) and dam (mother) to a mouse record. The sire MUST be a male mouse and the dam MUST be a female mouse. A mouse SHALL NOT be its own ancestor.

#### Scenario: Assign sire and dam to a mouse
- **WHEN** user assigns sire "M-010" (male) and dam "M-020" (female) to mouse "M-001"
- **THEN** the system records the lineage and "M-001" shows "M-010" as sire and "M-020" as dam

#### Scenario: Reject sire with incorrect sex
- **WHEN** user attempts to assign a female mouse as the sire of "M-001"
- **THEN** the system rejects the request with an error indicating the sire must be male

#### Scenario: Reject dam with incorrect sex
- **WHEN** user attempts to assign a male mouse as the dam of "M-001"
- **THEN** the system rejects the request with an error indicating the dam must be female

### Requirement: Manage genotype records
The system SHALL allow creating genotype records with a name, description, and zygosity. The system SHALL allow assigning a genotype to a mouse.

#### Scenario: Create a genotype and assign to mouse
- **WHEN** user creates genotype "BRCA1-KO" with zygosity "Homozygous" and assigns it to mouse "M-001"
- **THEN** mouse "M-001" shows genotype "BRCA1-KO" with zygosity "Homozygous"

#### Scenario: List mice by genotype
- **WHEN** user queries all mice with genotype "BRCA1-KO"
- **THEN** the system returns all mice assigned that genotype

### Requirement: Manage cage assignments
The system SHALL allow creating cages with a label, location, and capacity. The system SHALL allow assigning a mouse to a cage. The system SHALL NOT allow assigning more mice to a cage than its capacity.

#### Scenario: Assign mouse to a cage
- **WHEN** user assigns mouse "M-001" to cage "C-101" which has capacity 5 and currently holds 3 mice
- **THEN** the system records the assignment and cage "C-101" now holds 4 mice

#### Scenario: Reject assignment when cage is full
- **WHEN** user attempts to assign mouse "M-050" to cage "C-101" which is already at capacity (5/5)
- **THEN** the system rejects the request with an error indicating the cage is at capacity

#### Scenario: Transfer mouse between cages
- **WHEN** user reassigns mouse "M-001" from cage "C-101" to cage "C-202"
- **THEN** the mouse is removed from "C-101" and added to "C-202", and both cage counts are updated

### Requirement: View mouse pedigree
The system SHALL provide a pedigree view showing ancestors of a given mouse up to a configurable depth (default 3 generations).

#### Scenario: View three-generation pedigree
- **WHEN** user requests the pedigree for mouse "M-001" with depth 3
- **THEN** the system returns the lineage tree including parents, grandparents, and great-grandparents where known
