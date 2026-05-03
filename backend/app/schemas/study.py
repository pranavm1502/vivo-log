from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.study import StudyStatus


# --- Study ---

class StudyCreate(BaseModel):
    name: str
    description: str | None = None
    start_date: date
    end_date: date | None = None


class StudyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: StudyStatus | None = None
    end_date: date | None = None


class StudyRead(BaseModel):
    id: int
    name: str
    description: str | None
    start_date: date
    end_date: date | None
    status: StudyStatus

    model_config = {"from_attributes": True}


# --- Cohort ---

class CohortCreate(BaseModel):
    name: str
    description: str | None = None


class CohortRead(BaseModel):
    id: int
    study_id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}


# --- Enrollment ---

class EnrollmentCreate(BaseModel):
    mouse_id: int


class EnrollmentRemove(BaseModel):
    removal_reason: str | None = None


class EnrollmentRead(BaseModel):
    id: int
    cohort_id: int
    mouse_id: int
    enrolled_at: datetime
    removed_at: datetime | None
    removal_reason: str | None

    model_config = {"from_attributes": True}


# --- Measurement ---

class MeasurementCreate(BaseModel):
    tumor_length_mm: float | None = Field(default=None, ge=0)
    tumor_width_mm: float | None = Field(default=None, ge=0)
    body_weight_g: float | None = Field(default=None, ge=0)
    notes: str | None = None


class MeasurementRead(BaseModel):
    id: int
    enrollment_id: int
    recorded_at: datetime
    tumor_length_mm: float | None
    tumor_width_mm: float | None
    tumor_volume_mm3: float | None
    body_weight_g: float | None
    notes: str | None

    model_config = {"from_attributes": True}
