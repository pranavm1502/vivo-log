## Context

The vivo-log application has a complete FastAPI backend with CRUD endpoints for genotypes, cages, mice, studies, cohorts, enrollments, and measurements. The Flutter frontend currently renders list and detail views using Riverpod providers and Dio HTTP calls, but provides no forms for creating, editing, or deleting records. Users must interact with the API directly or run the seed script. There is also no mechanism to export data for external analysis or reporting.

The backend already returns proper 404 for missing resources but does not gracefully handle foreign-key violations on delete (it returns generic 500 errors). The frontend has no error handling for these cases.

## Goals / Non-Goals

**Goals:**
- Provide full CRUD UI for all entity types in the Flutter app (create, edit, delete)
- Add data export (CSV and XLSX) for colony and study datasets
- Return structured error responses from the backend on constraint violations
- Handle errors gracefully in the UI with user-friendly messages

**Non-Goals:**
- Bulk import from CSV/XLSX (future work)
- Offline-first or local caching
- Role-based access control or authentication
- Real-time collaboration or live updates
- Drag-and-drop reordering or advanced table editing

## Decisions

### 1. Flutter form approach: Dialog-based for simple entities, full-screen for complex ones

**Choice:** Use `showDialog` with form fields for genotypes and cages (few fields). Use full-screen form pages for mice (many fields + pickers) and studies/cohorts.

**Rationale:** Dialogs reduce navigation for simple 2-3 field forms. Complex forms with dropdowns (genotype picker, cage picker, date pickers) need more screen space. This matches common Flutter patterns.

**Alternatives considered:**
- All full-screen forms → too heavy for simple entities like genotypes
- All dialogs → insufficient space for mice form with its many fields and pickers
- Bottom sheets → awkward on macOS desktop

### 2. Export backend: Dedicated `/api/v1/export` router with streaming file response

**Choice:** Add a new router with endpoints that accept query parameters (entity type, optional filters) and return files with appropriate Content-Type and Content-Disposition headers. Support both CSV and XLSX formats.

**Rationale:** Server-side generation ensures consistent formatting regardless of client. Streaming prevents memory issues with large datasets. Using a dedicated router keeps export logic separate from entity CRUD.

**Alternatives considered:**
- Client-side generation in Flutter → platform-dependent file handling, duplicates business logic
- Return JSON and let client format → extra work on every client, no standard file download
- GraphQL-style export → over-engineering for this use case

### 3. XLSX library: `openpyxl`

**Choice:** Use `openpyxl` for XLSX generation (already the de-facto standard Python library).

**Rationale:** Lightweight, well-maintained, no binary dependencies. Supports streaming write mode for large datasets.

**Alternatives considered:**
- `xlsxwriter` → write-only (fine for our case), but less widely used
- `pandas.to_excel` → heavy dependency for just export

### 4. Delete constraint handling: Backend returns 409 Conflict with detail message

**Choice:** Catch `IntegrityError` on delete operations and return HTTP 409 with a JSON body explaining which relationship prevents deletion.

**Rationale:** The backend currently lets these bubble up as 500 errors. A 409 with a clear message lets the frontend show actionable guidance (e.g., "Cannot delete mouse M-001 because it is referenced as a sire by M-003, M-004").

**Alternatives considered:**
- Cascade deletes → dangerous in a research context, could silently remove data
- Soft deletes → adds complexity, not needed yet
- Pre-check before delete → race condition between check and delete

### 5. Flutter file export: `share_plus` for cross-platform sharing

**Choice:** Use `share_plus` to share/save exported files on macOS (and iOS if later supported).

**Rationale:** Platform-native share sheet handles file saving without needing to pick a directory ourselves. Works on macOS, iOS, Android.

**Alternatives considered:**
- `file_picker` save dialog → more code, less native feel
- `path_provider` + manual file write → user has to know where to find the file
- `url_launcher` with blob URLs → web-only pattern

## Risks / Trade-offs

- **[Large XLSX files]** → Mitigation: Use openpyxl's write-only mode for streaming; add a row limit (10,000) with a warning in the response
- **[Delete cascading expectations]** → Mitigation: Clear error messages explaining what blocks deletion and suggesting corrective actions
- **[Form state loss on navigation]** → Mitigation: Use `WillPopScope` (or `PopScope`) to warn before discarding unsaved changes
- **[Export performance]** → Mitigation: Server-side generation with async I/O; for very large datasets consider background job (non-goal for now)
