import json
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ThemeTokenBundle:
    theme_name: str
    bg_primary: str
    bg_secondary: str
    fg_primary: str
    fg_secondary: str
    accent_color: str
    badge_bg: str
    border_color: str

class ThemeManager:
    BUILTIN_THEMES = {
        "dark": ThemeTokenBundle(
            theme_name="dark",
            bg_primary="#0f172a",
            bg_secondary="#1e293b",
            fg_primary="#f8fafc",
            fg_secondary="#94a3b8",
            accent_color="#0284c7",
            badge_bg="rgba(56, 189, 248, 0.1)",
            border_color="#334155"
        ),
        "light": ThemeTokenBundle(
            theme_name="light",
            bg_primary="#ffffff",
            bg_secondary="#f1f5f9",
            fg_primary="#0f172a",
            fg_secondary="#475569",
            accent_color="#0284c7",
            badge_bg="#e0f2fe",
            border_color="#cbd5e1"
        ),
        "high_contrast": ThemeTokenBundle(
            theme_name="high_contrast",
            bg_primary="#000000",
            bg_secondary="#000000",
            fg_primary="#ffffff",
            fg_secondary="#ffff00",
            accent_color="#00ffff",
            badge_bg="#000000",
            border_color="#ffffff"
        )
    }

    def __init__(self, current_theme: str = "dark"):
        self.current_theme_name = current_theme

    def get_current_theme(self) -> ThemeTokenBundle:
        return self.BUILTIN_THEMES.get(self.current_theme_name, self.BUILTIN_THEMES["dark"])

    def set_theme(self, theme_name: str) -> bool:
        if theme_name in self.BUILTIN_THEMES:
            self.current_theme_name = theme_name
            return True
        return False
