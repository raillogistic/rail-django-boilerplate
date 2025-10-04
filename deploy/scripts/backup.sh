#!/usr/bin/env sh
set -e

COMMAND="$1"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

if [ "$COMMAND" = "db" ]; then
  echo "[backup] running DB backup..."
  mkdir -p ${DB_BACKUPS_DIR:-/backups/db}
  if [ -z "$DATABASE_URL" ]; then
    echo "DATABASE_URL is not set" >&2
    exit 1
  fi
  pg_dump "$DATABASE_URL" | gzip > "${DB_BACKUPS_DIR:-/backups/db}/db-${TIMESTAMP}.sql.gz"
  echo "[backup] DB backup completed."
elif [ "$COMMAND" = "media" ]; then
  echo "[backup] running media backup..."
  mkdir -p ${MEDIA_BACKUPS_DIR:-/backups/media}
  rsync -a --delete "${MEDIA_ROOT:-/app/media}/" "${MEDIA_BACKUPS_DIR:-/backups/media}/"
  echo "[backup] media backup completed."
else
  echo "Usage: backup.sh [db|media]" >&2
  exit 2
fi