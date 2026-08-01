# VigiLo Commercial Deployment Guide

## 1. Multi-Stage Production Installer

Deploy VigiLo across Windows endpoints using the multi-stage production installer:

```cmd
VigiLo_Production_Installer.exe /quiet /paired_chat_id=123456789
```

### Installer Validation Probes
The installer executes 12 automated pre-flight probes before extraction:
1. Welcome & License Agreement
2. System Compatibility Check
3. Administrator Validation Probe
4. Windows Version & Build Check
5. Camera Hardware Probe
6. Security Event Log Hook Check
7. Telegram Notification Pairing
8. Configuration Validation
9. Binary & Service Installation
10. Runtime Verification Probe
11. Push Health Check Verification
12. Installation Complete & Success

---

## 2. Silent & Unattended Deployment

For enterprise silent rollout via Intune or Group Policy (GPO):
```powershell
Start-Process -FilePath "VigiLo_Production_Installer.exe" -ArgumentList "/silent" -Wait
```
