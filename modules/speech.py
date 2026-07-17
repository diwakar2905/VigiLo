# modules/speech.py
import threading
import ctypes
from modules.base import BaseModule
from logs.logger import logger


class SpeechModule(BaseModule):
    def _run_alert(self, message):
        try:
            # 1. Announce via Text-To-Speech using native Win32 COM dispatch
            try:
                import win32com.client

                sapi = win32com.client.Dispatch("SAPI.SpVoice")
                sapi.Rate = 0
                sapi.Volume = 100
                sapi.Speak("Incoming Security Alert")
            except Exception as te:
                logger.error(f"SAPI voice initialization failed: {te}")
                sapi = None

            # 2. Show Windows Native Message Box (SystemModal + Warning Icon)
            # 4144 = 4096 (MB_SYSTEMMODAL - always on top) + 48 (MB_ICONWARNING)
            title = "⚠️ VigiLo Security Alert"

            def show_dialog():
                try:
                    ctypes.windll.user32.MessageBoxW(0, message, title, 4144)
                except Exception as me:
                    logger.error(f"Failed to show ctypes MessageBox: {me}")

            threading.Thread(target=show_dialog, daemon=True).start()

            # 3. Read the message out loud
            if sapi:
                try:
                    sapi.Speak(message)
                except Exception as se:
                    logger.error(f"SAPI voice speaking exception: {se}")

        except Exception as e:
            logger.error(f"Speech/MessageBox alert thread exception: {e}")

    def execute(self, message):
        """
        Spawns a native Windows speech and system modal dialog alert in a background thread.
        """
        if not message:
            return False

        logger.info(f"Triggering voice alert popup: '{message}'")
        threading.Thread(target=self._run_alert, args=(message,), daemon=True).start()
        return True
