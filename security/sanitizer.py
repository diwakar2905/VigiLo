# security/sanitizer.py
import os
from logs.logger import logger

def is_safe_path(base_dir, path, follow_symlinks=True):
    """
    Checks if 'path' lies strictly within 'base_dir'.
    Prevents path traversal attacks like using '../' to break out of sandbox directories.
    """
    if not path:
        return False
        
    try:
        # Resolve to absolute paths
        if follow_symlinks:
            real_base = os.path.realpath(base_dir)
            real_path = os.path.realpath(path)
        else:
            real_base = os.path.abspath(base_dir)
            real_path = os.path.abspath(path)

        norm_base = os.path.normcase(real_base)
        norm_path = os.path.normcase(real_path)

        # Check if the resolved path starts with the base directory
        common = os.path.commonpath([norm_base, norm_path])
        return os.path.normcase(common) == norm_base

    except Exception as e:
        logger.error(f"Path safety check exception for base={base_dir}, path={path}: {e}")
        return False

def sanitize_filename(filename):
    """
    Removes path separators and invalid characters from a filename to make it safe for disk writes.
    """
    if not filename:
        return ""
    # Strip path separators to prevent sub-directory creation
    filename = os.path.basename(filename)
    # Remove potentially dangerous characters
    bad_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in bad_chars:
        filename = filename.replace(char, '')
    return filename
