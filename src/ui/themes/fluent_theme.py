from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class FluentColorPalette:
    name: str
    bg_canvas: str
    bg_card: str
    bg_card_hover: str
    fg_primary: str
    fg_secondary: str
    fg_muted: str
    accent_blue: str
    accent_green: str
    accent_warning: str
    accent_critical: str
    border_subtle: str
    badge_protected_bg: str
    badge_protected_fg: str

class FluentThemeManager:
    PALETTES = {
        "dark": FluentColorPalette(
            name="dark",
            bg_canvas="#0f172a",
            bg_card="#1e293b",
            bg_card_hover="#334155",
            fg_primary="#f8fafc",
            fg_secondary="#cbd5e1",
            fg_muted="#64748b",
            accent_blue="#0284c7",
            accent_green="#10b981",
            accent_warning="#f59e0b",
            accent_critical="#ef4444",
            border_subtle="#334155",
            badge_protected_bg="rgba(16, 185, 129, 0.15)",
            badge_protected_fg="#10b981"
        ),
        "light": FluentColorPalette(
            name="light",
            bg_canvas="#f8fafc",
            bg_card="#ffffff",
            bg_card_hover="#f1f5f9",
            fg_primary="#0f172a",
            fg_secondary="#334155",
            fg_muted="#94a3b8",
            accent_blue="#0284c7",
            accent_green="#059669",
            accent_warning="#d97706",
            accent_critical="#dc2626",
            border_subtle="#e2e8f0",
            badge_protected_bg="#d1fae5",
            badge_protected_fg="#059669"
        ),
        "high_contrast": FluentColorPalette(
            name="high_contrast",
            bg_canvas="#000000",
            bg_card="#000000",
            bg_card_hover="#1a1a1a",
            fg_primary="#ffffff",
            fg_secondary="#ffffff",
            fg_muted="#ffff00",
            accent_blue="#00ffff",
            accent_green="#00ff00",
            accent_warning="#ffff00",
            accent_critical="#ff0000",
            border_subtle="#ffffff",
            badge_protected_bg="#000000",
            badge_protected_fg="#00ff00"
        )
    }

    def __init__(self, theme_name: str = "dark"):
        self.theme_name = theme_name

    def get_palette(self) -> FluentColorPalette:
        return self.PALETTES.get(self.theme_name, self.PALETTES["dark"])
