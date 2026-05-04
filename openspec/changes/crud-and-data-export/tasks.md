## 1. Backend: Constraint Error Handling

- [x] 1.1 Add IntegrityError handler to colony router delete endpoints (genotype, cage, mouse) returning 409 with descriptive detail message
- [x] 1.2 Add IntegrityError handler to studies router delete endpoints (study, cohort) returning 409 with descriptive detail message
- [x] 1.3 Write tests for 409 responses on constrained deletes (genotype in use, cage occupied, mouse referenced, study with enrollments, cohort with enrollments)

## 2. Backend: New Endpoints (Cohort Update, Measurement Delete)

- [x] 2.1 Add PATCH endpoint for cohort name update at `/api/v1/studies/{study_id}/cohorts/{cohort_id}`
- [x] 2.2 Add DELETE endpoint for measurement at `/api/v1/studies/{study_id}/cohorts/{cohort_id}/enrollments/{enrollment_id}/measurements/{measurement_id}`
- [x] 2.3 Write tests for cohort update and measurement delete endpoints

## 3. Backend: Export Router

- [x] 3.1 Add `openpyxl` dependency to pyproject.toml
- [x] 3.2 Create `/api/v1/export` router with CSV export endpoints for mice, cages, genotypes
- [x] 3.3 Add CSV export endpoint for study measurements (flattened with study/cohort/mouse info)
- [x] 3.4 Add CSV export endpoint for study enrollments (flattened)
- [x] 3.5 Add XLSX export endpoints mirroring CSV endpoints
- [x] 3.6 Register export router in main.py
- [x] 3.7 Write tests for export endpoints (verify CSV content, XLSX file structure, correct headers)

## 4. Flutter: Colony CRUD Forms

- [x] 4.1 Create genotype create/edit dialog with name, description, zygosity fields and validation
- [x] 4.2 Add delete genotype button with confirmation dialog and 409 error handling
- [x] 4.3 Create cage create/edit dialog with label, location, capacity fields and validation
- [x] 4.4 Add delete cage button with confirmation dialog and 409 error handling
- [x] 4.5 Create mouse create/edit form screen with ear tag, sex, DOB, genotype picker, cage picker, status
- [x] 4.6 Add delete mouse button with confirmation dialog and 409 error handling
- [x] 4.7 Add FAB/add buttons to list screens to launch create forms
- [x] 4.8 Add edit buttons to detail/list items to launch edit forms

## 5. Flutter: Study CRUD Forms

- [x] 5.1 Create study create/edit form screen with name, description, start date, end date, status fields
- [x] 5.2 Add delete study button with confirmation dialog and 409 error handling
- [x] 5.3 Create cohort create/edit dialog with name field
- [x] 5.4 Add delete cohort button with confirmation dialog and 409 error handling
- [x] 5.5 Add enroll mouse UI to cohort screen (eligible mouse picker, confirm enrollment)
- [x] 5.6 Add remove enrollment button with reason input dialog
- [x] 5.7 Add measurement form (tumor length, width, body weight) with live volume preview
- [x] 5.8 Add delete measurement button with confirmation dialog

## 6. Flutter: Data Export

- [x] 6.1 Add `share_plus` and `path_provider` dependencies to pubspec.yaml
- [x] 6.2 Add export service in api layer to call export endpoints and receive file bytes
- [x] 6.3 Add export button with format chooser (CSV/XLSX) to mouse list screen
- [x] 6.4 Add export button with format chooser to cage list screen
- [x] 6.5 Add export button with format chooser to study detail screen (measurements + enrollments)
- [x] 6.6 Implement file save and share sheet integration via share_plus

## 7. Flutter: Repository & Provider Updates

- [x] 7.1 Add create/update/delete methods to colony_repository for genotypes, cages, mice
- [x] 7.2 Add update cohort, delete measurement methods to study_repository
- [x] 7.3 Update Riverpod providers to invalidate/refresh on mutations
- [x] 7.4 Add error handling for 409 responses in repositories (parse detail message)

## 8. Testing & Polish

- [x] 8.1 Run all backend tests and fix any regressions
- [x] 8.2 Run Flutter analyze and fix any issues
- [x] 8.3 Manual smoke test: create, edit, delete a mouse end-to-end
- [x] 8.4 Manual smoke test: export mice as CSV and XLSX
