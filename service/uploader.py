import requests
import json

with open("config.json") as f:
    config = json.load(f)

def send_image(image_path):
    url = f"https://api.telegram.org/bot{config['bot_token']}/sendPhoto"
    files = {"photo": open(image_path, "rb")}
    data = {
        "chat_id": config["chat_id"],
        "caption": "🚨 Failed login detected on Windows device"
    }
    requests.post(url, files=files, data=data)
