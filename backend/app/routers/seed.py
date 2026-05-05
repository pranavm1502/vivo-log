"""Seed endpoint to load demo data into the database."""

import random
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.colony import Cage, Genotype, Mouse, Sex, MouseStatus
from app.models.study import Study, StudyStatus, Cohort, Enrollment, Measurement

router = APIRouter()


@router.post("/demo-data")
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    """Load realistic demo data for showcasing all features.
    Only works if the database is empty (no existing studies).
    """
    # Guard: only seed if DB is empty
    result = await db.execute(select(func.count(Study.id)))
    if result.scalar() > 0:
        return {"message": "Database already has data. Skipping seed.", "seeded": False}

    today = date.today()
    random.seed(42)

    # --- Genotypes ---
    genotypes = {}
    for name, desc, zyg in [
        ("Wild-type (C57BL/6)", "Standard inbred strain", "Homozygous"),
        ("p53 -/-", "Tumor suppressor knockout", "Homozygous"),
        ("BRCA1 +/-", "Breast cancer susceptibility", "Heterozygous"),
        ("HER2-OE", "HER2 overexpression transgenic", "Hemizygous"),
    ]:
        g = Genotype(name=name, description=desc, zygosity=zyg)
        db.add(g)
        await db.flush()
        genotypes[name] = g.id

    # --- Cages ---
    cages = {}
    for label, loc, cap in [
        ("A1-01", "Room 101, Rack A1", 5),
        ("A1-02", "Room 101, Rack A1", 5),
        ("A2-01", "Room 101, Rack A2", 5),
        ("A2-02", "Room 101, Rack A2", 5),
        ("B1-01", "Room 102, Rack B1", 5),
        ("B1-02", "Room 102, Rack B1", 5),
    ]:
        c = Cage(label=label, location=loc, capacity=cap)
        db.add(c)
        await db.flush()
        cages[label] = c.id

    # --- Mice ---
    mouse_ids = {}
    mouse_data = [
        ("WT-F001", "Female", "Wild-type (C57BL/6)", "A1-01", -90),
        ("WT-F002", "Female", "Wild-type (C57BL/6)", "A1-01", -88),
        ("WT-F003", "Female", "Wild-type (C57BL/6)", "A1-01", -92),
        ("WT-F004", "Female", "Wild-type (C57BL/6)", "A1-01", -85),
        ("WT-F005", "Female", "Wild-type (C57BL/6)", "A1-01", -91),
        ("WT-M001", "Male", "Wild-type (C57BL/6)", "A1-02", -89),
        ("WT-M002", "Male", "Wild-type (C57BL/6)", "A1-02", -87),
        ("WT-M003", "Male", "Wild-type (C57BL/6)", "A1-02", -93),
        ("WT-M004", "Male", "Wild-type (C57BL/6)", "A1-02", -86),
        ("P53-F001", "Female", "p53 -/-", "A2-01", -75),
        ("P53-F002", "Female", "p53 -/-", "A2-01", -74),
        ("P53-F003", "Female", "p53 -/-", "A2-01", -76),
        ("P53-M001", "Male", "p53 -/-", "A2-01", -73),
        ("P53-M002", "Male", "p53 -/-", "A2-01", -77),
        ("BR-F001", "Female", "BRCA1 +/-", "A2-02", -80),
        ("BR-F002", "Female", "BRCA1 +/-", "A2-02", -82),
        ("BR-F003", "Female", "BRCA1 +/-", "A2-02", -79),
        ("BR-M001", "Male", "BRCA1 +/-", "A2-02", -81),
        ("HER2-F001", "Female", "HER2-OE", "B1-01", -70),
        ("HER2-F002", "Female", "HER2-OE", "B1-01", -72),
        ("HER2-F003", "Female", "HER2-OE", "B1-01", -68),
        ("HER2-M001", "Male", "HER2-OE", "B1-01", -71),
        ("HER2-M002", "Male", "HER2-OE", "B1-01", -69),
        ("WT-F006", "Female", "Wild-type (C57BL/6)", "B1-02", -100),
        ("WT-M005", "Male", "Wild-type (C57BL/6)", "B1-02", -105),
    ]

    for ear_tag, sex, geno_name, cage_label, dob_offset in mouse_data:
        m = Mouse(
            ear_tag=ear_tag,
            sex=Sex(sex),
            date_of_birth=today + timedelta(days=dob_offset),
            status=MouseStatus.ALIVE,
            genotype_id=genotypes[geno_name],
            cage_id=cages[cage_label],
        )
        db.add(m)
        await db.flush()
        mouse_ids[ear_tag] = m.id

    # Set lineage: WT-F005 parents are WT-F006 (dam) and WT-M005 (sire)
    mouse_f005 = await db.get(Mouse, mouse_ids["WT-F005"])
    mouse_f005.dam_id = mouse_ids["WT-F006"]
    mouse_f005.sire_id = mouse_ids["WT-M005"]

    # --- Study 1: Completed tumor growth study ---
    study1 = Study(
        name="Tumor Growth Kinetics - p53 vs WT",
        description="Compare subcutaneous tumor growth rates between p53 knockout and wild-type mice after B16 melanoma cell injection.",
        start_date=today - timedelta(days=42),
        end_date=today - timedelta(days=14),
        status=StudyStatus.ACTIVE,
    )
    db.add(study1)
    await db.flush()

    cohort_wt = Cohort(study_id=study1.id, name="Vehicle Control (WT)", description="Wild-type mice, PBS injection only")
    cohort_p53 = Cohort(study_id=study1.id, name="p53 KO + Tumor", description="p53 knockout mice with B16 melanoma cells")
    db.add_all([cohort_wt, cohort_p53])
    await db.flush()

    # Enroll WT mice
    wt_tags = ["WT-F001", "WT-F002", "WT-F003", "WT-M001", "WT-M002"]
    p53_tags = ["P53-F001", "P53-F002", "P53-F003", "P53-M001", "P53-M002"]
    wt_enrollments = []
    p53_enrollments = []

    for tag in wt_tags:
        e = Enrollment(cohort_id=cohort_wt.id, mouse_id=mouse_ids[tag], enrolled_at=today - timedelta(days=42))
        db.add(e)
        await db.flush()
        wt_enrollments.append(e)

    for tag in p53_tags:
        e = Enrollment(cohort_id=cohort_p53.id, mouse_id=mouse_ids[tag], enrolled_at=today - timedelta(days=42))
        db.add(e)
        await db.flush()
        p53_enrollments.append(e)

    # Measurements over 4 weeks
    measurement_days = [0, 3, 7, 10, 14, 17, 21, 24, 28]

    for enr in wt_enrollments:
        base_weight = random.uniform(20.0, 23.0)
        for day in measurement_days:
            tumor_l = round(max(0, random.gauss(1.0 + day * 0.08, 0.3)), 1)
            tumor_w = round(max(0, tumor_l * random.uniform(0.6, 0.8)), 1)
            vol = round(tumor_l * tumor_w * tumor_w * 0.5, 1)
            weight = round(base_weight + random.gauss(0.3 * day / 28, 0.3), 1)
            db.add(Measurement(
                enrollment_id=enr.id,
                recorded_at=today - timedelta(days=42) + timedelta(days=day),
                tumor_length_mm=tumor_l,
                tumor_width_mm=tumor_w,
                tumor_volume_mm3=vol,
                body_weight_g=weight,
            ))

    for enr in p53_enrollments:
        base_weight = random.uniform(19.5, 22.5)
        for day in measurement_days:
            tumor_l = round(max(0, random.gauss(1.5 + day * 0.35, 0.5)), 1)
            tumor_w = round(max(0, tumor_l * random.uniform(0.65, 0.85)), 1)
            vol = round(tumor_l * tumor_w * tumor_w * 0.5, 1)
            weight_change = 0.2 * day / 28 if day < 14 else -0.5 * (day - 14) / 14
            weight = round(base_weight + random.gauss(weight_change, 0.4), 1)
            db.add(Measurement(
                enrollment_id=enr.id,
                recorded_at=today - timedelta(days=42) + timedelta(days=day),
                tumor_length_mm=tumor_l,
                tumor_width_mm=tumor_w,
                tumor_volume_mm3=vol,
                body_weight_g=weight,
            ))

    # Mark study 1 as completed
    study1.status = StudyStatus.COMPLETED

    # --- Study 2: Active immunotherapy study ---
    study2 = Study(
        name="Anti-PD1 Immunotherapy Response",
        description="Evaluate anti-PD1 checkpoint inhibitor efficacy in HER2-overexpressing tumor model.",
        start_date=today - timedelta(days=14),
        status=StudyStatus.ACTIVE,
    )
    db.add(study2)
    await db.flush()

    cohort_ctrl = Cohort(study_id=study2.id, name="Isotype Control", description="IgG isotype control antibody, 10mg/kg biweekly")
    cohort_pd1 = Cohort(study_id=study2.id, name="Anti-PD1 Treatment", description="Anti-PD1 antibody, 10mg/kg biweekly")
    db.add_all([cohort_ctrl, cohort_pd1])
    await db.flush()

    ctrl_tags = ["HER2-F001", "HER2-F002"]
    pd1_tags = ["HER2-F003", "HER2-M001", "HER2-M002"]
    ctrl_enrollments = []
    pd1_enrollments = []

    for tag in ctrl_tags:
        e = Enrollment(cohort_id=cohort_ctrl.id, mouse_id=mouse_ids[tag], enrolled_at=today - timedelta(days=14))
        db.add(e)
        await db.flush()
        ctrl_enrollments.append(e)

    for tag in pd1_tags:
        e = Enrollment(cohort_id=cohort_pd1.id, mouse_id=mouse_ids[tag], enrolled_at=today - timedelta(days=14))
        db.add(e)
        await db.flush()
        pd1_enrollments.append(e)

    measurement_days_2 = [0, 3, 7, 10, 14]
    random.seed(123)

    for enr in ctrl_enrollments:
        base_weight = random.uniform(21.0, 24.0)
        for day in measurement_days_2:
            tumor_l = round(max(0.5, random.gauss(2.0 + day * 0.25, 0.4)), 1)
            tumor_w = round(max(0.3, tumor_l * random.uniform(0.6, 0.8)), 1)
            vol = round(tumor_l * tumor_w * tumor_w * 0.5, 1)
            weight = round(base_weight + random.gauss(-0.1 * day / 14, 0.3), 1)
            db.add(Measurement(
                enrollment_id=enr.id,
                recorded_at=today - timedelta(days=14) + timedelta(days=day),
                tumor_length_mm=tumor_l,
                tumor_width_mm=tumor_w,
                tumor_volume_mm3=vol,
                body_weight_g=weight,
            ))

    for enr in pd1_enrollments:
        base_weight = random.uniform(21.0, 24.0)
        for day in measurement_days_2:
            if day <= 7:
                tumor_l = round(max(0.5, random.gauss(2.0 + day * 0.15, 0.3)), 1)
            else:
                tumor_l = round(max(0.3, random.gauss(2.0 + 7 * 0.15 - (day - 7) * 0.1, 0.3)), 1)
            tumor_w = round(max(0.2, tumor_l * random.uniform(0.6, 0.8)), 1)
            vol = round(tumor_l * tumor_w * tumor_w * 0.5, 1)
            weight = round(base_weight + random.gauss(0.05 * day / 14, 0.2), 1)
            db.add(Measurement(
                enrollment_id=enr.id,
                recorded_at=today - timedelta(days=14) + timedelta(days=day),
                tumor_length_mm=tumor_l,
                tumor_width_mm=tumor_w,
                tumor_volume_mm3=vol,
                body_weight_g=weight,
            ))

    # --- Study 3: Draft study ---
    study3 = Study(
        name="BRCA1 Targeted Therapy PK Study",
        description="Pharmacokinetics evaluation of novel PARP inhibitor in BRCA1 heterozygous model. Planned 6-week study with dose escalation.",
        start_date=today + timedelta(days=7),
        status=StudyStatus.DRAFT,
    )
    db.add(study3)
    await db.flush()

    for name, desc in [
        ("Low Dose (5mg/kg)", "PARP inhibitor 5mg/kg daily oral gavage"),
        ("High Dose (25mg/kg)", "PARP inhibitor 25mg/kg daily oral gavage"),
        ("Vehicle Control", "Methylcellulose vehicle, daily oral gavage"),
    ]:
        db.add(Cohort(study_id=study3.id, name=name, description=desc))

    await db.commit()

    return {
        "message": "Demo data loaded successfully",
        "seeded": True,
        "summary": {
            "genotypes": 4,
            "cages": 6,
            "mice": 25,
            "studies": 3,
            "measurements": 115,
        },
    }
