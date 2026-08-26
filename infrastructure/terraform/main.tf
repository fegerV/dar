# DarAgent Infrastructure Configuration
# This Terraform configuration sets up the production infrastructure

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.0"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "daragent"
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "redis_password" {
  description = "Redis password"
  type        = string
  sensitive   = true
  default     = ""
}

variable "secret_key" {
  description = "Application secret key"
  type        = string
  sensitive   = true
}

variable "polza_api_key" {
  description = "Polza AI API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "domain" {
  description = "Application domain"
  type        = string
  default     = "daragent.ru"
}

# Networks
resource "docker_network" "frontend" {
  name = "${var.app_name}-frontend"
  driver = "bridge"
}

resource "docker_network" "backend" {
  name = "${var.app_name}-backend"
  driver = "bridge"
  internal = true
}

resource "docker_network" "monitoring" {
  name = "${var.app_name}-monitoring"
  driver = "bridge"
}

# Volumes
resource "docker_volume" "postgres_data" {
  name = "${var.app_name}-postgres-data"
}

resource "docker_volume" "redis_data" {
  name = "${var.app_name}-redis-data"
}

resource "docker_volume" "prometheus_data" {
  name = "${var.app_name}-prometheus-data"
}

resource "docker_volume" "grafana_data" {
  name = "${var.app_name}-grafana-data"
}

resource "docker_volume" "loki_data" {
  name = "${var.app_name}-loki-data"
}

# PostgreSQL Container
resource "docker_container" "postgres" {
  name  = "${var.app_name}-postgres"
  image = "postgres:16-alpine"

  env = [
    "POSTGRES_USER=${var.app_name}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.app_name}",
  ]

  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }

  networks_advanced {
    name = docker_network.backend.name
  }

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U ${var.app_name}"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }

  restart = "unless-stopped"
}

# Redis Container
resource "docker_container" "redis" {
  name  = "${var.app_name}-redis"
  image = "redis:7-alpine"

  volumes {
    volume_name    = docker_volume.redis_data.name
    container_path = "/data"
  }

  networks_advanced {
    name = docker_network.backend.name
  }

  healthcheck {
    test     = ["CMD", "redis-cli", "ping"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }

  restart = "unless-stopped"
}

# Backend Container
resource "docker_container" "backend" {
  name  = "${var.app_name}-backend"
  image = "ghcr.io/fegerv/dar:latest-backend"

  env = [
    "DATABASE_URL=postgresql+asyncpg://${var.app_name}:${var.postgres_password}@${docker_container.postgres.name}:5432/${var.app_name}",
    "REDIS_URL=redis://${docker_container.redis.name}:6379/0",
    "SECRET_KEY=${var.secret_key}",
    "POLZA_API_KEY=${var.polza_api_key}",
  ]

  ports {
    internal = 8000
    external = 8000
  }

  networks_advanced {
    name = docker_network.frontend.name
  }

  networks_advanced {
    name = docker_network.backend.name
  }

  networks_advanced {
    name = docker_network.monitoring.name
  }

  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval = "30s"
    timeout  = "10s"
    retries  = 3
  }

  depends_on = [docker_container.postgres, docker_container.redis]
  restart   = "unless-stopped"
}

# Frontend Container
resource "docker_container" "frontend" {
  name  = "${var.app_name}-frontend"
  image = "ghcr.io/fegerv/dar:latest-frontend"

  env = [
    "NEXT_PUBLIC_API_URL=http://localhost:8000",
  ]

  ports {
    internal = 3000
    external = 3000
  }

  networks_advanced {
    name = docker_network.frontend.name
  }

  depends_on = [docker_container.backend]
  restart   = "unless-stopped"
}

# Outputs
output "backend_url" {
  value = "http://localhost:8000"
}

output "frontend_url" {
  value = "http://localhost:3000"
}

output "database_host" {
  value = docker_container.postgres.name
}

output "redis_host" {
  value = docker_container.redis.name
}
