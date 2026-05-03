import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MouseStatus(str, enum.Enum):
    ALIVE = "Alive"
    DECEASED = "Deceased"
    CULLED = "Culled"


class Sex(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"


class Genotype(Base):
    __tablename__ = "genotypes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    zygosity: Mapped[str | None] = mapped_column(String(50), nullable=True)

    mice: Mapped[list["Mouse"]] = relationship(back_populates="genotype")


class Cage(Base):
    __tablename__ = "cages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    mice: Mapped[list["Mouse"]] = relationship(back_populates="cage")


class Mouse(Base):
    __tablename__ = "mice"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ear_tag: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    sex: Mapped[Sex] = mapped_column(
        Enum(Sex, values_callable=lambda e: [x.value for x in e]), nullable=False
    )
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[MouseStatus] = mapped_column(
        Enum(MouseStatus, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=MouseStatus.ALIVE,
    )

    sire_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("mice.id"), nullable=True
    )
    dam_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("mice.id"), nullable=True
    )
    genotype_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("genotypes.id"), nullable=True
    )
    cage_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("cages.id"), nullable=True
    )

    sire: Mapped["Mouse | None"] = relationship(
        "Mouse", remote_side="Mouse.id", foreign_keys=[sire_id]
    )
    dam: Mapped["Mouse | None"] = relationship(
        "Mouse", remote_side="Mouse.id", foreign_keys=[dam_id]
    )
    genotype: Mapped["Genotype | None"] = relationship(back_populates="mice")
    cage: Mapped["Cage | None"] = relationship(back_populates="mice")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="mouse")


# Import here to avoid circular — Enrollment references Mouse
from app.models.study import Enrollment  # noqa: E402, F401
