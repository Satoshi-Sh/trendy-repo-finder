import requests
import json


def send_discord_message(webhook_url, message):
    if not webhook_url:
        return
    data = {
        "content": message,
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))

    if response.status_code == 204:
        print("Message sent successfully!")
    else:
        print(
            f"Failed to send message. Status code: {response.status_code}, Response: {response.text}"
        )
