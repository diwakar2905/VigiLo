# VigiLo Architecture Decision Records (ADRs)

## ADR-001: Formal Device State Machine Model
- **Status**: Approved & Implemented
- **Context**: Require strict separation between disarmed operation, local intruder guarding, and active device loss.
- **Decision**: Introduce three state modes (`DISARMED`, `WATCH_MODE`, `LOST_MODE`) enforced by `DeviceStateService` and `FeaturePermissionMatrix`.

## ADR-002: ServiceContainer Dependency Injection Pattern
- **Status**: Approved & Implemented
- **Context**: Decouple business logic, state persistence, timeline repositories, and UI controllers to prevent circular imports.
- **Decision**: Centralize initialization in `src/core/controllers/container.py` using a single-point-of-truth `ServiceContainer`.

## ADR-003: SHA-256 Tamper-Evident Hashing for Evidence Reports
- **Status**: Approved & Implemented
- **Context**: Incident reports and timeline entries must be legally verifiable and tamper-evident.
- **Decision**: Embed SHA-256 digest computation into `IncidentEvent` and `IncidentReportModel`.

## ADR-004: Multi-Provider Notification Abstraction Layer
- **Status**: Approved & Implemented
- **Context**: Telegram was previously the single hardcoded notification channel.
- **Decision**: Implement `INotificationProvider` interface and `NotificationService` manager with priority routing and backoff retries.

## ADR-005: Permanent DPAPI-Backed Device Identity
- **Status**: Approved & Implemented
- **Context**: Installations require permanent identity surviving reboots without cloud dependency.
- **Decision**: Generate hardware-bound UUID, RSA key pair, public fingerprint, and save via DPAPI storage.
