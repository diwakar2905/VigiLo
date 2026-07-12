# setup/install_wizard.py (Backward Compatibility Wrapper)
import sys
import os

# Append root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.installer_gui import InstallerApp
from security.privilege import is_admin, elevate

def main():
    if not is_admin():
        elevate()
    app = InstallerApp()
    app.mainloop()

if __name__ == "__main__":
    main()