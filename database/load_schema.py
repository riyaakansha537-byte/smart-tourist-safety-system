#!/usr/bin/env python3
"""
Schema DDL Loader Script
Executes database/schema.sql using psycopg2 with .env credentials.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "tourist_safety_db")
DB_USER = os.getenv("DATABASE_USER", "tourist_admin")
DB_PASS = os.getenv("DATABASE_PASSWORD", "")

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")

def load_schema():
    print(f"Connecting to {DB_NAME} on {DB_HOST}:{DB_PORT} as {DB_USER}...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        )
        conn.autocommit = True
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("Please ensure the database exists and credentials are correct.")
        sys.exit(1)

    print(f"Reading schema DDL from {SCHEMA_FILE}...")
    with open(SCHEMA_FILE, "r") as f:
        sql = f.read()

    print("Executing schema.sql...")
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        print("Schema DDL successfully executed!")
    except Exception as e:
        print(f"[ERROR] Failed to execute schema SQL: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    load_schema()
