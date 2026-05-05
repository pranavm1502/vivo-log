#!/usr/bin/env bash
# Helper script to initialize and start the bundled PostgreSQL.
# Usage:
#   init_postgres.sh <data_dir> <port>
#
# On first run (data_dir doesn't exist), runs initdb.
# Then starts postgres on the specified port.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PG_BIN="$SCRIPT_DIR/bin"
PG_LIB="$SCRIPT_DIR/lib"
PG_SHARE="$SCRIPT_DIR/share"

DATA_DIR="${1:-$HOME/Library/Application Support/Vivo-Log/db}"
PORT="${2:-5433}"
LOG_DIR="${3:-$HOME/Library/Application Support/Vivo-Log/logs}"

export DYLD_LIBRARY_PATH="$PG_LIB:${DYLD_LIBRARY_PATH:-}"

mkdir -p "$LOG_DIR"

# Initialize if needed
if [ ! -f "$DATA_DIR/PG_VERSION" ]; then
    echo "Initializing PostgreSQL database at $DATA_DIR..."
    mkdir -p "$DATA_DIR"
    "$PG_BIN/initdb" \
        --pgdata="$DATA_DIR" \
        --encoding=UTF8 \
        --locale=en_US.UTF-8 \
        --username=postgres \
        --auth=trust \
        -L "$PG_SHARE" \
        > "$LOG_DIR/initdb.log" 2>&1
    echo "Database initialized."
fi

# Start postgres
echo "Starting PostgreSQL on port $PORT..."
exec "$PG_BIN/postgres" \
    -D "$DATA_DIR" \
    -p "$PORT" \
    -k "" \
    -h "127.0.0.1" \
    > "$LOG_DIR/postgres.log" 2>&1
