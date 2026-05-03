"""Tests for colony CRUD operations (5.1), lineage validation (5.2),
cage capacity (5.3), and genotype filter (part of 5.1)."""

import pytest
from httpx import AsyncClient


# ── 5.1  Colony CRUD ────────────────────────────────────────────────

class TestGenotypeCRUD:
    async def test_create_genotype(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/colony/genotypes",
            json={"name": "BRCA1-KO", "zygosity": "Homozygous"},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "BRCA1-KO"
        assert data["zygosity"] == "Homozygous"

    async def test_list_genotypes(self, client: AsyncClient):
        await client.post("/api/v1/colony/genotypes", json={"name": "TP53-KO"})
        r = await client.get("/api/v1/colony/genotypes")
        assert r.status_code == 200
        assert any(g["name"] == "TP53-KO" for g in r.json())

    async def test_update_genotype(self, client: AsyncClient):
        r = await client.post("/api/v1/colony/genotypes", json={"name": "MYC-OE"})
        gid = r.json()["id"]
        r2 = await client.patch(
            f"/api/v1/colony/genotypes/{gid}",
            json={"description": "Overexpression model"},
        )
        assert r2.status_code == 200
        assert r2.json()["description"] == "Overexpression model"

    async def test_delete_genotype(self, client: AsyncClient):
        r = await client.post("/api/v1/colony/genotypes", json={"name": "DEL-TEST"})
        gid = r.json()["id"]
        r2 = await client.delete(f"/api/v1/colony/genotypes/{gid}")
        assert r2.status_code == 204


class TestCageCRUD:
    async def test_create_cage(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/colony/cages",
            json={"label": "C-101", "location": "Room A", "capacity": 5},
        )
        assert r.status_code == 201
        assert r.json()["capacity"] == 5

    async def test_list_cages(self, client: AsyncClient):
        await client.post("/api/v1/colony/cages", json={"label": "C-201"})
        r = await client.get("/api/v1/colony/cages")
        assert r.status_code == 200
        assert len(r.json()) >= 1


class TestMouseCRUD:
    async def test_create_mouse(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "M-001",
                "sex": "Female",
                "date_of_birth": "2026-01-15",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert data["ear_tag"] == "M-001"
        assert data["status"] == "Alive"

    async def test_update_mouse_status(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/colony/mice",
            json={"ear_tag": "M-002", "sex": "Male", "date_of_birth": "2026-01-10"},
        )
        mid = r.json()["id"]
        r2 = await client.patch(
            f"/api/v1/colony/mice/{mid}", json={"status": "Deceased"}
        )
        assert r2.status_code == 200
        assert r2.json()["status"] == "Deceased"

    async def test_reject_invalid_status(self, client: AsyncClient):
        r = await client.post(
            "/api/v1/colony/mice",
            json={"ear_tag": "M-003", "sex": "Female", "date_of_birth": "2026-02-01"},
        )
        mid = r.json()["id"]
        r2 = await client.patch(
            f"/api/v1/colony/mice/{mid}", json={"status": "Unknown"}
        )
        assert r2.status_code == 422

    async def test_list_mice_filter_by_genotype(self, client: AsyncClient):
        """5.1 + 3.7 — filter mice by genotype_id."""
        gr = await client.post("/api/v1/colony/genotypes", json={"name": "FILTER-G"})
        gid = gr.json()["id"]
        await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "M-FG1",
                "sex": "Male",
                "date_of_birth": "2026-01-01",
                "genotype_id": gid,
            },
        )
        await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "M-FG2",
                "sex": "Female",
                "date_of_birth": "2026-01-01",
            },
        )
        r = await client.get(f"/api/v1/colony/mice?genotype_id={gid}")
        assert r.status_code == 200
        assert all(m["genotype_id"] == gid for m in r.json())


# ── 5.2  Lineage validation ─────────────────────────────────────────

