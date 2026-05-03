"""Tests for study/cohort CRUD (5.4), enrollment eligibility (5.5),
tumor volume calculation (5.6), and measurement validation (5.7)."""

import pytest
from httpx import AsyncClient


# ── Helpers ──────────────────────────────────────────────────────────

async def _create_mouse(client: AsyncClient, ear_tag: str, sex: str = "Male") -> int:
    r = await client.post(
        "/api/v1/colony/mice",
        json={"ear_tag": ear_tag, "sex": sex, "date_of_birth": "2026-01-01"},
    )
    assert r.status_code == 201
    return r.json()["id"]


async def _create_active_study(client: AsyncClient, name: str) -> int:
    r = await client.post(
        "/api/v1/studies",
        json={"name": name, "start_date": "2026-03-01"},
    )
    sid = r.json()["id"]
    await client.patch(f"/api/v1/studies/{sid}", json={"status": "Active"})
    return sid


async def _create_cohort(client: AsyncClient, study_id: int, name: str) -> int:
    r = await client.post(
        f"/api/v1/studies/{study_id}/cohorts", json={"name": name}
    )
    return r.json()["id"]


# ── 5.4  Study & Cohort CRUD ────────────────────────────────────────

class TestStudyCRUD:
    async def test_create_study_draft(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/studies",
            json={"name": "Efficacy Study", "start_date": "2026-03-01"},
        )
        assert r.status_code == 201
        assert r.json()["status"] == "Draft"

    async def test_activate_study(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/studies",
            json={"name": "Activate Test", "start_date": "2026-03-01"},
        )
        sid = r.json()["id"]
        r2 = await client.patch(
            f"/api/v1/studies/{sid}", json={"status": "Active"}
        )
        assert r2.status_code == 200
        assert r2.json()["status"] == "Active"

    async def test_create_cohort(self, client: AsyncClient):
        sid = await _create_active_study(client, "Cohort Test Study")
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts",
            json={"name": "Vehicle Control"},
        )
        assert r.status_code == 201
        assert r.json()["name"] == "Vehicle Control"

    async def test_list_cohorts(self, client: AsyncClient):
        sid = await _create_active_study(client, "List Cohort Study")
        await client.post(
            f"/api/v1/studies/{sid}/cohorts", json={"name": "Arm A"}
        )
        await client.post(
            f"/api/v1/studies/{sid}/cohorts", json={"name": "Arm B"}
        )
        r = await client.get(f"/api/v1/studies/{sid}/cohorts")
        assert r.status_code == 200
        assert len(r.json()) == 2

    async def test_reject_enrollment_in_draft_study(self, client: AsyncClient):
        """Study must be Active for enrollment."""
        r = await client.post(
            "/api/v1/studies",
            json={"name": "Draft Block", "start_date": "2026-03-01"},
        )
        sid = r.json()["id"]
        cr = await client.post(
            f"/api/v1/studies/{sid}/cohorts", json={"name": "Draft Cohort"}
        )
        cid = cr.json()["id"]
        mid = await _create_mouse(client, "DRAFT-M")
        r2 = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments",
            json={"mouse_id": mid},
        )
        assert r2.status_code == 409
        assert "Active" in r2.json()["detail"]


# ── 5.5  Enrollment eligibility ─────────────────────────────────────

class TestEnrollmentEligibility:
    async def test_enroll_alive_mouse(self, client: AsyncClient):
        sid = await _create_active_study(client, "Alive Enroll")
        cid = await _create_cohort(client, sid, "Control")
        mid = await _create_mouse(client, "ALIVE-E1")
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments",
            json={"mouse_id": mid},
        )
        assert r.status_code == 201
        assert r.json()["mouse_id"] == mid

    async def test_reject_deceased_mouse(self, client: AsyncClient):
        sid = await _create_active_study(client, "Deceased Reject")
        cid = await _create_cohort(client, sid, "Control")
        mid = await _create_mouse(client, "DEAD-E1")
        await client.patch(f"/api/v1/colony/mice/{mid}", json={"status": "Deceased"})
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments",
            json={"mouse_id": mid},
        )
        assert r.status_code == 409
        assert "Deceased" in r.json()["detail"]

    async def test_reject_culled_mouse(self, client: AsyncClient):
        sid = await _create_active_study(client, "Culled Reject")
        cid = await _create_cohort(client, sid, "Treatment")
        mid = await _create_mouse(client, "CULL-E1")
        await client.patch(f"/api/v1/colony/mice/{mid}", json={"status": "Culled"})
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments",
            json={"mouse_id": mid},
        )
        assert r.status_code == 409
        assert "Culled" in r.json()["detail"]

    async def test_remove_enrollment(self, client: AsyncClient):
        sid = await _create_active_study(client, "Remove Enroll")
        cid = await _create_cohort(client, sid, "Control")
        mid = await _create_mouse(client, "REM-E1")
        er = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments",
            json={"mouse_id": mid},
        )
        eid = er.json()["id"]
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/remove",
            json={"removal_reason": "Reached humane endpoint"},
        )
        assert r.status_code == 200
        assert r.json()["removed_at"] is not None
        assert r.json()["removal_reason"] == "Reached humane endpoint"


