// ============================================================
// Smart Tourist Safety and Emergency Response System
// Authority Command Dashboard Logic (Phase 19)
// ============================================================

const API_BASE = window.location.origin;

// State management
let mapInstance = null;
let markers = {
  tourists: {},
  incidents: {},
  zones: [],
  resources: {},
};
let activeIncidents = [];
let zonesData = [];
let touristsData = [];
let teamsData = [];
let resourcesData = [];

// Predefined Goa Coordinates
const GOA_CENTER = [15.35, 73.95];

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  initLiveClock();
  initTacticalMap();
  initSocketIO();
  initActionHandlers();
  initTabNavigation();
  initFilterHandlers();
  
  // Initial data fetch
  refreshAllData();

  // Polling loop (every 3 seconds)
  setInterval(refreshAllData, 3000);
});

// ============================================================
// 1. Live Clock
// ============================================================
function initLiveClock() {
  const clockEl = document.getElementById("liveClock");
  function updateTime() {
    const now = new Date();
    clockEl.textContent = now.toUTCString().slice(17, 25) + " UTC";
  }
  updateTime();
  setInterval(updateTime, 1000);
}

// ============================================================
// 2. Leaflet Tactical Map Initialization
// ============================================================
function initTacticalMap() {
  const mapEl = document.getElementById("tacticalMap");
  if (!mapEl) return;

  mapInstance = L.map("tacticalMap", {
    zoomControl: true,
    attributionControl: false,
  }).setView(GOA_CENTER, 10);

  // High-contrast dark basemap tiles (CartoDB DarkMatter)
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 18,
    subdomains: "abcd",
  }).addTo(mapInstance);

  // Render predefined Safe and Dangerous Geofence Zones
  renderStaticZones();
}

function renderStaticZones() {
  const defaultZones = [
    { name: "Baga Beach Promenade", type: "SAFE", lat: 15.5553, lng: 73.7516, radiusKm: 2.5, risk: "LOW" },
    { name: "Old Goa Historic Quarter", type: "SAFE", lat: 15.5030, lng: 73.9118, radiusKm: 3.0, risk: "LOW" },
    { name: "Aguada Sea Cliff Surge Area", type: "DANGEROUS", lat: 15.4925, lng: 73.7735, radiusKm: 1.2, risk: "HIGH" },
    { name: "Netravali Dense Forest Reserve", type: "DANGEROUS", lat: 15.0872, lng: 74.2081, radiusKm: 6.0, risk: "HIGH" },
    { name: "Dudhsagar Waterfall Rapids & Gorge", type: "DANGEROUS", lat: 15.3144, lng: 74.3144, radiusKm: 3.5, risk: "CRITICAL" },
  ];

  defaultZones.forEach((z) => {
    const isDangerous = z.type === "DANGEROUS";
    const color = isDangerous ? "#ef4444" : "#10b981";
    const fillColor = isDangerous ? "#ef4444" : "#10b981";

    const circle = L.circle([z.lat, z.lng], {
      color: color,
      fillColor: fillColor,
      fillOpacity: isDangerous ? 0.22 : 0.15,
      weight: 2,
      radius: z.radiusKm * 1000,
    }).addTo(mapInstance);

    circle.bindPopup(`
      <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #1e293b;">
        <strong style="color: ${color}; font-size: 13px;">${z.name}</strong><br>
        <strong>Category:</strong> ${z.type} ZONE<br>
        <strong>Risk Level:</strong> ${z.risk}<br>
        <strong>Radius:</strong> ${z.radiusKm} km
      </div>
    `);
  });
}

// ============================================================
// 3. Socket.IO Real-Time Stream
// ============================================================
function initSocketIO() {
  try {
    const socket = io();

    socket.on("connect", () => {
      appendTerminalLog("WebSocket connected to tourist safety hub.", "info");
      socket.emit("join_room", { room: "dashboard" });
    });

    socket.on("emergency_alert", (data) => {
      const inc = data.incident || {};
      appendTerminalLog(`🚨 NEW EMERGENCY: [${inc.incident_type || 'SOS'}] Priority ${inc.priority}`, "danger");
      triggerAlertBanner(inc);
      refreshAllData();
    });

    socket.on("incident_status_changed", (data) => {
      const inc = data.incident || {};
      appendTerminalLog(`State transition: Incident #${inc.incident_id} -> ${inc.status}`, "warning");
      refreshAllData();
    });

    socket.on("resource_allocated", (data) => {
      appendTerminalLog(`Banker's Algorithm: Resource allocated for incident #${data.incident_id}`, "success");
      refreshAllData();
    });

    socket.on("resource_released", (data) => {
      appendTerminalLog(`Resource released for incident #${data.incident_id}. Available fleet restored.`, "info");
      refreshAllData();
    });

  } catch (e) {
    console.warn("Socket.IO client initialization skipped:", e);
  }
}

