#!/usr/bin/env sh
set -e

COMMAND="$1"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

backup_db() {
  echo "[backup] running DB backup..."
  DB_DIR=${DB_BACKUPS_DIR:-/backups/db}
  mkdir -p "$DB_DIR"
  if [ -z "$DATABASE_URL" ]; then
    echo "DATABASE_URL is not set" >&2
    exit 1
  fi
  OUT_FILE="$DB_DIR/db-${TIMESTAMP}.sql.gz"
  pg_dump "$DATABASE_URL" | gzip > "$OUT_FILE"
  echo "[backup] DB backup written to: $OUT_FILE"

  # Retention policy: delete files older than N days
  RETENTION_DAYS=${DB_BACKUP_RETENTION_DAYS:-7}
  if [ "$RETENTION_DAYS" -gt 0 ] 2>/dev/null; then
    echo "[backup] pruning DB backups older than $RETENTION_DAYS days..."
    find "$DB_DIR" -type f -name 'db-*.sql.gz' -mtime +"$RETENTION_DAYS" -print -delete || true
  fi
  echo "[backup] DB backup completed."
}

backup_media() {
  echo "[backup] running media backup..."
  SRC_DIR=${MEDIA_ROOT:-/app/media}
  DEST_DIR="${MEDIA_BACKUP_TARGET:-${MEDIA_BACKUPS_DIR:-/backups/media}}"

  # Create destination if local
  case "$DEST_DIR" in
    *:*)
      echo "[backup] remote destination detected: $DEST_DIR"
      ;;
    *)
      mkdir -p "$DEST_DIR"
      ;;
  esac

  rsync -a --delete "$SRC_DIR/" "$DEST_DIR/"
  echo "[backup] media backup completed to: $DEST_DIR"
}

case "$COMMAND" in
  db)
    backup_db
    ;;
  media)
    backup_media
    ;;
  *)
    echo "Usage: backup.sh [db|media]" >&2
    exit 2
    ;;
esac