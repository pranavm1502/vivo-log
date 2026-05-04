## Why

Researchers need to quickly assess study progress and treatment efficacy without manually inspecting individual measurements. Typical in-vivo tumor study analytics (tumor growth curves, body weight trends, survival/endpoint tracking) should be computed server-side and displayed per study/cohort, with a top-level dashboard summarizing all active studies at a glance.

## What Changes

- Add backend analytics endpoints that compute per-cohort and per-study metrics (mean tumor volume over time, body weight trends, growth rate, endpoint counts)
- Add a dashboard summary endpoint aggregating key metrics across all active studies
- Add a Flutter dashboard screen as the new home/landing tab showing study health at a glance
- Add analytics charts/visualizations on the study detail and cohort enrollment screens (tumor growth curves, body weight line charts, summary statistics cards)

## Capabilities

### New Capabilities
- `study-analytics`: Backend computation of per-cohort/per-study analytics (tumor growth curves, body weight trends, response classification, summary statistics) and API endpoints to serve them
- `analytics-dashboard`: Flutter dashboard UI with summary cards for active studies, key metrics, and drill-down navigation to study/cohort detail views with embedded charts

### Modified Capabilities
- `in-vivo-study`: Adding analytics display (charts, stats cards) to existing study detail and cohort enrollment screens

## Impact

- **Backend**: New `/api/v1/analytics` router with aggregation queries; no schema migrations needed (reads existing measurement data)
- **Frontend**: New dashboard screen added as first tab; `fl_chart` dependency for line/bar charts; modified study detail and cohort screens to embed analytics widgets
- **Dependencies**: `fl_chart` (Flutter charting library)
