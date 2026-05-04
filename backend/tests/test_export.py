"""Tests for export endpoints (CSV and XLSX)."""

import csv
import io

import pytest
from httpx import AsyncClient


class TestExportMice:
    async def test_export_mice_csv(self, client: AsyncClient):
        # Create a mouse first
        g = await client.post("/api/v1/colony/genotypes", json={"name": "Export-GT"})
        gid = g.json()["id"]
        c = await client.post(
            "/api/v1/colony/cages",
            json={"label": "Export-C1", "location": "Room", "capacity": 5},
        )
        cid = c.json()["id"]
        await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "EXP-M1",
                "sex": "Male",
                "date_of_birth": "2026-01-01",
                "genotype_id": gid,
                "cage_id": cid,
            },
        )

        r = await client.get("/api/v1/export/mice?format=csv")
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]
        reader = csv.DictReader(io.StringIO(r.text))
        rows = list(reader)
        assert len(rows) >= 1
        assert "ear_tag" in rows[0]
        assert "genotype_name" in rows[0]
        assert any(row["ear_tag"] == "EXP-M1" for row in rows)

    async def test_export_mice_xlsx(self, client: AsyncClient):
        r = await client.get("/api/v1/export/mice?format=xlsx")
        assert r.status_code == 200
        assert "spreadsheetml" in r.headers["content-type"]
        assert len(r.content) > 0


class TestExportCages:
    async def test_export_cages_csv(self, client: AsyncClient):
        await client.post(
            "/api/v1/colony/cages",
            json={"label": "Export-C2", "location": "Room B", "capacity": 3},
        )
        r = await client.get("/api/v1/export/cages?format=csv")
        assert r.status_code == 200
        reader = csv.DictReader(io.StringIO(r.text))
        rows = list(reader)
        assert any(row["label"] == "Export-C2" for row in rows)
        assert "current_occupancy" in rows[0]


class TestExportGenotypes:
    async def test_export_genotypes_csv(self, client: AsyncClient):
        await client.post(
            "/api/v1/colony/genotypes", json={"name": "Export-GT2", "zygosity": "Het"}
        )
        r = await client.get("/api/v1/export/genotypes?format=csv")
        assert r.status_code == 200
        reader = csv.DictReader(io.StringIO(r.text))
        rows = list(reader)
        assert any(row["name"] == "Export-GT2" for row in rows)


class TestExportStudyData:
    async def _setup_study_with_measurement(self, client: AsyncClient):
        g = await client.post("/api/v1/colony/genotypes", json={"name": "ExpS-GT"})
        gid = g.json()["id"]
        c = await client.post(
            "/api/v1/colony/cages",
            json={"label": "ExpS-C1", "location": "R", "capacity": 5},
        )
        cid = c.json()["id"]
        m = await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "ExpS-M1",
                "sex": "Female",
                "date_of_birth": "2026-01-01",
                "genotype_id": gid,
                "cage_id": cid,
            },
        )
        mid = m.json()["id"]
        s = await client.post(
            "/api/v1/studies",
            json={"name": "Export-Study", "start_date": "2026-01-01"},
        )
        sid = s.json()["id"]
        await client.patch(f"/api/v1/studies/{sid}", json={"status": "Active"})
        co = await client.post(
            f"/api/v1/studies/{sid}/cohorts", json={"name": "Exp-Cohort"}
        )
        coid = co.json()["id"]
        enr = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{coid}/enrollments",
            json={"mouse_id": mid},
        )
        eid = enr.json()["id"]
        await client.post(
            f"/api/v1/studies/{sid}/cohorts/{coid}/enrollments/{eid}/measurements",
            json={"tumor_length_mm": 10.0, "tumor_width_mm": 5.0, "body_weight_g": 20.0},
        )
        return sid

    async def test_export_study_measurements_csv(self, client: AsyncClient):
        sid = await self._setup_study_with_measurement(client)
        r = await client.get(f"/api/v1/export/studies/{sid}/measurements?format=csv")
        assert r.status_code == 200
        reader = csv.DictReader(io.StringIO(r.text))
        rows = list(reader)
        assert len(rows) >= 1
        assert rows[0]["study_name"] == "Export-Study"
        assert rows[0]["mouse_ear_tag"] == "ExpS-M1"
        assert "tumor_volume_mm3" in rows[0]

    async def test_export_study_enrollments_csv(self, client: AsyncClient):
        sid = await self._setup_study_with_measurement(client)
        r = await client.get(f"/api/v1/export/studies/{sid}/enrollments?format=csv")
        assert r.status_code == 200
        reader = csv.DictReader(io.StringIO(r.text))
        rows = list(reader)
        assert len(rows) >= 1
        assert rows[0]["cohort_name"] == "Exp-Cohort"

    async def test_export_study_measurements_xlsx(self, client: AsyncClient):
        sid = await self._setup_study_with_measurement(client)
        r = await client.get(f"/api/v1/export/studies/{sid}/measurements?format=xlsx")
        assert r.status_code == 200
        assert "spreadsheetml" in r.headers["content-type"]
