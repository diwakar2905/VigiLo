# VigiLo Engineering Bible & Architecture Specifications

## 1. Architecture Pattern & Scoping Rules

VigiLo enforces a strict **Controller -> Service -> Repository -> Model -> UI** pattern.

```
UI (Desktop Dashboard / Telegram Command Handlers)
       │
       ▼
Controller Layer (DeviceStateController, HealthController, etc.)
       │
       ▼
Service Layer (DeviceStateService, HealthMonitorService - implements IService)
       │
       ▼
Repository Layer (DeviceStateRepository, TimelineRepository, AuditLogRepository)
       │
       ▼
Models (DeviceStateModel, IncidentEvent, IncidentReportModel, HealthObject)
```

### Architectural Guarantees
1. **No Circular Dependencies**: Controller modules import Services; Services import Repositories and Models. No reverse imports allowed.
2. **Dependency Injection**: `ServiceContainer` acts as the global single-point-of-truth DI container wiring all repositories, services, and controllers.
3. **Interface Compliance**: All business services derive from `IService` and implement standard lifecycle (`initialize()`, `shutdown()`).

---

## 2. Device State Machine Specification

| State | Allowed Capabilities | Prohibited Capabilities |
| :--- | :--- | :--- |
| `DISARMED` | Runtime health, config viewing, log viewing | Failed login monitoring, camera capture, notifications, workstation lock, geo-locate, audio recording, file browsing |
| `WATCH_MODE` | Failed login monitoring, intruder camera capture, alert notifications, timeline logging | Remote workstation lock, silent screenshots, file browsing, audio recording |
| `LOST_MODE` | All Watch Mode features + Remote lock, Geo-locate, silent screenshots, recovery message, evidence collection, report generation | File browsing, audio recording, malware-like remote code execution |

---

## 3. Cryptographic Integrity & SHA-256 Hashing

Every timeline event computes a SHA-256 hash across its immutable fields:
`sha256(incident_id | timestamp | event_type | severity | description | json(metadata))`

The Incident Report generator computes a master summary hash across all timeline events and image hashes:
`sha256(report_id | device_id | generated_at | event_hashes | image_hashes)`

This guarantees legal admissibility and tamper verification.
