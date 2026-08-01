from datetime import datetime
from typing import Dict, List, Callable
from ..interfaces.i_service import IService
from ..models.health_object import HealthObject, HealthStatus

class HealthMonitorService(IService):
    def __init__(self):
        self._health_registry: Dict[str, HealthObject] = {}
        self._listeners: List[Callable[[HealthObject], None]] = []
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._health_registry.clear()
        self._listeners.clear()
        self._initialized = False

    def update_health(self, health_obj: HealthObject) -> None:
        self._health_registry[health_obj.component_name] = health_obj
        self._notify_subscribers(health_obj)

    def get_component_health(self, component_name: str) -> HealthObject:
        if component_name in self._health_registry:
            return self._health_registry[component_name]
        return HealthObject(
            component_name=component_name,
            status=HealthStatus.HEALTHY,
            message="Initial health state",
            last_check=datetime.utcnow().isoformat()
        )

    def get_all_health(self) -> Dict[str, HealthObject]:
        return dict(self._health_registry)

    def get_aggregate_health(self) -> HealthStatus:
        if not self._health_registry:
            return HealthStatus.HEALTHY
        
        statuses = [obj.status for obj in self._health_registry.values()]
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def subscribe(self, listener: Callable[[HealthObject], None]) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def _notify_subscribers(self, health_obj: HealthObject) -> None:
        for listener in self._listeners:
            try:
                listener(health_obj)
            except Exception as e:
                print(f"[ERROR] Health subscriber exception: {e}")
