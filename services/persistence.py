# services/persistence.py
import os
import subprocess
import winreg
from logs.logger import logger
from security.privilege import is_admin


class PersistenceService:
    def __init__(self, executable_path):
        self.exe_path = os.path.realpath(executable_path)
        self.working_dir = os.path.dirname(self.exe_path)
        self.service_task_name = "VigiLo_Service"
        self.commander_task_name = "VigiLo_Commander"

    def register_tasks(self):
        """Creates the scheduled tasks in Windows Task Scheduler via XML specifications."""
        if not is_admin():
            logger.error(
                "PersistenceService: Admin permissions required to schedule tasks."
            )
            return False

        # Clean old scheduler entries
        self.unregister_tasks()

        # 1. Register Service Task (runs on boot as SYSTEM context)
        service_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>VigiLo Security Service (System)</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{self.exe_path}</Command>
      <Arguments>--service</Arguments>
      <WorkingDirectory>{self.working_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

        service_xml_path = os.path.join(os.environ["TEMP"], "vigilo_service_task.xml")
        try:
            with open(service_xml_path, "w", encoding="utf-16") as f:
                f.write(service_xml)

            cmd = [
                "schtasks",
                "/Create",
                "/TN",
                self.service_task_name,
                "/XML",
                service_xml_path,
                "/F",
            ]
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            logger.info("Successfully registered SYSTEM boot scheduled task.")
        except Exception as e:
            logger.error(f"Failed to register SYSTEM boot task: {e}")
            return False
        finally:
            if os.path.exists(service_xml_path):
                try:
                    os.remove(service_xml_path)
                except Exception:
                    pass

        # 2. Register Commander Task (runs on Logon trigger for user profiles)
        commander_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>VigiLo User Agent (Commander)</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <GroupId>S-1-5-32-545</GroupId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{self.exe_path}</Command>
      <Arguments>--commander</Arguments>
      <WorkingDirectory>{self.working_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

        commander_xml_path = os.path.join(
            os.environ["TEMP"], "vigilo_commander_task.xml"
        )
        try:
            with open(commander_xml_path, "w", encoding="utf-16") as f:
                f.write(commander_xml)

            cmd = [
                "schtasks",
                "/Create",
                "/TN",
                self.commander_task_name,
                "/XML",
                commander_xml_path,
                "/F",
            ]
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            logger.info("Successfully registered USER logon commander task.")
            return True
        except Exception as e:
            logger.error(f"Failed to register USER logon commander task: {e}")
            return False
        finally:
            if os.path.exists(commander_xml_path):
                try:
                    os.remove(commander_xml_path)
                except Exception:
                    pass

    def unregister_tasks(self):
        """Deletes scheduled tasks from Task Scheduler."""
        if not is_admin():
            logger.warning(
                "PersistenceService: Admin permissions required to delete tasks."
            )
            return False

        for task in [self.service_task_name, self.commander_task_name]:
            try:
                cmd = ["schtasks", "/Delete", "/TN", task, "/F"]
                subprocess.run(
                    cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                logger.info(f"Task Scheduler: Deleted task {task} (if it existed).")
            except Exception as e:
                logger.error(f"Failed to delete scheduled task {task}: {e}")

    def add_registry_startup(self):
        """Adds registry Run startup entry (HKLM)."""
        if not is_admin():
            logger.error(
                "PersistenceService: Admin permissions required to write HKLM Run registry key."
            )
            return False

        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(
                key, "VigiLoMonitor", 0, winreg.REG_SZ, f'"{self.exe_path}" --service'
            )
            winreg.CloseKey(key)
            logger.info("Successfully registered Registry Run startup key.")
            return True
        except Exception as e:
            logger.error(f"Registry Run key registration exception: {e}")
            return False

    def remove_registry_startup(self):
        """Deletes registry Run startup entry (HKLM)."""
        if not is_admin():
            return False

        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, "VigiLoMonitor")
            winreg.CloseKey(key)
            logger.info("Registry Run key removed successfully.")
            return True
        except Exception as e:
            logger.debug(f"Registry Run key removal exception (can be ignored): {e}")
            return False
