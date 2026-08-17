# Disaster Recovery Runbook

## RTO / RPO
- RTO: 2 hours
- RPO: 15 minutes

## Recovery Steps
1. Restore PostgreSQL from latest full backup + WAL replay.
2. Redeploy backend/worker containers from last known good image.
3. Verify MinIO object sync from offsite.
4. Run smoke tests: `/health`, `/api/v1/auth/login`, payment webhook endpoint.
5. Notify status page and stakeholders.

## Failover
- Database replica promotion via Patroni or managed PostgreSQL failover.
- Worker queue drained or requeued with idempotency keys.

## Testing
- Monthly DR drill: simulate DB loss, restore from backup, measure RTO.
