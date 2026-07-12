# PART VI — Open Source & Repository

---

## Chapter 24 — Repository Structure

### 1. Repository Layout Conventions
The repository uses the following package structure:
*   `api/`: External platform integrations (Telegram).
*   `config/`: Configuration validation, serialization, and backup services.
*   `core/`: Lifecycle management and thread orchestration.
*   `security/`: DPAPI wrapper, policy engine, and audit logger.
*   `services/`: Background tasks and polling command servers.
*   `setup/`: Compilation scripts and setup wizards.

---

## Chapter 25 — Contribution Guide

### 1. Code Review Requirements
Before a pull request can be merged, it must meet the following criteria:
*   **Approval**: Requires approval from at least one core maintainer.
*   **Linting**: Must pass Black and Ruff formatting checks.
*   **Testing**: All unit tests must pass, and code coverage must remain above 80%.

---

## Chapter 26 — Issue & PR Templates

Standard markdown templates are provided in the repository to structure bug reports, feature requests, and pull request details.

---

## Chapter 27 — Architectural Decision Records (ADR)

### ADR-001: DPAPI Encryption for Configuration Secrets
*   **Status**: Accepted.
*   **Context**: Plaintext API tokens in configuration files pose a security risk.
*   **Decision**: Encrypt all secrets stored in `config.json` using Windows DPAPI, ensuring decryption is restricted to the active logon session.

### ADR-002: Thread Watchdog Recovery Logic
*   **Status**: Accepted.
*   **Context**: Unsupervised background threads can crash silently, leaving the system in an unmonitored state.
*   **Decision**: Implement a Thread Supervisor watchdog that monitors service heartbeats and restarts failed services with an exponential backoff.
