from typing import Dict, Any, List
from ..interfaces.i_service import IService
from ..exceptions.vigi_exceptions import SecurityException

class TelemetryService(IService):
    def __init__(self, opt_in: bool = False):
        self._opt_in = opt_in
        self._telemetry_buffer: List[Dict[str, Any]] = []
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._telemetry_buffer.clear()
        self._initialized = False

    def is_opted_in(self) -> bool:
        return self._opt_in

    def set_opt_in(self, enabled: bool) -> None:
        self._opt_in = enabled
        if not enabled:
            self._telemetry_buffer.clear()

    def record_anonymous_stat(self, metric_name: str, value: Any) -> bool:
        if not self._opt_in:
            return False  # Privacy First: Default OFF

        # Strict PII & Sensitive Keyword Filter
        forbidden_keywords = ["command", "photo", "image", "screenshot", "password", "token", "file", "user", "name", "email", "chat_id"]
        if any(k in metric_name.lower() for k in forbidden_keywords):
            raise SecurityException(f"Privacy Policy Enforcement: Telemetry metric '{metric_name}' contains sensitive keyword.")

        entry = {
            "metric": metric_name,
            "value": value
        }
        self._telemetry_buffer.append(entry)
        return True

    def get_buffered_telemetry(self) -> List[Dict[str, Any]]:
        if not self._opt_in:
            return []
        return list(self._telemetry_buffer)
