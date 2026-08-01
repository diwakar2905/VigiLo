import tkinter as tk
from tkinter import ttk
from ...core.controllers.container import ServiceContainer

class AboutView(ttk.Frame):
    def __init__(self, parent, container: ServiceContainer):
        super().__init__(parent)
        self.container = container
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.LabelFrame(self, text=" About VigiLo Device Recovery Platform ", padding=20)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        lbl_title = ttk.Label(main_frame, text="VigiLo Platform v3.5 (Commercial Edition)", font=("Segoe UI", 14, "bold"))
        lbl_title.pack(anchor="w", pady=(0, 10))

        desc = (
            "VigiLo is a commercial-grade, privacy-first Windows Device Recovery Platform.\n\n"
            "Core Guarantees:\n"
            "• 100% Local-First Architecture: Zero third-party cloud analytics or remote tracking servers.\n"
            "• Transparent Permission Explainer: Full transparency on OS hardware & API access.\n"
            "• Cryptographic Integrity: SHA-256 hashes on all evidence logs and incident reports.\n"
            "• Formal Device State Machine: Clear scoping between DISARMED, WATCH MODE, and LOST MODE.\n"
            "• Open-Source & Audit Ready: Designed to build user trust without spyware or hidden processes."
        )
        lbl_desc = ttk.Label(main_frame, text=desc, font=("Segoe UI", 10), justify="left", wraplength=600)
        lbl_desc.pack(anchor="w", pady=10)

        # Trust Service Explainer Summary
        trust_frame = ttk.LabelFrame(main_frame, text=" Trust & Privacy Justifications ", padding=10)
        trust_frame.pack(fill="x", expand=True, pady=10)

        perms = self.container.trust_service.get_permission_descriptors()
        for p in perms:
            status_text = "✅ Granted" if p.is_granted else "⚠️ Action Required"
            lbl = ttk.Label(trust_frame, text=f"• {p.name} [{status_text}]: {p.justification}", font=("Segoe UI", 9), wraplength=550)
            lbl.pack(anchor="w", pady=2)
