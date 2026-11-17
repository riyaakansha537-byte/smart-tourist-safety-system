# System Architecture & Technical Specifications

This document provides the high-level and detailed architectural blueprint for the **Smart Tourist Safety and Emergency Response System**.

---

## 1. System Overview

The system is organized into a four-tier architecture designed for high availability, low latency, real-time response, and academic rigor in Operating Systems and DBMS disciplines:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             TIER 1: CLIENT LAYER                            │
│                                                                             │
│   ┌─────────────────────────────────────┐  ┌──────────────────────────────┐ │
│   │        Flutter Mobile App           │  │     Authority Dashboard      │ │
│   │   (Android / iOS / Mobile Web)      │  │     (HTML5 / CSS3 / JS)      │ │
│   │                                     │  │                              │ │
│   │  • Tourist Registration & Safety ID │  │  • Real-Time Geo Map         │ │
│   │  • One-Tap SOS Distress Beacon      │  │  • Active Incidents Console  │ │
│   │  • Simulated GPS Telemetry Ping     │  │  • Live Banker's Matrix View │ │
│   │  • Emergency Contacts Manager       │  │  • Resource Fleet Monitor    │ │
│   │  • Incident Timeline Tracking       │  │  • Multi-Tourist Simulator   │ │
│   └──────────────────┬──────────────────┘  └──────────────┬───────────────┘ │
│                      │                                    │                 │
│                      │ HTTP REST / WebSocket              │ WebSocket       │
└──────────────────────┼────────────────────────────────────┼─────────────────┘
                       │                                    │
┌──────────────────────┼────────────────────────────────────┼─────────────────┐
│                      ▼      TIER 2: APPLICATION LAYER     ▼                 │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      Python Flask Web Framework                     │   │
│   │                                                                     │   │
│   │   • CORS Middleware (Cross-Origin Support)                          │   │
│   │   • Blueprints: /tourists, /location, /emergencies, /resources      │   │
│   │   • Flask-SocketIO Gateway (Room management: 'mobile', 'dashboard') │   │
│   │   • Request Validation & Sanitization Pipeline                      │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┼──────────────────────────────────────┐
│                                      ▼                                      │
│                      TIER 3: OS PROCESSING ENGINE                           │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  OS Component Subsystems:                                           │   │
│   │                                                                     │   │
│   │  1. Priority Scheduling: EmergencyPriorityQueue                     │   │
│   │     - Enforces total ordering: P1 Critical > P2 SOS > P5 GPS        │   │
│   │                                                                     │   │
│   │  2. Multithreading Pool: WorkerPool (N=3 daemon threads)            │   │
│   │     - Non-blocking dequeue and parallel event dispatch              │   │
│   │                                                                     │   │
│   │  3. Synchronization: SynchronizationManager                         │   │
│   │     - Mutex Lock (critical sections) + Counting Semaphore           │   │
│   │                                                                     │   │
│   │  4. Deadlock Avoidance: BankersAlgorithm                            │   │
│   │     - Available, Max, Allocation, Need matrices; Safe state check   │   │
│   │                                                                     │   │
│   │  5. Inter-Process Communication (IPC):                              │   │
│   │     - Autonomous sensor processes communicating via mp.Queue & Pipe │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┼──────────────────────────────────────┐
│                                      ▼                                      │
│                         TIER 4: PERSISTENCE LAYER                           │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     PostgreSQL 16+ Relational DBMS                  │   │
│   │                                                                     │   │
│   │  • ThreadedConnectionPool (min=2, max=10)                           │   │
│   │  • ACID Transactions with atomicity guarantees                      │   │
│   │  • 3NF Normalized Schema across 9 Entities                          │   │
│   │  • Referential Integrity Constraints & Cascades                     │   │
│   │  • B-Tree Indexes on Priority, Status, and Spatial Timestamps       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Interaction & Sequence Flow

### End-to-End Emergency Lifecycle Flow:

```
Tourist (Mobile)       Flask API        PriorityQueue       WorkerPool       Banker's Algo      PostgreSQL       Dashboard
      │                    │                  │                 │                  │                │                │
      │ 1. POST /sos ────▶ │                  │                 │                  │                │                │
      │                    │ 2. Enqueue P2 ─▶ │                 │                  │                │                │
      │                    │    Event         │                 │                  │                │                │
      │                    │                  │ 3. Dequeue P2 ─▶│                  │                │                │
      │                    │                  │                 │ 4. Request ─────▶│                │                │
      │                    │                  │                 │    Resources     │                │                │
      │                    │                  │                 │ 5. Safe State ───│                │                │
      │                    │                  │                 │    Confirmed ◀───│                │                │
      │                    │                  │                 │ 6. BEGIN Tx ─────────────────────▶│                │
      │                    │                  │                 │    Assign resource, update status │                │
      │                    │                  │                 │ 7. COMMIT Tx ────────────────────▶│                │
      │                    │                  │                 │ 8. Broadcast Event ──────────────────────────────▶ │
      │ 9. Push Alert ◀────┴──────────────────┴─────────────────┴────────────────────────────────────────────────────┤
```

---

## 3. Technology Stack Summary

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Mobile App** | Flutter / Dart | 3.x | Cross-platform tourist client (Android / iOS) |
| **State Management**| Provider | 6.1.1 | Reactive application state handling in Flutter |
| **Real-Time Client**| socket_io_client | 2.0.3 | WebSocket bi-directional event stream |
| **Backend API** | Python / Flask | 3.10+ | RESTful microservice & application factory |
| **Real-Time Server**| Flask-SocketIO | 5.3+ | WebSocket gateway for live telemetry & alerts |
| **Database** | PostgreSQL | 16+ | ACID-compliant relational persistence engine |
| **DB Driver** | psycopg2-binary | 2.9+ | Threaded connection pool client |
| **Testing** | pytest | 9.x | Automated test suite (120 test cases, 100% pass) |
| **Dashboard** | Vanilla HTML5/CSS3/JS | ES6+ | Zero-dependency real-time authority console |
| **Mapping Engine** | Leaflet.js | 1.9.4 | Open-source interactive map with dark tiles |
