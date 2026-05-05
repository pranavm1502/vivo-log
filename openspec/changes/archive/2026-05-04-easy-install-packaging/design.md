## Context

Vivo-Log is a macOS desktop application with a Flutter frontend, FastAPI backend, and PostgreSQL database. Currently it requires a developer environment (Python 3.12, Flutter SDK, Docker) and is started via a shell script. Target users are biology researchers who need a drag-and-drop install experience.

The macOS platform is the only target for now. The Flutter app already compiles to a native macOS .app bundle via `flutter build macos`. The challenge is embedding the backend server and database so everything runs self-contained.

## Goals / Non-Goals

**Goals:**
- Single DMG installer: download, drag to /Applications, double-click to run
- Zero external dependencies on the user's machine (no Python, Docker, Homebrew)
- Backend starts automatically on app launch, stops on app quit
- Database persists between app launches (data stored in ~/Library/Application Support/Vivo-Log/)
- First launch auto-initializes the database schema

**Non-Goals:**
- Windows/Linux packaging (future work)
- Auto-update mechanism (future work)
- Code signing / notarization for App Store distribution (can be added later)
- Multi-user / networked deployment

## Decisions

### 1. Backend packaging: PyInstaller single-folder bundle

**Choice:** Use PyInstaller to compile the FastAPI backend into a standalone executable directory.

**Alternatives considered:**
- **Nuitka**: Better optimization but slower build, more complex setup
- **Embedded Python**: Ship python3.12 framework + site-packages — larger, harder to manage paths
- **Rewrite in Dart**: Eliminates the Python dependency entirely but massive effort

**Rationale:** PyInstaller is well-established for FastAPI/uvicorn apps, produces a self-contained folder with all dependencies, and the resulting binary starts fast enough for a local server.

### 2. Database: Embedded PostgreSQL via bundled binaries

**Choice:** Bundle PostgreSQL 15 binaries (initdb, postgres) inside the .app bundle Resources folder. On first launch, run `initdb` to create a data directory in Application Support. On each launch, start `postgres` as a child process.

**Alternatives considered:**
- **SQLite**: Simpler but requires migrating the existing async PostgreSQL codebase
- **pg_embed (Rust crate)**: Not easily integrated into a Flutter/Python app
- **Docker inside the app**: Requires Docker Desktop installed — defeats the purpose

**Rationale:** PostgreSQL binaries are ~30MB and can be extracted from the Homebrew bottle for the target architecture. This keeps the existing backend code unchanged while being fully self-contained.

### 3. Lifecycle management: Flutter spawns backend as child process

**Choice:** The Flutter macOS runner spawns the PyInstaller backend executable and the PostgreSQL server as child processes on launch. On app quit (or SIGTERM), it sends SIGTERM to both processes.

**Implementation:**
- `AppDelegate.swift` or a Dart isolate using `Process.start` to launch backend + postgres
- Health check: poll `http://localhost:8000/docs` until 200 before showing the main UI
- Graceful shutdown: `Process.kill` on `AppLifecycleState.detached`

### 4. Data storage location

**Choice:** `~/Library/Application Support/Vivo-Log/`
- `db/` — PostgreSQL data directory
- `logs/` — backend and postgres logs

### 5. Distribution: DMG via create-dmg

**Choice:** Use `create-dmg` to build a styled DMG with drag-to-Applications shortcut.

**Build pipeline:** `build.sh` script that:
1. `flutter build macos --release`
2. `pyinstaller backend.spec` (produces `dist/backend/`)
3. Copy `dist/backend/` and postgres binaries into the .app bundle's Resources
4. Run `create-dmg` to produce the final DMG

## Risks / Trade-offs

- **App size ~200MB**: PostgreSQL binaries (~30MB) + Python runtime (~50MB) + Flutter app (~80MB) + dependencies. Acceptable for a desktop research tool.
- **macOS Gatekeeper**: Without notarization, users must right-click → Open on first launch. Documented in README; notarization is a future enhancement.
- **PostgreSQL port conflict**: If user has postgres running on 5432, the bundled instance will fail. Mitigation: use a non-standard port (5433) and configure via environment variable.
- **Architecture**: Must build separate bundles for Intel (x86_64) and Apple Silicon (arm64), or a universal binary. Initial target: arm64 only (Apple Silicon) since that's the development machine.
- **Alembic migrations on update**: When shipping a new version, the app must run `alembic upgrade head` on the existing database. The PyInstaller bundle includes alembic and migration files.