// ============================================================
// 4. Data Refresh Routines
// ============================================================
async function refreshAllData() {
  await Promise.all([
    fetchSummary(),
    fetchActiveEmergencies(),
    fetchBankerState(),
    fetchSchedulerStats(),
    fetchWorkerStats(),
    fetchRecentLogs(),
    fetchTourists(),
    fetchTeams(),
    fetchResources(),
  ]);
}

async function fetchSummary() {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard/summary`);
    if (!res.ok) return;
    const json = await res.json();
    const m = json.metrics || {};

    document.getElementById("valTourists").textContent = m.total_tourists ?? "--";
    document.getElementById("valEmergencies").textContent = m.active_incidents ?? "0";
    document.getElementById("valResources").textContent = 
      `${m.available_resources ?? 0} Veh / ${m.available_teams ?? 0} Teams`;
    const badgeBanker = document.getElementById("bankerStatusText");
    if (m.is_safe_state) {
      badgeBanker.textContent = "BANKER'S: SAFE STATE";
      document.getElementById("bankerSafetyBadge").textContent = "SAFE";
      document.getElementById("bankerSafetyBadge").className = "badge badge-p4";
    } else {
      badgeBanker.textContent = "BANKER'S: UNSAFE";
      document.getElementById("bankerSafetyBadge").textContent = "UNSAFE";
      document.getElementById("bankerSafetyBadge").className = "badge badge-p1";
    }

  } catch (e) {
    console.debug("Error fetching summary:", e);
  }
}

async function fetchActiveEmergencies() {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard/active-emergencies`);
    if (!res.ok) return;
    const json = await res.json();
    activeIncidents = json.data || [];
    renderIncidentsTable(activeIncidents);
    updateMapIncidentMarkers(activeIncidents);
    renderPendingQueueStats();
  } catch (e) {
    console.debug("Error fetching active emergencies:", e);
  }
}

function renderIncidentsTable(incidents) {
  const incBadge = document.getElementById("tabBadgeIncidents");
  if (incBadge) incBadge.textContent = incidents.length;

  const tbody = document.getElementById("incidentsBody");
  if (!tbody) return;

  if (incidents.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="table-empty">✅ All clear! No active distress incidents recorded.</td></tr>`;
    return;
  }

  tbody.innerHTML = incidents.map((inc) => {
    const pClass = `badge-p${inc.priority || 5}`;
    const lat = Number(inc.latitude).toFixed(4);
    const lng = Number(inc.longitude).toFixed(4);
    const description = inc.description?.trim()
      ? escapeHtml(inc.description)
      : '<span class="incident-no-details">No details provided</span>';
    const descriptionTitle = escapeHtml(inc.description?.trim() || "No details provided");
    return `
      <tr>
        <td><span class="badge ${pClass}">P${inc.priority}</span></td>
        <td><strong>#${inc.incident_id}</strong></td>
        <td>${escapeHtml(inc.tourist_name || `Tourist #${inc.tourist_id}`)}<br><small style="color:#64748b">${escapeHtml(inc.tourist_phone || '')}</small></td>
        <td><strong>${escapeHtml(inc.incident_type || 'SOS')}</strong></td>
        <td><div class="incident-description" title="${descriptionTitle}">${description}</div></td>
        <td style="font-family:'JetBrains Mono', monospace; font-size:11px;">${lat}, ${lng}</td>
        <td><span class="badge" style="background:rgba(30,41,59,0.7);">${escapeHtml(inc.status || 'RECEIVED')}</span></td>
        <td>
          <div style="display:flex; gap:4px;">
            <button class="btn btn-sm btn-secondary" onclick="handleAssignResource(${inc.incident_id})">Dispatch</button>
            <button class="btn btn-sm btn-outline-danger" onclick="handleResolveIncident(${inc.incident_id})">Resolve</button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function updateMapIncidentMarkers(incidents) {
  if (!mapInstance) return;

  // Clear obsolete markers
  Object.keys(markers.incidents).forEach((id) => {
    if (!incidents.find((i) => i.incident_id == id)) {
      mapInstance.removeLayer(markers.incidents[id]);
      delete markers.incidents[id];
    }
  });

  // Add/update active markers
  incidents.forEach((inc) => {
    const id = inc.incident_id;
    const lat = Number(inc.latitude);
    const lng = Number(inc.longitude);

    if (markers.incidents[id]) {
      markers.incidents[id].setLatLng([lat, lng]);
    } else {
      const markerColor = inc.priority === 1 ? '#ef4444' : (inc.priority === 2 ? '#f59e0b' : '#3b82f6');
      const icon = L.divIcon({
        className: 'custom-incident-marker',
        html: `<div style="background:${markerColor}; width:16px; height:16px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 10px ${markerColor};"></div>`,
        iconSize: [16, 16],
      });

      const m = L.marker([lat, lng], { icon: icon }).addTo(mapInstance);
      m.bindPopup(`
        <div style="font-family:'Inter', sans-serif; font-size:12px; color:#1e293b;">
          <strong style="color:${markerColor};">🚨 Incident #${inc.incident_id}</strong><br>
          <strong>Type:</strong> ${escapeHtml(inc.incident_type || 'SOS')} (Priority ${inc.priority})<br>
          <strong>Details:</strong> ${escapeHtml(inc.description || 'No details provided')}<br>
          <strong>Status:</strong> ${escapeHtml(inc.status || 'RECEIVED')}<br>
          <strong>Tourist:</strong> ${escapeHtml(inc.tourist_name || inc.tourist_id)}
        </div>
      `);
      markers.incidents[id] = m;
    }
  });
}

async function fetchBankerState() {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard/banker-state`);
    if (!res.ok) return;
    const json = await res.json();
    const banker = json.banker_matrices || {};
    const avail = banker.available || {};

    document.getElementById("availAmb").textContent = avail.AMBULANCE ?? "--";
    document.getElementById("availTeams").textContent = avail.RESCUE_TEAM ?? "--";
    document.getElementById("availCopter").textContent = avail.HELICOPTER ?? "--";

    const seqBox = document.getElementById("safeSequenceBox");
    const seqStatus = document.getElementById("safeSequenceStatus");
    const safeSequence = banker.safe_sequence || [];
    if (banker.is_safe && safeSequence.length > 0) {
      seqBox.textContent = safeSequence.map((processId) => `Incident #${processId}`).join("  →  ");
      seqBox.style.color = "#34d399";
      seqStatus.textContent = `SAFE · ${safeSequence.length} active request${safeSequence.length === 1 ? "" : "s"} can finish in this order`;
      seqStatus.style.color = "#34d399";
    } else if (banker.is_safe) {
      seqBox.textContent = "No active requests";
      seqBox.style.color = "#94a3b8";
      seqStatus.textContent = "SAFE · System is idle";
      seqStatus.style.color = "#34d399";
    } else {
      seqBox.textContent = safeSequence.length
        ? safeSequence.map((processId) => `Incident #${processId}`).join("  →  ")
        : "No safe execution order exists";
      seqBox.style.color = "#f87171";
      seqStatus.textContent = "UNSAFE · Allocation state needs attention";
      seqStatus.style.color = "#f87171";
    }
  } catch (e) {
    console.debug("Error fetching Banker's state:", e);
  }
}

