from src.ui.views.main_control_center import DeviceControlCenterApp

# Alias for backwards compatibility
VigiLoDashboardApp = DeviceControlCenterApp

def main():
    app = DeviceControlCenterApp()
    app.mainloop()

if __name__ == "__main__":
    main()
