# Backup Strategy

## PostgreSQL
- Daily full backup at 02:00 UTC via `pg_dump` / `pg_basebackup`.
- Continuous WAL archiving for point-in-time recovery (PITR).
- Retention: 7 daily + 4 weekly + 12 monthly backups.

## Critical Data
- Template versions
- Wallet ledger
- Payment records
- Generation metadata
- Analytics events

## Object Storage
- Daily sync of MinIO buckets to offsite storage.
- Versioning enabled on media bucket.

## Verification
- Weekly restore test to staging.
- Backup size and checksum monitoring.
