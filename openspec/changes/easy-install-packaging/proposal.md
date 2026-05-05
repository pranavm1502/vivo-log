## Why

Biology researchers need to run Vivo-Log on their lab machines without installing Python, Flutter, Docker, or managing terminal commands. The current workflow requires developer tooling (start.sh, docker compose, flutter run) which is inaccessible to non-technical users.

## What Changes

- Create a single native macOS application bundle (.app) that embeds the Flutter frontend, FastAPI backend, and PostgreSQL database
- Provide a one-click installer (DMG) that a researcher can download, drag to Applications, and launch
- Auto-start the backend and database when the app launches; shut them down on quit
- Remove the need for any terminal commands, Docker, Python venv, or Flutter SDK on the user's machine

## Capabilities

### New Capabilities
- `desktop-packaging`: Bundling the macOS app with embedded backend, database, and auto-lifecycle management into a distributable DMG installer

### Modified Capabilities

## Impact

- **Build system**: New build script that compiles Flutter for macOS, bundles a Python distributable (PyInstaller or embedded Python), and packages PostgreSQL binaries
- **Backend**: Must be packageable as a standalone executable (no venv dependency at runtime)
- **Database**: Embedded PostgreSQL (e.g., pg_embed or bundled postgres binaries) with auto-initialization on first launch
- **Frontend**: macOS runner configuration changes for app bundle metadata, lifecycle hooks to start/stop backend
- **Distribution**: New DMG creation step, code signing considerations for macOS Gatekeeper
- **Dependencies**: PyInstaller or Nuitka for backend, postgresql binaries or pg_embed, create-dmg for installer
