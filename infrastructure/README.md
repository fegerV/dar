# DarAgent Infrastructure

## Overview

This directory contains Infrastructure as Code (IaC) configurations for deploying DarAgent.

## Terraform

### Prerequisites

- Terraform >= 1.5.0
- Docker
- Docker provider for Terraform

### Usage

1. Initialize Terraform:
   ```bash
   cd infrastructure/terraform
   terraform init
   ```

2. Plan the deployment:
   ```bash
   terraform plan -var="postgres_password=your_password" -var="secret_key=your_secret"
   ```

3. Apply the configuration:
   ```bash
   terraform apply -var="postgres_password=your_password" -var="secret_key=your_secret"
   ```

4. Destroy the infrastructure:
   ```bash
   terraform destroy
   ```

### Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `environment` | Environment name | No | `production` |
| `app_name` | Application name | No | `daragent` |
| `postgres_password` | PostgreSQL password | Yes | - |
| `redis_password` | Redis password | No | - |
| `secret_key` | Application secret key | Yes | - |
| `polza_api_key` | Polza AI API key | No | - |
| `domain` | Application domain | No | `daragent.ru` |

## Docker Compose

### Development

```bash
docker-compose up -d
```

### Production with Monitoring

```bash
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### Monitoring Stack

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Loki**: http://localhost:3100

## Secrets Management

For production, use HashiCorp Vault or cloud provider secret managers:

### HashiCorp Vault

```bash
vault secrets enable -path=daragent kv-v2

vault kv put daragent/production \
  postgres_password="..." \
  secret_key="..." \
  polza_api_key="..."
```

### Environment Variables

Create a `.env` file (never commit to git):

```env
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key
POLZA_API_KEY=your_polza_api_key
GRAFANA_ADMIN_PASSWORD=your_grafana_password
```

## CI/CD Pipeline

GitHub Actions workflow includes:

1. **Lint**: Ruff (Python), ESLint (TypeScript)
2. **Unit Tests**: pytest, Jest
3. **Integration Tests**: Testcontainers (PostgreSQL, Redis)
4. **E2E Tests**: Playwright
5. **Load Tests**: Locust (100 RPS, p99 < 500ms)
6. **Build**: Docker images
7. **Deploy**: Staging → Production

## Monitoring

### Metrics

- Request rate, latency (p50, p99)
- Error rate
- Queue depth
- Generation success/failure rate
- Database connections
- System resources (CPU, memory, disk)

### Alerts

- Backend down
- High error rate (>5%)
- High latency (p99 > 500ms)
- High CPU/memory usage
- Disk space low
- Queue backlog (>50 jobs)
- High generation failure rate (>10%)

### Dashboards

- DarAgent main dashboard (Grafana)
- Request latency and rate
- Error rate
- Queue status
