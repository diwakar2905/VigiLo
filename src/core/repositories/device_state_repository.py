import os
import json
from datetime import datetime
from typing import Optional
from ..models.device_state import DeviceState, DeviceStateModel

class DeviceStateRepository:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    def load_state(self) -> DeviceStateModel:
        if not os.path.exists(self.storage_path):
            default = DeviceStateModel(
                state=DeviceState.WATCH_MODE,
                updated_at=datetime.utcnow().isoformat(),
                updated_by="SYSTEM_INIT",
                transition_reason="Initial default state"
            )
            self.save_state(default)
            return default

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return DeviceStateModel(
                    state=DeviceState(data.get("state", "WATCH_MODE")),
                    updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
                    updated_by=data.get("updated_by", "UNKNOWN"),
                    transition_reason=data.get("transition_reason", "")
                )
        except Exception as e:
            return DeviceStateModel(
                state=DeviceState.WATCH_MODE,
                updated_at=datetime.utcnow().isoformat(),
                updated_by="ERROR_RECOVERY",
                transition_reason=f"Failed to read state file ({e})"
            )

    def save_state(self, model: DeviceStateModel) -> bool:
        try:
            payload = {
                "state": model.state.value,
                "updated_at": model.updated_at,
                "updated_by": model.updated_by,
                "transition_reason": model.transition_reason
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save device state: {e}")
            return False
