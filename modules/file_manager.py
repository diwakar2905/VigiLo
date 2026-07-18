# modules/file_manager.py
import os
from modules.base import BaseModule
from security.sanitizer import is_safe_path
from logs.logger import logger


class FileManagerModule(BaseModule):
    def __init__(self, jail_root=None):
        # Default security jail boundary is the logged-in user profile folder
        self.jail_root = os.path.realpath(
            jail_root if jail_root else os.path.expanduser("~")
        )

    def list_dir(self, target_path="."):
        """Lists files in target_path. Enforces jail boundaries."""
        abs_target = os.path.realpath(os.path.abspath(target_path))

        if not is_safe_path(self.jail_root, abs_target):
            logger.warning(
                f"FileManager: Blocked path traversal scan attempt at {abs_target}"
            )
            return "❌ Access Denied: Target folder lies outside security sandbox boundaries."

        try:
            if not os.path.exists(abs_target):
                return "❌ Path not found."
            if not os.path.isdir(abs_target):
                return "❌ Target path is not a directory."

            files = os.listdir(abs_target)
            msg = f"📂 Files in {abs_target}:\n"
            msg += "\n".join(files[:20])
            if len(files) > 20:
                msg += f"\n...and {len(files)-20} more."
            return msg
        except Exception as e:
            logger.error(f"FileManager list directory exception: {e}")
            return f"❌ Error: {e}"

    def change_dir(self, target_path):
        """Changes the current working directory safely within the jail boundary."""
        if not target_path:
            return "❌ Usage: /cd [directory_path]"

        abs_target = os.path.realpath(os.path.abspath(target_path))

        if not is_safe_path(self.jail_root, abs_target):
            logger.warning(
                f"FileManager: Blocked path traversal traversal attempt to {abs_target}"
            )
            return "❌ Access Denied: Destination lies outside security sandbox boundaries."

        try:
            os.chdir(abs_target)
            return f"📂 Changed directory to: {os.getcwd()}"
        except Exception as e:
            logger.error(f"FileManager change directory exception: {e}")
            return f"❌ Error: {e}"

    def get_download_path(self, target_file):
        """Resolves target_file and verifies it is safe to read. Returns absolute path or None."""
        if not target_file:
            return None

        abs_target = os.path.realpath(os.path.abspath(target_file))

        if not is_safe_path(self.jail_root, abs_target):
            logger.warning(
                f"FileManager: Blocked file download attempt outside sandbox: {abs_target}"
            )
            return None

        if os.path.exists(abs_target) and os.path.isfile(abs_target):
            return abs_target

        return None

    def execute(self, action, arg=""):
        """Fulfills execution interface for BaseModule."""
        if action == "ls":
            return self.list_dir(arg if arg else ".")
        elif action == "cd":
            return self.change_dir(arg)
        elif action == "download":
            return self.get_download_path(arg)
        return "❌ Unknown File Manager Action"
