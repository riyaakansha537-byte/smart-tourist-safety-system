-- ============================================================
-- Smart Tourist Safety and Emergency Response System
-- Realistic Seed Data Script
-- Phase 4: Initial Data Population
-- ============================================================

-- Ensure clean state for seed execution
TRUNCATE TABLE emergency_logs CASCADE;
TRUNCATE TABLE resource_assignments CASCADE;
TRUNCATE TABLE resources CASCADE;
TRUNCATE TABLE rescue_teams CASCADE;
TRUNCATE TABLE locations CASCADE;
TRUNCATE TABLE safe_dangerous_zones CASCADE;
TRUNCATE TABLE emergency_incidents CASCADE;
TRUNCATE TABLE emergency_contacts CASCADE;
TRUNCATE TABLE tourists CASCADE;

-- Reset primary key sequences
ALTER SEQUENCE tourists_tourist_id_seq RESTART WITH 1;
ALTER SEQUENCE emergency_contacts_contact_id_seq RESTART WITH 1;
ALTER SEQUENCE safe_dangerous_zones_zone_id_seq RESTART WITH 1;
ALTER SEQUENCE locations_location_id_seq RESTART WITH 1;
ALTER SEQUENCE emergency_incidents_incident_id_seq RESTART WITH 1;
ALTER SEQUENCE emergency_logs_log_id_seq RESTART WITH 1;
ALTER SEQUENCE rescue_teams_team_id_seq RESTART WITH 1;
ALTER SEQUENCE resources_resource_id_seq RESTART WITH 1;
ALTER SEQUENCE resource_assignments_assignment_id_seq RESTART WITH 1;

-- ============================================================
-- 1. SAFE & DANGEROUS ZONES
-- Predefined geofences: 2 Safe tourist zones, 3 Dangerous zones
-- ============================================================
INSERT INTO safe_dangerous_zones (zone_name, zone_type, center_lat, center_lng, radius_km, risk_level, is_active)
VALUES
    ('Baga Beach Promenade', 'SAFE', 15.555300, 73.751600, 2.50, 'LOW', TRUE),
    ('Old Goa Historic Quarter', 'SAFE', 15.503000, 73.911800, 3.00, 'LOW', TRUE),
    ('Netravali Dense Forest Reserve', 'DANGEROUS', 15.087200, 74.208100, 6.00, 'HIGH', TRUE),
    ('Dudhsagar Waterfall Rapids & Gorge', 'DANGEROUS', 15.314400, 74.314400, 3.50, 'CRITICAL', TRUE),
    ('Aguada Sea Cliff & Surge Area', 'DANGEROUS', 15.492500, 73.773500, 1.20, 'HIGH', TRUE);

-- ============================================================
-- 2. RESCUE TEAMS
-- Diverse specialized emergency response units
-- ============================================================
INSERT INTO rescue_teams (team_name, specialization, status, current_capacity, max_capacity, contact_number)
VALUES
    ('Alpha Paramedic Rapid Response', 'MEDICAL', 'AVAILABLE', 0, 4, '+91-98230-11001'),
    ('Margao Trauma & Medical Unit', 'MEDICAL', 'BUSY', 2, 4, '+91-98230-11002'),
    ('Western Ghats Mountain SAR', 'SEARCH_AND_RESCUE', 'AVAILABLE', 0, 6, '+91-98230-22001'),
    ('Coastal Marine Life-Guards', 'SEARCH_AND_RESCUE', 'AVAILABLE', 0, 5, '+91-98230-22002'),
    ('Central Fire & Hazmat Brigade', 'FIRE', 'AVAILABLE', 0, 8, '+91-98230-33001');

-- ============================================================
-- 3. RESOURCES
-- Physical rescue apparatus representing Banker's Algorithm resource classes
-- ============================================================
INSERT INTO resources (resource_name, resource_type, status, current_lat, current_lng)
VALUES
    ('Ambulance-Alpha-01', 'AMBULANCE', 'AVAILABLE', 15.498900, 73.827800),
    ('Ambulance-Beta-02', 'AMBULANCE', 'AVAILABLE', 15.283200, 73.986200),
    ('Ambulance-Delta-03', 'AMBULANCE', 'ASSIGNED', 15.312000, 74.310000),
    ('Air-Ambulance-Heli-01', 'HELICOPTER', 'AVAILABLE', 15.380800, 73.831400),
    ('Coast-Guard-Heli-02', 'HELICOPTER', 'AVAILABLE', 15.480000, 73.810000),
    ('Rescue-Boat-Neptune-1', 'RESCUE_BOAT', 'AVAILABLE', 15.550000, 73.740000),
    ('Rapid-Fire-Engine-01', 'FIRE_TRUCK', 'AVAILABLE', 15.495000, 73.820000),
    ('Heavy-Rescue-Truck-02', 'FIRE_TRUCK', 'MAINTENANCE', 15.270000, 73.980000);

