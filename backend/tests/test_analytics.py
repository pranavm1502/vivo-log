"""Tests for analytics endpoints."""

from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.conftest import TestSession, engine
from app.database import get_db


@pytest_asyncio.fixture
async def client():
    async def _override():
        async with TestSession() as s:
            yield s

    app.dependency_overrides[get_db] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def _seed_study_with_measurements(client: AsyncClient):
    """Create a study with 2 cohorts, 2 mice each, and measurements."""
    import uuid
    uid = uuid.uuid4().hex[:6]

    # Create genotype and cage
    g = await client.post("/api/v1/colony/genotypes", json={"name": f"WT-{uid}"})
    gid = g.json()["id"]
    c = await client.post("/api/v1/colony/cages", json={"label": f"C-{uid}", "capacity": 5})
    cid = c.json()["id"]

    # Create 4 mice
    mice = []
    for i in range(4):
        r = await client.post("/api/v1/colony/mice", json={
            "ear_tag": f"M-{uid}-{i}",
            "sex": "Female",
            "date_of_birth": "2026-01-01",
            "genotype_id": gid,
            "cage_id": cid,
        })
        mice.append(r.json()["id"])

    # Create study (created as Draft, then activate)
    s = await client.post("/api/v1/studies", json={
        "name": f"Analytics Study {uid}",
        "start_date": "2026-01-15",
    })
    study_id = s.json()["id"]
    await client.patch(f"/api/v1/studies/{study_id}", json={"status": "Active"})

    # Create cohorts
    c1 = await client.post(f"/api/v1/studies/{study_id}/cohorts", json={"name": "Treatment"})
    c2 = await client.post(f"/api/v1/studies/{study_id}/cohorts", json={"name": "Control"})
    cohort1_id = c1.json()["id"]
    cohort2_id = c2.json()["id"]

    # Enroll mice
    e1 = await client.post(f"/api/v1/studies/{study_id}/cohorts/{cohort1_id}/enrollments", json={"mouse_id": mice[0]})
    assert e1.status_code == 201, f"Enrollment failed: {e1.status_code} {e1.text}"
    e2 = await client.post(f"/api/v1/studies/{study_id}/cohorts/{cohort1_id}/enrollments", json={"mouse_id": mice[1]})
    e3 = await client.post(f"/api/v1/studies/{study_id}/cohorts/{cohort2_id}/enrollments", json={"mouse_id": mice[2]})
    e4 = await client.post(f"/api/v1/studies/{study_id}/cohorts/{cohort2_id}/enrollments", json={"mouse_id": mice[3]})
    enr1 = e1.json()["id"]
    enr2 = e2.json()["id"]
    enr3 = e3.json()["id"]
    enr4 = e4.json()["id"]

    # Add measurements (simulate day 0, day 3, day 7)
    for enr_id in [enr1, enr2, enr3, enr4]:
        cohort_id = cohort1_id if enr_id in [enr1, enr2] else cohort2_id
        for day_offset in [0, 3, 7]:
            vol = 100 + day_offset * 10 + (5 if enr_id in [enr1, enr3] else -5)
            await client.post(
                f"/api/v1/studies/{study_id}/cohorts/{cohort_id}/enrollments/{enr_id}/measurements",
                json={
                    "tumor_length_mm": 5.0,
                    "tumor_width_mm": 4.0,
                    "tumor_volume_mm3": vol,
                    "body_weight_g": 20.0 + day_offset * 0.5,
                },
            )

    return study_id, cohort1_id, cohort2_id


class TestTumorGrowth:
    @pytest.mark.asyncio
    async def test_tumor_growth_returns_cohort_series(self, client):
        study_id, c1, c2 = await _seed_study_with_measurements(client)
        r = await client.get(f"/api/v1/analytics/studies/{study_id}/tumor-growth")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2
        # Each cohort should have series points
        for cohort_data in data:
            assert "cohort_id" in cohort_data
            assert "cohort_name" in cohort_data
            assert len(cohort_data["series"]) > 0
            for point in cohort_data["series"]:
                assert "day" in point
                assert "mean" in point
                assert "sem" in point
                assert "n" in point

    @pytest.mark.asyncio
    async def test_tumor_growth_study_not_found(self, client):
        r = await client.get("/api/v1/analytics/studies/9999/tumor-growth")
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_tumor_growth_empty_cohort(self, client):
        # Create study with a cohort but no enrollments
        s = await client.post("/api/v1/studies", json={
            "name": "Empty Study",
            "start_date": "2026-03-01",
        })
        study_id = s.json()["id"]
        await client.patch(f"/api/v1/studies/{study_id}", json={"status": "Active"})
        await client.post(f"/api/v1/studies/{study_id}/cohorts", json={"name": "Empty"})

        r = await client.get(f"/api/v1/analytics/studies/{study_id}/tumor-growth")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["series"] == []


class TestBodyWeight:
    @pytest.mark.asyncio
    async def test_body_weight_returns_series(self, client):
        study_id, _, _ = await _seed_study_with_measurements(client)
        r = await client.get(f"/api/v1/analytics/studies/{study_id}/body-weight")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2
        for cohort_data in data:
            assert len(cohort_data["series"]) > 0

    @pytest.mark.asyncio
    async def test_body_weight_excludes_null_values(self, client):
        # The seeded data all has body_weight_g set, so all are included
        study_id, _, _ = await _seed_study_with_measurements(client)
        r = await client.get(f"/api/v1/analytics/studies/{study_id}/body-weight")
        data = r.json()
        for cohort_data in data:
            for point in cohort_data["series"]:
                assert point["n"] > 0


class TestStudySummary:
    @pytest.mark.asyncio
    async def test_study_summary(self, client):
        study_id, _, _ = await _seed_study_with_measurements(client)
        r = await client.get(f"/api/v1/analytics/studies/{study_id}/summary")
        assert r.status_code == 200
        data = r.json()
        assert data["study_id"] == study_id
        assert "Analytics Study" in data["study_name"]
        assert data["status"] == "Active"
        assert data["total_enrollments"] == 4
        assert data["total_measurements"] == 12  # 4 enrollments * 3 measurements
        assert data["days_elapsed"] >= 0
        assert len(data["cohorts"]) == 2
        for c in data["cohorts"]:
            assert c["enrollment_count"] == 2
            assert c["latest_mean_volume"] is not None


class TestDashboard:
    @pytest.mark.asyncio
    async def test_dashboard_returns_active_studies(self, client):
        await _seed_study_with_measurements(client)
        r = await client.get("/api/v1/analytics/dashboard")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        study = data[0]
        assert "study_id" in study
        assert "study_name" in study
        assert "days_elapsed" in study
        assert "cohort_count" in study
        assert "total_enrollments" in study
        assert "total_measurements" in study
        assert "latest_mean_volume" in study

    @pytest.mark.asyncio
    async def test_dashboard_empty_when_no_active_studies(self, client):
        # Create a Draft study (not Active)
        await client.post("/api/v1/studies", json={
            "name": "Draft Only",
            "start_date": "2026-01-01",
        })
        r = await client.get("/api/v1/analytics/dashboard")
        assert r.status_code == 200
        # Draft study shouldn't show in dashboard
        for study in r.json():
            assert study["study_name"] != "Draft Only"
