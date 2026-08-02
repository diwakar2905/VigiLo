import tkinter as tk
from tkinter import ttk
from src.ui.viewmodels.recovery_wizard_viewmodel import RecoveryWizardViewModel
from .steps.step1_summary_view import Step1SummaryView
from .steps.step2_goals_view import Step2GoalsView
from .steps.step3_execution_view import Step3ExecutionView
from .steps.step4_evidence_view import Step4EvidenceView
from .steps.step5_pdf_view import Step5PdfView
from .steps.step6_completion_view import Step6CompletionView

class GuidedRecoveryWizardDialog(tk.Toplevel):
    """Commercial-Grade 6-Step Guided Device Recovery Wizard Dialog."""

    def __init__(self, parent, vm: RecoveryWizardViewModel = None):
        super().__init__(parent)
        self.vm = vm or RecoveryWizardViewModel()

        self.title("🛡️ VigiLo Guided Device Recovery Wizard")
        self.geometry("680x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._bind_vm()

    def _build_ui(self):
        # Header Progress Meter Bar
        header = ttk.Frame(self, padding=15)
        header.pack(fill="x")

        self.lbl_step = ttk.Label(header, text="Step 1 of 6: Incident Summary", font=("Segoe UI", 11, "bold"))
        self.lbl_step.pack(anchor="w")

        self.progress = ttk.Progressbar(header, maximum=6, value=1)
        self.progress.pack(fill="x", pady=(5, 0))

        # Swappable Body Container
        self.body_container = ttk.Frame(self)
        self.body_container.pack(fill="both", expand=True)

        # Footer Navigation Buttons
        footer = ttk.Frame(self, padding=15)
        footer.pack(fill="x")

        self.btn_back = ttk.Button(footer, text="< Back", command=self.vm.prev_step)
        self.btn_back.pack(side="left")

        self.btn_next = ttk.Button(footer, text="Next Step >", command=self._handle_next)
        self.btn_next.pack(side="right")

    def _bind_vm(self):
        self.vm.current_step.subscribe(self._on_step_changed)
        self._on_step_changed(self.vm.current_step.get())

    def _on_step_changed(self, step: int):
        self.progress.config(value=step)
        
        step_titles = [
            "Step 1 of 6: Incident Summary",
            "Step 2 of 6: Select Recovery Goals",
            "Step 3 of 6: Executing Recovery Actions",
            "Step 4 of 6: Evidence Package Summary",
            "Step 5 of 6: Generate Forensic PDF Report",
            "Step 6 of 6: Recovery Completed & Next Steps"
        ]
        self.lbl_step.config(text=step_titles[step - 1])

        # Clear body
        for w in self.body_container.winfo_children():
            w.destroy()

        # Swap Step View
        if step == 1:
            v = Step1SummaryView(self.body_container, self.vm)
        elif step == 2:
            v = Step2GoalsView(self.body_container, self.vm)
        elif step == 3:
            v = Step3ExecutionView(self.body_container, self.vm)
        elif step == 4:
            v = Step4EvidenceView(self.body_container, self.vm)
        elif step == 5:
            v = Step5PdfView(self.body_container, self.vm)
        elif step == 6:
            v = Step6CompletionView(self.body_container, self.vm)

        v.pack(fill="both", expand=True)

        # Update Navigation Buttons
        self.btn_back.config(state="disabled" if step == 1 or step == 3 else "normal")

        if step == 2:
            self.btn_next.config(text="Execute Recovery Actions >", command=self._handle_execute_goals)
        elif step == 6:
            self.btn_next.config(text="Finish & Close Wizard", command=self.destroy)
        else:
            self.btn_next.config(text="Next Step >", command=self._handle_next)

    def _handle_next(self):
        self.vm.next_step()

    def _handle_execute_goals(self):
        self.vm.execute_selected_goals()