async function fetchSchedulerStats() {
  renderPendingQueueStats();
}

function renderPendingQueueStats() {
  const queued = activeIncidents.filter((incident) => ["RECEIVED", "QUEUED"].includes(incident.status));
  const pCounts = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  queued.forEach((incident) => {
    if (pCounts[incident.priority] !== undefined) pCounts[incident.priority]++;
  });

  document.getElementById("countP1").textContent = pCounts[1];
  document.getElementById("countP2").textContent = pCounts[2];
  document.getElementById("countP3").textContent = pCounts[3];
  document.getElementById("countP4").textContent = pCounts[4];
  document.getElementById("countP5").textContent = pCounts[5];
  document.getElementById("valQueue").textContent = queued.length;
  document.getElementById("queueStatusText").textContent = `QUEUE: ${queued.length} PENDING`;
}

async function fetchWorkerStats() {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard/worker-stats`);
    if (!res.ok) return;
    const json = await res.json();
    const pool = json.worker_pool || {};
    const tasksByWorker = pool.tasks_by_worker || {};

    if (tasksByWorker["EmergencyWorker-1"] !== undefined) {
      document.getElementById("w1Tasks").textContent = `Tasks: ${tasksByWorker["EmergencyWorker-1"]}`;
    }
    if (tasksByWorker["EmergencyWorker-2"] !== undefined) {
      document.getElementById("w2Tasks").textContent = `Tasks: ${tasksByWorker["EmergencyWorker-2"]}`;
    }
    if (tasksByWorker["EmergencyWorker-3"] !== undefined) {
      document.getElementById("w3Tasks").textContent = `Tasks: ${tasksByWorker["EmergencyWorker-3"]}`;
    }
  } catch (e) {
    console.debug("Error fetching worker stats:", e);
  }
}

async function fetchRecentLogs() {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard/logs?limit=8`);
    if (!res.ok) return;
    const json = await res.json();
    const logs = json.data || [];
    
    const terminal = document.getElementById("terminalLogs");
    if (!terminal || logs.length === 0) return;

    terminal.innerHTML = logs.map((log) => {
      let logClass = "log-info";
      if (log.action.includes("CRITICAL") || log.action.includes("ACCIDENT")) logClass = "log-danger";
      else if (log.action.includes("BREACH") || log.action.includes("SOS")) logClass = "log-warning";
      else if (log.action.includes("ALLOCATED") || log.action.includes("RELEASED")) logClass = "log-success";

      const timeStr = log.created_at ? log.created_at.slice(11, 19) : "";
      return `<div class="log-entry ${logClass}">[${timeStr}] [${log.action}] #${log.incident_id || 0}: ${log.details || ''}</div>`;
    }).join("");
  } catch (e) {
    console.debug("Error fetching logs:", e);
  }
}