-- ============================================================
-- 4. TOURISTS
-- Profiles representing mobile app registered users
-- ============================================================
INSERT INTO tourists (name, phone, email, nationality, blood_group, registered_at)
VALUES
    ('Alice Johnson', '+1-555-0101', 'alice.johnson@example.com', 'American', 'O+', NOW() - INTERVAL '3 days'),
    ('Rajesh Kumar', '+91-98765-43210', 'rajesh.kumar@example.in', 'Indian', 'B+', NOW() - INTERVAL '2 days'),
    ('Sofia Martinez', '+34-600-112233', 'sofia.martinez@example.es', 'Spanish', 'A+', NOW() - INTERVAL '5 days'),
    ('Hiroshi Tanaka', '+81-90-1234-5678', 'hiroshi.tanaka@example.jp', 'Japanese', 'AB+', NOW() - INTERVAL '1 day'),
    ('Emma Dubois', '+33-6-1234-5678', 'emma.dubois@example.fr', 'French', 'O-', NOW() - INTERVAL '4 days'),
    ('Lucas Müller', '+49-151-23456789', 'lucas.mueller@example.de', 'German', 'A-', NOW() - INTERVAL '6 hours');

-- ============================================================
-- 5. EMERGENCY CONTACTS
-- Next-of-kin and diplomatic embassy connections
-- ============================================================
INSERT INTO emergency_contacts (tourist_id, name, phone, relationship)
VALUES
    (1, 'Robert Johnson', '+1-555-0102', 'Spouse'),
    (1, 'US Consulate Emergency Desk', '+91-22-2672-4000', 'Embassy'),
    (2, 'Pooja Kumar', '+91-98765-43211', 'Sister'),
    (3, 'Alejandro Martinez', '+34-600-112244', 'Father'),
    (3, 'Spanish Embassy Assistance', '+91-11-4129-3000', 'Embassy'),
    (4, 'Kenji Tanaka', '+81-90-1234-9999', 'Brother'),
    (5, 'Claire Dubois', '+33-6-1234-9999', 'Mother'),
    (6, 'Hannah Müller', '+49-151-23459999', 'Spouse');

-- ============================================================
-- 6. LOCATIONS
-- Simulated periodic GPS telemetry stream
-- ============================================================
INSERT INTO locations (tourist_id, latitude, longitude, recorded_at, zone_id)
VALUES
    -- Alice Johnson enjoying Baga Beach (Safe zone 1)
    (1, 15.554000, 73.752000, NOW() - INTERVAL '45 minutes', 1),
    (1, 15.556200, 73.753100, NOW() - INTERVAL '15 minutes', 1),
    -- Rajesh Kumar exploring Old Goa heritage (Safe zone 2)
    (2, 15.502000, 73.910000, NOW() - INTERVAL '2 hours', 2),
    (2, 15.503500, 73.912500, NOW() - INTERVAL '30 minutes', 2),
    -- Sofia Martinez trekking near Dudhsagar Gorge (Entered dangerous zone 4)
    (3, 15.320000, 74.300000, NOW() - INTERVAL '3 hours', NULL),
    (3, 15.314800, 74.314000, NOW() - INTERVAL '20 minutes', 4),
    -- Hiroshi Tanaka near Aguada Cliffs (Approaching dangerous zone 5)
    (4, 15.495000, 73.778000, NOW() - INTERVAL '1 hour', NULL),
    (4, 15.493000, 73.774000, NOW() - INTERVAL '10 minutes', 5),
    -- Emma Dubois in Netravali Wildlife Sanctuary (Dangerous zone 3)
    (5, 15.090000, 74.205000, NOW() - INTERVAL '50 minutes', 3),
    -- Lucas Müller in transit
    (6, 15.400000, 73.850000, NOW() - INTERVAL '5 minutes', NULL);

