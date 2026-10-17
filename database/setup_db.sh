#!/bin/bash
# ============================================================
# Smart Tourist Safety and Emergency Response System
# Database Schema Deployment Script
# ============================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    # .env is a local trusted configuration file; do not commit it.
    . "$PROJECT_ROOT/.env"
    set +a
fi
DB_NAME="${DATABASE_NAME:-tourist_safety_db}"
DB_USER="${DATABASE_USER:-tourist_admin}"
DB_HOST="${DATABASE_HOST:-localhost}"
DB_PORT="${DATABASE_PORT:-5432}"
DB_PASS="${DATABASE_PASSWORD:-}"
if [ -z "$DB_PASS" ]; then
    echo "Set DATABASE_PASSWORD in .env or the environment before running setup." >&2
    exit 1
fi
SCHEMA_PATH="$(dirname "$0")/schema.sql"

SEED_PATH="$(dirname "$0")/seed.sql"

echo "============================================================"
echo "Applying project schema and seed data to PostgreSQL database: $DB_NAME"
echo "============================================================"

echo "[1/3] Verifying connection with $DB_USER..."
PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT current_database(), current_user;"

# This schema drops/recreates project tables; use only on a disposable database.
echo "[2/3] Applying schema.sql (this resets project tables)..."
PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCHEMA_PATH"

echo "[3/3] Applying seed.sql (resets sample data)..."
PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SEED_PATH"

echo "============================================================"
echo "Database schema and seed data initialized successfully!"
echo "============================================================"
