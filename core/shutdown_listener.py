# core/shutdown_listener.py
import win32con
from logs.logger import logger
from core.runtime import IService
import threading


class ShutdownListener(IService):
    def __init__(self, callback):
        self.callback = callback
        self.class_name = "VigiLoShutdown"
        self.window_title = "VigiLo_Shutdown_Listener"
        self._thread = None
        self._initialized = False
        self._healthy = True
        self._hwnd = None

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def start(self) -> bool:
        self._thread = threading.Thread(
            target=self._run, name="ShutdownListenerThread", daemon=True
        )
        self._thread.start()
        return True

    def stop(self) -> bool:
        if self._hwnd:
            try:
                import win32gui

                # Post quit message to pump message thread
                win32gui.PostMessage(self._hwnd, win32con.WM_CLOSE, 0, 0)
            except Exception as e:
                logger.error(f"ShutdownListener failed to stop pump: {e}")
        return True

    def restart(self) -> bool:
        self.stop()
        return self.start()

    def health(self) -> bool:
        return self._healthy and (self._thread is not None and self._thread.is_alive())

    def status(self) -> str:
        if self.health():
            return "RUNNING"
        return "STOPPED"

    def _run(self):
        """
        Registers a window class and window to pump messages and listen for shutdown queries.
        """
        try:
            import win32gui
        except ImportError:
            logger.warning("win32gui is not available. Shutdown listener cannot start.")
            self._healthy = False
            return

        def wnd_proc(hwnd, msg, wparam, lparam):
            if msg == win32con.WM_QUERYENDSESSION:
                logger.warning(
                    "Windows query end session message received. Alerting shutdown..."
                )
                try:
                    self.callback()
                except Exception as cb_err:
                    logger.error(f"Shutdown callback failed: {cb_err}")
                return 1  # Accept end session
            elif msg == win32con.WM_DESTROY:
                win32gui.PostQuitMessage(0)
                return 0
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

            self._hwnd = win32gui.CreateWindowEx(
                0,
                wc.lpszClassName,
                self.window_title,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                wc.hInstance,
                None,
            )

            logger.info("Windows shutdown message pump active.")
            try:
                from core.runtime import ServiceManager

                ServiceManager().publish_heartbeat("ShutdownListener")
            except Exception:
                pass
            win32gui.PumpMessages()
            self._healthy = True
        except Exception as e:
            logger.error(f"Shutdown listener creation failed: {e}")
            self._healthy = False

    def pause(self) -> bool:
        logger.info("ShutdownListener: pause (no-op)")
        return True

    def resume(self) -> bool:
        logger.info("ShutdownListener: resume (no-op)")
        return True

    def dispose(self) -> None:
        logger.info("ShutdownListener: disposed resources")
