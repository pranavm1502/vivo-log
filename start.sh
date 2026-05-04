#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "==> Starting PostgreSQL..."
docker compose up -d db
echo "    Waiting for PostgreSQL to be ready..."
until docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do
  sleep 1
done
echo "    PostgreSQL is ready."

echo "==> Setting up backend..."
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  python3.12 -m venv .venv
fi
source .venv/bin/activate
pip install -q -e ".[dev]" 2>&1 | tail -1

echo "==> Running database migrations..."
alembic upgrade head

echo "==> Starting backend API server..."
# Kill any stale process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 1
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
sleep 2
echo "    Backend running (PID $BACKEND_PID) at http://localhost:8000"

echo "==> Setting up frontend..."
cd "$ROOT/frontend"
flutter pub get

echo "==> Launching Flutter app..."
flutter run -d macos

# When Flutter exits, clean up the backend
echo "==> Shutting down backend..."
kill $BACKEND_PID 2>/dev/null || true
