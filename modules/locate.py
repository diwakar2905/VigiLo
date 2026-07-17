# modules/locate.py
import subprocess
import requests
from modules.base import BaseModule
from logs.logger import logger


class LocateModule(BaseModule):
    def execute(self):
        """
        Scans nearby WiFi networks and performs IP-based Geolocation lookup.
        Returns a dictionary with 'wifi' scan data and 'geo' geolocation info.
        """
        result = {"wifi": [], "geo": None}

        # 1. Scan Nearby WiFi Networks (Triangulation Data)
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                startupinfo=si,
                encoding="utf-8",
                errors="ignore",
            )

            current_ssid = "Unknown"
            for line in output.split("\n"):
                line = line.strip()
                if line.startswith("SSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        current_ssid = parts[1].strip()
                elif line.startswith("BSSID"):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        bssid = parts[1].strip()
                        result["wifi"].append(
                            {"ssid": current_ssid, "bssid": bssid, "signal": "Unknown"}
                        )
                elif line.startswith("Signal"):
                    if result["wifi"]:
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            result["wifi"][-1]["signal"] = parts[1].strip()
        except Exception as e:
            logger.error(f"WiFi scan failed: {e}")

        # 2. Get IP-Based Geolocation
        try:
            resp = requests.get("http://ip-api.com/json/", timeout=10)
            if resp.status_code == 200:
                info = resp.json()
                if info.get("status") == "success":
                    result["geo"] = info
                else:
                    logger.error(f"IP Geo-IP returned error status: {info}")
            else:
                logger.error(f"IP Geo-IP HTTP failed: Status {resp.status_code}")
        except Exception as e:
            logger.error(f"IP Geolocation query exception: {e}")

        return result
