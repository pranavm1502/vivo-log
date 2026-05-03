#!/usr/bin/env python3
"""Seed the database with test data for visualization."""

import httpx
import sys

BASE = "http://localhost:8000/api/v1"


def main():
    c = httpx.Client(base_url=BASE, timeout=10)

    # Check API is up
    r = c.get("/../../health")
    if r.status_code != 200:
        print("Backend not running. Start it first with ./start.sh")
        sys.exit(1)

    # Clean existing test data first
    print("Cleaning existing test data...")
    import subprocess
    subprocess.run([
        "docker", "exec", "vivo-log-db-1", "psql", "-U", "postgres", "-d", "vivolog", "-c",
        "TRUNCATE measurements, enrollments, cohorts, studies, mice, cages, genotypes RESTART IDENTITY CASCADE;"
    ], check=True, capture_output=True)

    print("Seeding test data...")

    # ── Genotypes ────────────────────────────────────────────────
    genotypes = []
    for name, desc, zyg in [
        ("Test-WT-C57BL/6", "Wild type control", "Homozygous"),
        ("Test-BRCA1-KO", "BRCA1 knockout", "Heterozygous"),
        ("Test-P53-Mut", "P53 point mutation", "Hemizygous"),
    ]:
        r = c.post("/colony/genotypes", json={"name": name, "description": desc, "zygosity": zyg})
        genotypes.append(r.json())
        print(f"  Genotype: {name}")

    # ── Cages ────────────────────────────────────────────────────
    cages = []
    for label, loc, cap in [
        ("Test-R1-A01", "Room 1, Rack A", 5),
        ("Test-R1-A02", "Room 1, Rack A", 5),
        ("Test-R1-B01", "Room 1, Rack B", 4),
        ("Test-R2-A01", "Room 2, Rack A", 5),
    ]:
        r = c.post("/colony/cages", json={"label": label, "location": loc, "capacity": cap})
        cages.append(r.json())
        print(f"  Cage: {label}")

    # ── Mice ─────────────────────────────────────────────────────
    mice_data = [
        ("Test-M001", "Male",   "2025-10-01", 0, 0),
        ("Test-M002", "Female", "2025-10-05", 0, 0),
        ("Test-M003", "Male",   "2025-11-12", 1, 1),
        ("Test-M004", "Female", "2025-11-12", 1, 1),
        ("Test-M005", "Male",   "2025-12-20", 2, 2),
        ("Test-M006", "Female", "2025-12-20", 0, 2),
        ("Test-M007", "Male",   "2026-01-15", 1, 3),
        ("Test-M008", "Female", "2026-01-15", 2, 3),
        ("Test-M009", "Male",   "2026-02-01", 0, 0),
        ("Test-M010", "Female", "2026-02-01", 1, 1),
    ]
    mice = []
    for tag, sex, dob, geno_idx, cage_idx in mice_data:
        r = c.post("/colony/mice", json={
            "ear_tag": tag,
            "sex": sex,
            "date_of_birth": dob,
            "genotype_id": genotypes[geno_idx]["id"],
            "cage_id": cages[cage_idx]["id"],
        })
        mice.append(r.json())
        print(f"  Mouse: {tag} ({sex})")

    # Set lineage: M003 & M004 are offspring of M001 (sire) and M002 (dam)
    for child_idx in [2, 3]:
        c.put(f"/colony/mice/{mice[child_idx]['id']}/lineage",
              json={"sire_id": mice[0]["id"], "dam_id": mice[1]["id"]})
    # M007 & M008 are offspring of M003 (sire) and M004 (dam)
    for child_idx in [6, 7]:
        c.put(f"/colony/mice/{mice[child_idx]['id']}/lineage",
              json={"sire_id": mice[2]["id"], "dam_id": mice[3]["id"]})
    print("  Lineage: M001×M002 → M003,M004 | M003×M004 → M007,M008")

    # Cull one mouse for variety
    c.patch(f"/colony/mice/{mice[4]['id']}", json={"status": "Culled"})
    print("  Status: Test-M005 → Culled")

    # ── Study ────────────────────────────────────────────────────
    r = c.post("/studies", json={
        "name": "Test-Tumor-Growth-Pilot",
        "description": "Pilot study tracking subcutaneous tumor growth in treated vs control mice",
        "start_date": "2026-03-01",
    })
    study = r.json()
    print(f"  Study: {study['name']}")

    # Activate
    c.patch(f"/studies/{study['id']}", json={"status": "Active"})

    # Cohorts
    r = c.post(f"/studies/{study['id']}/cohorts", json={
        "name": "Test-Treatment-10mg",
        "description": "10mg/kg dose, 3x weekly",
    })
    cohort_tx = r.json()

    r = c.post(f"/studies/{study['id']}/cohorts", json={
        "name": "Test-Vehicle-Control",
        "description": "Vehicle only control group",
    })
    cohort_ctrl = r.json()
    print(f"  Cohorts: {cohort_tx['name']}, {cohort_ctrl['name']}")

    # Enroll mice (only Alive ones)
    enrollments = []
    # Treatment: M003, M006, M009
    for m_idx in [2, 5, 8]:
        r = c.post(f"/studies/{study['id']}/cohorts/{cohort_tx['id']}/enrollments",
                    json={"mouse_id": mice[m_idx]["id"]})
        enrollments.append(("tx", r.json()))
    # Control: M004, M008, M010
    for m_idx in [3, 7, 9]:
        r = c.post(f"/studies/{study['id']}/cohorts/{cohort_ctrl['id']}/enrollments",
                    json={"mouse_id": mice[m_idx]["id"]})
        enrollments.append(("ctrl", r.json()))
    print(f"  Enrolled: 3 treatment + 3 control mice")

    # ── Measurements (simulating 3 timepoints) ──────────────────
    import random
    random.seed(42)

    timepoints = [
        ("2026-03-01", 3.0),   # baseline, small tumors
        ("2026-03-08", 6.0),   # week 1
        ("2026-03-15", 10.0),  # week 2
    ]

    for group, enrollment in enrollments:
        cohort_id = cohort_tx["id"] if group == "tx" else cohort_ctrl["id"]
        base_length = 3.0
        for day_label, time_factor in timepoints:
            if group == "tx":
                # Treatment: slower growth
                length = base_length + time_factor * 0.5 + random.uniform(-0.5, 0.5)
                width = length * 0.7 + random.uniform(-0.3, 0.3)
            else:
                # Control: faster growth
                length = base_length + time_factor * 1.2 + random.uniform(-0.5, 0.5)
                width = length * 0.75 + random.uniform(-0.3, 0.3)

            weight = 22.0 + random.uniform(-1.5, 1.5)

            c.post(
                f"/studies/{study['id']}/cohorts/{cohort_id}/enrollments/{enrollment['id']}/measurements",
                json={
                    "tumor_length_mm": round(length, 1),
                    "tumor_width_mm": round(width, 1),
                    "body_weight_g": round(weight, 1),
                    "notes": f"Timepoint {day_label}",
                },
            )
    print(f"  Measurements: 3 timepoints × 6 mice = 18 records")

    # ── Second study (Draft) for variety ─────────────────────────
    c.post("/studies", json={
        "name": "Test-Combination-Therapy",
        "description": "Phase 2: combination of Drug A + Drug B",
        "start_date": "2026-05-01",
    })
    print("  Study: Test-Combination-Therapy (Draft)")

    print("\nDone! Restart the Flutter app to see the data.")


if __name__ == "__main__":
    main()
