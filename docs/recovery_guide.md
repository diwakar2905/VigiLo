# VigiLo Guided Device Recovery & Self-Healing Guide

## 1. Guided Device Recovery Flow

When a laptop is reported lost or stolen:

1. Launch **Recovery Wizard** from Desktop UI or send `/lost` in Telegram.
2. Step 1: Transition device state to `LOST_MODE`.
3. Step 2: Trigger immediate workstation lock (`LockWorkstation`).
4. Step 3: Gather evidence snapshot (Webcam capture + Geo/WiFi triangulation + Silent Desktop Screenshot).
5. Step 4: Compile SHA-256 tamper-evident PDF Forensic Report.
6. Step 5: Export report for law enforcement.

---

## 2. Self-Healing Engine Protocol

`SelfHealingService` runs background watchdog checks every 60 seconds:
- **Corrupted Config**: Auto-restores last known good `config.json` backup.
- **Stopped Services**: Auto-restarts background monitor task.
- **Missing Files**: Logs critical tamper event and triggers owner alert.
