#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups/daragent}"
RETENTION_DAYS="${BACKUP_FULL_RETENTION_DAYS:-7}"
WAL_RETENTION_DAYS="${WAL_RETENTION_DAYS:-2}"
PGHOST="${POSTGRES_HOST:-postgres}"
PGPORT="${POSTGRES_PORT:-5432}"
PGUSER="${POSTGRES_USER:-daragent}"
PGDATABASE="${POSTGRES_DB:-daragent}"
PGPASSWORD="${POSTGRES_PASSWORD:-daragent}"

export PGPASSWORD

mkdir -p "$BACKUP_DIR"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting backup..."

FULL_BACKUP_FILE="$BACKUP_DIR/full_$(date +%Y%m%d_%H%M%S).dump"
pg_dump -Fc -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f "$FULL_BACKUP_FILE"
echo "Full backup completed: $FULL_BACKUP_FILE"

if command -v wal-g &>/dev/null; then
    export WALG_POSTGRES_USER="$PGUSER"
    export WALG_POSTGRES_PASSWORD="$PGPASSWORD"
    export WALG_POSTGRES_HOST="$PGHOST"
    export WALG_POSTGRES_PORT="$PGPORT"
    export WALG_POSTGRES_DB="$PGDATABASE"

    WALG_TMP_DIR="${WALG_TMP_DIR:-/tmp/wal-g}"
    export WALG_TMP_DIR

    if [ -z "${WALG_S3_PREFIX:-}" ]; then
        echo "WAL-G S3 prefix not set; skipping offsite WAL archive."
    else
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Archiving WAL segments to S3..."
        wal-g wal push /var/lib/postgresql/data/pg_wal
        echo "WAL archive completed."
    fi

    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Pushing full backup to S3..."
    wal-g backup-push /var/lib/postgresql/data
else
    echo "wal-g not installed; skipping WAL archiving."
fi

echo "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -type f -name "full_*.dump" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -type f -name "wal_*.log" -mtime +$WAL_RETENTION_DAYS -delete

if [ -n "${OFFSITE_RSYNC_TARGET:-}" ]; then
    echo "Syncing backups to offsite: $OFFSITE_RSYNC_TARGET"
    rsync -av --delete "$BACKUP_DIR/" "$OFFSITE_RSYNC_TARGET"
    echo "Offsite sync completed."
fi

if [ -n "${OFFSITE_S3_BUCKET:-}" ]; then
    echo "Syncing backups to S3: $OFFSITE_S3_BUCKET"
    aws s3 sync "$BACKUP_DIR/" "s3://$OFFSITE_S3_BUCKET/backups/" --storage-class STANDARD_IA
    echo "S3 sync completed."
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Backup process completed."

cat > "$BACKUP_DIR/last_backup" <<EOF
backup_file=$FULL_BACKUP_FILE
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
retention_days=$RETENTION_DAYS
wal_retention_days=$WAL_RETENTION_DAYS
EOF
