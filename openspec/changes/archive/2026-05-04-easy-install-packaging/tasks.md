## 1. Backend Packaging with PyInstaller

- [x] 1.1 Install PyInstaller in the backend dev dependencies
- [x] 1.2 Create `backend.spec` PyInstaller spec file (single-folder mode, include alembic migrations and app package)
- [x] 1.3 Test PyInstaller build: `pyinstaller backend.spec` produces working `dist/backend/` executable
- [x] 1.4 Verify the built backend starts uvicorn and responds on localhost:8000

## 2. Bundle PostgreSQL Binaries

- [x] 2.1 Download PostgreSQL 15 arm64 binaries (from Homebrew bottle or official archive)
- [x] 2.2 Create a `packaging/postgres/` directory with required binaries (postgres, initdb, pg_ctl) and libs
- [x] 2.3 Write a helper script/logic that runs `initdb` on first launch to create the data directory
- [x] 2.4 Verify bundled postgres starts on port 5433 and accepts connections

## 3. Flutter App Lifecycle Integration

- [x] 3.1 Create a Dart service class (`BackendLifecycle`) that spawns the backend executable as a child process
- [x] 3.2 Create a Dart service class (`DatabaseLifecycle`) that spawns postgres and manages initdb on first run
- [x] 3.3 Add startup health check: poll localhost:8000 until the backend is ready, show loading UI
- [x] 3.4 Add graceful shutdown: kill backend and postgres processes on app quit (AppLifecycleState.detached)
- [x] 3.5 Handle crash recovery: detect stale PID/lock files and clean up on next launch
- [x] 3.6 Configure backend to connect to port 5433 (pass DATABASE_URL environment variable to backend process)

## 4. macOS App Bundle Assembly

- [x] 4.1 Update `frontend/macos/Runner/Info.plist` with proper app metadata (bundle name, version, icon)
- [x] 4.2 Add a build step to copy `dist/backend/` into the .app bundle's Resources directory
- [x] 4.3 Add a build step to copy PostgreSQL binaries into the .app bundle's Resources/postgres/ directory
- [x] 4.4 Update `BackendLifecycle` to resolve the backend executable path relative to the app bundle
- [x] 4.5 Update `DatabaseLifecycle` to resolve postgres binary paths relative to the app bundle

## 5. Build Script

- [x] 5.1 Create `build.sh` that runs `flutter build macos --release`
- [x] 5.2 Add PyInstaller backend build step to `build.sh`
- [x] 5.3 Add step to copy backend bundle and postgres binaries into the built .app
- [x] 5.4 Add `create-dmg` step to produce `dist/Vivo-Log.dmg` with Applications shortcut
- [x] 5.5 Test full build pipeline end-to-end: `./build.sh` produces a working DMG

## 6. Data Storage and Migrations

- [x] 6.1 Configure Application Support path: `~/Library/Application Support/Vivo-Log/db/` for postgres data
- [x] 6.2 Configure log directory: `~/Library/Application Support/Vivo-Log/logs/`
- [x] 6.3 Ensure Alembic migrations run on each app start (include migration files in PyInstaller bundle)
- [x] 6.4 Test data persistence: create data, quit app, relaunch, verify data intact

## 7. Testing and Validation

- [x] 7.1 Test first launch on a clean machine (no dev tools installed)
- [x] 7.2 Test that quitting the app leaves no orphan processes
- [x] 7.3 Test DMG install: drag to Applications, eject DMG, launch from Applications
- [x] 7.4 Test port conflict scenario: run postgres on 5432, verify app uses 5433 without issues
- [x] 7.5 Test app launch when previous session crashed (stale lock file recovery)
