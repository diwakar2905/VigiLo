# utils/network.py
import urllib.request
from logs.logger import logger


def check_internet(timeout=2):
    """
    Checks internet connectivity by attempting to open a connection to Google.
    Returns True if connection succeeded, False otherwise.
    """
    try:
        # Use a lightweight connection request to check network availability
        urllib.request.urlopen("https://www.google.com", timeout=timeout)
        return True
    except Exception as e:
        logger.debug(f"Internet connectivity check failed: {e}")
        return False


def download_file_with_checksum(url: str, dest_path: str, expected_hash: str) -> bool:
    """Downloads a file from a URL to dest_path and verifies its SHA-256 checksum."""
    import hashlib
    import os

    try:
        logger.info(f"Downloading {url} to {dest_path}...")
        dir_name = os.path.dirname(dest_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        h = hashlib.sha256()
        # Request with a standard User-Agent header to avoid HTTP 403 Forbidden on GitHub
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=45) as response, open(
            dest_path, "wb"
        ) as out_file:
            while chunk := response.read(16384):
                out_file.write(chunk)
                h.update(chunk)

        actual_hash = h.hexdigest()
        if actual_hash.lower() != expected_hash.lower():
            logger.error(
                f"Checksum mismatch for {os.path.basename(dest_path)}: "
                f"expected {expected_hash.lower()}, got {actual_hash.lower()}"
            )
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except Exception:
                    pass
            return False

        logger.info(
            f"Successfully downloaded and verified {os.path.basename(dest_path)}"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to download model file: {e}")
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                pass
        return False
