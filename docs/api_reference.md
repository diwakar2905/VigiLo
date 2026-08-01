# VigiLo Public API Reference (v1)

> Stable, versioned public API facade (`src/api/v1/public_api.py`) exposing core VigiLo capabilities to UI components, plugins, and automation engines.

## Endpoints & Methods

### 1. Device State API
- `get_device_state() -> str`: Returns current DeviceState (`DISARMED`, `WATCH_MODE`, `LOST_MODE`).
- `set_device_state(target_state: str, reason: str, actor: str) -> bool`: Transitions system state.

### 2. Device Identity API
- `get_device_identity() -> DeviceIdentityModel`: Returns hardware-bound UUID, Public ID, and RSA fingerprint.

### 3. Timeline & Incident API
- `get_timeline_events(filter_type: str, limit: int) -> List[IncidentEvent]`: Fetches persistent timeline.
- `record_incident(event_type: str, severity: str, description: str, metadata: dict) -> IncidentEvent`: Records event with SHA-256 hash.
- `generate_forensic_report() -> IncidentReportModel`: Compiles tamper-evident forensic report.

### 4. Health & Diagnostics API
- `get_system_health() -> str`: Returns aggregate system status (`HEALTHY`, `DEGRADED`, `UNHEALTHY`).
- `run_self_diagnostics() -> Dict`: Runs automated probe checks.

### 5. Observability API
- `get_telemetry_snapshot() -> TelemetrySnapshot`: Exposes real-time CPU, RAM, queue size, thread counts.