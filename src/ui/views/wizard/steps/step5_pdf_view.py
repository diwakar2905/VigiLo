import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.ui.viewmodels.recovery_wizard_viewmodel import RecoveryWizardViewModel

class Step5PdfView(ttk.Frame):
    """Step 5: Professional Forensic PDF Generator View."""

    def __init__(self, parent, vm: RecoveryWizardViewModel):
        super().__init__(parent, padding=15)
        self.vm = vm

        self._build_ui()

    def _build_ui(self):
        lbl_h = ttk.Label(self, text="Step 5: Generate Digital Forensic PDF Report", font=("Segoe UI", 12, "bold"))
        lbl_h.pack(anchor="w", pady=(0, 10))

        lbl_desc = ttk.Label(self, text="Compile a legally admissible forensic PDF report containing incident summary, device identity, captured evidence, and digital integrity hashes.", font=("Segoe UI", 10), wraplength=550)
        lbl_desc.pack(anchor="w", pady=(0, 15))

        btn_gen = ttk.Button(self, text="📄 Save Forensic PDF Report", command=self._handle_save_pdf)
        btn_gen.pack(anchor="w", pady=10)

        self.lbl_result = ttk.Label(self, text="Status: PDF Report Ready to Generate", font=("Segoe UI", 9, "italic"))
        self.lbl_result.pack(anchor="w", pady=5)

    def _handle_save_pdf(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")],
            title="Save Forensic Report PDF"
        )
        if path:
            success = self.vm.generate_pdf_report(path)
            if success:
                self.lbl_result.config(text=f"✅ Forensic Report Saved: {path}", foreground="#10b981")
                messagebox.showinfo("Forensic PDF Generated", f"Forensic report saved successfully to:\n{path}")
            else:
                self.lbl_result.config(text="❌ Failed to generate PDF report.", foreground="#ef4444")