// ============================================================
// 5. Interactive Simulation Handlers
// ============================================================
function initActionHandlers() {
  // Critical Accident (P1)
  document.getElementById("btnSimAccident")?.addEventListener("click", async () => {
    appendTerminalLog("Simulating Critical Accident (Priority 1)...", "warning");
    const payload = {
      tourist_id: 1,
      latitude: 15.4925,
      longitude: 73.7735,
      description: "Severe sea-cliff impact accident",
    };
    await sendEmergencyRequest("/api/emergencies/accident", payload);
  });

  // SOS (P2)
  document.getElementById("btnSimSOS")?.addEventListener("click", async () => {
    appendTerminalLog("Simulating Mobile SOS Distress (Priority 2)...", "warning");
    const payload = {
      tourist_id: 2,
      latitude: 15.5553,
      longitude: 73.7516,
      description: "Tourist triggered SOS distress beacon",
    };
    await sendEmergencyRequest("/api/emergencies/sos", payload);
  });

  // Geofence Breach (P3)
  document.getElementById("btnSimGeofence")?.addEventListener("click", async () => {
    appendTerminalLog("Simulating Dangerous Geofence Breach (Priority 3)...", "warning");
    const payload = {
      tourist_id: 3,
      latitude: 15.3144,
      longitude: 74.3144,
      description: "Perimeter breach in Dudhsagar Rapids Gorge",
    };
    await sendEmergencyRequest("/api/emergencies/geofence", payload);
  });

  // GPS Ping (P5)
  document.getElementById("btnSimGPS")?.addEventListener("click", async () => {
    appendTerminalLog("Submitting GPS telemetry ping (Priority 5)...", "info");
    const payload = {
      tourist_id: 1,
      latitude: 15.5560,
      longitude: 73.7525,
    };
    await fetch(`${API_BASE}/api/location`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    refreshAllData();
  });

  // Full Simulation
  document.getElementById("btnRunSim")?.addEventListener("click", async () => {
    await runIncidentSimulation();
  });

  document.getElementById("btnAddSample")?.addEventListener("click", async () => {
    await addSampleTouristsAndEmergencies();
  });

  // Banker's Test: Safe Grant
  document.getElementById("btnTestSafeAlloc")?.addEventListener("click", async () => {
    appendTerminalLog("Testing Banker's Algorithm Safe Grant (1 Ambulance)...", "info");
    const payload = {
      incident_id: 999,
      demands: { AMBULANCE: 1, RESCUE_TEAM: 0, HELICOPTER: 0 },
      incident_type: "SOS",
    };
    const res = await fetch(`${API_BASE}/api/resources/allocate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    if (json.allocated) {
      appendTerminalLog(`Safe allocation approved! Sequence: ${JSON.stringify(json.safe_sequence)}`, "success");
    } else {
      appendTerminalLog(`Allocation rejected: ${json.reason}`, "danger");
    }
    refreshAllData();
  });

  // Banker's Test: Deadlock Deny
  document.getElementById("btnTestUnsafeAlloc")?.addEventListener("click", async () => {
    appendTerminalLog("Testing Banker's Deadlock Avoidance (Demanding 20 Ambulances)...", "warning");
    const payload = {
      incident_id: 998,
      demands: { AMBULANCE: 20, RESCUE_TEAM: 10, HELICOPTER: 5 },
      incident_type: "CRITICAL_ACCIDENT",
    };
    const res = await fetch(`${API_BASE}/api/resources/allocate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    appendTerminalLog(`DEADLOCK DENIED by Banker's: ${json.reason}`, "danger");
    refreshAllData();
  });

  // Refresh button
  document.getElementById("btnRefreshIncidents")?.addEventListener("click", refreshAllData);

  // Dismiss alert
  document.getElementById("btnDismissAlert")?.addEventListener("click", () => {
    document.getElementById("alertBanner").style.display = "none";
  });
}

async function sendEmergencyRequest(endpoint, payload) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    refreshAllData();
    return json;
  } catch (e) {
    console.error("Failed emergency request:", e);
  }
}

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, options);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.message || payload.reason || `Request failed (${response.status})`);
  }
  return payload;
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function addSampleTouristsAndEmergencies() {
  const button = document.getElementById("btnAddSample");
  const runButton = document.getElementById("btnRunSim");
  if (button?.disabled) return;
  if (button) {
    button.disabled = true;
    button.textContent = "Adding…";
  }
  if (runButton) runButton.disabled = true;

  const batchId = Date.now();
  const samples = [
    {
      name: "Demo Tourist Asha",
      phone: `+1555${String(batchId).slice(-7)}1`,
      email: `demo.${batchId}.1@example.com`,
      description: "Suspected stroke; sudden weakness and difficulty speaking.",
      latitude: 15.5030,
      longitude: 73.9118,
    },
    {
      name: "Demo Tourist Ravi",
      phone: `+1555${String(batchId).slice(-7)}2`,
      email: `demo.${batchId}.2@example.com`,
      description: "Asthma attack; having difficulty breathing.",
      latitude: 15.5553,
      longitude: 73.7516,
    },
    {
      name: "Demo Tourist Mina",
      phone: `+1555${String(batchId).slice(-7)}3`,
      email: `demo.${batchId}.3@example.com`,
      description: "Fall injury; tourist reports severe pain and needs assistance.",
      latitude: 15.4925,
      longitude: 73.7735,
    },
  ];

  let created = 0;
  try {
    for (const sample of samples) {
      const touristResponse = await apiRequest("/api/tourists", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: sample.name,
          phone: sample.phone,
          email: sample.email,
          nationality: "Demo",
        }),
      });
      const tourist = touristResponse.data;

      const emergencyResponse = await apiRequest("/api/emergencies/sos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tourist_id: tourist.tourist_id,
          latitude: sample.latitude,
          longitude: sample.longitude,
          description: sample.description,
        }),
      });
      const incident = emergencyResponse.data;

      await apiRequest(`/api/emergencies/${incident.incident_id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: "QUEUED",
          details: "Added to the dispatcher queue for the dashboard demonstration.",
          action: "QUEUED_FOR_DISPATCH",
          performed_by: "DashboardSample",
        }),
      });
      created++;
      appendTerminalLog(`Sample SOS queued: Incident #${incident.incident_id} for ${tourist.name}.`, "warning");
    }

    await refreshAllData();
    appendTerminalLog(`Sample batch complete: ${created} demo tourists and emergencies added.`, "success");
  } catch (error) {
    appendTerminalLog(`Sample batch stopped after ${created} incident(s): ${error.message}`, "danger");
    await refreshAllData();
  } finally {
    if (button) {
      button.disabled = false;
      button.innerHTML = "<span>＋</span> Sample";
    }
    if (runButton) runButton.disabled = false;
  }
}

