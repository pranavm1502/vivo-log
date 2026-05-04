from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.colony import Mouse, MouseStatus
from app.models.study import Cohort, Enrollment, Measurement, Study, StudyStatus
from app.schemas.study import (
    CohortCreate,
    CohortRead,
    CohortUpdate,
    EnrollmentCreate,
    EnrollmentRead,
    EnrollmentRemove,
    MeasurementCreate,
    MeasurementRead,
    StudyCreate,
    StudyRead,
    StudyUpdate,
)

router = APIRouter()


# ── Study CRUD (4.1) ────────────────────────────────────────────────

@router.post("", response_model=StudyRead, status_code=201)
async def create_study(body: StudyCreate, db: AsyncSession = Depends(get_db)):
    study = Study(**body.model_dump(), status=StudyStatus.DRAFT)
    db.add(study)
    await db.commit()
    await db.refresh(study)
    return study


@router.get("", response_model=list[StudyRead])
async def list_studies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Study))
    return result.scalars().all()


@router.get("/{study_id}", response_model=StudyRead)
async def get_study(study_id: int, db: AsyncSession = Depends(get_db)):
    study = await db.get(Study, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    return study


@router.patch("/{study_id}", response_model=StudyRead)
async def update_study(
    study_id: int, body: StudyUpdate, db: AsyncSession = Depends(get_db)
):
    study = await db.get(Study, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(study, key, value)
    await db.commit()
    await db.refresh(study)
    return study


@router.delete("/{study_id}", status_code=204)
async def delete_study(study_id: int, db: AsyncSession = Depends(get_db)):
    study = await db.get(Study, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    # Check if any cohorts in this study have enrollments
    count = await db.scalar(
        select(func.count())
        .select_from(Enrollment)
        .join(Cohort, Enrollment.cohort_id == Cohort.id)
        .where(Cohort.study_id == study_id)
    )
    if count:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete study because it has active enrollments",
        )
    await db.delete(study)
    await db.commit()


# ── Cohort CRUD (4.2) ───────────────────────────────────────────────

@router.post("/{study_id}/cohorts", response_model=CohortRead, status_code=201)
async def create_cohort(
    study_id: int, body: CohortCreate, db: AsyncSession = Depends(get_db)
):
    study = await db.get(Study, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    cohort = Cohort(study_id=study_id, **body.model_dump())
    db.add(cohort)
    await db.commit()
    await db.refresh(cohort)
    return cohort


@router.get("/{study_id}/cohorts", response_model=list[CohortRead])
async def list_cohorts(study_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Cohort).where(Cohort.study_id == study_id))
    return result.scalars().all()


@router.get("/{study_id}/cohorts/{cohort_id}", response_model=CohortRead)
async def get_cohort(
    study_id: int, cohort_id: int, db: AsyncSession = Depends(get_db)
):
    cohort = await db.get(Cohort, cohort_id)
    if not cohort or cohort.study_id != study_id:
        raise HTTPException(status_code=404, detail="Cohort not found")
    return cohort


@router.patch("/{study_id}/cohorts/{cohort_id}", response_model=CohortRead)
async def update_cohort(
    study_id: int,
    cohort_id: int,
    body: CohortUpdate,
    db: AsyncSession = Depends(get_db),
):
    cohort = await db.get(Cohort, cohort_id)
    if not cohort or cohort.study_id != study_id:
        raise HTTPException(status_code=404, detail="Cohort not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(cohort, field, value)
    await db.commit()
    await db.refresh(cohort)
    return cohort


@router.delete("/{study_id}/cohorts/{cohort_id}", status_code=204)
async def delete_cohort(
    study_id: int, cohort_id: int, db: AsyncSession = Depends(get_db)
):
    cohort = await db.get(Cohort, cohort_id)
    if not cohort or cohort.study_id != study_id:
        raise HTTPException(status_code=404, detail="Cohort not found")
    # Check if cohort has enrollments
    count = await db.scalar(
        select(func.count()).where(Enrollment.cohort_id == cohort_id)
    )
    if count:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete cohort because it has enrollments",
        )
    await db.delete(cohort)
    await db.commit()


# ── Enrollment (4.3, 4.4) ───────────────────────────────────────────

@router.post(
    "/{study_id}/cohorts/{cohort_id}/enrollments",
    response_model=EnrollmentRead,
    status_code=201,
)
async def enroll_mouse(
    study_id: int,
    cohort_id: int,
    body: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
):
    # Validate study exists and is Active
    study = await db.get(Study, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    if study.status != StudyStatus.ACTIVE:
        raise HTTPException(
            status_code=409, detail="Study must be Active to enroll mice"
        )

    # Validate cohort belongs to study
    cohort = await db.get(Cohort, cohort_id)
    if not cohort or cohort.study_id != study_id:
        raise HTTPException(status_code=404, detail="Cohort not found")

    # Validate mouse exists and is eligible
    mouse = await db.get(Mouse, body.mouse_id)
    if not mouse:
        raise HTTPException(status_code=404, detail="Mouse not found")
    if mouse.status in (MouseStatus.DECEASED, MouseStatus.CULLED):
        raise HTTPException(
            status_code=409,
            detail=f"{mouse.status.value} mice cannot be enrolled",
        )

    enrollment = Enrollment(
        cohort_id=cohort_id,
        mouse_id=body.mouse_id,
        enrolled_at=datetime.now(UTC).replace(tzinfo=None),
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.get(
    "/{study_id}/cohorts/{cohort_id}/enrollments",
    response_model=list[EnrollmentRead],
)
async def list_enrollments(
    study_id: int, cohort_id: int, db: AsyncSession = Depends(get_db)
):
    cohort = await db.get(Cohort, cohort_id)
    if not cohort or cohort.study_id != study_id:
        raise HTTPException(status_code=404, detail="Cohort not found")
    result = await db.execute(
        select(Enrollment).where(Enrollment.cohort_id == cohort_id)
    )
    return result.scalars().all()


@router.post(
    "/{study_id}/cohorts/{cohort_id}/enrollments/{enrollment_id}/remove",
    response_model=EnrollmentRead,
)
async def remove_enrollment(
    study_id: int,
    cohort_id: int,
    enrollment_id: int,
    body: EnrollmentRemove,
    db: AsyncSession = Depends(get_db),
):
    enrollment = await db.get(Enrollment, enrollment_id)
    if not enrollment or enrollment.cohort_id != cohort_id:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    enrollment.removed_at = datetime.now(UTC).replace(tzinfo=None)
    enrollment.removal_reason = body.removal_reason
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


# ── Measurements (4.5, 4.6, 4.7) ────────────────────────────────────

def _compute_tumor_volume(
    length: float | None, width: float | None
) -> float | None:
    """Volume = Length × Width² / 2. Returns None if either dimension is missing."""
    if length is not None and width is not None:
        return length * width * width / 2.0
    return None


@router.post(
    "/{study_id}/cohorts/{cohort_id}/enrollments/{enrollment_id}/measurements",
    response_model=MeasurementRead,
    status_code=201,
)
async def create_measurement(
    study_id: int,
    cohort_id: int,
    enrollment_id: int,
    body: MeasurementCreate,
    db: AsyncSession = Depends(get_db),
):
    enrollment = await db.get(Enrollment, enrollment_id)
    if not enrollment or enrollment.cohort_id != cohort_id:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    tumor_volume = _compute_tumor_volume(body.tumor_length_mm, body.tumor_width_mm)

    measurement = Measurement(
        enrollment_id=enrollment_id,
        recorded_at=datetime.now(UTC).replace(tzinfo=None),
        tumor_length_mm=body.tumor_length_mm,
        tumor_width_mm=body.tumor_width_mm,
        tumor_volume_mm3=tumor_volume,
        body_weight_g=body.body_weight_g,
        notes=body.notes,
    )
    db.add(measurement)
    await db.commit()
    await db.refresh(measurement)
    return measurement


@router.get(
    "/{study_id}/cohorts/{cohort_id}/enrollments/{enrollment_id}/measurements",
    response_model=list[MeasurementRead],
)
async def list_measurements(
    study_id: int,
    cohort_id: int,
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
):
    enrollment = await db.get(Enrollment, enrollment_id)
    if not enrollment or enrollment.cohort_id != cohort_id:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    result = await db.execute(
        select(Measurement)
        .where(Measurement.enrollment_id == enrollment_id)
        .order_by(Measurement.recorded_at.asc())
    )
    return result.scalars().all()


@router.delete(
    "/{study_id}/cohorts/{cohort_id}/enrollments/{enrollment_id}/measurements/{measurement_id}",
    status_code=204,
)
async def delete_measurement(
    study_id: int,
    cohort_id: int,
    enrollment_id: int,
    measurement_id: int,
    db: AsyncSession = Depends(get_db),
):
    measurement = await db.get(Measurement, measurement_id)
    if not measurement or measurement.enrollment_id != enrollment_id:
        raise HTTPException(status_code=404, detail="Measurement not found")
    await db.delete(measurement)
    await db.commit()
