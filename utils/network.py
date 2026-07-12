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