async function runIncidentSimulation() {
  const button = document.getElementById("btnRunSim");
  const sampleButton = document.getElementById("btnAddSample");
  if (button?.disabled) return;
  if (button) {
    button.disabled = true;
    button.textContent = "Processing…";
  }
  if (sampleButton) sampleButton.disabled = true;

  try {
    const response = await apiRequest("/api/dashboard/active-emergencies");
    const incidents = (response.data || []).sort((a, b) => {
      const priorityDifference = (a.priority || 5) - (b.priority || 5);
      if (priorityDifference !== 0) return priorityDifference;
      return new Date(a.created_at) - new Date(b.created_at);
    });

    if (incidents.length === 0) {
      appendTerminalLog("No active incidents to process. Add a sample batch or wait for an emergency.", "info");
      return;
    }

    appendTerminalLog(`Simulation dispatch started for ${incidents.length} active incident(s), in priority order.`, "info");
    for (let index = 0; index < incidents.length; index++) {
      const incident = incidents[index];
      appendTerminalLog(`Processing ${index + 1}/${incidents.length}: Incident #${incident.incident_id} (P${incident.priority}).`, "warning");

      if (!["PROCESSING", "RESOURCE_ASSIGNED"].includes(incident.status)) {
        await apiRequest(`/api/emergencies/${incident.incident_id}/status`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            status: "PROCESSING",
            details: "Dashboard simulation began handling this emergency.",
            action: "SIMULATION_DISPATCH_STARTED",
            performed_by: "DashboardSimulation",
          }),
        });
        await refreshAllData();
        await wait(850);
      }

      await window.handleResolveIncident(
        incident.incident_id,
        "Dashboard simulation completed the response automatically."
      );
      appendTerminalLog(`Incident #${incident.incident_id} resolved (${index + 1}/${incidents.length}).`, "success");
      await wait(450);
    }

    appendTerminalLog("Simulation complete: all active incidents were handled one by one.", "success");
  } catch (error) {
    appendTerminalLog(`Simulation stopped: ${error.message}`, "danger");
  } finally {
    if (button) {
      button.disabled = false;
      button.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Run Simulation';
    }
    if (sampleButton) sampleButton.disabled = false;
    await refreshAllData();
  }
}

// Table Action: Dispatch
window.handleAssignResource = async function (incidentId) {
  appendTerminalLog(`Dispatching resources for incident #${incidentId}...`, "info");
  const payload = {
    incident_id: incidentId,
    demands: { AMBULANCE: 1, RESCUE_TEAM: 1 },
  };
  await fetch(`${API_BASE}/api/resources/allocate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  refreshAllData();
};

// Table Action: Resolve
window.handleResolveIncident = async function (incidentId, details = "Dispatcher marked resolved.") {
  appendTerminalLog(`Resolving incident #${incidentId} and releasing held resources...`, "info");
  await apiRequest("/api/resources/release", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ incident_id: incidentId }),
  });
  await apiRequest(`/api/emergencies/${incidentId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: "RESOLVED", details }),
  });
  await refreshAllData();
};

function triggerAlertBanner(incident) {
  const banner = document.getElementById("alertBanner");
  const title = document.getElementById("alertTitle");
  const details = document.getElementById("alertDetails");
  if (!banner) return;

  title.textContent = `CRITICAL INCIDENT #${incident.incident_id || 0} [${incident.incident_type || 'SOS'}]`;
  const reason = incident.description?.trim() || 'No additional details provided';
  details.textContent = `${reason} · Priority ${incident.priority || 1} · (${Number(incident.latitude).toFixed(4)}, ${Number(incident.longitude).toFixed(4)})`;
  banner.style.display = "flex";
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function appendTerminalLog(message, type = "info") {
  const terminal = document.getElementById("terminalLogs");
  if (!terminal) return;
  const time = new Date().toTimeString().slice(0, 8);
  const div = document.createElement("div");
  div.className = `log-entry log-${type}`;
  div.textContent = `[${time}] ${message}`;
  terminal.prepend(div);
}

// ============================================================
// 6. Tab Navigation
// ============================================================
function initTabNavigation() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      if (!targetId) return;

      // Deactivate all tabs and panels
      tabBtns.forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));

      // Activate clicked tab and its panel
      btn.classList.add("active");
      const panel = document.getElementById(targetId);
      if (panel) panel.classList.add("active");
    });
  });
}

