#!/usr/bin/env sh
set -e

echo "[deploy] Starting production deployment..."

# Resolve paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"  # django-graphql-boilerplate
COMPOSE_FILE="$PROJECT_ROOT/deploy/docker-compose.production.yml"
ENV_FILE="$PROJECT_ROOT/deploy/.env.production"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "[deploy] Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "[deploy] Missing env file: $ENV_FILE" >&2
  echo "[deploy] Copy from .env.production.example and set secure values." >&2
  exit 1
fi

echo "[deploy] Bringing up stack with build..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build

echo "[deploy] Applying migrations..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec web python manage.py migrate --noinput

echo "[deploy] Collecting static files..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec web python manage.py collectstatic --noinput

echo "[deploy] Waiting for application health (max ~60s)..."
ATTEMPTS=20
SLEEP=3
for i in $(seq 1 "$ATTEMPTS"); do
  if docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec web curl -fs http://localhost:8000/health/check/ >/dev/null 2>&1; then
    echo "[deploy] App is healthy."
    break
  fi
  echo "[deploy] Attempt $i/$ATTEMPTS: not healthy yet; retrying in ${SLEEP}s..."
  sleep "$SLEEP"
  if [ "$i" -eq "$ATTEMPTS" ]; then
    echo "[deploy] Health check failed. Inspect logs: 'docker compose -f \"$COMPOSE_FILE\" logs web nginx'" >&2
    exit 1
  fi
done

echo "[deploy] Deployment complete. GraphQL: http://localhost/graphql/"