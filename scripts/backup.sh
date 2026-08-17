#!/usr/bin/env bash
set -euo pipefail
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/daragent"
mkdir -p "$BACKUP_DIR"
pg_dump -Fc -U "${POSTGRES_USER:-dar}" -d "${POSTGRES_DB:-daragent}" -f "$BACKUP_DIR/db_$DATE.dump"
find "$BACKUP_DIR" -type f -mtime +7 -delete
echo "Backup completed: $BACKUP_DIR/db_$DATE.dump"
