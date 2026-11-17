#!/bin/bash
# ============================================================
# Smart Tourist Safety and Emergency Response System
# Database Setup & Schema Deployment Script
# ============================================================

set -e

DB_NAME="tourist_safety_db"
DB_USER="tourist_admin"
DB_PASS="tourist_safe_2024"
SCHEMA_PATH="$(dirname "$0")/schema.sql"

SEED_PATH="$(dirname "$0")/seed.sql"

echo "============================================================"
echo "Initializing PostgreSQL Database: $DB_NAME"
echo "============================================================"

# Step 1: Create Role and Database using postgres superuser (via sudo)
echo "[1/4] Ensuring role '$DB_USER' and database '$DB_NAME' exist..."
sudo -u postgres psql << EOF
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
      CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASS' CREATEDB;
      RAISE NOTICE 'Role % created', '$DB_USER';
   ELSE
      ALTER ROLE $DB_USER WITH PASSWORD '$DB_PASS' CREATEDB;
      RAISE NOTICE 'Role % password updated', '$DB_USER';
   END IF;
END
\$\$;

SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
GRANT ALL ON SCHEMA public TO $DB_USER;
EOF

# Step 2: Test connection with tourist_admin credentials
echo "[2/4] Verifying connection with $DB_USER..."
PGPASSWORD="$DB_PASS" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT current_database(), current_user;"

# Step 3: Apply schema.sql
echo "[3/4] Applying schema.sql (DDL)..."
PGPASSWORD="$DB_PASS" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -f "$SCHEMA_PATH"

# Step 4: Apply seed.sql
echo "[4/4] Applying seed.sql (Sample Data)..."
PGPASSWORD="$DB_PASS" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -f "$SEED_PATH"

echo "============================================================"
echo "Database schema and seed data initialized successfully!"
echo "============================================================"
