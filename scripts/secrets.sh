#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-generate}"
ENV_FILE="${2:-./backend/.env.production}"

generate_secret() {
    local name="$1"
    local length="${2:-32}"
    local value
    value=$(python3 -c "import secrets; print(secrets.token_urlsafe($length))")
    echo "$name=$value" >> "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    echo "Generated $name"
}

case "$ACTION" in
    generate)
        if [ ! -f "$ENV_FILE" ]; then
            touch "$ENV_FILE"
            chmod 600 "$ENV_FILE"
        fi

        echo "Generating secrets for $ENV_FILE..."
        generate_secret "APP_SECRET_KEY" 48
        generate_secret "JWT_SECRET_KEY" 48
        generate_secret "MINIO_ACCESS_KEY" 32
        generate_secret "MINIO_SECRET_KEY" 48
        generate_secret "YOOKASSA_WEBHOOK_SECRET" 32

        echo "POSTGRES_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" >> "$ENV_FILE"
        echo "REDIS_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" >> "$ENV_FILE"

        echo ""
        echo "Secrets generated. Review $ENV_FILE before using."
        echo "Add the following to your secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager):"
        echo "  - APP_SECRET_KEY"
        echo "  - JWT_SECRET_KEY"
        echo "  - MINIO_ACCESS_KEY"
        echo "  - MINIO_SECRET_KEY"
        echo "  - YOOKASSA_SHOP_ID"
        echo "  - YOOKASSA_SECRET_KEY"
        echo "  - YOOKASSA_WEBHOOK_SECRET"
        ;;

    validate)
        required_vars=(
            "APP_SECRET_KEY"
            "JWT_SECRET_KEY"
            "MINIO_ACCESS_KEY"
            "MINIO_SECRET_KEY"
            "DATABASE_URL"
            "YOOKASSA_SHOP_ID"
            "YOOKASSA_SECRET_KEY"
            "YOOKASSA_WEBHOOK_SECRET"
        )
        all_valid=true
        for var in "${required_vars[@]}"; do
            value=$(grep "^${var}=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- || true)
            if [ -z "$value" ] || [ "$value" == "change-me" ] || [ "$value" == "minioadmin" ]; then
                echo "MISSING or WEAK: $var"
                all_valid=false
            fi
        done

        if [ "$all_valid" = true ]; then
            echo "All secrets are properly configured."
            exit 0
        else
            echo "Some secrets are missing or weak. Run with 'generate' to create new ones."
            exit 1
        fi
        ;;

    rotate)
        old_env="${3:-./backend/.env}"
        echo "Rotating secrets..."
        echo "Current timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        generate_secret "APP_SECRET_KEY" 48
        generate_secret "JWT_SECRET_KEY" 48

        echo "WARNING: Rotating JWT_SECRET_KEY invalidates all existing tokens."
        echo "Users will need to re-authenticate."
        ;;

    *)
        echo "Usage: $0 {generate|validate|rotate} [env_file] [old_env_file]"
        echo "  generate  - Generate all required secrets"
        echo "  validate  - Check that all secrets are set and strong"
        echo "  rotate    - Rotate JWT and app secrets (will invalidate sessions)"
        exit 1
        ;;
esac
