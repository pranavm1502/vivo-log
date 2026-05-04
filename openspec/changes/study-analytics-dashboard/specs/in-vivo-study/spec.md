## MODIFIED Requirements

### Requirement: Study detail screen layout
The study detail screen SHALL display a tumor growth comparison chart above the cohorts list, allowing researchers to assess treatment efficacy at a glance before drilling into individual cohorts.

#### Scenario: Study with measurement data
- **WHEN** the user navigates to a study detail screen that has cohorts with measurements
- **THEN** a multi-cohort tumor growth comparison chart SHALL be displayed above the cohorts list section

#### Scenario: Study with no measurement data
- **WHEN** the user navigates to a study detail screen where no cohorts have measurements
- **THEN** the chart section SHALL be hidden and only the cohorts list is shown

### Requirement: Cohort enrollment screen layout
The cohort enrollment screen SHALL display analytics charts (tumor growth and body weight) above the enrollments list, providing visual context for the cohort's data.

#### Scenario: Viewing cohort with measurements
- **WHEN** the user navigates to a cohort enrollment screen that has measurements
- **THEN** tumor growth and body weight charts SHALL be displayed above the enrollment list

#### Scenario: Viewing cohort without measurements
- **WHEN** the user navigates to a cohort enrollment screen with no measurements
- **THEN** the charts section SHALL be hidden and only the enrollment/enroll UI is shown
