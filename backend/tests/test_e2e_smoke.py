"""End-to-end smoke test: create mouse → enroll in study → record measurement → verify volume."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_workflow(client: AsyncClient):
    # 1. Create a genotype
    resp = await client.post(
        "/api/v1/colony/genotypes",
        json={"name": "WT-C57BL/6", "description": "Wild type", "zygosity": "Homozygous"},
    )
    assert resp.status_code == 201
    genotype_id = resp.json()["id"]

    # 2. Create a cage
    resp = await client.post(
        "/api/v1/colony/cages",
        json={"label": "R1-C01", "location": "Room 1", "capacity": 5},
    )
    assert resp.status_code == 201
    cage_id = resp.json()["id"]

    # 3. Create a mouse
    resp = await client.post(
        "/api/v1/colony/mice",
        json={
            "ear_tag": "M-001",
            "sex": "Female",
            "date_of_birth": "2026-01-15",
            "genotype_id": genotype_id,
            "cage_id": cage_id,
        },
    )
    assert resp.status_code == 201
    mouse = resp.json()
    mouse_id = mouse["id"]
    assert mouse["status"] == "Alive"
    assert mouse["ear_tag"] == "M-001"

    # 4. Create a study
    resp = await client.post(
        "/api/v1/studies",
        json={
            "name": "Tumor Growth Pilot",
            "description": "Pilot study for tumor growth kinetics",
            "start_date": "2026-04-01",
        },
    )
    assert resp.status_code == 201
    study_id = resp.json()["id"]
    assert resp.json()["status"] == "Draft"

    # 5. Activate the study
    resp = await client.patch(
        f"/api/v1/studies/{study_id}",
        json={"status": "Active"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "Active"

    # 6. Create a cohort
    resp = await client.post(
        f"/api/v1/studies/{study_id}/cohorts",
        json={"name": "Treatment Group A", "description": "10mg/kg dose"},
    )
    assert resp.status_code == 201
    cohort_id = resp.json()["id"]

    # 7. Enroll mouse in cohort
    resp = await client.post(
        f"/api/v1/studies/{study_id}/cohorts/{cohort_id}/enrollments",
        json={"mouse_id": mouse_id},
    )
    assert resp.status_code == 201
    enrollment_id = resp.json()["id"]
    assert resp.json()["mouse_id"] == mouse_id

    # 8. Record a measurement with tumor dimensions
    resp = await client.post(
        f"/api/v1/studies/{study_id}/cohorts/{cohort_id}/enrollments/{enrollment_id}/measurements",
        json={
            "tumor_length_mm": 10.0,
            "tumor_width_mm": 6.0,
            "body_weight_g": 22.5,
            "notes": "Day 1 baseline",
        },
    )
    assert resp.status_code == 201
    m = resp.json()
    # Volume = Length × Width² / 2 = 10 × 36 / 2 = 180.0
    assert m["tumor_volume_mm3"] == pytest.approx(180.0)
    assert m["body_weight_g"] == 22.5
    assert m["notes"] == "Day 1 baseline"

    # 9. Record a second measurement to confirm history ordering
    resp = await client.post(
        f"/api/v1/studies/{study_id}/cohorts/{cohort_id}/enrollments/{enrollment_id}/measurements",
        json={
            "tumor_length_mm": 12.0,
            "tumor_width_mm": 7.0,
            "body_weight_g": 22.8,
            "notes": "Day 3",
        },
    )
    assert resp.status_code == 201
    m2 = resp.json()
    # Volume = 12 × 49 / 2 = 294.0
    assert m2["tumor_volume_mm3"] == pytest.approx(294.0)

    # 10. Fetch measurement history and verify order
    resp = await client.get(
        f"/api/v1/studies/{study_id}/cohorts/{cohort_id}/enrollments/{enrollment_id}/measurements"
    )
    assert resp.status_code == 200
    measurements = resp.json()
    assert len(measurements) == 2
    assert measurements[0]["notes"] == "Day 1 baseline"
    assert measurements[1]["notes"] == "Day 3"

    # 11. Verify the mouse pedigree endpoint works (no parents set)
    resp = await client.get(f"/api/v1/colony/mice/{mouse_id}/pedigree")
    assert resp.status_code == 200
    pedigree = resp.json()
    assert pedigree["ear_tag"] == "M-001"
