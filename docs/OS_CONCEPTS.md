# Operating Systems Concepts: Implementation & Academic Defense Guide

This document details the Operating Systems (OS) principles designed, implemented, and validated within the **Smart Tourist Safety and Emergency Response System**.

---

## 1. Multithreading & Thread Pool Architecture

### Theoretical Foundation
Multithreading enables concurrent execution within a single process address space. In an emergency response dispatch system, I/O latency (database writes, network telemetries, and socket broadcasts) must not block the main request ingest loop.

### Implementation Details
- **Location:** `backend/workers/worker_pool.py`, `backend/workers/*_worker.py`
- **Mechanism:**
  - A managed worker thread pool initializes with `N = 3` daemon worker threads.
  - Worker threads run continuously in a non-terminating loop:
    ```python
    while not self._stop_event.is_set():
        event = self.priority_scheduler.dequeue(block=True, timeout=1.0)
        self.dispatch_event(event)
    ```
  - Dedicated specialized workers:
    1. `gps_worker.py`: Ingests GPS telemetry updates, performs zone boundary detection.
    2. `sos_worker.py`: Processes emergency beacons and initiates Banker's algorithm allocation.
    3. `geofence_worker.py`: Handles geofence breach escalations.
    4. `notification_worker.py`: Dispatches push alerts across Socket.IO rooms.

### Concurrency Characteristics
- **I/O Bound vs CPU Bound:** While Python possesses a Global Interpreter Lock (GIL), all network requests, database transactions (`psycopg2`), and socket emissions release the GIL during execution, allowing true concurrent throughput.

---

## 2. Priority Scheduling (Preemptive Dispatch Ordering)

### Theoretical Foundation
Classical scheduling algorithms (e.g., FCFS or Round-Robin) treat all jobs uniformly. In emergency operations, a critical road collision or drowning hazard cannot wait behind periodic location pings. Priority scheduling enforces total order by urgency.

### Implementation Details
- **Location:** `backend/scheduler/priority_queue.py`
- **Class:** `EmergencyPriorityQueue`, `EmergencyEvent`
- **Priority Hierarchy:**
  | Priority Level | Event Type | Description |
  |---|---|---|
  | **P1 (Highest)** | `CRITICAL_ACCIDENT` | Severe vehicle collision, cardiac arrest, imminent loss of life |
  | **P2** | `SOS` | Tourist SOS beacon trigger, personal distress |
  | **P3** | `DANGEROUS_ZONE` | Geofence breach into restricted/hazardous territory |
  | **P4** | `SAFETY_ALERT` | Inclement weather warning, advisory notice |
  | **P5 (Lowest)** | `GPS_UPDATE` | Routine background telemetry heartbeat |

- **Data Structure:**
  - Implemented using Python's `queue.PriorityQueue` augmented with thread-safe telemetry hooks.
  - Total ordering defined via `@dataclass(order=True)`:
    - Primary Sort Key: `priority: int` (Ascending, where 1 is highest priority).
    - Secondary Sort Key (Tie-breaker): `timestamp: float` (Enforces FIFO ordering for identical priority levels, preventing internal starvation).

---

## 3. Mutual Exclusion & Synchronization Primitives

### Theoretical Foundation
When multiple worker threads attempt concurrent updates to shared resources (e.g., vehicle inventories or resource allocation matrices), unprotected execution creates race conditions and lost update anomalies.

### Implementation Details
- **Location:** `backend/resource_manager/synchronization.py`
- **Class:** `SynchronizationManager`
- **Primitives Implemented:**
  1. **Mutex Lock (`threading.Lock`):**
     - Guarantees mutual exclusion when modifying shared state.
     - Implemented as an atomic context manager:
       ```python
       with sync_mgr.critical_section():
           # Critical Section: Available / Allocation matrices safely updated
       ```
     - Measures lock contention and duration metrics.
  2. **Counting Semaphore (`threading.Semaphore`):**
     - Controls resource bandwidth by limiting the maximum number of simultaneous dispatch procedures:
       ```python
       with sync_mgr.acquire_dispatch_permit(timeout=5.0):
           # Only N concurrent dispatches permitted simultaneously
       ```

