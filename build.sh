#!/usr/bin/env bash
# Build script for Vivo-Log macOS application.
# Produces dist/Vivo-Log.dmg containing the complete .app bundle.
#
# Prerequisites (developer machine only):
#   - Flutter SDK
#   - Python 3.12 with PyInstaller (pip install pyinstaller)
#   - PostgreSQL 15 binaries in packaging/postgres/
#   - create-dmg (brew install create-dmg)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DIST="$ROOT/dist"

echo "=== Vivo-Log Build Script ==="
echo ""

# 1. Build Flutter macOS app
echo "[1/5] Building Flutter macOS app..."
cd "$ROOT/frontend"
flutter build macos --release
APP_BUNDLE="$ROOT/frontend/build/macos/Build/Products/Release/vivo_log.app"

if [ ! -d "$APP_BUNDLE" ]; then
  echo "ERROR: Flutter build failed - .app not found at $APP_BUNDLE"
  exit 1
fi
echo "      Flutter build complete."

# 2. Build backend with PyInstaller
echo "[2/5] Building backend with PyInstaller..."
cd "$ROOT/backend"
source .venv/bin/activate
pyinstaller backend.spec --noconfirm --clean 2>&1 | tail -3

if [ ! -f "$ROOT/backend/dist/backend/backend" ]; then
  echo "ERROR: PyInstaller build failed - executable not found"
  exit 1
fi
echo "      Backend build complete."

# 3. Copy backend into .app bundle Resources
echo "[3/5] Copying backend into app bundle..."
RESOURCES="$APP_BUNDLE/Contents/Resources"
mkdir -p "$RESOURCES"
rm -rf "$RESOURCES/backend"
cp -R "$ROOT/backend/dist/backend" "$RESOURCES/backend"
echo "      Backend copied to Resources/backend/"

# 4. Copy PostgreSQL binaries into .app bundle Resources and fix rpaths
echo "[4/5] Copying PostgreSQL binaries into app bundle..."
rm -rf "$RESOURCES/postgres"
cp -R "$ROOT/packaging/postgres" "$RESOURCES/postgres"
chmod +x "$RESOURCES/postgres/bin/"*
echo "      Fixing library paths..."
bash "$RESOURCES/postgres/fix_rpaths.sh"
echo "      PostgreSQL copied to Resources/postgres/"

# 5. Create DMG
echo "[5/5] Creating DMG installer..."
mkdir -p "$DIST"
DMG_PATH="$DIST/Vivo-Log.dmg"
rm -f "$DMG_PATH"

# Rename the app bundle for the DMG
FINAL_APP="$DIST/Vivo-Log.app"
rm -rf "$FINAL_APP"
cp -R "$APP_BUNDLE" "$FINAL_APP"

if command -v create-dmg &> /dev/null; then
  create-dmg \
    --volname "Vivo-Log" \
    --volicon "$ROOT/frontend/macos/Runner/Assets.xcassets/AppIcon.appiconset/app_icon_512.png" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "Vivo-Log.app" 150 185 \
    --app-drop-link 450 185 \
    "$DMG_PATH" \
    "$FINAL_APP" \
    2>&1 | tail -3
else
  # Fallback: create a DMG with Applications shortcut using hdiutil
  echo "      create-dmg not found, using hdiutil with Applications symlink..."
  DMG_STAGING="$DIST/dmg-staging"
  rm -rf "$DMG_STAGING"
  mkdir -p "$DMG_STAGING"
  cp -R "$FINAL_APP" "$DMG_STAGING/Vivo-Log.app"
  ln -s /Applications "$DMG_STAGING/Applications"
  hdiutil create -volname "Vivo-Log" -srcfolder "$DMG_STAGING" -ov -format UDZO "$DMG_PATH"
  rm -rf "$DMG_STAGING"
fi

rm -rf "$FINAL_APP"

echo ""
echo "=== Build Complete ==="
echo "DMG: $DMG_PATH"
echo "Size: $(du -h "$DMG_PATH" | cut -f1)"
