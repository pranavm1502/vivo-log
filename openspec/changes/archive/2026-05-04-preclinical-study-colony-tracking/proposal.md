## Why

Preclinical research teams currently lack an integrated system for managing mouse colonies and tracking in-vivo study data. Colony lineage, genotyping, and cage assignments are managed in spreadsheets, while experimental measurements (tumor dimensions, body weight) are recorded manually with no automated calculations or validation. This leads to data entry errors, lost lineage records, and inability to enforce enrollment rules—ultimately compromising study integrity and slowing research timelines.

## What Changes

- Introduce a **Colony Management** module for tracking individual mice, their lineage (sire/dam), genotype information, and cage locations.
- Introduce an **In-Vivo Study** module for defining studies, enrolling mice into cohorts, and capturing timestamped experimental data (tumor length/width, body weight).
- Automatically calculate **tumor volume** (Volume = Length × Width² / 2) when tumor dimensions are entered.
- Enforce enrollment rules: a mouse with status "Deceased" or "Culled" **cannot** be enrolled in a study.
- Provide a **FastAPI/PostgreSQL** backend with RESTful APIs and a **Flutter** cross-platform frontend.

## Capabilities

### New Capabilities
- `colony-management`: Tracking mouse records including lineage (sire/dam), genotype, status, and cage location assignments.
- `in-vivo-study`: Defining studies, creating cohorts, enrolling mice, and capturing timestamped experimental measurements with automatic tumor volume calculation.

### Modified Capabilities
<!-- No existing capabilities to modify — this is a greenfield system. -->

## Impact

- **New database schema**: Tables for mice, cages, genotypes, lineage, studies, cohorts, enrollments, and measurements in PostgreSQL.
- **New API surface**: RESTful endpoints under `/api/v1/colony/` and `/api/v1/studies/` served by FastAPI.
- **New frontend**: Flutter application with screens for colony browse/edit, study management, cohort enrollment, and measurement entry.
- **Dependencies**: Python 3.11+, FastAPI, SQLAlchemy, Alembic, PostgreSQL 15+, Flutter 3.x, Dart.
