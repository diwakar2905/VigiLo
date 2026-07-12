# ui/styles.py

BG      = "#1e1e1e"   # VS Code / modern Windows dark slate theme background
BG2     = "#252526"   # Card / panel background
BG3     = "#2d2d30"   # Scroll / secondary panel background
ACCENT  = "#4A90D9"   # Steel blue accent color
GREEN   = "#4EC994"   # Muted green accent
WARN    = "#ce9178"   # Warning orange accent
DIM     = "#858585"   # Muted text label color
FG      = "#d4d4d4"   # Primary foreground text color

def apply_styles(style):
    """Configures the provided ttk.Style instance with the WatchDog dark design system rules."""
    style.theme_use("clam")
    style.configure("TFrame",           background=BG)
    style.configure("TLabel",           background=BG,  foreground=FG,     font=("Segoe UI", 10))
    style.configure("TButton",          font=("Segoe UI", 10))
    style.configure("Header.TLabel",    font=("Segoe UI", 20, "bold"),  foreground=ACCENT, background=BG)
    style.configure("SubHeader.TLabel", font=("Segoe UI", 10),          foreground=DIM,    background=BG)
    style.configure("Warning.TLabel",   font=("Segoe UI", 10),          foreground=WARN,   background=BG)
    style.configure("TLabelframe",      background=BG2,  relief="flat")
    style.configure("TLabelframe.Label",background=BG2,  foreground=ACCENT, font=("Segoe UI", 10, "bold"))
    style.configure("Padded.TEntry",    padding=(8, 4, 4, 4),
                    fieldbackground="#3c3c3c", foreground=FG,
                    insertcolor=FG)
    style.configure("Horizontal.TProgressbar", troughcolor="#3c3c3c",
                    background=ACCENT, thickness=8)
