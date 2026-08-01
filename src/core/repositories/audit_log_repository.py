import os
import json
from datetime import datetime
from typing import Dict, Any

class AuditLogRepository:
    def __init__(self, log_filepath: str):
        self.log_filepath = log_filepath
        os.makedirs(os.path.dirname(self.log_filepath), exist_ok=True)

    def write_entry(self, category: str, action: str, actor: str, details: Dict[str, Any]) -> bool:
        try:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "category": category,
                "action": action,
                "actor": actor,
                "details": details
            }
            with open(self.log_filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            return True
        except Exception as e:
            print(f"[ERROR] Audit log write failed: {e}")
            return False
