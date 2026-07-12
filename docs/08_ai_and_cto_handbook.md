# PART VIII — AI Rules & CTO Handbook

---

## Chapter 31 — AI Development Rules

### 1. AI Assistant Constraints
AI assistants modifying the VigiLo codebase must follow these rules:
*   **No Placeholders**: Do not write comments like `# TODO: implement this`. All code modifications must be fully functional.
*   **No API Changes**: Public APIs must remain backward compatible unless explicitly approved in an ADR.
*   **Type Hinting**: All new functions and variables must be fully type-annotated.

---

## Chapter 32 — Antigravity Engineering Prompts

We provide standard system prompts in the repository to guide code creation, review, and testing tasks.

---

## Chapter 33 — CTO Decisions Register

### 1. Architectural Decisions
*   **DPAPI Encryption**: Secrets (such as Telegram API tokens) must be encrypted using Windows DPAPI to prevent unauthorized access at rest.
*   **Atomic Configuration Updates**: Settings updates must be written atomically to a temporary file before replacing the target file, avoiding file corruption.
*   **Thread Watchdog**: Background services must run under a thread supervisor watchdog that restarts failed services using exponential backoff logic.

---

## Chapter 34 — Core SRE Principles

VigiLo services must be monitored to ensure system stability:
*   **Uptime**: Track service run times.
*   **Error Rate**: Monitor exception rates within loop executions.
*   **Heartbeat Checks**: Ensure background threads tick periodically, indicating they are alive.

---

## Chapter 35 — PR Approval Checklists

Every pull request must pass the following checks:
1.  All unit and integration tests must run successfully.
2.  Code coverage must remain above 80%.
3.  No secrets or plaintext credentials may be checked in.
4.  Ruff and Black linting checks must pass without errors.

---

## Chapter 36 — Pre-Release Verification

Before tagging a release, developers must:
1.  Verify the installer builds and registers the Windows service correctly.
2.  Check that configuration migrations load legacy schemas successfully.
3.  Confirm that DPAPI encryption and decryption loops function as expected.

---

## Chapter 37 — Multi-Year Future Roadmap

*   **V1 (Core)**: Resilient runtime orchestrator and local DPAPI configuration encryption (Complete).
*   **V2 (Dashboard)**: Native Windows desktop dashboard interface.
*   **V3 (Enterprise)**: Centralized cloud policy engine and kernel-level tamper protection driver.
