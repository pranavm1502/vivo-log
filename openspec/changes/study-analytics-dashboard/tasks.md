## 1. Backend: Analytics Endpoints

- [x] 1.1 Create `/api/v1/analytics` router with study validation helper (404 on missing study)
- [x] 1.2 Implement tumor growth time-series endpoint: aggregate measurements by day-post-enrollment per cohort, compute mean/SEM/n
- [x] 1.3 Implement body weight time-series endpoint: same aggregation logic filtered to non-null body_weight_g
- [x] 1.4 Implement study summary endpoint: enrollment count, measurement count, days elapsed, per-cohort latest mean volume
- [x] 1.5 Implement dashboard summary endpoint: all active studies with cohort count, enrollment/measurement totals, latest mean volume
- [x] 1.6 Register analytics router in main.py

## 2. Backend: Analytics Tests

- [x] 2.1 Write tests for tumor growth endpoint (multi-cohort, empty cohort, study not found)
- [x] 2.2 Write tests for body weight endpoint (with data, null values excluded)
- [x] 2.3 Write tests for study summary endpoint
- [x] 2.4 Write tests for dashboard summary endpoint (active studies only, empty case)

## 3. Frontend: Analytics Repository & Providers

- [x] 3.1 Add `fl_chart` dependency to pubspec.yaml
- [x] 3.2 Create analytics data models (TumorGrowthSeries, BodyWeightSeries, StudySummary, DashboardSummary)
- [x] 3.3 Create analytics_repository.dart with methods for all analytics endpoints
- [x] 3.4 Create Riverpod providers for analytics data (tumorGrowthProvider, bodyWeightProvider, studySummaryProvider, dashboardProvider)

## 4. Frontend: Chart Widgets

- [x] 4.1 Create TumorGrowthChart widget (line chart with SEM bands, multi-cohort support, legend)
- [x] 4.2 Create BodyWeightChart widget (line chart, single cohort)
- [x] 4.3 Create StudyComparisonChart widget (multi-cohort overlay for study detail)

## 5. Frontend: Dashboard Screen

- [x] 5.1 Create DashboardScreen with study summary cards (name, days elapsed, cohort count, enrollments, latest volume)
- [x] 5.2 Add tap-to-navigate from dashboard cards to study detail screen
- [x] 5.3 Handle empty state (no active studies message)
- [x] 5.4 Add Dashboard as first tab in bottom nav (shift Mice, Cages, Studies right)

## 6. Frontend: Embed Analytics in Existing Screens

- [x] 6.1 Add StudyComparisonChart to study detail screen above cohorts list (hide if no data)
- [x] 6.2 Add TumorGrowthChart and BodyWeightChart to cohort enrollment screen above enrollments (hide if no data)
- [x] 6.3 Add summary stats row (enrollment count, measurement count) to cohort screen header

## 7. Testing & Polish

- [x] 7.1 Run all backend tests and fix regressions
- [x] 7.2 Run flutter analyze and fix issues
- [x] 7.3 Manual smoke test: verify charts render with existing measurement data
- [x] 7.4 Manual smoke test: verify dashboard loads and navigates correctly
