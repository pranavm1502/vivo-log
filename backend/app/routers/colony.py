from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.colony import Cage, Genotype, Mouse, MouseStatus, Sex
from app.schemas.colony import (
    CageAssign,
    CageCreate,
    CageRead,
    CageUpdate,
    GenotypeCreate,
    GenotypeRead,
    GenotypeUpdate,
    LineageAssign,
    MouseCreate,
    MouseRead,
    MouseUpdate,
    PedigreeNode,
)

router = APIRouter()


# ── Genotype CRUD (3.1) ─────────────────────────────────────────────

@router.post("/genotypes", response_model=GenotypeRead, status_code=201)
async def create_genotype(body: GenotypeCreate, db: AsyncSession = Depends(get_db)):
    genotype = Genotype(**body.model_dump())
    db.add(genotype)
    await db.commit()
    await db.refresh(genotype)
    return genotype


@router.get("/genotypes", response_model=list[GenotypeRead])
async def list_genotypes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Genotype))
    return result.scalars().all()


@router.get("/genotypes/{genotype_id}", response_model=GenotypeRead)
async def get_genotype(genotype_id: int, db: AsyncSession = Depends(get_db)):
    genotype = await db.get(Genotype, genotype_id)
    if not genotype:
        raise HTTPException(status_code=404, detail="Genotype not found")
    return genotype


@router.patch("/genotypes/{genotype_id}", response_model=GenotypeRead)
async def update_genotype(
    genotype_id: int, body: GenotypeUpdate, db: AsyncSession = Depends(get_db)
):
    genotype = await db.get(Genotype, genotype_id)
    if not genotype:
        raise HTTPException(status_code=404, detail="Genotype not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(genotype, key, value)
    await db.commit()
    await db.refresh(genotype)
    return genotype


@router.delete("/genotypes/{genotype_id}", status_code=204)
async def delete_genotype(genotype_id: int, db: AsyncSession = Depends(get_db)):
    genotype = await db.get(Genotype, genotype_id)
    if not genotype:
        raise HTTPException(status_code=404, detail="Genotype not found")
    await db.delete(genotype)
    await db.commit()


# ── Cage CRUD (3.2) ─────────────────────────────────────────────────

@router.post("/cages", response_model=CageRead, status_code=201)
async def create_cage(body: CageCreate, db: AsyncSession = Depends(get_db)):
    cage = Cage(**body.model_dump())
    db.add(cage)
    await db.commit()
    await db.refresh(cage)
    return CageRead.model_validate(cage, from_attributes=True).model_copy(
        update={"occupancy": 0}
    )


@router.get("/cages", response_model=list[CageRead])
async def list_cages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Cage).options(selectinload(Cage.mice))
    )
    cages = result.scalars().all()
    return [
        CageRead.model_validate(c, from_attributes=True).model_copy(
            update={"occupancy": len(c.mice)}
        )
        for c in cages
    ]


@router.get("/cages/{cage_id}", response_model=CageRead)
async def get_cage(cage_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Cage).where(Cage.id == cage_id).options(selectinload(Cage.mice))
    )
    cage = result.scalar_one_or_none()
    if not cage:
        raise HTTPException(status_code=404, detail="Cage not found")
    return CageRead.model_validate(cage, from_attributes=True).model_copy(
        update={"occupancy": len(cage.mice)}
    )


