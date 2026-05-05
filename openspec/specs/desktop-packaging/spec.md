## ADDED Requirements

### Requirement: One-click application launch
The system SHALL provide a macOS application bundle (.app) that a user can launch by double-clicking. The application SHALL start the backend API server and PostgreSQL database automatically without requiring any terminal commands, Docker, Python, or Flutter SDK on the user's machine.

#### Scenario: First launch initializes database
- **WHEN** user launches Vivo-Log.app for the first time
- **THEN** the application creates a PostgreSQL data directory at ~/Library/Application Support/Vivo-Log/db/, initializes the database schema, starts the backend server, and displays the main dashboard

#### Scenario: Subsequent launch reuses existing data
- **WHEN** user launches Vivo-Log.app after having previously used it
- **THEN** the application starts PostgreSQL using the existing data directory, runs any pending database migrations, starts the backend server, and displays the dashboard with all previously saved data

#### Scenario: Application shows loading state during startup
- **WHEN** the application is starting up and the backend is not yet ready
- **THEN** the application displays a loading indicator until the backend health check succeeds

### Requirement: Graceful shutdown on quit
The system SHALL stop the backend server and PostgreSQL database when the application is closed. No orphan processes SHALL remain after the app quits.

#### Scenario: User quits the application
- **WHEN** user closes the Vivo-Log window or selects Quit from the menu
- **THEN** the application sends SIGTERM to the backend server and PostgreSQL process, waits for graceful shutdown, and then exits

#### Scenario: Application crash cleanup
- **WHEN** the application crashes or is force-quit
- **THEN** on next launch the application detects stale PID files or lock files and cleans them up before starting fresh

### Requirement: DMG installer for distribution
The system SHALL be distributable as a DMG disk image file that contains the Vivo-Log.app bundle and a shortcut to the Applications folder.

#### Scenario: User installs from DMG
- **WHEN** user opens the DMG file
- **THEN** they see the Vivo-Log.app icon and an Applications folder shortcut, and can drag the app to install it

#### Scenario: Installed app runs without DMG mounted
- **WHEN** user ejects the DMG and launches Vivo-Log.app from Applications
- **THEN** the application runs correctly with all bundled dependencies

### Requirement: Self-contained backend executable
The system SHALL bundle the FastAPI backend as a standalone executable that does not require a Python installation on the user's machine. All Python dependencies SHALL be included in the bundle.

#### Scenario: Backend starts from bundled executable
- **WHEN** the application launches the backend
- **THEN** it runs the PyInstaller-compiled backend binary from within the .app bundle's Resources directory and the API responds on localhost:8000

### Requirement: Embedded PostgreSQL
The system SHALL bundle PostgreSQL binaries within the application and manage the database lifecycle automatically. The database SHALL use a non-standard port (5433) to avoid conflicts with any existing PostgreSQL installation.

#### Scenario: No port conflict with existing PostgreSQL
- **WHEN** user has PostgreSQL already running on port 5432
- **THEN** the bundled PostgreSQL starts on port 5433 without conflict and the backend connects to it successfully

#### Scenario: Database data persists across app launches
- **WHEN** user quits and relaunches the application
- **THEN** all studies, cohorts, enrollments, and measurements are preserved in the database

### Requirement: Build script produces distributable
The system SHALL include a build script that produces the final DMG from source in a single command. The script SHALL compile the Flutter frontend, package the Python backend, bundle PostgreSQL binaries, assemble the .app bundle, and create the DMG.

#### Scenario: Build from source
- **WHEN** developer runs `./build.sh` on a macOS machine with Flutter and Python installed
- **THEN** the script produces `dist/Vivo-Log.dmg` containing the complete application bundle
