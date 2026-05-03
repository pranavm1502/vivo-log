from datetime import date

from pydantic import BaseModel, Field

from app.models.colony import MouseStatus, Sex


# --- Genotype ---

class GenotypeCreate(BaseModel):
    name: str
    description: str | None = None
    zygosity: str | None = None


class GenotypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    zygosity: str | None = None


class GenotypeRead(BaseModel):
    id: int
    name: str
    description: str | None
    zygosity: str | None

    model_config = {"from_attributes": True}


# --- Cage ---

class CageCreate(BaseModel):
    label: str
    location: str | None = None
    capacity: int = Field(default=5, ge=1)


class CageUpdate(BaseModel):
    label: str | None = None
    location: str | None = None
    capacity: int | None = Field(default=None, ge=1)


class CageRead(BaseModel):
    id: int
    label: str
    location: str | None
    capacity: int
    occupancy: int = 0

    model_config = {"from_attributes": True}


# --- Mouse ---

class MouseCreate(BaseModel):
    ear_tag: str
    sex: Sex
    date_of_birth: date
    genotype_id: int | None = None
    cage_id: int | None = None


class MouseUpdate(BaseModel):
    ear_tag: str | None = None
    status: MouseStatus | None = None
    genotype_id: int | None = None


class MouseRead(BaseModel):
    id: int
    ear_tag: str
    sex: Sex
    date_of_birth: date
    status: MouseStatus
    sire_id: int | None
    dam_id: int | None
    genotype_id: int | None
    cage_id: int | None

    model_config = {"from_attributes": True}


class LineageAssign(BaseModel):
    sire_id: int | None = None
    dam_id: int | None = None


class CageAssign(BaseModel):
    cage_id: int | None = None


class PedigreeNode(BaseModel):
    id: int
    ear_tag: str
    sex: Sex
    sire: "PedigreeNode | None" = None
    dam: "PedigreeNode | None" = None

    model_config = {"from_attributes": True}