@router.patch("/cages/{cage_id}", response_model=CageRead)
async def update_cage(
    cage_id: int, body: CageUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Cage).where(Cage.id == cage_id).options(selectinload(Cage.mice))
    )
    cage = result.scalar_one_or_none()
    if not cage:
        raise HTTPException(status_code=404, detail="Cage not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(cage, key, value)
    await db.commit()
    await db.refresh(cage)
    return CageRead.model_validate(cage, from_attributes=True).model_copy(
        update={"occupancy": len(cage.mice)}
    )


@router.delete("/cages/{cage_id}", status_code=204)
async def delete_cage(cage_id: int, db: AsyncSession = Depends(get_db)):
    cage = await db.get(Cage, cage_id)
    if not cage:
        raise HTTPException(status_code=404, detail="Cage not found")
    await db.delete(cage)
    await db.commit()


# ── Mouse CRUD (3.3) ────────────────────────────────────────────────

@router.post("/mice", response_model=MouseRead, status_code=201)
async def create_mouse(body: MouseCreate, db: AsyncSession = Depends(get_db)):
    mouse = Mouse(
        ear_tag=body.ear_tag,
        sex=body.sex,
        date_of_birth=body.date_of_birth,
        status=MouseStatus.ALIVE,
        genotype_id=body.genotype_id,
    )
    # Validate cage capacity if assigning
    if body.cage_id is not None:
        cage = await _get_cage_with_count(db, body.cage_id)
        mouse.cage_id = body.cage_id
    db.add(mouse)
    await db.commit()
    await db.refresh(mouse)
    return mouse


@router.get("/mice", response_model=list[MouseRead])
async def list_mice(
    genotype_id: int | None = Query(default=None),
    status: MouseStatus | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Mouse)
    if genotype_id is not None:
        stmt = stmt.where(Mouse.genotype_id == genotype_id)
    if status is not None:
        stmt = stmt.where(Mouse.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/mice/{mouse_id}", response_model=MouseRead)
async def get_mouse(mouse_id: int, db: AsyncSession = Depends(get_db)):
    mouse = await db.get(Mouse, mouse_id)
    if not mouse:
        raise HTTPException(status_code=404, detail="Mouse not found")
    return mouse


@router.patch("/mice/{mouse_id}", response_model=MouseRead)
async def update_mouse(
    mouse_id: int, body: MouseUpdate, db: AsyncSession = Depends(get_db)
):
    mouse = await db.get(Mouse, mouse_id)
    if not mouse:
        raise HTTPException(status_code=404, detail="Mouse not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(mouse, key, value)
    await db.commit()
    await db.refresh(mouse)
    return mouse


@router.delete("/mice/{mouse_id}", status_code=204)
async def delete_mouse(mouse_id: int, db: AsyncSession = Depends(get_db)):
    mouse = await db.get(Mouse, mouse_id)
    if not mouse:
        raise HTTPException(status_code=404, detail="Mouse not found")
    await db.delete(mouse)
    await db.commit()


# ── Lineage Assignment (3.4) ────────────────────────────────────────

@router.put("/mice/{mouse_id}/lineage", response_model=MouseRead)
async def assign_lineage(
    mouse_id: int, body: LineageAssign, db: AsyncSession = Depends(get_db)
):
    mouse = await db.get(Mouse, mouse_id)
    if not mouse:
        raise HTTPException(status_code=404, detail="Mouse not found")

    if body.sire_id is not None:
        sire = await db.get(Mouse, body.sire_id)
        if not sire:
            raise HTTPException(status_code=404, detail="Sire not found")
        if sire.sex != Sex.MALE:
            raise HTTPException(status_code=400, detail="Sire must be male")
        if body.sire_id == mouse_id:
            raise HTTPException(status_code=400, detail="Mouse cannot be its own sire")
        mouse.sire_id = body.sire_id

    if body.dam_id is not None:
        dam = await db.get(Mouse, body.dam_id)
        if not dam:
            raise HTTPException(status_code=404, detail="Dam not found")
        if dam.sex != Sex.FEMALE:
            raise HTTPException(status_code=400, detail="Dam must be female")
        if body.dam_id == mouse_id:
            raise HTTPException(status_code=400, detail="Mouse cannot be its own dam")
        mouse.dam_id = body.dam_id

    await db.commit()
    await db.refresh(mouse)
    return mouse


# ── Cage Assignment (3.5) ───────────────────────────────────────────

async def _get_cage_with_count(db: AsyncSession, cage_id: int) -> Cage:
    """Get a cage and validate it exists; raise 409 if at capacity."""
    result = await db.execute(
        select(Cage).where(Cage.id == cage_id).options(selectinload(Cage.mice))
    )
    cage = result.scalar_one_or_none()
    if not cage:
        raise HTTPException(status_code=404, detail="Cage not found")
    if len(cage.mice) >= cage.capacity:
        raise HTTPException(status_code=409, detail="Cage is at capacity")
    return cage


@router.put("/mice/{mouse_id}/cage", response_model=MouseRead)
async def assign_cage(
    mouse_id: int, body: CageAssign, db: AsyncSession = Depends(get_db)
):
    mouse = await db.get(Mouse, mouse_id)
    if not mouse:
        raise HTTPException(status_code=404, detail="Mouse not found")

    if body.cage_id is not None:
        # Exclude this mouse from count if already in target cage
        result = await db.execute(
            select(Cage).where(Cage.id == body.cage_id).options(selectinload(Cage.mice))
        )
        cage = result.scalar_one_or_none()
        if not cage:
            raise HTTPException(status_code=404, detail="Cage not found")
        current_count = sum(1 for m in cage.mice if m.id != mouse_id)
        if current_count >= cage.capacity:
            raise HTTPException(status_code=409, detail="Cage is at capacity")

    mouse.cage_id = body.cage_id
    await db.commit()
    await db.refresh(mouse)
    return mouse


# ── Pedigree (3.6) ──────────────────────────────────────────────────

@router.get("/mice/{mouse_id}/pedigree", response_model=PedigreeNode)
async def get_pedigree(
    mouse_id: int,
    depth: int = Query(default=3, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
):
    mouse = await db.get(Mouse, mouse_id)
    if not mouse:
        raise HTTPException(status_code=404, detail="Mouse not found")
    return await _build_pedigree(db, mouse, depth)


async def _build_pedigree(
    db: AsyncSession, mouse: Mouse, depth: int
) -> PedigreeNode:
    node = PedigreeNode(id=mouse.id, ear_tag=mouse.ear_tag, sex=mouse.sex)
    if depth <= 0:
        return node
    if mouse.sire_id:
        sire = await db.get(Mouse, mouse.sire_id)
        if sire:
            node.sire = await _build_pedigree(db, sire, depth - 1)
    if mouse.dam_id:
        dam = await db.get(Mouse, mouse.dam_id)
        if dam:
            node.dam = await _build_pedigree(db, dam, depth - 1)
    return node
