# setup/uninstaller.py (Backward Compatibility Wrapper)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.uninstaller_gui import UninstallerApp
from security.privilege import is_admin, elevate


def main():
    if not is_admin():
        elevate()
    app = UninstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
