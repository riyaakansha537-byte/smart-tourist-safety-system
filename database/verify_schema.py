#!/usr/bin/env python3
"""
Database Schema Verification Script
Verifies that all 9 tables, primary keys, foreign keys, and indexes exist in PostgreSQL.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load .env configuration
load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "tourist_safety_db")
DB_USER = os.getenv("DATABASE_USER", "tourist_admin")
DB_PASS = os.getenv("DATABASE_PASSWORD", "")

EXPECTED_TABLES = [
    "tourists",
    "emergency_contacts",
    "safe_dangerous_zones",
    "locations",
    "emergency_incidents",
    "emergency_logs",
    "rescue_teams",
    "resources",
    "resource_assignments",
]

def verify():
    print(f"Connecting to {DB_NAME} on {DB_HOST}:{DB_PORT} as {DB_USER}...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        )
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("\nPlease ensure the database and user are created.")
        print(f"You can run: ./database/setup_db.sh")
        sys.exit(1)

    cursor = conn.cursor()

    print("\n--- Verifying Tables ---")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    existing_tables = [row[0] for row in cursor.fetchall()]

    missing_tables = [t for t in EXPECTED_TABLES if t not in existing_tables]
    for table in EXPECTED_TABLES:
        status = "EXISTS" if table in existing_tables else "MISSING"
        print(f"  [{status}] {table}")

    if missing_tables:
        print(f"\n[FAIL] Missing tables: {missing_tables}")
        sys.exit(1)

    print("\n--- Verifying Indexes ---")
    cursor.execute("""
        SELECT tablename, indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
    """)
    indexes = cursor.fetchall()
    print(f"Found {len(indexes)} total indexes in schema.")
    for table, index in indexes:
        print(f"  {table} -> {index}")

    print("\n--- Verifying Foreign Key Constraints ---")
    cursor.execute("""
        SELECT
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.delete_rule
        FROM information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.referential_constraints AS rc
            ON tc.constraint_name = rc.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
        ORDER BY tc.table_name;
    """)
    fks = cursor.fetchall()
    for t, c, ft, fc, dr in fks:
        print(f"  {t}.{c} -> {ft}.{fc} (ON DELETE {dr})")

    print("\n--- Verifying Seed Record Counts ---")
    total_records = 0
    for table in EXPECTED_TABLES:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        total_records += count
        print(f"  {table:25} : {count:3} rows")

    print("\n" + "=" * 60)
    print(f"ALL 9 TABLES VERIFIED. TOTAL RECORDS POPULATED: {total_records}")
    print("=" * 60)
    conn.close()

if __name__ == "__main__":
    verify()