// ============================================================
// 7. Filter & Search Handlers
// ============================================================
function initFilterHandlers() {
  // Tourists search
  document.getElementById("touristSearchInput")?.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    filterTouristsTable(q, document.getElementById("filterBloodGroup")?.value || "");
  });

  // Tourists blood group filter
  document.getElementById("filterBloodGroup")?.addEventListener("change", (e) => {
    const q = document.getElementById("touristSearchInput")?.value?.toLowerCase() || "";
    filterTouristsTable(q, e.target.value);
  });

  // Teams search
  document.getElementById("teamSearchInput")?.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    filterTeamsTable(q, document.getElementById("filterTeamStatus")?.value || "");
  });

  // Teams status filter
  document.getElementById("filterTeamStatus")?.addEventListener("change", (e) => {
    const q = document.getElementById("teamSearchInput")?.value?.toLowerCase() || "";
    filterTeamsTable(q, e.target.value);
  });

  // Resources type filter
  document.getElementById("filterResourceType")?.addEventListener("change", () => {
    filterResourcesTable();
  });

  // Resources status filter
  document.getElementById("filterResourceStatus")?.addEventListener("change", () => {
    filterResourcesTable();
  });

  // Refresh buttons
  document.getElementById("btnRefreshTourists")?.addEventListener("click", fetchTourists);
  document.getElementById("btnRefreshTeams")?.addEventListener("click", fetchTeams);
  document.getElementById("btnRefreshResources")?.addEventListener("click", fetchResources);
}

function filterTouristsTable(query, bloodFilter) {
  const filtered = touristsData.filter((t) => {
    const matchesSearch = !query ||
      (t.name || "").toLowerCase().includes(query) ||
      (t.phone || "").toLowerCase().includes(query) ||
      (t.email || "").toLowerCase().includes(query) ||
      (t.nationality || "").toLowerCase().includes(query);
    const matchesBlood = !bloodFilter || (t.blood_group || "") === bloodFilter;
    return matchesSearch && matchesBlood;
  });
  renderTouristsTable(filtered);
}

function filterTeamsTable(query, statusFilter) {
  const filtered = teamsData.filter((t) => {
    const matchesSearch = !query ||
      (t.team_name || "").toLowerCase().includes(query) ||
      (t.specialization || "").toLowerCase().includes(query);
    const matchesStatus = !statusFilter || (t.status || "") === statusFilter;
    return matchesSearch && matchesStatus;
  });
  renderTeamsTable(filtered);
}

function filterResourcesTable() {
  const typeFilter = document.getElementById("filterResourceType")?.value || "";
  const statusFilter = document.getElementById("filterResourceStatus")?.value || "";
  const filtered = resourcesData.filter((r) => {
    const matchesType = !typeFilter || (r.resource_type || "") === typeFilter;
    const matchesStatus = !statusFilter || (r.status || "") === statusFilter;
    return matchesType && matchesStatus;
  });
  renderResourcesTable(filtered);
}

// ============================================================
// 8. Fetch & Render Tourists
// ============================================================
async function fetchTourists() {
  try {
    const res = await fetch(`${API_BASE}/api/tourists?limit=100`);
    if (!res.ok) return;
    const json = await res.json();
    touristsData = json.data || [];
    renderTouristsTable(touristsData);
    const badge = document.getElementById("tabBadgeTourists");
    if (badge) badge.textContent = touristsData.length;
  } catch (e) {
    console.debug("Error fetching tourists:", e);
  }
}

