#!/usr/bin/env bash
# Script de build pour Render

set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
