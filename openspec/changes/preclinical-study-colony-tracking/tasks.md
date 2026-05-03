## 1. Project Scaffolding

- [ ] 1.1 Initialize Python project with FastAPI, SQLAlchemy 2.0, Alembic, and Pydantic v2 dependencies
- [ ] 1.2 Configure PostgreSQL connection, Alembic environment, and project settings module
- [ ] 1.3 Initialize Flutter project with Riverpod, HTTP client, and OpenAPI codegen dependencies
- [ ] 1.4 Set up Docker Compose for local PostgreSQL and backend service

## 2. Database Schema & Migrations

- [ ] 2.1 Create SQLAlchemy models for Genotype and Cage entities
- [ ] 2.2 Create SQLAlchemy model for Mouse with self-referential FKs (sire_id, dam_id), genotype_id FK, and cage_id FK
- [ ] 2.3 Create SQLAlchemy models for Study and Cohort entities
- [ ] 2.4 Create SQLAlchemy model for Enrollment (cohort_id FK, mouse_id FK, enrolled_at, removed_at, removal_reason)
- [ ] 2.5 Create SQLAlchemy model for Measurement (enrollment_id FK, tumor dimensions, tumor_volume_mm3, body_weight_g, recorded_at, notes)
- [ ] 2.6 Generate and verify Alembic migration for the full schema

## 3. Colony Management API

- [ ] 3.1 Implement CRUD endpoints for Genotype (`/api/v1/colony/genotypes`)
- [ ] 3.2 Implement CRUD endpoints for Cage with capacity validation (`/api/v1/colony/cages`)
- [ ] 3.3 Implement CRUD endpoints for Mouse with status enum validation (`/api/v1/colony/mice`)
- [ ] 3.4 Implement lineage assignment endpoint with sire-male/dam-female validation
- [ ] 3.5 Implement cage assignment endpoint with capacity check and transfer logic
- [ ] 3.6 Implement pedigree endpoint returning ancestor tree up to configurable depth
- [ ] 3.7 Implement query endpoint to list mice filtered by genotype

## 4. In-Vivo Study API

- [ ] 4.1 Implement CRUD endpoints for Study with status transitions (`/api/v1/studies`)
- [ ] 4.2 Implement CRUD endpoints for Cohort within a study (`/api/v1/studies/{id}/cohorts`)
- [ ] 4.3 Implement enrollment endpoint with mouse status check — reject "Deceased" or "Culled" mice with 409
- [ ] 4.4 Implement enrollment removal endpoint recording timestamp and reason
- [ ] 4.5 Implement measurement recording endpoint with non-negative validation
- [ ] 4.6 Implement server-side tumor volume calculation (Length × Width² / 2) on measurement save — null when either dimension is missing
- [ ] 4.7 Implement measurement history endpoint returning chronological list per enrollment

## 5. API Tests

- [ ] 5.1 Write tests for colony CRUD operations (mouse, genotype, cage)
- [ ] 5.2 Write tests for lineage validation (sire must be male, dam must be female)
- [ ] 5.3 Write tests for cage capacity enforcement and transfer logic
- [ ] 5.4 Write tests for study and cohort CRUD with status transitions
- [ ] 5.5 Write tests for enrollment eligibility — verify deceased/culled rejection
- [ ] 5.6 Write tests for tumor volume auto-calculation and null handling
- [ ] 5.7 Write tests for measurement validation (non-negative values, partial measurements)

## 6. Flutter Frontend — Colony Management

- [ ] 6.1 Generate API client from FastAPI OpenAPI spec
- [ ] 6.2 Create repository and Riverpod providers for colony entities
- [ ] 6.3 Build mouse list screen with filtering by genotype and status
- [ ] 6.4 Build mouse detail/edit screen with lineage, genotype, and cage assignment
- [ ] 6.5 Build cage list and detail screens showing assigned mice and capacity
- [ ] 6.6 Build pedigree view widget for a selected mouse

## 7. Flutter Frontend — In-Vivo Study

- [ ] 7.1 Create repository and Riverpod providers for study entities
- [ ] 7.2 Build study list and study detail screens with cohort management
- [ ] 7.3 Build cohort enrollment screen with mouse picker (filters out deceased/culled)
- [ ] 7.4 Build measurement entry form with tumor dimension inputs and live volume preview
- [ ] 7.5 Build measurement history view with chronological table per enrollment

## 8. Integration & Polish

- [ ] 8.1 End-to-end smoke test: create mouse → enroll in study → record measurement → verify volume
- [ ] 8.2 Add OpenAPI schema validation and generate final Flutter client
- [ ] 8.3 Write README with setup instructions, environment variables, and development workflow
