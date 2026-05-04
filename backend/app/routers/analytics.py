"""Analytics router – aggregated study metrics."""

import math
from collections import defaultdict
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.study import Cohort, Enrollment, Measurement, Study, StudyStatus

router = APIRouter()


# ── Response schemas ──────────────────────────────────────────────────────────


class TimeSeriesPoint(BaseModel):
    day: int
    mean: float
    sem: float
    n: int


class CohortSeries(BaseModel):
    cohort_id: int
    cohort_name: str
    series: list[TimeSeriesPoint]


class CohortSummary(BaseModel):
    cohort_id: int
    cohort_name: str
    enrollment_count: int
    latest_mean_volume: float | None


class StudySummaryResponse(BaseModel):
    study_id: int
    study_name: str
    status: str
    days_elapsed: int
    total_enrollments: int
    total_measurements: int
    cohorts: list[CohortSummary]


class DashboardStudy(BaseModel):
    study_id: int
    study_name: str
    days_elapsed: int
    cohort_count: int
    total_enrollments: int
    total_measurements: int
    latest_mean_volume: float | None


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _get_study_or_404(study_id: int, db: AsyncSession) -> Study:
    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    return study


def _days_between(dt: datetime, enrolled_at: datetime) -> int:
    """Compute days post-enrollment, rounded to nearest integer."""
    delta = dt - enrolled_at
    return round(delta.total_seconds() / 86400)


def _compute_series(
    measurements: list[tuple[datetime, datetime, float | None]],
    value_extractor: str,
) -> list[TimeSeriesPoint]:
    """Aggregate measurements into daily mean ± SEM.

    measurements: list of (recorded_at, enrolled_at, value) tuples.
    """
    by_day: dict[int, list[float]] = defaultdict(list)
    for recorded_at, enrolled_at, value in measurements:
        if value is None:
            continue
        day = _days_between(recorded_at, enrolled_at)
        by_day[day].append(value)

    points: list[TimeSeriesPoint] = []
    for day in sorted(by_day):
        values = by_day[day]
        n = len(values)
        mean = sum(values) / n
        if n > 1:
            variance = sum((v - mean) ** 2 for v in values) / (n - 1)
            sem = math.sqrt(variance) / math.sqrt(n)
        else:
            sem = 0.0
        points.append(TimeSeriesPoint(day=day, mean=round(mean, 4), sem=round(sem, 4), n=n))
    return points


async def _load_study_measurements(study_id: int, db: AsyncSession):
    """Load all cohorts with enrollments and measurements for a study."""
    result = await db.execute(
        select(Cohort)
        .where(Cohort.study_id == study_id)
        .options(
            selectinload(Cohort.enrollments).selectinload(Enrollment.measurements)
        )
    )
    return result.scalars().all()


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/studies/{study_id}/tumor-growth", response_model=list[CohortSeries])
async def tumor_growth(study_id: int, db: AsyncSession = Depends(get_db)):
    await _get_study_or_404(study_id, db)
    cohorts = await _load_study_measurements(study_id, db)

    result = []
    for cohort in cohorts:
        data: list[tuple[datetime, datetime, float | None]] = []
        for enrollment in cohort.enrollments:
            for m in enrollment.measurements:
                data.append((m.recorded_at, enrollment.enrolled_at, m.tumor_volume_mm3))
        series = _compute_series(data, "tumor_volume_mm3")
        result.append(CohortSeries(cohort_id=cohort.id, cohort_name=cohort.name, series=series))
    return result


@router.get("/studies/{study_id}/body-weight", response_model=list[CohortSeries])
async def body_weight(study_id: int, db: AsyncSession = Depends(get_db)):
    await _get_study_or_404(study_id, db)
    cohorts = await _load_study_measurements(study_id, db)

    result = []
    for cohort in cohorts:
        data: list[tuple[datetime, datetime, float | None]] = []
        for enrollment in cohort.enrollments:
            for m in enrollment.measurements:
                data.append((m.recorded_at, enrollment.enrolled_at, m.body_weight_g))
        series = _compute_series(data, "body_weight_g")
        result.append(CohortSeries(cohort_id=cohort.id, cohort_name=cohort.name, series=series))
    return result


@router.get("/studies/{study_id}/summary", response_model=StudySummaryResponse)
async def study_summary(study_id: int, db: AsyncSession = Depends(get_db)):
    study = await _get_study_or_404(study_id, db)
    cohorts = await _load_study_measurements(study_id, db)

    days_elapsed = (date.today() - study.start_date).days

    cohort_summaries: list[CohortSummary] = []
    total_enrollments = 0
    total_measurements = 0

    for cohort in cohorts:
        enrollment_count = len(cohort.enrollments)
        total_enrollments += enrollment_count
        measurement_count = sum(len(e.measurements) for e in cohort.enrollments)
        total_measurements += measurement_count

        # Latest mean volume: get the most recent day's measurements
        latest_volumes: list[float] = []
        max_day = -1
        for enrollment in cohort.enrollments:
            for m in enrollment.measurements:
                if m.tumor_volume_mm3 is not None:
                    day = _days_between(m.recorded_at, enrollment.enrolled_at)
                    if day > max_day:
                        max_day = day
                        latest_volumes = [m.tumor_volume_mm3]
                    elif day == max_day:
                        latest_volumes.append(m.tumor_volume_mm3)

        latest_mean = round(sum(latest_volumes) / len(latest_volumes), 2) if latest_volumes else None
        cohort_summaries.append(CohortSummary(
            cohort_id=cohort.id,
            cohort_name=cohort.name,
            enrollment_count=enrollment_count,
            latest_mean_volume=latest_mean,
        ))

    return StudySummaryResponse(
        study_id=study.id,
        study_name=study.name,
        status=study.status.value if isinstance(study.status, StudyStatus) else study.status,
        days_elapsed=days_elapsed,
        total_enrollments=total_enrollments,
        total_measurements=total_measurements,
        cohorts=cohort_summaries,
    )


@router.get("/dashboard", response_model=list[DashboardStudy])
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Study)
        .where(Study.status == StudyStatus.ACTIVE)
        .options(
            selectinload(Study.cohorts)
            .selectinload(Cohort.enrollments)
            .selectinload(Enrollment.measurements)
        )
    )
    studies = result.scalars().all()

    dashboard: list[DashboardStudy] = []
    for study in studies:
        days_elapsed = (date.today() - study.start_date).days
        total_enrollments = 0
        total_measurements = 0
        all_latest_volumes: list[float] = []

        for cohort in study.cohorts:
            total_enrollments += len(cohort.enrollments)
            for enrollment in cohort.enrollments:
                total_measurements += len(enrollment.measurements)
                # Get latest volume per enrollment
                latest_m = None
                for m in enrollment.measurements:
                    if m.tumor_volume_mm3 is not None:
                        if latest_m is None or m.recorded_at > latest_m.recorded_at:
                            latest_m = m
                if latest_m and latest_m.tumor_volume_mm3 is not None:
                    all_latest_volumes.append(latest_m.tumor_volume_mm3)

        latest_mean = round(sum(all_latest_volumes) / len(all_latest_volumes), 2) if all_latest_volumes else None

        dashboard.append(DashboardStudy(
            study_id=study.id,
            study_name=study.name,
            days_elapsed=days_elapsed,
            cohort_count=len(study.cohorts),
            total_enrollments=total_enrollments,
            total_measurements=total_measurements,
            latest_mean_volume=latest_mean,
        ))

    return dashboard
