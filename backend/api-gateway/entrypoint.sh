#!/usr/bin/env sh
set -eu

sh migrate.sh
exec python manage.py runserver 0.0.0.0:8000
