#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups/daragent}"
PGHOST="${POSTGRES_HOST:-postgres}"
PGPORT="${POSTGRES_PORT:-5432}"
PGUSER="${POSTGRES_USER:-daragent}"
PGDATABASE="${POSTGRES_DB:-daragent}"
PGPASSWORD="${POSTGRES_PASSWORD:-daragent}"
RESTORE_FILE="${1:-}"

export PGPASSWORD

if [ -z "$RESTORE_FILE" ]; then
    echo "Usage: $0 <backup_file_or_timestamp>"
    echo "Available backups:"
    ls -lt "$BACKUP_DIR"/full_*.dump 2>/dev/null || echo "No backup files found."
    exit 1
fi

if [ -f "$RESTORE_FILE" ]; then
    BACKUP_PATH="$RESTORE_FILE"
else
    BACKUP_PATH=$(ls -t "$BACKUP_DIR"/full_*.dump 2>/dev/null | grep -m1 "$RESTORE_FILE")
    if [ -z "$BACKUP_PATH" ]; then
        echo "Backup file matching '$RESTORE_FILE' not found."
        exit 1
    fi
fi

echo "Restoring from: $BACKUP_PATH"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Stopping application services..."
if [ -f /app/pids/backend.pid ]; then
    kill "$(cat /app/pids/backend.pid)" 2>/dev/null || true
fi
if [ -f /app/pids/worker.pid ]; then
    kill "$(cat /app/pids/worker.pid)" 2>/dev/null || true
fi
sleep 2

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Dropping and recreating database..."
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "DROP DATABASE IF EXISTS ${PGDATABASE}_old;"
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "ALTER DATABASE ${PGDATABASE} RENAME TO ${PGDATABASE}_old;" 2>/dev/null || true
createdb -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Restoring database..."
pg_restore -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" --no-owner --no-privileges "$BACKUP_PATH"

if command -v wal-g &>/dev/null; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Restoring WAL segments..."
    wal-g wal push "$PGDATABASE" --target-user "$PGUSER" --target-host "$PGHOST" --target-port "$PGPORT" || true
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Running database migrations..."
cd /app/backend && alembic upgrade head

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Restart application services..."
cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &
echo $! > /app/pids/backend.pid

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Restore completed. Verifying..."
python3 -c "
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$PGDATABASE')
with engine.connect() as conn:
    result = conn.execute(text('SELECT count(*) FROM users'))
    print(f'Users in restored DB: {result.scalar()}')
"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Restore complete."
