# PART III — Windows Integration & Event Bus Platforms

---

## Chapter 8 — Windows Platform Integration

### 1. Session 0 Isolation
Windows Services run in **Session 0**, which is isolated from the interactive user desktop shell. Because Session 0 processes cannot interact directly with the user GUI or capture camera/screen data on certain hardware drivers, VigiLo uses a multi-session architecture:
*   **VigiLo Service (Session 0)**: Runs as SYSTEM, monitoring the event log and managing the upload queue.
*   **VigiLo Commander (User Session)**: Runs in the active user's session context, handling Telegram polling and desktop captures.

### 2. Single-Instance Named Mutexes
To prevent duplicate background instances from running simultaneously, VigiLo creates named mutexes on startup:
*   **Service Mutex**: `Global\\VigiLoServiceMutex` (SYSTEM context)
*   **Commander Mutex**: `Local\\VigiLoCommanderMutex` (User session context)

---

## Chapter 9 — Event Bus Architecture

### 1. Internal Pub-Sub Broker
The `EventPublisher` serves as the central message bus. Services publish lifecycle events (such as `ServiceStarted` or `HeartbeatLost`) to the broker, which forwards them to registered subscriber callbacks.

```
[Service Trigger] ──> [Publish Event + Correlation ID] ──> [EventPublisher] ──> [Subscriber Callbacks]
```

---

## Chapter 10 — Logging Platform

### 1. Logging Configurations
Logs are split into separate rotation-managed streams:
*   **Runtime Logs (`logs/vigilo.log`)**: General execution steps.
*   **Security Audit Logs (`logs/audit.log`)**: Structured JSON objects recording access evaluations and permission decisions.

---

## Chapter 11 — Metrics Platform

### 1. Telemetry Capture
The `ServiceManager` monitors system resource usage via `psutil`:
*   **Memory**: Process resident set size (RSS).
*   **CPU**: Processor usage percentage.
*   **Service Metrics**: Track restarts, heartbeats, and error counts.

---

## Chapter 12 — Recovery Platform

### 1. Self-Healing Sequence
If the Thread Supervisor detects a service crash or missed heartbeat:
1.  **Halt**: Suspends active work loops.
2.  **Backoff Delay**: Waits according to the restart delay ladder.
3.  **Restore Check**: Verifies configurations against their checksums, restoring from backups if necessary.
4.  **Restart**: Attempts to restart the service cleanly.
