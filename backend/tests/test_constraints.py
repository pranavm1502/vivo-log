"""Tests for 409 Conflict responses on constrained delete operations."""

import pytest
from httpx import AsyncClient


class TestColonyConstraintViolations:
    async def test_delete_genotype_in_use_returns_409(self, client: AsyncClient):
        # Create genotype and mouse using it
        g = await client.post("/api/v1/colony/genotypes", json={"name": "InUse-GT"})
        gid = g.json()["id"]
        c = await client.post(
            "/api/v1/colony/cages",
            json={"label": "C-409-1", "location": "Room", "capacity": 5},
        )
        cid = c.json()["id"]
        await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "M-409-1",
                "sex": "Male",
                "date_of_birth": "2026-01-01",
                "genotype_id": gid,
                "cage_id": cid,
            },
        )
        # Try to delete genotype
        r = await client.delete(f"/api/v1/colony/genotypes/{gid}")
        assert r.status_code == 409
        assert "assigned to one or more mice" in r.json()["detail"]

    async def test_delete_cage_with_mice_returns_409(self, client: AsyncClient):
        g = await client.post("/api/v1/colony/genotypes", json={"name": "CageDel-GT"})
        gid = g.json()["id"]
        c = await client.post(
            "/api/v1/colony/cages",
            json={"label": "C-409-2", "location": "Room", "capacity": 5},
        )
        cid = c.json()["id"]
        await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "M-409-2",
                "sex": "Female",
                "date_of_birth": "2026-01-01",
                "genotype_id": gid,
                "cage_id": cid,
            },
        )
        r = await client.delete(f"/api/v1/colony/cages/{cid}")
        assert r.status_code == 409
        assert "still contains mice" in r.json()["detail"]

    async def test_delete_mouse_as_sire_returns_409(self, client: AsyncClient):
        g = await client.post("/api/v1/colony/genotypes", json={"name": "Sire-GT"})
        gid = g.json()["id"]
        c = await client.post(
            "/api/v1/colony/cages",
            json={"label": "C-409-3", "location": "Room", "capacity": 5},
        )
        cid = c.json()["id"]
        # Create sire
        sire = await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "M-409-SIRE",
                "sex": "Male",
                "date_of_birth": "2026-01-01",
                "genotype_id": gid,
                "cage_id": cid,
            },
        )
        sire_id = sire.json()["id"]
        # Create dam
        dam = await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "M-409-DAM",
                "sex": "Female",
                "date_of_birth": "2026-01-01",
                "genotype_id": gid,
                "cage_id": cid,
            },
        )
        dam_id = dam.json()["id"]
        # Create child with lineage
        child = await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "M-409-CHILD",
                "sex": "Male",
                "date_of_birth": "2026-03-01",
                "genotype_id": gid,
                "cage_id": cid,
            },
        )
        child_id = child.json()["id"]
        await client.put(
            f"/api/v1/colony/mice/{child_id}/lineage",
            json={"sire_id": sire_id, "dam_id": dam_id},
        )
        # Try to delete sire
        r = await client.delete(f"/api/v1/colony/mice/{sire_id}")
        assert r.status_code == 409
        assert "referenced as a parent" in r.json()["detail"]


class TestStudyConstraintViolations:
    async def test_delete_study_with_cohort_enrollments_returns_409(
        self, client: AsyncClient
    ):
        # Create study, activate, add cohort, enroll mouse
        g = await client.post("/api/v1/colony/genotypes", json={"name": "Study409-GT"})
        gid = g.json()["id"]
        c = await client.post(
            "/api/v1/colony/cages",
            json={"label": "C-409-S", "location": "Room", "capacity": 5},
        )
        cid = c.json()["id"]
        m = await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "M-409-S1",
                "sex": "Male",
                "date_of_birth": "2026-01-01",
                "genotype_id": gid,
                "cage_id": cid,
            },
        )
        mid = m.json()["id"]
        s = await client.post(
            "/api/v1/studies",
            json={"name": "Study-409", "start_date": "2026-01-01"},
        )
        sid = s.json()["id"]
        await client.patch(f"/api/v1/studies/{sid}", json={"status": "Active"})
        co = await client.post(
            f"/api/v1/studies/{sid}/cohorts", json={"name": "Cohort-409"}
        )
        coid = co.json()["id"]
        await client.post(
            f"/api/v1/studies/{sid}/cohorts/{coid}/enrollments",
            json={"mouse_id": mid},
        )
        # Try to delete study
        r = await client.delete(f"/api/v1/studies/{sid}")
        assert r.status_code == 409
        assert "active enrollments" in r.json()["detail"]

    async def test_delete_cohort_with_enrollments_returns_409(
        self, client: AsyncClient
    ):
        g = await client.post(
            "/api/v1/colony/genotypes", json={"name": "Cohort409-GT"}
        )
        gid = g.json()["id"]
        c = await client.post(
            "/api/v1/colony/cages",
            json={"label": "C-409-C", "location": "Room", "capacity": 5},
        )
        cid = c.json()["id"]
        m = await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "M-409-C1",
                "sex": "Female",
                "date_of_birth": "2026-01-01",
                "genotype_id": gid,
                "cage_id": cid,
            },
        )
        mid = m.json()["id"]
        s = await client.post(
            "/api/v1/studies",
            json={"name": "Study-409-C", "start_date": "2026-01-01"},
        )
        sid = s.json()["id"]
        await client.patch(f"/api/v1/studies/{sid}", json={"status": "Active"})
        co = await client.post(
            f"/api/v1/studies/{sid}/cohorts", json={"name": "Cohort-409-C"}
        )
        coid = co.json()["id"]
        await client.post(
            f"/api/v1/studies/{sid}/cohorts/{coid}/enrollments",
            json={"mouse_id": mid},
        )
        # Try to delete cohort
        r = await client.delete(f"/api/v1/studies/{sid}/cohorts/{coid}")
        assert r.status_code == 409
        assert "has enrollments" in r.json()["detail"]
