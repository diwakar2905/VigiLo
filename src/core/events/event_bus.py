import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable
from src.core.interfaces.i_service import IService

@dataclass
class VigiLoEvent:
    event_type: str
    data: Dict[str, Any]
    event_id: str = field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:8].upper()}")
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class EventBus(IService):
    def __init__(self):
        self._subscribers: Dict[str, Dict[str, Callable[[VigiLoEvent], None]]] = {}
        self._event_history: List[VigiLoEvent] = []
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._subscribers.clear()
        self._event_history.clear()
        self._initialized = False

    def subscribe(self, event_type: str, handler: Callable[[VigiLoEvent], None]) -> str:
        sub_id = f"SUB-{uuid.uuid4().hex[:8].upper()}"
        if event_type not in self._subscribers:
            self._subscribers[event_type] = {}
        self._subscribers[event_type][sub_id] = handler
        return sub_id

    def unsubscribe(self, event_type: str, sub_id: str) -> bool:
        if event_type in self._subscribers and sub_id in self._subscribers[event_type]:
            del self._subscribers[event_type][sub_id]
            return True
        return False

    def publish(self, event: VigiLoEvent) -> int:
        self._event_history.append(event)
        if len(self._event_history) > 1000:
            self._event_history = self._event_history[-500:]

        handlers = list(self._subscribers.get(event.event_type, {}).values())
        # Also notify wildcard "*" subscribers
        handlers.extend(list(self._subscribers.get("*", {}).values()))

        delivered_count = 0
        for handler in handlers:
            try:
                handler(event)
                delivered_count += 1
            except Exception as e:
                print(f"[ERROR] EventBus handler exception on '{event.event_type}': {e}")
        return delivered_count

    def get_recent_events(self, limit: int = 50) -> List[VigiLoEvent]:
        return list(self._event_history[-limit:])
