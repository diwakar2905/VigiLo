# api/notification_interface.py
"""Abstract base class for notification channels."""

from __future__ import annotations
from abc import ABC, abstractmethod


class NotificationInterface(ABC):
    """Abstract interface defining the contract for notification clients."""

    @abstractmethod
    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Sends a text message."""
        pass

    @abstractmethod
    def send_photo(self, image_path: str, caption: str | None = None) -> bool:
        """Sends a photo/image file."""
        pass

    @abstractmethod
    def send_audio(self, audio_path: str, caption: str | None = None) -> bool:
        """Sends an audio file."""
        pass

    @abstractmethod
    def send_document(self, doc_path: str, caption: str | None = None) -> bool:
        """Sends a document/file."""
        pass
