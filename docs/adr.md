# VigiLo Architecture Decision Records (ADRs)

## ADR-001: Formal Device State Machine Model
- **Status**: Approved & Implemented
- **Context**: The existing WatchDog system had an always-active monitoring model without clear separation between disarmed operation, local guarding, and active device loss.
- **Decision**: Introduce three distinct state machine modes (`DISARMED`, `WATCH_MODE`, `LOST_MODE`) enforced by `DeviceStateService` and `FeaturePermissionMatrix`.
- **Consequences**: Features such as workstation locking and silent screenshots are strictly restricted to `LOST_MODE`, protecting local user privacy during normal device usage.

## ADR-002: ServiceContainer Dependency Injection Pattern
- **Status**: Approved & Implemented
- **Context**: Decouple business logic, state persistence, timeline repositories, and UI controllers to prevent circular imports and god classes.
- **Decision**: Centralize initialization in `src/core/controllers/container.py` using a singleton `ServiceContainer`.
- **Consequences**: Standardized access across background services (`monitor.py`, `commander.py`) and desktop UI applications (`dashboard_app.py`).

## ADR-003: SHA-256 Tamper-Evident Hashing for Evidence Reports
- **Status**: Approved & Implemented
- **Context**: Incident reports and timeline entries must be legally verifiable and tamper-evident.
- **Decision**: Embed SHA-256 digest computation into `IncidentEvent` and `IncidentReportModel`.
- **Consequences**: Reports can be independently validated for authenticity and integrity.