---

## 4. Deadlock Avoidance: Dijkstra's Banker's Algorithm

### Theoretical Foundation
In a multi-resource emergency infrastructure, deadlock can occur if multiple incidents claim resources incrementally with circular waiting. Banker's Algorithm prevents deadlocks before they happen by testing if the system remains in a **safe state** before any resource is granted.

### Implementation Details
- **Location:** `backend/resource_manager/bankers_algorithm.py`
- **Class:** `BankersAlgorithm`
- **Resource Classes Modeled:**
  1. `AMBULANCE` (Road vehicles)
  2. `RESCUE_TEAM` (Specialized personnel squads)
  3. `HELICOPTER` (Aviation evacuation units)

- **Matrices & Vectors:**
  - **Available Vector $[m]$:** Quantity of unallocated units of each resource type.
  - **Max Matrix $[n \times m]$:** Maximum potential requirement declared for each active incident process.
  - **Allocation Matrix $[n \times m]$:** Current units allocated to each incident process.
  - **Need Matrix $[n \times m]$:** Remaining resources required:
    $$\text{Need}[i][j] = \text{Max}[i][j] - \text{Allocation}[i][j]$$

- **Resource Request Algorithm:**
  1. Verify $\text{Request}_i \le \text{Need}_i$. (Else throw error: exceeded declared claim).
  2. Verify $\text{Request}_i \le \text{Available}$. (Else process must wait).
  3. Pretend to allocate:
     $$\text{Available} \leftarrow \text{Available} - \text{Request}_i$$
     $$\text{Allocation}_i \leftarrow \text{Allocation}_i + \text{Request}_i$$
     $$\text{Need}_i \leftarrow \text{Need}_i - \text{Request}_i$$
  4. Run Safety Algorithm. If safe, commit allocation. If unsafe, rollback to prior state and reject request.

- **Safety Algorithm:**
  - Initializes $\text{Work} = \text{Available}$ and $\text{Finish}[i] = \text{False}$ for all $i$.
  - Iteratively finds process $p$ where $\text{Finish}[p] == \text{False}$ and $\text{Need}_p \le \text{Work}$.
  - Simulates completion: $\text{Work} \leftarrow \text{Work} + \text{Allocation}_p$, $\text{Finish}[p] \leftarrow \text{True}$.
  - System is in a **SAFE STATE** if and only if all processes finish ($\text{Finish}[i] == \text{True}$ for all $i$), producing a guaranteed `safe_sequence`.

---

## 5. Inter-Process Communication (IPC)

### Theoretical Foundation
Operating Systems distinguish between:
- **Inter-Thread Communication:** Shared heap, shared memory space within a single OS Process ID (PID). Fast but susceptible to single-process crashes and thread-safety bugs.
- **Inter-Process Communication (IPC):** Communication across distinct OS processes with isolated virtual address spaces and separate PIDs. Requires OS kernel primitives.

### Implementation Details
- **Location:** `simulation/ipc_demo.py`, `tests/test_ipc.py`
- **IPC Primitives Demonstrated:**
  1. **IPC Message Queue (`multiprocessing.Queue`):**
     - Autonomous producer process spawns (`PID_A`), serializes telemetry records, and pushes across kernel boundary into IPC queue.
     - Autonomous authority ingest process (`PID_B`) dequeues and processes telemetry.
  2. **Duplex IPC Pipe (`multiprocessing.Pipe`):**
     - Full-duplex channel between parent process and child sensor process for synchronized two-way emergency handshakes (`send` and `recv`).
  3. **Shared Memory (`multiprocessing.Manager`):**
     - Shared process memory proxy with internal process lock synchronization.
