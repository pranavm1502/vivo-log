import csv
import io
from enum import Enum

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.colony import Cage, Genotype, Mouse
from app.models.study import Cohort, Enrollment, Measurement, Study

router = APIRouter()


class ExportFormat(str, Enum):
    CSV = "csv"
    XLSX = "xlsx"


def _streaming_csv(rows: list[dict], filename: str) -> StreamingResponse:
    if not rows:
        output = io.StringIO()
        output.write("")
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _streaming_xlsx(rows: list[dict], filename: str) -> StreamingResponse:
    wb = Workbook(write_only=True)
    ws = wb.create_sheet()
    if rows:
        ws.append(list(rows[0].keys()))
        for row in rows:
            ws.append(list(row.values()))
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _respond(rows: list[dict], basename: str, fmt: ExportFormat) -> StreamingResponse:
    if fmt == ExportFormat.XLSX:
        return _streaming_xlsx(rows, f"{basename}.xlsx")
    return _streaming_csv(rows, f"{basename}.csv")


# ── Colony Exports ───────────────────────────────────────────────────


@router.get("/mice")
async def export_mice(
    format: ExportFormat = Query(default=ExportFormat.CSV),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Mouse).options(
            selectinload(Mouse.genotype), selectinload(Mouse.cage),
            selectinload(Mouse.sire), selectinload(Mouse.dam),
        )
    )
    mice = result.scalars().all()
    rows = [
        {
            "id": m.id,
            "ear_tag": m.ear_tag,
            "sex": m.sex.value if m.sex else None,
            "date_of_birth": str(m.date_of_birth) if m.date_of_birth else None,
            "status": m.status.value if m.status else None,
            "genotype_name": m.genotype.name if m.genotype else None,
            "cage_label": m.cage.label if m.cage else None,
            "sire_ear_tag": m.sire.ear_tag if m.sire else None,
            "dam_ear_tag": m.dam.ear_tag if m.dam else None,
        }
        for m in mice
    ]
    return _respond(rows, "mice", format)


@router.get("/cages")
async def export_cages(
    format: ExportFormat = Query(default=ExportFormat.CSV),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Cage).options(selectinload(Cage.mice)))
    cages = result.scalars().all()
    rows = [
        {
            "id": c.id,
            "label": c.label,
            "location": c.location,
            "capacity": c.capacity,
            "current_occupancy": len(c.mice),
        }
        for c in cages
    ]
    return _respond(rows, "cages", format)


@router.get("/genotypes")
async def export_genotypes(
    format: ExportFormat = Query(default=ExportFormat.CSV),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Genotype))
    genotypes = result.scalars().all()
    rows = [
        {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "zygosity": g.zygosity,
        }
        for g in genotypes
    ]
    return _respond(rows, "genotypes", format)


# ── Study Exports ────────────────────────────────────────────────────


@router.get("/studies/{study_id}/measurements")
async def export_study_measurements(
    study_id: int,
    format: ExportFormat = Query(default=ExportFormat.CSV),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Measurement)
        .join(Enrollment, Measurement.enrollment_id == Enrollment.id)
        .join(Cohort, Enrollment.cohort_id == Cohort.id)
        .join(Mouse, Enrollment.mouse_id == Mouse.id)
        .join(Study, Cohort.study_id == Study.id)
        .where(Study.id == study_id)
        .options(
            selectinload(Measurement.enrollment).selectinload(Enrollment.cohort).selectinload(Cohort.study),
            selectinload(Measurement.enrollment).selectinload(Enrollment.mouse),
        )
        .order_by(Measurement.recorded_at.asc())
    )
    measurements = result.scalars().all()
    rows = [
        {
            "study_name": m.enrollment.cohort.study.name,
            "cohort_name": m.enrollment.cohort.name,
            "mouse_ear_tag": m.enrollment.mouse.ear_tag,
            "enrolled_at": str(m.enrollment.enrolled_at) if m.enrollment.enrolled_at else None,
            "recorded_at": str(m.recorded_at) if m.recorded_at else None,
            "tumor_length_mm": m.tumor_length_mm,
            "tumor_width_mm": m.tumor_width_mm,
            "tumor_volume_mm3": m.tumor_volume_mm3,
            "body_weight_g": m.body_weight_g,
        }
        for m in measurements
    ]
    return _respond(rows, f"study_{study_id}_measurements", format)


@router.get("/studies/{study_id}/enrollments")
async def export_study_enrollments(
    study_id: int,
    format: ExportFormat = Query(default=ExportFormat.CSV),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Enrollment)
        .join(Cohort, Enrollment.cohort_id == Cohort.id)
        .join(Mouse, Enrollment.mouse_id == Mouse.id)
        .join(Study, Cohort.study_id == Study.id)
        .where(Study.id == study_id)
        .options(
            selectinload(Enrollment.cohort).selectinload(Cohort.study),
            selectinload(Enrollment.mouse),
        )
    )
    enrollments = result.scalars().all()
    rows = [
        {
            "study_name": e.cohort.study.name,
            "cohort_name": e.cohort.name,
            "mouse_ear_tag": e.mouse.ear_tag,
            "enrolled_at": str(e.enrolled_at) if e.enrolled_at else None,
            "removed_at": str(e.removed_at) if e.removed_at else None,
            "removal_reason": e.removal_reason,
        }
        for e in enrollments
    ]
    return _respond(rows, f"study_{study_id}_enrollments", format)
