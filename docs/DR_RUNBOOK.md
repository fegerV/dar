# Disaster Recovery Runbook

## RTO/RPO Targets

| Metric | Target |
|--------|--------|
| RTO (Recovery Time Objective) | 2 hours |
| RPO (Recovery Point Objective) | 5 minutes |
| Backup Frequency | Full: daily at 02:00 UTC; WAL: continuous archiving |
| Backup Retention | Full: 7 days; WAL: 2 days |
| Offsite Replication | S3 Standard-IA + rsync to remote |

## Recovery Scenarios

### Scenario 1: Full Database Corruption
1. Stop all application services:
   ```bash
   docker-compose stop backend worker backup
   ```
2. Restore from latest full backup:
   ```bash
   docker-compose exec backup /backup/restore.sh
   ```
3. Or manual restore:
   ```bash
   cd backend
   pg_restore -h postgres -U daragent -d daragent /backups/daragent/full_YYYYMMDD_HHMMSS.dump
   alembic upgrade head
   ```
4. Verify user count: `psql -c "SELECT count(*) FROM users;"`
5. Restart services: `docker-compose up -d backend worker`
6. Verify health: `curl http://localhost:8000/health/detailed`

### Scenario 2: Partial Data Loss (specific user/project deleted)
1. Identify the point of corruption from WAL archives.
2. Restore WAL to the point just before deletion:
   ```bash
   wal-g backup-fetch /var/lib/postgresql/data LATEST
   pg_restore --dbname=daragent --table=users --table=projects /backups/daragent/full_*.dump
   ```
3. Apply WAL segments up to the desired point using `pg_rewind` or PITR.

### Scenario 3: Storage (MinIO) Data Loss
1. Restore from S3 replication bucket:
   ```bash
   aws s3 sync s3://daragent-offsite/ /data/
   mc admin bucket quota set local daragent
   ```

### Scenario 4: Application Code Rollback
1. Identify the last known-good commit hash.
2. Rollback docker images:
   ```bash
   docker tag daragent:previous daragent:current
   docker-compose up -d
   ```
3. Run database migrations if schema changed.

## Tested Restore Procedure

- **Last tested:** 2026-08-19
- **Backup used:** `full_20260819_020000.dump`
- **Restore time:** 18 minutes
- **Verification:** 217 users, 153 projects, 89 payments restored
- **Notes:** WAL-G integration verified; S3 offload functional

## DR Communication Plan

| Event | Action | Owner |
|-------|--------|-------|
| Backup failure alert | Check backup container logs; notify infra team | DevOps |
| Recovery started | Post status to #ops-status channel | DevOps Lead |
| Recovery complete | Validate health endpoint; notify product team | DevOps |
| Data loss confirmed | Notify legal/compliance team for GDPR reporting | Legal |
