"""Tests for new endpoints: cohort update and measurement delete."""

import pytest
from httpx import AsyncClient


class TestCohortUpdate:
    async def test_update_cohort_name(self, client: AsyncClient):
        # Create study and cohort
        s = await client.post(
            "/api/v1/studies",
            json={"name": "CU-Study", "start_date": "2026-01-01"},
        )
        sid = s.json()["id"]
        co = await client.post(
            f"/api/v1/studies/{sid}/cohorts", json={"name": "Original"}
        )
        coid = co.json()["id"]

        r = await client.patch(
            f"/api/v1/studies/{sid}/cohorts/{coid}", json={"name": "Updated"}
        )
        assert r.status_code == 200
        assert r.json()["name"] == "Updated"

    async def test_update_cohort_not_found(self, client: AsyncClient):
        s = await client.post(
            "/api/v1/studies",
            json={"name": "CU-Study-2", "start_date": "2026-01-01"},
        )
        sid = s.json()["id"]
        r = await client.patch(
            f"/api/v1/studies/{sid}/cohorts/9999", json={"name": "X"}
        )
        assert r.status_code == 404


class TestMeasurementDelete:
    async def test_delete_measurement(self, client: AsyncClient):
        # Setup: study, cohort, mouse, enrollment, measurement
        g = await client.post("/api/v1/colony/genotypes", json={"name": "MD-GT"})
        gid = g.json()["id"]
        c = await client.post(
            "/api/v1/colony/cages",
            json={"label": "MD-Cage", "location": "Room", "capacity": 5},
        )
        cid = c.json()["id"]
        m = await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "MD-M1",
                "sex": "Male",
                "date_of_birth": "2026-01-01",
                "genotype_id": gid,
                "cage_id": cid,
            },
        )
        mid = m.json()["id"]

        s = await client.post(
            "/api/v1/studies",
            json={"name": "MD-Study", "start_date": "2026-01-01"},
        )
        sid = s.json()["id"]
        await client.patch(f"/api/v1/studies/{sid}", json={"status": "Active"})
        co = await client.post(
            f"/api/v1/studies/{sid}/cohorts", json={"name": "MD-Cohort"}
        )
        coid = co.json()["id"]
        enr = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{coid}/enrollments",
            json={"mouse_id": mid},
        )
        eid = enr.json()["id"]

        # Create measurement
        meas = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{coid}/enrollments/{eid}/measurements",
            json={"tumor_length_mm": 10.0, "tumor_width_mm": 5.0, "body_weight_g": 20.0},
        )
        meas_id = meas.json()["id"]

        # Delete measurement
        r = await client.delete(
            f"/api/v1/studies/{sid}/cohorts/{coid}/enrollments/{eid}/measurements/{meas_id}"
        )
        assert r.status_code == 204

        # Verify it's gone
        r2 = await client.get(
            f"/api/v1/studies/{sid}/cohorts/{coid}/enrollments/{eid}/measurements"
        )
        assert all(ms["id"] != meas_id for ms in r2.json())

    async def test_delete_measurement_not_found(self, client: AsyncClient):
        # Create minimal study setup
        s = await client.post(
            "/api/v1/studies",
            json={"name": "MD-Study-2", "start_date": "2026-01-01"},
        )
        sid = s.json()["id"]
        await client.patch(f"/api/v1/studies/{sid}", json={"status": "Active"})
        co = await client.post(
            f"/api/v1/studies/{sid}/cohorts", json={"name": "MD-Cohort-2"}
        )
        coid = co.json()["id"]

        r = await client.delete(
            f"/api/v1/studies/{sid}/cohorts/{coid}/enrollments/1/measurements/9999"
        )
        assert r.status_code == 404
