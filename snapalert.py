from dotenv import load_dotenv
import os
import requests

load_dotenv()

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

payload = {
    "chat_id": chat_id,
    "text": "⚡ Snap Alert"
}

response = requests.post(telegram_url, data=payload)

print("Status:", response.status_code)
print(response.text)