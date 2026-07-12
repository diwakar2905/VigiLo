# PART II — Architecture & Core Platforms

---

## Chapter 4 — System Architecture Overview

### 1. High-Level Architecture Topology
VigiLo is built as a highly decoupled, service-oriented system containing three distinct layers:
1.  **Orchestration Layer**: Manages service dependency trees, lifecycles, and failure recovery policies.
2.  **Telemetry Layer**: Monitors Event Logs and queues captured images offline.
3.  **Command & Control (C2) Layer**: Polles and processes incoming remote actions.

```
       +---------------------------------------------+
       |               VigiLo Engine                 |
       +---------------------+-----------------------+
                             |
         +-------------------+-------------------+
         |                                       |
         v                                       v
+--------+--------+                     +--------+--------+
| ServiceManager  |                     |  Security Core  |
| - EventMonitor  |                     | - SecretManager |
| - UploadQueue   |                     | - PolicyEngine  |
+-----------------+                     +-----------------+
```

---

## Chapter 5 — Configuration Platform

### 1. Problem Statement
Writing to a configuration file directly is prone to corruption if the system loses power or crashes mid-write. Manually editing settings can also lead to invalid values or missing parameters.

### 2. Architecture & Design Decisions
*   **Atomic Save**: Writes data to a temporary file in the same directory, flushes disk buffers using `os.fsync`, and then replaces the target configuration file atomically using `os.replace`.
*   **Integrity Manifests**: A `.meta` file next to `config.json` stores the SHA-256 hash of the valid configuration.
*   **Rolling Backups**: Keeps a rolling history of the last 5 valid configurations. If the primary configuration file is corrupted, the system automatically restores the latest valid backup.

```
[Write Config Request] ──> [Create Backup] ──> [Atomic Save to Temp] ──> [os.replace] ──> [Update SHA256 Meta]
```

---

## Chapter 6 — Security Platform

### 1. Authentication & Authorization
Authentication validates the caller identity (checking the Telegram sender's chat ID). Authorization checks the requested action against a declarative `PermissionMatrix` (e.g. webcam capture requires administrator or system context).

### 2. Sandbox Policy Engine
The policy engine prevents directory traversal attacks by validating target directories against a designated sandbox path using `os.path.realpath`.

```
[Inbound Remote Action] ──> [Check Matrix Permissions] ──> [Sanitize Target Paths] ──> [Audit Log JSON Event]
```

---

## Chapter 7 — Runtime Platform

### 1. Resilient Service Orchestrator
The runtime host replaces daemon threads with cooperatively managed threads (`ManagedThread`) that support cancellation events and clean joins on shutdown.

### 2. SRE Thread Watchdog
*   **Heartbeats**: Registered services write periodic heartbeat ticks.
*   **Exponential Backoff**: If a service misses its heartbeat, the Thread Supervisor attempts restarts with progressive backoff delays (1s -> 2s -> 5s -> 10s -> 30s) before escalating to a critical `FAILED` state.