# ── 5.6  Tumor volume calculation ───────────────────────────────────

class TestTumorVolume:
    async def _setup_enrollment(self, client: AsyncClient, tag: str) -> tuple[int, int, int]:
        sid = await _create_active_study(client, f"TV-{tag}")
        cid = await _create_cohort(client, sid, "Control")
        mid = await _create_mouse(client, f"TV-{tag}")
        er = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments",
            json={"mouse_id": mid},
        )
        return sid, cid, er.json()["id"]

    async def test_volume_calculated(self, client: AsyncClient):
        sid, cid, eid = await self._setup_enrollment(client, "CALC")
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/measurements",
            json={"tumor_length_mm": 12.5, "tumor_width_mm": 8.3},
        )
        assert r.status_code == 201
        # Volume = 12.5 * 8.3^2 / 2 = 430.5625
        assert abs(r.json()["tumor_volume_mm3"] - 430.5625) < 0.001

    async def test_volume_null_no_width(self, client: AsyncClient):
        sid, cid, eid = await self._setup_enrollment(client, "NOWIDTH")
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/measurements",
            json={"tumor_length_mm": 12.5},
        )
        assert r.status_code == 201
        assert r.json()["tumor_volume_mm3"] is None

    async def test_volume_null_no_length(self, client: AsyncClient):
        sid, cid, eid = await self._setup_enrollment(client, "NOLEN")
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/measurements",
            json={"tumor_width_mm": 8.3},
        )
        assert r.status_code == 201
        assert r.json()["tumor_volume_mm3"] is None


# ── 5.7  Measurement validation ─────────────────────────────────────

class TestMeasurementValidation:
    async def _setup_enrollment(self, client: AsyncClient, tag: str) -> tuple[int, int, int]:
        sid = await _create_active_study(client, f"MV-{tag}")
        cid = await _create_cohort(client, sid, "Control")
        mid = await _create_mouse(client, f"MV-{tag}")
        er = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments",
            json={"mouse_id": mid},
        )
        return sid, cid, er.json()["id"]

    async def test_record_complete_measurement(self, client: AsyncClient):
        sid, cid, eid = await self._setup_enrollment(client, "COMP")
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/measurements",
            json={
                "tumor_length_mm": 10.0,
                "tumor_width_mm": 5.0,
                "body_weight_g": 22.1,
            },
        )
        assert r.status_code == 201
        assert r.json()["body_weight_g"] == 22.1

    async def test_record_body_weight_only(self, client: AsyncClient):
        sid, cid, eid = await self._setup_enrollment(client, "BWONLY")
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/measurements",
            json={"body_weight_g": 21.8},
        )
        assert r.status_code == 201
        assert r.json()["tumor_length_mm"] is None
        assert r.json()["tumor_width_mm"] is None

    async def test_reject_negative_length(self, client: AsyncClient):
        sid, cid, eid = await self._setup_enrollment(client, "NEGLEN")
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/measurements",
            json={"tumor_length_mm": -5.0},
        )
        assert r.status_code == 422

    async def test_reject_negative_weight(self, client: AsyncClient):
        sid, cid, eid = await self._setup_enrollment(client, "NEGWT")
        r = await client.post(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/measurements",
            json={"body_weight_g": -1.0},
        )
        assert r.status_code == 422

    async def test_measurement_history_ordered(self, client: AsyncClient):
        sid, cid, eid = await self._setup_enrollment(client, "HIST")
        for i in range(3):
            await client.post(
                f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/measurements",
                json={"body_weight_g": 20.0 + i},
            )
        r = await client.get(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/measurements"
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 3
        timestamps = [m["recorded_at"] for m in data]
        assert timestamps == sorted(timestamps)

    async def test_measurement_history_empty(self, client: AsyncClient):
        sid, cid, eid = await self._setup_enrollment(client, "EMPTY")
        r = await client.get(
            f"/api/v1/studies/{sid}/cohorts/{cid}/enrollments/{eid}/measurements"
        )
        assert r.status_code == 200
        assert r.json() == []
