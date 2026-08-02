import os
import json
from typing import Dict
from src.core.interfaces.i_service import IService

class I18nService(IService):
    def __init__(self, locales_dir: str, default_locale: str = "en"):
        self.locales_dir = locales_dir
        self.current_locale = default_locale
        self._translations: Dict[str, str] = {}
        self._initialized = False

    def initialize(self) -> bool:
        self.load_locale(self.current_locale)
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._translations.clear()
        self._initialized = False

    def load_locale(self, locale_code: str) -> bool:
        locale_file = os.path.join(self.locales_dir, f"{locale_code}.json")
        if os.path.exists(locale_file):
            try:
                with open(locale_file, "r", encoding="utf-8") as f:
                    self._translations = json.load(f)
                self.current_locale = locale_code
                return True
            except Exception as e:
                print(f"[ERROR] Failed to load locale '{locale_code}': {e}")
        return False

    def translate(self, key: str, **kwargs) -> str:
        text = self._translations.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text

    def t(self, key: str, **kwargs) -> str:
        return self.translate(key, **kwargs)