function renderTouristsTable(tourists) {
  const tbody = document.getElementById("touristsBody");
  if (!tbody) return;

  if (tourists.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No registered tourists found.</td></tr>`;
    return;
  }

  tbody.innerHTML = tourists.map((t) => {
    const initials = (t.name || "?").split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2);
    const bloodBadge = t.blood_group
      ? `<span class="blood-badge">${t.blood_group}</span>`
      : `<span style="color: var(--text-dim);">N/A</span>`;
    const regDate = (t.registered_at || t.created_at) ? new Date(t.registered_at || t.created_at).toLocaleDateString("en-IN", {
      year: "numeric", month: "short", day: "numeric"
    }) : "—";
    const contactCount = t.contact_count || t.emergency_contact_count || 0;

    return `
      <tr>
        <td><strong>#${t.tourist_id}</strong></td>
        <td>
          <div class="avatar-cell">
            <div class="avatar-badge">${initials}</div>
            <div>
              <strong>${t.name}</strong>
            </div>
          </div>
        </td>
        <td>
          <div style="display:flex; flex-direction:column; gap:3px;">
            <span class="contact-chip">📞 ${t.phone || 'N/A'}</span>
            <span class="contact-chip">✉️ ${t.email || 'N/A'}</span>
          </div>
        </td>
        <td>
          <div style="display:flex; flex-direction:column; gap:4px;">
            <span style="font-size:0.8rem;">🌍 ${t.nationality || 'Unknown'}</span>
            ${bloodBadge}
          </div>
        </td>
        <td>
          <span class="contact-chip">👨‍👩‍👧 ${contactCount} contact${contactCount !== 1 ? 's' : ''}</span>
        </td>
        <td style="font-size:0.78rem; color: var(--text-muted);">${regDate}</td>
        <td>
          <button class="btn btn-sm btn-secondary" onclick="viewTouristProfile(${t.tourist_id})">View Profile</button>
        </td>
      </tr>
    `;
  }).join("");
}

// Tourist Profile Modal
window.viewTouristProfile = async function(touristId) {
  try {
    const res = await fetch(`${API_BASE}/api/tourists/${touristId}`);
    if (!res.ok) return;
    const json = await res.json();
    const t = json.data || {};

    document.getElementById("mTouristName").textContent = t.name || "Tourist";
    document.getElementById("mTouristId").textContent = `#${t.tourist_id}`;

    // Fetch contacts
    let contactsHtml = "";
    try {
      const cRes = await fetch(`${API_BASE}/api/tourists/${touristId}/contacts`);
      if (cRes.ok) {
        const cJson = await cRes.json();
        const contacts = cJson.data || [];
        if (contacts.length > 0) {
          contactsHtml = contacts.map((c) => `
            <div class="detail-row">
              <span class="detail-label">${c.relationship || 'Contact'}</span>
              <span class="detail-val">${c.name} — ${c.phone}</span>
            </div>
          `).join("");
        } else {
          contactsHtml = `<div class="detail-row"><span class="detail-label">Emergency Contacts</span><span class="detail-val" style="color:var(--text-dim);">None registered</span></div>`;
        }
      }
    } catch (ce) {
      contactsHtml = `<div class="detail-row"><span class="detail-label">Emergency Contacts</span><span class="detail-val" style="color:var(--text-dim);">Could not load</span></div>`;
    }

    const body = document.getElementById("touristModalBody");
    body.innerHTML = `
      <div class="detail-row">
        <span class="detail-label">Full Name</span>
        <span class="detail-val">${t.name || '—'}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Phone</span>
        <span class="detail-val">${t.phone || '—'}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Email</span>
        <span class="detail-val">${t.email || '—'}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Nationality</span>
        <span class="detail-val">${t.nationality || '—'}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Blood Group</span>
        <span class="detail-val">${t.blood_group ? `<span class="blood-badge">${t.blood_group}</span>` : '—'}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Registered</span>
        <span class="detail-val">${(t.registered_at || t.created_at) ? new Date(t.registered_at || t.created_at).toLocaleString() : '—'}</span>
      </div>
      <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--border-subtle);">
        <div class="matrix-title" style="margin-bottom: 0.5rem;">Emergency Next-of-Kin Contacts</div>
        ${contactsHtml}
      </div>
    `;

    document.getElementById("touristModal").style.display = "flex";
  } catch (e) {
    console.error("Error loading tourist profile:", e);
  }
};

// Close tourist modal
document.getElementById("btnCloseTouristModal")?.addEventListener("click", () => {
  document.getElementById("touristModal").style.display = "none";
});

// Close modal when clicking backdrop
document.getElementById("touristModal")?.addEventListener("click", (e) => {
  if (e.target.id === "touristModal") {
    document.getElementById("touristModal").style.display = "none";
  }
});

// ============================================================
// 9. Fetch & Render Rescue Teams
// ============================================================
async function fetchTeams() {
  try {
    const res = await fetch(`${API_BASE}/api/resources/teams`);
    if (!res.ok) return;
    const json = await res.json();
    teamsData = json.data || [];
    renderTeamsTable(teamsData);
    const badge = document.getElementById("tabBadgeTeams");
    if (badge) badge.textContent = teamsData.length;
  } catch (e) {
    console.debug("Error fetching teams:", e);
  }
}

