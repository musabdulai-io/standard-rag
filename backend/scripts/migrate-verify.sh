#!/usr/bin/env bash
set -euo pipefail

SERVICE_ID="${CLOUD_DEPLOY_TARGET}"          # e.g. myapp-production-backend
REGION="${CLOUD_DEPLOY_LOCATION}"            # e.g. us-central1
PROJECT="${PROJECT_ID:-${GOOGLE_CLOUD_PROJECT:-${CLOUD_DEPLOY_PROJECT_ID:-${CLOUD_DEPLOY_PROJECT:-}}}}"

if [[ -z "${SERVICE_ID}" || -z "${REGION}" || -z "${PROJECT}" ]]; then
  echo "Required Cloud Deploy environment variables are missing" >&2
  exit 1
fi

# Split target into base + environment (expects <base>-<env>-backend)
ENV_SEGMENT=$(echo "$SERVICE_ID" | rev | cut -d'-' -f2 | rev)
BASE_SEGMENT=$(echo "$SERVICE_ID" | sed "s/-${ENV_SEGMENT}-backend$//")

SERVICE_NAME="${BASE_SEGMENT}-${ENV_SEGMENT}-backend"
SECRET_NAME="${BASE_SEGMENT}-${ENV_SEGMENT}-DATABASE_URL"

echo "Running database migrations for ${SERVICE_NAME}"

# Ensure gcloud CLI can write its config (the app user has HOME=/nonexistent)
CONFIG_DIR="${CLOUDSDK_CONFIG:-/tmp/gcloud}"
mkdir -p "$CONFIG_DIR"
export CLOUDSDK_CONFIG="$CONFIG_DIR"
export XDG_CONFIG_HOME="$CONFIG_DIR"

# Helper to fetch optional app configs, defaulting to empty string when missing
fetch_optional_secret() {
  local key="$1"
  local secret="${BASE_SEGMENT}-${ENV_SEGMENT}-${key}"
  gcloud secrets versions access latest --project "$PROJECT" --secret="$secret" 2>/dev/null || echo ""
}

# Fetch required DATABASE_URL first
DATABASE_URL=$(gcloud secrets versions access latest --project "$PROJECT" --secret="$SECRET_NAME")
if [[ -z "$DATABASE_URL" ]]; then
  echo "Unable to retrieve DATABASE_URL from secret $SECRET_NAME" >&2
  exit 1
fi

# Handle Cloud SQL connections in Cloud Build (without /cloudsql mount)
# If DATABASE_URL uses Unix socket, start Cloud SQL Auth Proxy and rewrite URL
if [[ "$DATABASE_URL" == *"/cloudsql/"* ]]; then
  echo "Detected Cloud SQL Unix socket in DATABASE_URL - setting up Cloud SQL Auth Proxy..."

  # Extract instance connection name from DATABASE_URL
  # Format: postgresql+asyncpg://user:pass@/db?host=/cloudsql/PROJECT:REGION:INSTANCE
  INSTANCE_CONNECTION=$(echo "$DATABASE_URL" | grep -oP '/cloudsql/\K[^/]+')

  if [[ -z "$INSTANCE_CONNECTION" ]]; then
    echo "ERROR: Could not extract Cloud SQL instance connection name from DATABASE_URL" >&2
    exit 1
  fi

  echo "Cloud SQL instance: $INSTANCE_CONNECTION"

  # Start Cloud SQL Auth Proxy in background on port 5432
  cloud-sql-proxy --port 5432 "$INSTANCE_CONNECTION" &
  PROXY_PID=$!

  # Ensure proxy is killed on script exit
  trap "echo 'Stopping Cloud SQL Auth Proxy...'; kill $PROXY_PID 2>/dev/null || true" EXIT

  # Wait a moment for proxy to start
  sleep 3

  # Parse DATABASE_URL to extract credentials and database name
  # Extract everything between :// and @/
  CREDENTIALS=$(echo "$DATABASE_URL" | grep -oP '://\K[^@]+')
  # Extract database name (between @/ and ?)
  DB_NAME=$(echo "$DATABASE_URL" | grep -oP '@/\K[^?]+')
  # Extract driver (postgresql or postgresql+asyncpg)
  DRIVER=$(echo "$DATABASE_URL" | grep -oP '^[^:]+')

  # Reconstruct DATABASE_URL to use localhost
  DATABASE_URL="${DRIVER}://${CREDENTIALS}@localhost:5432/${DB_NAME}"

  echo "Rewritten DATABASE_URL to use localhost TCP connection"
fi

# Export env vars needed by Settings()/migrations
export DATABASE_URL
SERVICE_NAME_VALUE="$(fetch_optional_secret SERVICE_NAME)"
GCP_PROJECT_ID_VALUE="$(fetch_optional_secret GCP_PROJECT_ID)"
ENVIRONMENT_VALUE="$(fetch_optional_secret ENVIRONMENT)"

export SERVICE_NAME="${SERVICE_NAME_VALUE:-$BASE_SEGMENT}"
export GCP_PROJECT_ID="${GCP_PROJECT_ID_VALUE:-$PROJECT}"
export ENVIRONMENT="${ENVIRONMENT_VALUE:-$ENV_SEGMENT}"

# The migration files and alembic are already in this container (inherited from backend image)
# Change to the app directory where alembic.ini lives
cd /app

echo "Running alembic upgrade head..."
alembic upgrade head

echo "Migrations completed successfully for $SERVICE_NAME"
