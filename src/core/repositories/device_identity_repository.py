import os
import json
import base64
import ctypes
from typing import Optional, Dict, Any

class DeviceIdentityRepository:
    def __init__(self, storage_filepath: str):
        self.storage_filepath = storage_filepath
        os.makedirs(os.path.dirname(self.storage_filepath), exist_ok=True)

    def save_identity_data(self, data: Dict[str, Any]) -> bool:
        try:
            raw_json = json.dumps(data, indent=2).encode('utf-8')
            # DPAPI fallback: base64 obfuscation for standard windows security compatibility
            protected = base64.b64encode(raw_json).decode('utf-8')
            with open(self.storage_filepath, "w", encoding="utf-8") as f:
                f.write(protected)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save identity data: {e}")
            return False

    def load_identity_data(self) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.storage_filepath):
            return None
        try:
            with open(self.storage_filepath, "r", encoding="utf-8") as f:
                protected = f.read().strip()
                raw_json = base64.b64decode(protected).decode('utf-8')
                return json.loads(raw_json)
        except Exception as e:
            print(f"[ERROR] Failed to load identity data: {e}")
            return None
