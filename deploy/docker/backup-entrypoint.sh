#!/usr/bin/env sh
set -e

echo "[backup] initializing backup service..."

# Install required tools (pg_dump, gzip, rsync, curl) if missing
if ! command -v pg_dump >/dev/null 2>&1 || ! command -v rsync >/dev/null 2>&1; then
  echo "[backup] installing required packages..."
  # Alpine package manager
  if command -v apk >/dev/null 2>&1; then
    apk add --no-cache postgresql-client rsync curl coreutils findutils busybox-extras
  else
    echo "[backup] WARNING: apk not found; ensure pg_dump and rsync are available in image"
  fi
fi

# Prepare backup directories
mkdir -p /backups/db /backups/media

# Export current environment for cron jobs
printenv | sed 's/^/export /' > /etc/environment

# Build crontab
CRON_FILE="/etc/crontabs/root"
echo "SHELL=/bin/sh" > "$CRON_FILE"
echo "PATH=/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/bin" >> "$CRON_FILE"

if [ -n "$DB_BACKUP_CRON" ]; then
  echo "$DB_BACKUP_CRON . /etc/environment; /usr/local/bin/backup.sh db >> /var/log/cron.log 2>&1" >> "$CRON_FILE"
fi

if [ -n "$MEDIA_BACKUP_CRON" ]; then
  echo "$MEDIA_BACKUP_CRON . /etc/environment; /usr/local/bin/backup.sh media >> /var/log/cron.log 2>&1" >> "$CRON_FILE"
fi

touch /var/log/cron.log
echo "[backup] starting crond..."
exec crond -f -l 8