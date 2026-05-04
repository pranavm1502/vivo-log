## ADDED Requirements

### Requirement: Dashboard landing screen
The system SHALL display a dashboard as the first tab in the bottom navigation, showing a summary of all active studies with key metrics.

#### Scenario: Dashboard with active studies
- **WHEN** the user opens the app or navigates to the Dashboard tab
- **THEN** the screen SHALL display a card for each active study showing study name, days elapsed, cohort count, total enrollments, and latest mean tumor volume

#### Scenario: Dashboard with no active studies
- **WHEN** there are no active studies
- **THEN** the dashboard SHALL display an empty state message

### Requirement: Study summary card on dashboard
Each study card on the dashboard SHALL display key metrics in a compact format and allow navigation to the study detail screen.

#### Scenario: Tapping a study card
- **WHEN** the user taps a study summary card on the dashboard
- **THEN** the app SHALL navigate to the study detail screen for that study

### Requirement: Tumor growth chart on cohort screen
The system SHALL display a line chart showing mean tumor volume over time (days post-enrollment) on the cohort enrollment screen, with error bars representing SEM.

#### Scenario: Cohort with measurement data
- **WHEN** the user views a cohort that has tumor volume measurements
- **THEN** a line chart SHALL be displayed with days on x-axis and mean tumor volume (mm³) on y-axis, with SEM error bands

#### Scenario: Cohort with no measurements
- **WHEN** the user views a cohort with no measurements
- **THEN** the chart area SHALL display a placeholder message indicating no data available

### Requirement: Body weight chart on cohort screen
The system SHALL display a line chart showing mean body weight over time on the cohort enrollment screen.

#### Scenario: Cohort with body weight data
- **WHEN** the user views a cohort that has body weight measurements
- **THEN** a line chart SHALL be displayed with days on x-axis and mean body weight (g) on y-axis

### Requirement: Study-level multi-cohort comparison chart
The study detail screen SHALL display an overlay line chart comparing tumor growth across all cohorts in that study.

#### Scenario: Study with multiple cohorts
- **WHEN** the user views a study detail screen with 2+ cohorts that have measurements
- **THEN** a line chart SHALL be displayed with one colored line per cohort, with a legend identifying each cohort

#### Scenario: Study with single cohort
- **WHEN** the study has only one cohort with measurements
- **THEN** the chart SHALL display a single line for that cohort
