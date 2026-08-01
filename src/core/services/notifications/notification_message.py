from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class NotificationMessage:
    title: str
    body: str
    severity: str = "INFO"  # INFO, WARNING, CRITICAL
    attachment_path: Optional[str] = None
    priority: int = 1  # 1 = Highest, 10 = Lowest
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
