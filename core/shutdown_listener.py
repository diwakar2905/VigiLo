# core/shutdown_listener.py
import win32con
from logs.logger import logger

class ShutdownListener:
    def __init__(self, callback):
        self.callback = callback
        self.class_name = "VigiLoShutdown"
        self.window_title = "VigiLo_Shutdown_Listener"

    def start(self):
        """
        Registers a window class and window to pump messages and listen for shutdown queries.
        """
        try:
            import win32gui
        except ImportError:
            logger.warning("win32gui is not available. Shutdown listener cannot start.")
            return

        def wnd_proc(hwnd, msg, wparam, lparam):
            if msg == win32con.WM_QUERYENDSESSION:
                logger.warning("Windows query end session message received. Alerting shutdown...")
                try:
                    self.callback()
                except Exception as cb_err:
                    logger.error(f"Shutdown callback failed: {cb_err}")
                return 1 # Accept end session
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

        try:
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = wnd_proc
            wc.lpszClassName = self.class_name
            wc.hInstance = win32gui.GetModuleHandle(None)
            
            try:
                win32gui.RegisterClass(wc)
            except Exception:
                # Class may already be registered
                pass

            win32gui.CreateWindowEx(
                0, wc.lpszClassName, self.window_title, 
                0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
            )
            
            logger.info("Windows shutdown message pump active.")
            win32gui.PumpMessages()
        except Exception as e:
            logger.error(f"Shutdown listener creation failed: {e}")
