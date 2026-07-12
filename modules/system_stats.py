# modules/system_stats.py
from datetime import datetime
import platform
import psutil
from modules.base import BaseModule
from logs.logger import logger

class SystemStatsModule(BaseModule):
    def execute(self):
        """
        Gathers CPU, memory, disk usage, battery status, and boot time metrics.
        Returns a dictionary containing system statistics.
        """
        stats = {
            "os": f"{platform.system()} {platform.release()}",
            "cpu_usage": 0.0,
            "cpu_freq": "N/A",
            "ram_total_gb": 0.0,
            "ram_used_gb": 0.0,
            "ram_percent": 0.0,
            "disk_total_gb": 0.0,
            "disk_free_gb": 0.0,
            "battery_percent": None,
            "battery_plugged": None,
            "boot_time": "Unknown"
        }

        try:
            # CPU
            try:
                stats["cpu_usage"] = psutil.cpu_percent(interval=0.5)
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    stats["cpu_freq"] = f"{cpu_freq.current:.1f}Mhz"
            except Exception as ce:
                logger.error(f"CPU telemetry failed: {ce}")

            # RAM
            try:
                ram = psutil.virtual_memory()
                stats["ram_total_gb"] = round(ram.total / (1024**3), 1)
                stats["ram_used_gb"] = round(ram.used / (1024**3), 1)
                stats["ram_percent"] = ram.percent
            except Exception as re:
                logger.error(f"RAM telemetry failed: {re}")

            # Disk (C:\)
            try:
                disk = psutil.disk_usage('C:\\')
                stats["disk_total_gb"] = round(disk.total / (1024**3), 1)
                stats["disk_free_gb"] = round(disk.free / (1024**3), 1)
            except Exception as de:
                logger.error(f"Disk telemetry failed: {de}")

            # Battery
            try:
                battery = psutil.sensors_battery()
                if battery:
                    stats["battery_percent"] = battery.percent
                    stats["battery_plugged"] = battery.power_plugged
            except Exception as be:
                logger.error(f"Battery telemetry failed: {be}")

            # Boot Time
            try:
                bt = psutil.boot_time()
                stats["boot_time"] = datetime.fromtimestamp(bt).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as bte:
                logger.error(f"Boot time query failed: {bte}")

        except Exception as e:
            logger.error(f"System statistics retrieval failed: {e}")

        return stats
