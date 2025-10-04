#!/usr/bin/env sh
set -e

FILE_PATH="$1"

if [ -z "$FILE_PATH" ]; then
  echo "Usage: restore_db.sh <dump.sql.gz|dump.sql>" >&2
  exit 2
fi

if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL is not set" >&2
  exit 1
fi

echo "[restore] restoring database from $FILE_PATH ..."
if echo "$FILE_PATH" | grep -qE '\.gz$'; then
  gunzip -c "$FILE_PATH" | psql "$DATABASE_URL"
else
  psql "$DATABASE_URL" < "$FILE_PATH"
fi
echo "[restore] database restore completed."