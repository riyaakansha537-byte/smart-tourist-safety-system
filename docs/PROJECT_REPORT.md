# Smart Tourist Safety and Emergency Response System
## Comprehensive Academic Project Report

**Course / Project:** PBL-2 (Project-Based Learning)  
**Domains Covered:** Operating Systems (OS) & Database Management Systems (DBMS)  
**Technologies:** Python, Flask, PostgreSQL, Flutter, Dart, Socket.IO, JavaScript  

---

## Abstract

Tourism contributes substantially to global economic development, yet tourists often encounter critical hazards including unfamiliar topography, hazardous geofence zones, vehicular collisions, and medical distress. Existing municipal emergency infrastructures operate in decoupled silos with manual, non-prioritized dispatch systems prone to resource starvation, race conditions, and catastrophic circular-wait deadlocks.

This project presents the **Smart Tourist Safety and Emergency Response System**, an end-to-end mission-critical software platform designed to manage high-volume, concurrent tourist distress events under finite emergency apparatus availability. The system bridges core **Operating Systems** primitives (multithreaded worker pools, total-order priority scheduling, mutex/semaphore synchronization, Dijkstra's Banker's Algorithm for deadlock avoidance, and inter-process communication) with foundational **Database Management Systems** design (3NF normalized relational schema across 9 entities, referential integrity cascades, thread-safe connection pooling, ACID transaction guarantees, and B-Tree indexing strategies).

The platform delivers a production-grade cross-platform **Flutter Mobile Client** for tourists, an interactive **Authority Command Dashboard** with real-time Leaflet GIS mapping, and a Python **Flask-SocketIO** backend. The system has been validated with 120 automated test cases (100% pass rate) and a dedicated live demonstration script.

---

## 1. Introduction & Problem Statement

### 1.1 Background
During peak tourism seasons, emergency responders encounter spikes in simultaneous distress signals. A coastal or mountainous district may operate with limited physical apparatus:
- 4 Ambulances
- 5 Specialized Rescue Teams
- 2 Emergency Medical Evacuation Helicopters

### 1.2 Core Problem
When multiple tourists generate concurrent emergencies, traditional first-come, first-served (FCFS) dispatch leads to fatal failures:
1. **Priority Inversion / Misallocation:** A routine inquiry or low-priority telemetry update blocks dispatch of an ambulance to a critical head-on collision.
2. **Race Conditions:** Two concurrent worker threads claim the same ambulance simultaneously due to unprotected shared state.
3. **Deadlock:** Multiple incident processes claim resources incrementally (Incident A holds an Ambulance and requests a Helicopter; Incident B holds a Helicopter and requests an Ambulance), entering a permanent circular-wait deadlock.
4. **Data Inconsistency:** Incomplete database updates leave rescue vehicles marked as assigned without corresponding incident records.

---

## 2. Operating Systems Concepts Implementation

### 2.1 Multithreading (`WorkerPool`)
- Managed thread pool comprising 3 continuous daemon worker threads.
- Non-blocking event consumption from priority queues with zero CPU spinlock.
- Specialized handlers: `GPSWorker`, `SOSWorker`, `GeofenceWorker`, `NotificationWorker`.

### 2.2 Priority Scheduling (`EmergencyPriorityQueue`)
- Total ordering enforced:
  - $P_1$: Critical Road Accident / Medical Evacuation (Priority 1)
  - $P_2$: Personal SOS Beacon (Priority 2)
  - $P_3$: Dangerous Zone Breach (Priority 3)
  - $P_4$: General Safety Alert (Priority 4)
  - $P_5$: Background GPS Telemetry (Priority 5)
- Tie-breaking via high-precision timestamps prevents starvation within identical priority classes.

### 2.3 Mutual Exclusion & Synchronization (`SynchronizationManager`)
- **Mutex Lock (`threading.Lock`):** Protects critical sections during allocation vector updates.
- **Counting Semaphore (`threading.Semaphore`):** Limits peak concurrent dispatch bandwidth to prevent network and resource thrashing.

### 2.4 Deadlock Avoidance (`BankersAlgorithm`)
- Models multi-class resources: Ambulances, Rescue Teams, Helicopters.
- Maintains dynamic matrices: Available, Max, Allocation, Need.
- Pre-allocation simulation verifies that the system remains in a safe state with a valid execution sequence before any physical resource is assigned.

### 2.5 Inter-Process Communication (IPC)
- Demonstrates true process-level message passing using `multiprocessing.Queue` and duplex `multiprocessing.Pipe` across independent operating system processes with distinct PIDs.

---

## 3. Database Management Systems Implementation

### 3.1 Relational Schema & 3NF Normalization
- 9 distinct entities: `tourist`, `emergency_contact`, `location`, `safe_dangerous_zone`, `emergency_incident`, `emergency_log`, `rescue_team`, `resource`, `resource_assignment`.
- Fully normalized to Third Normal Form (3NF), eliminating insertion, update, and deletion anomalies.

### 3.2 Integrity Constraints
- Foreign keys with `ON DELETE CASCADE` on child records (`emergency_contact`, `emergency_log`).
- `CHECK` constraints on priority bounds (1-5), risk levels, blood groups, and status lifecycles.
- `UNIQUE` indexes preventing duplicate assignments and registrations.

### 3.3 Connection Pooling & Performance Indexing
- Thread-safe `ThreadedConnectionPool` (2 min, 10 max connections).
- Strategic B-Tree indexes on `(status)`, `(priority, created_at)`, and `(tourist_id, recorded_at DESC)`.

### 3.4 ACID Transactions (`transaction_scope`)
- Atomic multi-table mutations committed via `BEGIN` / `COMMIT` / `ROLLBACK`.
- Guarantees zero orphaned assignments or mismatched status states.

---

## 4. Frontend & Mobile Clients

### 4.1 Flutter Mobile Application
- **Architecture:** Material 3 dark safety design with custom glassmorphism components.
- **Screens:** Splash, Registration, Home Safety Dashboard, SOS Emergency Dispatcher, Contacts Manager, Incident History, Tourist Profile with Diagnostics, Safety Notifications.
- **Real-Time Integration:** REST HTTP client + bi-directional Socket.IO listener.

### 4.2 Authority Command Dashboard
- High-contrast responsive web console featuring Leaflet.js interactive maps.
- Live Banker's Algorithm matrix viewer, active emergency list, resource inventory tracker, and built-in multi-tourist concurrent event simulation controls.

---

## 5. Verification & Testing Results

- **Automated Test Suite:** 120 tests across 10 test modules.
- **Pass Rate:** 100% (120 passed in 2.96 seconds).
- **Test Modules:**
  - `test_db_connection.py` (7 tests)
  - `test_flask_app.py` (8 tests)
  - `test_tourist_api.py` (17 tests)
  - `test_location_api.py` (20 tests)
  - `test_emergency_api.py` (20 tests)
  - `test_priority_queue.py` (11 tests)
  - `test_resource_manager.py` (10 tests)
  - `test_resource_and_dashboard_api.py` (18 tests)
  - `test_workers.py` (7 tests)
  - `test_ipc.py` (1 test)
  - `test_end_to_end_pipeline.py` (1 test)

---

## 6. Conclusion & Future Scope

The project successfully demonstrates how foundational concepts in Operating Systems and Database Systems can be harmoniously synthesized to solve real-world emergency dispatch challenges. 

**Future enhancements:**
1. Integration of real GPS hardware (GNSS sensors) via Android native channels.
2. Integration of graph-based shortest path routing (Dijkstra / A*) for live ambulance navigation.
3. Multi-node distributed database replication with PostgreSQL streaming replication.
