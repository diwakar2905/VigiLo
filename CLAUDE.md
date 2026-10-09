# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

VigiLo is a local-first Windows device recovery platform (intruder detection on failed logon, webcam capture, Telegram/webhook alerts, remote lock, forensic timeline/reports). Python 3.10+ (CI uses 3.11 on `windows-latest`). It is explicitly positioned as *not* spyware/RAT: no cloud telemetry, and intrusive features are gated by device state.

## Commands

```bash
pip install -r requirements.txt
pip install pytest pytest-cov flake8

python -m pytest tests/                                   # full suite (what CI runs)
python -m pytest tests/unit/test_security_gateway.py      # one file
python -m pytest tests/unit/test_security_gateway.py::TestSecurityGateway::test_capability_registry_lookups  # one test

flake8 src/ service/ --count --select=E9,F63,F7,F82 --show-source --statistics   # CI lint (syntax/undefined names only)

python -m src.ui.dashboard_app        # Tkinter desktop Control Center
python service/monitor.py             # background monitor service (Windows only, needs pywin32)
python scripts/quality_gates.py       # release quality gate (wraps pytest)
pyinstaller --noconfirm monitor.spec  # build the service exe (also WatchDog_Setup.spec / WatchDog_Uninstall.spec)
```

Running outside Windows: `pywin32`, `pyaudio`, and the `service/` layer won't work. `tests/ui/*` and `tests/unit/test_phase7_platform.py` need `tkinter`. The remaining unit/integration/benchmark tests pass on Linux with `psutil` and `requests` installed. When `PROGRAMDATA` is unset, `ServiceContainer` creates a literal `C:\ProgramData/` directory in the cwd. Delete it, and don't commit it.

## Architecture

Two layers coexist:

1. **`service/`: legacy runtime loop** (`monitor.py`, `commander.py`, `camera.py`, `uploader.py`). `monitor.py` polls the Windows Security event log for Event ID 4625 (failed logon), captures a webcam photo, and sends it via Telegram. `commander.py` polls Telegram for remote commands (lock, screenshot, location, audio, etc.). It reads root `config.json` (bot token, chat id, thresholds), or the config next to the exe when frozen. These modules import `src.core` *optionally* (wrapped in try/except), so the service must keep working even if the core container fails. Don't break that fallback.

2. **`src/`: the layered platform**, which follows **Controller → Service → Repository → Model** (plus `ui/`). Cross-layer shortcuts and circular imports are forbidden by `CONTRIBUTING.md`.
   - `src/core/controllers/container.py`: `ServiceContainer` is the singleton DI root (`ServiceContainer.get_instance(base_data_dir=None)`). It builds every repository and service in dependency order and calls `initialize()` on each. Persistent data lives under `%PROGRAMDATA%\VigiLo\` (`device_state.json`, `timeline.db` SQLite, `audit.log`, `identity.dat`, `policies.json`). Tests pass a temp `base_data_dir`. Passing a different dir replaces the singleton. **New services must be wired here.**
   - Every service implements `IService` (`src/core/interfaces/i_service.py`: `initialize()` / `shutdown()`).
   - **Device state gating**: `src/core/models/device_state.py` defines `DeviceState` (`DISARMED`, `WATCH_MODE`, `LOST_MODE`) and `FeaturePermissionMatrix`, which lists the features allowed per state. Lock, location, and screenshot are `LOST_MODE` only. New features must be registered in the matrix.
   - **Privileged operations go through `SecurityGateway`** (`src/core/security/security_gateway.py`). `execute_privileged_operation(SecurityGatewayRequest)` runs the checks in order: capability lookup in `CapabilityRegistry` → allowed-caller check → `PermissionEngineService.authorize` (state, role, and privilege) → security policy check → audit log → run the handler. A new privileged action means adding a capability to the registry and a permission to the engine's default matrix, never calling the OS directly.
   - `FeatureFlagService`: tiered flags that can be overridden with `VIGILO_FLAG_<NAME>=1` env vars.
   - `CommandAuthorizationService`: anti-replay nonces, a timestamp skew limit under 60s, and rate limiting for remote commands.
   - Notifications: implement `INotificationProvider` (`src/core/services/notifications/`) and register it with `NotificationService` in the container. Telegram and webhook providers already exist.
   - Exceptions: raise from `src/core/exceptions` (`SecurityException`, `RecoverableException`, `FatalException`, `UserException`). The project's rule is no bare `except:` or silent fallbacks in `src/` (the `service/` legacy loop is the exception, by design).
   - Use `CorrelationContext` (`src/core/models/correlation_context.py`) to propagate correlation/trace/incident IDs across layers.
   - Timeline events are stored in SQLite with SHA-256 hash chaining (tamper-evident). Reports export to PDF and JSON.
   - Extension surfaces: `src/api/v1/public_api.py` (versioned facade), `sdk/vigi_sdk.py` and `src/core/plugins/` (plugin SDK with capability sandboxing), `src/core/scripting/script_engine.py` (AST-sandboxed automation rules), and `src/core/events/event_bus.py` (pub/sub).
   - `src/ui/`: Tkinter **MVVM**. Views (`views/`) bind to ViewModels (`viewmodels/`) through `ObservableProperty`. Theming is in `ui/themes/` (dark, light, high_contrast). Strings come from `locales/*.json` through `src/core/i18n`.

`setup/` contains the installer, uninstaller, and startup registration (Windows scheduled task/service). `docs/` holds the design references: `engineering_bible.md`, `adr.md` (ADR-001…010), `threat_model.md`, and `plugin_sdk_guide.md`. Check `adr.md` before making architectural changes.

## Conventions

- Conventional commit prefixes (`feat:`, `fix:`, `docs:`, `test:`).
- Fill in `.github/PULL_REQUEST_TEMPLATE.md` for PRs.
- Privacy-first: no third-party telemetry, analytics, or cloud data paths.
