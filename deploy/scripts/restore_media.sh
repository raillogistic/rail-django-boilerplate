#!/usr/bin/env sh
set -e

SOURCE_DIR="$1"
TARGET_DIR="${MEDIA_ROOT:-/app/media}"

if [ -z "$SOURCE_DIR" ]; then
  echo "Usage: restore_media.sh <backup_dir>" >&2
  exit 2
fi

echo "[restore] restoring media from $SOURCE_DIR to $TARGET_DIR ..."
mkdir -p "$TARGET_DIR"
rsync -a "$SOURCE_DIR/" "$TARGET_DIR/"
echo "[restore] media restore completed."