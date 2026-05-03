import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StudyStatus(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    COMPLETED = "Completed"


class Study(Base):
    __tablename__ = "studies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[StudyStatus] = mapped_column(
        Enum(StudyStatus, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=StudyStatus.DRAFT,
    )

    cohorts: Mapped[list["Cohort"]] = relationship(back_populates="study")


class Cohort(Base):
    __tablename__ = "cohorts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    study_id: Mapped[int] = mapped_column(Integer, ForeignKey("studies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    study: Mapped["Study"] = relationship(back_populates="cohorts")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="cohort")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cohort_id: Mapped[int] = mapped_column(Integer, ForeignKey("cohorts.id"), nullable=False)
    mouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("mice.id"), nullable=False)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    removed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    removal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    cohort: Mapped["Cohort"] = relationship(back_populates="enrollments")
    mouse: Mapped["Mouse"] = relationship(back_populates="enrollments")
    measurements: Mapped[list["Measurement"]] = relationship(back_populates="enrollment")


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enrollment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("enrollments.id"), nullable=False
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    tumor_length_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    tumor_width_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    tumor_volume_mm3: Mapped[float | None] = mapped_column(Float, nullable=True)
    body_weight_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    enrollment: Mapped["Enrollment"] = relationship(back_populates="measurements")


from app.models.colony import Mouse  # noqa: E402, F401
