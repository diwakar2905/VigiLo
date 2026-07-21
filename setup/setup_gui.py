import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def setup_telegram():
    print("=== Anti-Theft Telegram Setup ===")
    bot_token = input("Enter your Telegram Bot Token: ").strip()
    chat_id = input("Enter your Telegram Chat ID: ").strip()

    # Load existing config or create new
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    else:
        config = {}

    # Preserve existing keys if they exist
    config["telegram"] = {"bot_token": bot_token, "chat_id": chat_id}
    if "security" not in config:
        config["security"] = {"failed_attempt_threshold": 2, "event_id": 4625, "check_interval_seconds": 3}
    if "camera" not in config:
        config["camera"] = {"device_index": 0}

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    print(f"[✓] Telegram configuration saved to {CONFIG_PATH}")

if __name__ == "__main__":
    setup_telegram()