class TestLineageValidation:
    async def _make_mouse(self, client, ear_tag, sex):
        r = await client.post(
            "/api/v1/colony/mice",
            json={"ear_tag": ear_tag, "sex": sex, "date_of_birth": "2026-01-01"},
        )
        return r.json()["id"]

    async def test_assign_lineage(self, client: AsyncClient):
        sire = await self._make_mouse(client, "SIRE-1", "Male")
        dam = await self._make_mouse(client, "DAM-1", "Female")
        child = await self._make_mouse(client, "CHILD-1", "Female")
        r = await client.put(
            f"/api/v1/colony/mice/{child}/lineage",
            json={"sire_id": sire, "dam_id": dam},
        )
        assert r.status_code == 200
        assert r.json()["sire_id"] == sire
        assert r.json()["dam_id"] == dam

    async def test_reject_female_sire(self, client: AsyncClient):
        female = await self._make_mouse(client, "F-SIRE", "Female")
        child = await self._make_mouse(client, "CHILD-FS", "Male")
        r = await client.put(
            f"/api/v1/colony/mice/{child}/lineage", json={"sire_id": female}
        )
        assert r.status_code == 400
        assert "male" in r.json()["detail"].lower()

    async def test_reject_male_dam(self, client: AsyncClient):
        male = await self._make_mouse(client, "M-DAM", "Male")
        child = await self._make_mouse(client, "CHILD-MD", "Female")
        r = await client.put(
            f"/api/v1/colony/mice/{child}/lineage", json={"dam_id": male}
        )
        assert r.status_code == 400
        assert "female" in r.json()["detail"].lower()


# ── 5.3  Cage capacity ──────────────────────────────────────────────

class TestCageCapacity:
    async def test_assign_mouse_to_cage(self, client: AsyncClient):
        cr = await client.post(
            "/api/v1/colony/cages", json={"label": "CAP-1", "capacity": 2}
        )
        cage_id = cr.json()["id"]
        mr = await client.post(
            "/api/v1/colony/mice",
            json={"ear_tag": "CAP-M1", "sex": "Male", "date_of_birth": "2026-01-01"},
        )
        mid = mr.json()["id"]
        r = await client.put(
            f"/api/v1/colony/mice/{mid}/cage", json={"cage_id": cage_id}
        )
        assert r.status_code == 200
        assert r.json()["cage_id"] == cage_id

    async def test_reject_over_capacity(self, client: AsyncClient):
        cr = await client.post(
            "/api/v1/colony/cages", json={"label": "CAP-FULL", "capacity": 1}
        )
        cage_id = cr.json()["id"]
        m1 = await client.post(
            "/api/v1/colony/mice",
            json={"ear_tag": "CF-M1", "sex": "Male", "date_of_birth": "2026-01-01"},
        )
        await client.put(
            f"/api/v1/colony/mice/{m1.json()['id']}/cage",
            json={"cage_id": cage_id},
        )
        m2 = await client.post(
            "/api/v1/colony/mice",
            json={"ear_tag": "CF-M2", "sex": "Female", "date_of_birth": "2026-01-01"},
        )
        r = await client.put(
            f"/api/v1/colony/mice/{m2.json()['id']}/cage",
            json={"cage_id": cage_id},
        )
        assert r.status_code == 409
        assert "capacity" in r.json()["detail"].lower()

    async def test_transfer_between_cages(self, client: AsyncClient):
        c1 = await client.post(
            "/api/v1/colony/cages", json={"label": "XFER-A", "capacity": 2}
        )
        c2 = await client.post(
            "/api/v1/colony/cages", json={"label": "XFER-B", "capacity": 2}
        )
        mr = await client.post(
            "/api/v1/colony/mice",
            json={
                "ear_tag": "XFER-M1",
                "sex": "Male",
                "date_of_birth": "2026-01-01",
            },
        )
        mid = mr.json()["id"]
        await client.put(
            f"/api/v1/colony/mice/{mid}/cage",
            json={"cage_id": c1.json()["id"]},
        )
        r = await client.put(
            f"/api/v1/colony/mice/{mid}/cage",
            json={"cage_id": c2.json()["id"]},
        )
        assert r.status_code == 200
        assert r.json()["cage_id"] == c2.json()["id"]
