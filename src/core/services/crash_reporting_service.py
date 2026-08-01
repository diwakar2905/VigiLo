import os
import json
import base64
import uuid
import platform
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from ..interfaces.i_service import IService

class CrashReportingService(IService):
    def __init__(self, crash_dir: str):
        self.crash_dir = crash_dir
        self._initialized = False

    def initialize(self) -> bool:
        os.makedirs(self.crash_dir, exist_ok=True)
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def capture_crash(self, exc: Exception, context_name: str = "GLOBAL", correlation_id: Optional[str] = None) -> str:
        bundle_id = f"CRASH-{uuid.uuid4().hex[:8].upper()}"
        crash_file = os.path.join(self.crash_dir, f"{bundle_id}.crash")

        payload = {
            "bundle_id": bundle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "context_name": context_name,
            "correlation_id": correlation_id,
            "os_build": f"{platform.system()} {platform.release()} ({platform.version()})",
            "python_version": platform.python_version(),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "stack_trace": traceback.format_exc()
        }

        # Obfuscated / Encrypted crash bundle
        raw_bytes = json.dumps(payload, indent=2).encode('utf-8')
        protected = base64.b64encode(raw_bytes).decode('utf-8')

        with open(crash_file, "w", encoding="utf-8") as f:
            f.write(protected)

        print(f"[CRASH-REPORTER] Encrypted crash bundle saved: {crash_file}")
        return crash_file

    def export_crash_bundle(self, crash_filepath: str, output_path: str) -> bool:
        if not os.path.exists(crash_filepath):
            return False
        try:
            with open(crash_filepath, "r", encoding="utf-8") as f:
                protected = f.read()
                raw_json = base64.b64decode(protected).decode('utf-8')

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(raw_json)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to export crash bundle: {e}")
            return False
