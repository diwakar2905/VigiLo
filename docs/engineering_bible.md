# VigiLo Engineering Bible & Phase 5 Architecture Specifications

## 1. Clean Architecture & Scoping Rules

VigiLo enforces a strict **Controller -> Service -> Repository -> Model -> UI** pattern.

```
UI Layer (Desktop Dashboard / Guided Recovery Wizard / Telegram Command Center)
       │
       ▼
Controller Layer (DeviceStateController, IdentityController, PairingController, AuthController)
       │
       ▼
Service Layer (DeviceStateService, IdentityService, PermissionEngine, SecurityPolicyService, NotificationService)
       │
       ▼
Repository Layer (DeviceStateRepository, TimelineRepository, IdentityRepository, AuditLogRepository)
       │
       ▼
Models (DeviceStateModel, DeviceIdentityModel, IncidentEvent, CorrelationContext, HealthObject)
```

### Architectural Principles & SOLID Compliance
1. **Single Responsibility Principle (SRP)**: Each service handles exactly one responsibility (`DeviceIdentityService` handles cryptographic identity, `NotificationService` handles multi-provider routing).
2. **Open/Closed Principle (OCP)**: New notification providers (Email, Discord, Push) implement `INotificationProvider` without modifying `NotificationService`.
3. **Liskov Substitution Principle (LSP)**: All services implement `IService` (`initialize()`, `shutdown()`).
4. **Interface Segregation Principle (ISP)**: Focused, lightweight interfaces (`INotificationProvider`, `IService`).
5. **Dependency Inversion Principle (DIP)**: Controllers and high-level modules depend on service abstractions via single-point-of-truth `ServiceContainer`.

---

## 2. Phase 5 Platform Hardening Modules

### 2.1 Notification Abstraction Layer
- `INotificationProvider` interface with `priority`, `send()`, and `check_health()`.
- Priority-based dispatch with exponential backoff retries (0.5s * 1.5 factor).
- Multi-provider fallback (Telegram -> Webhook -> Secondary).

### 2.2 Device Identity Platform
- Generates machine UUID, public ID (`VIGI-xxxx`), fingerprint (SHA-256), and RSA keypair.
- Persisted locally using Windows DPAPI obfuscated storage (`identity.dat`). Private keys are never exposed in unencrypted form.

### 2.3 Command Authorization & Replay Protection
- Every request validates timestamp skew (<60s) and nonce uniqueness.
- Rate-limited to max 30 requests per minute per user context.
- Propagates unified `CorrelationContext` (`correlation_id`, `trace_id`, `audit_id`, `incident_id`, `log_id`).

### 2.4 Tamper Detection Engine
- Inspects binary files (`monitor.py`, `commander.py`, `dashboard_app.py`), Windows Registry keys, and Windows Task Scheduler tasks (`AntiTheft_Commander`).
- Anomaly pipeline: Audit Log -> Timeline Record -> Incident Alert.
