# Production Security Baseline

## Network
- Cloudflare in front of all public endpoints.
- Firewall rules: only 80/443 inbound.
- SSH restricted to bastion/VPN.

## Application
- HTTPS only, HSTS enabled.
- JWT access + refresh tokens, short expiry.
- Rate limiting per IP/user.
- Request validation + MIME/size checks on uploads.
- Non-root Docker containers.

## Secrets
- All secrets in Vault / AWS Secrets Manager.
- No secrets in repo or logs.
- Rotation policy: 90 days.

## Monitoring
- Audit logs for admin actions.
- Alerting on auth failures, payment anomalies, queue depth.
