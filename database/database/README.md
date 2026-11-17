# Database Management Subsystem

This directory contains the database design specifications, DDL schema scripts, and seed data for the **Smart Tourist Safety and Emergency Response System**.

## Contents

- `schema.sql`: PostgreSQL DDL script creating all 9 tables, constraints, foreign keys with ON DELETE rules, and performance indexes.
- `seed.sql`: Realistic seed data including safe/dangerous zones, rescue teams, resources, tourists, emergency contacts, GPS trails, sample incidents, assignments, and audit logs.
- `setup_db.sh`: Automated bash script to create the PostgreSQL role, database, permissions, and deploy both `schema.sql` and `seed.sql`.
- `load_schema.py`: Python utility to deploy `schema.sql` directly over `psycopg2`.
- `load_seed.py`: Python utility to load `seed.sql` directly over `psycopg2`.
- `verify_schema.py`: Automated Python verification script testing database connectivity, table existence, foreign keys, indexes, and record counts using `psycopg2`.

## Design Documentation

For complete Entity-Relationship diagrams, Data Dictionaries, 3NF Normalization proofs, and Concurrency specifications, see:
- [`docs/DATABASE_DESIGN.md`](../docs/DATABASE_DESIGN.md)

## Quick Schema Overview

| Entity | Purpose | Key Relationships |
|---|---|---|
| `tourists` | Registered mobile users | 1:N with contacts, locations, incidents |
| `emergency_contacts` | Next-of-kin / embassy contacts | N:1 with tourists (CASCADE) |
| `safe_dangerous_zones` | Geofence polygons / circles | 1:N with locations (SET NULL) |
| `locations` | Tourist GPS track points | N:1 with tourists (CASCADE) |
| `emergency_incidents` | Safety alerts, SOS, accident calls | N:1 with tourists (RESTRICT) |
| `emergency_logs` | Immutable audit trail of operations | N:1 with incidents (CASCADE) |
| `rescue_teams` | Specialised response squads | 1:N with assignments (SET NULL) |
| `resources` | Physical vehicles & equipment | 1:N with assignments (SET NULL) |
| `resource_assignments` | Junction table for dispatches | Links incidents, teams, and resources |
