# VigiLo Migration & Version Upgrade Guide

## 1. Upgrading to VigiLo Platform v3.5.0

VigiLo v3.5.0 introduces **Phase 5 Platform Hardening**, including DPAPI identity storage, security policy engines, multi-provider notifications, and schema migration tracking.

### Automatic Migration Engine
`ReleaseHardeningService` automatically verifies schema compatibility on startup:
1. Inspects existing `config.json` version tag.
2. Migrates schema from `v3.0.0` -> `v3.5.0`.
3. Injects default security policy configurations into `C:\ProgramData\VigiLo\policies.json`.
4. Auto-generates permanent identity credentials in `C:\ProgramData\VigiLo\identity.dat`.

### Manual Upgrade Commands
```bash
git pull origin main
pip install -r requirements.txt
python -m pytest tests/
```
