# Database Management Systems Concepts: Implementation & Academic Defense Guide

This document details the Database Management Systems (DBMS) principles designed, implemented, and validated within the **Smart Tourist Safety and Emergency Response System**.

---

## 1. Relational Modeling & Schema Design

### Entity Architecture
The persistent storage layer is built upon PostgreSQL 16+ using a normalized relational model comprising 9 distinct entities:

```
[TOURIST] (1) ────< (N) [EMERGENCY_CONTACT]
[TOURIST] (1) ────< (N) [LOCATION] >──── (N) [SAFE_DANGEROUS_ZONE]
[TOURIST] (1) ────< (N) [EMERGENCY_INCIDENT]
                           │ (1)
                           ├───< (N) [EMERGENCY_LOG]
                           └───< (N) [RESOURCE_ASSIGNMENT]
                                       │ (N)           │ (N)
                                       ▼ (1)           ▼ (1)
                                  [RESOURCE]     [RESCUE_TEAM]
```

### Table Dictionary & Schema
- `tourist`: Primary user profiles (`tourist_id`, `name`, `phone`, `email`, `nationality`, `blood_group`, `registered_at`).
- `emergency_contact`: Trusted next-of-kin contacts (`contact_id`, `tourist_id` FK, `name`, `phone`, `relationship`).
- `location`: GPS breadcrumb telemetry history (`location_id`, `tourist_id` FK, `latitude`, `longitude`, `zone_id` FK, `recorded_at`).
- `safe_dangerous_zone`: Circular geofence polygons (`zone_id`, `zone_name`, `zone_type`, `center_lat`, `center_lng`, `radius_km`, `risk_level`, `is_active`).
- `emergency_incident`: Core emergency events (`incident_id`, `tourist_id` FK, `incident_type`, `priority`, `status`, `latitude`, `longitude`, `description`, `created_at`, `resolved_at`).
- `emergency_log`: Append-only immutable audit trail (`log_id`, `incident_id` FK, `action`, `details`, `performed_by`, `created_at`).
- `rescue_team`: Tactical teams (`team_id`, `team_name`, `specialization`, `status`, `current_capacity`, `max_capacity`, `contact_number`).
- `resource`: Response apparatus (`resource_id`, `resource_name`, `resource_type`, `status`, `current_lat`, `current_lng`).
- `resource_assignment`: M:N resolution table (`assignment_id`, `incident_id` FK, `resource_id` FK, `team_id` FK, `status`, `assigned_at`, `released_at`).

---

## 2. Normalization Analysis (3NF Proof)

Every relation in the schema has been formally structured and verified to meet **Third Normal Form (3NF)**:

### 1. First Normal Form (1NF)
- **Criterion:** All attribute values are atomic; no repeating groups or composite attributes exist.
- **Verification:** Phone numbers and email addresses are atomic single-valued fields. Locations store scalar `latitude` and `longitude` numeric values rather than raw coordinate arrays or unparsed strings.

### 2. Second Normal Form (2NF)
- **Criterion:** Must be in 1NF, and all non-key attributes are fully functionally dependent on the entire primary key (no partial dependencies).
- **Verification:** All relations utilize single-column surrogate primary keys (`SERIAL` IDs: `tourist_id`, `incident_id`, `assignment_id`). Since candidate keys are single attributes, partial dependency is mathematically impossible.

### 3. Third Normal Form (3NF)
- **Criterion:** Must be in 2NF, and no non-key attribute is transitively dependent on the primary key ($X \to Y$ and $Y \to Z$ where $Z$ is not part of any key).
- **Verification:**
  - In `location`, zone metadata (`zone_name`, `risk_level`) is not duplicated in `location`; only foreign key `zone_id` is maintained, referencing `safe_dangerous_zone`.
  - In `resource_assignment`, resource characteristics (`resource_type`, `resource_name`) are normalized inside `resource`, eliminating transitive dependencies.

---

## 3. Referential Integrity & Cascading Constraints

