# Smart Tourist Safety and Emergency Response System

[![Tests](https://img.shields.io/badge/Tests-120%20Passed%20(100%25)-success)](pytest.ini)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](backend/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-336791)](database/)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B)](mobile/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-Real--Time-black)](backend/notifications/)

A mission-critical tourist safety monitoring and emergency dispatch platform combining **Operating Systems (OS)** concurrency primitives and **Database Management Systems (DBMS)** design.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CLIENT LAYER                                    │
│   ┌───────────────────────────────────┐    ┌─────────────────────────────┐  │
│   │         Flutter Mobile App        │    │     Authority Dashboard     │  │
│   │    • Digital Safety ID            │    │    • Real-Time GIS Map      │  │
│   │    • 1-Tap SOS Beacon             │    │    • Live Banker's Matrix   │  │
│   │    • Geofence Warning Alerts      │    │    • Multi-Tourist Sim      │  │
│   │    • Emergency Contacts Manager   │    │    • Resource Fleet Monitor │  │
│   └─────────────────┬─────────────────┘    └──────────────┬──────────────┘  │
│                     │                                     │                 │
│                     │ HTTP REST / WebSocket               │ WebSocket       │
└─────────────────────┼─────────────────────────────────────┼─────────────────┘
                      │                                     │
┌─────────────────────┼─────────────────────────────────────┼─────────────────┐
│                     ▼           BACKEND LAYER             ▼                 │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                   Python Flask + Flask-SocketIO                     │   │
│   │                                                                     │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │               OS EVENT PROCESSING ENGINE                    │   │   │
│   │   │                                                             │   │   │
│   │   │  1. Priority Queue       (OS Priority Scheduling)           │   │   │
│   │   │  2. Worker Thread Pool   (OS Multithreading: 3 daemons)     │   │   │
│   │   │  3. Sync Manager         (OS Mutex Locks & Semaphores)      │   │   │
│   │   │  4. Banker's Algorithm   (OS Deadlock Avoidance)            │   │   │
│   │   │  5. IPC Channels         (OS Queues & Duplex Pipes)         │   │   │
│   │   └──────────────────────────────┬──────────────────────────────┘   │   │
│   └──────────────────────────────────┼──────────────────────────────────┘   │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┼──────────────────────────────────────┐
│                                      ▼                                      │
│                                DATABASE LAYER                               │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                  PostgreSQL 16+ Relational DBMS                     │   │
│   │                                                                     │   │
│   │   • ThreadedConnectionPool (min=2, max=10)                          │   │
│   │   • 3NF Normalized Schema across 9 Relational Entities              │   │
│   │   • ACID Transactions with atomicity & rollback guarantees          │   │
│   │   • Foreign Key Cascades & Declarative Domain Check Constraints     │   │
│   │   • High-Performance B-Tree Indexes on Priority & Status            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Academic Concepts Matrix

### Operating Systems (OS) Concepts

| Concept | Implementation File | Key Mechanism Demonstrated |
|---|---|---|
| **Multithreading** | `backend/workers/worker_pool.py` | 3 continuous daemon worker threads consuming from scheduler |
| **Priority Scheduling** | `backend/scheduler/priority_queue.py` | Total ordering: P1 (Accident) > P2 (SOS) > P3 (Zone) > P5 (GPS) |
| **Synchronization** | `backend/resource_manager/synchronization.py`| Mutex Lock (`threading.Lock`) & Semaphore (`threading.Semaphore`) |
| **Deadlock Avoidance** | `backend/resource_manager/bankers_algorithm.py` | Dijkstra's Banker's Algorithm (Available, Max, Alloc, Need) |
| **Inter-Process Comm (IPC)** | `simulation/ipc_demo.py` | `multiprocessing.Queue` & duplex `multiprocessing.Pipe` across PIDs |
| **Resource Allocation** | `backend/resource_manager/resource_manager.py` | Coordinated request, reservation, and release lifecycle |

### Database Management Systems (DBMS) Concepts

| Concept | Implementation File | Key Mechanism Demonstrated |
|---|---|---|
| **Relational Modeling** | `database/schema.sql` | 9 entities with complete ER relationships |
| **3NF Normalization** | `docs/DBMS_CONCEPTS.md` | Formal 1NF, 2NF, and 3NF proof across all relations |
| **Integrity Constraints** | `database/schema.sql` | Primary Keys, Foreign Keys (`ON DELETE CASCADE`), `CHECK` constraints |
| **Connection Pooling** | `backend/db/connection.py` | Thread-safe `ThreadedConnectionPool` (2 min, 10 max connections) |
| **ACID Transactions** | `backend/db/transactions.py` | Atomic multi-step operations using `transaction_scope()` |
| **Indexing Strategy** | `database/schema.sql` | B-Tree indexes on `status`, `priority`, and time telemetry |
| **Concurrency Control** | `docs/DBMS_CONCEPTS.md` | MVCC and Read Committed isolation in PostgreSQL |

---

## Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 16+ (or local setup)
- Flutter SDK (for mobile client)

### 2. Virtual Environment Setup
```bash
# Clone and navigate
cd smart-tourist-safety

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Initialization
```bash
# Set environment variables in .env (or copy .env.example)
cp .env.example .env

# Run automated database setup script
chmod +x database/setup_db.sh
./database/setup_db.sh
```

### 4. Running the Backend Server & Dashboard
```bash
# Run server (Flask + Socket.IO + Static Web Dashboard)
python run_server.py
```
- API Base URL: `http://localhost:5000`
- Authority Command Dashboard: `http://localhost:5000/dashboard`
- API Health Check: `http://localhost:5000/api/health`

### 5. Running the Academic Defense Demonstration
Run the automated CLI scenario showcasing all OS & DBMS concepts in real time:
```bash
python demo_scenario.py
```

### 6. Running the Dedicated IPC Demonstration
```bash
python simulation/ipc_demo.py
```

### 7. Running the Test Suite (120 Tests)
```bash
pytest
```

### Database Backup and Restore

Create a full PostgreSQL schema-and-data archive in `database/backups/`:

```bash
./venv/bin/python database/manage_backup.py backup
./venv/bin/python database/manage_backup.py list
```

To restore a backup into the database configured in `.env`, pass its file path.
The command asks for confirmation because it replaces the objects and data from
that snapshot:

```bash
./venv/bin/python database/manage_backup.py restore database/backups/<backup-file>.dump
```

The backup utility requires PostgreSQL client tools (`pg_dump` and
`pg_restore`). Backups are excluded from Git. For daily backups on Linux, add a
cron entry with the project's absolute path (edit with `crontab -e`):

```cron
0 2 * * * cd /absolute/path/to/smart-tourist-safety && ./venv/bin/python database/manage_backup.py backup >> database/backup.log 2>&1
```

Keep a copy of the backup directory on another disk or machine as well; a
backup stored only beside PostgreSQL will not protect against disk failure.

---

## Flutter Mobile Application

The tourist mobile application is built in Flutter with Material 3 dark styling:

```bash
cd mobile/tourist_app
flutter pub get
flutter run
```

### Mobile Features:
- **Splash Screen:** Animated brand identity with saved session detection.
- **Registration Screen:** Tourist registration (Name, Phone, Email, Blood Group, Nationality).
- **Home Dashboard:** Quick SOS trigger, live simulated telemetry, current zone status.
- **SOS Dispatcher:** Multi-hazard incident selector (Medical, Accident, Water, Cliff).
- **Emergency Contacts:** Add, view, and manage next-of-kin contacts.
- **Incident History:** Track status timeline (QUEUED -> PROCESSING -> DISPATCHED -> RESOLVED).
- **Profile & Diagnostics:** Digital safety card with real-time backend/socket diagnostics.

---

## REST API Specification

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/tourists` | POST, GET | Register and query tourist profiles |
| `/api/tourists/<id>/contacts` | POST, GET, DELETE | Manage emergency contacts |
| `/api/location` | POST | Ingest GPS telemetry & evaluate geofences |
| `/api/emergencies/sos` | POST | Trigger Priority 2 SOS distress beacon |
| `/api/emergencies/accident` | POST | Trigger Priority 1 critical collision report |
| `/api/emergencies` | GET | List and filter active emergency incidents |
| `/api/resources` | GET | List physical apparatus status (Ambulances, etc.) |
| `/api/dashboard/summary` | GET | Ingest consolidated OS and DBMS metrics |
| `/api/dashboard/banker-state` | GET | Real-time Available, Max, Alloc, Need snapshot |

---

## Documentation Index

- [Project Analysis & Roadmap](docs/PROJECT_ANALYSIS.md)
- [Project State & Milestones](docs/PROJECT_STATE.md)
- [OS Concepts Guide](docs/OS_CONCEPTS.md)
- [DBMS Concepts Guide](docs/DBMS_CONCEPTS.md)
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Academic Project Report](docs/PROJECT_REPORT.md)
- [Presentation Slides Outline](docs/PRESENTATION_SLIDES_OUTLINE.md)
- [Database Schema Design](docs/DATABASE_DESIGN.md)

---

## License
Academic Coursework (PBL-2) — All Rights Reserved.
