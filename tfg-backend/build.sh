#!/usr/bin/env bash
# Script que Render ejecuta al desplegar

set -o errexit  # corta el deploy si algo falla

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate