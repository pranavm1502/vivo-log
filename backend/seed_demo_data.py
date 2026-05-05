"""Seed the database with realistic demo data for showcasing all features.

Usage:
    python seed_demo_data.py [--base-url http://127.0.0.1:8000]

This populates the app with:
- Genotypes (WT, p53-/-, BRCA1+/-, HER2-OE)
- Cages with mice
- A completed tumor growth study with measurements over 4 weeks
- An active immunotherapy study
- A draft pharmacokinetics study
"""

import argparse
import random
import sys
from datetime import date, timedelta

import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"


def api(method, path, json=None):
    url = f"{BASE_URL}{path}"
    resp = getattr(requests, method)(url, json=json, timeout=10)
    if resp.status_code >= 400:
        print(f"  ERROR {resp.status_code}: {method.upper()} {path} -> {resp.text[:200]}")
        return None
    if resp.status_code == 204:
        return {}
    return resp.json()


def seed():
    print("Seeding demo data...")

    # --- Genotypes ---
    print("\n[1/7] Creating genotypes...")
    genotypes = {}
    for g in [
        {"name": "Wild-type (C57BL/6)", "description": "Standard inbred strain", "zygosity": "Homozygous"},
        {"name": "p53 -/-", "description": "Tumor suppressor knockout", "zygosity": "Homozygous"},
        {"name": "BRCA1 +/-", "description": "Breast cancer susceptibility", "zygosity": "Heterozygous"},
        {"name": "HER2-OE", "description": "HER2 overexpression transgenic", "zygosity": "Hemizygous"},
    ]:
        res = api("post", "/colony/genotypes", g)
        if res:
            genotypes[g["name"]] = res["id"]
            print(f"  Created genotype: {g['name']}")

    # --- Cages ---
    print("\n[2/7] Creating cages...")
    cages = {}
    for c in [
        {"label": "A1-01", "location": "Room 101, Rack A1", "capacity": 5},
        {"label": "A1-02", "location": "Room 101, Rack A1", "capacity": 5},
        {"label": "A2-01", "location": "Room 101, Rack A2", "capacity": 5},
        {"label": "A2-02", "location": "Room 101, Rack A2", "capacity": 5},
        {"label": "B1-01", "location": "Room 102, Rack B1", "capacity": 5},
        {"label": "B1-02", "location": "Room 102, Rack B1", "capacity": 5},
    ]:
        res = api("post", "/colony/cages", c)
        if res:
            cages[c["label"]] = res["id"]
            print(f"  Created cage: {c['label']}")

    # --- Mice ---
    print("\n[3/7] Creating mice...")
    today = date.today()
    mice = []

    mouse_data = [
        # Cage A1-01: WT females
        ("WT-F001", "Female", "Wild-type (C57BL/6)", "A1-01", -90),
        ("WT-F002", "Female", "Wild-type (C57BL/6)", "A1-01", -88),
        ("WT-F003", "Female", "Wild-type (C57BL/6)", "A1-01", -92),
        ("WT-F004", "Female", "Wild-type (C57BL/6)", "A1-01", -85),
        ("WT-F005", "Female", "Wild-type (C57BL/6)", "A1-01", -91),
        # Cage A1-02: WT males
        ("WT-M001", "Male", "Wild-type (C57BL/6)", "A1-02", -89),
        ("WT-M002", "Male", "Wild-type (C57BL/6)", "A1-02", -87),
        ("WT-M003", "Male", "Wild-type (C57BL/6)", "A1-02", -93),
        ("WT-M004", "Male", "Wild-type (C57BL/6)", "A1-02", -86),
        # Cage A2-01: p53 KO
        ("P53-F001", "Female", "p53 -/-", "A2-01", -75),
        ("P53-F002", "Female", "p53 -/-", "A2-01", -74),
        ("P53-F003", "Female", "p53 -/-", "A2-01", -76),
        ("P53-M001", "Male", "p53 -/-", "A2-01", -73),
        ("P53-M002", "Male", "p53 -/-", "A2-01", -77),
        # Cage A2-02: BRCA1
        ("BR-F001", "Female", "BRCA1 +/-", "A2-02", -80),
        ("BR-F002", "Female", "BRCA1 +/-", "A2-02", -82),
        ("BR-F003", "Female", "BRCA1 +/-", "A2-02", -79),
        ("BR-M001", "Male", "BRCA1 +/-", "A2-02", -81),
        # Cage B1-01: HER2
        ("HER2-F001", "Female", "HER2-OE", "B1-01", -70),
        ("HER2-F002", "Female", "HER2-OE", "B1-01", -72),
        ("HER2-F003", "Female", "HER2-OE", "B1-01", -68),
        ("HER2-M001", "Male", "HER2-OE", "B1-01", -71),
        ("HER2-M002", "Male", "HER2-OE", "B1-01", -69),
        # Cage B1-02: mixed for breeding
        ("WT-F006", "Female", "Wild-type (C57BL/6)", "B1-02", -100),
        ("WT-M005", "Male", "Wild-type (C57BL/6)", "B1-02", -105),
    ]

    for ear_tag, sex, geno_name, cage_label, dob_offset in mouse_data:
        dob = (today + timedelta(days=dob_offset)).isoformat()
        m = {
            "ear_tag": ear_tag,
            "sex": sex,
            "date_of_birth": dob,
            "genotype_id": genotypes.get(geno_name),
            "cage_id": cages.get(cage_label),
        }
        res = api("post", "/colony/mice", m)
        if res:
            mice.append(res)
    print(f"  Created {len(mice)} mice")

    # Build lookup by ear_tag
    mouse_by_tag = {m["ear_tag"]: m["id"] for m in mice if m}

    # --- Study 1: Completed tumor growth study ---
    print("\n[4/7] Creating completed tumor growth study...")
    study1 = api("post", "/studies", {
        "name": "Tumor Growth Kinetics - p53 vs WT",
        "description": "Compare subcutaneous tumor growth rates between p53 knockout and wild-type mice after B16 melanoma cell injection.",
        "start_date": (today - timedelta(days=42)).isoformat(),
        "end_date": (today - timedelta(days=14)).isoformat(),
    })
    if study1:
        sid = study1["id"]
        api("patch", f"/studies/{sid}", {"status": "Active"})
        print(f"  Study: {study1['name']}")

        # Cohorts
        cohort_vehicle = api("post", f"/studies/{sid}/cohorts", {
            "name": "Vehicle Control (WT)",
            "description": "Wild-type mice, PBS injection only",
        })
        cohort_p53 = api("post", f"/studies/{sid}/cohorts", {
            "name": "p53 KO + Tumor",
            "description": "p53 knockout mice with B16 melanoma cells",
        })

        # Enroll mice
        wt_enrolled = []
        p53_enrolled = []

        for tag in ["WT-F001", "WT-F002", "WT-F003", "WT-M001", "WT-M002"]:
            if tag in mouse_by_tag and cohort_vehicle:
                res = api("post", f"/studies/{sid}/cohorts/{cohort_vehicle['id']}/enrollments", {
                    "mouse_id": mouse_by_tag[tag],
                })
                if res:
                    wt_enrolled.append(res)

        for tag in ["P53-F001", "P53-F002", "P53-F003", "P53-M001", "P53-M002"]:
            if tag in mouse_by_tag and cohort_p53:
                res = api("post", f"/studies/{sid}/cohorts/{cohort_p53['id']}/enrollments", {
                    "mouse_id": mouse_by_tag[tag],
                })
                if res:
                    p53_enrolled.append(res)

        print(f"  Enrolled {len(wt_enrolled)} WT + {len(p53_enrolled)} p53 mice")

        # Measurements over 4 weeks (days 0, 3, 7, 10, 14, 17, 21, 24, 28)
        measurement_days = [0, 3, 7, 10, 14, 17, 21, 24, 28]
        random.seed(42)

        for enr in wt_enrolled:
            base_weight = random.uniform(20.0, 23.0)
            for day in measurement_days:
                rec_date = (today - timedelta(days=42) + timedelta(days=day)).isoformat()
                # WT: slow/no tumor growth, stable weight
                tumor_l = max(0, random.gauss(1.0 + day * 0.08, 0.3))
                tumor_w = max(0, tumor_l * random.uniform(0.6, 0.8))
                weight = base_weight + random.gauss(0.3 * day / 28, 0.3)
                api("post", f"/studies/{sid}/cohorts/{cohort_vehicle['id']}/enrollments/{enr['id']}/measurements", {
                    "recorded_at": rec_date,
                    "tumor_length_mm": round(tumor_l, 1),
                    "tumor_width_mm": round(tumor_w, 1),
                    "body_weight_g": round(weight, 1),
                })

        for enr in p53_enrolled:
            base_weight = random.uniform(19.5, 22.5)
            for day in measurement_days:
                rec_date = (today - timedelta(days=42) + timedelta(days=day)).isoformat()
                # p53 KO: rapid tumor growth, weight loss later
                tumor_l = max(0, random.gauss(1.5 + day * 0.35, 0.5))
                tumor_w = max(0, tumor_l * random.uniform(0.65, 0.85))
                weight_change = 0.2 * day / 28 if day < 14 else -0.5 * (day - 14) / 14
                weight = base_weight + random.gauss(weight_change, 0.4)
                api("post", f"/studies/{sid}/cohorts/{cohort_p53['id']}/enrollments/{enr['id']}/measurements", {
                    "recorded_at": rec_date,
                    "tumor_length_mm": round(tumor_l, 1),
                    "tumor_width_mm": round(tumor_w, 1),
                    "body_weight_g": round(weight, 1),
                })

        total_meas = len(wt_enrolled) * len(measurement_days) + len(p53_enrolled) * len(measurement_days)
        print(f"  Added {total_meas} measurements")

        # Mark study as completed now that data is in
        api("patch", f"/studies/{sid}", {"status": "Completed"})
        print("  Marked study as Completed")

    # --- Study 2: Active immunotherapy study ---
    print("\n[5/7] Creating active immunotherapy study...")
    study2 = api("post", "/studies", {
        "name": "Anti-PD1 Immunotherapy Response",
        "description": "Evaluate anti-PD1 checkpoint inhibitor efficacy in HER2-overexpressing tumor model.",
        "start_date": (today - timedelta(days=14)).isoformat(),
    })
    if study2:
        sid = study2["id"]
        api("patch", f"/studies/{sid}", {"status": "Active"})
        print(f"  Study: {study2['name']}")

        cohort_ctrl = api("post", f"/studies/{sid}/cohorts", {
            "name": "Isotype Control",
            "description": "IgG isotype control antibody, 10mg/kg biweekly",
        })
        cohort_pd1 = api("post", f"/studies/{sid}/cohorts", {
            "name": "Anti-PD1 Treatment",
            "description": "Anti-PD1 antibody, 10mg/kg biweekly",
        })

        ctrl_enrolled = []
        pd1_enrolled = []

        for tag in ["HER2-F001", "HER2-F002"]:
            if tag in mouse_by_tag and cohort_ctrl:
                res = api("post", f"/studies/{sid}/cohorts/{cohort_ctrl['id']}/enrollments", {
                    "mouse_id": mouse_by_tag[tag],
                })
                if res:
                    ctrl_enrolled.append(res)

        for tag in ["HER2-F003", "HER2-M001", "HER2-M002"]:
            if tag in mouse_by_tag and cohort_pd1:
                res = api("post", f"/studies/{sid}/cohorts/{cohort_pd1['id']}/enrollments", {
                    "mouse_id": mouse_by_tag[tag],
                })
                if res:
                    pd1_enrolled.append(res)

        print(f"  Enrolled {len(ctrl_enrolled)} control + {len(pd1_enrolled)} treatment mice")

        # 2 weeks of data so far
        measurement_days = [0, 3, 7, 10, 14]
        random.seed(123)

        for enr in ctrl_enrolled:
            base_weight = random.uniform(21.0, 24.0)
            for day in measurement_days:
                rec_date = (today - timedelta(days=14) + timedelta(days=day)).isoformat()
                tumor_l = max(0.5, random.gauss(2.0 + day * 0.25, 0.4))
                tumor_w = max(0.3, tumor_l * random.uniform(0.6, 0.8))
                weight = base_weight + random.gauss(-0.1 * day / 14, 0.3)
                api("post", f"/studies/{sid}/cohorts/{cohort_ctrl['id']}/enrollments/{enr['id']}/measurements", {
                    "recorded_at": rec_date,
                    "tumor_length_mm": round(tumor_l, 1),
                    "tumor_width_mm": round(tumor_w, 1),
                    "body_weight_g": round(weight, 1),
                })

        for enr in pd1_enrolled:
            base_weight = random.uniform(21.0, 24.0)
            for day in measurement_days:
                rec_date = (today - timedelta(days=14) + timedelta(days=day)).isoformat()
                # Treatment: tumor growth slows/regresses after day 7
                if day <= 7:
                    tumor_l = max(0.5, random.gauss(2.0 + day * 0.15, 0.3))
                else:
                    tumor_l = max(0.3, random.gauss(2.0 + 7 * 0.15 - (day - 7) * 0.1, 0.3))
                tumor_w = max(0.2, tumor_l * random.uniform(0.6, 0.8))
                weight = base_weight + random.gauss(0.05 * day / 14, 0.2)
                api("post", f"/studies/{sid}/cohorts/{cohort_pd1['id']}/enrollments/{enr['id']}/measurements", {
                    "recorded_at": rec_date,
                    "tumor_length_mm": round(tumor_l, 1),
                    "tumor_width_mm": round(tumor_w, 1),
                    "body_weight_g": round(weight, 1),
                })

        total_meas = len(ctrl_enrolled) * len(measurement_days) + len(pd1_enrolled) * len(measurement_days)
        print(f"  Added {total_meas} measurements")

    # --- Study 3: Draft study ---
    print("\n[6/7] Creating draft pharmacokinetics study...")
    study3 = api("post", "/studies", {
        "name": "BRCA1 Targeted Therapy PK Study",
        "description": "Pharmacokinetics evaluation of novel PARP inhibitor in BRCA1 heterozygous model. Planned 6-week study with dose escalation.",
        "start_date": (today + timedelta(days=7)).isoformat(),
    })
    if study3:
        print(f"  Study: {study3['name']}")
        sid = study3["id"]
        api("post", f"/studies/{sid}/cohorts", {
            "name": "Low Dose (5mg/kg)",
            "description": "PARP inhibitor 5mg/kg daily oral gavage",
        })
        api("post", f"/studies/{sid}/cohorts", {
            "name": "High Dose (25mg/kg)",
            "description": "PARP inhibitor 25mg/kg daily oral gavage",
        })
        api("post", f"/studies/{sid}/cohorts", {
            "name": "Vehicle Control",
            "description": "Methylcellulose vehicle, daily oral gavage",
        })
        print("  Created 3 cohorts (no enrollments yet)")

    # --- Set lineage for a few mice ---
    print("\n[7/7] Setting breeding lineage...")
    # WT-F001 and WT-M001 are parents of WT-F005
    if "WT-F005" in mouse_by_tag and "WT-F006" in mouse_by_tag and "WT-M005" in mouse_by_tag:
        api("put", f"/colony/mice/{mouse_by_tag['WT-F005']}/lineage", {
            "dam_id": mouse_by_tag["WT-F006"],
            "sire_id": mouse_by_tag["WT-M005"],
        })
        print("  Set WT-F005 parents: dam=WT-F006, sire=WT-M005")

    print("\n✅ Demo data seeded successfully!")
    print("   - 4 genotypes, 6 cages, 26 mice")
    print("   - 1 completed study with tumor growth data (4 weeks)")
    print("   - 1 active immunotherapy study (2 weeks so far)")
    print("   - 1 draft study (planned, no data yet)")
    print("   - Breeding lineage for 1 mouse")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed demo data into Vivo-Log")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/api/v1", help="Backend API URL")
    args = parser.parse_args()
    BASE_URL = args.base_url
    seed()