-- ============================================================
-- 7. EMERGENCY INCIDENTS
-- Representative incidents covering all priority tiers (1 to 5)
-- ============================================================
INSERT INTO emergency_incidents (
    tourist_id, incident_type, priority, status, latitude, longitude, description, created_at, resolved_at
)
VALUES
    -- Incident 1: Priority 1 - Critical accident in canyon (Actively being handled)
    (
        3, 
        'CRITICAL_ACCIDENT', 
        1, 
        'RESOURCE_ASSIGNED', 
        15.314800, 
        74.314000, 
        'Tourist slipped down rocky embankment near waterfall. Multiple fractures reported.', 
        NOW() - INTERVAL '25 minutes', 
        NULL
    ),
    -- Incident 2: Priority 2 - Panic SOS button pressed
    (
        5, 
        'SOS', 
        2, 
        'QUEUED', 
        15.090000, 
        74.205000, 
        'Tourist triggered emergency SOS via mobile app. Lost in dense forest, darkness falling.', 
        NOW() - INTERVAL '12 minutes', 
        NULL
    ),
    -- Incident 3: Priority 3 - Automated geofence perimeter breach
    (
        4, 
        'DANGEROUS_ZONE', 
        3, 
        'RECEIVED', 
        15.493000, 
        73.774000, 
        'Geofence violation: tourist entered high-risk Aguada Sea Cliff surge zone.', 
        NOW() - INTERVAL '5 minutes', 
        NULL
    ),
    -- Incident 4: Priority 4 - Safety advisory resolved
    (
        1, 
        'SAFETY_ALERT', 
        4, 
        'RESOLVED', 
        15.556200, 
        73.753100, 
        'Mild dehydration reported. Advised to visit coastal medical outpost.', 
        NOW() - INTERVAL '4 hours', 
        NOW() - INTERVAL '2 hours'
    );

-- ============================================================
-- 8. RESOURCE ASSIGNMENTS
-- Junction allocation linking Incident 1 to Ambulance and Medical Team
-- ============================================================
INSERT INTO resource_assignments (incident_id, resource_id, team_id, status, assigned_at, released_at)
VALUES
    (1, 3, 2, 'EN_ROUTE', NOW() - INTERVAL '20 minutes', NULL);

-- ============================================================
-- 9. EMERGENCY LOGS
-- Immutable system audit trail demonstrating the OS/DBMS pipeline
-- ============================================================
INSERT INTO emergency_logs (incident_id, action, details, performed_by, created_at)
VALUES
    (1, 'INCIDENT_CREATED', 'Emergency reported via REST API POST /api/emergencies/accident', 'API_DISPATCHER', NOW() - INTERVAL '25 minutes'),
    (1, 'PRIORITY_ENQUEUED', 'Assigned Priority 1 (CRITICAL_ACCIDENT) into PriorityQueue', 'SCHEDULER_ENGINE', NOW() - INTERVAL '24 minutes'),
    (1, 'DEQUEUED_BY_WORKER', 'Dequeued by WorkerThread-1 for immediate processing', 'WORKER_THREAD_1', NOW() - INTERVAL '23 minutes'),
    (1, 'BANKER_CHECK_SAFE', 'Deadlock avoidance check: Request=[1,1,0], Safe sequence found: P1->P2->P3', 'RESOURCE_MANAGER', NOW() - INTERVAL '21 minutes'),
    (1, 'RESOURCE_ASSIGNED', 'Allocated Ambulance-Delta-03 and Margao Medical Unit', 'WORKER_THREAD_1', NOW() - INTERVAL '20 minutes'),
    (1, 'TRANSACTION_COMMITTED', 'ACID transaction committed: resource, team, and incident state updated', 'DB_TRANSACTION_MGR', NOW() - INTERVAL '20 minutes'),
    (2, 'INCIDENT_CREATED', 'SOS distress call triggered via mobile button press', 'API_DISPATCHER', NOW() - INTERVAL '12 minutes'),
    (2, 'PRIORITY_ENQUEUED', 'Assigned Priority 2 (SOS) into PriorityQueue awaiting available SAR team', 'SCHEDULER_ENGINE', NOW() - INTERVAL '11 minutes');
