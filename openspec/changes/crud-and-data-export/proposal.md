## Why

The Flutter frontend currently provides read-only list and detail views for mice, cages, studies, cohorts, and measurements. Users cannot create, edit, or delete records from the app—they must use the API directly or a seed script. Additionally, there is no way to export colony or study data for reporting, sharing with collaborators, or offline analysis. Adding full CRUD forms and data export will make the app self-sufficient for day-to-day lab use.

## What Changes

- Add create/edit/delete UI flows for mice, genotypes, cages, studies, cohorts, enrollments, and measurements in the Flutter app
- Add confirmation dialogs before destructive actions (delete)
- Add inline form validation matching backend constraints (required fields, non-negative values, capacity limits)
- Add a data export feature that generates CSV or XLSX files for colony data (mice, cages, genotypes) and study data (enrollments, measurements)
- Add a backend export endpoint that returns formatted data files
- Handle foreign-key constraint errors gracefully in the UI (e.g., cannot delete a mouse that is a sire/dam or enrolled in a study)

## Capabilities

### New Capabilities
- `data-export`: Server-side data export to CSV/XLSX with filtering options, covering colony and study datasets

### Modified Capabilities
- `colony-management`: Add frontend CRUD forms for mice, genotypes, and cages with validation and error handling for constraint violations
- `in-vivo-study`: Add frontend CRUD forms for studies, cohorts, enrollments, and measurements; add edit cohort support; handle enrollment/removal flows in the UI

## Impact

- **Backend**: New `/api/v1/export` router with endpoints for CSV/XLSX generation; add `openpyxl` dependency for XLSX support; add proper HTTP 409 error responses for constraint violations on delete
- **Frontend**: New form screens/dialogs for create and edit operations across all entity types; delete buttons with confirmation; export button on list screens triggering file download/share
- **Dependencies**: `openpyxl` (Python, for XLSX); Flutter `share_plus` or `path_provider` for file saving on macOS
