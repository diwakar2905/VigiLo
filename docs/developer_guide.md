# VigiLo Developer Guide & Service Creation Protocol

## 1. Creating a New Notification Provider

To add a new notification provider (e.g. Email, Discord, Signal):

1. Implement `INotificationProvider`:
   ```python
   from src.core.services.notifications import INotificationProvider, NotificationMessage
   from src.core.models.health_object import HealthObject, HealthStatus

   class EmailNotificationProvider(INotificationProvider):
       @property
       def provider_id(self) -> str:
           return "email"

       @property
       def priority(self) -> int:
           return 3  # Priority level

       def send(self, message: NotificationMessage) -> bool:
           # Implementation
           return True

       def check_health(self) -> HealthObject:
           return HealthObject("Provider:Email", HealthStatus.HEALTHY, "SMTP Ready", "2026-08-01T00:00:00")
   ```

2. Register provider in `ServiceContainer`:
   ```python
   self.notification_service.register_provider(EmailNotificationProvider(...))
   ```

---

## 2. Using the Centralized Exception Framework

Never write bare `except:` or silent fallbacks. Raise structured exceptions:

```python
from src.core.exceptions import SecurityException, RecoverableException, UserException

# Security violation
raise SecurityException("Unauthorized API access attempt")

# Transient network failure
raise RecoverableException("Failed to reach webhook endpoint")
```

---

## 3. Correlation Context Propagation

Attach `CorrelationContext` when logging or dispatching events:

```python
from src.core.models import CorrelationContext

ctx = CorrelationContext.create_new()
print(f"Executing operation with correlation_id: {ctx.correlation_id}")
```