Data integrity is enforced at the database engine level via declarative constraints:
- **Foreign Key Cascading:**
  - `EMERGENCY_CONTACT`: Foreign key `ON DELETE CASCADE` ensures child emergency contacts are purged if a tourist account is deleted.
  - `EMERGENCY_LOG`: Foreign key `ON DELETE CASCADE` maintains lifecycle synchronization with parent incidents.
- **Check Constraints (`CHECK`):**
  - Priority boundaries: `priority BETWEEN 1 AND 5`.
  - Blood groups: `blood_group IN ('A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-')`.
  - Zone risk levels: `risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')`.
  - Resource status: `status IN ('AVAILABLE', 'ASSIGNED', 'MAINTENANCE', 'OUT_OF_SERVICE')`.
- **Unique Constraints (`UNIQUE`):**
  - Unique phone number & email address in `tourist` prevents duplicate records.
  - Unique index on `(resource_id, incident_id)` prevents assigning the same apparatus twice.

---

## 4. Indexing Strategy & Performance Optimization

To guarantee sub-millisecond query performance during high emergency incident volume, dedicated B-Tree indexes are defined:

| Index Name | Table | Columns | Purpose |
|---|---|---|---|
| `idx_incident_status` | `emergency_incident` | `(status)` | Accelerates active emergency filtering on dashboard |
| `idx_incident_priority` | `emergency_incident` | `(priority, created_at)` | Optimizes OS Priority scheduler extraction |
| `idx_incident_tourist` | `emergency_incident` | `(tourist_id)` | Enables instant retrieval of tourist emergency history |
| `idx_location_tourist_time` | `location` | `(tourist_id, recorded_at DESC)` | Optimizes latest GPS breadcrumb lookup |
| `idx_resource_status` | `resource` | `(status, resource_type)` | Accelerates Banker's algorithm resource discovery |
| `idx_team_status` | `rescue_team` | `(status, specialization)` | Fast team lookup during dispatch |

---

## 5. Thread-Safe Connection Pooling

### Theoretical Foundation
Establishing a new TCP socket and performing database authentication on every HTTP API request introduces substantial latency (50-100ms) and risks exhaustively exceeding maximum PostgreSQL connection limits (`max_connections`).

### Implementation Details
- **Location:** `backend/db/connection.py`
- **Class:** `ThreadedConnectionPool`
- **Configuration:**
  - `minconn = 2`: Pre-warmed idle connections available immediately.
  - `maxconn = 10`: Upper bound preventing database thread exhaustion.
- **Safety Mechanism:** Connections are acquired using a thread-safe context manager that automatically returns the connection back to the pool in a `finally` block:
  ```python
  @contextmanager
  def get_db_connection():
      conn = pool.getconn()
      try:
          yield conn
      finally:
          pool.putconn(conn)
  ```

---

## 6. ACID Transactions & Concurrency Control

### ACID Implementation
1. **Atomicity:** When an emergency resource is assigned, four database mutations must either all succeed together or all fail together:
   - Insert into `resource_assignment`
   - Update `resource.status = 'ASSIGNED'`
   - Update `emergency_incident.status = 'RESOURCE_ASSIGNED'`
   - Insert audit entry into `emergency_log`
   Implemented via `transaction_scope()` in `backend/db/transactions.py`:
   ```python
   with transaction_scope() as conn:
       cursor = conn.cursor()
       # Operations 1, 2, 3, 4 executed
       # conn.commit() on success, conn.rollback() on any error
   ```
2. **Consistency:** All check constraints, foreign keys, and unique indexes are validated prior to transaction commit.
3. **Isolation:** PostgreSQL uses Multi-Version Concurrency Control (MVCC) with Read Committed isolation by default, eliminating dirty reads without blocking read operations during concurrent writes.
4. **Durability:** Committed transactions are flushed to Write-Ahead Logging (WAL) on disk, guaranteeing survival against unexpected server failures.
