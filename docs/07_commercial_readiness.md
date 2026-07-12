# PART VII — Commercial Readiness & Dashboard

---

## Chapter 28 — Installer & Packaging

### 1. Inno Setup Packaging Wizard
The setup installer (`VigiLo_Setup.exe`) packages the application binaries and handles deployment tasks:
*   **Privilege Elevation**: Requests administrative rights during installation.
*   **Service Registration**: Installs VigiLo as a Windows service using the Service Control Manager (SCM).
*   **Task Scheduler**: Creates a scheduled task to launch VigiLo Commander automatically at user logon.

---

## Chapter 29 — Desktop UI Dashboard

### 1. User Control Panel
The desktop dashboard provides configuration and monitoring interfaces:
*   **Telemetry Monitor**: Displays CPU, memory, and service status metrics.
*   **Credential Setup**: Enables users to configure their Telegram Bot Token and Chat ID.
*   **Incident Viewer**: Shows captured images and event logs from security incidents.

---

## Chapter 30 — Enterprise Deployment Policies

### 1. Group Policy Objects (GPO)
VigiLo settings can be deployed across enterprise networks using Group Policy:
*   **Registry Injection**: Administrators can pre-configure VigiLo settings by applying registry keys under `HKLM\Software\Policies\VigiLo`.
*   **Silent Deployments**: The installer supports silent installations (`/VERYSILENT /SUPPRESSMSGBOXES`) for automated deployment tools.
