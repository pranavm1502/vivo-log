## Context

The app currently stores per-enrollment tumor measurements (length, width, computed volume, body weight) and exposes them as flat lists. Researchers need aggregated views: growth curves, cohort comparisons, and quick study-level summaries. No analytics infrastructure exists yet.

## Goals / Non-Goals

**Goals:**
- Compute cohort-level analytics server-side (mean ± SEM tumor volume over time, mean body weight over time, percent body weight change)
- Provide per-study summary stats (enrollment count, measurement count, latest mean tumor volume per cohort, days since study start)
- Serve a dashboard-level summary of all active studies with key health indicators
- Display analytics as line charts and summary cards in the Flutter frontend

**Non-Goals:**
- Statistical tests (t-tests, ANOVA) — out of scope for this iteration
- Kaplan-Meier survival analysis — future enhancement
- Custom date range filtering on analytics — use full dataset for now
- PDF report generation

## Decisions

### 1. Server-side aggregation vs client-side computation
**Decision**: Server-side aggregation in Python/SQLAlchemy.
**Rationale**: Keeps Flutter client thin, avoids loading all measurements into memory on mobile, and enables caching later. The backend already has access to all data relationships.

### 2. Analytics response shape
**Decision**: Return time-series data as arrays of `{day: int, mean: float, sem: float, n: int}` objects grouped by cohort. Day 0 = enrollment date for each mouse.
**Rationale**: Day-relative indexing (days post-enrollment) is the standard way to plot tumor growth curves across animals enrolled on different dates.

### 3. Charting library
**Decision**: `fl_chart` for Flutter.
**Rationale**: Mature, well-maintained, supports line charts with error bands, responsive, no native dependencies. Alternatives (syncfusion, charts_flutter) are either paid or archived.

### 4. Dashboard placement
**Decision**: Add Dashboard as the first tab in the bottom nav, shifting existing tabs (Mice, Cages, Studies) right.
**Rationale**: Dashboard is the natural landing page — researchers want a quick health check before drilling into specifics.

### 5. Analytics endpoints structure
**Decision**: Two endpoint groups:
- `GET /api/v1/analytics/studies/{study_id}/tumor-growth` — per-cohort tumor volume time series
- `GET /api/v1/analytics/studies/{study_id}/body-weight` — per-cohort body weight time series
- `GET /api/v1/analytics/studies/{study_id}/summary` — summary stats (enrollment counts, latest volumes, days elapsed)
- `GET /api/v1/analytics/dashboard` — all active studies with summary metrics

**Rationale**: Separate endpoints allow granular fetching; dashboard only needs summaries, not full time-series.

## Risks / Trade-offs

- **[Performance with large datasets]** → Acceptable for current scale (<100 mice, <1000 measurements). If it grows, add query caching or materialized views.
- **[SEM with n=1]** → Return SEM=0 when cohort has single enrollment. Frontend handles gracefully.
- **[Day alignment across mice enrolled on different dates]** → Use days-post-enrollment as x-axis, which is standard practice.
- **[fl_chart dependency size]** → Adds ~200KB to app bundle; acceptable trade-off for native chart rendering.