function renderTeamsTable(teams) {
  const tbody = document.getElementById("teamsBody");
  if (!tbody) return;

  if (teams.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="table-empty">No rescue teams found.</td></tr>`;
    return;
  }

  tbody.innerHTML = teams.map((t) => {
    const statusColor = t.status === "AVAILABLE" ? "var(--color-success)" : "var(--color-warning)";
    const statusGlow = t.status === "AVAILABLE" ? "var(--color-success-glow)" : "var(--color-warning-glow)";
    const capacityPct = t.max_capacity > 0
      ? Math.round((t.current_capacity / t.max_capacity) * 100)
      : 0;
    const capacityHighClass = capacityPct > 75 ? " high" : "";

    return `
      <tr>
        <td><strong>#${t.team_id}</strong></td>
        <td>
          <div class="avatar-cell">
            <div class="avatar-badge" style="background: linear-gradient(135deg, ${statusColor}, #3b82f6);">🛡️</div>
            <strong>${t.team_name || 'Unnamed Team'}</strong>
          </div>
        </td>
        <td><span class="contact-chip">${t.specialization || 'General'}</span></td>
        <td>
          <div class="capacity-container">
            <div class="capacity-meter">
              <div class="capacity-fill${capacityHighClass}" style="width: ${capacityPct}%;"></div>
            </div>
            <span class="capacity-text">${t.current_capacity || 0} / ${t.max_capacity || 0} members</span>
          </div>
        </td>
        <td><span class="contact-chip">📞 ${t.contact_number || 'N/A'}</span></td>
        <td>
          <span class="badge" style="background: ${statusColor}22; color: ${statusColor}; border: 1px solid ${statusColor}55; box-shadow: 0 0 6px ${statusGlow};">
            <span class="dot" style="background: ${statusColor}; width:6px; height:6px; box-shadow: 0 0 4px ${statusColor};"></span>
            ${t.status || 'UNKNOWN'}
          </span>
        </td>
      </tr>
    `;
  }).join("");
}

// ============================================================
// 10. Fetch & Render Fleet Resources
// ============================================================
async function fetchResources() {
  try {
    const res = await fetch(`${API_BASE}/api/resources`);
    if (!res.ok) return;
    const json = await res.json();
    resourcesData = json.data || [];
    renderResourcesTable(resourcesData);
    const badge = document.getElementById("tabBadgeResources");
    if (badge) badge.textContent = resourcesData.length;
  } catch (e) {
    console.debug("Error fetching resources:", e);
  }
}

function renderResourcesTable(resources) {
  const tbody = document.getElementById("resourcesBody");
  if (!tbody) return;

  if (resources.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="table-empty">No fleet apparatus found.</td></tr>`;
    return;
  }

  const typeIcons = {
    AMBULANCE: "🚑",
    RESCUE_TEAM: "🛡️",
    HELICOPTER: "🚁",
    FIRE_TRUCK: "🚒",
    PATROL_BOAT: "🚤",
  };

  const statusStyles = {
    AVAILABLE: { bg: "rgba(16,185,129,0.15)", color: "#34d399", border: "rgba(16,185,129,0.4)" },
    ASSIGNED: { bg: "rgba(245,158,11,0.15)", color: "#fbbf24", border: "rgba(245,158,11,0.4)" },
    MAINTENANCE: { bg: "rgba(100,116,139,0.15)", color: "#94a3b8", border: "rgba(100,116,139,0.4)" },
    DISPATCHED: { bg: "rgba(59,130,246,0.15)", color: "#60a5fa", border: "rgba(59,130,246,0.4)" },
  };

  tbody.innerHTML = resources.map((r) => {
    const icon = typeIcons[r.resource_type] || "📦";
    const st = statusStyles[r.status] || statusStyles.MAINTENANCE;
    const lat = (r.current_lat || r.latitude) != null ? Number(r.current_lat || r.latitude).toFixed(4) : "—";
    const lng = (r.current_lng || r.longitude) != null ? Number(r.current_lng || r.longitude).toFixed(4) : "—";

    return `
      <tr>
        <td><strong>#${r.resource_id}</strong></td>
        <td>
          <div class="avatar-cell">
            <div class="avatar-badge" style="background: linear-gradient(135deg, ${st.color}, #3b82f6); font-size: 1rem;">${icon}</div>
            <strong>${r.name || r.resource_name || `Unit-${r.resource_id}`}</strong>
          </div>
        </td>
        <td><span class="contact-chip">${icon} ${(r.resource_type || 'UNKNOWN').replace(/_/g, ' ')}</span></td>
        <td style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; color: var(--text-muted);">${lat}, ${lng}</td>
        <td>
          <span class="badge" style="background: ${st.bg}; color: ${st.color}; border: 1px solid ${st.border};">
            ${r.status || 'UNKNOWN'}
          </span>
        </td>
        <td>
          ${r.status === 'AVAILABLE'
            ? `<button class="btn btn-sm btn-secondary" onclick="appendTerminalLog('Resource #${r.resource_id} flagged for dispatch.', 'info')">Flag Dispatch</button>`
            : `<span style="color: var(--text-dim); font-size: 0.75rem;">—</span>`
          }
        </td>
      </tr>
    `;
  }).join("");
}

