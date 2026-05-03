## Context

This is a greenfield system for preclinical research teams. There is no existing application—colony and study data are currently managed via spreadsheets and manual records. The system will be built as a client-server application: a FastAPI backend with PostgreSQL for persistence and a Flutter frontend for cross-platform access (desktop and tablet use in lab environments).

Key constraints:
- Data integrity is critical—lineage records and study measurements directly impact research outcomes.
- The system must enforce business rules at the API layer (e.g., enrollment eligibility).
- Researchers need to enter measurements quickly at the bench, so the UI must minimize friction.

## Goals / Non-Goals

**Goals:**
- Provide a reliable colony management system with full lineage tracking (sire/dam), genotype records, and cage assignments.
- Support in-vivo study workflows: study creation, cohort definition, mouse enrollment, and timestamped measurement capture.
- Automatically compute derived values (tumor volume) server-side to ensure consistency.
- Enforce enrollment business rules at the API level so no client can bypass them.
- Deliver a responsive Flutter frontend that works on desktop and tablet.

**Non-Goals:**
- IACUC protocol management or compliance reporting.
- Breeding optimization or automated pairing recommendations.
- Image capture or histology data management.
- Multi-tenant / multi-institution support (single deployment target).
- Real-time collaboration or live data sync between multiple concurrent users.

## Decisions

### 1. Python / FastAPI for the backend
**Choice**: FastAPI with async endpoints, Pydantic v2 models, SQLAlchemy 2.0 ORM.
**Rationale**: FastAPI provides automatic OpenAPI docs (useful for Flutter codegen), strong typing via Pydantic, and async support for I/O-bound DB operations. The team is familiar with Python.
**Alternatives considered**: Django REST Framework (heavier, less async-native), Node/Express (team less familiar).

### 2. PostgreSQL 15+ for persistence
**Choice**: PostgreSQL with Alembic for migrations.
**Rationale**: Strong support for relational integrity (foreign keys for lineage), JSON columns for flexible genotype metadata, and mature tooling. Alembic provides version-controlled schema migrations.
**Alternatives considered**: SQLite (insufficient for concurrent access), MongoDB (lineage relationships are inherently relational).

### 3. Server-side tumor volume calculation
**Choice**: Compute `Volume = Length × Width² / 2` in the API layer when measurements are saved, and store the result.
**Rationale**: Ensures consistency—every client gets the same formula. The frontend can show a preview, but the persisted value is always server-computed.
**Alternatives considered**: Client-only calculation (risk of formula drift across platforms), database trigger (harder to test and debug).

### 4. Enrollment eligibility enforced at API layer
**Choice**: The `POST /api/v1/studies/{id}/cohorts/{id}/enrollments` endpoint checks mouse status and rejects enrollment if status is "Deceased" or "Culled" with a `409 Conflict`.
**Rationale**: Business rules in the API layer are testable, auditable, and cannot be bypassed by any client.

### 5. Flutter frontend with repository pattern
**Choice**: Flutter 3.x with Riverpod for state management and a repository layer that calls the FastAPI-generated client.
**Rationale**: Flutter allows a single codebase for desktop (macOS/Windows) and tablet (iPad). Riverpod provides testable, compile-safe state management. OpenAPI codegen reduces manual HTTP boilerplate.
**Alternatives considered**: React/Next.js (no native mobile/tablet story), SwiftUI (Apple-only).

### 6. Data model structure
**Key entities and relationships:**
- `Mouse` — id, ear_tag, sex, date_of_birth, status (Alive/Deceased/Culled), sire_id (self-FK), dam_id (self-FK), genotype_id, cage_id
- `Genotype` — id, name, description, zygosity
- `Cage` — id, label, location, capacity
- `Study` — id, name, description, start_date, end_date, status
- `Cohort` — id, study_id (FK), name, description
- `Enrollment` — id, cohort_id (FK), mouse_id (FK), enrolled_at, removed_at, removal_reason
- `Measurement` — id, enrollment_id (FK), recorded_at, tumor_length_mm, tumor_width_mm, tumor_volume_mm3, body_weight_g, notes

## Risks / Trade-offs

- **[Risk] Self-referential lineage queries may be slow for deep pedigrees** → Mitigation: Limit pedigree display depth to 5 generations; add recursive CTE index if needed later.
- **[Risk] Concurrent measurement entry could cause conflicts** → Mitigation: Optimistic concurrency via row versioning on measurement records. Out of scope for v1, revisit if usage patterns demand it.
- **[Risk] Flutter desktop maturity** → Mitigation: Target macOS first (most mature Flutter desktop platform); keep UI simple to avoid platform-specific edge cases.
- **[Trade-off] Server-computed tumor volume adds a round trip** → Acceptable because data integrity outweighs latency; frontend preview provides immediate feedback.
