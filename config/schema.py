# config/schema.py

class ImmutableConfigMixin:
    """Provides read-only snapshot enforcement to configuration schema structures."""
    _readonly = False

    def __setattr__(self, name, value):
        if getattr(self, '_readonly', False) and name != '_readonly':
            raise AttributeError("This configuration snapshot is read-only. Modifying configuration must go through ConfigManager.save().")
        super().__setattr__(name, value)

    def freeze(self):
        """Recursively freezes the configuration schema object, making it read-only."""
        self._readonly = True
        for attr in self.__dict__.values():
            if isinstance(attr, ImmutableConfigMixin):
                attr.freeze()

class TelegramConfig(ImmutableConfigMixin):
    def __init__(self, bot_token="YOUR_BOT_TOKEN", chat_id="YOUR_CHAT_ID"):
        self.bot_token = str(bot_token).strip()
        self.chat_id = str(chat_id).strip()

    def to_dict(self):
        return {
            "bot_token": self.bot_token,
            "chat_id": self.chat_id
        }

class SecurityConfig(ImmutableConfigMixin):
    def __init__(self, failed_attempt_threshold=2, event_id=4625, check_interval_seconds=0.1):
        self.failed_attempt_threshold = int(failed_attempt_threshold)
        self.event_id = int(event_id)
        self.check_interval_seconds = float(check_interval_seconds)

    def to_dict(self):
        return {
            "failed_attempt_threshold": self.failed_attempt_threshold,
            "event_id": self.event_id,
            "check_interval_seconds": self.check_interval_seconds
        }

class CameraConfig(ImmutableConfigMixin):
    def __init__(self, device_index=0):
        self.device_index = int(device_index)

    def to_dict(self):
        return {
            "device_index": self.device_index
        }

class AppConfig(ImmutableConfigMixin):
    def __init__(self, telegram=None, security=None, camera=None):
        self.telegram = telegram if telegram else TelegramConfig()
        self.security = security if security else SecurityConfig()
        self.camera = camera if camera else CameraConfig()

    def to_dict(self):
        return {
            "telegram": self.telegram.to_dict(),
            "security": self.security.to_dict(),
            "camera": self.camera.to_dict()
        }
