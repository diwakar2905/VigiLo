# VigiLo Troubleshooting & Crash Diagnostics Guide

## 1. Running Automated Self-Diagnostics

To diagnose component failures, run the self-diagnostics suite via Telegram or Desktop UI:

```
Telegram: /diagnose
Desktop UI: Health Tab -> Run Full Self-Diagnostics
```

Probes checked:
- Windows Administrator privileges
- Disk space availability (C:)
- Notification Provider responsiveness
- Windows Security Event Log API accessibility

---

## 2. Crash Reporting & Encrypted Crash Bundles

If an unhandled exception occurs, `CrashReportingService` generates an encrypted crash bundle in `C:\ProgramData\VigiLo\crashes\`:

```
CRASH-XXXXXX.crash
```

### Exporting Crash Bundles
Users can manually export encrypted crash bundles for support review:
```python
container.crash_reporter.export_crash_bundle("C:\\ProgramData\\VigiLo\\crashes\\CRASH-1234.crash", "crash_report.json")
```
**Privacy Assurance**: Crash bundles are NEVER automatically uploaded over the network.
