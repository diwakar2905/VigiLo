# config/schema.py


class ImmutableConfigMixin:
    """Provides read-only snapshot enforcement to configuration schema structures."""

    _readonly = False

    def __setattr__(self, name, value):
        if getattr(self, "_readonly", False) and name != "_readonly":
            raise AttributeError(
                "This configuration snapshot is read-only. Modifying configuration must go through ConfigManager.save()."
            )
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
        return {"bot_token": self.bot_token, "chat_id": self.chat_id}


class SecurityConfig(ImmutableConfigMixin):
    def __init__(
        self, failed_attempt_threshold=2, event_id=4625, check_interval_seconds=0.1
    ):
        self.failed_attempt_threshold = int(failed_attempt_threshold)
        self.event_id = int(event_id)
        self.check_interval_seconds = float(check_interval_seconds)

    def to_dict(self):
        return {
            "failed_attempt_threshold": self.failed_attempt_threshold,
            "event_id": self.event_id,
            "check_interval_seconds": self.check_interval_seconds,
        }


class CameraConfig(ImmutableConfigMixin):
    def __init__(self, device_index=0):
        self.device_index = int(device_index)

    def to_dict(self):
        return {"device_index": self.device_index}


class FaceVerificationConfig(ImmutableConfigMixin):
    def __init__(self, enabled=False, threshold=0.363, reference_embeddings=None):
        self.enabled = bool(enabled)
        self.threshold = float(threshold)
        self.reference_embeddings = reference_embeddings if reference_embeddings else []

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "threshold": self.threshold,
            "reference_embeddings": self.reference_embeddings,
        }


class VaultConfig(ImmutableConfigMixin):
    def __init__(self, enabled=True, target_dir="C:\\VigiLoVault", vault_key=""):
        self.enabled = bool(enabled)
        self.target_dir = str(target_dir).strip()
        self.vault_key = str(vault_key).strip()

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "target_dir": self.target_dir,
            "vault_key": self.vault_key,
        }


class WhatsAppConfig(ImmutableConfigMixin):
    def __init__(
        self,
        enabled=False,
        phone_number_id="",
        access_token="",
        recipient_phone="",
    ):
        self.enabled = bool(enabled)
        self.phone_number_id = str(phone_number_id).strip()
        self.access_token = str(access_token).strip()
        self.recipient_phone = str(recipient_phone).strip()

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "phone_number_id": self.phone_number_id,
            "access_token": self.access_token,
            "recipient_phone": self.recipient_phone,
        }


class AppConfig(ImmutableConfigMixin):
    def __init__(
        self,
        telegram=None,
        security=None,
        camera=None,
        face_verification=None,
        vault=None,
        whatsapp=None,
    ):
        self.telegram = telegram if telegram else TelegramConfig()
        self.security = security if security else SecurityConfig()
        self.camera = camera if camera else CameraConfig()
        self.face_verification = (
            face_verification if face_verification else FaceVerificationConfig()
        )
        self.vault = vault if vault else VaultConfig()
        self.whatsapp = whatsapp if whatsapp else WhatsAppConfig()

    def to_dict(self):
        return {
            "telegram": self.telegram.to_dict(),
            "security": self.security.to_dict(),
            "camera": self.camera.to_dict(),
            "face_verification": self.face_verification.to_dict(),
            "vault": self.vault.to_dict(),
            "whatsapp": self.whatsapp.to_dict(),
        }
