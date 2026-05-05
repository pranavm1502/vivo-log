#!/usr/bin/env bash
# Rewrite dylib paths in bundled PostgreSQL binaries to use @loader_path/@executable_path
# This makes the binaries self-contained without needing DYLD_LIBRARY_PATH
set -euo pipefail

PG_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$PG_DIR/bin"
LIB_DIR="$PG_DIR/lib"

echo "Fixing library paths in bundled PostgreSQL..."

# All known absolute paths that need rewriting (original -> filename)
ORIG_PATHS=(
  "/opt/homebrew/opt/gettext/lib/libintl.8.dylib"
  "/opt/homebrew/opt/zstd/lib/libzstd.1.dylib"
  "/opt/homebrew/opt/lz4/lib/liblz4.1.dylib"
  "/opt/homebrew/opt/openssl@3/lib/libssl.3.dylib"
  "/opt/homebrew/opt/openssl@3/lib/libcrypto.3.dylib"
  "/opt/homebrew/opt/krb5/lib/libgssapi_krb5.2.2.dylib"
  "/opt/homebrew/Cellar/krb5/1.22.2/lib/libgssapi_krb5.2.2.dylib"
  "/opt/homebrew/Cellar/krb5/1.22.2/lib/libkrb5.3.3.dylib"
  "/opt/homebrew/Cellar/krb5/1.22.2/lib/libk5crypto.3.1.dylib"
  "/opt/homebrew/Cellar/krb5/1.22.2/lib/libcom_err.3.0.dylib"
  "/opt/homebrew/Cellar/krb5/1.22.2/lib/libkrb5support.1.1.dylib"
  "/opt/homebrew/opt/icu4c@78/lib/libicui18n.78.dylib"
  "/opt/homebrew/opt/icu4c@78/lib/libicuuc.78.dylib"
  "/opt/homebrew/opt/icu4c@78/lib/libicudata.78.dylib"
  "/opt/homebrew/opt/postgresql@15/lib/libpq.5.dylib"
)

# Make everything writable
chmod -R u+w "$BIN_DIR" "$LIB_DIR" 2>/dev/null || true

# Fix binaries
for bin in "$BIN_DIR"/*; do
  [ -f "$bin" ] || continue
  echo "  Fixing binary: $(basename "$bin")"
  for orig in "${ORIG_PATHS[@]}"; do
    local_name="$(basename "$orig")"
    install_name_tool -change "$orig" "@executable_path/../lib/$local_name" "$bin" 2>/dev/null || true
  done
  # Also catch any versioned Cellar paths (openssl version may vary)
  for ref in $(otool -L "$bin" 2>/dev/null | grep "/opt/homebrew" | awk '{print $1}'); do
    local_name="$(basename "$ref")"
    install_name_tool -change "$ref" "@executable_path/../lib/$local_name" "$bin" 2>/dev/null || true
  done
  codesign --force --sign - "$bin" 2>/dev/null || true
done

# Fix dylibs (they reference each other)
for lib in "$LIB_DIR"/*.dylib; do
  [ -f "$lib" ] || continue
  echo "  Fixing dylib: $(basename "$lib")"
  # Change the install name ID
  install_name_tool -id "@loader_path/$(basename "$lib")" "$lib" 2>/dev/null || true
  # Change references to other libs
  for orig in "${ORIG_PATHS[@]}"; do
    local_name="$(basename "$orig")"
    install_name_tool -change "$orig" "@loader_path/$local_name" "$lib" 2>/dev/null || true
  done
  # Also catch any versioned Cellar paths (openssl version may vary)
  for ref in $(otool -L "$lib" 2>/dev/null | grep "/opt/homebrew" | awk '{print $1}'); do
    local_name="$(basename "$ref")"
    install_name_tool -change "$ref" "@loader_path/$local_name" "$lib" 2>/dev/null || true
  done
  codesign --force --sign - "$lib" 2>/dev/null || true
done

# Verify no absolute paths remain
echo ""
echo "Verification:"
REMAINING=$(for f in "$BIN_DIR"/* "$LIB_DIR"/*.dylib; do otool -L "$f" 2>/dev/null | grep "/opt/homebrew" || true; done)
if [ -z "$REMAINING" ]; then
  echo "  All paths are relative. Success!"
else
  echo "  WARNING: Some absolute paths remain:"
  echo "$REMAINING"
  exit 1
fi
