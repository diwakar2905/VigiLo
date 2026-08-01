import time
import psutil
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List
from ..interfaces.i_service import IService

@dataclass
class MetricPoint:
    metric_name: str
    value: float
    unit: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class TelemetrySnapshot:
    cpu_percent: float
    ram_used_mb: float
    ram_total_mb: float
    queue_size: int
    failure_count: int
    restart_count: int
    active_threads: int
    heartbeat: str
    recent_metrics: List[MetricPoint] = field(default_factory=list)

class ObservabilityService(IService):
    def __init__(self):
        self._failure_count = 0
        self._restart_count = 0
        self._queue_size = 0
        self._metric_history: List[MetricPoint] = []
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._metric_history.clear()
        self._initialized = False

    def record_metric(self, name: str, value: float, unit: str = "count") -> None:
        point = MetricPoint(metric_name=name, value=value, unit=unit)
        self._metric_history.append(point)
        if len(self._metric_history) > 1000:
            self._metric_history = self._metric_history[-500:]

    def record_failure(self) -> None:
        self._failure_count += 1
        self.record_metric("service_failures", self._failure_count, "count")

    def record_restart(self) -> None:
        self._restart_count += 1
        self.record_metric("service_restarts", self._restart_count, "count")

    def set_queue_size(self, size: int) -> None:
        self._queue_size = size
        self.record_metric("queue_size", size, "items")

    def get_telemetry_snapshot(self) -> TelemetrySnapshot:
        proc = psutil.Process()
        mem_info = proc.memory_info()
        sys_mem = psutil.virtual_memory()

        return TelemetrySnapshot(
            cpu_percent=psutil.cpu_percent(interval=None),
            ram_used_mb=mem_info.rss / (1024 * 1024),
            ram_total_mb=sys_mem.total / (1024 * 1024),
            queue_size=self._queue_size,
            failure_count=self._failure_count,
            restart_count=self._restart_count,
            active_threads=proc.num_threads(),
            heartbeat=datetime.utcnow().isoformat(),
            recent_metrics=list(self._metric_history[-20:])
        )
