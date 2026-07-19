#!/usr/bin/env sh
set -eu

echo "Waiting for PostgreSQL at ${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}..."

until python - <<'PY'
import os
import sys

import psycopg2

try:
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "moderation"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )
    conn.close()
except psycopg2.OperationalError:
    sys.exit(1)
PY
do
  sleep 2
done

echo "PostgreSQL is ready. Running migrations..."
python manage.py migrate --noinput
